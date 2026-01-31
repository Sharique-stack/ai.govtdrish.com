import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# ---------------------------------------------------------
# 1. VISUAL SETUP (The "Yesterday" Look)
# ---------------------------------------------------------
st.set_page_config(page_title="Govt Drish AI", page_icon="🇮🇳", layout="wide")

# Hide Streamlit elements for a "Pro App" feel
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #ffffff; border-bottom: 2px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOGIC & API
# ---------------------------------------------------------
try:
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Connect API Key in Settings")
    st.stop()

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# ---------------------------------------------------------
# 3. THE "CLEAN" LAYOUT
# ---------------------------------------------------------

# Title Area (Clean & Centered)
col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.title("🇮🇳 Govt Drish AI")
with col_head2:
    # THE SWITCH IS HERE (Discrete, not in sidebar)
    jeetu_mode = st.toggle("🎙️ Jeetu Mode", value=False)

# Prompts
drishya_prompt = "You are Drishya, a professional AI Counselor. If asked in Hindi, use Pure Hindi. If English, use Professional English. Keep answers short and strategic."
jeetu_prompt = "You are Jeetu Bhaiya. Speak in Hinglish (Hindi+English). Be emotional, strict, and motivating like a big brother."

active_prompt = jeetu_prompt if jeetu_mode else drishya_prompt

# ---------------------------------------------------------
# 4. TABS (Original Order)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya Chat", "🗓️ Sarthi Planner", "🔥 Chanakya Roast", "🧠 Smriti Memory"])

# === TAB 1: DRISHYA ===
with tab1:
    # Chat Container
    chat_container = st.container()
    
    # Input Container (Bottom)
    with st.container():
        c1, c2 = st.columns([1, 10])
        with c1:
            audio_input = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='mic')
        with c2:
            text_input = st.chat_input("Ask about your exam...")

    # Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Handle Input
    user_msg = text_input
    if audio_input:
        st.toast("🎤 Voice received (Transcribing...)") # Placeholder for Whisper

    if user_msg:
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_msg)
            
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    response = model.generate_content(f"{active_prompt}\nUser: {user_msg}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    if jeetu_mode:
                        audio = text_to_speech(response.text[:400])
                        if audio:
                            st.audio(audio, format='audio/mp3')

# === TAB 2: SARTHI ===
with tab2:
    st.subheader("🗓️ Daily Study Planner")
    c1, c2 = st.columns(2)
    with c1:
        exam = st.selectbox("Exam", ["UPSC", "SSC CGL", "NEET", "Bank PO"])
    with c2:
        hrs = st.slider("Hours", 2, 12, 6)
    
    if st.button("Create Schedule"):
        res = model.generate_content(f"Create a table schedule for {exam} ({hrs} hours).")
        st.markdown(res.text)

# === TAB 3: CHANAKYA ===
with tab3:
    st.subheader("🔥 Reality Check")
    bad = st.text_input("My Distraction", "Instagram")
    if st.button("Roast Me"):
        res = model.generate_content(f"Roast user for {bad} in Hinglish.")
        st.error(res.text)
        if jeetu_mode: st.audio(text_to_speech(res.text))

# === TAB 4: SMRITI ===
with tab4:
    st.subheader("🧠 Memory Hacks")
    topic = st.text_input("Topic", "Rivers of India")
    if st.button("Generate Trick"):
        res = model.generate_content(f"Mnemonic for {topic}")
        st.success(res.text)
