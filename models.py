from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

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
    session_id: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        # Generate session ID for logging/debugging purposes
        import uuid
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]

    def add_message(self, message: Message) -> None:
        """Add a message to history and maintain the sliding window"""
        self.messages.append(message)
        user_message_count = sum(1 for msg in self.messages if msg.role == "user")
        
        # Maintain sliding window - remove old messages if exceeds max rounds
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
            
            # Remove old messages from the beginning
            removed_messages = self.messages[:remove_index]
            self.messages = self.messages[remove_index:]
            
            # Log what was removed for debugging
            print(f"[Session {self.session_id}] Removed {len(removed_messages)} old messages to maintain window size")

    def get_context_messages(self) -> List[Dict]:
        """Get messages in OpenAI chat format"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def clear_history(self) -> None:
        """Clear all messages in current session"""
        message_count = len(self.messages)
        self.messages = []
        print(f"[Session {self.session_id}] Cleared {message_count} messages")
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        total_messages = len(self.messages)
        user_messages = sum(1 for msg in self.messages if msg.role == "user")
        assistant_messages = sum(1 for msg in self.messages if msg.role == "assistant")
        
        return {
            "session_id": self.session_id,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "max_rounds": self.max_rounds
        }