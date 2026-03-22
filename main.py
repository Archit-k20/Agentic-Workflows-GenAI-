import streamlit as st

from Assistant.assistant_app import show_assistant_ui
from Generator.generator_app import show_generator_ui
from Summarizer.Summarizer_app import show_summarizer_ui


st.set_page_config(
    page_title="GenAI Multi-Modal App",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


SECTION_OPTIONS = {
    "Summarizer": "📝 Summarizer Tool",
    "Generator": "🎨 Generator Tool",
    "Assistant": "📚 Assistant Tool",
}


def get_theme_palette(mode):
    if mode == "Dark":
        return {
            "bg": "#09111f",
            "panel": "rgba(10, 23, 42, 0.72)",
            "panel_strong": "rgba(12, 27, 49, 0.92)",
            "sidebar": "rgba(9, 18, 34, 0.95)",
            "text": "#f7fafc",
            "muted": "#b8c4d8",
            "accent": "#ff7a59",
            "accent_alt": "#4fd1c5",
            "border": "rgba(148, 163, 184, 0.18)",
            "input_bg": "rgba(15, 23, 42, 0.86)",
            "shadow": "0 18px 50px rgba(2, 6, 23, 0.36)",
            "hero": "linear-gradient(135deg, rgba(255, 122, 89, 0.22), rgba(79, 209, 197, 0.18), rgba(56, 189, 248, 0.12))",
        }
    return {
        "bg": "#f4f7fb",
        "panel": "rgba(255, 255, 255, 0.82)",
        "panel_strong": "rgba(255, 255, 255, 0.95)",
        "sidebar": "rgba(248, 250, 252, 0.95)",
        "text": "#10233d",
        "muted": "#51627c",
        "accent": "#ff6b4a",
        "accent_alt": "#0ea5a4",
        "border": "rgba(15, 23, 42, 0.09)",
        "input_bg": "rgba(255, 255, 255, 0.98)",
        "shadow": "0 18px 50px rgba(15, 23, 42, 0.08)",
        "hero": "linear-gradient(135deg, rgba(255, 107, 74, 0.18), rgba(14, 165, 164, 0.14), rgba(59, 130, 246, 0.10))",
    }


def apply_theme(mode):
    palette = get_theme_palette(mode)
    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {palette['bg']};
            --panel-bg: {palette['panel']};
            --panel-strong: {palette['panel_strong']};
            --sidebar-bg: {palette['sidebar']};
            --text-color: {palette['text']};
            --muted-color: {palette['muted']};
            --accent-color: {palette['accent']};
            --accent-alt: {palette['accent_alt']};
            --border-color: {palette['border']};
            --input-bg: {palette['input_bg']};
            --shadow-color: {palette['shadow']};
            --hero-bg: {palette['hero']};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(255, 122, 89, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(79, 209, 197, 0.12), transparent 24%),
                linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0)),
                var(--app-bg);
            color: var(--text-color);
        }}

        [data-testid="stAppViewContainer"] {{
            background: transparent;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }}

        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
        }}

        h1, h2, h3, h4, h5, h6, p, li, label, span {{
            color: var(--text-color);
        }}

        .hero-shell {{
            background: var(--hero-bg);
            border: 1px solid var(--border-color);
            border-radius: 28px;
            padding: 1.75rem 1.8rem;
            box-shadow: var(--shadow-color);
            backdrop-filter: blur(16px);
            margin-bottom: 1.2rem;
        }}

        .hero-kicker {{
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.16);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            margin-bottom: 0.95rem;
        }}

        .hero-title {{
            font-size: clamp(2rem, 4vw, 3.45rem);
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 0.6rem;
        }}

        .hero-subtitle {{
            font-size: 1.03rem;
            color: var(--muted-color);
            max-width: 48rem;
            margin-bottom: 0;
        }}

        .mini-card {{
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 22px;
            padding: 1rem 1.05rem;
            min-height: 140px;
            backdrop-filter: blur(12px);
            box-shadow: var(--shadow-color);
        }}

        .mini-card-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--muted-color);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.6rem;
        }}

        .mini-card-value {{
            font-size: 1.7rem;
            font-weight: 800;
            color: var(--text-color);
            margin-bottom: 0.4rem;
        }}

        .mini-card-copy {{
            color: var(--muted-color);
            font-size: 0.94rem;
            line-height: 1.5;
        }}

        .feature-card {{
            background: var(--panel-strong);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 1.15rem 1.2rem;
            min-height: 260px;
            box-shadow: var(--shadow-color);
            margin: 0.35rem 0 1.15rem 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .feature-card h4 {{
            margin-bottom: 0.55rem;
            line-height: 1.2;
        }}

        .feature-card p {{
            color: var(--muted-color);
            margin-bottom: 0.55rem;
            line-height: 1.55;
        }}

        [data-testid="stSegmentedControl"] {{
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 999px;
            padding: 0.35rem;
            box-shadow: var(--shadow-color);
            margin-bottom: 1rem;
        }}

        [data-testid="stSegmentedControl"] button {{
            border-radius: 999px !important;
            font-weight: 700;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--text-color);
        }}

        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stNumberInput input {{
            background: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 14px !important;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            background: linear-gradient(135deg, var(--accent-color), var(--accent-alt));
            color: white;
            border: 0;
            border-radius: 14px;
            font-weight: 700;
            padding: 0.65rem 1rem;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.16);
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            filter: brightness(1.04);
            transform: translateY(-1px);
        }}

        [data-testid="stExpander"] {{
            border: 1px solid var(--border-color);
            border-radius: 18px;
            background: var(--panel-bg);
        }}

        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] > div:has(> .workflow-shell) {{
            margin-bottom: 1rem;
        }}

        .workflow-shell {{
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow-color);
            margin-top: 0.4rem;
        }}

        .app-note {{
            color: var(--muted-color);
            font-size: 0.92rem;
            margin-top: 0.35rem;
        }}

        div[data-testid="column"] > div:has(.feature-card) {{
            padding-left: 0.6rem;
            padding-right: 0.6rem;
        }}

        div[data-testid="column"]:first-child > div:has(.feature-card) {{
            padding-left: 0;
            padding-right: 0.8rem;
        }}

        div[data-testid="column"]:last-child > div:has(.feature-card) {{
            padding-left: 0.8rem;
            padding-right: 0;
        }}

        .feature-card-accent {{
            width: 54px;
            height: 6px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-color), var(--accent-alt));
            margin-bottom: 0.95rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

