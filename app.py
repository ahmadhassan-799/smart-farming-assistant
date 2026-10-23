import asyncio
import queue
import threading
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

from ai_agent import farm_agent
from memory_store import (
    save_farmer_data,
    get_farmer_data,
    save_chat_history,
    get_chat_history,
)
from guardrails import check_farming_input
from weather_tool import get_weather
from image_analysis import analyze_crop_image
from image_generation import generate_farming_image
from computer_use import research_farming

load_dotenv()
client = OpenAI()

st.set_page_config(
    page_title="Green AI Studio",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# GREEN AI STUDIO DESIGN
# --------------------------------------------------

st.markdown("""
<style>
:root {
    --green: #087443;
    --dark-green: #064e3b;
    --text: #173b30;
    --muted: #526e60;
    --border: #d5e7d9;
    --surface: #ffffff;
    --background: #f3faf5;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--background) !important;
    color: var(--text) !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--dark-green) !important;
    font-weight: 750 !important;
}

.stMarkdown p,
.stMarkdown li,
[data-testid="stCaptionContainer"] p {
    color: var(--text) !important;
    opacity: 1 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #eaf5ed !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--dark-green);
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    min-height: 43px;
    border-radius: 12px !important;
    background: #ffffff !important;
    color: var(--dark-green) !important;
    border: 1px solid #bddbc6 !important;
    font-weight: 700 !important;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #e4f5e9 !important;
    border-color: var(--green) !important;
    transform: translateY(-1px);
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: var(--green) !important;
    color: white !important;
    border-color: var(--green) !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input {
    background: #ffffff !important;
    color: #173b30 !important;
    border-color: #c7dfce !important;
    border-radius: 11px !important;
    -webkit-text-fill-color: #173b30 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #71877a !important;
    -webkit-text-fill-color: #71877a !important;
    opacity: 1 !important;
}

/* Forms and expanders */
[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 20px !important;
}

[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #dcebe0 !important;
    border-radius: 16px !important;
    padding: 13px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #173b30 !important;
    opacity: 1 !important;
}

/* Real farmland hero */
.hero {
    background:
        linear-gradient(
            90deg,
            rgba(3, 43, 29, 0.90) 0%,
            rgba(5, 76, 43, 0.70) 55%,
            rgba(5, 76, 43, 0.32) 100%
        ),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=2000&q=85");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 24px;
    padding: 45px 36px;
    margin-bottom: 25px;
    min-height: 275px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 12px 32px rgba(7,75,43,0.16);
}

.hero .eyebrow {
    display: inline-block;
    width: fit-content;
    color: white !important;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.32);
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 750;
    margin-bottom: 15px;
}

.hero h1 {
    color: white !important;
    font-size: clamp(30px, 4vw, 47px);
    font-weight: 800 !important;
    line-height: 1.15;
    margin-bottom: 12px;
}

.hero p {
    color: #f0fff4 !important;
    font-size: 16px;
    line-height: 1.8;
    max-width: 800px;
}

/* Section headings */
.section-heading {
    font-size: 25px;
    color: var(--dark-green) !important;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 5px;
}

.section-subtitle {
    color: var(--muted) !important;
    margin-bottom: 15px;
}

/* Feature cards */
.tool-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 19px;
    min-height: 145px;
    margin-bottom: 12px;
    box-shadow: 0 5px 16px rgba(17,75,43,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.tool-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 22px rgba(17,75,43,0.09);
}

.tool-card .tool-icon {
    font-size: 27px;
    margin-bottom: 8px;
}

.tool-card h4,
.info-card h4 {
    color: var(--dark-green) !important;
    font-size: 17px;
    margin: 0 0 8px;
}

.tool-card p,
.info-card p {
    color: var(--muted) !important;
    font-size: 13px;
    line-height: 1.65;
    margin: 0;
}

.info-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 14px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 15px;
}

[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--dark-green) !important;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 28px 21px;
        min-height: 240px;
        border-radius: 18px;
    }

    .hero h1 {
        font-size: 31px;
    }

    .section-heading {
        font-size: 21px;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# STREAMING RUNNER
# --------------------------------------------------

@st.cache_resource
def get_stream_runner():
    class StreamRunner:
        def __init__(self):
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(
                target=self.loop.run_forever,
                daemon=True,
            )
            self.thread.start()

        async def stream(self, context, output_queue):
            try:
                result = Runner.run_streamed(
                    farm_agent,
                    input=context,
                )

                async for event in result.stream_events():
                    if (
                        event.type == "raw_response_event"
                        and isinstance(
                            event.data,
                            ResponseTextDeltaEvent,
                        )
                    ):
                        output_queue.put(
                            ("text", event.data.delta)
                        )

                output_queue.put(("done", None))

            except Exception as error:
                output_queue.put(("error", repr(error)))

        def start(self, context, output_queue):
            asyncio.run_coroutine_threadsafe(
                self.stream(context, output_queue),
                self.loop,
            )

    return StreamRunner()


runner = get_stream_runner()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "email": "",
    "messages": [],
    "finished": False,
    "page": "chat",
    "voice_token": None,
    "voice_token_error": None,
    "voice_token_created": False,
}

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


def start_new_chat():
    st.session_state.messages = []
    st.session_state.finished = False
    st.session_state.page = "chat"
    st.rerun()


# --------------------------------------------------
# LIVE VOICE
# --------------------------------------------------

def create_live_voice_token():
    try:
        token_response = client.realtime.client_secrets.create(
            expires_after={
                "anchor": "created_at",
                "seconds": 600,
            },
            session={
                "type": "realtime",
                "model": "gpt-realtime",
                "instructions": (
                    "You are a friendly Smart Farming Assistant. "
                    "Help farmers with crops, soil, irrigation, "
                    "weather and common plant problems. Speak simply. "
                    "Reply in the language the farmer uses. "
                    "Do not claim certain diagnosis from symptoms alone. "
                    "For chemical advice, recommend following the label."
                ),
                "audio": {
                    "input": {
                        "turn_detection": {
                            "type": "server_vad"
                        }
                    },
                    "output": {
                        "voice": "marin"
                    },
                },
            },
        )

        st.session_state.voice_token = token_response.value
        st.session_state.voice_token_error = None
        st.session_state.voice_token_created = True

    except Exception as error:
        st.session_state.voice_token = None
        st.session_state.voice_token_error = str(error)
        st.session_state.voice_token_created = False


def show_live_voice():
    st.markdown("### 🎙️ Live Voice Conversation")
    st.caption(
        "Prepare dabao, phir Start Live Voice dabao. "
        "Microphone permission allow karo aur baat shuru karo."
    )

    if st.session_state.voice_token is None:
        if st.button(
            "🎙️ Prepare Live Voice",
            key="prepare_live_voice",
            type="primary",
        ):
            with st.spinner("Live voice connect kar rahe hain..."):
                create_live_voice_token()

            if st.session_state.voice_token:
                st.success("Voice ready hai!")
            else:
                st.error(
                    "Voice setup error: "
                    + str(st.session_state.voice_token_error)
                )

            st.rerun()

        if st.session_state.voice_token_error:
            st.error(st.session_state.voice_token_error)

        return

    html_path = Path(__file__).parent / "voice_component.html"

    if not html_path.exists():
        st.error(
            "voice_component.html nahi mili. "
            "Is file ko app.py ke same folder mein rakho."
        )
        return

    try:
        html = html_path.read_text(encoding="utf-8")
        html = html.replace(
            "__EPHEMERAL_TOKEN__",
            st.session_state.voice_token,
        )

        components.html(
            html,
            height=330,
            scrolling=True,
        )

        st.caption(
            "Transcript voice panel mein nazar aayega. "
            "Token expire ho to page refresh karke dobara prepare karo."
        )

    except Exception as error:
        st.error(f"Live voice panel error: {error}")


# --------------------------------------------------
# ASK FARMING AI: STREAMING + MEMORY + GUARDRAILS
# --------------------------------------------------

def ask_farming_question(problem):
    problem = problem.strip()

    if not problem:
        return ""

    safe, warning_message = check_farming_input(problem)

    st.session_state.messages.append({
        "role": "user",
        "message": problem,
    })

    save_chat_history(
        st.session_state.email,
        "user",
        problem,
    )

    if not safe:
        warning = "⚠️ SAFETY WARNING\n\n" + str(warning_message)

        st.session_state.messages.append({
            "role": "assistant",
            "message": warning,
        })

        save_chat_history(
            st.session_state.email,
            "assistant",
            warning,
        )

        st.warning(warning)
        return warning

    previous = get_farmer_data(st.session_state.email)

    context = (
        f"Farmer identity: {st.session_state.email}\n"
        f"Current question: {problem}\n"
        f"Previous crop: {previous.get('previous_crop', 'unknown')}\n"
        f"Previous problem: {previous.get('previous_problem', 'unknown')}\n"
        "Use recent conversation for context. "
        "Reply in the same language as the farmer.\n"
        "Recent chat history:\n"
    )

    for item in st.session_state.messages[-9:-1]:
        context += f"{item['role']}: {item['message']}\n"

    output_queue = queue.Queue()
    runner.start(context, output_queue)
    answer_parts = []

    with st.chat_message("assistant"):
        placeholder = st.empty()

        while True:
            kind, value = output_queue.get()

            if kind == "text":
                answer_parts.append(value)
                placeholder.markdown(
                    "".join(answer_parts) + " ▌"
                )

            elif kind == "error":
                st.error(f"Streaming error: {value}")
                print("STREAMING ERROR:", value, flush=True)
                return ""

            elif kind == "done":
                break

        answer = "".join(answer_parts).strip()
        placeholder.markdown(
            answer or "AI ne koi text jawab nahi diya."
        )

    if not answer:
        return ""

    st.session_state.messages.append({
        "role": "assistant",
        "message": answer,
    })

    save_chat_history(
        st.session_state.email,
        "assistant",
        answer,
    )

    save_farmer_data(
        st.session_state.email,
        previous.get("previous_crop", "unknown"),
        problem,
    )

    return answer


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

if not st.session_state.email:
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">🌿 GREEN AI STUDIO</div>
        <h1>Grow Smarter.<br>Farm Better.</h1>
        <p>
            Your personal Smart Farming Assistant.
            Get crop guidance, explore farming research,
            analyze plant photos and make informed farming decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("## 🌱 Your Farm, Powered by AI")

        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">🌾</div>
            <h4>Crop Care</h4>
            <p>Practical guidance about crops, soil and irrigation.</p>
        </div>
        <div class="tool-card">
            <div class="tool-icon">🌦️</div>
            <h4>Weather and Research</h4>
            <p>Explore weather information and agriculture research.</p>
        </div>
        <div class="tool-card">
            <div class="tool-icon">🤖</div>
            <h4>AI Farming Assistant</h4>
            <p>Ask questions and receive crop-specific guidance.</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("## 👋 Welcome, Farmer!")
        st.caption("Enter your email to open your farming workspace.")

        with st.form("email_form"):
            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
            )

            start = st.form_submit_button(
                "🌿 Enter Green AI Studio",
                type="primary",
                use_container_width=True,
            )

        if start:
            email = email.strip().lower()

            if "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            else:
                st.session_state.email = email
                st.session_state.messages = []
                st.session_state.finished = False
                st.rerun()

    st.stop()


# --------------------------------------------------
# FINISHED SCREEN
# --------------------------------------------------

if st.session_state.finished:
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">🌿 GREEN AI STUDIO</div>
        <h1>Thank You, Farmer!</h1>
        <p>Your session has ended. Come back whenever you need farming help.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start a New Chat", type="primary"):
        start_new_chat()

    st.stop()


# --------------------------------------------------
# SIDEBAR + FARMING TOOLS
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌿 Green AI Studio")
    st.caption("Your smart farming workspace")
    st.markdown("---")

    st.markdown("### 👨‍🌾 Farmer")
    st.write(st.session_state.email)

    if st.button("💬 New Chat", use_container_width=True):
        start_new_chat()

    if st.button("📚 Chat History", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧰 Farming Tools")

    with st.expander("🔎 Farming Research"):
        research_question = st.text_area(
            "Agriculture research question",
            placeholder="Latest wheat farming recommendations...",
            key="research_question",
        )

        if st.button(
            "Search Agriculture Websites",
            key="search_agriculture_web",
        ):
            if not research_question.strip():
                st.warning("Pehle apna research question likho.")
            else:
                with st.spinner("Researching agriculture sources..."):
                    research_result = research_farming(
                        research_question.strip()
                    )

                st.markdown("### Research Results")
                st.write(research_result)

    with st.expander("🌦️ Weather"):
        city = st.text_input(
            "City name",
            key="weather_city",
            placeholder="e.g. Lahore",
        )

        if st.button("Check Weather"):
            if not city.strip():
                st.warning("Enter a city name first.")
            else:
                try:
                    with st.spinner("Checking weather..."):
                        st.write(get_weather(city.strip()))
                except Exception as error:
                    st.error(f"Weather error: {error}")

    with st.expander("📸 Crop Photo Analysis"):
        photo = st.file_uploader(
            "Upload JPG, PNG or WEBP",
            type=["jpg", "jpeg", "png", "webp"],
            key="crop_photo",
        )

        if st.button("Analyze Crop Photo"):
            if photo is None:
                st.warning("Upload a photo first.")
            else:
                temp_path = None

                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=Path(photo.name).suffix.lower(),
                    ) as temp:
                        temp.write(photo.getvalue())
                        temp_path = temp.name

                    with st.spinner("Analyzing photo..."):
                        result = analyze_crop_image(temp_path)

                    message = "📸 Crop analysis:\n\n" + str(result)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "message": message,
                    })

                    save_chat_history(
                        st.session_state.email,
                        "assistant",
                        message,
                    )

                    st.rerun()

                except Exception as error:
                    st.error(f"Photo analysis failed: {error}")

                finally:
                    if temp_path:
                        Path(temp_path).unlink(missing_ok=True)

    with st.expander("🎨 Generate Farming Image"):
        prompt = st.text_area(
            "Describe your image",
            placeholder="A healthy wheat field with irrigation",
            key="image_prompt",
        )

        if st.button("Generate Image"):
            if not prompt.strip():
                st.warning("Describe the image first.")
            else:
                try:
                    with st.spinner("Generating image..."):
                        image_path = Path(
                            generate_farming_image(prompt.strip())
                        )

                    if image_path.exists():
                        st.image(
                            str(image_path),
                            caption="AI-generated farming image",
                            use_container_width=True,
                        )
                    else:
                        st.error("Generated image file was not found.")

                except Exception as error:
                    st.error(f"Image generation failed: {error}")

    st.markdown("---")
    st.caption("🌱 Better farming starts with better information.")


# --------------------------------------------------
# CHAT HISTORY PAGE
# --------------------------------------------------

if st.session_state.page == "history":
    st.markdown(
        '<div class="section-heading">📚 Chat History</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Your saved farming conversations</div>',
        unsafe_allow_html=True,
    )

    history = get_chat_history(st.session_state.email)

    if not history:
        st.info("Abhi is email ki koi saved history nahi hai.")
    else:
        for item in history:
            role = item.get("role", "")
            message = item.get("message", "")

            if role in ("user", "assistant"):
                with st.chat_message(role):
                    st.markdown(message)

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "chat"
        st.rerun()

    st.stop()


# --------------------------------------------------
# MAIN DASHBOARD
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="eyebrow">🌿 YOUR PERSONAL FARMING COPILOT</div>
    <h1>Grow Smarter.<br>Harvest Better.</h1>
    <p>
        Welcome to Green AI Studio — ask farming questions,
        analyze crop problems, explore research and make smarter
        decisions for your farm.
    </p>
</div>
""", unsafe_allow_html=True)

# Dashboard metrics
metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("🌱 AI Assistant", "Ready")

with metric2:
    st.metric("🧠 Memory", "Enabled")

with metric3:
    st.metric("🧰 Farming Tools", "6+")

st.markdown(
    '<div class="section-heading">💬 Ask Your Farming AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">Describe your crop problem or ask any farming question.</div>',
    unsafe_allow_html=True,
)

# Suggested prompts
suggestions = [
    "🌾 Wheat farming tips",
    "🍃 Yellow leaves problem",
    "💧 Irrigation advice",
]

suggestion_cols = st.columns(3)

for index, suggestion in enumerate(suggestions):
    with suggestion_cols[index]:
        if st.button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True,
        ):
            question = suggestion.split(" ", 1)[1]
            ask_farming_question(question)
            st.rerun()


