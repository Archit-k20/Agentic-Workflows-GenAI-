import os
import streamlit as st
from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI, OpenAIEmbeddings

def show_url_qna(api_key=None):
    if not api_key:
        st.error("OpenAI API key is required")
        return

    st.markdown("Enter up to 3 news article URLs to begin.")
    urls = []
    for i in range(3):
        url = st.text_input(f"URL {i+1}")
        urls.append(url.strip())

    process_clicked = st.button("🔍 Process URLs")
    faiss_folder_path = "faiss_store_openai"
    status_placeholder = st.empty()

    if process_clicked:
        # Validate URLs before processing
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
        if not valid_urls:
            status_placeholder.error("Please enter at least one valid URL starting with http:// or https://")
            return

        try:
            # Initialize components with API key
            llm = OpenAI(api_key=api_key, temperature=0.9, max_tokens=500)
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            
            loader = UnstructuredURLLoader(urls=valid_urls)
            status_placeholder.info("📡 Loading article content...")
            data = loader.load()

            # Split and embed
            splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ".", ","],
                chunk_size=1000,
                chunk_overlap=200
            )
            status_placeholder.info("🔧 Splitting text into chunks...")
            docs = splitter.split_documents(data)

            vectorstore = FAISS.from_documents(docs, embeddings)
            status_placeholder.info("📦 Generating vector embeddings...")
            
            vectorstore.save_local(faiss_folder_path)
            status_placeholder.success("✅ Articles indexed!")
        except Exception as e:
            status_placeholder.error(f"Error processing URLs: {str(e)}")
            return

    query = st.text_input("Ask a question about the URLs:")
    if query:
        if not os.path.exists(faiss_folder_path):
            st.warning("Please process URLs first before asking questions")
            return
            
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vectorstore = FAISS.load_local(
                faiss_folder_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            
            llm = OpenAI(api_key=api_key, temperature=0.7, max_tokens=500)
            chain = RetrievalQAWithSourcesChain.from_llm(
                llm=llm, 
                retriever=vectorstore.as_retriever()
            )
            
            result = chain({"question": query}, return_only_outputs=True)

            st.markdown("### 📘 Answer")
            st.success(result["answer"])
            
            if "sources" in result:
                st.markdown("#### 📄 Sources")
                st.code(result["sources"])
        except Exception as e:
            st.error(f"Error answering question: {str(e)}")
