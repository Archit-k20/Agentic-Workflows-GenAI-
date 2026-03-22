# Agentic Workflows GenAI App

[![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991)](https://platform.openai.com/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/Archit-k20/Agentic-Workflows-GenAI-)

A Streamlit-native multi-modal AI workspace that combines utility tools with full agentic workflows for research, document intelligence, code generation, content creation, and support triage.

This project was built to feel like a single AI operations desk where users can move from raw input to structured output, rather than using disconnected one-off tools.

## Preview
Link: https://archit-k20-agentic-workflows-genai--main-g71qyn.streamlit.app/

![App Logo](static/logo.jpg)

The app includes a refreshed Streamlit dashboard with:

- light and dark theme support
- workspace switching for `Summarizer`, `Generator`, and `Assistant`
- dashboard cards and workflow summaries
- agentic flows with planning, validation, critique, and escalation logic

## Why This App

Most Streamlit GenAI demos stop at simple prompt-in / output-out experiences.

This application goes further by combining:

- classic AI utilities
- retrieval workflows
- agentic planning and review loops
- code verification
- confidence-based support routing

It is useful as:

- a portfolio project
- a productivity hub for AI experiments
- a foundation for internal copilots
- a base for document, research, and support automation

## Core Workspaces

The application is organized into three top-level workspaces.

### 1. Summarizer Workspace

Focused on condensing information from different media types.

Features:

- `Text Summarizer`
  - summarize raw text
  - uses OpenAI when an API key is available
  - falls back to a local Hugging Face pipeline where possible

- `YouTube Summarizer`
  - extracts transcript text from a YouTube video
  - summarizes the transcript

- `Article Summarizer`
  - fetches an article from a URL
  - extracts readable text
  - summarizes the article

- `PDF/DOCX Summarizer`
  - accepts uploaded PDF and DOCX files
  - extracts text directly from uploaded file objects
  - summarizes the extracted content

- `Image Text Extractor`
  - uses Tesseract OCR on images
  - optionally summarizes extracted text

### 2. Generator Workspace

Focused on creation workflows and output packaging.

Features:

- `Text-to-Image`
  - image generation from prompt text

- `Text-to-Speech`
  - narration/audio generation from text
  - multiple voice options

- `YouTube Captions`
  - transcript extraction from a YouTube URL

- `Code Copilot`
  - prompt-based code generation
  - verification before output
  - one repair pass if verification fails
  - supports:
    - Python
    - JavaScript
    - Java
    - C
    - C++

- `Content Pipeline`
  - content planning
  - script generation
  - image prompt generation
  - platform-specific captions
  - hashtag generation
  - optional narration audio

### 3. Assistant Workspace

Focused on retrieval, reasoning, and workflow-based AI assistance.

Features:

- `Research Agent`
  - accepts a topic and research URLs
  - plans sub-questions
  - summarizes sources
  - synthesizes a cited report
  - critiques and revises the final output

- `Document Intelligence`
  - accepts PDF, DOCX, TXT, and image files
  - extracts text or OCR content
  - classifies the document
  - extracts entities
  - generates action items and due dates where possible

- `Document QnA`
  - processes uploaded files
  - creates embeddings and a FAISS index
  - answers questions over the uploaded documents

- `News Article QnA`
  - processes support/news URLs
  - builds retrieval context
  - answers grounded questions from those sources

- `Support/Triage Agent`
  - classifies a support request
  - reads support URLs
  - drafts a grounded answer
  - computes confidence
  - routes the issue to:
    - `answer`
    - `escalate`

## Agentic Workflows Included

This version contains five workflow-oriented modules:

1. `Research Agent`
2. `Document Intelligence`
3. `Code Copilot`
4. `Multimodal Content Pipeline`
5. `Support/Triage Agent`

Each one is built as more than just a generation call. Depending on the workflow, it may include:

- planning
- retrieval
- structured extraction
- verification
- critique
- revision
- confidence scoring
- escalation logic

## End-to-End Workflow Summary

### Research Agent

1. user enters a research topic
2. user provides source URLs
3. the agent creates a research plan
4. each source is read and summarized
5. a cited report is drafted
6. the report is critiqued and optionally revised

### Document Intelligence

1. user uploads files
2. text is extracted from PDF, DOCX, TXT, or images
3. the document is classified
4. entities are extracted
5. action items are generated

### Code Copilot

1. user enters a coding prompt
2. the agent generates code
3. code is verified locally using the available toolchain
4. if verification fails, a repair pass runs
5. verified code and a report are returned

### Content Pipeline

1. user enters a content idea
2. the pipeline creates a plan
3. it generates a script
4. it generates image prompts and platform captions
5. it reviews and refines the content package
6. it optionally creates narration audio

### Support/Triage Agent

1. user enters a support question
2. the request is classified by intent and severity
3. support URLs are processed
4. a grounded draft answer is created
5. confidence is scored
6. the request is answered or escalated

## UI / Frontend

The frontend is built entirely with Streamlit.

Notable UI improvements in the current version:

- custom dashboard-style landing area
- improved theme styling
- fixed dark mode toggle behavior
- segmented workspace navigation
- cleaner input, card, and expander styling
- better visual separation between workflow sections

No external frontend framework is used.

## Tech Stack

- `Streamlit`
- `OpenAI`
- `LangChain`
- `langchain-openai`
- `langchain-community`
- `FAISS`
- `newspaper3k`
- `PyMuPDF`
- `python-docx`
- `pytesseract`
- `youtube-transcript-api`
- `transformers`
- `torch`

## Project Structure

```text
Streamlit_AgenticApp/
|-- .streamlit/
|   `-- config.toml
|-- Assistant/
|   |-- assistant_app.py
|   |-- document_intelligence.py
|   |-- document_qna.py
|   |-- init.py
|   |-- research_agent.py
|   |-- support_triage.py
|   `-- url_qna.py
|-- Generator/
|   |-- code_copilot.py
|   |-- content_pipeline.py
|   |-- generator_app.py
|   |-- image_gen.py
|   |-- text_to_speech.py
|   `-- yt_caption_generator.py
|-- Summarizer/
|   |-- Summarizer_app.py
|   |-- YT_summary.py
|   |-- article_summarizer.py
|   |-- file_summarizer.py
|   |-- image_to_text.py
|   |-- init.py
|   `-- textsummary.py
|-- static/
|   `-- logo.jpg
|-- main.py
|-- requirements.txt
`-- README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Archit-k20/Agentic-Workflows-GenAI-.git
cd Agentic-Workflows-GenAI-
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

You can either:

- paste your OpenAI API key into the Streamlit sidebar at runtime
- or keep it locally in a `.env` file for personal development

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

Important:

- `.env` is ignored by git
- never commit secrets to GitHub

### 5. Optional local tools

Some features require local tooling:

- `Tesseract OCR`
  - needed for image OCR
  - expected default Windows path:
    - `C:\Program Files\Tesseract-OCR\tesseract.exe`

- Code Copilot verification runtimes/compilers:
  - `python`
  - `node`
  - `javac`
  - `gcc`
  - `g++`

If one of these is missing, code generation can still work, but verification for that language may be unavailable.

### 6. Run the app

```bash
streamlit run main.py
```

## What Was Improved In This Version

This repository now includes:

- stabilized app structure and cleaner git setup
- fixed function signature mismatches
- fixed in-memory uploaded file handling
- safer dependency handling
- updated OpenAI usage paths
- lazy loading for heavier local pipelines
- a verified multi-language Code Copilot
- five workflow-based AI modules
- a redesigned Streamlit frontend
- better theming and visual hierarchy

## Current Limitations

- live AI workflows require a valid OpenAI API key
- OCR quality depends on Tesseract installation and image quality
- article extraction depends on the structure of the target page
- some local fallback behaviors depend on available hardware and downloaded models
- research and support workflows currently rely on user-provided URLs rather than a persistent central knowledge base

## Recommended Next Improvements

- add persistent memory for documents and sources
- add export to PDF/Markdown for reports
- add unit/integration tests for workflow modules
- add persistent support knowledge base
- rename `init.py` files to proper `__init__.py`
- add deployment instructions for Streamlit Community Cloud or Render
- add dedicated screenshots/GIFs of the full UI

## Author

Maintained by Archit Kumar.

## License

No license file is currently included. Add one if you want to publish the project with an explicit license.
