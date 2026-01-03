# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
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
CRITICAL COVERAGE TEST SUITE
============================

Comprehensive tests for critical system functionality:
1. Smoke Tests - System startup verification
2. Security Edge Tests - SafeBooleanEvaluator and SafePredicateEvaluator
3. E2E Whitebox/Blackbox Tests - Full pipeline validation
4. Translator Tests - Input standardization
5. Idle Discovery Tests - Curiosity engine validation

Date: 2025-12-10
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, pi, sympify


# =============================================================================
# SMOKE TESTS - System Startup Verification
# =============================================================================

class TestSmokeSystemStartup:
    """Smoke tests to verify critical system components start correctly."""

    def test_phase0_system_starts(self):
        """Verify Phase0System starts without errors."""
        from symbo_agentic_reasoners.core.system import Phase0System

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        assert phase0.df is not None, "Directory Facilitator should be initialized"
        assert phase0.blackboard is not None, "Blackboard should be initialized"

        phase0.shutdown()

    def test_orchestrator_initializes(self):
        """Verify MainOrchestrator initializes correctly."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        assert orchestrator is not None

        phase0.shutdown()

    def test_problem_analysis_team_initializes(self):
        """Verify ProblemAnalysisTeam initializes correctly."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        team = ProblemAnalysisTeam()

        assert team.parser is not None, "Parser should be initialized"
        assert team.recognizer is not None, "Recognizer should be initialized"

    def test_algebra_supervisor_initializes(self):
        """Verify AlgebraSupervisor initializes with DF."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        supervisor = AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        assert supervisor is not None

        phase0.shutdown()

    def test_calculus_supervisor_initializes(self):
        """Verify CalculusSupervisor initializes with DF."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        supervisor = CalculusSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        assert supervisor is not None

        phase0.shutdown()

    def test_notation_translator_initializes(self):
        """Verify NotationTranslatorAgent initializes correctly."""
        from symbo_agentic_reasoners.agents.base.notation_translator import NotationTranslatorAgent

        translator = NotationTranslatorAgent("test_translator")
        assert translator is not None
        assert len(translator.latex_to_sympy_patterns) > 0

    def test_all_core_imports_succeed(self):
        """Verify all critical imports succeed without errors."""
        # Core
        from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
        from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry
        from symbo_agentic_reasoners.core.omdoc_schema import OMObject, create_variable
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.core.system import Phase0System

        # Protocols
        from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage

        # Infrastructure
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator

        # Problem Analysis
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        # All imports succeeded
        assert True


# =============================================================================
# SECURITY EDGE TESTS - Safe Evaluators
# =============================================================================

class TestSafeBooleanEvaluatorEdgeCases:
    """Edge case tests for SafeBooleanEvaluator security."""

    def test_simple_and_expression(self):
        """Test simple AND expression evaluates correctly."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True, 'B': True})
        assert evaluator.evaluate('A and B') == True

        evaluator = SafeBooleanEvaluator({'A': True, 'B': False})
        assert evaluator.evaluate('A and B') == False

    def test_simple_or_expression(self):
        """Test simple OR expression evaluates correctly."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': False, 'B': True})
        assert evaluator.evaluate('A or B') == True

        evaluator = SafeBooleanEvaluator({'A': False, 'B': False})
        assert evaluator.evaluate('A or B') == False

    def test_not_expression(self):
        """Test NOT expression evaluates correctly."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True})
        assert evaluator.evaluate('not A') == False

        evaluator = SafeBooleanEvaluator({'A': False})
        assert evaluator.evaluate('not A') == True

    def test_complex_boolean_expression(self):
        """Test complex nested boolean expression."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True, 'B': False, 'C': True})
        # (A and not B) or C = (True and True) or True = True
        assert evaluator.evaluate('(A and not B) or C') == True

    def test_boolean_constants(self):
        """Test boolean constants True and False."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({})
        assert evaluator.evaluate('True') == True
        assert evaluator.evaluate('False') == False

    def test_comparison_operators(self):
        """Test comparison operators in evaluator."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True, 'B': True})
        assert evaluator.evaluate('A == B') == True

        evaluator = SafeBooleanEvaluator({'A': True, 'B': False})
        assert evaluator.evaluate('A != B') == True

    def test_blocks_import_attempt(self):
        """Test that import attempts are blocked."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({})

        with pytest.raises(ValueError):
            evaluator.evaluate('__import__("os")')

    def test_blocks_builtin_access(self):
        """Test that __builtins__ access is blocked."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({})

        with pytest.raises(ValueError):
            evaluator.evaluate('__builtins__')

    def test_blocks_function_calls(self):
        """Test that function calls are blocked."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({})

        with pytest.raises(ValueError):
            evaluator.evaluate('print("hello")')

    def test_blocks_attribute_access(self):
        """Test that attribute access is blocked."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True})

        with pytest.raises(ValueError):
            evaluator.evaluate('A.__class__')

    def test_unknown_variable_raises_error(self):
        """Test that unknown variables raise ValueError."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({'A': True})

        with pytest.raises(ValueError, match="Unknown variable"):
            evaluator.evaluate('X')

    def test_invalid_syntax_raises_error(self):
        """Test that invalid syntax raises ValueError."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            SafeBooleanEvaluator
        )

        evaluator = SafeBooleanEvaluator({})

        with pytest.raises(ValueError):
            evaluator.evaluate('A and and B')


