import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Govt Drish AI",
    page_icon="🇮🇳",
    layout="wide"
)

# Custom CSS for a clean, App-like feel
st.markdown("""
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Better Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 0px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
        border-bottom: 3px solid #0066cc;
        color: #0066cc;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. API & LOGIC SETUP
# ==========================================
try:
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ API Key Missing. Please check Streamlit Secrets.")
    st.stop()

def text_to_speech(text):
    """Converts text to audio bytes (Hindi accent used for Hinglish)"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# Initialize Chat History if empty
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 3. HEADER & CONTROLS
# ==========================================
col_title, col_toggle = st.columns([6, 2])

with col_title:
    st.title("🇮🇳 Govt Drish AI")

with col_toggle:
    st.write("") # Spacer
    # The Magic Switch
    jeetu_mode = st.toggle("🎙️ Jeetu Bhaiya Mode", value=False)

# ==========================================
# 4. SYSTEM PROMPTS (THE BRAIN)
# ==========================================

# PROMPT 1: DRISHYA (The Professional)
drishya_core = """
ROLE: You are Drishya, a professional AI Career Counselor for Indian government exams (UPSC, SSC, NEET).
TONE: Professional, Wise, Encouraging.
LANGUAGE RULES:
1. If the user asks in English -> Reply in Professional English.
2. If the user asks in Hindi -> Reply in Pure, Formal Hindi (Devanagari).
GOAL: Provide specific, actionable advice. Avoid fluff.
"""

# PROMPT 2: JEETU BHAIYA (The Mentor)
jeetu_core = """
ROLE: You are 'Jeetu Bhaiya', the famous coaching mentor.
TONE: "Bade Bhaiya" (Big Brother). Emotional, strict but loving.
LANGUAGE: Hinglish (Hindi + English mix).
STYLE: Use words like 'Arre beta', 'Bhai', 'Samjha?', 'Fod denge'.
GOAL: Connect emotionally. If the user is stressed, motivate them. If lazy, scold them.
"""

# Select the active personality
active_prompt = jeetu_core if jeetu_mode else drishya_core

# ==========================================
# 5. MAIN TABS (THE TOOLS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya Chat", "🗓️ Sarthi Planner", "🔥 Chanakya Roast", "🧠 Smriti Memory"])

# --- TAB 1: THE MAIN CHAT ---
with tab1:
    # 1. Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")

    # 2. Input Area (Mic + Text Side-by-Side)
    c1, c2 = st.columns([1, 8])
    
    with c1:
        # Mic Button
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='recorder')
    
    with c2:
        # Text Input
        user_text = st.chat_input("Ask about your exam strategy...")

    # 3. Process Input
    user_query = None
    
    # Check for Voice
    if audio_data:
        # Note: Without OpenAI Whisper API, we can't transact speech-to-text accurately yet.
        # This acts as the placeholder for the UI UX you requested.
        st.toast("🎤 Voice received! (Speech-to-Text module pending)")
        st.info("ℹ️ Voice Input detected. Please type your query for now (Whisper API needed for transcription).")

    # Check for Text
    if user_text:
        user_query = user_text

    # 4. Generate AI Response
    if user_query:
        # Add User Message to State
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate Reply
        with st.spinner("Thinking..." if not jeetu_mode else "Jeetu Bhaiya bol rahe hain..."):
            final_prompt = f"{active_prompt}\n\nUSER QUERY: {user_query}"
            response = model.generate_content(final_prompt)
            ai_reply = response.text
            
            # Add AI Message to State
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.markdown(ai_reply)
                
                # PLAY AUDIO (Only if Jeetu Mode is ON)
                if jeetu_mode:
                    audio_bytes = text_to_speech(ai_reply[:500]) # Speak first 500 chars for speed
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')

# --- TAB 2: SARTHI (PLANNER) ---
with tab2:
    st.subheader("🗓️ Sarthi: Daily Planner")
    c1, c2 = st.columns(2)
    with c1:
        exam = st.selectbox("Target Exam", ["UPSC CSE", "SSC CGL", "NEET UG", "Bank PO", "Railways"])
    with c2:
        hours = st.slider("Study Hours/Day", 2, 16, 8)
    
    if st.button("Generate Schedule"):
        prompt = f"{active_prompt} Create a strictly timed 1-day schedule for {exam} for a student studying {hours} hours."
        with st.spinner("Creating Plan..."):
            res = model.generate_content(prompt)
            st.markdown(res.text)
            if jeetu_mode:
                st.audio(text_to_speech("Ye raha tumhara plan. Isse follow karna padega!"))

# --- TAB 3: CHANAKYA (ROAST) ---
with tab3:
    st.subheader("🔥 Chanakya: Reality Check")
    weakness = st.text_input("My Distraction / Weakness:", "Instagram Reels")
    
    if st.button("Roast Me"):
        prompt = f"You are Chanakya. The user wastes time on {weakness}. Roast them brutally in Hinglish."
        with st.spinner("Preparing Roast..."):
            res = model.generate_content(prompt)
            st.error(res.text)
            if jeetu_mode:
                st.audio(text_to_speech(res.text))

# --- TAB 4: SMRITI (MEMORY) ---
with tab4:
    st.subheader("🧠 Smriti: Memory Hacks")
    topic = st.text_input("Topic to Memorize:", "Fundamental Rights of India")
    
    if st.button("Create Mnemonic"):
        prompt = f"{active_prompt} Create a funny, easy mnemonic to remember: {topic}."
        with st.spinner("Hacking Memory..."):
            res = model.generate_content(prompt)
            st.success(res.text)
