import streamlit as st
from models import Message, ConversationHistory
from character_system import CharacterSystem
from gemini_client import GeminiClient
from config import MAX_CONVERSATION_ROUNDS, CONVERSATION_HISTORY_FILE

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = ConversationHistory(
        max_rounds=MAX_CONVERSATION_ROUNDS,
        json_file_path=CONVERSATION_HISTORY_FILE
    )
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
    st.title("Conversation Status")
    current_messages = len(st.session_state.conversation_history.messages)
    user_messages = sum(1 for msg in st.session_state.conversation_history.messages if msg.role == "user")
    assistant_messages = sum(1 for msg in st.session_state.conversation_history.messages if msg.role == "assistant")
    st.write(f"**Current Rounds:** {user_messages}/{MAX_CONVERSATION_ROUNDS}")
    st.write(f"**Total Messages:** {current_messages} (User: {user_messages}, Assistant: {assistant_messages})")
    st.write(f"**History File:** {CONVERSATION_HISTORY_FILE}")
    
    if st.button("Clear History"):
        st.session_state.conversation_history.messages = []
        st.session_state.conversation_history.save_to_json()
        st.rerun()

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