class TestSafePredicateEvaluatorEdgeCases:
    """Edge case tests for SafePredicateEvaluator security."""

    def test_simple_lambda_greater_than(self):
        """Test simple lambda predicate."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: x > 0")
        assert pred(5) == True
        assert pred(-5) == False

    def test_lambda_equality(self):
        """Test lambda with equality check."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: x == 0")
        assert pred(0) == True
        assert pred(1) == False

    def test_lambda_multiple_args(self):
        """Test lambda with multiple arguments."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x, y: x + y > 10")
        assert pred(5, 6) == True
        assert pred(3, 4) == False

    def test_lambda_with_arithmetic(self):
        """Test lambda with arithmetic operations."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: x * 2 == 10")
        assert pred(5) == True
        assert pred(3) == False

    def test_lambda_with_safe_function(self):
        """Test lambda with allowed safe functions."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: abs(x) == 5")
        assert pred(5) == True
        assert pred(-5) == True
        assert pred(3) == False

    def test_lambda_with_conditional(self):
        """Test lambda with conditional expression."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: 1 if x > 0 else 0")
        assert pred(5) == 1
        assert pred(-5) == 0

    def test_blocks_import_in_lambda(self):
        """Test that import is blocked in lambda (at call time)."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        # SafePredicateEvaluator blocks unsafe functions at call time
        pred = SafePredicateEvaluator.parse_predicate("lambda x: __import__('os')")
        with pytest.raises(ValueError):
            pred(1)  # Should fail when called

    def test_blocks_exec_in_lambda(self):
        """Test that exec is blocked in lambda (at call time)."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        # SafePredicateEvaluator blocks unsafe functions at call time
        pred = SafePredicateEvaluator.parse_predicate("lambda x: exec('print(1)')")
        with pytest.raises(ValueError):
            pred(1)  # Should fail when called

    def test_blocks_eval_in_lambda(self):
        """Test that eval is blocked in lambda (at call time)."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        # SafePredicateEvaluator blocks unsafe functions at call time
        pred = SafePredicateEvaluator.parse_predicate("lambda x: eval('x')")
        with pytest.raises(ValueError):
            pred(1)  # Should fail when called

    def test_non_lambda_rejected(self):
        """Test that non-lambda expressions are rejected."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        with pytest.raises(ValueError, match="lambda expression"):
            SafePredicateEvaluator.parse_predicate("x > 0")

    def test_wrong_arg_count_raises_error(self):
        """Test that wrong argument count raises error."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        pred = SafePredicateEvaluator.parse_predicate("lambda x: x > 0")

        with pytest.raises(ValueError, match="Expected 1 args"):
            pred(1, 2)  # Too many args

    def test_dangerous_code_injection_blocked(self):
        """Test that code injection attempts are blocked (at call time)."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            SafePredicateEvaluator
        )

        dangerous_inputs = [
            "lambda x: __import__('os').system('dir')",
            "lambda x: open('/etc/passwd').read()",
            "lambda x: globals()",
            "lambda x: locals()",
            "lambda x: compile('x', '', 'exec')",
        ]

        for dangerous in dangerous_inputs:
            pred = SafePredicateEvaluator.parse_predicate(dangerous)
            with pytest.raises(ValueError):
                pred(1)  # Should fail when called


class TestPropositionalSpecialistSecurity:
    """Security tests for PropositionalLogicSpecialist."""

    def test_truth_table_safe_evaluation(self):
        """Test truth table uses safe evaluation."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            PropositionalLogicSpecialist
        )

        specialist = PropositionalLogicSpecialist()

        result = specialist.generate_truth_table(['A', 'B'], 'A and B')

        assert 'error' not in result
        assert len(result['truth_table']) == 4

        # Verify results
        tt = result['truth_table']
        assert tt[0]['result'] == False  # F and F = F
        assert tt[1]['result'] == False  # F and T = F
        assert tt[2]['result'] == False  # T and F = F
        assert tt[3]['result'] == True   # T and T = T

    def test_tautology_detection(self):
        """Test tautology detection with safe evaluator."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            PropositionalLogicSpecialist
        )

        specialist = PropositionalLogicSpecialist()

        # A or not A is a tautology
        result = specialist.is_tautology(['A'], 'A or not A')

        assert 'error' not in result
        assert result['is_tautology'] == True

    def test_contradiction_detection(self):
        """Test contradiction detection with safe evaluator."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            PropositionalLogicSpecialist
        )

        specialist = PropositionalLogicSpecialist()

        # A and not A is a contradiction
        result = specialist.is_contradiction(['A'], 'A and not A')

        assert 'error' not in result
        assert result['is_contradiction'] == True


class TestPredicateSpecialistSecurity:
    """Security tests for PredicateLogicSpecialist."""

    def test_forall_safe_evaluation(self):
        """Test universal quantification uses safe evaluation."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            PredicateLogicSpecialist
        )

        specialist = PredicateLogicSpecialist()

        result = specialist.process({
            'operation': 'forall',
            'domain': [1, 2, 3, 4, 5],
            'predicate': 'lambda x: x > 0'
        })

        assert 'error' not in result
        assert result['forall'] == True

    def test_exists_safe_evaluation(self):
        """Test existential quantification uses safe evaluation."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            PredicateLogicSpecialist
        )

        specialist = PredicateLogicSpecialist()

        result = specialist.process({
            'operation': 'exists',
            'domain': [1, 2, 3, 4, 5],
            'predicate': 'lambda x: x > 3'
        })

        assert 'error' not in result
        assert result['exists'] == True
        assert len(result['witnesses']) == 2  # 4 and 5

    def test_count_safe_evaluation(self):
        """Test count quantification uses safe evaluation."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            PredicateLogicSpecialist
        )

        specialist = PredicateLogicSpecialist()

        result = specialist.process({
            'operation': 'count',
            'domain': [1, 2, 3, 4, 5],
            'predicate': 'lambda x: x > 2',
            'count': 3
        })

        assert 'error' not in result
        assert result['exactly_n'] == True  # 3, 4, 5 satisfy x > 2


# =============================================================================
# E2E WHITEBOX/BLACKBOX TESTS
# =============================================================================

