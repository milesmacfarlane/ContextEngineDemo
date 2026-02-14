"""
Question Models - Data structures for questions and assessments
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import random
import string


class QuestionType(Enum):
    """Types of questions"""
    CALCULATION = "calculation"
    MULTI_STEP = "multi_step"
    JUSTIFICATION = "justification"
    IDENTIFICATION = "identification"
    MIXED = "mixed"


class AnswerFormat(Enum):
    """Format of expected answer"""
    NUMERIC = "numeric"
    NUMERIC_WITH_UNIT = "numeric_unit"
    TEXT = "text"
    MULTIPLE_VALUES = "multiple_values"


@dataclass
class QuestionPart:
    """Individual part of a multi-part question"""
    letter: str
    instruction: str
    marks: float
    answer: Any
    answer_format: AnswerFormat = AnswerFormat.NUMERIC
    solution_steps: List[str] = field(default_factory=list)


@dataclass
class Question:
    """Universal question model"""
    
    # Identification
    id: str
    unit: str
    outcomes: List[str]
    question_type: QuestionType
    
    # Difficulty & Marking
    difficulty: int  # 1-5
    total_marks: int
    mark_breakdown: Dict[str, float]
    
    # Content
    context: str
    question_text: str
    given_data: Dict[str, Any]
    
    # Parts (for multi-part questions)
    parts: List[QuestionPart] = field(default_factory=list)
    
    # Answer (for single-part questions)
    answer: Any = None
    answer_format: AnswerFormat = AnswerFormat.NUMERIC
    solution_steps: List[str] = field(default_factory=list)
    
    # Multiple Choice (optional)
    is_multiple_choice: bool = False
    options: Optional[List[str]] = None
    correct_option_index: Optional[int] = None
    
    # Metadata
    context_template_id: str = ""
    requires_calculator: bool = False
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique question ID"""
        unit_code = self.unit[:4].upper()
        random_suffix = ''.join(random.choices(string.digits, k=5))
        return f"{unit_code}_{random_suffix}"
    
    def get_marks_display(self) -> str:
        """Get formatted marks display"""
        if self.total_marks == 1:
            return "[1 mark]"
        return f"[{self.total_marks} marks]"
    
    def get_outcomes_display(self) -> str:
        """Get formatted outcomes display"""
        return ", ".join(self.outcomes)


@dataclass
class Assessment:
    """Complete test/assessment"""
    
    # Identification
    title: str
    unit: str
    version_id: str
    
    # Questions
    questions: List[Question]
    
    # Metadata
    date_generated: str
    total_marks: int = 0
    estimated_time_minutes: int = 0
    
    # Options
    include_answer_key: bool = True
    include_work_space: bool = True
    show_outcomes: bool = False
    
    def __post_init__(self):
        """Calculate total marks"""
        self.total_marks = sum(q.total_marks for q in self.questions)
        self.estimated_time_minutes = len(self.questions) * 3  # ~3 min per question
    
    def get_outcome_coverage(self) -> Dict[str, int]:
        """Get count of questions per outcome"""
        outcome_counts = {}
        for q in self.questions:
            for outcome in q.outcomes:
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        return outcome_counts
    
    def get_difficulty_distribution(self) -> Dict[int, int]:
        """Get count of questions per difficulty level"""
        difficulty_counts = {}
        for q in self.questions:
            difficulty_counts[q.difficulty] = difficulty_counts.get(q.difficulty, 0) + 1
        return difficulty_counts
    
    def get_question_type_distribution(self) -> Dict[str, int]:
        """Get count of questions per type"""
        type_counts = {}
        for q in self.questions:
            type_name = q.question_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return type_counts


# Test
if __name__ == "__main__":
    # Create sample question
    q = Question(
        id="STAT_00001",
        unit="Statistics",
        outcomes=["12E5.S.1"],
        question_type=QuestionType.CALCULATION,
        difficulty=2,
        total_marks=2,
        mark_breakdown={"calculations": 1.0, "answer": 1.0},
        context="Student test scores",
        question_text="Calculate the mean, median, and mode.",
        given_data={"dataset": [7, 2, 4, 7, 0, 1, 3, 2, 6, 1]},
        answer={"mean": 3.3, "median": 2.5, "mode": "2, 7"},
        answer_format=AnswerFormat.MULTIPLE_VALUES,
        solution_steps=[
            "Mean: (7+2+4+7+0+1+3+2+6+1)/10 = 3.3",
            "Median: middle values = 2.5",
            "Mode: 2 and 7 (both appear twice)"
        ]
    )
    
    print(f"Question ID: {q.id}")
    print(f"Marks: {q.get_marks_display()}")
    print(f"Outcomes: {q.get_outcomes_display()}")
    
    # Create sample assessment
    assessment = Assessment(
        title="Statistics Unit Test",
        unit="Statistics",
        version_id="20260211-12345",
        questions=[q],
        date_generated="2026-02-11"
    )
    
    print(f"\nAssessment: {assessment.title}")
    print(f"Total marks: {assessment.total_marks}")
    print(f"Outcome coverage: {assessment.get_outcome_coverage()}")
