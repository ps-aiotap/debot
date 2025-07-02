import streamlit as st
import asyncio
from main import ChatbotApp

# Page config
st.set_page_config(
    page_title="AI Domain Expert Chatbot",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot with caching."""
    app = ChatbotApp()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(app.initialize())
    return app if success else None

def main():
    st.title("🤖 AI Domain Expert Chatbot")
    st.markdown("Ask questions about your domain-specific documentation and selected websites.")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing chatbot..."):
            st.session_state.chatbot = initialize_chatbot()
    
    if not st.session_state.chatbot:
        st.error("Failed to initialize chatbot. Please check your configuration and data sources.")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        
        source_filter = st.selectbox(
            "Source Filter",
            ["all", "docs", "web"],
            help="Filter responses by source type"
        )
        
        use_cache = st.checkbox(
            "Use cached responses",
            value=True,
            help="Use cached responses for faster replies"
        )
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Source Types:**")
        st.markdown("- **docs**: Local documents and PDFs")
        st.markdown("- **web**: Crawled websites")
        st.markdown("- **all**: All sources")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander(f"Sources ({len(message['sources'])})", expanded=False):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**{i}. {source['filename']}** ({source['type']})")
                            st.markdown(f"*Source: {source['source']}*")
                            st.markdown(f"Preview: {source['content_preview']}")
                            st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.ask_question(
                    prompt, 
                    use_cache=use_cache, 
                    source_filter=source_filter
                )
            
            if "error" in response:
                st.error(response["error"])
                return
            
            # Display answer
            answer = response["answer"]
            st.markdown(answer)
            
            # Show cache indicator
            if response.get("cached", False):
                st.info("ℹ️ This response was retrieved from cache")
            
            # Show sources
            sources = response.get("sources", [])
            if sources:
                with st.expander(f"Sources ({len(sources)})", expanded=False):
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"**{i}. {source['filename']}** ({source['type']})")
                        st.markdown(f"*Source: {source['source']}*")
                        st.markdown(f"Preview: {source['content_preview']}")
                        st.markdown("---")
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })

if __name__ == "__main__":
    main()