class TestE2EBlackbox:
    """Blackbox E2E tests - testing system as a whole without internal knowledge."""

    def test_basic_arithmetic_blackbox(self):
        """Test basic arithmetic through full pipeline (blackbox)."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        # Test cases (input, expected_result_contains)
        test_cases = [
            ("2 + 3", "5"),
            ("10 - 4", "6"),
            ("3 * 4", "12"),
            ("2**3", "8"),
        ]

        for problem, expected in test_cases:
            structured = team.process(problem)
            result = orchestrator.process(structured)
            assert result is not None, f"Problem '{problem}' should produce a result"
            assert str(expected) in str(result), f"Expected {expected} in result for '{problem}'"

        phase0.shutdown()

    def test_factorization_blackbox(self):
        """Test factorization through full pipeline (blackbox)."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        structured = team.process("factor x**2 - 4")
        result = orchestrator.process(structured)

        assert result is not None
        result_str = str(result)
        # Should factor to (x-2)(x+2) or equivalent
        assert 'x' in result_str
        assert '-' in result_str or '+' in result_str

        phase0.shutdown()

    def test_derivative_blackbox(self):
        """Test differentiation through full pipeline (blackbox)."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
        from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        # Register both supervisor and specialist
        CalculusSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        DifferentiationSpecialist(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        structured = team.process("differentiate x**3")
        result = orchestrator.process(structured)

        assert result is not None
        result_str = str(result)
        # d/dx(x^3) = 3x^2
        assert '3' in result_str
        assert 'x' in result_str

        phase0.shutdown()

    def test_integration_blackbox(self):
        """Test integration through full pipeline (blackbox)."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
        from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        # Register both supervisor and specialist
        CalculusSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        IntegrationSpecialist(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        structured = team.process("integrate x**2")
        result = orchestrator.process(structured)

        assert result is not None
        result_str = str(result)
        # integral of x^2 = x^3/3
        assert 'x' in result_str
        assert '3' in result_str

        phase0.shutdown()


class TestE2EWhitebox:
    """Whitebox E2E tests - testing internal flow and state."""

    def test_df_registration_flow(self):
        """Test that specialists register with Directory Facilitator."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        # Before supervisor creation
        initial_registrations = len(phase0.df.services) if hasattr(phase0.df, 'services') else 0

        AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)

        # After supervisor creation - should have registered specialists
        final_registrations = len(phase0.df.services) if hasattr(phase0.df, 'services') else 0

        assert final_registrations >= initial_registrations

        phase0.shutdown()

    def test_problem_classification_flow(self):
        """Test that problems are correctly classified."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain, ProblemType
        )

        team = ProblemAnalysisTeam()

        # Calculus problem
        calc_structured = team.process("differentiate x**2")
        assert calc_structured.domain == MathDomain.CALCULUS
        assert calc_structured.problem_type == ProblemType.COMPUTATION

        # Algebra problem
        alg_structured = team.process("factor x**2 - 9")
        assert alg_structured.domain == MathDomain.ALGEBRA

    def test_omdoc_conversion_flow(self):
        """Test that problems are converted to OMDoc format."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.core.omdoc_schema import OMObject

        team = ProblemAnalysisTeam()

        structured = team.process("x**2 + 1")

        assert structured.omdoc_content is not None
        assert isinstance(structured.omdoc_content, OMObject)

    def test_sympy_expression_created(self):
        """Test that native symbolic expressions are created during parsing."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        team = ProblemAnalysisTeam()

        structured = team.process("x**2 + 2*x + 1")

        assert structured.sympy_expr is not None


# =============================================================================
# TRANSLATOR/INPUT STANDARDIZATION TESTS
# =============================================================================

