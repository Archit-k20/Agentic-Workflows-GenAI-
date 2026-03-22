import streamlit as st

def show_generator_ui(api_key=None):
    st.header("🚀 Content Generator Toolkit")
    
    if not api_key:
        st.error("OpenAI API key is required")
        return

    tabs = st.tabs([
        "🎨 Text-to-Image",
        "🗣️ Text-to-Speech",
        "🎬 YouTube Captions",
        "🛠 Code Copilot",
        "🎞 Content Pipeline"
    ])

    # ---- Text to Image ----
    with tabs[0]:
        st.markdown("### Generate an Image from Text")
        prompt = st.text_input("Enter image prompt")
        if st.button("Generate Image"):
            if prompt:
                from .image_gen import generate_image_from_text
                image = generate_image_from_text(prompt, api_key)
                if isinstance(image, str) and image.startswith("Error"):
                    st.error(image)
                else:
                    st.image(image, caption="Generated Image", use_container_width=True)
            else:
                st.warning("Please enter a prompt.")

    # ---- Text to Speech ----
    with tabs[1]:
        st.markdown("### Convert Text to Audio")
        text = st.text_area("Enter text to convert")
        voice = st.selectbox("Select a voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        if st.button("Generate Speech"):
            if text:
                from .text_to_speech import generate_speech
                audio = generate_speech(text, voice, api_key)
                if isinstance(audio, str) and audio.startswith("Error"):
                    st.error(audio)
                else:
                    st.audio(audio, format="audio/mp3")
            else:
                st.warning("Please enter text to convert.")

    # ---- YouTube Captions ----
    with tabs[2]:
        st.markdown("### Extract Captions from a YouTube Video")
        yt_url = st.text_input("YouTube Video URL")
        if st.button("Extract Captions"):
            if yt_url:
                from .yt_caption_generator import caption_from_youtube_url
                captions = caption_from_youtube_url(yt_url)
                st.text_area("Extracted Captions", value=captions, height=300)
            else:
                st.warning("Please enter a valid YouTube URL.")

    # ---- Text to Code ----
    with tabs[3]:
        from .code_copilot import show_code_copilot
        show_code_copilot(api_key)

    with tabs[4]:
        from .content_pipeline import show_content_pipeline
        show_content_pipeline(api_key)
