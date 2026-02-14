"""
Context Engine - Narrative Generation System
Loads context banks and assembles rich narratives for questions
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd


@dataclass
class ContextMetadata:
    """Metadata about a context from ContextBanks.xlsx"""
    context_id: str
    context_name: str
    value_min: float
    value_max: float
    typical_mean: float
    unit: str
    unit_position: str  # "prefix" or "suffix"
    display_as: str     # "currency", "percent", "temperature", etc.
    category: str
    description: str


@dataclass
class ContextCompatibility:
    """Which variations work with this context"""
    context_id: str
    calculate: bool
    missing_value: bool
    missing_count: bool
    compare: bool
    effect_add: bool
    effect_remove: bool
    word_problem: bool
    estimation: bool
    notes: str = ""


@dataclass
class NarrativeTemplate:
    """Template for assembling narrative"""
    context_id: str
    level: str          # "minimal", "standard", "rich"
    template_type: str  # "intro", "motivation", "background", "complete"
    template: str
    uses_name: bool = False
    uses_location: bool = False
    uses_job: bool = False
    uses_course: bool = False
    uses_venue: bool = False
    example: str = ""


@dataclass
class AssembledNarrative:
    """Fully assembled narrative with data"""
    context_id: str
    level: str
    intro: str
    motivation: str = ""
    background: str = ""
    data_presentation: str = ""
    question_stem: str = ""
    full_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BankLoader:
    """
    Loads context banks from Excel with smart caching.
    
    Excel is the source of truth (easy to edit).
    JSON cache is used for fast loading (if Excel unchanged).
    """
    
    def __init__(self, excel_path: str = "data/ContextBanks.xlsx"):
        self.excel_path = excel_path
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_path = self.cache_dir / "context_banks.json"
        self.meta_path = self.cache_dir / "cache_meta.json"
    
    def load(self) -> Dict[str, Any]:
        """
        Load banks - use cache if Excel unchanged.
        
        Returns:
            Dict with all bank data
        """
        if self._is_cache_fresh():
            print("📦 Loading from cache (fast)...")
            return self._load_from_cache()
        else:
            print("📊 Loading from Excel (slower, first time only)...")
            return self._load_from_excel()
    
    def _is_cache_fresh(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_path.exists() or not self.meta_path.exists():
            return False
        
        if not os.path.exists(self.excel_path):
            return False
        
        # Check modification time
        excel_mtime = os.path.getmtime(self.excel_path)
        
        with open(self.meta_path, 'r') as f:
            meta = json.load(f)
        
        return meta.get('excel_mtime') == excel_mtime
    
    def _load_from_cache(self) -> Dict[str, Any]:
        """Load from JSON cache"""
        with open(self.cache_path, 'r') as f:
            return json.load(f)
    
    def _load_from_excel(self) -> Dict[str, Any]:
        """Load from Excel and save to cache"""
        banks = {}
        
        # Load each sheet
        banks['metadata'] = self._load_metadata()
        banks['compatibility'] = self._load_compatibility()
        banks['templates'] = self._load_templates()
        banks['stems'] = self._load_stems()
        banks['presentations'] = self._load_presentations()
        banks['durations'] = self._load_durations()
        banks['comparisons'] = self._load_comparisons()
        
        # Save to cache
        with open(self.cache_path, 'w') as f:
            json.dump(banks, f, indent=2)
        
        # Save metadata
        meta = {
            'excel_mtime': os.path.getmtime(self.excel_path),
            'cached_at': datetime.now().isoformat(),
            'num_contexts': len(banks['metadata'])
        }
        with open(self.meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"✅ Loaded {len(banks['metadata'])} contexts from Excel")
        print(f"💾 Cached for fast loading next time")
        
        return banks
    
    def _load_metadata(self) -> List[Dict]:
        """Load ContextMetadata sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='ContextMetadata')
        return df.to_dict('records')
    
    def _load_compatibility(self) -> List[Dict]:
        """Load ContextCompatibility sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='ContextCompatibility')
        
        # Convert TRUE/FALSE strings to booleans
        bool_cols = ['calculate', 'missing_value', 'missing_count', 'compare',
                     'effect_add', 'effect_remove', 'word_problem', 'estimation']
        
        for col in bool_cols:
            df[col] = df[col].astype(str).str.upper() == 'TRUE'
        
        return df.to_dict('records')
    
    def _load_templates(self) -> List[Dict]:
        """Load ContextTemplates sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='ContextTemplates')
        
        # Convert TRUE/FALSE to booleans
        bool_cols = ['UsesName', 'UsesLocation', 'UsesJob', 'UsesCourse', 'UsesVenue']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper() == 'TRUE'
        
        return df.to_dict('records')
    
    def _load_stems(self) -> List[Dict]:
        """Load SentenceStems sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='SentenceStems')
        return df.to_dict('records')
    
    def _load_presentations(self) -> List[Dict]:
        """Load DataPresentations sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='DataPresentations')
        return df.to_dict('records')
    
    def _load_durations(self) -> List[Dict]:
        """Load Durations sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='Durations')
        return df.to_dict('records')
    
    def _load_comparisons(self) -> List[Dict]:
        """Load ComparisonPhrases sheet"""
        df = pd.read_excel(self.excel_path, sheet_name='ComparisonPhrases')
        return df.to_dict('records')


class ContextEngine:
    """
    Main context engine - assembles narratives from banks.
    
    Usage:
        engine = ContextEngine(data_manager, excel_path="data/ContextBanks.xlsx")
        
        # Generate narrative for a question
        narrative = engine.generate_narrative(
            context_id="server_tips",
            variation="calculate",
            level="standard",
            difficulty=2,
            num_values=7
        )
    """
    
    def __init__(self, data_manager, excel_path: str = "data/ContextBanks.xlsx"):
        self.data = data_manager
        self.loader = BankLoader(excel_path)
        self.banks = self.loader.load()
        
        # Index for fast lookup
        self._index_banks()
    
    def _index_banks(self):
        """Create indexes for fast lookup"""
        # Index metadata by context_id
        self.metadata_index = {
            item['ContextID']: item 
            for item in self.banks['metadata']
        }
        
        # Index compatibility by context_id
        self.compatibility_index = {
            item['ContextID']: item
            for item in self.banks['compatibility']
        }
        
        # Index templates by context_id and level
        self.templates_index = {}
        for item in self.banks['templates']:
            key = (item['ContextID'], item['Level'])
            if key not in self.templates_index:
                self.templates_index[key] = []
            self.templates_index[key].append(item)
        
        # Index stems by context_id, type, and variation
        self.stems_index = {}
        for item in self.banks['stems']:
            key = (item['ContextID'], item['StemType'], item.get('Variation', 'all'))
            if key not in self.stems_index:
                self.stems_index[key] = []
            self.stems_index[key].append(item)
        
        # Index presentations by context_id
        self.presentations_index = {}
        for item in self.banks['presentations']:
            context_id = item['ContextID']
            if context_id not in self.presentations_index:
                self.presentations_index[context_id] = []
            self.presentations_index[context_id].append(item)
        
        # Index durations by context_id
        self.durations_index = {}
        for item in self.banks['durations']:
            context_id = item['ContextID']
            if context_id not in self.durations_index:
                self.durations_index[context_id] = []
            self.durations_index[context_id].append(item)
        
        # Index comparisons by context_id
        self.comparisons_index = {}
        for item in self.banks['comparisons']:
            context_id = item['ContextID']
            if context_id not in self.comparisons_index:
                self.comparisons_index[context_id] = []
            self.comparisons_index[context_id].append(item)
    
    def get_compatible_contexts(self, variation: str) -> List[str]:
        """
        Get list of contexts that support a given variation.
        
        Args:
            variation: "calculate", "missing_value", "compare", etc.
        
        Returns:
            List of context_ids that support this variation
        """
        compatible = []
        for context_id, compat in self.compatibility_index.items():
            if compat.get(variation, False):
                compatible.append(context_id)
        return compatible
    
    def get_context_metadata(self, context_id: str) -> Optional[Dict]:
        """Get metadata for a context"""
        return self.metadata_index.get(context_id)
    
    def check_compatibility(self, context_id: str, variation: str) -> bool:
        """Check if context supports variation"""
        compat = self.compatibility_index.get(context_id)
        if not compat:
            return False
        return compat.get(variation, False)
    
    def generate_dataset(self, context_id: str, difficulty: int, n: int) -> List[float]:
        """
        Generate dataset appropriate for context and difficulty.
        
        Args:
            context_id: Which context
            difficulty: 1-5
            n: Number of values
        
        Returns:
            List of values appropriate for context
        """
        meta = self.metadata_index[context_id]
        
        value_min = meta['ValueMin']
        value_max = meta['ValueMax']
        typical = meta['TypicalMean']
        
        if difficulty == 1:
            # Easy: Stay close to typical, nice round numbers
            spread = (value_max - value_min) * 0.2
            values = [
                typical + random.uniform(-spread, spread)
                for _ in range(n)
            ]
            # Round to nice numbers
            values = [self._round_to_nice(v, meta) for v in values]
        
        elif difficulty == 2:
            # Medium: Wider range
            spread = (value_max - value_min) * 0.4
            values = [
                typical + random.uniform(-spread, spread)
                for _ in range(n)
            ]
            values = [self._round_to_nice(v, meta) for v in values]
        
        elif difficulty == 3:
            # Medium-hard: Even wider, some decimals
            spread = (value_max - value_min) * 0.6
            values = [
                random.uniform(max(value_min, typical - spread), 
                             min(value_max, typical + spread))
                for _ in range(n)
            ]
            # Less aggressive rounding
            if meta['DisplayAs'] in ['currency', 'percent']:
                values = [round(v, 1) for v in values]
            else:
                values = [round(v, 2) for v in values]
        
        else:  # difficulty >= 4
            # Hard: Full range, potential outliers
            # Most values in normal range
            normal_values = [
                random.uniform(value_min + (value_max - value_min) * 0.2,
                             value_max - (value_max - value_min) * 0.2)
                for _ in range(n - 1)
            ]
            # One potential outlier
            outlier = random.choice([
                value_min + random.uniform(0, (value_max - value_min) * 0.1),
                value_max - random.uniform(0, (value_max - value_min) * 0.1)
            ])
            values = normal_values + [outlier]
            random.shuffle(values)
            
            # Minimal rounding
            values = [round(v, 2) for v in values]
        
        return values
    
    def _round_to_nice(self, value: float, meta: Dict) -> float:
        """Round to contextually appropriate precision"""
        if value < 1:
            return round(value, 2)
        elif value < 10:
            return round(value, 1)
        elif value < 100:
            return round(value / 5) * 5  # Round to nearest 5
        elif value < 1000:
            return round(value / 10) * 10  # Round to nearest 10
        else:
            return round(value / 100) * 100  # Round to nearest 100
    
    def format_value(self, value: float, context_id: str) -> str:
        """
        Format a value with appropriate unit.
        
        Args:
            value: Numerical value
            context_id: Which context (for unit info)
        
        Returns:
            Formatted string like "$45.50" or "75%" or "23°C"
        """
        meta = self.metadata_index[context_id]
        unit = meta['Unit']
        unit_pos = meta['UnitPosition']
        display_as = meta['DisplayAs']
        
        # Format based on display type
        if display_as == 'currency':
            formatted = f"${value:.2f}"
        elif display_as == 'thousands':
            formatted = f"${value/1000:.0f}k"
        elif display_as == 'percent':
            formatted = f"{value:.1f}%"
        elif display_as == 'temperature':
            formatted = f"{value:.1f}°C"
        elif display_as in ['count', 'length', 'area', 'volume', 'mass']:
            if unit_pos == 'prefix':
                formatted = f"{unit}{value:.1f}"
            else:
                formatted = f"{value:.1f} {unit}"
        else:
            # Generic
            if unit_pos == 'prefix':
                formatted = f"{unit}{value:.1f}"
            else:
                formatted = f"{value:.1f}{unit}" if unit else f"{value:.1f}"
        
        return formatted
    
    def generate_narrative(self,
                          context_id: str,
                          variation: str,
                          level: str = "standard",
                          difficulty: int = 2,
                          num_values: int = 7,
                          **kwargs) -> AssembledNarrative:
        """
        Generate complete narrative for a question.
        
        Args:
            context_id: Which context to use
            variation: Which math variation (calculate, missing_value, etc.)
            level: Narrative depth ("minimal", "standard", "rich")
            difficulty: 1-5
            num_values: How many data points
            **kwargs: Additional parameters (target_mean, etc.)
        
        Returns:
            AssembledNarrative with all components
        """
        # Check compatibility
        if not self.check_compatibility(context_id, variation):
            raise ValueError(f"Context '{context_id}' doesn't support variation '{variation}'")
        
        # Get templates for this level
        templates = self.templates_index.get((context_id, level), [])
        if not templates:
            raise ValueError(f"No templates found for {context_id} at level {level}")
        
        # Assemble narrative based on level
        if level == "minimal":
            return self._assemble_minimal(context_id, variation, templates, difficulty, num_values, **kwargs)
        elif level == "standard":
            return self._assemble_standard(context_id, variation, templates, difficulty, num_values, **kwargs)
        else:  # rich
            return self._assemble_rich(context_id, variation, templates, difficulty, num_values, **kwargs)
    
    def _assemble_minimal(self, context_id, variation, templates, difficulty, num_values, **kwargs):
        """Assemble minimal level narrative (one sentence)"""
        # Find "complete" template
        complete_templates = [t for t in templates if t['TemplateType'] == 'complete']
        if not complete_templates:
            raise ValueError(f"No complete template for {context_id} minimal level")
        
        template = random.choice(complete_templates)
        
        # Get data
        dataset = self.generate_dataset(context_id, difficulty, num_values)
        formatted_data = ", ".join([self.format_value(v, context_id) for v in dataset])
        
        # Get question stem
        question = self._get_question_stem(context_id, variation)
        
        # Get duration
        duration = self._get_duration_label(context_id, num_values)
        
        # Fill placeholders
        text = template['Template']
        text = self._fill_placeholders(text, context_id, template, {
            'data': formatted_data,
            'question': question,
            'duration': duration,
            'n': num_values
        })
        
        return AssembledNarrative(
            context_id=context_id,
            level="minimal",
            intro=text,
            full_text=text,
            metadata={
                'dataset': dataset,
                'formatted_data': formatted_data,
                'difficulty': difficulty,
                'variation': variation
            }
        )
    
    def _assemble_standard(self, context_id, variation, templates, difficulty, num_values, **kwargs):
        """Assemble standard level narrative"""
        # Get intro template
        intro_templates = [t for t in templates if t['TemplateType'] == 'intro']
        if not intro_templates:
            raise ValueError(f"No intro template for {context_id}")
        intro_template = random.choice(intro_templates)
        
        # Get motivation (if available)
        motivation = ""
        motivation_templates = [t for t in templates if t['TemplateType'] == 'motivation']
        if motivation_templates:
            motivation_template = random.choice(motivation_templates)
            motivation = motivation_template['Template']
        
        # Generate data
        dataset = self.generate_dataset(context_id, difficulty, num_values)
        
        # Get data intro stem
        data_intro = self._get_data_intro_stem(context_id, variation)
        
        # Get duration
        duration = self._get_duration_label(context_id, num_values)
        
        # Format data
        formatted_data = ", ".join([self.format_value(v, context_id) for v in dataset])
        
        # Get question stem
        question = self._get_question_stem(context_id, variation)
        
        # Fill placeholders
        intro = self._fill_placeholders(intro_template['Template'], context_id, intro_template, {
            'duration': duration,
            'n': num_values
        })
        
        if motivation:
            motivation = self._fill_placeholders(motivation, context_id, intro_template, {})
        
        # Assemble full text
        parts = [intro]
        if motivation:
            parts.append(motivation)
        parts.append(f"{data_intro} {formatted_data}")
        parts.append(question)
        
        full_text = "\n\n".join(parts)
        
        return AssembledNarrative(
            context_id=context_id,
            level="standard",
            intro=intro,
            motivation=motivation,
            data_presentation=f"{data_intro} {formatted_data}",
            question_stem=question,
            full_text=full_text,
            metadata={
                'dataset': dataset,
                'difficulty': difficulty,
                'variation': variation
            }
        )
    
    def _assemble_rich(self, context_id, variation, templates, difficulty, num_values, **kwargs):
        """Assemble rich level narrative (full scenario)"""
        # Get intro
        intro_templates = [t for t in templates if t['TemplateType'] == 'intro']
        intro_template = random.choice(intro_templates) if intro_templates else None
        
        # Get background
        background_templates = [t for t in templates if t['TemplateType'] == 'background']
        background_template = random.choice(background_templates) if background_templates else None
        
        # Get motivation
        motivation_templates = [t for t in templates if t['TemplateType'] == 'motivation']
        motivation_template = random.choice(motivation_templates) if motivation_templates else None
        
        # Generate data
        dataset = self.generate_dataset(context_id, difficulty, num_values)
        
        # Get duration
        duration = self._get_duration_label(context_id, num_values)
        
        # Format data (use list format for rich)
        data_presentation = self._format_data_rich(context_id, dataset, duration)
        
        # Get question
        question = self._get_question_stem(context_id, variation)
        
        # Fill all templates
        intro = ""
        if intro_template:
            intro = self._fill_placeholders(intro_template['Template'], context_id, intro_template, {
                'duration': duration,
                'n': num_values
            })
        
        background = ""
        if background_template:
            # For missing_value, might need previous_amount
            previous_amount = kwargs.get('previous_amount', '')
            background = self._fill_placeholders(background_template['Template'], context_id, background_template, {
                'previous_amount': previous_amount
            })
        
        motivation = ""
        if motivation_template:
            motivation = self._fill_placeholders(motivation_template['Template'], context_id, motivation_template, {})
        
        # Assemble
        parts = []
        if intro:
            parts.append(intro)
        if background:
            parts.append(background)
        if motivation:
            parts.append(motivation)
        parts.append(data_presentation)
        parts.append(question)
        
        full_text = "\n\n".join(parts)
        
        return AssembledNarrative(
            context_id=context_id,
            level="rich",
            intro=intro,
            background=background,
            motivation=motivation,
            data_presentation=data_presentation,
            question_stem=question,
            full_text=full_text,
            metadata={
                'dataset': dataset,
                'difficulty': difficulty,
                'variation': variation
            }
        )
    
    def _fill_placeholders(self, template: str, context_id: str, template_obj: Dict, extra: Dict = None) -> str:
        """Fill placeholders in template"""
        if extra is None:
            extra = {}
        
        text = template
        
        # Standard placeholders from data manager
        if template_obj.get('UsesName'):
            name_data = self.data.get_name(with_title=True)
            text = text.replace('{name}', name_data['full_name'])
            
            # Pronouns
            # Simple heuristic based on title
            if name_data.get('title') in ['Mr.', 'Dr.']:
                text = text.replace('{pronoun}', 'he')
                text = text.replace('{pronoun_possessive}', 'his')
            else:
                text = text.replace('{pronoun}', 'she')
                text = text.replace('{pronoun_possessive}', 'her')
        
        if template_obj.get('UsesLocation'):
            place = self.data.get_place_cdn()
            text = text.replace('{city}', place['city'])
        
        if template_obj.get('UsesVenue'):
            venue = self.data.get_theater()
            text = text.replace('{venue}', venue)
        
        if template_obj.get('UsesJob'):
            job = self.data.get_summer_job()
            text = text.replace('{job}', job)
        
        if template_obj.get('UsesCourse'):
            course = self.data.get_course()
            text = text.replace('{course}', course)
        
        # Extra placeholders passed in
        for key, value in extra.items():
            text = text.replace(f'{{{key}}}', str(value))
        
        return text
    
    def _get_question_stem(self, context_id: str, variation: str) -> str:
        """Get appropriate question stem"""
        # Try context-specific first
        stems = self.stems_index.get((context_id, 'question_stem', variation), [])
        if not stems:
            # Try context-specific but variation 'all'
            stems = self.stems_index.get((context_id, 'question_stem', 'all'), [])
        
        if not stems:
            # Fallback generic
            generic_stems = {
                'calculate': "Calculate the mean.",
                'missing_value': "Find the missing value needed.",
                'compare': "Compare the means.",
            }
            return generic_stems.get(variation, "Answer the question.")
        
        stem = random.choice(stems)
        return stem['Stem']
    
    def _get_data_intro_stem(self, context_id: str, variation: str) -> str:
        """Get data introduction stem"""
        stems = self.stems_index.get((context_id, 'data_intro', 'all'), [])
        if not stems:
            stems = self.stems_index.get((context_id, 'data_intro', variation), [])
        
        if not stems:
            return "The values recorded were:"
        
        stem = random.choice(stems)
        return stem['Stem']
    
    def _get_duration_label(self, context_id: str, n: int) -> str:
        """Get appropriate duration label"""
        durations = self.durations_index.get(context_id, [])
        if not durations:
            return f"{n} values"
        
        duration = random.choice(durations)
        
        if n == 1:
            return f"1 {duration['SingularLabel']}"
        else:
            return f"{n} {duration['PluralLabel']}"
    
    def _format_data_rich(self, context_id: str, dataset: List[float], duration: str) -> str:
        """Format data for rich narrative (list or table format)"""
        presentations = self.presentations_index.get(context_id, [])
        
        # Prefer list or table format for rich
        list_formats = [p for p in presentations if p['Format'] in ['list', 'table']]
        if not list_formats:
            list_formats = presentations
        
        if not list_formats:
            # Fallback
            formatted = ", ".join([self.format_value(v, context_id) for v in dataset])
            return f"Values: {formatted}"
        
        format_spec = random.choice(list_formats)
        
        if format_spec['Format'] == 'list':
            # One per line
            lines = []
            for i, value in enumerate(dataset, 1):
                formatted_value = self.format_value(value, context_id)
                lines.append(f"Day {i}: {formatted_value}")
            return "\n".join(lines)
        
        else:
            # Inline fallback
            formatted = ", ".join([self.format_value(v, context_id) for v in dataset])
            return f"{duration}: {formatted}"