apply_theme(st.session_state.theme_mode)


with st.sidebar:
    st.image("static/logo.jpg", width=124)
    st.markdown("### GenAI Control Deck")
    dark_mode_enabled = st.toggle("Dark mode", value=st.session_state.theme_mode == "Dark")
    st.session_state.theme_mode = "Dark" if dark_mode_enabled else "Light"
    apply_theme(st.session_state.theme_mode)

    st.markdown("### Workspace Status")
    st.caption("Five agentic workflows and the core utility tools are now available in one app.")

    with st.expander("ℹ️ About this App", expanded=False):
        st.markdown(
            """
            **GenAI Multi-Modal App** combines:
            - Research and support agents
            - Document intelligence and QnA
            - Multimodal generation workflows
            - Safer multi-language code copilot
            """
        )

    st.markdown("---")
    st.markdown("🔗 [GitHub Repo](https://github.com/Lamstersickness/GenAI_App)")
    st.markdown("🛠 Maintained by Archit Kumar [LinkedIn](https://www.linkedin.com/in/archit-kumar-aa6375259?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)")
    st.markdown("---")
    st.subheader("🔑 OpenAI API Key")
    api_key = st.text_input(
        "Enter your OpenAI API key:",
        type="password",
        help="Get your key from https://platform.openai.com/api-keys",
    )

    if api_key:
        st.success("API key loaded for live workflows.")
    else:
        st.info("Some features need an OpenAI API key. Local extraction and fallback flows can still be explored.")


st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-kicker">Streamlit-native AI workspace</div>
        <div class="hero-title">Build, research, summarize, and ship from one agentic dashboard.</div>
        <p class="hero-subtitle">
            A more polished frontend, clearer workflow entry points, and a working light/dark visual system
            wrapped around your summarizer, generator, assistant, and new agentic pipelines.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
with metric_col1:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">Workflows</div>
            <div class="mini-card-value">5</div>
            <div class="mini-card-copy">Research, document intelligence, code copilot, content pipeline, and support triage.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col2:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">Utility Tools</div>
            <div class="mini-card-value">8+</div>
            <div class="mini-card-copy">Summaries, OCR, captions, TTS, image generation, QnA, and more.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col3:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-card-title">Theme Mode</div>
            <div class="mini-card-value">{st.session_state.theme_mode}</div>
            <div class="mini-card-copy">Visual palette now updates the actual Streamlit app containers correctly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col4:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-card-title">Live Ready</div>
            <div class="mini-card-value">{'Yes' if api_key else 'Partial'}</div>
            <div class="mini-card-copy">Use your API key for full live runs across the agentic workflows.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

feature_col1, feature_col2, feature_col3 = st.columns([1, 1, 1], gap="large")
with feature_col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-card-accent"></div>
            <h4>Research and Triage</h4>
            <p>Use grounded workflows that plan, retrieve, cite, score confidence, and escalate when needed.</p>
            <p class="app-note">Best for analyst-style outputs and support experiences.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with feature_col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-card-accent"></div>
            <h4>Document and Media Intelligence</h4>
            <p>Summaries, OCR, entity extraction, action items, captions, narration, and structured outputs.</p>
            <p class="app-note">Best for uploaded files, videos, and operational document workflows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with feature_col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-card-accent"></div>
            <h4>Build and Launch</h4>
            <p>Generate code with verification, produce content packages, and move from idea to assets faster.</p>
            <p class="app-note">Best for creators, builders, and rapid internal tooling.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Workspace")
selected_section = st.segmented_control(
    "Choose a workspace",
    options=list(SECTION_OPTIONS.keys()),
    default="Assistant",
    selection_mode="single",
    label_visibility="collapsed",
)

st.markdown('<div class="workflow-shell">', unsafe_allow_html=True)
if selected_section == "Summarizer":
    st.markdown("## 📝 Summarizer Tool")
    st.caption("Compress articles, documents, transcripts, and extracted image text.")
    show_summarizer_ui(api_key)
elif selected_section == "Generator":
    st.markdown("## 🎨 Generator Tool")
    st.caption("Create visuals, narration, captions, verified code, and packaged content workflows.")
    show_generator_ui(api_key)
else:
    st.markdown("## 📚 Assistant Tool")
    st.caption("Run the agentic workflows, document intelligence, retrieval QnA, and support routing.")
    show_assistant_ui(api_key)
st.markdown("</div>", unsafe_allow_html=True)