# --------------------------------------------------
# CONVERSATION
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">🌱 Your Conversation</div>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("""
    <div class="info-card">
        <h4>👋 Welcome, Farmer!</h4>
        <p>
            Ask your first question below. Your AI assistant can
            help with crop care, soil, irrigation and common plant problems.
        </p>
    </div>
    """, unsafe_allow_html=True)

for item in st.session_state.messages:
    role = item.get("role", "")
    message = item.get("message", "")

    if role in ("user", "assistant"):
        with st.chat_message(role):
            st.markdown(message)


# --------------------------------------------------
# PREMIUM CHAT INPUT
# --------------------------------------------------

st.markdown("---")

st.markdown("""
<div class="info-card">
    <h4>🌿 Your Farm. Your Questions. Smarter Decisions.</h4>
    <p>Type your question below to start a conversation with your AI farming assistant.</p>
</div>
""", unsafe_allow_html=True)

with st.form("farming_chat_form", clear_on_submit=True):
    problem = st.text_input(
        "Your farming question",
        placeholder="e.g. My wheat leaves are turning yellow...",
        label_visibility="collapsed",
    )

    send_text = st.form_submit_button(
        "🌿 Ask Smart Farming AI",
        type="primary",
        use_container_width=True,
    )

if send_text:
    if problem.strip():
        ask_farming_question(problem)
        st.rerun()
    else:
        st.warning("Pehle apna sawal likho.")


# --------------------------------------------------
# FARMING TOOLS CARDS
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">🧰 Explore Farming Tools</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">Tools to help you make informed farming decisions.</div>',
    unsafe_allow_html=True,
)

tool_columns = st.columns(3)

tool_cards = [
    (
        "🌿",
        "Crop Analysis",
        "Upload a plant photo to explore possible crop health issues.",
    ),
    (
        "🌦️",
        "Weather",
        "Check weather information for your selected city.",
    ),
    (
        "🎨",
        "Image Generation",
        "Create farming-related images with AI.",
    ),
    (
        "🔎",
        "Farming Research",
        "Explore agriculture research and source links.",
    ),
    (
        "🎙️",
        "Voice Assistant",
        "Talk to your farming assistant using live voice.",
    ),
    (
        "🧠",
        "Memory & History",
        "Continue conversations with saved history.",
    ),
]

for index, (icon, title, description) in enumerate(tool_cards):
    with tool_columns[index % 3]:
        st.markdown(
            f"""
            <div class="tool-card">
                <div class="tool-icon">{icon}</div>
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# LIVE VOICE
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">🎙️ Talk to Your Farming AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">Use your microphone for a live farming conversation.</div>',
    unsafe_allow_html=True,
)

show_live_voice()


# --------------------------------------------------
# FOOTER + FINISH
# --------------------------------------------------

st.markdown("---")

left, right = st.columns([3, 1])

with left:
    st.caption(
        "🌱 Green AI Studio · Smart tools for better farming decisions"
    )

with right:
    if st.button("🏁 Finish Chat", use_container_width=True):
        st.session_state.finished = True
        st.rerun()