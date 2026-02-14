"""
Mathematics Assessment PDF Generator
Creates practice pages, worksheets, quizzes, and tests with optional answer keys
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import random


class MathAssessmentGenerator:
    """Generate mathematics assessment PDFs"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for assessments"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='AssessmentTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Header info style
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Question number style
        self.styles.add(ParagraphStyle(
            name='QuestionNumber',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            leftIndent=0
        ))
        
        # Question text style
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20
        ))
        
        # Answer style
        self.styles.add(ParagraphStyle(
            name='AnswerText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d5016'),
            leftIndent=40,
            spaceAfter=6
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
    
    def create_practice_page(self, skill_name, questions, answer_key_type=None, filename=None):
        """
        Create a practice page focusing on a single skill
        
        Args:
            skill_name: Name of the skill being practiced
            questions: List of question dictionaries
            answer_key_type: None, 'answers_only', or 'with_steps'
            filename: Output filename (default: auto-generated)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/mnt/user-data/outputs/practice_{skill_name.replace(' ', '_')}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("Mathematics Practice", self.styles['AssessmentTitle']))
        story.append(Paragraph(f"Skill: {skill_name}", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Student info section
        info_table = Table([
            ['Name: _______________________________', f'Date: {datetime.now().strftime("%B %d, %Y")}'],
            ['', f'Questions: {len(questions)}']
        ], colWidths=[4*inch, 2.5*inch])
        
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Questions
        for i, q in enumerate(questions, 1):
            story.append(Paragraph(f"Question {i}", self.styles['QuestionNumber']))
            story.append(Paragraph(q['question'], self.styles['QuestionText']))
            story.append(Spacer(1, 0.15*inch))
        
        # Answer key on separate page if requested
        if answer_key_type:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", self.styles['AssessmentTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            for i, q in enumerate(questions, 1):
                story.append(Paragraph(f"Question {i}", self.styles['QuestionNumber']))
                
                if answer_key_type == 'answers_only':
                    story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                elif answer_key_type == 'with_steps':
                    story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                    if 'steps' in q and q['steps']:
                        story.append(Paragraph("Steps:", self.styles['AnswerText']))
                        for step in q['steps']:
                            story.append(Paragraph(f"• {step}", self.styles['AnswerText']))
                
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return filename
    
    def create_worksheet(self, title, skill_sections, answer_key_type=None, filename=None):
        """
        Create a worksheet with multiple skills
        
        Args:
            title: Worksheet title
            skill_sections: List of dicts with 'skill_name' and 'questions'
            answer_key_type: None, 'answers_only', or 'with_steps'
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/mnt/user-data/outputs/worksheet_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        
        # Header
        story.append(Paragraph(title, self.styles['AssessmentTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Student info
        total_questions = sum(len(section['questions']) for section in skill_sections)
        info_table = Table([
            ['Name: _______________________________', f'Date: {datetime.now().strftime("%B %d, %Y")}'],
            ['', f'Total Questions: {total_questions}']
        ], colWidths=[4*inch, 2.5*inch])
        
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Instructions
        story.append(Paragraph("Instructions: Complete all questions. Show your work.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Sections
        question_num = 1
        for section in skill_sections:
            story.append(Paragraph(f"Skill: {section['skill_name']}", self.styles['SectionHeader']))
            
            for q in section['questions']:
                story.append(Paragraph(f"Question {question_num}", self.styles['QuestionNumber']))
                story.append(Paragraph(q['question'], self.styles['QuestionText']))
                story.append(Spacer(1, 0.15*inch))
                question_num += 1
            
            story.append(Spacer(1, 0.15*inch))
        
        # Answer key
        if answer_key_type:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", self.styles['AssessmentTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            question_num = 1
            for section in skill_sections:
                story.append(Paragraph(f"Skill: {section['skill_name']}", self.styles['SectionHeader']))
                
                for q in section['questions']:
                    story.append(Paragraph(f"Question {question_num}", self.styles['QuestionNumber']))
                    
                    if answer_key_type == 'answers_only':
                        story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                    elif answer_key_type == 'with_steps':
                        story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                        if 'steps' in q and q['steps']:
                            story.append(Paragraph("Steps:", self.styles['AnswerText']))
                            for step in q['steps']:
                                story.append(Paragraph(f"• {step}", self.styles['AnswerText']))
                    
                    story.append(Spacer(1, 0.08*inch))
                    question_num += 1
        
        doc.build(story)
        return filename
    
    def create_quiz(self, title, skill_sections, answer_key_type=None, filename=None):
        """
        Create a quiz with increasing difficulty
        
        Args:
            title: Quiz title
            skill_sections: List of dicts with 'skill_name' and 'questions' (sorted by difficulty)
            answer_key_type: None, 'answers_only', or 'with_steps'
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/mnt/user-data/outputs/quiz_{timestamp}.pdf"
        
        # Similar to worksheet but with difficulty indicators
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        
        # Header
        story.append(Paragraph(title, self.styles['AssessmentTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Student info
        total_questions = sum(len(section['questions']) for section in skill_sections)
        info_table = Table([
            ['Name: _______________________________', f'Date: {datetime.now().strftime("%B %d, %Y")}'],
            ['', f'Total Questions: {total_questions}'],
            ['', 'Score: ______ / ______']
        ], colWidths=[4*inch, 2.5*inch])
        
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Instructions
        story.append(Paragraph("Instructions: Answer all questions. Show your work for full credit. "
                              "Questions increase in difficulty.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Sections with difficulty progression
        question_num = 1
        for section in skill_sections:
            story.append(Paragraph(f"Skill: {section['skill_name']}", self.styles['SectionHeader']))
            
            for i, q in enumerate(section['questions']):
                # Add difficulty indicator
                difficulty = q.get('difficulty', 'Medium')
                story.append(Paragraph(f"Question {question_num} ({difficulty})", 
                                      self.styles['QuestionNumber']))
                story.append(Paragraph(q['question'], self.styles['QuestionText']))
                story.append(Spacer(1, 0.15*inch))
                question_num += 1
            
            story.append(Spacer(1, 0.15*inch))
        
        # Answer key
        if answer_key_type:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", self.styles['AssessmentTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            question_num = 1
            for section in skill_sections:
                story.append(Paragraph(f"Skill: {section['skill_name']}", self.styles['SectionHeader']))
                
                for q in section['questions']:
                    difficulty = q.get('difficulty', 'Medium')
                    story.append(Paragraph(f"Question {question_num} ({difficulty})", 
                                          self.styles['QuestionNumber']))
                    
                    if answer_key_type == 'answers_only':
                        story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                    elif answer_key_type == 'with_steps':
                        story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                        if 'steps' in q and q['steps']:
                            story.append(Paragraph("Steps:", self.styles['AnswerText']))
                            for step in q['steps']:
                                story.append(Paragraph(f"• {step}", self.styles['AnswerText']))
                    
                    story.append(Spacer(1, 0.08*inch))
                    question_num += 1
        
        doc.build(story)
        return filename
    
    def create_test(self, title, all_skills_questions, answer_key_type=None, filename=None):
        """
        Create a comprehensive test with all skills at increasing difficulty
        
        Args:
            title: Test title
            all_skills_questions: List of question dicts sorted by difficulty across all skills
            answer_key_type: None, 'answers_only', or 'with_steps'
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/mnt/user-data/outputs/test_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        
        # Header
        story.append(Paragraph(title, self.styles['AssessmentTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Student info
        info_table = Table([
            ['Name: _______________________________', f'Date: {datetime.now().strftime("%B %d, %Y")}'],
            ['Class: _______________________________', f'Total Questions: {len(all_skills_questions)}'],
            ['', 'Score: ______ / ______']
        ], colWidths=[4*inch, 2.5*inch])
        
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Instructions
        story.append(Paragraph("Instructions:", self.styles['Heading2']))
        story.append(Paragraph("• Read each question carefully", self.styles['Normal']))
        story.append(Paragraph("• Show all your work for full credit", self.styles['Normal']))
        story.append(Paragraph("• Questions progress from easier to more challenging", self.styles['Normal']))
        story.append(Paragraph("• Use the back of pages if you need more space", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Questions
        for i, q in enumerate(all_skills_questions, 1):
            difficulty = q.get('difficulty', 'Medium')
            skill = q.get('skill_name', '')
            
            story.append(Paragraph(f"Question {i} - {skill} ({difficulty})", 
                                  self.styles['QuestionNumber']))
            story.append(Paragraph(q['question'], self.styles['QuestionText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Answer key
        if answer_key_type:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", self.styles['AssessmentTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            for i, q in enumerate(all_skills_questions, 1):
                difficulty = q.get('difficulty', 'Medium')
                skill = q.get('skill_name', '')
                
                story.append(Paragraph(f"Question {i} - {skill} ({difficulty})", 
                                      self.styles['QuestionNumber']))
                
                if answer_key_type == 'answers_only':
                    story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                elif answer_key_type == 'with_steps':
                    story.append(Paragraph(f"Answer: {q['answer']}", self.styles['AnswerText']))
                    if 'steps' in q and q['steps']:
                        story.append(Paragraph("Steps:", self.styles['AnswerText']))
                        for step in q['steps']:
                            story.append(Paragraph(f"• {step}", self.styles['AnswerText']))
                
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return filename


# Example usage and demo
def create_demo_assessments():
    """Create sample assessments to demonstrate the system"""
    
    generator = MathAssessmentGenerator()
    
    # Sample questions for mean calculation
    sample_questions_easy = [
        {
            'question': 'Ms. Lee works as a server. Tips over 5 days: $45, $52, $48, $50, $55. Calculate the mean daily tips.',
            'answer': '$50',
            'steps': [
                'Add all values: $45 + $52 + $48 + $50 + $55 = $250',
                'Count the number of values: 5',
                'Divide sum by count: $250 ÷ 5 = $50'
            ],
            'difficulty': 'Easy'
        },
        {
            'question': 'Test scores: 78%, 85%, 72%, 90%, 88%. Find the mean test score.',
            'answer': '82.6%',
            'steps': [
                'Add all scores: 78 + 85 + 72 + 90 + 88 = 413',
                'Count the number of scores: 5',
                'Divide sum by count: 413 ÷ 5 = 82.6%'
            ],
            'difficulty': 'Easy'
        }
    ]
    
    sample_questions_medium = [
        {
            'question': 'Daily temperatures this week: -12°C, -8°C, -15°C, -10°C, -6°C. Calculate the mean temperature.',
            'answer': '-10.2°C',
            'steps': [
                'Add all temperatures: (-12) + (-8) + (-15) + (-10) + (-6) = -51',
                'Count the number of days: 5',
                'Divide sum by count: -51 ÷ 5 = -10.2°C'
            ],
            'difficulty': 'Medium'
        },
        {
            'question': 'Concert attendance: 487, 523, 456, 501, 489. What is the mean attendance?',
            'answer': '491.2 people',
            'steps': [
                'Add all values: 487 + 523 + 456 + 501 + 489 = 2456',
                'Count events: 5',
                'Divide: 2456 ÷ 5 = 491.2 people'
            ],
            'difficulty': 'Medium'
        }
    ]
    
    sample_questions_hard = [
        {
            'question': 'Home prices in the area: $450,000, $520,000, $380,000, $495,000, $425,000. Calculate the mean home price.',
            'answer': '$454,000',
            'steps': [
                'Add all prices: $450,000 + $520,000 + $380,000 + $495,000 + $425,000 = $2,270,000',
                'Count properties: 5',
                'Divide: $2,270,000 ÷ 5 = $454,000'
            ],
            'difficulty': 'Hard'
        }
    ]
    
    # 1. Practice Page
    print("Creating practice page...")
    practice_file = generator.create_practice_page(
        skill_name="Calculating Mean (Average)",
        questions=sample_questions_easy + sample_questions_medium[:1],
        answer_key_type='with_steps'
    )
    print(f"✓ Practice page created: {practice_file}")
    
    # 2. Worksheet
    print("\nCreating worksheet...")
    worksheet_file = generator.create_worksheet(
        title="Mean Calculation Worksheet",
        skill_sections=[
            {
                'skill_name': 'Calculating Mean - Easy',
                'questions': sample_questions_easy
            },
            {
                'skill_name': 'Calculating Mean - Medium',
                'questions': sample_questions_medium
            }
        ],
        answer_key_type='answers_only'
    )
    print(f"✓ Worksheet created: {worksheet_file}")
    
    # 3. Quiz
    print("\nCreating quiz...")
    quiz_file = generator.create_quiz(
        title="Mean Calculation Quiz",
        skill_sections=[
            {
                'skill_name': 'Mean Calculation',
                'questions': sample_questions_easy[:1] + sample_questions_medium[:1] + sample_questions_hard
            }
        ],
        answer_key_type='with_steps'
    )
    print(f"✓ Quiz created: {quiz_file}")
    
    # 4. Test
    print("\nCreating test...")
    all_questions = sample_questions_easy + sample_questions_medium + sample_questions_hard
    for q in all_questions:
        q['skill_name'] = 'Mean Calculation'
    
    test_file = generator.create_test(
        title="Grade 12 Essential Mathematics - Unit Test",
        all_skills_questions=all_questions,
        answer_key_type='with_steps'
    )
    print(f"✓ Test created: {test_file}")
    
    return [practice_file, worksheet_file, quiz_file, test_file]


if __name__ == "__main__":
    print("=== Mathematics Assessment PDF Generator ===\n")
    files = create_demo_assessments()
    print("\n=== All assessments created successfully! ===")
    print(f"\nGenerated {len(files)} PDF files")
