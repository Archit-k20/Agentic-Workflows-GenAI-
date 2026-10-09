"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.file_summarizer import (
    get_file_summary_pipeline,
    extract_text_from_pdf,
    extract_text_from_docx,
    summarize_file,
)
