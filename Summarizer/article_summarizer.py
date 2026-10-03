"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.article_summarizer import get_article_summary_pipeline, summarize_article
