import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Govt Drish AI Lab", page_icon="🇮🇳", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Make the Buy Button pop */
            .stLinkButton > a {
                background-color: #ff4b4b;
                color: white !important;
                font-weight: bold;
                border-radius: 5px;
                text-align: center;
                display: block;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. API & REVENUE SETUP
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
except:
    st.error("⚠️ API Key Missing! Check Secrets.")
    st.stop()

# --- REVENUE ENGINE: SMART LINK MATCHER ---
def get_exam_link(user_query, selected_exam=None):
    """Finds the best matching Test Series URL"""
    
    # 1. Emergency Fallback List (Works instantly without scraper)
    default_links = {
        "ssc": "https://govtdrish.com/test-series/ssc-cgl-tier-i",
        "cgl": "https://govtdrish.com/test-series/ssc-cgl-tier-i",
        "upsc": "https://govtdrish.com/test-series/upsc-cse-prelims",
        "ias": "https://govtdrish.com/test-series/upsc-cse-prelims",
        "neet": "https://govtdrish.com/test-series/neet-ug",
        "bank": "https://govtdrish.com/test-series/sbi-po-prelims",
        "railway": "https://govtdrish.com/test-series/rrb-ntpc",
        "default": "https://govtdrish.com/test-series"
    }

    # 2. Try to load Scraper Data (If available)
    try:
        if os.path.exists("exam_links.csv"):
            df = pd.read_csv("exam_links.csv")
            # Convert to dictionary {name: url}
            scraper_links = dict(zip(df['Exam Name'].str.lower(), df['URL']))
            default_links.update(scraper_links) # Merge them
    except:
        pass # Ignore errors, stick to defaults

    # 3. Logic: Check Selected Exam OR Query Text
    search_term = selected_exam.lower() if selected_exam else user_query.lower()
    
    for key, url in default_links.items():
        if key in search_term:
            return url
            
    return default_links["default"]

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9446/9446261.png", width=80)
    st.title("🇮🇳 Govt Drish AI")
    st.markdown("---")
    
    st.subheader("⚙️ AI Personality")
    jeetu_mode = st.toggle("🎙️ Jeetu Bhaiya Mode", value=False)
    
    if jeetu_mode:
        st.success("✅ **Jeetu Mode ON**")
    else:
        st.info("ℹ️ **Drishya Mode ON**")
        
    st.markdown("---")
    st.info("💡 **Marketing Hook:**\nAI now auto-detects exams and generates 'Buy Now' buttons.")

# ==========================================
# 4. SYSTEM PROMPTS
# ==========================================
if jeetu_mode:
    persona = """
    ROLE: Jeetu Bhaiya (Mentor).
    TONE: Emotional, Hinglish, Strict.
    RULE: Always end by telling them to practice on Govt Drish.
    """
else:
    persona = """
    ROLE: Drishya (Counselor).
    TONE: Professional English/Hindi.
    RULE: Always recommend taking a mock test.
    """

# ==========================================
# 5. MAIN TABS
# ==========================================
st.title("🚀 Govt Drish: The AI Exam Companion")
tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Drishya (Counselor)", "🗓️ Sarthi (Planner)", "🔥 Chanakya (Quiz)", "🧠 Smriti (Memory)"])

# --- TAB 1: DRISHYA ---
with tab1:
    st.header("Drishya: Exam Strategy")
    
    # Hybrid Input
    c1, c2 = st.columns([1, 8])
    with c1: audio_in = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic1')
    with c2: 
        if audio_in: st.caption("Voice detected.")
    
    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 16, 40, 23)
        qual = st.selectbox("Qualification", ["10th", "12th", "Graduate", "Post Grad"])
    with col2:
        weakness = st.text_input("Weak Subject", "Maths")

    if st.button("Find Strategy"):
        with st.spinner("Analyzing..."):
            prompt = f"{persona} User: Age {age}, {qual}, Weakness: {weakness}. Suggest 2 exams and a strategy."
            res = model.generate_content(prompt)
            st.markdown(res.text)
            
            # --- THE REVENUE ENGINE ---
            # Smartly guess the exam based on qualification/weakness context
            suggested_link = get_exam_link(f"{qual} {weakness}")
            st.markdown("---")
            st.link_button("👉 Start Practicing (₹49 Only)", suggested_link)
            # --------------------------

            if jeetu_mode: st.audio(text_to_speech(res.text[:300]))

# --- TAB 2: SARTHI ---
with tab2:
    st.header("Sarthi: Study Planner")
    exam_name = st.text_input("Target Exam", "SSC CGL")
    days = st.slider("Days Left", 15, 180, 45)
    
    if st.button("Generate Plan"):
        with st.spinner("Planning..."):
            prompt = f"{persona} Create a {days}-day plan for {exam_name}. Include Govt Drish Mock Tests."
            res = model.generate_content(prompt)
            st.markdown(res.text)
            
            # --- THE REVENUE ENGINE ---
            # Direct link to the specific exam
            exam_link = get_exam_link(exam_name, exam_name)
            st.markdown("### 🚀 Execute the Plan")
            st.link_button(f"👉 Buy {exam_name} Test Series", exam_link)
            # --------------------------

            if jeetu_mode: st.audio(text_to_speech("Ye raha plan. Ab jao test lagao!"))

# --- TAB 3: CHANAKYA ---
with tab3:
    st.header("Chanakya: Quiz & Roast")
    topic = st.selectbox("Topic", ["Current Affairs", "History", "Science"])
    
    if st.button("Generate Quiz"):
        res = model.generate_content(f"{persona} Give 3 MCQs on {topic} with answers. Then roast the user.")
        st.markdown(res.text)
        
        # --- THE REVENUE ENGINE ---
        st.warning("Low Score? Improve it now.")
        st.link_button("👉 Unlock Topic Tests (₹49)", "https://govtdrish.com/test-series")

# --- TAB 4: SMRITI ---
with tab4:
    st.header("Smriti: Memory Hacks")
    txt = st.text_area("Text to Memorize")
    if st.button("Hack It"):
        res = model.generate_content(f"{persona} Mnemonic for: {txt}")
        st.success(res.text)
        if jeetu_mode: st.audio(text_to_speech(res.text))
