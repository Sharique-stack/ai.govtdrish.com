import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Govt Drish AI Lab", layout="wide")

# HIDE STREAMLIT STYLE (Optional - makes it look more pro)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- API SETUP ---
# For local dev, you can hardcode it or set it in environment variables
# st.secrets is better for deployment
api_key = st.secrets["GEMINI_API_KEY"]
# --- REPLACEMENT API SETUP ---
if api_key:
    genai.configure(api_key=api_key)
    
    # Let's find the correct flash model name automatically
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Look for the best flash model
        flash_model = next((m for m in available_models if 'flash' in m.lower()), "models/gemini-pro")
        
        model = genai.GenerativeModel(flash_model)
        st.sidebar.success(f"Connected to: {flash_model}")
    except Exception as e:
        st.error(f"Error listing models: {e}")

# --- SIDEBAR (THE BRANDING) ---
with st.sidebar:
    st.title("🇮🇳 Govt Drish AI")
    st.markdown("---")
    st.info("💡 **Marketing Hook:**\nAll outputs below are designed to funnel users to the **₹49/month Test Series**.")
    st.markdown("---")
    st.write("© 2026 Govt Drish Tech Labs")

# --- MAIN INTERFACE ---
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
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Your Age", min_value=16, max_value=40, value=23)
        qualification = st.selectbox("Qualification", ["10th Pass", "12th Pass", "Graduate (Arts)", "Graduate (Science/Tech)", "Graduate (Commerce)", "Post Graduate"])
    with col2:
        category = st.selectbox("Category", ["General", "OBC", "SC/ST", "EWS"])
        weakness = st.text_input("Your Weak Subject (e.g., 'English', 'Maths')")

    if st.button("Find My Exams", type="primary"):
        if not api_key:
            st.error("Please enter API Key first.")
        else:
            with st.spinner("Drishya is scanning 1670+ exams..."):
                prompt = f"""
                Act as 'Drishya', an expert career counselor for Govt Drish.
                User Profile: Age {age}, {qualification}, Category {category}, Weak in {weakness}.
                
                Task:
                1. Recommend top 3 Govt Exams they are eligible for in India (2026).
                2. Explain WHY based on their weakness (e.g., if weak in English, suggest Railways).
                3. STRICTLY END with a sales pitch: "Start practicing for these specific exams on Govt Drish for just ₹49/month."
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
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
        if not api_key:
            st.error("Please enter API Key first.")
        else:
            with st.spinner("Creating your strategy..."):
                prompt = f"""
                Act as 'Sarthi', a strict exam strategist.
                Create a {days_left}-day study plan for {exam_name} assuming {hours_daily} hours of study daily.
                
                CRITICAL INSTRUCTION:
                Every 3rd day, you MUST schedule a "Govt Drish Mock Test (Sectional)".
                Every Sunday, you MUST schedule a "Govt Drish Full Mock Test".
                
                Output as a clean Markdown Table.
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
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
        if not api_key:
            st.error("Please enter API Key.")
        else:
            with st.spinner(f"Chanakya is drafting questions on {topic}..."):
                prompt = f"""
                Generate 3 high-quality Multiple Choice Questions on {topic}.
                Format: 
                Q1: [Question]
                A) [Option]
                B) [Option]...
                **Correct Answer:** [Ans]
                **Explanation:** [Short Explanation with a memory trick if possible]
                
                After the 3 questions, add a "Roast": If they couldn't answer these, tell them to buy the Govt Drish ₹49 pass.
                """
                response = model.generate_content(prompt)
                st.session_state.quiz_content = response.text
                st.session_state.quiz_generated = True

    if st.session_state.quiz_generated:
        st.markdown("---")
        st.markdown(st.session_state.quiz_content)
        st.warning("⚠️ **Did you get 3/3?** If not, your competition is winning. Practice more on Govt Drish.")

# ==========================================
# TOOL 4: SMRITI - MEMORY HACKER
# ==========================================
with tab4:
    st.header("Smriti: Memorize Anything in 10 Seconds")
    st.write("Paste a hard topic, list, or dates. Get a funny trick/mnemonic.")
    
    hard_text = st.text_area("Paste text here (e.g., 'G20 Countries', 'Articles of Constitution')")
    
    if st.button("Hack My Memory"):
        if not api_key:
            st.error("Please enter API Key.")
        else:
            with st.spinner("Cooking up a trick..."):
                prompt = f"""
                Act as 'Smriti'. The user wants to remember this: "{hard_text}".
                Create a funny Mnemonic (Acronym or Hinglish sentence) to help them remember it.
                Make it weird or funny so it sticks.
                """
                response = model.generate_content(prompt)
                st.markdown("### 🧠 Your Memory Trick:")
                st.info(response.text)
                st.markdown("---")
                st.caption("powered by Govt Drish AI")