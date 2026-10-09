"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.yt_caption_generator import (
    extract_video_id,
    get_transcript,
    caption_from_youtube_url,
)
