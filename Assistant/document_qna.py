import os
import streamlit as st
import re
from tempfile import NamedTemporaryFile
from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredPDFLoader, 
    UnstructuredWordDocumentLoader, 
    CSVLoader
)
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def show_document_qna(uploaded_files, api_key=None):
    # Initialize and validate
    if not api_key:
        st.error("🔑 OpenAI API key is required")
        return
        
    if not uploaded_files:
        st.info("ℹ️ Please upload at least one document to begin")
        return

    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    st.title("📄 Document QnA Tool")
    
    # Configuration
    faiss_folder_path = "faiss_store_docs"
    llm = OpenAI(api_key=api_key, temperature=0.7, max_tokens=1000)
    
    # File processing
    if st.button("🔧 Process Files"):
        with st.spinner("Processing documents..."):
            try:
                docs = []
                temp_files = []
                
                for uploaded_file in uploaded_files[:3]:  # Limit to 3 files
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    
                    with NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                        # Write file content
                        if hasattr(uploaded_file, 'chunks'):
                            for chunk in uploaded_file.chunks():
                                tmp.write(chunk)
                        else:
                            tmp.write(uploaded_file.read())
                        temp_files.append(tmp.name)
                    
                    # Select appropriate loader
                    if file_ext == '.pdf':
                        loader = UnstructuredPDFLoader(tmp.name)
                    elif file_ext == '.docx':
                        loader = UnstructuredWordDocumentLoader(tmp.name)
                    elif file_ext == '.csv':
                        loader = CSVLoader(tmp.name)
                    else:
                        st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                        continue
                        
                    data = loader.load()
                    docs.extend(data)
                
                # Process documents
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1500,
                    chunk_overlap=200,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                split_docs = text_splitter.split_documents(docs)
                
                # Create and save vectorstore
                embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                vectorstore = FAISS.from_documents(split_docs, embeddings)
                vectorstore.save_local(faiss_folder_path)
                
                st.success("✅ Documents processed and ready for querying!")
                
            except Exception as e:
                st.error(f"❌ Error processing files: {str(e)}")
            finally:
                # Clean up temp files
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass

    # Query handling
    query = st.text_input("💬 Ask a question about your documents:")
    if query:
        if not os.path.exists(faiss_folder_path):
            st.warning("⚠️ Please process documents first")
            return
            
        with st.spinner("Searching for answers..."):
            try:
                embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                vectorstore = FAISS.load_local(
                    faiss_folder_path, 
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
                
                chain = RetrievalQAWithSourcesChain.from_llm(
                    llm=llm,
                    retriever=vectorstore.as_retriever(),
                    return_source_documents=True
                )
                
                result = chain({"question": query}, return_only_outputs=True)
                
                # Clean and format response
                answer = re.sub(r"\(.*?AppData.*?\.pdf\)", "", result.get("answer", "No answer found."))
                sources = result.get("sources", "No sources found.")
                
                # Display results
                st.markdown(f"""
                ### 📝 Answer
                {answer}
                
                ---
                
                ### 📚 Sources
                ```
                {sources}
                ```
                """)
                
            except Exception as e:
                st.error(f"❌ Error answering question: {str(e)}")
