"""
Context Engine Demo - Streamlit App with PDF Generation
Interactive demonstration of the narrative context system + PDF export
"""

import streamlit as st
import sys
from pathlib import Path
import random
from datetime import datetime

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

# Import PDF generator
try:
    from math_pdf_generator import MathAssessmentGenerator
except ImportError:
    st.warning("PDF generator not found. PDF export will be disabled.")
    MathAssessmentGenerator = None

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
    .pdf-section {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
        margin: 20px 0;
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
        pdf_generator = MathAssessmentGenerator() if MathAssessmentGenerator else None
        return generator, pdf_generator
    except Exception as e:
        st.error(f"Error loading system: {e}")
        return None, None

# Load generators
generator, pdf_generator = load_system()

if generator is None:
    st.error("⚠️ Could not load the context engine. Check that all files are present.")
    st.stop()

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'single'  # 'single' or 'pdf'

# Header
st.markdown('<p class="main-header">🎨 Context Engine Demo</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate Statistics Questions with Rich Narratives</p>', unsafe_allow_html=True)

# Mode selector
col_mode1, col_mode2 = st.columns(2)
with col_mode1:
    if st.button("📝 Single Question Mode", use_container_width=True, 
                 type="primary" if st.session_state.mode == 'single' else "secondary"):
        st.session_state.mode = 'single'
        st.rerun()

with col_mode2:
    if st.button("📄 PDF Generation Mode", use_container_width=True,
                 type="primary" if st.session_state.mode == 'pdf' else "secondary",
                 disabled=pdf_generator is None):
        st.session_state.mode = 'pdf'
        st.rerun()

st.markdown("---")

# =======================
# SINGLE QUESTION MODE
# =======================
if st.session_state.mode == 'single':
    
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
                "minimal": "📄 Minimal (1 sentence)",
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
            - **4 Variations** - Calculate, find missing value, compare, and more
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

# =======================
# PDF GENERATION MODE
# =======================
else:
    with st.sidebar:
        st.header("📄 PDF Generation")
        
        st.subheader("1️⃣ Assessment Type")
        assessment_type = st.selectbox(
            "Type",
            ["practice", "worksheet", "quiz", "test"],
            format_func=lambda x: {
                "practice": "📝 Practice Page (Single Skill)",
                "worksheet": "📋 Worksheet (Multiple Skills)",
                "quiz": "📊 Quiz (Progressive Difficulty)",
                "test": "📖 Test (Comprehensive)"
            }[x]
        )
        
        st.subheader("2️⃣ Question Settings")
        
        if assessment_type == "practice":
            # Variation selector first
            st.write("**Variation:**")
            selected_variation = st.selectbox(
                "Question type",
                ["calculate", "missing_value", "compare", "missing_count"],
                format_func=lambda x: {
                    "calculate": "📊 Calculate Mean",
                    "missing_value": "🎯 Find Missing Value",
                    "compare": "⚖️ Compare Means",
                    "missing_count": "🔢 Find Number of Values"
                }[x],
                key="practice_variation"
            )
            
            # Single context for practice
            st.write("**Context:**")
            # Get only compatible contexts for this variation
            compatible_contexts = generator.engine.get_compatible_contexts(selected_variation)
            
            # Group by category
            context_by_category = {}
            for ctx_id in compatible_contexts:
                meta = generator.engine.get_context_metadata(ctx_id)
                category = meta['Category']
                if category not in context_by_category:
                    context_by_category[category] = []
                context_by_category[category].append((ctx_id, meta['ContextName']))
            
            categories = sorted(context_by_category.keys())
            category = st.selectbox("Category", categories, key="pdf_category")
            
            contexts_in_category = context_by_category[category]
            context_choice = st.selectbox(
                "Context",
                contexts_in_category,
                format_func=lambda x: x[1],
                key="pdf_context"
            )
            selected_contexts = [context_choice[0]]
            
            num_questions = st.slider("Number of questions", 3, 15, 5)
            
        elif assessment_type == "worksheet":
            # Variation selector
            st.write("**Variations to include:**")
            available_variations = ["calculate", "missing_value", "compare", "missing_count"]
            selected_variations = st.multiselect(
                "Select 1-4 variations",
                available_variations,
                default=["calculate"],
                format_func=lambda x: {
                    "calculate": "📊 Calculate Mean",
                    "missing_value": "🎯 Find Missing Value",
                    "compare": "⚖️ Compare Means",
                    "missing_count": "🔢 Find Number of Values"
                }[x],
                max_selections=4,
                key="worksheet_variations"
            )
            
            if not selected_variations:
                st.warning("Please select at least one variation")
                selected_contexts = []
            else:
                # Multiple contexts
                st.write("**Select 2-4 Skills:**")
                # Get contexts compatible with ANY of the selected variations
                all_compatible = set()
                for var in selected_variations:
                    all_compatible.update(generator.engine.get_compatible_contexts(var))
                all_contexts = list(all_compatible)
                
                # Simplified: just show all contexts
                available = [(ctx, generator.engine.get_context_metadata(ctx)['ContextName']) 
                            for ctx in all_contexts]
                
                selected = st.multiselect(
                    "Contexts",
                    available,
                    format_func=lambda x: x[1],
                    max_selections=4,
                    key="worksheet_contexts"
                )
                
                selected_contexts = [s[0] for s in selected] if selected else []
            
            num_questions_per = st.slider("Questions per skill", 2, 8, 3)
            
        elif assessment_type == "quiz":
            # Variation selector
            st.write("**Variations to include:**")
            available_variations = ["calculate", "missing_value", "compare", "missing_count"]
            selected_variations = st.multiselect(
                "Select 1-3 variations",
                available_variations,
                default=["calculate"],
                format_func=lambda x: {
                    "calculate": "📊 Calculate Mean",
                    "missing_value": "🎯 Find Missing Value",
                    "compare": "⚖️ Compare Means",
                    "missing_count": "🔢 Find Number of Values"
                }[x],
                max_selections=3,
                key="quiz_variations"
            )
            
            if not selected_variations:
                st.warning("Please select at least one variation")
                selected_contexts = []
            else:
                # 2-3 contexts with difficulty progression
                st.write("**Select 2-3 Skills:**")
                # Get contexts compatible with ANY of the selected variations
                all_compatible = set()
                for var in selected_variations:
                    all_compatible.update(generator.engine.get_compatible_contexts(var))
                all_contexts = list(all_compatible)
                
                available = [(ctx, generator.engine.get_context_metadata(ctx)['ContextName']) 
                            for ctx in all_contexts]
                
                selected = st.multiselect(
                    "Contexts",
                    available,
                    format_func=lambda x: x[1],
                    max_selections=3,
                    key="quiz_contexts"
                )
                
                selected_contexts = [s[0] for s in selected] if selected else []
            
            num_questions_per = st.slider("Questions per skill", 2, 5, 3)
            
        else:  # test
            # All available contexts
            st.write("**Variations to include:**")
            available_variations = ["calculate", "missing_value", "compare", "missing_count"]
            selected_variations = st.multiselect(
                "Select variations for test",
                available_variations,
                default=["calculate", "missing_value"],
                format_func=lambda x: {
                    "calculate": "📊 Calculate Mean",
                    "missing_value": "🎯 Find Missing Value",
                    "compare": "⚖️ Compare Means",
                    "missing_count": "🔢 Find Number of Values"
                }[x],
                key="test_variations"
            )
            
            if not selected_variations:
                st.warning("Please select at least one variation")
                selected_contexts = []
            else:
                st.write("**Comprehensive test across compatible skills**")
                # Get contexts compatible with ALL selected variations
                if len(selected_variations) == 1:
                    compatible_set = set(generator.engine.get_compatible_contexts(selected_variations[0]))
                else:
                    # Intersection: only contexts that support ALL variations
                    compatible_set = set(generator.engine.get_compatible_contexts(selected_variations[0]))
                    for var in selected_variations[1:]:
                        compatible_set &= set(generator.engine.get_compatible_contexts(var))
                
                selected_contexts = list(compatible_set)[:8]  # Limit to 8 contexts for tests
                st.info(f"Using {len(selected_contexts)} contexts that support all selected variations")
            
            num_questions_total = st.slider("Total questions", 10, 30, 15)
        
        st.subheader("3️⃣ Difficulty")
        if assessment_type in ["practice", "worksheet"]:
            difficulty = st.slider("Difficulty level", 1, 5, 2, key="pdf_difficulty")
        else:  # quiz or test - progressive
            st.info("Difficulty will progress from Easy → Hard")
            difficulty = None
        
        st.subheader("4️⃣ Answer Key")
        answer_key_option = st.radio(
            "Include answer key?",
            ["No answer key", "Answers only", "Full solutions with steps"],
            key="answer_key"
        )
        
        answer_key_type = {
            "No answer key": None,
            "Answers only": "answers_only",
            "Full solutions with steps": "with_steps"
        }[answer_key_option]
        
        st.markdown("---")
        
        # Generate PDF button
        can_generate = False
        if assessment_type == "practice":
            can_generate = len(selected_contexts) == 1
        elif assessment_type in ["worksheet", "quiz"]:
            can_generate = len(selected_contexts) >= 2 and len(selected_variations) >= 1
        elif assessment_type == "test":
            can_generate = len(selected_contexts) >= 3 and len(selected_variations) >= 1
        
        if st.button("📄 Generate PDF", type="primary", use_container_width=True, disabled=not can_generate):
            st.session_state.generate_pdf = True
    
    # Main content
    st.header("PDF Assessment Generator")
    
    if not can_generate:
        st.warning("👈 Please configure the assessment settings in the sidebar")
        
        st.markdown("### 📄 PDF Assessment Types")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Practice Page")
            st.write("""
            - **Single skill** focus
            - 3-15 questions
            - Same difficulty level
            - Great for homework or classwork
            """)
            
            st.markdown("#### 📊 Quiz")
            st.write("""
            - **2-3 skills**
            - Progressive difficulty (Easy → Hard)
            - 6-15 questions total
            - Includes difficulty indicators
            """)
        
        with col2:
            st.markdown("#### 📋 Worksheet")
            st.write("""
            - **2-4 skills**
            - Multiple questions per skill
            - Mixed practice
            - Great for review
            """)
            
            st.markdown("#### 📖 Test")
            st.write("""
            - **Comprehensive** assessment
            - Multiple skills
            - Progressive difficulty
            - 10-30 questions
            """)
    
    elif st.session_state.get('generate_pdf', False):
        with st.spinner("📄 Generating PDF assessment..."):
            try:
                # Generate questions
                questions_for_pdf = []
                
                if assessment_type == "practice":
                    # Single context, multiple questions with selected variation
                    context_id = selected_contexts[0]
                    
                    for i in range(num_questions):
                        q = generator.generate(
                            variation=selected_variation,
                            difficulty=difficulty,
                            context_id=context_id,
                            level="standard"
                        )
                        questions_for_pdf.append({
                            'question': q.question_text,
                            'answer': q.answer,
                            'steps': q.solution_steps,
                            'difficulty': 'Easy' if difficulty <= 2 else 'Medium' if difficulty <= 3 else 'Hard'
                        })
                    
                    # Generate PDF
                    meta = generator.engine.get_context_metadata(context_id)
                    variation_name = {
                        "calculate": "Calculate Mean",
                        "missing_value": "Find Missing Value",
                        "compare": "Compare Means",
                        "missing_count": "Find Number of Values"
                    }[selected_variation]
                    
                    filename = pdf_generator.create_practice_page(
                        skill_name=f"{meta['ContextName']} - {variation_name}",
                        questions=questions_for_pdf,
                        answer_key_type=answer_key_type
                    )
                    
                elif assessment_type == "worksheet":
                    # Multiple contexts, rotate through variations
                    skill_sections = []
                    
                    for context_id in selected_contexts:
                        section_questions = []
                        
                        # Rotate through selected variations for each context
                        for i in range(num_questions_per):
                            variation = selected_variations[i % len(selected_variations)]
                            
                            # Check if this context supports this variation
                            compatible = generator.engine.get_compatible_contexts(variation)
                            if context_id not in compatible:
                                # Skip this variation for this context
                                continue
                            
                            q = generator.generate(
                                variation=variation,
                                difficulty=difficulty,
                                context_id=context_id,
                                level="standard"
                            )
                            section_questions.append({
                                'question': q.question_text,
                                'answer': q.answer,
                                'steps': q.solution_steps,
                                'difficulty': 'Easy' if difficulty <= 2 else 'Medium' if difficulty <= 3 else 'Hard'
                            })
                        
                        if section_questions:  # Only add if we generated questions
                            meta = generator.engine.get_context_metadata(context_id)
                            skill_sections.append({
                                'skill_name': meta['ContextName'],
                                'questions': section_questions
                            })
                    
                    filename = pdf_generator.create_worksheet(
                        title="Mean Calculation Worksheet",
                        skill_sections=skill_sections,
                        answer_key_type=answer_key_type
                    )
                
                elif assessment_type == "quiz":
                    # Progressive difficulty with selected variations
                    skill_sections = []
                    difficulties = [1, 2, 3]  # Easy, Medium, Hard
                    
                    for context_id in selected_contexts:
                        section_questions = []
                        
                        for i, diff in enumerate(difficulties[:num_questions_per]):
                            # Rotate through selected variations
                            variation = selected_variations[i % len(selected_variations)]
                            
                            # Check compatibility
                            compatible = generator.engine.get_compatible_contexts(variation)
                            if context_id not in compatible:
                                continue
                            
                            q = generator.generate(
                                variation=variation,
                                difficulty=diff,
                                context_id=context_id,
                                level="standard"
                            )
                            section_questions.append({
                                'question': q.question_text,
                                'answer': q.answer,
                                'steps': q.solution_steps,
                                'difficulty': 'Easy' if diff <= 2 else 'Medium' if diff <= 3 else 'Hard'
                            })
                        
                        if section_questions:
                            meta = generator.engine.get_context_metadata(context_id)
                            skill_sections.append({
                                'skill_name': meta['ContextName'],
                                'questions': section_questions
                            })
                    
                    filename = pdf_generator.create_quiz(
                        title="Mean Calculation Quiz",
                        skill_sections=skill_sections,
                        answer_key_type=answer_key_type
                    )
                
                else:  # test
                    # Comprehensive test with selected variations
                    all_questions = []
                    difficulties = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5] * 3  # Progressive
                    
                    questions_per_context = num_questions_total // len(selected_contexts) if selected_contexts else 0
                    
                    for context_id in selected_contexts:
                        for i in range(questions_per_context):
                            # Rotate through variations
                            variation = selected_variations[i % len(selected_variations)]
                            diff = difficulties[i % len(difficulties)]
                            
                            q = generator.generate(
                                variation=variation,
                                difficulty=diff,
                                context_id=context_id,
                                level="standard"
                            )
                            
                            meta = generator.engine.get_context_metadata(context_id)
                            all_questions.append({
                                'question': q.question_text,
                                'answer': q.answer,
                                'steps': q.solution_steps,
                                'difficulty': 'Easy' if diff <= 2 else 'Medium' if diff <= 3 else 'Hard',
                                'skill_name': meta['ContextName']
                            })
                    
                    # Sort by difficulty
                    all_questions.sort(key=lambda x: ['Easy', 'Medium', 'Hard'].index(x['difficulty']))
                    
                    filename = pdf_generator.create_test(
                        title="Grade 12 Essential Mathematics - Mean Calculation Test",
                        all_skills_questions=all_questions,
                        answer_key_type=answer_key_type
                    )
                
                st.session_state.generate_pdf = False
                st.session_state.pdf_file = filename
                
                # Don't rerun - let the download section appear below
                
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Show download button if PDF generated
    if 'pdf_file' in st.session_state and st.session_state.pdf_file:
        # Clear the generation flag
        st.session_state.generate_pdf = False
        
        # Big success banner
        st.success("🎉 **PDF Generated Successfully!**")
        st.balloons()  # Celebrate when download is ready
        
        st.markdown('<div class="pdf-section">', unsafe_allow_html=True)
        
        # Read PDF file
        try:
            with open(st.session_state.pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            # Create filename for download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_name = f"{assessment_type}_{timestamp}.pdf"
            
            # Show PDF info
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("Assessment Type", assessment_type.title())
                st.metric("Answer Key", answer_key_option)
            with col_info2:
                if assessment_type == "practice":
                    st.metric("Questions", len(questions_for_pdf))
                    st.metric("Variation", selected_variation.replace('_', ' ').title())
                elif assessment_type in ["worksheet", "quiz"]:
                    total_q = sum(len(section['questions']) for section in skill_sections)
                    st.metric("Total Questions", total_q)
                    st.metric("Skills", len(selected_contexts))
                else:  # test
                    st.metric("Total Questions", len(all_questions))
                    st.metric("Variations", len(selected_variations))
            
            st.markdown("---")
            
            # Big prominent download button
            st.markdown("### 📥 Ready to Download")
            st.download_button(
                label=f"⬇️ Download {assessment_type.title()} PDF",
                data=pdf_bytes,
                file_name=download_name,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
            st.info(f"💡 **Tip:** The file will be saved as `{download_name}` in your Downloads folder")
            
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Generate another button
        col_again1, col_again2 = st.columns([1, 1])
        with col_again1:
            if st.button("🔄 Generate Another PDF", use_container_width=True):
                st.session_state.pdf_file = None
                st.rerun()
        with col_again2:
            if st.button("📝 Back to Single Question Mode", use_container_width=True):
                st.session_state.mode = 'single'
                st.session_state.pdf_file = None
                st.rerun()

# Footer
st.markdown("---")
st.caption("🎨 Context Engine Demo | Built with Streamlit")
st.caption("📊 50 contexts • 3 narrative levels • 4 variations • PDF export • Infinite possibilities")
