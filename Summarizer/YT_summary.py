"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.YT_summary import (
    get_text_summary_pipeline,
    extract_video_id,
    get_transcript,
    summarize_from_url,
)
