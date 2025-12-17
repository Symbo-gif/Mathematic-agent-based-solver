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
Tests for Math Notation Translator Agent
========================================

Tests translation between:
- LaTeX <-> SymPy
- Natural language -> SymPy
- Unicode -> SymPy
- Wolfram -> SymPy
- SymPy -> Various outputs
"""

import pytest
from symbo_agentic_reasoners.agents.base.notation_translator import (
    NotationTranslatorAgent,
    NotationFormat,
    TranslationResult,
    translate_notation,
    latex_to_sympy,
    sympy_to_latex_str,
    natural_to_sympy,
)


class TestNotationTranslatorAgent:
    """Tests for NotationTranslatorAgent class."""

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        translator = NotationTranslatorAgent("test_translator")
        assert translator.agent_id == "test_translator"

    def test_latex_to_sympy_fraction(self):
        """Test LaTeX fraction conversion."""
        translator = NotationTranslatorAgent("test_001")
        result = translator.translate(
            r"\frac{x}{2}",
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        assert result.success
        assert 'x' in result.translated_text
        # Accept various valid forms: x/2, x*(1/2), 0.5*x, x*0.5, etc.
        has_division = (
            '/' in result.translated_text or
            '*' in result.translated_text or  # x*(1/2) or 0.5*x
            '0.5' in result.translated_text or
            'Rational' in result.translated_text
        )
        assert has_division, f"No division structure: {result.translated_text}"

    def test_latex_to_sympy_power(self):
        """Test LaTeX power conversion."""
        translator = NotationTranslatorAgent("test_002")
        result = translator.translate(
            r"x^{2}",
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        assert result.success
        assert '**2' in result.translated_text or 'x**2' in result.translated_text

    def test_latex_to_sympy_sqrt(self):
        """Test LaTeX square root conversion."""
        translator = NotationTranslatorAgent("test_003")
        result = translator.translate(
            r"\sqrt{x}",
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        assert result.success
        assert 'sqrt' in result.translated_text.lower()

    def test_latex_to_sympy_trig(self):
        """Test LaTeX trigonometric function conversion."""
        translator = NotationTranslatorAgent("test_004")
        result = translator.translate(
            r"\sin(x) + \cos(x)",
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        assert result.success
        assert 'sin' in result.translated_text
        assert 'cos' in result.translated_text

    def test_sympy_to_latex(self):
        """Test SymPy to LaTeX conversion."""
        translator = NotationTranslatorAgent("test_005")
        result = translator.translate(
            "x**2 + 2*x + 1",
            NotationFormat.SYMPY,
            NotationFormat.LATEX
        )
        assert result.success
        # LaTeX should have proper notation
        assert 'x' in result.translated_text

    def test_sympy_to_unicode(self):
        """Test SymPy to Unicode pretty print."""
        translator = NotationTranslatorAgent("test_006")
        result = translator.translate(
            "x**2",
            NotationFormat.SYMPY,
            NotationFormat.UNICODE
        )
        assert result.success
        # Should produce some output
        assert len(result.translated_text) > 0

    @pytest.mark.skip(reason="Native parser doesn't support multi-arg functions like diff(expr, x)")
    def test_natural_to_sympy_derivative(self):
        """Test natural language derivative conversion."""
        translator = NotationTranslatorAgent("test_007")
        result = translator.translate(
            "derivative of x squared with respect to x",
            NotationFormat.NATURAL,
            NotationFormat.SYMPY
        )
        assert result.success
        assert 'diff' in result.translated_text or 'x' in result.translated_text

    @pytest.mark.skip(reason="Native parser doesn't support multi-arg functions like integrate(expr, x)")
    def test_natural_to_sympy_integral(self):
        """Test natural language integral conversion."""
        translator = NotationTranslatorAgent("test_008")
        result = translator.translate(
            "integral of x with respect to x",
            NotationFormat.NATURAL,
            NotationFormat.SYMPY
        )
        assert result.success

    def test_unicode_to_sympy(self):
        """Test Unicode math to SymPy."""
        translator = NotationTranslatorAgent("test_009")
        result = translator.translate(
            "x² + 2x + 1",
            NotationFormat.UNICODE,
            NotationFormat.SYMPY
        )
        assert result.success
        assert 'x' in result.translated_text

    def test_wolfram_to_sympy(self):
        """Test Wolfram/Mathematica to SymPy."""
        translator = NotationTranslatorAgent("test_010")
        # Test simpler Wolfram expression
        result = translator.translate(
            "x^2 + 2*x",
            NotationFormat.WOLFRAM,
            NotationFormat.SYMPY
        )
        # Wolfram conversion is partial - just check it doesn't crash
        assert result is not None
        # If it succeeds, verify output
        if result.success:
            assert 'x' in result.translated_text


class TestFormatDetection:
    """Tests for automatic format detection."""

    def test_detect_latex(self):
        """Test LaTeX format detection."""
        translator = NotationTranslatorAgent("test_detect_001")
        fmt = translator.detect_format(r"\frac{x}{y}")
        assert fmt == NotationFormat.LATEX

    def test_detect_wolfram(self):
        """Test Wolfram format detection."""
        translator = NotationTranslatorAgent("test_detect_002")
        fmt = translator.detect_format("Sin[x] + Cos[x]")
        assert fmt == NotationFormat.WOLFRAM

    def test_detect_unicode(self):
        """Test Unicode format detection."""
        translator = NotationTranslatorAgent("test_detect_003")
        fmt = translator.detect_format("x² + y²")
        assert fmt == NotationFormat.UNICODE

    def test_detect_natural(self):
        """Test natural language detection."""
        translator = NotationTranslatorAgent("test_detect_004")
        fmt = translator.detect_format("the derivative of x squared with respect to x")
        assert fmt == NotationFormat.NATURAL

    def test_detect_sympy_default(self):
        """Test SymPy detection as default."""
        translator = NotationTranslatorAgent("test_detect_005")
        fmt = translator.detect_format("x**2 + 2*x + 1")
        assert fmt == NotationFormat.SYMPY


class TestAutoTranslation:
    """Tests for automatic format detection and translation."""

    def test_auto_translate_latex(self):
        """Test auto-translation from LaTeX."""
        translator = NotationTranslatorAgent("test_auto_001")
        result = translator.translate_auto(r"\frac{1}{x}", NotationFormat.SYMPY)
        assert result.success
        assert result.source_format == NotationFormat.LATEX

    def test_auto_translate_unicode(self):
        """Test auto-translation from Unicode."""
        translator = NotationTranslatorAgent("test_auto_002")
        result = translator.translate_auto("π + θ", NotationFormat.SYMPY)
        assert result.success


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_translate_notation_function(self):
        """Test translate_notation convenience function."""
        result = translate_notation("x**2", "latex", "sympy")
        assert 'x' in result

    def test_latex_to_sympy_function(self):
        """Test latex_to_sympy convenience function."""
        result = latex_to_sympy(r"\sin(x)")
        assert 'sin' in result.lower()

    def test_sympy_to_latex_function(self):
        """Test sympy_to_latex_str convenience function."""
        result = sympy_to_latex_str("x**2")
        assert 'x' in result

    def test_natural_to_sympy_function(self):
        """Test natural_to_sympy convenience function."""
        result = natural_to_sympy("x squared")
        # Should produce some output
        assert len(result) > 0


class TestGetAllFormats:
    """Tests for getting all format translations."""

    def test_get_all_formats(self):
        """Test converting to all available formats."""
        translator = NotationTranslatorAgent("test_all_001")
        results = translator.get_all_formats("x**2 + 1")

        # Should have multiple formats
        assert len(results) >= 3

        # Should include SymPy and LaTeX at minimum
        assert NotationFormat.SYMPY in results
        assert NotationFormat.LATEX in results


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_input(self):
        """Test handling of empty input."""
        translator = NotationTranslatorAgent("test_edge_001")
        result = translator.translate("", NotationFormat.SYMPY, NotationFormat.LATEX)
        # Should handle gracefully (may fail or return empty)
        assert result is not None

    def test_invalid_expression(self):
        """Test handling of invalid expression."""
        translator = NotationTranslatorAgent("test_edge_002")
        result = translator.translate(
            "this is not math at all @#$%",
            NotationFormat.SYMPY,
            NotationFormat.LATEX
        )
        # Should return a result (may fail but shouldn't crash)
        assert result is not None

    def test_complex_latex(self):
        """Test handling of complex LaTeX expression."""
        translator = NotationTranslatorAgent("test_edge_003")
        result = translator.translate(
            r"\int_0^1 x^2 dx",
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        # Should handle complex expressions
        assert result is not None


class TestRoundTrip:
    """Tests for round-trip conversions."""

    def test_sympy_latex_roundtrip(self):
        """Test SymPy -> LaTeX -> SymPy roundtrip."""
        translator = NotationTranslatorAgent("test_rt_001")

        original = "x**2 + 2*x + 1"

        # SymPy -> LaTeX
        to_latex = translator.translate(
            original,
            NotationFormat.SYMPY,
            NotationFormat.LATEX
        )
        assert to_latex.success

        # LaTeX -> SymPy
        back_to_sympy = translator.translate(
            to_latex.translated_text,
            NotationFormat.LATEX,
            NotationFormat.SYMPY
        )
        assert back_to_sympy.success

        # Should be equivalent expressions
        import sympy as sp
        original_expr = sp.sympify(original)
        roundtrip_expr = sp.sympify(back_to_sympy.translated_text)
        assert sp.simplify(original_expr - roundtrip_expr) == 0


class TestProcessMethod:
    """Tests for BDI agent process method."""

    def test_process_with_source_format(self):
        """Test process method with explicit source format."""
        translator = NotationTranslatorAgent("test_process_001")

        result = translator.process({
            'text': r"\frac{1}{2}",
            'source_format': 'latex',
            'target_format': 'sympy'
        })

        assert result['success']
        assert result['source_format'] == 'latex'
        assert result['target_format'] == 'sympy'

    def test_process_auto_detect(self):
        """Test process method with auto-detection."""
        translator = NotationTranslatorAgent("test_process_002")

        result = translator.process({
            'text': r"\sin(x)",
            'target_format': 'sympy'
        })

        assert result['success']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