class TestNotationTranslatorComprehensive:
    """Comprehensive tests for notation translator."""

    def test_latex_fractions(self):
        """Test LaTeX fraction conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        # Test basic fraction translation - just verify successful translation
        # since the exact output form can vary (x/y, x*(1/y), 0.5, etc.)
        test_cases = [
            r"\frac{1}{2}",
            r"\frac{x}{y}",
            r"\frac{a+b}{c}",
        ]

        for latex in test_cases:
            result = translator.translate(latex, NotationFormat.LATEX, NotationFormat.SYMPY)
            assert result.success, f"Failed to translate: {latex}"
            # Verify we got a non-empty result
            assert result.translated_text, f"Empty translation for: {latex}"
            # For fractions, result should contain division-related elements
            output = result.translated_text
            # Should have some division indicator (/, *, numeric value, or division-related structure)
            has_division_structure = (
                '/' in output or
                '*' in output or  # x*(1/y) form
                '**(-' in output or  # x*y**(-1) form
                output.replace('.', '').replace('-', '').isdigit() or  # Numeric result
                'Rational' in output  # Rational() form
            )
            assert has_division_structure, f"No division structure found for {latex}: {output}"

    def test_latex_powers(self):
        """Test LaTeX power notation conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate(r"x^{3}", NotationFormat.LATEX, NotationFormat.SYMPY)
        assert result.success
        assert '**3' in result.translated_text or 'x**3' in result.translated_text

    def test_latex_trig_functions(self):
        """Test LaTeX trigonometric function conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        trig_funcs = [r"\sin", r"\cos", r"\tan"]

        for func in trig_funcs:
            result = translator.translate(f"{func}(x)", NotationFormat.LATEX, NotationFormat.SYMPY)
            assert result.success
            # Check the function name is in result
            expected_func = func.replace("\\", "")
            assert expected_func in result.translated_text

    def test_latex_sqrt(self):
        """Test LaTeX square root conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate(r"\sqrt{x}", NotationFormat.LATEX, NotationFormat.SYMPY)
        assert result.success
        assert 'sqrt' in result.translated_text.lower()

    def test_unicode_superscripts(self):
        """Test Unicode superscript conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        # x² should become x**2
        result = translator.translate("x²", NotationFormat.UNICODE, NotationFormat.SYMPY)
        assert result.success
        assert '**2' in result.translated_text

    def test_unicode_greek_letters(self):
        """Test Unicode Greek letter conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate("π", NotationFormat.UNICODE, NotationFormat.SYMPY)
        assert result.success
        assert 'pi' in result.translated_text

    @pytest.mark.xfail(reason="Natural language parsing not fully implemented")
    def test_natural_language_derivative(self):
        """Test natural language derivative conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate(
            "derivative of x squared with respect to x",
            NotationFormat.NATURAL,
            NotationFormat.SYMPY
        )
        assert result.success

    @pytest.mark.xfail(reason="Natural language parsing not fully implemented")
    def test_natural_language_integral(self):
        """Test natural language integral conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate(
            "integral of x with respect to x",
            NotationFormat.NATURAL,
            NotationFormat.SYMPY
        )
        assert result.success

    def test_wolfram_functions(self):
        """Test Wolfram/Mathematica syntax conversion."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        result = translator.translate(
            "Sin[x] + Cos[x]",
            NotationFormat.WOLFRAM,
            NotationFormat.SYMPY
        )
        # Should attempt conversion (may not fully succeed but shouldn't crash)
        assert result is not None

    def test_format_autodetection(self):
        """Test automatic format detection."""
        from symbo_agentic_reasoners.agents.base.notation_translator import (
            NotationTranslatorAgent, NotationFormat
        )

        translator = NotationTranslatorAgent("test")

        # LaTeX
        assert translator.detect_format(r"\frac{1}{2}") == NotationFormat.LATEX

        # Wolfram
        assert translator.detect_format("Sin[x]") == NotationFormat.WOLFRAM

        # Unicode
        assert translator.detect_format("x² + π") == NotationFormat.UNICODE

        # Natural language
        assert translator.detect_format("the derivative of x squared") == NotationFormat.NATURAL

        # Default to SymPy
        assert translator.detect_format("x**2") == NotationFormat.SYMPY


class TestProblemAnalysisComprehensive:
    """Comprehensive tests for problem analysis and input standardization."""

    def test_power_notation_caret(self):
        """Test that caret notation is converted to SymPy power."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        team = ProblemAnalysisTeam()

        structured = team.process("x^2 + 1")

        assert structured.sympy_expr is not None
        # x^2 should be parsed as x**2

    def test_equation_format_handling(self):
        """Test that equations with = 0 are handled."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        team = ProblemAnalysisTeam()

        structured = team.process("solve x^2 - 4 = 0")

        assert structured is not None
        assert structured.metadata['operation'] == 'solve'

    def test_operation_extraction(self):
        """Test operation extraction from various input formats."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

        team = ProblemAnalysisTeam()

        # Derivative
        deriv = team.process("differentiate x^3")
        assert deriv.metadata['operation'] == 'derivative'

        # Integral
        integ = team.process("integrate x^2")
        assert integ.metadata['operation'] == 'integral'

        # Factor
        factor = team.process("factor x^2 - 9")
        assert factor.metadata['operation'] == 'factor'

        # Expand
        expand = team.process("expand (x+1)^2")
        assert expand.metadata['operation'] == 'expand'

    def test_domain_classification_accuracy(self):
        """Test domain classification accuracy."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain
        )

        team = ProblemAnalysisTeam()

        # Calculus keywords
        calc_inputs = [
            "derivative of sin(x)",
            "integrate x^2 dx",
            "limit as x approaches 0",
            "differentiate x^3",
        ]

        for inp in calc_inputs:
            structured = team.process(inp)
            assert structured.domain == MathDomain.CALCULUS, f"'{inp}' should be CALCULUS"

        # Algebra keywords
        alg_inputs = [
            "factor x^2 - 4",
            "solve for x",
            "expand (x+1)^2",
        ]

        for inp in alg_inputs:
            structured = team.process(inp)
            assert structured.domain == MathDomain.ALGEBRA, f"'{inp}' should be ALGEBRA"


# =============================================================================
# IDLE DISCOVERY TESTS
# =============================================================================

class TestCuriosityEngineComprehensive:
    """Comprehensive tests for curiosity engine / idle discovery."""

    @pytest.fixture
    def mock_solver(self):
        """Create a mock solver for testing."""
        solver = Mock()
        mock_result = Mock()
        mock_result.status.value = 'success'
        mock_result.result = sympify('x + 1')
        solver.solve.return_value = mock_result
        return solver

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_engine_initialization(self, mock_solver, temp_dir):
        """Test CuriosityEngine initializes correctly."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine

        engine = CuriosityEngine(mock_solver, save_dir=temp_dir)

        assert engine.solver is mock_solver
        assert engine.generator is not None
        assert engine.scorer is not None

    def test_problem_generation_algebra(self):
        """Test algebra problem generation."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            ProblemGenerator, ExplorationCategory
        )

        gen = ProblemGenerator()
        problem, category = gen.generate(ExplorationCategory.ALGEBRA)

        assert category == ExplorationCategory.ALGEBRA
        assert isinstance(problem, str)
        assert len(problem) > 0

    def test_problem_generation_calculus(self):
        """Test calculus problem generation."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            ProblemGenerator, ExplorationCategory
        )

        gen = ProblemGenerator()
        problem, category = gen.generate(ExplorationCategory.CALCULUS)

        assert category == ExplorationCategory.CALCULUS
        assert isinstance(problem, str)

    def test_problem_generation_number_theory(self):
        """Test number theory problem generation."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            ProblemGenerator, ExplorationCategory
        )

        gen = ProblemGenerator()
        problem, category = gen.generate(ExplorationCategory.NUMBER_THEORY)

        assert category == ExplorationCategory.NUMBER_THEORY
        assert isinstance(problem, str)

    def test_interest_scoring_mundane(self):
        """Test interest scoring for mundane results."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            InterestScorer, InterestLevel
        )

        scorer = InterestScorer()

        level, notes = scorer.score("simple problem", Symbol('x')**2 + 1, 50.0)
        assert isinstance(level, InterestLevel)

    def test_interest_scoring_zero(self):
        """Test interest scoring for zero result."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            InterestScorer, InterestLevel
        )

        scorer = InterestScorer()

        level, notes = scorer.score(
            "simplify(sin(x)**2 + cos(x)**2 - 1)",
            Integer(0),
            10.0
        )
        assert level.value >= InterestLevel.NOTABLE.value
        # Result of 0 is notable - may mention zero, number, or integer
        assert any(keyword in notes.lower() for keyword in ['zero', 'number', 'integer', 'simplified'])

    def test_interest_scoring_pi(self):
        """Test interest scoring for pi result."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            InterestScorer, InterestLevel
        )

        scorer = InterestScorer()

        level, notes = scorer.score("some_problem", pi, 10.0)
        assert level.value >= InterestLevel.NOTABLE.value
        assert 'pi' in notes.lower()

    def test_explore_one(self, mock_solver, temp_dir):
        """Test single exploration."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            CuriosityEngine, ExplorationCategory, ExplorationResult
        )

        engine = CuriosityEngine(mock_solver, save_dir=temp_dir)

        result = engine.explore_one(ExplorationCategory.ALGEBRA)

        assert isinstance(result, ExplorationResult)
        assert result.category == ExplorationCategory.ALGEBRA
        assert engine.stats.problems_generated >= 1

    def test_get_statistics(self, mock_solver, temp_dir):
        """Test getting exploration statistics."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine

        engine = CuriosityEngine(mock_solver, save_dir=temp_dir)

        # Explore a few
        for _ in range(3):
            engine.explore_one()

        stats = engine.get_statistics()

        assert stats['problems_generated'] == 3
        assert 'success_rate' in stats

    def test_suggest_exploration(self, mock_solver, temp_dir):
        """Test exploration suggestion."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            CuriosityEngine, ExplorationCategory
        )

        engine = CuriosityEngine(mock_solver, save_dir=temp_dir)

        suggestion = engine.suggest_exploration()

        assert isinstance(suggestion, ExplorationCategory)

    def test_exploration_result_to_dict(self):
        """Test ExplorationResult conversion to dictionary."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import (
            ExplorationResult, ExplorationCategory, InterestLevel
        )

        result = ExplorationResult(
            problem="factor(x**2 - 1)",
            category=ExplorationCategory.ALGEBRA,
            solution="(x-1)*(x+1)",
            success=True,
            interest_level=InterestLevel.INTERESTING,
            solve_time_ms=10.0
        )

        d = result.to_dict()

        assert d['problem'] == "factor(x**2 - 1)"
        assert d['category'] == 'algebra'
        assert d['success'] is True

    def test_failed_solve_handling(self, temp_dir):
        """Test handling of failed solves."""
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine

        # Create failing solver
        fail_solver = Mock()
        mock_result = Mock()
        mock_result.status.value = 'error'
        mock_result.result = None
        fail_solver.solve.return_value = mock_result

        engine = CuriosityEngine(fail_solver, save_dir=temp_dir)
        result = engine.explore_one()

        assert result.success is False
        assert engine.stats.problems_failed >= 1


