import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Govt Drish AI Lab", page_icon="🇮🇳", layout="wide")

# HIDE STREAMLIT BRANDING
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. API & AUDIO SETUP
# ==========================================
try:
    # Fetch API Key from Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Auto-select the best Flash model
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_model = next((m for m in available_models if 'flash' in m.lower()), "models/gemini-1.5-flash")
        model = genai.GenerativeModel(flash_model)
    except Exception as e:
        st.error(f"Model Error: {e}")
        model = genai.GenerativeModel("models/gemini-pro") # Fallback

except Exception as e:
    st.error("⚠️ API Key Missing! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

def text_to_speech(text):
    """Generates audio bytes (Hindi accent for Hinglish)"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# ==========================================
# 3. SIDEBAR (THE "CLUTTERED" BRANDING)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9446/9446261.png", width=80)
    st.title("🇮🇳 Govt Drish AI")
    st.markdown("---")
    
    # THE JEETU BHAIYA TOGGLE (Added Here)
    st.subheader("⚙️ AI Personality")
    jeetu_mode = st.toggle("🎙️ Jeetu Bhaiya Mode", value=False)
    
    if jeetu_mode:
        st.success("✅ **Jeetu Mode ON**\n(Hinglish + Voice + Motivation)")
    else:
        st.info("ℹ️ **Drishya Mode ON**\n(Professional English/Hindi)")
        
    st.markdown("---")
    st.info("💡 **Marketing Hook:**\nAll outputs below are designed to funnel users to the **₹49/month Test Series**.")
    st.markdown("---")
    st.write("© 2026 Govt Drish Tech Labs")

# ==========================================
# 4. SYSTEM PROMPTS (THE BRAIN)
# ==========================================
# Base Instructions based on Mode
if jeetu_mode:
    persona_instruction = """
    ROLE: You are 'Jeetu Bhaiya', the famous mentor.
    TONE: Emotional, "Bade Bhaiya", Strict but Loving.
    LANGUAGE: Hinglish (Hindi + English mix).
    STYLE: Use words like 'Arre beta', 'Tension mat le', 'Fod denge'.
    """
else:
    persona_instruction = """
    ROLE: You are 'Drishya', a professional expert career counselor.
    TONE: Formal, Analytical, Encouraging.
    LANGUAGE: English (default) or Pure Hindi if asked.
    """

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.title("🚀 Govt Drish: The AI Exam Companion")
st.markdown("Your personal AI team for **Selection Strategy**, **Planning**, **Practice**, and **Memory**.")

# TABS FOR THE 4 TOOLS
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya (Counselor)", "🗓️ Sarthi (Planner)", "🔥 Chanakya (Quiz)", "🧠 Smriti (Memory)"])

# ==========================================
# TOOL 1: DRISHYA - CAREER COUNSELOR
# ==========================================
with tab1:
    st.header("Drishya: Find Your Perfect Exam Match")
    st.write("Confused about eligibility? Let AI analyze your profile across 1670+ exams.")
    
    # HYBRID INPUT (Mic + Text)
    c1, c2 = st.columns([1, 8])
    with c1:
        audio_in = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic1')
    with c2:
        if audio_in: st.caption("🎤 Voice detected. Please verify your details below.")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Your Age", min_value=16, max_value=40, value=23)
        qualification = st.selectbox("Qualification", ["10th Pass", "12th Pass", "Graduate (Arts)", "Graduate (Science/Tech)", "Graduate (Commerce)", "Post Graduate"])
    with col2:
        category = st.selectbox("Category", ["General", "OBC", "SC/ST", "EWS"])
        weakness = st.text_input("Your Weak Subject (e.g., 'English', 'Maths')")

    if st.button("Find My Exams", type="primary"):
        with st.spinner("Scanning 1670+ exams..."):
            prompt = f"""
            {persona_instruction}
            User Profile: Age {age}, {qualification}, Category {category}, Weak in {weakness}.
            
            Task:
            1. Recommend top 3 Govt Exams they are eligible for in India (2026).
            2. Explain WHY based on their weakness.
            3. STRICTLY END with a sales pitch: "Start practicing for these specific exams on Govt Drish for just ₹49/month."
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
            # AUDIO OUTPUT (If Jeetu Mode)
            if jeetu_mode:
                st.audio(text_to_speech(response.text[:500])) # Speak first 500 chars
                
            st.success("👉 **Action:** Go to GovtDrish.com and search for these exams!")

# ==========================================
# TOOL 2: SARTHI - STUDY PLANNER
# ==========================================
with tab2:
    st.header("Sarthi: Your Personal Success Schedule")
    st.write("Get a day-by-day plan tailored to your free time.")
    
    exam_name = st.text_input("Target Exam (e.g., SSC CGL 2026)")
    days_left = st.slider("Days until Exam", 15, 180, 45)
    hours_daily = st.slider("Hours available per day", 2, 12, 5)
    
    if st.button("Generate Study Plan"):
        with st.spinner("Creating your strategy..."):
            prompt = f"""
            {persona_instruction}
            Create a {days_left}-day study plan for {exam_name} assuming {hours_daily} hours of study daily.
            
            CRITICAL INSTRUCTION:
            Every 3rd day, you MUST schedule a "Govt Drish Mock Test (Sectional)".
            Every Sunday, you MUST schedule a "Govt Drish Full Mock Test".
            
            Output as a clean Markdown Table.
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
            if jeetu_mode:
                st.audio(text_to_speech("Ye raha tumhara plan. Isse follow karna padega!"))
                
            st.info("💡 **Pro Tip:** Stick this on your wall. Don't miss the scheduled Mock Tests!")

# ==========================================
# TOOL 3: CHANAKYA - AI QUIZ
# ==========================================
with tab3:
    st.header("Chanakya: The 2-Minute Challenge")
    topic = st.radio("Choose your Challenge:", ["Current Affairs (Today)", "Indian Constitution", "General Science", "English Vocab"], horizontal=True)
    
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
        st.session_state.quiz_content = ""

    if st.button("Generate New Quiz"):
        with st.spinner(f"Chanakya is drafting questions on {topic}..."):
            prompt = f"""
            {persona_instruction}
            Generate 3 high-quality Multiple Choice Questions on {topic}.
            Format: 
            Q1: [Question]
            A) [Option]...
            **Correct Answer:** [Ans]
            **Explanation:** [Short Explanation]
            
            After the 3 questions, add a "Roast": If they couldn't answer these, tell them to buy the Govt Drish ₹49 pass.
            """
            response = model.generate_content(prompt)
            st.session_state.quiz_content = response.text
            st.session_state.quiz_generated = True

    if st.session_state.quiz_generated:
        st.markdown("---")
        st.markdown(st.session_state.quiz_content)
        
        if jeetu_mode:
            st.audio(text_to_speech("Jawab soch samajh ke dena!"))
            
        st.warning("⚠️ **Did you get 3/3?** If not, your competition is winning. Practice more on Govt Drish.")

# ==========================================
# TOOL 4: SMRITI - MEMORY HACKER
# ==========================================
with tab4:
    st.header("Smriti: Memorize Anything in 10 Seconds")
    st.write("Paste a hard topic, list, or dates. Get a funny trick/mnemonic.")
    
    hard_text = st.text_area("Paste text here (e.g., 'G20 Countries', 'Articles of Constitution')")
    
    if st.button("Hack My Memory"):
        with st.spinner("Cooking up a trick..."):
            prompt = f"""
            {persona_instruction}
            The user wants to remember this: "{hard_text}".
            Create a funny Mnemonic (Acronym or Hinglish sentence) to help them remember it.
            Make it weird or funny so it sticks.
            """
            response = model.generate_content(prompt)
            st.markdown("### 🧠 Your Memory Trick:")
            st.info(response.text)
            
            if jeetu_mode:
                st.audio(text_to_speech(response.text))
                
            st.markdown("---")
            st.caption("powered by Govt Drish AI")
