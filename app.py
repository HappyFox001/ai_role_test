import streamlit as st
from models import Message, ConversationHistory
from character_system import CharacterSystem
from gemini_client import GeminiClient
from config import MAX_CONVERSATION_ROUNDS

# Initialize session-based conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = ConversationHistory(
        max_rounds=MAX_CONVERSATION_ROUNDS
    )

# Initialize session start time for logging
if "session_start_time" not in st.session_state:
    from datetime import datetime
    st.session_state.session_start_time = datetime.now()
if "character_system" not in st.session_state:
    st.session_state.character_system = CharacterSystem()
if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = GeminiClient()

st.set_page_config(
    page_title="AI Companion Chat",
    page_icon="🤖",
    layout="wide"
)

with st.sidebar:
    st.title("Character Information")
    character = st.session_state.character_system.character
    st.write(f"**Name:** {character.name}")
    st.write(f"**Age:** {character.age}")
    st.write(f"**Race:** {character.race}")
    st.write("**Personality:**")
    for trait in character.personality:
        st.write(f"- {trait}")
    st.write("**Likes:**")
    for like in character.likes:
        st.write(f"- {like}")
    st.write("**Dislikes:**")
    for dislike in character.dislikes:
        st.write(f"- {dislike}")
    
    st.divider()
    st.title("Session Status")
    
    # Get session statistics
    stats = st.session_state.conversation_history.get_session_stats()
    
    # Display session info
    st.write(f"**Session ID:** `{stats['session_id']}`")
    st.write(f"**Current Rounds:** {stats['user_messages']}/{stats['max_rounds']}")
    st.write(f"**Total Messages:** {stats['total_messages']} (User: {stats['user_messages']}, Assistant: {stats['assistant_messages']})")
    
    # Session duration
    from datetime import datetime
    session_duration = datetime.now() - st.session_state.session_start_time
    duration_minutes = int(session_duration.total_seconds() / 60)
    st.write(f"**Session Duration:** {duration_minutes} minutes")
    
    # Storage info
    st.caption("💾 Data stored in browser session only - independent per tab/window")
    
    if st.button("Clear Session History"):
        st.session_state.conversation_history.clear_history()
        st.rerun()
    
    # Session log toggle
    st.divider()
    if st.checkbox("Show Session Log", help="Display conversation history for debugging"):
        st.subheader("Session Conversation Log")
        if st.session_state.conversation_history.messages:
            for i, msg in enumerate(st.session_state.conversation_history.messages):
                timestamp = msg.timestamp.strftime("%H:%M:%S")
                role_emoji = "👤" if msg.role == "user" else "🤖"
                content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                st.caption(f"{i+1}. [{timestamp}] {role_emoji} {msg.role}: {content_preview}")
        else:
            st.caption("No messages in current session")

st.title("AI Companion Chat")

for msg in st.session_state.conversation_history.messages:
    with st.chat_message(msg.role):
        st.write(msg.content)
        if msg.emotion and msg.emotion.type:
            st.caption(f"Emotion: {msg.emotion.type} ({msg.emotion.intensity:.2f})")
        if msg.state and msg.state.type:
            st.caption(f"State: {msg.state.type}")

if prompt := st.chat_input("Type your message here..."):
    user_message = Message(role="user", content=prompt)
    st.session_state.conversation_history.add_message(user_message)
    
    with st.chat_message("user"):
        st.write(prompt)
    
    chunks_received = []
    
    for chunk in st.session_state.gemini_client.stream_chat(
        st.session_state.conversation_history.get_context_messages(),
        st.session_state.character_system # Pass the whole system
    ):
        chunks_received.append(chunk)
        
        with st.chat_message("assistant"):
            st.write(chunk.text)
            
            if chunk.emotion:
                st.caption(f"Emotion: {chunk.emotion.type} ({chunk.emotion.intensity:.2f})")
            if chunk.state:
                st.caption(f"State: {chunk.state.type}")
        
        chunk_message = Message(
            role="assistant",
            content=chunk.text,
            emotion=chunk.emotion,
            state=chunk.state
        )
        st.session_state.conversation_history.add_message(chunk_message)