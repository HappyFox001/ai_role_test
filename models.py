from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
import json

class Emotion(BaseModel):
    type: str
    intensity: float = Field(ge=0.0, le=1.0)

class State(BaseModel):
    type: str

class ResponseChunk(BaseModel):
    chunk_index: int
    text: str
    emotion: Optional[Emotion] = None
    state: Optional[State] = None

class ConversationResponse(BaseModel):
    conversation: List[ResponseChunk]

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    emotion: Optional[Emotion] = None
    state: Optional[State] = None

class Character(BaseModel):
    name: str = "梅露梅莉亚＝伊拉＝班盖艾斯"
    gender: str = "女性"
    age: int = 3
    race: str = "人造人类"
    height: int = 142
    weight: int = 38
    specialties: List[str] = ["魔元素的操控"]
    likes: List[str] = ["聊天", "洗澡", "购物"]
    dislikes: List[str] = ["歧视与偏见等负面情绪"]
    personality: List[str] = ["开朗", "天真", "坦率"]
    attitude: str = "毫无戒心、温柔善良"
    background: str = ""

    def load_from_md(self, md_content: str):
        """Load character information from markdown content"""
        pass

class ConversationHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    max_rounds: int = 30
    json_file_path: str = "conversation_history.json"

    def __init__(self, **data):
        super().__init__(**data)
        self.load_from_json()

    def add_message(self, message: Message) -> None:
        """Add a message to history and maintain the sliding window"""
        self.messages.append(message)
        user_message_count = sum(1 for msg in self.messages if msg.role == "user")
        
        if user_message_count > self.max_rounds:
            user_messages_to_remove = user_message_count - self.max_rounds
            user_count = 0
            remove_index = 0
            
            for i, msg in enumerate(self.messages):
                if msg.role == "user":
                    user_count += 1
                    if user_count > user_messages_to_remove:
                        remove_index = i
                        break
            self.messages = self.messages[remove_index:]
        
        self.save_to_json()

    def get_context_messages(self) -> List[Dict]:
        """Get messages in OpenAI chat format"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def save_to_json(self) -> None:
        """Save conversation history to JSON file"""
        try:    
            messages_data = []
            for msg in self.messages:
                msg_dict = {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "emotion": msg.emotion.dict() if msg.emotion else None,
                    "state": msg.state.dict() if msg.state else None
                }
                messages_data.append(msg_dict)
            
            data = {
                "messages": messages_data,
                "max_rounds": self.max_rounds
            }
            
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving conversation history: {e}")
    
    def load_from_json(self) -> None:
        """Load conversation history from JSON file"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                messages = []
                for msg_data in data.get("messages", []):
                    emotion = None
                    if msg_data.get("emotion"):
                        emotion = Emotion(**msg_data["emotion"])
                    
                    state = None
                    if msg_data.get("state"):
                        state = State(**msg_data["state"])
                    
                    message = Message(
                        role=msg_data["role"],
                        content=msg_data["content"],
                        timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                        emotion=emotion,
                        state=state
                    )
                    messages.append(message)
                
                self.messages = messages
                self.max_rounds = data.get("max_rounds", 30)
                
                user_message_count = sum(1 for msg in self.messages if msg.role == "user")
                if user_message_count > self.max_rounds:
                    user_messages_to_remove = user_message_count - self.max_rounds
                    user_count = 0
                    remove_index = 0
                    
                    for i, msg in enumerate(self.messages):
                        if msg.role == "user":
                            user_count += 1
                            if user_count > user_messages_to_remove:
                                remove_index = i
                                break
                    
                    self.messages = self.messages[remove_index:]
                    
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            self.messages = []