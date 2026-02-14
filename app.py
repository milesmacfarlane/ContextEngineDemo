"""
Context Engine Demo - Streamlit App
Interactive demonstration of the narrative context system
"""

import streamlit as st
import sys
from pathlib import Path
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from data_manager import DataManager
    from generators.mean_generator_v2 import MeanGeneratorV2
    from context_engine import ContextEngine
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure all files are in the correct locations. See README.md for setup instructions.")
    st.stop()

# Page config
st.set_page_config(
    page_title="Context Engine Demo",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .context-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 10px 0;
    }
    .question-box {
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin: 10px 0;
    }
    .answer-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
    .stats-card {
        background-color: #fff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def load_system():
    """Load the context engine system (cached)"""
    try:
        data_manager = DataManager("data/WorksheetMergeMasterSourceFile.xlsx")
        generator = MeanGeneratorV2(data_manager, "data/ContextBanks.xlsx")
        return generator
    except Exception as e:
        st.error(f"Error loading system: {e}")
        return None

# Load generator
generator = load_system()

if generator is None:
    st.error("⚠️ Could not load the context engine. Check that all files are present.")
    st.stop()

# Header
st.markdown('<p class="main-header">🎨 Context Engine Demo</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate Statistics Questions with Rich Narratives</p>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Question Generator")
    
    # Variation selector
    st.subheader("1️⃣ Math Variation")
    variation = st.selectbox(
        "Select variation",
        ["calculate", "missing_value", "compare", "missing_count"],
        format_func=lambda x: {
            "calculate": "📊 Calculate Mean",
            "missing_value": "🎯 Find Missing Value",
            "compare": "⚖️ Compare Means",
            "missing_count": "🔢 Find Number of Values"
        }[x],
        help="Choose which type of mean question to generate"
    )
    
    # Get compatible contexts
    compatible_contexts = generator.engine.get_compatible_contexts(variation)
    
    st.subheader("2️⃣ Context")
    
    context_mode = st.radio(
        "Context selection",
        ["🎲 Random (Surprise me!)", "🎯 Choose specific context"],
        label_visibility="collapsed"
    )
    
    if context_mode == "🎯 Choose specific context":
        # Group contexts by category
        context_by_category = {}
        for ctx_id in compatible_contexts:
            meta = generator.engine.get_context_metadata(ctx_id)
            category = meta['Category']
            if category not in context_by_category:
                context_by_category[category] = []
            context_by_category[category].append((ctx_id, meta['ContextName']))
        
        # Category selector
        categories = sorted(context_by_category.keys())
        category = st.selectbox("Category", categories)
        
        # Context selector within category
        contexts_in_category = context_by_category[category]
        context_choice = st.selectbox(
            "Context",
            contexts_in_category,
            format_func=lambda x: x[1]
        )
        context_id = context_choice[0]
        
        # Show context info
        meta = generator.engine.get_context_metadata(context_id)
        with st.expander("ℹ️ Context Details"):
            st.write(f"**{meta['ContextName']}**")
            st.write(meta['Description'])
            st.write(f"**Range:** {meta['ValueMin']}-{meta['ValueMax']} {meta['Unit']}")
            st.write(f"**Category:** {meta['Category']}")
    else:
        context_id = None
        st.info(f"Will randomly select from {len(compatible_contexts)} compatible contexts")
    
    st.subheader("3️⃣ Narrative Level")
    level = st.select_slider(
        "Detail level",
        options=["minimal", "standard", "rich"],
        value="standard",
        format_func=lambda x: {
            "minimal": "📝 Minimal (1 sentence)",
            "standard": "📖 Standard (Brief scenario)",
            "rich": "📚 Rich (Full backstory)"
        }[x],
        help="Choose how much narrative detail to include"
    )
    
    st.subheader("4️⃣ Difficulty")
    difficulty = st.slider(
        "Difficulty level",
        min_value=1,
        max_value=5,
        value=2,
        help="1 = Easy, 5 = Hard"
    )
    
    st.markdown("---")
    
    # Generate button
    if st.button("🎲 Generate Question", type="primary", use_container_width=True):
        st.session_state.generate = True
    
    # Show stats
    st.markdown("---")
    st.subheader("📊 System Stats")
    st.metric("Total Contexts", 50)
    st.metric("Compatible with this variation", len(compatible_contexts))
    st.metric("Narrative Levels", 3)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Generated Question")
    
    if st.session_state.get('generate', False):
        with st.spinner("🎨 Crafting your question..."):
            try:
                # Generate question
                question = generator.generate(
                    variation=variation,
                    difficulty=difficulty,
                    context_id=context_id,
                    level=level
                )
                
                # Store in session
                st.session_state.question = question
                st.session_state.generate = False
                
                st.success("✅ Question generated!")
                
            except Exception as e:
                st.error(f"Error generating question: {e}")
                st.stop()
    
    # Display question
    if 'question' in st.session_state:
        q = st.session_state.question
        
        # Context info
        st.markdown('<div class="context-box">', unsafe_allow_html=True)
        st.markdown(f"**Context:** {q.given_data['context_id']}")
        st.markdown(f"**Level:** {q.given_data['level'].title()}")
        st.markdown(f"**Variation:** {q.given_data['variation'].replace('_', ' ').title()}")
        st.markdown(f"**Difficulty:** {q.difficulty}/5")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Question text
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown("### Question")
        st.write(q.question_text)
        st.markdown(f"**[{q.total_marks} mark{'s' if q.total_marks != 1 else ''}]**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show answer toggle
        show_answer = st.checkbox("👁️ Show Answer & Solution", value=False)
        
        if show_answer:
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Answer")
            st.markdown(f"**{q.answer}**")
            
            if q.solution_steps:
                st.markdown("### 📝 Solution Steps")
                for i, step in enumerate(q.solution_steps, 1):
                    st.text(f"{i}. {step}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Regenerate options
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🔄 Same context, new data"):
                st.session_state.generate = True
                st.rerun()
        
        with col_b:
            if st.button("🎲 Random context"):
                context_id = None
                st.session_state.generate = True
                st.rerun()
        
        with col_c:
            if st.button("📊 Change variation"):
                st.session_state.generate = False
                st.rerun()
    
    else:
        # Welcome message
        st.info("👈 Configure your question in the sidebar, then click **Generate Question**")
        
        st.markdown("### 🌟 What is the Context Engine?")
        st.write("""
        The Context Engine generates mathematics questions with **rich, engaging narratives** 
        using **50 different real-world contexts** across 13 categories.
        
        **Same math concept**, but presented in contexts students actually care about:
        - 📱 Digital (file sizes, download speeds)
        - 🏃 Fitness (heart rate, calories)
        - 🎵 Music (song duration, tempo)
        - 🚗 Transportation (commute time, speed)
        - 🏠 Household (bills, cooking time)
        - And many more!
        """)
        
        st.markdown("### ✨ Features")
        st.write("""
        - **50 Contexts** - From server tips to heart rate to file sizes
        - **3 Narrative Levels** - Minimal, standard, or rich storytelling
        - **8 Variations** - Calculate, find missing value, compare, and more
        - **Smart Compatibility** - Only generates questions that make sense
        - **Realistic Values** - Context-appropriate number ranges
        - **Automatic Units** - Proper formatting ($, %, °C, bpm, etc.)
        """)

with col2:
    st.header("📚 Examples")
    
    # Show example questions
    examples = [
        {
            "title": "💰 Server Tips (Minimal)",
            "text": "Ms. Lee works as a server. Tips over 5 days: $45, $52, $48, $50, $55. Calculate the mean.",
            "answer": "$50.00"
        },
        {
            "title": "❤️ Heart Rate (Rich)",
            "text": "Dr. Singh works as a sports medicine specialist. She is evaluating an athlete's cardiovascular fitness...",
            "answer": "Detailed scenario with exercise stages"
        },
        {
            "title": "📁 File Sizes (Standard)",
            "text": "Project file sizes recorded: 145MB, 203MB, 178MB, 195MB, 220MB. Calculate the mean file size.",
            "answer": "188.2 MB"
        },
        {
            "title": "🎵 Music Tempo",
            "text": "A DJ tracked BPM for songs: 120 bpm, 128 bpm, 115 bpm, 132 bpm, 125 bpm",
            "answer": "124.0 bpm"
        }
    ]
    
    for example in examples:
        with st.expander(example["title"]):
            st.write(example["text"])
            st.caption(f"Answer: {example['answer']}")
    
    st.markdown("---")
    
    st.header("🎯 Context Categories")
    
    categories_info = {
        "Physical": "Lengths, areas, volumes, masses",
        "Recreation": "Running, cycling, music, playlists",
        "Health": "Heart rate, calories, blood pressure",
        "Transportation": "Speeds, distances, commute times",
        "Household": "Cooking, utilities, groceries",
        "Academic": "Test scores, attendance, grades",
        "Environmental": "Temperature, rainfall, snowfall",
        "Digital": "File sizes, download speeds, data",
        "Earnings": "Tips, wages",
        "Financial": "Home prices, bills"
    }
    
    for category, description in categories_info.items():
        st.markdown(f"**{category}**")
        st.caption(description)

# Footer
st.markdown("---")
st.caption("🎨 Context Engine Demo | Built with Streamlit")
st.caption("📊 50 contexts • 3 narrative levels • 8 variations • Infinite possibilities")