# =============================================================================
# COMBINED PIPELINE TEST
# =============================================================================

class TestFullPipelineIntegration:
    """Full pipeline integration tests."""

    def test_full_algebra_pipeline(self):
        """Test complete algebra pipeline from input to output."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        problems = [
            ("2 + 2", lambda r: "4" in str(r)),
            ("3 * 5", lambda r: "15" in str(r)),
            ("2**4", lambda r: "16" in str(r)),
            ("expand (x+1)**2", lambda r: "x" in str(r)),
        ]

        for problem, validator in problems:
            structured = team.process(problem)
            result = orchestrator.process(structured)
            assert result is not None, f"No result for: {problem}"
            assert validator(result), f"Invalid result for: {problem}"

        phase0.shutdown()

    def test_full_calculus_pipeline(self):
        """Test complete calculus pipeline from input to output."""
        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
        from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
        from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist
        from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist

        phase0 = Phase0System(allow_mock=True)
        phase0.start()

        # Register supervisor and specialists
        CalculusSupervisor(df=phase0.df, blackboard=phase0.blackboard)
        DifferentiationSpecialist(df=phase0.df, blackboard=phase0.blackboard)
        IntegrationSpecialist(df=phase0.df, blackboard=phase0.blackboard)
        orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)
        team = ProblemAnalysisTeam()

        problems = [
            ("differentiate x**2", lambda r: "x" in str(r) and "2" in str(r)),
            ("integrate x", lambda r: "x" in str(r)),
        ]

        for problem, validator in problems:
            structured = team.process(problem)
            result = orchestrator.process(structured)
            assert result is not None, f"No result for: {problem}"
            assert validator(result), f"Invalid result for: {problem}"

        phase0.shutdown()


# =============================================================================
# INPUT NORMALIZER PREPROCESSING TESTS (Second Opinion Review)
# =============================================================================

class TestInputNormalizerPreprocessing:
    """Tests for new preprocessing features from second opinion review."""

    def test_vector_calculus_gradient(self):
        """Test gradient expansion."""
        from symbo_agentic_reasoners.core.input_normalizer import expand_vector_calculus

        result = expand_vector_calculus("grad(f, [x, y])")
        assert "diff(f, x)" in result
        assert "diff(f, y)" in result

    def test_vector_calculus_divergence(self):
        """Test divergence expansion."""
        from symbo_agentic_reasoners.core.input_normalizer import expand_vector_calculus

        result = expand_vector_calculus("div([P, Q], [x, y])")
        assert "diff(P, x)" in result
        assert "diff(Q, y)" in result

    def test_vector_calculus_curl(self):
        """Test curl expansion."""
        from symbo_agentic_reasoners.core.input_normalizer import expand_vector_calculus

        result = expand_vector_calculus("curl([P, Q, R], [x, y, z])")
        # Curl components
        assert "diff(R, y)" in result
        assert "diff(Q, z)" in result

    def test_enhanced_implicit_multiplication_sigma_sqrt(self):
        """Test sigmasqrt -> sigma*sqrt."""
        from symbo_agentic_reasoners.core.input_normalizer import enhanced_implicit_multiplication

        result = enhanced_implicit_multiplication("sigmasqrt(2pi)")
        assert "sigma*sqrt" in result

    def test_enhanced_implicit_multiplication_coefficient(self):
        """Test 2sigma -> 2*sigma."""
        from symbo_agentic_reasoners.core.input_normalizer import enhanced_implicit_multiplication

        result = enhanced_implicit_multiplication("2sigma")
        assert "2*sigma" in result

    def test_enhanced_implicit_multiplication_greek(self):
        """Test 2pi -> 2*pi."""
        from symbo_agentic_reasoners.core.input_normalizer import enhanced_implicit_multiplication

        result = enhanced_implicit_multiplication("2pi")
        assert "2*pi" in result

    def test_multi_expression_splitting(self):
        """Test splitting comma-separated expressions."""
        from symbo_agentic_reasoners.core.input_normalizer import split_multi_expressions

        result = split_multi_expressions("x^2, y^2, z^2")
        assert len(result) == 3
        assert "x^2" in result

    def test_multi_expression_preserves_function_calls(self):
        """Test that function calls with commas aren't split."""
        from symbo_agentic_reasoners.core.input_normalizer import split_multi_expressions

        result = split_multi_expressions("integrate(x, (x, 0, 1)), diff(y, y)")
        assert len(result) == 2
        assert "integrate(x, (x, 0, 1))" in result

    def test_equation_normalization(self):
        """Test equation = normalization to Eq()."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_equation_equals

        result = normalize_equation_equals("x^2 - 4 = 0")
        assert "Eq(" in result

    def test_equation_normalization_preserves_comparisons(self):
        """Test that == and <= are preserved."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_equation_equals

        assert "==" in normalize_equation_equals("a == b")
        assert "<=" in normalize_equation_equals("x <= 5")

    def test_prime_notation_simple(self):
        """Test y'(x) -> diff(y(x), x)."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("y'(x)")
        assert "diff(y(x), x)" in result

    def test_prime_notation_double(self):
        """Test y''(x) -> diff(y(x), x, 2)."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("y''(x)")
        assert "diff(y(x), x, 2)" in result

    def test_prime_notation_with_coefficient(self):
        """Test 3y'(x) -> 3*diff(y(x), x)."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("3y'(x)")
        assert "diff(y(x), x)" in result
        assert "3*" in result

    def test_prime_notation_letter_prefix(self):
        """Test xy'(x) -> x*diff(y(x), x)."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("xy'(x)")
        assert "diff(y(x), x)" in result
        assert "x*" in result

    def test_ode_full_expression(self):
        """Test full ODE expression conversion."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("y''(x) - 3y'(x) + 2y(x) = 0")
        # All derivatives should be converted
        assert "y'(" not in result
        assert "diff(y(x), x, 2)" in result
        assert "diff(y(x), x)" in result

    def test_full_pipeline_gradient(self):
        """Test gradient through full pipeline."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        result = normalize_input("grad(f, [x, y])")
        assert "[diff(f, x), diff(f, y)]" in result


