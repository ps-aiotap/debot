import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from simple_main import ChatbotApp

load_dotenv()

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
    st.session_state.initialized = False

@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot once and cache it."""
    app = ChatbotApp()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.initialize())
    return app

# Streamlit UI
st.title("🤖 DHHS AI Domain Expert Chatbot")
st.markdown("Ask questions about your documents, test cases, and business requirements.")

# Initialize chatbot
if not st.session_state.initialized:
    with st.spinner("Initializing chatbot..."):
        try:
            st.session_state.chatbot = initialize_chatbot()
            st.session_state.initialized = True
            st.success("Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()

# Chat interface
if st.session_state.initialized:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.ask_question(prompt)
                    answer = response.get('answer', 'No answer generated.')
                    sources = response.get('sources', [])
                    
                    st.markdown(answer)
                    
                    # Show sources if available
                    if sources:
                        st.markdown("**Sources:**")
                        for i, source in enumerate(sources, 1):
                            filename = source.get('filename', 'Unknown')
                            st.markdown(f"{i}. {filename}")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    This chatbot can answer questions about:
    - 📄 Your documents (.md, .txt, .docx)
    - 📊 Test cases and business requirements
    - 📋 PDF documents
    - 🌐 Crawled web content
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()