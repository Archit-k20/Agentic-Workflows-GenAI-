import streamlit as st
from .document_intelligence import show_document_intelligence
from .document_qna import show_document_qna
from .research_agent import show_research_agent
from .support_triage import show_support_triage
from .url_qna import show_url_qna

def show_assistant_ui(api_key=None):
    st.header("🧠 LangChain Assistant Tools")
    st.markdown("Interact with uploaded documents or news URLs using LLM-powered QnA.")
    
    if not api_key:
        st.error("OpenAI API key is required")
        return

    tabs = st.tabs(["🔎 Research Agent", "🧾 Document Intelligence", "📄 Document QnA", "🌐 News Article QnA", "🆘 Support/Triage"])

    with tabs[0]:
        st.subheader("🔎 Run a Cited Research Workflow")
        show_research_agent(api_key)

    with tabs[1]:
        st.subheader("🧾 Extract Entities and Action Items")
        show_document_intelligence(api_key)

    with tabs[2]:
        st.subheader("📎 Ask Questions from Uploaded Documents")
        
        uploaded_files = st.file_uploader(
            "Upload up to 3 PDF/DOCX files",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            show_document_qna(uploaded_files, api_key)
        else:
            st.info("Please upload at least one document to begin.")

    with tabs[3]:
        st.subheader("📰 Ask Questions from News URLs")
        show_url_qna(api_key)

    with tabs[4]:
        st.subheader("🆘 Route Support Questions with Confidence")
        show_support_triage(api_key)
