# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
PHASE 6 - SYN-4: FORMAL LANGUAGE TRANSLATOR (Tier 3)
=====================================================

Translates between natural language and formal notation.

CAPABILITIES:
------------
- Natural language to formal notation
- Formal notation to natural language
- Multi-format support (LaTeX, ASCII, Unicode)
- Ambiguity detection
- Context-aware translation

REFERENCE:
---------
- Agent_System_Audit.docx.md: SYN-4 Formal Language Translator
- Phase_6_Formal_Verification.md: Synthesis Team
"""

import sys
import os
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.formal_translator')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class NotationFormat(Enum):
    """Supported notation formats"""
    NATURAL = "natural"    # English prose
    LATEX = "latex"        # LaTeX math mode
    ASCII = "ascii"        # Plain ASCII symbols
    UNICODE = "unicode"    # Unicode math symbols
    SYMBOLIC = "symbolic"  # Internal symbolic rep


class TranslationQuality(Enum):
    """Quality of translation"""
    EXACT = "exact"        # Perfect translation
    APPROXIMATE = "approximate"  # Some information loss
    AMBIGUOUS = "ambiguous"      # Multiple interpretations
    FAILED = "failed"


@dataclass
class TranslationResult:
    """Result of a translation"""
    source_format: NotationFormat
    target_format: NotationFormat
    source_text: str
    translated_text: str
    quality: TranslationQuality
    alternatives: List[str] = field(default_factory=list)
    ambiguities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_format': self.source_format.value,
            'target_format': self.target_format.value,
            'translated': self.translated_text,
            'quality': self.quality.value,
            'has_alternatives': len(self.alternatives) > 0,
            'ambiguity_count': len(self.ambiguities)
        }


class FormalLanguageTranslator(BDIAgent):
    """
    SYN-4: Formal Language Translator
    
    DIRECTIVE:
    ---------
    Translate between natural language and formal mathematical notation.
    
    INPUTS:
    ------
    - Natural language statements
    - Formal notation
    - Target format specifications
    
    OUTPUTS:
    -------
    - Translated text
    - Ambiguity reports
    - Alternative interpretations
    
    DEPENDENCIES:
    ------------
    - KM-1 (ContextExtractorAgent): For context awareness
    - SYN-3 (ConjectureGenerator): For statement parsing
    
    FAILURE MODE: DEGRADED - Returns partial translation with warnings
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 714-723
    """
    
    # Natural language patterns -> formal equivalents
    NL_TO_FORMAL = {
        r'for all (\w+)': (r'∀\1', r'\\forall \1'),
        r'there exists? (\w+)': (r'∃\1', r'\\exists \1'),
        r'such that': (r':', r':'),
        r'implies': (r'→', r'\\implies'),
        r'if and only if': (r'↔', r'\\iff'),
        r'and': (r'∧', r'\\land'),
        r'or': (r'∨', r'\\lor'),
        r'not': (r'¬', r'\\neg'),
        r'in': (r'∈', r'\\in'),
        r'subset of': (r'⊆', r'\\subseteq'),
        r'union': (r'∪', r'\\cup'),
        r'intersection': (r'∩', r'\\cap'),
        r'empty set': (r'∅', r'\\emptyset'),
        r'infinity': (r'∞', r'\\infty'),
        r'less than or equal': (r'≤', r'\\leq'),
        r'greater than or equal': (r'≥', r'\\geq'),
        r'not equal': (r'≠', r'\\neq'),
        r'plus or minus': (r'±', r'\\pm'),
        r'sum of': (r'Σ', r'\\sum'),
        r'product of': (r'Π', r'\\prod'),
        r'integral of': (r'∫', r'\\int'),
    }
    
    # Unicode to LaTeX
    UNICODE_TO_LATEX = {
        '∀': r'\forall',
        '∃': r'\exists',
        '→': r'\rightarrow',
        '↔': r'\leftrightarrow',
        '∧': r'\land',
        '∨': r'\lor',
        '¬': r'\neg',
        '∈': r'\in',
        '⊆': r'\subseteq',
        '∪': r'\cup',
        '∩': r'\cap',
        '∅': r'\emptyset',
        '∞': r'\infty',
        '≤': r'\leq',
        '≥': r'\geq',
        '≠': r'\neq',
        '±': r'\pm',
        'Σ': r'\sum',
        'Π': r'\prod',
        '∫': r'\int',
        'α': r'\alpha',
        'β': r'\beta',
        'γ': r'\gamma',
        'δ': r'\delta',
        'π': r'\pi',
        'θ': r'\theta',
        'λ': r'\lambda',
    }
    
    # LaTeX to Unicode
    LATEX_TO_UNICODE = {v: k for k, v in UNICODE_TO_LATEX.items()}
    
    def __init__(
        self,
        agent_id: str = 'formal_translator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Formal Language Translator
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Translation cache
        self.cache: Dict[str, TranslationResult] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.translations_performed = 0
        self.ambiguities_detected = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Formal Language Translator initialized")
        print(f"  Patterns: {len(self.NL_TO_FORMAL)}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='synthesis.translator',
            agent_id=self.agent_id,
            algorithm='formal_translation',
            cost='medium',
            type='translation',
            tier='3',
            algorithms='nl_formal_multi_format'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: synthesis.translator")
    
    def translate(
        self,
        text: str,
        source_format: NotationFormat,
        target_format: NotationFormat
    ) -> TranslationResult:
        """
        Translate text between formats.
        
        Args:
            text: Source text
            source_format: Format of source
            target_format: Desired target format
            
        Returns:
            TranslationResult
        """
        self.tasks_executed += 1
        self.translations_performed += 1
        
        try:
            if source_format == target_format:
                return TranslationResult(
                    source_format=source_format,
                    target_format=target_format,
                    source_text=text,
                    translated_text=text,
                    quality=TranslationQuality.EXACT
                )
            
            # Route to appropriate translator
            if source_format == NotationFormat.NATURAL:
                result = self._translate_from_natural(text, target_format)
            elif source_format == NotationFormat.LATEX:
                result = self._translate_from_latex(text, target_format)
            elif source_format == NotationFormat.UNICODE:
                result = self._translate_from_unicode(text, target_format)
            else:
                result = TranslationResult(
                    source_format=source_format,
                    target_format=target_format,
                    source_text=text,
                    translated_text=text,
                    quality=TranslationQuality.APPROXIMATE
                )
            
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Translation failed: {type(e).__name__}: {e}")
            
            return TranslationResult(
                source_format=source_format,
                target_format=target_format,
                source_text=text,
                translated_text=f"TRANSLATION_ERROR: {str(e)}",
                quality=TranslationQuality.FAILED
            )
    
    def _translate_from_natural(
        self,
        text: str,
        target: NotationFormat
    ) -> TranslationResult:
        """Translate from natural language"""
        translated = text.lower()
        ambiguities = []
        
        for pattern, replacements in self.NL_TO_FORMAL.items():
            if re.search(pattern, translated, re.IGNORECASE):
                if target == NotationFormat.UNICODE:
                    translated = re.sub(pattern, replacements[0], translated, flags=re.IGNORECASE)
                elif target == NotationFormat.LATEX:
                    translated = re.sub(pattern, replacements[1], translated, flags=re.IGNORECASE)
        
        # Detect ambiguities
        ambiguous_patterns = ['or', 'and', 'is']
        for p in ambiguous_patterns:
            if translated.count(p) > 1:
                ambiguities.append(f"Multiple '{p}' may have ambiguous interpretation")
                self.ambiguities_detected += 1
        
        quality = (TranslationQuality.AMBIGUOUS if ambiguities
                  else TranslationQuality.APPROXIMATE)
        
        return TranslationResult(
            source_format=NotationFormat.NATURAL,
            target_format=target,
            source_text=text,
            translated_text=translated,
            quality=quality,
            ambiguities=ambiguities
        )
    
    def _translate_from_latex(
        self,
        text: str,
        target: NotationFormat
    ) -> TranslationResult:
        """Translate from LaTeX"""
        translated = text
        
        if target == NotationFormat.UNICODE:
            for latex, uni in self.LATEX_TO_UNICODE.items():
                translated = translated.replace(latex, uni)
        elif target == NotationFormat.NATURAL:
            translated = self._latex_to_natural(text)
        
        return TranslationResult(
            source_format=NotationFormat.LATEX,
            target_format=target,
            source_text=text,
            translated_text=translated,
            quality=TranslationQuality.EXACT
        )
    
    def _translate_from_unicode(
        self,
        text: str,
        target: NotationFormat
    ) -> TranslationResult:
        """Translate from Unicode symbols"""
        translated = text
        
        if target == NotationFormat.LATEX:
            for uni, latex in self.UNICODE_TO_LATEX.items():
                translated = translated.replace(uni, latex + ' ')
        elif target == NotationFormat.NATURAL:
            translated = self._unicode_to_natural(text)
        
        return TranslationResult(
            source_format=NotationFormat.UNICODE,
            target_format=target,
            source_text=text,
            translated_text=translated,
            quality=TranslationQuality.EXACT
        )
    
    def _latex_to_natural(self, text: str) -> str:
        """Convert LaTeX to natural language"""
        result = text
        replacements = [
            (r'\\forall\s*(\w+)', r'for all \1'),
            (r'\\exists\s*(\w+)', r'there exists \1'),
            (r'\\implies', r'implies'),
            (r'\\iff', r'if and only if'),
            (r'\\land', r'and'),
            (r'\\lor', r'or'),
            (r'\\neg', r'not'),
            (r'\\in', r'in'),
            (r'\\subseteq', r'is a subset of'),
            (r'\\leq', r'less than or equal to'),
            (r'\\geq', r'greater than or equal to'),
            (r'\\neq', r'is not equal to'),
        ]
        
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def _unicode_to_natural(self, text: str) -> str:
        """Convert Unicode symbols to natural language"""
        replacements = {
            '∀': 'for all',
            '∃': 'there exists',
            '→': 'implies',
            '↔': 'if and only if',
            '∧': 'and',
            '∨': 'or',
            '¬': 'not',
            '∈': 'in',
            '⊆': 'is a subset of',
            '≤': 'is less than or equal to',
            '≥': 'is greater than or equal to',
            '≠': 'is not equal to',
        }
        
        result = text
        for symbol, word in replacements.items():
            result = result.replace(symbol, f' {word} ')
        
        return ' '.join(result.split())
    
    def detect_format(self, text: str) -> NotationFormat:
        """Detect the format of input text"""
        # Check for LaTeX commands
        if re.search(r'\\[a-zA-Z]+', text):
            return NotationFormat.LATEX
        
        # Check for Unicode math symbols
        unicode_symbols = set('∀∃→↔∧∨¬∈⊆∪∩∅∞≤≥≠±ΣΠ∫αβγδπθλ')
        if any(c in unicode_symbols for c in text):
            return NotationFormat.UNICODE
        
        # Check for natural language indicators
        nl_words = {'for all', 'there exists', 'implies', 'and', 'or', 'not'}
        if any(w in text.lower() for w in nl_words):
            return NotationFormat.NATURAL
        
        return NotationFormat.ASCII
    
    def process(self, task_entry: Any) -> Any:
        """Process translation task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing translation task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'translate')
            
            if operation == 'translate':
                text = metadata.get('text', '')
                source = NotationFormat(metadata.get('source', 'natural'))
                target = NotationFormat(metadata.get('target', 'unicode'))
                result = self.translate(text, source, target)
                return self._create_result_entry(task_entry, result.to_dict())
                
            elif operation == 'detect':
                text = metadata.get('text', '')
                detected = self.detect_format(text)
                result = {'detected_format': detected.value}
                
            elif operation == 'to_latex':
                text = metadata.get('text', '')
                source = self.detect_format(text)
                result = self.translate(text, source, NotationFormat.LATEX)
                return self._create_result_entry(task_entry, result.to_dict())
                
            elif operation == 'to_natural':
                text = metadata.get('text', '')
                source = self.detect_format(text)
                result = self.translate(text, source, NotationFormat.NATURAL)
                return self._create_result_entry(task_entry, result.to_dict())
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Translation task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['translator', 'synthesis'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'translator'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for translation tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['translator'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['translate'], status=EntryStatus.PENDING)
            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata and task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                    tasks.append(task)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create translation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'translate')
            steps = ['claim_task', 'detect_format', 'translate', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'translate_{operation}_{task_id}',
                steps=steps,
                target_desire='formal_translation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform formal translation."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()
            elif action == 'detect_format':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                text = metadata.get('text', '')
                source_format = self.detect_format(text)
                target_format = NotationFormat(metadata.get('target', 'unicode'))
                intention.metadata['text'] = text
                intention.metadata['source_format'] = source_format
                intention.metadata['target_format'] = target_format
                intention.advance()
            elif action == 'translate':
                text = intention.metadata.get('text', '')
                source = intention.metadata.get('source_format', NotationFormat.NATURAL)
                target = intention.metadata.get('target_format', NotationFormat.UNICODE)
                result = self.translate(text, source, target)
                intention.metadata['translation_result'] = result
                intention.advance()
            elif action == 'verify_result':
                result = intention.metadata.get('translation_result')
                verified = result is not None and result.quality != TranslationQuality.FAILED
                intention.metadata['verified'] = verified
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('translation_result')
                if self.blackboard and result:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(result.translated_text),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['translator', 'synthesis', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata=result.to_dict()
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translator statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'translations_performed': self.translations_performed,
            'ambiguities_detected': self.ambiguities_detected,
            'cache_size': len(self.cache)
        })
        return stats


