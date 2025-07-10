import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from simple_main import SimpleChatbotApp

load_dotenv(override=True)

# Clear Streamlit cache
st.cache_data.clear()
st.cache_resource.clear()

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
    st.session_state.initialized = False


def initialize_chatbot():
    """Initialize chatbot once and cache it."""
    import sys
    import traceback

    try:
        print("DEBUG: Starting chatbot initialization", flush=True)
        app = SimpleChatbotApp()
        print("DEBUG: SimpleChatbotApp created", flush=True)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("DEBUG: About to run app.initialize()", flush=True)
        result = loop.run_until_complete(app.initialize())
        print(f"DEBUG: app.initialize() completed with result: {result}", flush=True)
        return app
    except Exception as e:
        error_msg = f"INITIALIZATION ERROR: {str(e)}"
        print(error_msg, flush=True)
        print(f"ERROR TYPE: {type(e)}", flush=True)
        print(f"TRACEBACK: {traceback.format_exc()}", flush=True)
        sys.stdout.flush()
        raise e


# Streamlit UI
st.title("🤖 AI Domain Expert Chatbot")
st.markdown(
    "Ask questions about your documents, test cases, and business requirements."
)

# Debug .env values
# with st.expander("🔧 Environment Debug Info"):
#     st.write(f"**CHROMA_HOST:** {os.getenv('CHROMA_HOST', 'NOT SET')}")
#     st.write(f"**CHROMA_PORT:** {os.getenv('CHROMA_PORT', 'NOT SET')}")
#     st.write(f"**REDIS_HOST:** {os.getenv('REDIS_HOST', 'NOT SET')}")
#     st.write(f"**REDIS_PORT:** {os.getenv('REDIS_PORT', 'NOT SET')}")
#     st.write(f"**GROQ_API_KEY:** {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")
#     st.write(f"**Working Directory:** {os.getcwd()}")
#     st.write(f"**.env file exists:** {os.path.exists('.env')}")

#     # K8s specific debugging
#     st.write("**Data Directories:**")
#     import glob

#     for dir_path in ["/app/data/docs", "/app/data/pdfs", "/app/data/mds"]:
#         if os.path.exists(dir_path):
#             files = glob.glob(f"{dir_path}/*")
#             st.write(f"  {dir_path}: {len(files)} files")
#         else:
#             st.write(f"  {dir_path}: NOT FOUND")

#     # Test service connectivity
#     st.write("**Service Connectivity:**")
#     try:
#         import requests

#         chroma_url = f"http://{os.getenv('CHROMA_HOST', 'localhost')}:{os.getenv('CHROMA_PORT', '8000')}/api/v1/heartbeat"
#         response = requests.get(chroma_url, timeout=2)
#         st.write(f"  ChromaDB Heartbeat: {response.status_code} - {response.text[:50]}")
#     except Exception as e:
#         st.write(f"  ChromaDB Heartbeat: ERROR - {str(e)}")

#     # Test ChromaDB client creation
#     st.write("**ChromaDB Client Test:**")
#     try:
#         import chromadb

#         host = os.getenv("CHROMA_HOST", "localhost")
#         port = int(os.getenv("CHROMA_PORT", "8000"))

#         # Try simple client without complex settings
#         client = chromadb.HttpClient(host=host, port=port)
#         st.write(f"  Simple Client Creation: SUCCESS")

#         # Test collection operations
#         collection = client.get_or_create_collection("test_collection")
#         st.write(f"  Collection Creation: SUCCESS")

#         # Clean up immediately
#         client.delete_collection("test_collection")
#         st.write(f"  Basic Test: SUCCESS")

#     except Exception as e:
#         st.write(f"  ChromaDB Client: ERROR - {str(e)}")
#         st.code(str(e))

# Initialize chatbot
if not st.session_state.initialized:
    with st.spinner("Initializing chatbot..."):
        try:
            st.session_state.chatbot = initialize_chatbot()
            st.session_state.initialized = True
            st.success("Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            # Show more debug info on failure
            with st.expander("🚫 Initialization Error Details"):
                st.code(str(e))
                st.write(
                    "Check the Environment Debug Info above for connection issues."
                )
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
                    answer = response.get("answer", "No answer generated.")
                    sources = response.get("sources", [])

                    st.markdown(answer)

                    # Show sources if available
                    if sources:
                        st.markdown("**Sources:**")
                        for i, source in enumerate(sources, 1):
                            filename = source.get("filename", "Unknown")
                            st.markdown(f"{i}. {filename}")

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown(
        """
    This chatbot can answer questions about:
    - 📄 Your documents (.md, .txt, .docx)
    - 📊 Test cases and business requirements
    - 📋 PDF documents
    - 🌐 Crawled web content
    """
    )

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
