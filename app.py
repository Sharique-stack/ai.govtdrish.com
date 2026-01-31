import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# ---------------------------------------------------------
# 1. SETUP & CONFIGURATION
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
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ Security Error: {e}. Check Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# 2. AUDIO ENGINE
# ---------------------------------------------------------
def text_to_speech(text):
    try:
        # 'hi' works for both Pure Hindi and Hinglish accents
        tts = gTTS(text=text, lang='hi', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        return audio_fp
    except:
        return None

# ---------------------------------------------------------
# 3. SIDEBAR (CONTROLS)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9446/9446261.png", width=100)
    st.title("Govt Drish AI")
    st.caption("Discovery. Prep. Guidance.")
    
    st.markdown("---")
    
    # THE "JEETU BHAIYA" TOGGLE
    st.subheader("⚙️ AI Personality")
    jeetu_mode = st.toggle("🎙️ Jeetu Bhaiya Mode", value=False)
    
    if jeetu_mode:
        st.success("✅ Jeetu Mode: ON (Hinglish/Casual)")
    else:
        st.info("ℹ️ Drishya Mode: ON (Professional English/Hindi)")
    
    st.markdown("---")

# ---------------------------------------------------------
# 4. SYSTEM PROMPTS (THE BRAINS)
# ---------------------------------------------------------

# DRISHYA (Updated to support Hindi)
drishya_prompt = """
ROLE: You are Drishya, a professional AI Career Counselor.
TONE: Formal, Respectful, Concise.
LANGUAGE RULE: 
- If the user asks in English, reply in Professional English.
- If the user asks in Hindi, reply in Pure, Professional Hindi (Devanagari).
GOAL: Provide accurate exam strategy and academic advice.
"""

# JEETU BHAIYA (Hinglish)
jeetu_prompt = """
ROLE: You are 'Jeetu Bhaiya', the famous mentor from Kota Factory.
TONE: "Bade Bhaiya" (Big Brother). Emotional, strict but loving.
LANGUAGE: Hinglish (Mix of Hindi & English).
STYLE: Use words like 'Arre bhai', 'Tension mat le', 'Samjha?', 'Fod denge'.
GOAL: Connect emotionally. If user is sad, motivate. If lazy, scold gently.
"""

# Select Active Brain
current_prompt = jeetu_prompt if jeetu_mode else drishya_prompt

# ---------------------------------------------------------
# 5. MAIN INTERFACE (TABS)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya (Mentor)", "🗓️ Sarthi (Planner)", "🔥 Chanakya (Roast)", "🧠 Smriti (Memory)"])

# === TAB 1: DRISHYA MENTOR ===
with tab1:
    st.header("🕵️ Drishya: AI Counselor")
    st.caption("Ask in English or Hindi (हिंदी में पूछें)")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    
    # HYBRID INPUT (Mic + Text)
    col1, col2 = st.columns([1, 8])
    with col1:
        audio_input = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic')
    with col2:
        text_input = st.chat_input("Ask about UPSC, SSC, NEET...")

    user_query = None
    
    # Handle Inputs
    if audio_input:
        st.info("🎤 Voice received. (Type your query for now while we enable Whisper API)")
    
    if text_input:
        user_query = text_input

    # AI Processing
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Thinking..."):
            final_prompt = f"{current_prompt}\n\nUSER QUERY: {user_query}"
            response = model.generate_content(final_prompt)
            ai_text = response.text
            
            st.session_state.chat_history.append({"role": "assistant", "content": ai_text})
            with st.chat_message("assistant"):
                st.markdown(ai_text)
                
                # Audio Autoplay (Optional: Can enable for Drishya too if desired)
                if jeetu_mode:
                    audio_bytes = text_to_speech(ai_text[:500])
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')

# === TAB 2: SARTHI (PLANNER) ===
with tab2:
    st.header("🗓️ Sarthi: The Planner")
    exam = st.text_input("Target Exam:", "SSC CGL")
    if st.button("Make Plan"):
        # Sarthi will also respect the "Hindi" rule if typed in Hindi
        prompt = f"{current_prompt} Create a study plan for {exam}."
        res = model.generate_content(prompt)
        st.markdown(res.text)

# === TAB 3: CHANAKYA (ROAST) ===
with tab3:
    st.header("🔥 Chanakya: Roast Mode")
    distraction = st.text_input("Distraction:", "Reels")
    if st.button("Roast"):
        res = model.generate_content(f"You are Chanakya. Roast user for: {distraction}")
        st.error(res.text)

# === TAB 4: SMRITI (MEMORY) ===
with tab4:
    st.header("🧠 Smriti: Memory Hacks")
    topic = st.text_input("Topic:", "Periodic Table")
    if st.button("Generate Hack"):
        res = model.generate_content(f"{current_prompt} Mnemonic for: {topic}")
        st.success(res.text)