if __name__ == "__main__":
    """Test Formal Language Translator"""
    print("=" * 80)
    print("PHASE 6 - FORMAL LANGUAGE TRANSLATOR TEST")
    print("=" * 80)
    print()
    
    # Initialize translator
    translator = FormalLanguageTranslator()
    print()
    
    # Test 1: Natural to Unicode
    print("Test 1: Natural Language → Unicode")
    text = "for all x there exists y such that x implies y"
    result = translator.translate(text, NotationFormat.NATURAL, NotationFormat.UNICODE)
    print(f"  Input:  {text}")
    print(f"  Output: {result.translated_text}")
    print(f"  Quality: {result.quality.value}")
    print()
    
    # Test 2: Natural to LaTeX
    print("Test 2: Natural Language → LaTeX")
    text = "for all n in naturals n less than or equal n plus 1"
    result = translator.translate(text, NotationFormat.NATURAL, NotationFormat.LATEX)
    print(f"  Input:  {text}")
    print(f"  Output: {result.translated_text}")
    print()
    
    # Test 3: LaTeX to Unicode
    print("Test 3: LaTeX → Unicode")
    text = r"\forall x \in A : x \geq 0"
    result = translator.translate(text, NotationFormat.LATEX, NotationFormat.UNICODE)
    print(f"  Input:  {text}")
    print(f"  Output: {result.translated_text}")
    print()
    
    # Test 4: Unicode to Natural
    print("Test 4: Unicode → Natural Language")
    text = "∀x ∈ ℕ: x ≥ 0 ∧ x → x"
    result = translator.translate(text, NotationFormat.UNICODE, NotationFormat.NATURAL)
    print(f"  Input:  {text}")
    print(f"  Output: {result.translated_text}")
    print()
    
    # Test 5: Format detection
    print("Test 5: Format Detection")
    samples = [
        r"\forall x \in A",
        "∀x ∈ A",
        "for all x in A",
        "x + y = z"
    ]
    for s in samples:
        fmt = translator.detect_format(s)
        print(f"  '{s[:30]}...' → {fmt.value}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(translator.get_statistics(), indent=2))
