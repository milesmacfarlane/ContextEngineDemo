"""
Mean Generator - UPDATED TO USE CONTEXT ENGINE
Handles all mean-related question variations with rich narratives
"""

import random
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from question_models import Question, QuestionType, AnswerFormat
from statistics_calculator import StatisticsCalculator
from context_engine import ContextEngine


class MeanGeneratorV2:
    """
    Mean generator using context engine for narratives.
    
    Now supports:
    - 50 different contexts (server tips, test scores, heart rate, file size, etc.)
    - 3 narrative levels (minimal, standard, rich)
    - Context-appropriate value ranges
    - Automatic unit formatting
    
    Usage:
        gen = MeanGeneratorV2(data_manager, excel_path="data/ContextBanks.xlsx")
        
        # Generate with specific context
        q = gen.generate(
            variation="calculate",
            difficulty=2,
            context_id="server_tips",  # Optional - will pick random if not specified
            level="standard"            # "minimal", "standard", or "rich"
        )
        
        # Let it pick random compatible context
        q = gen.generate(variation="missing_value", difficulty=3)
    """
    
    def __init__(self, data_manager, excel_path: str = "data/ContextBanks.xlsx"):
        self.data = data_manager
        self.calc = StatisticsCalculator()
        self.engine = ContextEngine(data_manager, excel_path)
    
    def generate(self,
                 variation: str = "calculate",
                 difficulty: int = 2,
                 context_id: str = None,
                 level: str = "standard",
                 marks: int = None) -> Question:
        """
        Generate a mean question using context engine.
        
        Args:
            variation: "calculate", "missing_value", "compare", etc.
            difficulty: 1-5
            context_id: Specific context or None for random
            level: "minimal", "standard", or "rich"
            marks: Override default marks (varies by variation)
        
        Returns:
            Question object
        """
        # Pick random compatible context if not specified
        if context_id is None:
            compatible = self.engine.get_compatible_contexts(variation)
            if not compatible:
                raise ValueError(f"No contexts support variation '{variation}'")
            context_id = random.choice(compatible)
        
        # Route to appropriate variation generator
        if variation == "calculate":
            return self._generate_calculate(context_id, difficulty, level, marks or 1)
        elif variation == "missing_value":
            return self._generate_missing_value(context_id, difficulty, level, marks or 2)
        elif variation == "compare":
            return self._generate_compare(context_id, difficulty, level, marks or 2)
        elif variation == "missing_count":
            return self._generate_missing_count(context_id, difficulty, level, marks or 2)
        else:
            raise ValueError(f"Variation '{variation}' not yet implemented")
    
    def _generate_calculate(self, context_id: str, difficulty: int, level: str, marks: int) -> Question:
        """
        VARIATION: Calculate mean
        Given dataset → find mean
        """
        # Determine number of values based on difficulty
        if difficulty == 1:
            n = random.randint(5, 7)
        elif difficulty == 2:
            n = random.randint(7, 10)
        elif difficulty == 3:
            n = random.randint(8, 12)
        else:
            n = random.randint(10, 15)
        
        # Generate narrative using context engine
        narrative = self.engine.generate_narrative(
            context_id=context_id,
            variation="calculate",
            level=level,
            difficulty=difficulty,
            num_values=n
        )
        
        # Extract dataset
        dataset = narrative.metadata['dataset']
        
        # Calculate mean
        mean = self.calc.calculate_mean(dataset)
        
        # Format answer with unit
        formatted_answer = self.engine.format_value(mean, context_id)
        
        # Build solution steps
        solution_steps = [
            f"Dataset: {', '.join([str(round(v, 2)) for v in dataset])}",
            f"Sum: {' + '.join([str(round(v, 2)) for v in dataset])} = {sum(dataset):.2f}",
            f"Count: {len(dataset)}",
            f"Mean: {sum(dataset):.2f} ÷ {len(dataset)} = {mean:.2f}",
            f"Answer: {formatted_answer}"
        ]
        
        return Question(
            id="",
            unit="Statistics",
            outcomes=["12E5.S.1"],
            question_type=QuestionType.CALCULATION,
            difficulty=difficulty,
            total_marks=marks,
            mark_breakdown={"calculation": float(marks)},
            context=narrative.intro,
            question_text=narrative.full_text,
            given_data={
                "dataset": dataset,
                "context_id": context_id,
                "variation": "calculate",
                "level": level
            },
            answer=formatted_answer,
            answer_format=AnswerFormat.NUMERIC_WITH_UNIT,
            solution_steps=solution_steps,
            context_template_id=context_id,
            requires_calculator=True
        )
    
    def _generate_missing_value(self, context_id: str, difficulty: int, level: str, marks: int) -> Question:
        """
        VARIATION: Find missing value
        Given target mean → find value needed to achieve it
        """
        # Number of existing values
        if difficulty <= 2:
            num_existing = random.randint(4, 5)
        elif difficulty == 3:
            num_existing = random.randint(5, 7)
        else:
            num_existing = random.randint(7, 10)
        
        # Get context metadata for value range
        meta = self.engine.get_context_metadata(context_id)
        typical = meta['TypicalMean']
        
        # Generate existing values (slightly below target)
        dataset_partial = self.engine.generate_dataset(context_id, difficulty, num_existing)
        existing_mean = self.calc.calculate_mean(dataset_partial)
        
        # Pick target mean (higher than current)
        if difficulty <= 2:
            target_mean = existing_mean + random.uniform(2, 10)
        else:
            target_mean = existing_mean + random.uniform(5, 20)
        
        # Round target to nice number
        target_mean = self.engine._round_to_nice(target_mean, meta)
        
        # Calculate missing value needed
        existing_sum = sum(dataset_partial)
        total_needed = target_mean * (num_existing + 1)
        missing_value = total_needed - existing_sum
        
        # Generate narrative
        # For missing_value, we need to customize the question stem
        # We'll generate base narrative then modify
        
        # Create custom question text
        intro = f"{self.data.get_name(with_title=True)['full_name']} wants to achieve a mean of {self.engine.format_value(target_mean, context_id)}."
        
        data_display = ", ".join([self.engine.format_value(v, context_id) for v in dataset_partial])
        
        question_text = f"""{intro}

Over {num_existing} periods, the values were:
{data_display}

To achieve a mean of {self.engine.format_value(target_mean, context_id)} over {num_existing + 1} periods, what value is needed next?"""
        
        # Format answer
        formatted_answer = self.engine.format_value(missing_value, context_id)
        
        # Solution steps
        solution_steps = [
            f"Target mean: {target_mean:.2f}",
            f"Total periods: {num_existing + 1}",
            f"Total needed: {target_mean:.2f} × {num_existing + 1} = {total_needed:.2f}",
            f"Already have: {' + '.join([f'{v:.2f}' for v in dataset_partial])} = {existing_sum:.2f}",
            f"Still need: {total_needed:.2f} - {existing_sum:.2f} = {missing_value:.2f}",
            f"Answer: {formatted_answer}"
        ]
        
        return Question(
            id="",
            unit="Statistics",
            outcomes=["12E5.S.1"],
            question_type=QuestionType.CALCULATION,
            difficulty=difficulty,
            total_marks=marks,
            mark_breakdown={"understanding": marks/2, "calculation": marks/2},
            context=intro,
            question_text=question_text,
            given_data={
                "existing_values": dataset_partial,
                "target_mean": target_mean,
                "missing_value": missing_value,
                "context_id": context_id,
                "variation": "missing_value",
                "level": level
            },
            answer=formatted_answer,
            answer_format=AnswerFormat.NUMERIC_WITH_UNIT,
            solution_steps=solution_steps,
            context_template_id=context_id,
            requires_calculator=True
        )
    
    def _generate_compare(self, context_id: str, difficulty: int, level: str, marks: int) -> Question:
        """
        VARIATION: Compare means
        Compare two datasets
        """
        # Generate two datasets
        if difficulty <= 2:
            n = random.randint(5, 7)
        else:
            n = random.randint(8, 12)
        
        dataset1 = self.engine.generate_dataset(context_id, difficulty, n)
        dataset2 = self.engine.generate_dataset(context_id, difficulty, n)
        
        mean1 = self.calc.calculate_mean(dataset1)
        mean2 = self.calc.calculate_mean(dataset2)
        
        # Determine comparison
        if mean1 > mean2:
            comparison = "INCREASE"
            change = mean1 - mean2
        elif mean2 > mean1:
            comparison = "DECREASE"  
            change = mean2 - mean1
        else:
            comparison = "NO CHANGE"
            change = 0
        
        # Format datasets
        data1_str = ", ".join([self.engine.format_value(v, context_id) for v in dataset1])
        data2_str = ", ".join([self.engine.format_value(v, context_id) for v in dataset2])
        
        # Build question
        intro = f"Comparing two sets of {self.engine.get_context_metadata(context_id)['ContextName'].lower()}:"
        
        question_text = f"""{intro}

Period 1:
{data1_str}

Period 2:
{data2_str}

a) Calculate the mean for each period.
b) Did the mean increase, decrease, or stay the same from Period 1 to Period 2?"""
        
        # Solution
        solution_steps = [
            f"Period 1 mean: {sum(dataset1):.2f} ÷ {len(dataset1)} = {mean1:.2f}",
            f"Period 2 mean: {sum(dataset2):.2f} ÷ {len(dataset2)} = {mean2:.2f}",
            f"Comparison: {comparison}",
            f"Change: {change:.2f}" if change > 0 else "No change"
        ]
        
        answer_text = f"Period 1: {self.engine.format_value(mean1, context_id)}, Period 2: {self.engine.format_value(mean2, context_id)}, {comparison}"
        
        return Question(
            id="",
            unit="Statistics",
            outcomes=["12E5.S.1"],
            question_type=QuestionType.MULTI_STEP,
            difficulty=difficulty,
            total_marks=marks,
            mark_breakdown={"calculation": marks/2, "comparison": marks/2},
            context=intro,
            question_text=question_text,
            given_data={
                "dataset1": dataset1,
                "dataset2": dataset2,
                "context_id": context_id,
                "variation": "compare",
                "level": level
            },
            answer=answer_text,
            answer_format=AnswerFormat.TEXT,
            solution_steps=solution_steps,
            context_template_id=context_id,
            requires_calculator=True
        )
    
    def _generate_missing_count(self, context_id: str, difficulty: int, level: str, marks: int) -> Question:
        """
        VARIATION: Find number of values
        Given mean and sum → find how many values
        
        Example: Mean is 25, sum is 375, how many values?
        Answer: 375 ÷ 25 = 15 values
        """
        # This is a less common but interesting variation
        # Generate a scenario where we know the mean and total, need to find count
        
        if difficulty <= 2:
            n_actual = random.randint(5, 10)
        else:
            n_actual = random.randint(10, 20)
        
        # Generate dataset
        dataset = self.engine.generate_dataset(context_id, difficulty, n_actual)
        
        mean_actual = self.calc.calculate_mean(dataset)
        sum_actual = sum(dataset)
        
        # Round mean to nice number
        meta = self.engine.get_context_metadata(context_id)
        mean_actual = self.engine._round_to_nice(mean_actual, meta)
        
        # Recalculate sum based on rounded mean
        sum_actual = mean_actual * n_actual
        
        # Build question
        intro = f"A set of values has a mean of {self.engine.format_value(mean_actual, context_id)}."
        
        question_text = f"""{intro}

The sum of all values is {self.engine.format_value(sum_actual, context_id)}.

How many values are in the dataset?"""
        
        # Solution
        solution_steps = [
            f"Mean = {mean_actual:.2f}",
            f"Sum = {sum_actual:.2f}",
            f"Formula: Count = Sum ÷ Mean",
            f"Count = {sum_actual:.2f} ÷ {mean_actual:.2f}",
            f"Count = {n_actual}",
            f"Answer: {n_actual} values"
        ]
        
        return Question(
            id="",
            unit="Statistics",
            outcomes=["12E5.S.1"],
            question_type=QuestionType.CALCULATION,
            difficulty=difficulty,
            total_marks=marks,
            mark_breakdown={"understanding": marks/2, "calculation": marks/2},
            context=intro,
            question_text=question_text,
            given_data={
                "mean": mean_actual,
                "sum": sum_actual,
                "count": n_actual,
                "context_id": context_id,
                "variation": "missing_count",
                "level": level
            },
            answer=f"{n_actual} values",
            answer_format=AnswerFormat.TEXT,
            solution_steps=solution_steps,
            context_template_id=context_id,
            requires_calculator=True
        )
