import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
import random

# ---------------------------------------------------------
# 1. SETUP & CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Govt Drish AI", page_icon="🇮🇳", layout="wide")

# HIDE BRANDING
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# API KEY CHECK
try:
    # Look for GEMINI_API_KEY in secrets
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ API Key Error: {e}. Check Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# 2. AUDIO ENGINE
# ---------------------------------------------------------
def text_to_speech(text):
    """Generates audio bytes for the response"""
    try:
        # We use Hindi 'hi' to capture the Indian accent for Hinglish
        tts = gTTS(text=text, lang='hi', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        return audio_fp
    except:
        return None

# ---------------------------------------------------------
# 3. SIDEBAR: THE CONTROL CENTER
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9446/9446261.png", width=80)
    st.title("Govt Drish AI")
    st.caption("Discovery. Prep. Guidance.")
    
    st.markdown("---")
    
    # THE MAGIC TOGGLE
    st.subheader("🧠 AI Persona")
    jeetu_mode = st.toggle("🎙️ Jeetu Bhaiya Mode", value=False)
    
    if jeetu_mode:
        st.success("✅ Jeetu Bhaiya is Online!")
        st.info("Expect Hinglish answers & Audio support.")
    else:
        st.info("ℹ️ Drishya (Professional Mode) Active.")

    st.markdown("---")
    
# ---------------------------------------------------------
# 4. SYSTEM PROMPTS (THE BRAINS)
# ---------------------------------------------------------

# DRISHYA (Professional)
drishya_core = """
You are Drishya, a professional AI Career Counselor for Indian government exams.
Tone: Professional, Analytical, Encouraging.
Language: English (unless asked for Hindi).
Goal: Provide accurate exam data and study strategies.
"""

# JEETU BHAIYA (Emotional/Hinglish)
jeetu_core = """
You are 'Jeetu Bhaiya', the famous mentor from Kota Factory.
Tone: "Bhaiya" (Big Brother), Emotional, Strict but loving.
Language: Hinglish (Mix of Hindi & English).
Style: Use words like 'Arre bhai', 'Tension mat le', 'Samjha?', 'Fod denge'.
Goal: Connect emotionally. If the user is stressed, motivate them. If lazy, scold them.
"""

# Select the active brain
active_prompt = jeetu_core if jeetu_mode else drishya_core

# ---------------------------------------------------------
# 5. UI LAYOUT
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya Chat", "🗓️ Sarthi (Planner)", "🔥 Chanakya (Roast)", "🧠 Smriti (Memory)"])

# === TAB 1: DRISHYA CHAT (The Main Interface) ===
with tab1:
    st.subheader("💬 Ask Drishya")
    if jeetu_mode:
        st.caption("🎤 Jeetu Bhaiya is listening...")
    else:
        st.caption("Professional Career Guidance")

    # Chat History Container
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Area
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # 1. Show User Message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Generate AI Response
        with st.spinner("Thinking..." if not jeetu_mode else "Jeetu Bhaiya bol rahe hain..."):
            final_prompt = f"{active_prompt}\n\nUSER QUERY: {user_input}"
            response = model.generate_content(final_prompt)
            ai_reply = response.text

            # 3. Show AI Message
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.markdown(ai_reply)
                
                # 4. AUDIO (Only if Jeetu Mode is ON)
                if jeetu_mode:
                    audio_bytes = text_to_speech(ai_reply[:500]) # Limit audio length for speed
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')

# === TAB 2: SARTHI (Planner) ===
with tab2:
    st.header("🗓️ Sarthi: Study Planner")
    col1, col2 = st.columns(2)
    with col1:
        exam_name = st.selectbox("Exam:", ["SSC CGL", "UPSC CSE", "NEET", "Bank PO"])
    with col2:
        hours = st.slider("Daily Hours:", 2, 14, 6)
    
    if st.button("Generate Plan"):
        prompt = f"{active_prompt} Create a realistic 1-day schedule for {exam_name} for a student studying {hours} hours."
        res = model.generate_content(prompt)
        st.markdown(res.text)

# === TAB 3: CHANAKYA (Roast Mode) ===
with tab3:
    st.header("🔥 Chanakya: The Reality Check")
    distraction = st.text_input("My biggest distraction is:", "Instagram Reels")
    if st.button("Roast Me"):
        roast_prompt = f"You are Chanakya. The user is wasting time on {distraction}. Roast them brutally in Hinglish."
        res = model.generate_content(roast_prompt)
        st.error(res.text)
        if jeetu_mode:
             audio = text_to_speech(res.text)
             st.audio(audio)

# === TAB 4: SMRITI (Memory Hacks) ===
with tab4:
    st.header("🧠 Smriti: Mnemonic Generator")
    topic = st.text_input("Topic to remember (e.g., Mughal Emperors):")
    if st.button("Create Hack"):
        hack_prompt = f"{active_prompt} Create a funny mnemonic/trick to remember: {topic}."
        res = model.generate_content(hack_prompt)
        st.success(res.text)
