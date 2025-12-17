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
Math Notation Translator Agent
==============================

Translates between different mathematical notation formats:
- LaTeX
- SymPy (Python symbolic math)
- Natural language (English)
- Unicode math symbols
- ASCII math
- MathML
- Wolfram (Mathematica)

This agent allows users to input math in any format and convert it to any other.
"""

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict, List, Tuple

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    parse_expr as native_parse_expr, Symbol, Expr, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt, symbols
)
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger('symbo_agentic_reasoners.agents.notation_translator')


class NotationFormat(Enum):
    """Supported mathematical notation formats."""
    SYMPY = 'sympy'           # Python SymPy syntax
    LATEX = 'latex'           # LaTeX markup
    NATURAL = 'natural'       # Natural language (English)
    UNICODE = 'unicode'       # Unicode math symbols
    ASCII = 'ascii'           # Plain ASCII
    MATHML = 'mathml'         # MathML XML
    WOLFRAM = 'wolfram'       # Mathematica syntax
    INFIX = 'infix'           # Standard infix notation


@dataclass
class TranslationResult:
    """Result of a notation translation."""
    success: bool
    source_format: NotationFormat
    target_format: NotationFormat
    source_text: str
    translated_text: str
    sympy_expr: Optional[Any] = None
    error_message: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)


class NotationTranslatorAgent(BDIAgent):
    """
    Agent that translates between mathematical notation formats.

    Supports bidirectional translation between:
    - LaTeX <-> SymPy
    - Natural language -> SymPy
    - SymPy -> Unicode pretty print
    - SymPy -> MathML
    - SymPy -> ASCII
    - Wolfram -> SymPy (partial)

    Usage:
        translator = NotationTranslatorAgent("translator_001")
        result = translator.translate("\\frac{x^2}{2}", NotationFormat.LATEX, NotationFormat.SYMPY)
        # result.translated_text == "x**2/2"
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self._setup_conversion_tables()
        print(f"[{agent_id}] Notation Translator initialized")
        print(f"  Supported formats: {[f.value for f in NotationFormat]}")

    def _setup_conversion_tables(self):
        """Initialize conversion lookup tables."""

        # LaTeX to SymPy patterns
        self.latex_to_sympy_patterns = [
            # Fractions
            (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'((\1)/(\2))'),
            # Powers
            (r'\^{([^}]+)}', r'**(\1)'),
            (r'\^(\d)', r'**\1'),
            # Square root
            (r'\\sqrt\{([^}]+)\}', r'sqrt(\1)'),
            (r'\\sqrt\[(\d+)\]\{([^}]+)\}', r'(\2)**(1/\1)'),
            # Trigonometric
            (r'\\sin', 'sin'),
            (r'\\cos', 'cos'),
            (r'\\tan', 'tan'),
            (r'\\cot', 'cot'),
            (r'\\sec', 'sec'),
            (r'\\csc', 'csc'),
            (r'\\arcsin', 'asin'),
            (r'\\arccos', 'acos'),
            (r'\\arctan', 'atan'),
            # Logarithms
            (r'\\ln', 'log'),
            (r'\\log', 'log'),
            (r'\\log_(\d+)', r'log(\1,'),
            # Exponential
            (r'\\exp', 'exp'),
            (r'e\^', 'exp'),
            # Greek letters
            (r'\\alpha', 'alpha'),
            (r'\\beta', 'beta'),
            (r'\\gamma', 'gamma'),
            (r'\\delta', 'delta'),
            (r'\\epsilon', 'epsilon'),
            (r'\\theta', 'theta'),
            (r'\\lambda', 'lamda'),  # SymPy uses 'lamda' to avoid keyword
            (r'\\mu', 'mu'),
            (r'\\pi', 'pi'),
            (r'\\sigma', 'sigma'),
            (r'\\omega', 'omega'),
            (r'\\phi', 'phi'),
            (r'\\psi', 'psi'),
            # Infinity
            (r'\\infty', 'oo'),
            # Multiplication
            (r'\\cdot', '*'),
            (r'\\times', '*'),
            # Division
            (r'\\div', '/'),
            # Plus/minus
            (r'\\pm', '+-'),
            # Integrals
            (r'\\int_\{([^}]+)\}\^\{([^}]+)\}\s*([^d]+)\s*d([a-zA-Z])', r'integrate(\3, (\4, \1, \2))'),
            (r'\\int\s*([^d]+)\s*d([a-zA-Z])', r'integrate(\1, \2)'),
            # Derivatives
            (r'\\frac\{d\}\{d([a-zA-Z])\}\s*(.+)', r'diff(\2, \1)'),
            (r'\\frac\{d\^(\d+)\}\{d([a-zA-Z])\^(\d+)\}\s*(.+)', r'diff(\4, \2, \1)'),
            # Limits
            (r'\\lim_\{([a-zA-Z])\\to([^}]+)\}\s*(.+)', r'limit(\3, \1, \2)'),
            # Summation
            (r'\\sum_\{([a-zA-Z])=([^}]+)\}\^\{([^}]+)\}\s*(.+)', r'Sum(\4, (\1, \2, \3))'),
            # Product
            (r'\\prod_\{([a-zA-Z])=([^}]+)\}\^\{([^}]+)\}\s*(.+)', r'Product(\4, (\1, \2, \3))'),
            # Cleanup
            (r'\\left', ''),
            (r'\\right', ''),
            (r'\{', '('),
            (r'\}', ')'),
            (r'\\,', ' '),
            (r'\\;', ' '),
            (r'\\!', ''),
        ]

        # Natural language patterns to SymPy
        self.natural_to_sympy_patterns = [
            # Basic operations
            (r'\bthe\s+square\s+root\s+of\s+(\S+)', r'sqrt(\1)'),
            (r'\bsquare\s+root\s+of\s+(\S+)', r'sqrt(\1)'),
            (r'(\S+)\s+squared', r'(\1)**2'),
            (r'(\S+)\s+cubed', r'(\1)**3'),
            (r'(\S+)\s+to\s+the\s+power\s+of\s+(\d+)', r'(\1)**\2'),
            (r'(\S+)\s+raised\s+to\s+(\d+)', r'(\1)**\2'),
            # Calculus
            (r'\bderivative\s+of\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'diff(\1, \2)'),
            (r'\bdifferentiate\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'diff(\1, \2)'),
            (r'\bintegral\s+of\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'integrate(\1, \2)'),
            (r'\bintegrate\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'integrate(\1, \2)'),
            (r'\bintegral\s+of\s+(.+?)\s+d(\w+)', r'integrate(\1, \2)'),
            (r'\blimit\s+of\s+(.+?)\s+as\s+(\w+)\s+approaches\s+(\S+)', r'limit(\1, \2, \3)'),
            (r'\blimit\s+as\s+(\w+)\s+goes\s+to\s+(\S+)\s+of\s+(.+)', r'limit(\3, \1, \2)'),
            # Algebra
            (r'\bsolve\s+(.+?)\s+for\s+(\w+)', r'solve(\1, \2)'),
            (r'\bfactor\s+(.+)', r'factor(\1)'),
            (r'\bexpand\s+(.+)', r'expand(\1)'),
            (r'\bsimplify\s+(.+)', r'simplify(\1)'),
            # Words to operators
            (r'\bplus\b', '+'),
            (r'\bminus\b', '-'),
            (r'\btimes\b', '*'),
            (r'\bdivided\s+by\b', '/'),
            (r'\bover\b', '/'),
            (r'\bequals?\b', '='),
            # Constants
            (r'\bpi\b', 'pi'),
            (r'\be\b(?!\w)', 'E'),
            (r'\binfinity\b', 'oo'),
        ]

        # Unicode to ASCII
        self.unicode_to_ascii = {
            '²': '**2', '³': '**3', '⁴': '**4', '⁵': '**5',
            '⁶': '**6', '⁷': '**7', '⁸': '**8', '⁹': '**9',
            '×': '*', '÷': '/', '−': '-', '±': '+-',
            '√': 'sqrt', '∞': 'oo',
            'π': 'pi', 'θ': 'theta', 'α': 'alpha', 'β': 'beta',
            'γ': 'gamma', 'δ': 'delta', 'λ': 'lamda', 'μ': 'mu',
            'σ': 'sigma', 'φ': 'phi', 'ω': 'omega',
            '∫': 'integrate', '∑': 'Sum', '∏': 'Product',
            '∂': 'diff',
            '≤': '<=', '≥': '>=', '≠': '!=', '≈': '~=',
            '→': '->', '←': '<-',
        }

        # Wolfram to SymPy
        self.wolfram_to_sympy = {
            'Sin': 'sin', 'Cos': 'cos', 'Tan': 'tan',
            'ArcSin': 'asin', 'ArcCos': 'acos', 'ArcTan': 'atan',
            'Log': 'log', 'Exp': 'exp', 'Sqrt': 'sqrt',
            'Pi': 'pi', 'E': 'E', 'I': 'I',
            'Infinity': 'oo', 'True': 'True', 'False': 'False',
            'D[': 'diff(', 'Integrate[': 'integrate(',
            'Solve[': 'solve(', 'Factor[': 'factor(',
            'Expand[': 'expand(', 'Simplify[': 'simplify(',
            ']': ')', ',': ',',
        }

    def translate(self, text: str,
                  source_format: NotationFormat,
                  target_format: NotationFormat) -> TranslationResult:
        """
        Translate mathematical notation from one format to another.

        Args:
            text: Input mathematical expression
            source_format: Format of the input
            target_format: Desired output format

        Returns:
            TranslationResult with translated text and metadata
        """
        try:
            # First, convert to SymPy as intermediate representation
            sympy_expr = self._to_sympy(text, source_format)

            if sympy_expr is None:
                return TranslationResult(
                    success=False,
                    source_format=source_format,
                    target_format=target_format,
                    source_text=text,
                    translated_text="",
                    error_message=f"Failed to parse {source_format.value} input"
                )

            # Convert from SymPy to target format
            translated = self._from_sympy(sympy_expr, target_format)

            return TranslationResult(
                success=True,
                source_format=source_format,
                target_format=target_format,
                source_text=text,
                translated_text=translated,
                sympy_expr=sympy_expr
            )

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return TranslationResult(
                success=False,
                source_format=source_format,
                target_format=target_format,
                source_text=text,
                translated_text="",
                error_message=str(e)
            )

    def _to_sympy(self, text: str, source_format: NotationFormat) -> Optional[Any]:
        """Convert from any format to SymPy expression."""

        if source_format == NotationFormat.SYMPY:
            return self._parse_sympy(text)

        elif source_format == NotationFormat.LATEX:
            return self._latex_to_sympy(text)

        elif source_format == NotationFormat.NATURAL:
            return self._natural_to_sympy(text)

        elif source_format == NotationFormat.UNICODE:
            return self._unicode_to_sympy(text)

        elif source_format == NotationFormat.WOLFRAM:
            return self._wolfram_to_sympy(text)

        elif source_format == NotationFormat.ASCII:
            return self._parse_sympy(text)  # ASCII is similar to SymPy

        elif source_format == NotationFormat.INFIX:
            return self._parse_sympy(text)

        else:
            return None

    def _from_sympy(self, expr: Any, target_format: NotationFormat) -> str:
        """Convert from native symbolic expression to target format. NO SYMPY."""

        if target_format == NotationFormat.SYMPY:
            return str(expr)

        elif target_format == NotationFormat.LATEX:
            return self._native_to_latex(expr)

        elif target_format == NotationFormat.UNICODE:
            return self._native_to_unicode(expr)

        elif target_format == NotationFormat.ASCII:
            return str(expr)

        elif target_format == NotationFormat.MATHML:
            return self._native_to_mathml(expr)

        elif target_format == NotationFormat.NATURAL:
            return self._sympy_to_natural(expr)

        elif target_format == NotationFormat.WOLFRAM:
            return self._sympy_to_wolfram(expr)

        elif target_format == NotationFormat.INFIX:
            return str(expr)

        else:
            return str(expr)

    def _native_to_latex(self, expr: Any) -> str:
        """Convert native symbolic expression to LaTeX. NO SYMPY."""
        if expr is None:
            return ""

        # Use to_latex method if available
        if hasattr(expr, 'to_latex'):
            return expr.to_latex()

        # Fallback: convert string representation to LaTeX
        expr_str = str(expr)

        # Apply transformations
        result = expr_str
        result = re.sub(r'\*\*', '^', result)  # Power
        result = re.sub(r'sqrt\(([^)]+)\)', r'\\sqrt{\1}', result)
        result = re.sub(r'sin\(([^)]+)\)', r'\\sin\\left(\1\\right)', result)
        result = re.sub(r'cos\(([^)]+)\)', r'\\cos\\left(\1\\right)', result)
        result = re.sub(r'tan\(([^)]+)\)', r'\\tan\\left(\1\\right)', result)
        result = re.sub(r'log\(([^)]+)\)', r'\\ln\\left(\1\\right)', result)
        result = re.sub(r'exp\(([^)]+)\)', r'e^{\1}', result)
        result = result.replace('*', ' \\cdot ')
        result = re.sub(r'([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', r'\\frac{\1}{\2}', result)

        return result

    def _native_to_unicode(self, expr: Any) -> str:
        """Convert native symbolic expression to Unicode. NO SYMPY."""
        if expr is None:
            return ""

        expr_str = str(expr)

        # Unicode replacements
        result = expr_str
        result = result.replace('**2', '\u00b2')  # superscript 2
        result = result.replace('**3', '\u00b3')  # superscript 3
        result = result.replace('*', '\u00d7')  # multiplication sign
        result = result.replace('sqrt', '\u221a')  # square root
        result = result.replace('pi', '\u03c0')  # pi
        result = result.replace('alpha', '\u03b1')
        result = result.replace('beta', '\u03b2')
        result = result.replace('gamma', '\u03b3')
        result = result.replace('theta', '\u03b8')
        result = result.replace('omega', '\u03c9')
        result = result.replace('oo', '\u221e')  # infinity

        return result

    def _native_to_mathml(self, expr: Any) -> str:
        """Convert native symbolic expression to MathML. NO SYMPY."""
        if expr is None:
            return "<math></math>"

        expr_str = str(expr)

        # Simple MathML generation
        mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML">\n'
        mathml += f'  <mi>{expr_str}</mi>\n'
        mathml += '</math>'

        return mathml

    def _parse_sympy(self, text: str) -> Optional[Any]:
        """Parse SymPy/Python syntax to native expression. NO SYMPY."""
        try:
            # Replace ^ with ** for power
            text = text.replace('^', '**')

            # Handle implicit multiplication (e.g., 2x -> 2*x, 2 x -> 2*x)
            text = re.sub(r'(\d)\s*([a-zA-Z])', r'\1*\2', text)  # 2x or 2 x -> 2*x
            text = re.sub(r'([a-zA-Z])\s+(\d)', r'\1*\2', text)  # x 2 -> x*2 (with space)
            text = re.sub(r'\)\s*([a-zA-Z0-9])', r')*\1', text)  # ) x -> )*x

            # Handle implicit multiplication before ( but NOT for known functions
            # List of function names that should NOT get * before (
            known_funcs = {'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                          'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh',
                          'log', 'ln', 'exp', 'sqrt', 'abs',
                          'diff', 'integrate', 'limit', 'sum', 'product',
                          'simplify', 'expand', 'factor', 'solve'}

            def add_mult_if_not_func(match):
                prefix = match.group(1)
                # Check if prefix ends with a known function name
                for func in known_funcs:
                    if prefix.lower().endswith(func):
                        return match.group(0)  # Don't add *
                return prefix + '*('

            text = re.sub(r'([a-zA-Z0-9]+)\(', add_mult_if_not_func, text)

            # Parse using native parser
            expr = native_parse_expr(text)
            return expr

        except Exception as e:
            logger.debug(f"Native parse failed: {e}")
            return None

    def _latex_to_sympy(self, text: str) -> Optional[Any]:
        """Convert LaTeX to SymPy."""
        try:
            converted = text

            # Apply all pattern replacements
            for pattern, replacement in self.latex_to_sympy_patterns:
                converted = re.sub(pattern, replacement, converted)

            # Clean up any remaining LaTeX commands
            converted = re.sub(r'\\[a-zA-Z]+', '', converted)

            # Try parsing the result
            return self._parse_sympy(converted)

        except Exception as e:
            logger.debug(f"LaTeX conversion failed: {e}")
            return None

    def _natural_to_sympy(self, text: str) -> Optional[Any]:
        """Convert natural language to SymPy."""
        try:
            converted = text.lower()

            # Apply natural language patterns
            for pattern, replacement in self.natural_to_sympy_patterns:
                converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)

            # Clean up
            converted = converted.strip()

            # If it still looks like natural language, try a simpler approach
            if not self._looks_like_math(converted):
                # Extract just the mathematical parts
                converted = self._extract_math_from_natural(text)

            return self._parse_sympy(converted)

        except Exception as e:
            logger.debug(f"Natural language conversion failed: {e}")
            return None

    def _unicode_to_sympy(self, text: str) -> Optional[Any]:
        """Convert Unicode math to SymPy."""
        try:
            converted = text

            # Replace Unicode symbols
            for unicode_char, ascii_equiv in self.unicode_to_ascii.items():
                converted = converted.replace(unicode_char, ascii_equiv)

            return self._parse_sympy(converted)

        except Exception as e:
            logger.debug(f"Unicode conversion failed: {e}")
            return None

    def _wolfram_to_sympy(self, text: str) -> Optional[Any]:
        """Convert Wolfram/Mathematica syntax to SymPy."""
        try:
            converted = text

            # Replace Wolfram function names
            for wolfram, sympy in self.wolfram_to_sympy.items():
                converted = converted.replace(wolfram, sympy)

            # Handle Wolfram-style function application
            converted = re.sub(r'(\w+)\[([^\]]+)\]', r'\1(\2)', converted)

            return self._parse_sympy(converted)

        except Exception as e:
            logger.debug(f"Wolfram conversion failed: {e}")
            return None

    def _sympy_to_natural(self, expr: Any) -> str:
        """Convert SymPy expression to natural language description."""
        try:
            expr_str = str(expr)

            # Basic replacements
            result = expr_str
            result = re.sub(r'\*\*2\b', ' squared', result)
            result = re.sub(r'\*\*3\b', ' cubed', result)
            result = re.sub(r'\*\*(\d+)', r' to the power of \1', result)
            result = result.replace('*', ' times ')
            result = result.replace('/', ' divided by ')
            result = result.replace('+', ' plus ')
            result = result.replace('-', ' minus ')
            result = result.replace('sqrt', 'the square root of')
            result = result.replace('pi', 'pi')
            result = result.replace('oo', 'infinity')

            # Clean up multiple spaces
            result = re.sub(r'\s+', ' ', result).strip()

            return result

        except Exception:
            return str(expr)

    def _sympy_to_wolfram(self, expr: Any) -> str:
        """Convert SymPy expression to Wolfram syntax."""
        try:
            result = str(expr)

            # Convert function names
            result = result.replace('sin', 'Sin')
            result = result.replace('cos', 'Cos')
            result = result.replace('tan', 'Tan')
            result = result.replace('log', 'Log')
            result = result.replace('exp', 'Exp')
            result = result.replace('sqrt', 'Sqrt')
            result = result.replace('pi', 'Pi')
            result = result.replace('oo', 'Infinity')

            # Convert power notation
            result = re.sub(r'\*\*', '^', result)

            # Convert function calls to bracket notation
            result = re.sub(r'(\w+)\(([^)]+)\)', r'\1[\2]', result)

            return result

        except Exception:
            return str(expr)

    def _looks_like_math(self, text: str) -> bool:
        """Check if text looks like a mathematical expression."""
        # Contains operators or function calls
        math_indicators = ['+', '-', '*', '/', '**', '^', '(', ')',
                         'sin', 'cos', 'tan', 'log', 'exp', 'sqrt',
                         'diff', 'integrate', 'solve', 'factor']
        return any(ind in text for ind in math_indicators)

    def _extract_math_from_natural(self, text: str) -> str:
        """Extract mathematical content from natural language."""
        # Find expressions in quotes or after "is" / "equals"
        match = re.search(r'"([^"]+)"', text)
        if match:
            return match.group(1)

        match = re.search(r'(?:is|equals?|=)\s*(.+?)(?:\.|$)', text)
        if match:
            return match.group(1).strip()

        # Just return the original, cleaned up
        return re.sub(r'[^a-zA-Z0-9+\-*/^().,\s]', '', text)

    def detect_format(self, text: str) -> NotationFormat:
        """
        Auto-detect the notation format of input text.

        Args:
            text: Input mathematical expression

        Returns:
            Detected NotationFormat
        """
        # Check for LaTeX
        if re.search(r'\\[a-zA-Z]+', text) or re.search(r'\{.*\}', text):
            return NotationFormat.LATEX

        # Check for Wolfram
        if re.search(r'[A-Z][a-z]+\[', text):
            return NotationFormat.WOLFRAM

        # Check for Unicode math
        unicode_chars = set(self.unicode_to_ascii.keys())
        if any(c in text for c in unicode_chars):
            return NotationFormat.UNICODE

        # Check for natural language
        natural_words = ['the', 'of', 'with', 'respect', 'to', 'squared',
                        'derivative', 'integral', 'solve', 'equals']
        word_count = sum(1 for w in natural_words if w in text.lower())
        if word_count >= 2:
            return NotationFormat.NATURAL

        # Default to SymPy/infix
        return NotationFormat.SYMPY

    def translate_auto(self, text: str, target_format: NotationFormat) -> TranslationResult:
        """
        Translate with automatic source format detection.

        Args:
            text: Input mathematical expression
            target_format: Desired output format

        Returns:
            TranslationResult with translated text
        """
        source_format = self.detect_format(text)
        return self.translate(text, source_format, target_format)

    def get_all_formats(self, text: str) -> Dict[NotationFormat, str]:
        """
        Convert input to all available formats.

        Args:
            text: Input mathematical expression

        Returns:
            Dictionary mapping NotationFormat to translated string
        """
        source_format = self.detect_format(text)
        results = {}

        for target_format in NotationFormat:
            try:
                result = self.translate(text, source_format, target_format)
                if result.success:
                    results[target_format] = result.translated_text
            except Exception:
                continue

        return results

    # BDI Agent methods
    def update_beliefs(self):
        """Update beliefs based on percepts. Reactive agent - no persistent beliefs."""
        pass

    def deliberate(self) -> Optional[Intention]:
        """Select an intention to pursue based on current beliefs and desires."""
        return None  # Reactive agent - responds to translate() calls

    def execute_step(self, intention: Intention):
        """Execute a step of an intention. Reactive agent - no multi-step intentions."""
        pass

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a translation task.

        Expected task format:
        {
            'text': str,
            'source_format': str or NotationFormat (optional, auto-detected if missing),
            'target_format': str or NotationFormat
        }
        """
        text = task.get('text', '')
        target = task.get('target_format', 'sympy')
        source = task.get('source_format')

        # Convert string to enum if needed
        if isinstance(target, str):
            target = NotationFormat(target.lower())
        if isinstance(source, str):
            source = NotationFormat(source.lower())

        if source:
            result = self.translate(text, source, target)
        else:
            result = self.translate_auto(text, target)

        return {
            'success': result.success,
            'translated': result.translated_text,
            'source_format': result.source_format.value,
            'target_format': result.target_format.value,
            'error': result.error_message
        }


# Convenience functions
def translate_notation(text: str,
                       target_format: str = 'sympy',
                       source_format: str = None) -> str:
    """
    Quick translation function.

    Args:
        text: Input mathematical expression
        target_format: Target format name ('sympy', 'latex', 'natural', etc.)
        source_format: Source format name (auto-detected if None)

    Returns:
        Translated string
    """
    translator = NotationTranslatorAgent("quick_translator")
    target = NotationFormat(target_format.lower())

    if source_format:
        source = NotationFormat(source_format.lower())
        result = translator.translate(text, source, target)
    else:
        result = translator.translate_auto(text, target)

    return result.translated_text if result.success else text


def latex_to_sympy(latex: str) -> str:
    """Convert LaTeX to SymPy syntax."""
    return translate_notation(latex, 'sympy', 'latex')


def sympy_to_latex_str(sympy_text: str) -> str:
    """Convert SymPy syntax to LaTeX."""
    return translate_notation(sympy_text, 'latex', 'sympy')


def natural_to_sympy(natural: str) -> str:
    """Convert natural language to SymPy syntax."""
    return translate_notation(natural, 'sympy', 'natural')


if __name__ == "__main__":
    # Demo
    translator = NotationTranslatorAgent("demo_translator")

    print("\n=== Math Notation Translator Demo ===\n")

    # Test cases
    tests = [
        (r"\frac{x^2}{2}", NotationFormat.LATEX, NotationFormat.SYMPY),
        ("x**2 + 2*x + 1", NotationFormat.SYMPY, NotationFormat.LATEX),
        ("the derivative of x squared with respect to x", NotationFormat.NATURAL, NotationFormat.SYMPY),
        ("x² + 2x + 1", NotationFormat.UNICODE, NotationFormat.SYMPY),
        ("Sin[x] + Cos[x]", NotationFormat.WOLFRAM, NotationFormat.SYMPY),
    ]

    for text, source, target in tests:
        result = translator.translate(text, source, target)
        print(f"{source.value:10} -> {target.value:10}")
        print(f"  Input:  {text}")
        print(f"  Output: {result.translated_text}")
        print()