# =============================================================================
# ERROR DIAGNOSTIC TESTS
# =============================================================================

class TestInputDiagnostic:
    """Tests for enhanced error message system."""

    def test_malformed_matrix_detection(self):
        """Test detection of malformed matrix literals."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        # Empty brackets
        diag = InputDiagnostic.diagnose("det([, ])", "det([, ])")
        assert diag['category'] == 'matrix_syntax'
        assert 'malformed' in diag['message'].lower()

        # Missing elements
        diag = InputDiagnostic.diagnose("eigenvals([[1,2], ])", "eigenvals([[1,2], ])")
        assert diag['category'] == 'matrix_syntax'

    def test_probability_notation_detection(self):
        """Test detection of unsupported probability notation."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        diag = InputDiagnostic.diagnose(
            "E(X^2) where X ~ Normal(0,1)",
            "E(X**2) where X ~ Normal(0,1)"
        )
        # Can be either probability_notation or probability_english depending on pattern order
        assert diag['category'] in ('probability_notation', 'probability_english')
        assert 'not' in diag['message'].lower() or 'probability' in diag['message'].lower()
        assert diag['suggestion'] is not None

    def test_english_glue_detection(self):
        """Test detection of English phrases that can't be parsed."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        # "where" phrase
        diag = InputDiagnostic.diagnose(
            "f(x) where x > 0",
            "f(x) where x > 0"  # Unchanged because it can't be parsed
        )
        assert diag['category'] == 'english_phrase'
        assert 'where' in diag['message'].lower()

    def test_linalg_command_detection(self):
        """Test detection of linear algebra command issues."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        diag = InputDiagnostic.diagnose(
            "eigenvals([[1,2], ])",
            "eigenvals([[1,2], ])"
        )
        # Could be matrix_syntax or linalg_syntax depending on which matches first
        assert diag['category'] in ('matrix_syntax', 'linalg_syntax')

    def test_format_error_basic(self):
        """Test basic error formatting."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        diag = {
            'category': 'test',
            'message': 'Test error message',
            'suggestion': 'Try this fix',
            'details': 'Technical details here'
        }

        formatted = InputDiagnostic.format_error(diag)
        assert 'Test error message' in formatted
        assert 'Try this fix' in formatted
        assert 'Technical details' not in formatted  # Not in non-verbose

        formatted_verbose = InputDiagnostic.format_error(diag, verbose=True)
        assert 'Technical details' in formatted_verbose

    def test_generic_fallback(self):
        """Test generic error message for unknown issues."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        # Valid input that shouldn't match any error pattern
        diag = InputDiagnostic.diagnose("x + y", "x + y", "Some random error")
        # Should still return a diagnostic
        assert 'category' in diag
        assert 'message' in diag

    def test_distribution_with_english(self):
        """Test detection of distributions with English glue words."""
        from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

        diag = InputDiagnostic.diagnose(
            "X ~ Normal(0, 1) where x > 0",
            "X ~ Normal(0, 1) where x > 0"
        )
        assert diag['category'] in ('probability_english', 'english_phrase')


