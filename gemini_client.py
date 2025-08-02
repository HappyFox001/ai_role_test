from openai import OpenAI
from typing import List, Dict, Generator
import json
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_OPENAI_BASE_URL, EMOTIONS, STATES
from models import ResponseChunk, Emotion, State
from character_system import CharacterSystem

class GeminiClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url=GEMINI_OPENAI_BASE_URL
        )
        self.model = GEMINI_MODEL
        
    def _convert_to_openai_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert messages to OpenAI format (already in correct format)"""
        return messages

    def _parse_json_from_buffer(self, buffer: str) -> tuple[List[ResponseChunk], str]:
        """Tries to parse complete JSON objects from the buffer."""
        chunks = []
        remaining_buffer = buffer
        brace_count = 0
        start_pos = 0
        i = 0
        
        while i < len(buffer):
            char = buffer[i]
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = buffer[start_pos:i+1]
                    try:
                        data = json.loads(json_str)
                        if "conversation" in data:
                            for chunk_data in data["conversation"]:
                                chunks.append(ResponseChunk(
                                    chunk_index=chunk_data.get("chunk_index", len(chunks)),
                                    text=chunk_data.get("text", ""),
                                    emotion=Emotion(**chunk_data["emotion"]) if "emotion" in chunk_data else None,
                                    state=State(**chunk_data["state"]) if "state" in chunk_data else None
                                ))
                        else:
                            chunks.append(ResponseChunk(
                                chunk_index=len(chunks),
                                text=data.get("text", ""),
                                emotion=Emotion(**data["emotion"]) if "emotion" in data else None,
                                state=State(**data["state"]) if "state" in data else None
                            ))
                        remaining_buffer = buffer[i+1:]
                    except (json.JSONDecodeError, TypeError):
                        print(f"Warning: Failed to parse JSON: {json_str}")
            i += 1
                
        return chunks, remaining_buffer

    def stream_chat(self, messages: List[Dict[str, str]], character_system: CharacterSystem) -> Generator[ResponseChunk, None, None]:
        """Stream chat responses using OpenAI-compatible API and robust JSON parsing."""
        character_prompt = character_system.get_character_prompt()
        openai_messages = self._convert_to_openai_format(messages)
        
        system_message = {
            "role": "system",
            "content": f"""{character_prompt}

ストリーミング形式で応答する必要があります。応答は「conversation」フィールドを含むJSONオブジェクトで、会話チャンクの配列を含む必要があります。
emotion の `type` は次のいずれかでなければなりません: {EMOTIONS}
state の `type` は次のいずれかでなければなりません: {STATES}

conversation配列の各チャンクには次が含まれている必要があります:
- chunk_index: このチャンクのインデックス（0から開始）
- text: テキストコンテンツ（日本語）
- emotion: {{"type": "emotion_type", "intensity": 0.0-1.0}}
- state: {{"type": "state_type"}}

適切なストリーミング表示を可能にするため、応答を少なくとも2-3つのチャンクに分割してください。

応答例:
{{
  "conversation": [
    {{
      "chunk_index": 0,
      "text": "こんにちは！今日はどんな一日でしたか？",
      "emotion": {{
        "type": "Joy",
        "intensity": 0.8
      }},
      "state": {{
        "type": "Serenity"
      }}
    }},
    {{
      "chunk_index": 1,
      "text": "私、今とても面白い冒険の本を読んでいるんです！",
      "emotion": {{
        "type": "Anticipation",
        "intensity": 0.6
      }},
      "state": {{
        "type": "Curiosity"
      }}
    }},
    {{
      "chunk_index": 2,
      "text": "もしよろしければ、一緒にお話ししませんか？",
      "emotion": {{
        "type": "Anticipation",
        "intensity": 0.7
      }},
      "state": {{
        "type": "Interest"
      }}
    }}
  ]
}}"""
        }
        
        api_messages = [system_message] + openai_messages
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=0.9,
            top_p=0.8,
            stream=True
        )

        buffer = ""
        chunk_count = 0
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                buffer += content
                print(f"[DEBUG] 收到流式数据块 {chunk_count}: {repr(content)}")
                print(f"[DEBUG] 当前缓冲区内容: {repr(buffer)}")
                
                if '\n' in buffer:
                    parsed_chunks, remaining_buffer = self._parse_json_from_buffer(buffer)
                    print(f"[DEBUG] 解析出 {len(parsed_chunks)} 个chunk")
                    for i, parsed_chunk in enumerate(parsed_chunks):
                        print(f"[DEBUG] Chunk {i}: text='{parsed_chunk.text}', emotion={parsed_chunk.emotion}, state={parsed_chunk.state}")
                        yield parsed_chunk
                    buffer = remaining_buffer
                    print(f"[DEBUG] 剩余缓冲区: {repr(buffer)}")
                chunk_count += 1
        
        print(f"[DEBUG] 流式结束，最终缓冲区: {repr(buffer)}")
        if buffer:
            parsed_chunks, _ = self._parse_json_from_buffer(buffer + "\n")
            print(f"[DEBUG] 最终解析出 {len(parsed_chunks)} 个chunk")
            for parsed_chunk in parsed_chunks:
                print(f"[DEBUG] 最终Chunk: text='{parsed_chunk.text}', emotion={parsed_chunk.emotion}, state={parsed_chunk.state}")
                yield parsed_chunk