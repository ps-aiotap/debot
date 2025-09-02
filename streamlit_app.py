import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

load_dotenv(override=True)

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
    st.session_state.initialized = False


def initialize_chatbot(persona_manager=None, force_reindex=False):
    """Initialize chatbot once and cache it."""
    print("DEBUG: Starting chatbot initialization")
    if force_reindex:
        os.environ["FORCE_REINDEX"] = "true"
    app = SimpleChatbotApp(persona_manager=persona_manager)
    print("DEBUG: SimpleChatbotApp created")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("DEBUG: About to run app.initialize()")
    loop.run_until_complete(app.initialize())
    print("DEBUG: app.initialize() completed")
    return app


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

# Initialize persona manager
if "persona_manager" not in st.session_state:
    st.session_state.persona_manager = PersonaManager()

# Initialize chatbot
if not st.session_state.initialized:
    with st.spinner("Initializing chatbot and indexing documents..."):
        try:
            st.session_state.chatbot = initialize_chatbot(st.session_state.persona_manager, force_reindex=True)
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
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    # Enable explainability for debugging
                    response = loop.run_until_complete(st.session_state.chatbot.ask_question(prompt, use_cache=False, explain=True))
                    answer = response.get("answer", "No answer generated.")
                    sources = response.get("sources", [])
                    explanation = response.get("explanation")
                    


                    st.markdown(answer)

                    # Show sources if available (filter out hash documents)
                    if sources:
                        # Filter out content hash documents
                        actual_sources = [s for s in sources if s.get('type') != 'hash']
                        if actual_sources:
                            st.markdown("**Sources:**")
                            for i, source in enumerate(actual_sources, 1):
                                filename = source.get("filename", "Unknown")
                                doc_type = source.get("type", "Unknown")
                                st.markdown(f"{i}. {filename} ({doc_type})")
                        else:
                            st.markdown("*No document sources found*")
                    
                    # Show explainability if available
                    if explanation:
                        with st.expander("🔍 Why these documents were selected", expanded=False):
                            st.write(f"**Query:** {explanation['query']}")
                            st.write(f"**Documents Retrieved:** {explanation['total_docs_retrieved']}")
                            
                            if explanation.get('potential_issues'):
                                st.warning("**Potential Issues:**")
                                for issue in explanation['potential_issues']:
                                    st.write(f"⚠️ {issue}")
                            
                            st.write("**Document Analysis:**")
                            for exp in explanation['explanations']:
                                with st.container():
                                    st.write(f"**📄 {exp['document']}**")
                                    st.write(f"- Similarity Score: {exp['similarity_score']}")
                                    st.write(f"- Reason: {exp['relevance_reason']}")
                                    if exp['keyword_matches']:
                                        st.write(f"- Keywords: {', '.join(exp['keyword_matches'][:5])}")
                                    if exp['location_mismatch']:
                                        st.error(f"⚠️ Location mismatch: Query locations {exp['query_locations']} vs Doc locations {exp['doc_locations']}")
                                    st.divider()

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
    
    # Persona selector
    st.subheader("👤 Persona Settings")
    available_personas = st.session_state.persona_manager.get_available_personas()
    current_persona = st.session_state.persona_manager.get_current_persona()
    
    selected_persona = st.selectbox(
        "Select Persona",
        available_personas,
        index=available_personas.index(current_persona) if current_persona in available_personas else 0
    )
    
    # Change persona if selection changed
    if selected_persona != current_persona:
        if st.session_state.persona_manager.set_persona(selected_persona):
            st.session_state.chatbot = None
            st.session_state.initialized = False
            st.rerun()
    
    # Display active collections
    st.write("**Active Collections:**")
    for collection in st.session_state.persona_manager.get_collections():
        st.write(f"- {collection}")
    
    # Display prompt style
    st.write(f"**Prompt Style:** {st.session_state.persona_manager.get_prompt_style()}")
    
    # Explainability toggle
    st.subheader("🔍 Debug Options")
    if st.checkbox("Show retrieval explanations", value=True):
        st.write("Explanations will show why documents were selected")
    
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
    
    if st.button("🔄 Reinitialize Chatbot"):
        st.session_state.chatbot = None
        st.session_state.initialized = False
        st.rerun()