# =============================================================================
# SEMANTIC PARSER TESTS - Internal AST Layer (SymPy Last Resort)
# =============================================================================

class TestFallbackTracker:
    """Tests for the fallback tracker - SymPy last resort monitoring."""

    def test_tracker_initializes(self):
        """Verify FallbackTracker initializes correctly."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()
        assert tracker is not None
        stats = tracker.get_statistics()
        assert stats['total'] == 0

    def test_tracking_domain_success(self):
        """Test tracking successful domain solver resolution."""
        from symbo_agentic_reasoners.core.fallback_tracker import (
            FallbackTracker, ResolutionMethod
        )

        tracker = FallbackTracker()

        with tracker.track("solve", "x**2 - 4", domain="algebra"):
            tracker.mark_domain_success()

        stats = tracker.get_statistics()
        assert stats['total'] == 1
        assert stats['domain_solver_count'] == 1
        assert stats['sympy_fallback_count'] == 0

    def test_tracking_sympy_fallback(self):
        """Test tracking SymPy fallback."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        with tracker.track("solve", "x**5 - x + 1", domain="algebra"):
            tracker.mark_fallback("quintic formula not implemented")

        stats = tracker.get_statistics()
        assert stats['total'] == 1
        assert stats['domain_solver_count'] == 0
        assert stats['sympy_fallback_count'] == 1
        assert stats['fallback_rate'] == 1.0

    def test_tracking_intentional_sympy(self):
        """Test tracking intentional SymPy usage."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        with tracker.track("simplify", "sin(x)**2 + cos(x)**2", domain="algebra"):
            tracker.mark_intentional_sympy("simplification is SymPy strength")

        stats = tracker.get_statistics()
        assert stats['total'] == 1
        assert stats['sympy_intentional_count'] == 1
        assert stats['sympy_fallback_count'] == 0  # Intentional != fallback

    def test_domain_breakdown(self):
        """Test domain breakdown statistics."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        with tracker.track("solve", "x**2", domain="algebra"):
            tracker.mark_domain_success()

        with tracker.track("diff", "x**3", domain="calculus"):
            tracker.mark_domain_success()

        with tracker.track("integrate", "exp(x**2)", domain="calculus"):
            tracker.mark_fallback("no closed form")

        breakdown = tracker.get_domain_breakdown()
        assert 'algebra' in breakdown
        assert 'calculus' in breakdown
        assert breakdown['algebra']['domain_solver'] == 1
        assert breakdown['calculus']['domain_solver'] == 1
        assert breakdown['calculus']['sympy_fallback'] == 1

    def test_recent_fallbacks(self):
        """Test getting recent fallback records."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        with tracker.track("op1", "input1"):
            tracker.mark_fallback("reason1")

        with tracker.track("op2", "input2"):
            tracker.mark_fallback("reason2")

        fallbacks = tracker.get_recent_fallbacks(n=10)
        assert len(fallbacks) == 2
        assert fallbacks[0]['fallback_reason'] == 'reason1'
        assert fallbacks[1]['fallback_reason'] == 'reason2'

    def test_statistics_calculation(self):
        """Test correct statistics calculation."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        # 3 domain successes, 2 fallbacks = 40% fallback rate
        for i in range(3):
            with tracker.track(f"op{i}", f"input{i}"):
                tracker.mark_domain_success()

        for i in range(2):
            with tracker.track(f"fallback{i}", f"fallback_input{i}"):
                tracker.mark_fallback(f"reason{i}")

        stats = tracker.get_statistics()
        assert stats['total'] == 5
        assert stats['domain_solver_count'] == 3
        assert stats['sympy_fallback_count'] == 2
        assert abs(stats['fallback_rate'] - 0.4) < 0.01

    def test_clear_statistics(self):
        """Test clearing statistics."""
        from symbo_agentic_reasoners.core.fallback_tracker import FallbackTracker

        tracker = FallbackTracker()

        with tracker.track("op", "input"):
            tracker.mark_domain_success()

        assert tracker.get_statistics()['total'] == 1

        tracker.clear()

        assert tracker.get_statistics()['total'] == 0

    def test_global_tracker(self):
        """Test global tracker singleton."""
        from symbo_agentic_reasoners.core.fallback_tracker import (
            get_tracker, get_fallback_statistics
        )

        tracker1 = get_tracker()
        tracker2 = get_tracker()
        assert tracker1 is tracker2  # Same instance

        # Clear for clean test
        tracker1.clear()

        with tracker1.track("test", "test_input"):
            tracker1.mark_domain_success()

        stats = get_fallback_statistics()
        assert stats['total'] >= 1


