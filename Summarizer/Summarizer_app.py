import streamlit as st
from .textsummary import summary
from .YT_summary import summarize_from_url
from .article_summarizer import summarize_article
from .file_summarizer import summarize_file
from .image_to_text import extract_text_from_image

def show_summarizer_ui(api_key=None):
    st.subheader("🧠 AI Summarization Suite")
    
    if not api_key:
        st.error("OpenAI API key is required for some features")
        # Don't return here since some features don't need API key

    tabs = st.tabs(["📝 Text Summarizer", "📺 YouTube Summarizer", 
                   "📰 Article Summarizer", "📄 PDF/DOCX Summarizer", 
                   "🖼️ Image Text Extractor"])

    # ---- Text Summarizer ----
    with tabs[0]:
        st.markdown("### Summarize Raw Text")
        input_text = st.text_area("Enter text to summarize:")
        if st.button("Summarize Text"):
            if input_text.strip():
                output = summary(input_text, api_key)
                st.success("✅ Summary:")
                st.write(output)
            else:
                st.warning("Please enter text.")
    
    # ---- YouTube Summarizer ----
    with tabs[1]:
        st.markdown("### Summarize YouTube Video")
        yt_url = st.text_input("YouTube URL")
        if st.button("Summarize Video"):
            if yt_url:
                result = summarize_from_url(yt_url, api_key)
                st.success("✅ Video Summary:")
                st.write(result)
            else:
                st.warning("Please enter a valid URL.")

    # ---- Article Summarizer ----
    with tabs[2]:
        st.markdown("### Summarize Web Article")
        article_url = st.text_input("Article URL")
        if st.button("Summarize Article"):
            if article_url:
                result = summarize_article(article_url, api_key)
                st.success("✅ Article Summary:")
                st.write(result)
            else:
                st.warning("Please enter a valid article URL.")

    # ---- File Summarizer ----
    with tabs[3]:
        st.markdown("### Summarize Uploaded File")
        file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
        if file and st.button("Summarize File"):
            result = summarize_file(file, api_key)
            st.success("✅ File Summary:")
            st.write(result)
            
    # ---- Image Text Extractor ----
    with tabs[4]:
        st.markdown("### Extract Text from Images")
        uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        
        if uploaded_image:
            if st.button("Extract Text"):
                extracted_text = extract_text_from_image(uploaded_image)
                st.text_area("Extracted Text", value=extracted_text, height=300)
                
                # Optional summarization of extracted text
                if extracted_text and api_key and not extracted_text.startswith("Error"):
                    if st.button("Summarize Extracted Text"):
                        summary_result = summary(extracted_text, api_key)
                        st.success("✅ Summary of Extracted Text:")
                        st.write(summary_result)