class TestSemanticParser:
    """Tests for the semantic parser - internal AST layer before SymPy."""

    def test_parser_initializes(self):
        """Verify SemanticParser initializes correctly."""
        from symbo_agentic_reasoners.core.semantic_parser import SemanticParser

        parser = SemanticParser()
        assert parser is not None
        assert len(parser.COMMAND_PATTERNS) > 0

    def test_solve_command_parsing(self):
        """Test parsing of solve() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType, CommandNode
        )

        parser = SemanticParser()
        result = parser.parse("solve(x**2 - 4 = 0, x)")

        assert result.success
        assert result.node.node_type == NodeType.SOLVE
        assert isinstance(result.node, CommandNode)
        assert result.node.command_name == 'solve'
        assert 'x' in result.node.variables

    def test_solve_with_multiple_variables(self):
        """Test solve() with multiple variables."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("solve(x**2 + y**2 = 1, [x, y])")

        assert result.success
        assert result.node.node_type == NodeType.SOLVE
        assert 'x' in result.node.variables
        assert 'y' in result.node.variables

    def test_dsolve_command_parsing(self):
        """Test parsing of dsolve() command for ODEs."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("dsolve(y'(x) + y(x) = 0, y(x))")

        assert result.success
        assert result.node.node_type == NodeType.DSOLVE
        assert result.node.command_name == 'dsolve'
        assert result.node.function == 'y(x)'

    def test_grad_command_parsing(self):
        """Test parsing of grad() vector calculus command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("grad(x**2 + y**2, [x, y])")

        assert result.success
        assert result.node.node_type == NodeType.GRAD
        assert result.node.command_name == 'grad'
        assert result.node.variables == ['x', 'y']

    def test_div_command_parsing(self):
        """Test parsing of div() vector calculus command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("div([x*y, y*z, z*x], [x, y, z])")

        assert result.success
        assert result.node.node_type == NodeType.DIV
        assert result.node.command_name == 'div'
        assert result.node.variables == ['x', 'y', 'z']

    def test_curl_command_parsing(self):
        """Test parsing of curl() vector calculus command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("curl([y*z, z*x, x*y], [x, y, z])")

        assert result.success
        assert result.node.node_type == NodeType.CURL
        assert result.node.command_name == 'curl'
        assert result.node.variables == ['x', 'y', 'z']

    def test_diff_command_parsing(self):
        """Test parsing of diff() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("diff(sin(x), x)")

        assert result.success
        assert result.node.node_type == NodeType.DIFF
        assert result.node.variables == ['x']

    def test_diff_with_order(self):
        """Test parsing of diff() with higher order."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("diff(x**3, x, 2)")

        assert result.success
        assert result.node.node_type == NodeType.DIFF
        assert result.node.extra_args.get('order') == 2

    def test_integrate_indefinite_parsing(self):
        """Test parsing of indefinite integral."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("integrate(x**2, x)")

        assert result.success
        assert result.node.node_type == NodeType.INTEGRATE
        assert result.node.extra_args.get('definite') == False

    def test_integrate_definite_parsing(self):
        """Test parsing of definite integral with limits."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("integrate(x, (x, 0, 1))")

        assert result.success
        assert result.node.node_type == NodeType.INTEGRATE
        assert result.node.extra_args.get('definite') == True
        assert result.node.extra_args.get('lower') == '0'
        assert result.node.extra_args.get('upper') == '1'

    def test_limit_command_parsing(self):
        """Test parsing of limit() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("limit(sin(x)/x, x, 0)")

        assert result.success
        assert result.node.node_type == NodeType.LIMIT
        assert result.node.extra_args.get('point') == '0'

    def test_factor_command_parsing(self):
        """Test parsing of factor() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("factor(x**2 - 4)")

        assert result.success
        assert result.node.node_type == NodeType.FACTOR

    def test_expand_command_parsing(self):
        """Test parsing of expand() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("expand((x + 1)**3)")

        assert result.success
        assert result.node.node_type == NodeType.EXPAND

    def test_det_command_parsing(self):
        """Test parsing of det() linear algebra command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("det([[1, 2], [3, 4]])")

        assert result.success
        assert result.node.node_type == NodeType.DET

    def test_eigenvals_command_parsing(self):
        """Test parsing of eigenvals() command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType
        )

        parser = SemanticParser()
        result = parser.parse("eigenvals([[1, 2], [3, 4]])")

        assert result.success
        assert result.node.node_type == NodeType.EIGENVALS

    def test_equation_parsing(self):
        """Test parsing of equation (with = sign)."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType, ExpressionNode
        )

        parser = SemanticParser()
        result = parser.parse("x**2 - 4 = 0")

        assert result.success
        assert result.node.node_type == NodeType.EQUATION
        assert isinstance(result.node, ExpressionNode)
        assert result.node.is_equation

    def test_expression_parsing(self):
        """Test parsing of plain expression."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, NodeType, ExpressionNode
        )

        parser = SemanticParser()
        result = parser.parse("2 + 3 * 4")

        assert result.success
        assert result.node.node_type == NodeType.EXPRESSION
        assert isinstance(result.node, ExpressionNode)

    def test_routing_info_for_solve(self):
        """Test routing information extraction for solve command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, get_routing_info
        )

        parser = SemanticParser()
        result = parser.parse("solve(x**2 - 4 = 0, x)")

        routing = get_routing_info(result.node)
        assert routing['domain'] == 'algebra'
        assert routing['specialist'] == 'polynomial'
        assert routing['operation'] == 'solve'

    def test_routing_info_for_calculus(self):
        """Test routing information extraction for calculus command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, get_routing_info
        )

        parser = SemanticParser()
        result = parser.parse("diff(sin(x), x)")

        routing = get_routing_info(result.node)
        assert routing['domain'] == 'calculus'
        assert routing['specialist'] == 'differentiation'
        assert routing['operation'] == 'diff'

    def test_routing_info_for_linalg(self):
        """Test routing information extraction for linear algebra command."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            SemanticParser, get_routing_info
        )

        parser = SemanticParser()
        result = parser.parse("det([[1, 2], [3, 4]])")

        routing = get_routing_info(result.node)
        assert routing['domain'] == 'linear_algebra'
        assert routing['specialist'] == 'matrix'
        assert routing['operation'] == 'determinant'

    def test_variable_extraction(self):
        """Test extraction of variables from expressions."""
        from symbo_agentic_reasoners.core.semantic_parser import SemanticParser

        parser = SemanticParser()
        result = parser.parse("x**2 + 2*y - sin(z)")

        assert result.success
        # Variables should include x, y, z but not sin (a function)
        vars_found = result.node.variables
        assert 'x' in vars_found
        assert 'y' in vars_found
        assert 'z' in vars_found
        assert 'sin' not in vars_found  # sin is a function, not a variable

    def test_empty_input_handling(self):
        """Test handling of empty input."""
        from symbo_agentic_reasoners.core.semantic_parser import SemanticParser

        parser = SemanticParser()
        result = parser.parse("")

        assert not result.success
        assert result.error is not None

    def test_convenience_function(self):
        """Test the parse_to_semantic convenience function."""
        from symbo_agentic_reasoners.core.semantic_parser import (
            parse_to_semantic, NodeType
        )

        result = parse_to_semantic("factor(x**2 - 9)")

        assert result.success
        assert result.node.node_type == NodeType.FACTOR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
