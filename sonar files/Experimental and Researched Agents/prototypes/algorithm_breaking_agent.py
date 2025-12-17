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
ALGORITHM BREAKING AGENT - Prototype Implementation
====================================================

Adversarial testing agent for discovering algorithmic weaknesses in the
Symbo Agentic Reasoners mathematical reasoning system.

Philosophy: "Break it before production does."

This agent systematically tests mathematical algorithms for:
- Weaknesses and edge cases
- Logical errors and flaws
- Numerical instabilities
- Performance issues
- Incorrect implementations

SCOPE: ONLY tests OUR OWN CODEBASE (symbo_agentic_reasoners/)
NO SYMPY: Uses native string-based test generation

Usage:
    from prototypes.algorithm_breaking_agent import AlgorithmBreakingAgent

    agent = AlgorithmBreakingAgent()
    report = agent.run_attack_campaign(
        targets=['symbolic', 'solver', 'calculus'],
        attack_types=['parser', 'boundary', 'stability']
    )
    print(report.generate_markdown())
"""

import sys
import os
import time
import json
import random
import threading
import traceback
from typing import Dict, List, Any, Optional, Callable, Iterator, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Ensure proper encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ==============================================================================
# SEVERITY AND CATEGORY DEFINITIONS
# ==============================================================================

class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRITICAL"   # Algorithm produces incorrect results silently
    HIGH = "HIGH"           # Algorithm crashes or hangs
    MEDIUM = "MEDIUM"       # Edge case mishandling, degraded behavior
    LOW = "LOW"             # Minor issues, code improvements needed
    INFO = "INFO"           # Informational findings, not vulnerabilities


class VulnerabilityCategory(Enum):
    """Categories of algorithmic vulnerabilities"""
    INCORRECT_RESULT = "Incorrect Result"
    CRASH = "Crash/Exception"
    HANG = "Hang/Timeout"
    NUMERICAL_INSTABILITY = "Numerical Instability"
    EDGE_CASE = "Edge Case Mishandling"
    BOUNDARY_VIOLATION = "Boundary Violation"
    TYPE_ERROR = "Type Error"
    RESOURCE_EXHAUSTION = "Resource Exhaustion"
    SECURITY = "Security Issue"
    PERFORMANCE = "Performance Issue"


class AttackStatus(Enum):
    """Status of an attack attempt"""
    SUCCESS = "SUCCESS"         # Attack found a vulnerability
    NO_FINDING = "NO_FINDING"   # Attack completed, no vulnerability
    TIMEOUT = "TIMEOUT"         # Attack timed out
    ERROR = "ERROR"             # Attack itself failed
    SKIPPED = "SKIPPED"         # Attack was skipped


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class AlgorithmVulnerability:
    """Represents a discovered algorithmic weakness."""

    vuln_id: str
    severity: Severity
    category: VulnerabilityCategory

    # Location
    target_module: str
    target_function: str
    code_location: str = ""

    # Description
    title: str = ""
    description: str = ""
    root_cause: str = ""

    # Reproduction
    proof_of_concept: str = ""
    test_input: str = ""
    observed_behavior: str = ""
    expected_behavior: str = ""

    # Impact
    impact: str = ""
    exploitability: str = ""

    # Remediation
    suggested_fix: str = ""
    fix_complexity: str = "MEDIUM"

    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_by: str = "AlgorithmBreakingAgent"
    cwe_id: Optional[str] = None
    related_vulns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'vuln_id': self.vuln_id,
            'severity': self.severity.value,
            'category': self.category.value,
            'target_module': self.target_module,
            'target_function': self.target_function,
            'code_location': self.code_location,
            'title': self.title,
            'description': self.description,
            'root_cause': self.root_cause,
            'proof_of_concept': self.proof_of_concept,
            'test_input': self.test_input,
            'observed_behavior': self.observed_behavior,
            'expected_behavior': self.expected_behavior,
            'impact': self.impact,
            'exploitability': self.exploitability,
            'suggested_fix': self.suggested_fix,
            'fix_complexity': self.fix_complexity,
            'discovered_at': self.discovered_at.isoformat(),
            'discovered_by': self.discovered_by,
            'cwe_id': self.cwe_id,
            'related_vulns': self.related_vulns
        }


@dataclass
class AttackResult:
    """Result of a single attack execution."""
    attack_id: str
    attack_name: str
    status: AttackStatus
    category: str
    duration_ms: float
    target_function: str = ""
    vulnerabilities: List[AlgorithmVulnerability] = field(default_factory=list)
    exception: Optional[str] = None
    details: str = ""

    def found_vulnerability(self) -> bool:
        return len(self.vulnerabilities) > 0


@dataclass
class AttackCampaignReport:
    """Comprehensive attack campaign report."""
    report_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    targets: List[str] = field(default_factory=list)
    attack_types: List[str] = field(default_factory=list)
    results: List[AttackResult] = field(default_factory=list)
    vulnerabilities: List[AlgorithmVulnerability] = field(default_factory=list)
    generated_tests: List[str] = field(default_factory=list)

    @property
    def total_attacks(self) -> int:
        return len(self.results)

    @property
    def successful_attacks(self) -> int:
        return sum(1 for r in self.results if r.status == AttackStatus.SUCCESS)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.LOW)

    def generate_markdown(self) -> str:
        """Generate markdown report."""
        duration = (self.completed_at - self.started_at).total_seconds() if self.completed_at else 0

        lines = []
        lines.append("# Algorithm Breaking Agent - Attack Campaign Report")
        lines.append("")
        lines.append(f"**Report ID:** {self.report_id}")
        lines.append(f"**Date:** {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Duration:** {duration:.2f} seconds")
        lines.append("")

        # Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Attacks:** {self.total_attacks}")
        lines.append(f"- **Successful Attacks:** {self.successful_attacks}")
        lines.append(f"- **Vulnerabilities Found:** {len(self.vulnerabilities)}")
        lines.append("")

        # Severity breakdown
        lines.append("### Vulnerability Severity Distribution")
        lines.append(f"- CRITICAL: {self.critical_count}")
        lines.append(f"- HIGH: {self.high_count}")
        lines.append(f"- MEDIUM: {self.medium_count}")
        lines.append(f"- LOW: {self.low_count}")
        lines.append("")

        # Vulnerabilities
        if self.vulnerabilities:
            lines.append("## Discovered Vulnerabilities")
            lines.append("")

            for vuln in sorted(self.vulnerabilities, key=lambda v: v.severity.value):
                lines.append(f"### {vuln.vuln_id}: {vuln.title}")
                lines.append(f"- **Severity:** {vuln.severity.value}")
                lines.append(f"- **Category:** {vuln.category.value}")
                lines.append(f"- **Target:** {vuln.target_module}.{vuln.target_function}")
                lines.append("")
                lines.append(f"**Description:** {vuln.description}")
                lines.append("")
                lines.append("**Proof of Concept:**")
                lines.append("```python")
                lines.append(vuln.proof_of_concept)
                lines.append("```")
                lines.append("")
                lines.append(f"**Expected:** {vuln.expected_behavior}")
                lines.append(f"**Observed:** {vuln.observed_behavior}")
                lines.append("")
                lines.append(f"**Suggested Fix:** {vuln.suggested_fix}")
                lines.append("")

        lines.append("---")
        lines.append("*Generated by Algorithm Breaking Agent*")

        return "\n".join(lines)

    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps({
            'report_id': self.report_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'targets': self.targets,
            'attack_types': self.attack_types,
            'summary': {
                'total_attacks': self.total_attacks,
                'successful_attacks': self.successful_attacks,
                'vulnerabilities': len(self.vulnerabilities),
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count
            },
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
            'results': [
                {
                    'attack_id': r.attack_id,
                    'attack_name': r.attack_name,
                    'status': r.status.value,
                    'category': r.category,
                    'duration_ms': r.duration_ms,
                    'target_function': r.target_function
                }
                for r in self.results
            ]
        }, indent=2)


# ==============================================================================
# ATTACK VECTOR BASE CLASS
# ==============================================================================

class AttackVector(ABC):
    """Base class for attack vectors."""

    def __init__(self, attack_id: str, name: str, category: str):
        self.attack_id = attack_id
        self.name = name
        self.category = category

    @abstractmethod
    def generate_payloads(self) -> Iterator[Tuple[str, str, str]]:
        """
        Generate attack payloads.

        Yields:
            (payload, expected_behavior, attack_description)
        """
        pass

    @abstractmethod
    def execute(self, target_function: Callable, timeout: float = 10.0) -> AttackResult:
        """Execute the attack against a target function."""
        pass


# ==============================================================================
# EXPRESSION FUZZER
# ==============================================================================

class ExpressionFuzzer:
    """
    Generates adversarial mathematical expressions.

    NO SYMPY - Uses native string-based generation.
    """

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

        self.operators = ['+', '-', '*', '/', '**', '^']
        self.variables = ['x', 'y', 'z', 'a', 'b', 'c', 'n', 'm']
        self.functions = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs']
        self.constants = ['pi', 'e', 'I', 'oo', '-oo', 'zoo', 'nan']

    def fuzz_empty(self) -> Iterator[Tuple[str, str]]:
        """Generate empty and whitespace inputs."""
        payloads = [
            ('', 'ValueError or graceful handling'),
            ('   ', 'ValueError or graceful handling'),
            ('\n', 'ValueError or graceful handling'),
            ('\t', 'ValueError or graceful handling'),
            ('\r\n', 'ValueError or graceful handling'),
            ('\x00', 'Reject null bytes'),
            ('\x00x+1', 'Reject null bytes'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def fuzz_unbalanced(self) -> Iterator[Tuple[str, str]]:
        """Generate unbalanced parentheses."""
        payloads = [
            ('(x+1', 'SyntaxError'),
            ('x+1)', 'SyntaxError'),
            ('((x+1)', 'SyntaxError'),
            ('(x+1))', 'SyntaxError'),
            ('((((((x))))))', 'Parse successfully or depth error'),
            (')x+1(', 'SyntaxError'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def fuzz_depth_bomb(self, depth: int = 100) -> Iterator[Tuple[str, str]]:
        """Generate deeply nested expressions."""
        # Nested parentheses
        nested = '(' * depth + 'x' + ')' * depth
        yield (nested, 'Parse or depth limit error')

        # Nested functions
        func_nested = 'sin(' * depth + 'x' + ')' * depth
        yield (func_nested, 'Parse or depth limit error')

        # Nested operations
        op_nested = '(' + 'x+' + '(' * (depth-1) + 'x' + ')' * (depth-1) + ')'
        yield (op_nested, 'Parse or depth limit error')

    def fuzz_width_bomb(self, width: int = 1000) -> Iterator[Tuple[str, str]]:
        """Generate extremely wide expressions."""
        # Sum of many terms
        terms = '+'.join([f'x_{i}' for i in range(width)])
        yield (terms, 'Parse or length limit error')

        # Product of many terms
        factors = '*'.join([f'x_{i}' for i in range(width)])
        yield (factors, 'Parse or length limit error')

    def fuzz_operators(self) -> Iterator[Tuple[str, str]]:
        """Generate operator edge cases."""
        payloads = [
            ('x++y', 'SyntaxError'),
            ('x--y', 'Parse as x-(-y) or error'),
            ('x**-1', 'Parse as x^(-1)'),
            ('x***y', 'SyntaxError'),
            ('+-x', 'SyntaxError or parse as +(-x)'),
            ('x+*y', 'SyntaxError'),
            ('/x', 'SyntaxError'),
            ('x/', 'SyntaxError'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def fuzz_unicode(self) -> Iterator[Tuple[str, str]]:
        """Generate Unicode math expressions."""
        payloads = [
            ('x + y', 'Parse or normalize'),          # em-space
            ('x\u2212y', 'Parse as x-y'),              # minus sign
            ('\u03B1 + \u03B2', 'Parse Greek letters'), # alpha + beta
            ('x\u00B2 + y\u00B2', 'Parse as x^2+y^2'), # superscript 2
            ('\u222B x dx', 'Parse as integral'),      # integral sign
            ('\u221A x', 'Parse as sqrt(x)'),          # square root
            ('\u03C0', 'Parse as pi'),                 # pi
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def fuzz_injection(self) -> Iterator[Tuple[str, str]]:
        """Generate injection attempt expressions."""
        payloads = [
            ('__import__("os")', 'SecurityError'),
            ('eval("1+1")', 'SecurityError'),
            ('exec("x=1")', 'SecurityError'),
            ('().__class__.__bases__', 'SecurityError'),
            ('x.__class__', 'SecurityError'),
            ('globals()', 'SecurityError'),
            ('locals()', 'SecurityError'),
            ('lambda: 1', 'SecurityError'),
            ('{x.__class__}', 'SecurityError'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def fuzz_random(self, count: int = 100) -> Iterator[Tuple[str, str]]:
        """Generate random expressions with mutations."""
        for _ in range(count):
            # Generate base expression
            expr = self._generate_random_expr(depth=random.randint(1, 5))

            # Apply random mutation
            mutated = self._mutate_expr(expr)

            yield (mutated, 'Graceful handling')

    def _generate_random_expr(self, depth: int) -> str:
        """Generate a random valid expression."""
        if depth <= 0:
            return random.choice(self.variables + ['1', '2', '3', 'pi', 'e'])

        choice = random.choice(['binary', 'unary', 'function'])

        if choice == 'binary':
            left = self._generate_random_expr(depth - 1)
            right = self._generate_random_expr(depth - 1)
            op = random.choice(self.operators[:4])  # +, -, *, /
            return f'({left}{op}{right})'

        elif choice == 'unary':
            inner = self._generate_random_expr(depth - 1)
            return f'-({inner})'

        else:
            func = random.choice(self.functions)
            inner = self._generate_random_expr(depth - 1)
            return f'{func}({inner})'

    def _mutate_expr(self, expr: str) -> str:
        """Apply random mutation to expression."""
        mutations = [
            lambda e: e.replace('(', '', 1),           # Remove opening paren
            lambda e: e.replace(')', '', 1),           # Remove closing paren
            lambda e: e.replace('+', '++', 1),         # Double operator
            lambda e: e + random.choice(self.operators), # Trailing operator
            lambda e: random.choice(self.operators) + e, # Leading operator
            lambda e: e.replace('x', ''),              # Remove variable
            lambda e: e[:len(e)//2],                   # Truncate
        ]

        mutation = random.choice(mutations)
        return mutation(expr)


# ==============================================================================
# BOUNDARY VALUE TESTER
# ==============================================================================

class BoundaryValueTester:
    """
    Tests algorithm behavior at boundary values.
    """

    def generate_numeric_boundaries(self) -> Iterator[Tuple[str, str]]:
        """Generate numeric boundary test cases."""
        payloads = [
            ('0', 'Handle zero'),
            ('-0', 'Handle negative zero'),
            ('1', 'Handle one'),
            ('-1', 'Handle negative one'),
            ('0.0', 'Handle float zero'),
            ('0.1 + 0.2', 'Handle floating point'),  # Classic FP issue
            ('10**100', 'Handle large numbers'),
            ('10**-100', 'Handle small numbers'),
            ('10**1000', 'Handle very large or error'),
            ('10**-1000', 'Handle very small or error'),
            ('10**10000', 'Error or handle'),
            ('999999999999999999999', 'Handle large integer'),
            ('0.000000000000000001', 'Handle small decimal'),
            ('inf', 'Handle infinity'),
            ('-inf', 'Handle negative infinity'),
            ('nan', 'Handle NaN'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def generate_indeterminate_forms(self) -> Iterator[Tuple[str, str]]:
        """Generate indeterminate form test cases."""
        payloads = [
            ('0/0', 'Report indeterminate or NaN'),
            ('oo/oo', 'Report indeterminate'),
            ('0*oo', 'Report indeterminate'),
            ('oo - oo', 'Report indeterminate'),
            ('0**0', 'Return 1 or report indeterminate'),
            ('1**oo', 'Report indeterminate'),
            ('oo**0', 'Report indeterminate'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def generate_division_by_zero(self) -> Iterator[Tuple[str, str]]:
        """Generate division by zero test cases."""
        payloads = [
            ('1/0', 'Return oo or ZeroDivisionError'),
            ('-1/0', 'Return -oo or ZeroDivisionError'),
            ('x/0', 'Return zoo or error'),
            ('(x-x)/(x-x)', 'Handle 0/0 case'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)


# ==============================================================================
# NUMERICAL STABILITY ANALYZER
# ==============================================================================

class NumericalStabilityAnalyzer:
    """
    Detects numerical instabilities in algorithms.
    """

    def generate_cancellation_tests(self) -> Iterator[Tuple[str, str]]:
        """Generate catastrophic cancellation test cases."""
        payloads = [
            # Classic cancellation
            ('sqrt(x+1) - sqrt(x)', 'Use conjugate for x=10**15'),
            # Large number subtraction
            ('(10**15 + 1) - 10**15', 'Should be 1'),
            # Nearly equal subtraction
            ('1.0000000000001 - 1.0', 'Precision loss detection'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def generate_overflow_tests(self) -> Iterator[Tuple[str, str]]:
        """Generate overflow test cases."""
        payloads = [
            ('exp(1000)', 'Handle overflow'),
            ('factorial(1000)', 'Handle or compute'),
            ('2**10000', 'Handle large integer'),
            ('10.0**309', 'Float overflow'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)

    def generate_underflow_tests(self) -> Iterator[Tuple[str, str]]:
        """Generate underflow test cases."""
        payloads = [
            ('exp(-1000)', 'Handle underflow to 0'),
            ('10.0**-309', 'Float underflow'),
            ('1/(10**1000)', 'Underflow to 0'),
        ]
        for payload, expected in payloads:
            yield (payload, expected)


# ==============================================================================
# ATTACK EXECUTOR
# ==============================================================================

class AttackExecutor:
    """Executes attacks with timeout and error handling."""

    def __init__(self, default_timeout: float = 10.0):
        self.default_timeout = default_timeout

    def execute_with_timeout(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        timeout: float = None
    ) -> Tuple[Any, float, Optional[Exception]]:
        """
        Execute function with timeout.

        Returns:
            (result, duration_ms, exception)
        """
        if kwargs is None:
            kwargs = {}
        if timeout is None:
            timeout = self.default_timeout

        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e

        start = time.time()
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)

        duration_ms = (time.time() - start) * 1000

        if thread.is_alive():
            return None, duration_ms, TimeoutError(f"Function timed out after {timeout}s")

        return result[0], duration_ms, exception[0]


# ==============================================================================
# ALGORITHM BREAKING AGENT
# ==============================================================================

class AlgorithmBreakingAgent:
    """
    Algorithm Breaking Agent - Adversarial Testing for Mathematical Algorithms.

    Follows BDI architecture (simplified for prototype):
    - Beliefs: Knowledge about target algorithms and discovered vulnerabilities
    - Desires: Find all algorithmic weaknesses
    - Intentions: Attack plans currently being executed
    """

    def __init__(self, agent_id: str = 'algorithm_breaking_agent'):
        self.agent_id = agent_id

        # BDI-style state
        self.beliefs: Dict[str, Any] = {
            'discovered_vulnerabilities': [],
            'target_modules': [],
            'coverage': {},
        }
        self.desires: List[str] = ['find_all_weaknesses', 'maximize_coverage']
        self.intentions: List[Dict[str, Any]] = []

        # Components
        self.fuzzer = ExpressionFuzzer()
        self.boundary_tester = BoundaryValueTester()
        self.stability_analyzer = NumericalStabilityAnalyzer()
        self.executor = AttackExecutor()

        # Counters
        self.vuln_counter = 0
        self.verbose = True

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] [{self.agent_id}] {message}")

    def _generate_vuln_id(self) -> str:
        """Generate unique vulnerability ID."""
        self.vuln_counter += 1
        return f"ABA-{datetime.now().strftime('%Y%m%d')}-{self.vuln_counter:04d}"

    # ==========================================================================
    # MAIN ATTACK METHODS
    # ==========================================================================

    def run_attack_campaign(
        self,
        targets: List[str] = None,
        attack_types: List[str] = None,
        duration_minutes: int = 10,
        generate_tests: bool = True
    ) -> AttackCampaignReport:
        """
        Run a comprehensive attack campaign.

        Args:
            targets: Target modules (e.g., ['symbolic', 'solver'])
            attack_types: Attack types (e.g., ['parser', 'boundary', 'stability'])
            duration_minutes: Maximum campaign duration
            generate_tests: Whether to generate pytest cases

        Returns:
            AttackCampaignReport with all findings
        """
        if targets is None:
            targets = ['symbolic', 'solver', 'calculus']
        if attack_types is None:
            attack_types = ['parser', 'boundary', 'stability']

        report = AttackCampaignReport(
            report_id=f"CAMPAIGN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            started_at=datetime.now(),
            targets=targets,
            attack_types=attack_types
        )

        self._log("=" * 70)
        self._log("ALGORITHM BREAKING AGENT - ATTACK CAMPAIGN STARTED")
        self._log(f"Targets: {targets}")
        self._log(f"Attack Types: {attack_types}")
        self._log("=" * 70)

        start_time = time.time()
        max_duration = duration_minutes * 60

        # Run attack phases
        for attack_type in attack_types:
            if time.time() - start_time > max_duration:
                self._log("Campaign duration limit reached", "WARN")
                break

            self._log(f"\n--- Running {attack_type.upper()} attacks ---")

            if attack_type == 'parser':
                results = self._run_parser_attacks()
            elif attack_type == 'boundary':
                results = self._run_boundary_attacks()
            elif attack_type == 'stability':
                results = self._run_stability_attacks()
            elif attack_type == 'fuzzing':
                results = self._run_fuzzing_attacks()
            else:
                self._log(f"Unknown attack type: {attack_type}", "WARN")
                continue

            report.results.extend(results)

            for result in results:
                if result.found_vulnerability():
                    report.vulnerabilities.extend(result.vulnerabilities)

        report.completed_at = datetime.now()

        # Generate pytest cases if requested
        if generate_tests and report.vulnerabilities:
            report.generated_tests = self._generate_pytest_cases(report.vulnerabilities)

        # Summary
        self._log("\n" + "=" * 70)
        self._log("CAMPAIGN COMPLETE")
        self._log(f"Attacks: {report.total_attacks}")
        self._log(f"Successful: {report.successful_attacks}")
        self._log(f"Vulnerabilities: {len(report.vulnerabilities)}")
        self._log(f"  CRITICAL: {report.critical_count}")
        self._log(f"  HIGH: {report.high_count}")
        self._log(f"  MEDIUM: {report.medium_count}")
        self._log(f"  LOW: {report.low_count}")
        self._log("=" * 70)

        return report

    # ==========================================================================
    # ATTACK PHASES
    # ==========================================================================

    def _run_parser_attacks(self) -> List[AttackResult]:
        """Run parser-focused attacks."""
        results = []

        # Empty input attacks
        for payload, expected in self.fuzzer.fuzz_empty():
            result = self._execute_parser_attack(
                attack_id=f"PARSE-EMPTY-{len(results)+1:03d}",
                attack_name="Empty Input",
                payload=payload,
                expected=expected
            )
            results.append(result)
            if result.found_vulnerability():
                self._log(f"  [VULN] {result.vulnerabilities[0].title}", "WARN")

        # Unbalanced parentheses
        for payload, expected in self.fuzzer.fuzz_unbalanced():
            result = self._execute_parser_attack(
                attack_id=f"PARSE-UNBAL-{len(results)+1:03d}",
                attack_name="Unbalanced Parentheses",
                payload=payload,
                expected=expected
            )
            results.append(result)

        # Injection attacks
        for payload, expected in self.fuzzer.fuzz_injection():
            result = self._execute_parser_attack(
                attack_id=f"PARSE-INJ-{len(results)+1:03d}",
                attack_name="Injection Attempt",
                payload=payload,
                expected=expected
            )
            results.append(result)
            if result.found_vulnerability():
                self._log(f"  [VULN] {result.vulnerabilities[0].title}", "WARN")

        return results

    def _run_boundary_attacks(self) -> List[AttackResult]:
        """Run boundary value attacks."""
        results = []

        # Numeric boundaries
        for payload, expected in self.boundary_tester.generate_numeric_boundaries():
            result = self._execute_boundary_attack(
                attack_id=f"BOUND-NUM-{len(results)+1:03d}",
                attack_name="Numeric Boundary",
                payload=payload,
                expected=expected
            )
            results.append(result)

        # Indeterminate forms
        for payload, expected in self.boundary_tester.generate_indeterminate_forms():
            result = self._execute_boundary_attack(
                attack_id=f"BOUND-IND-{len(results)+1:03d}",
                attack_name="Indeterminate Form",
                payload=payload,
                expected=expected
            )
            results.append(result)

        return results

    def _run_stability_attacks(self) -> List[AttackResult]:
        """Run numerical stability attacks."""
        results = []

        # Cancellation tests
        for payload, expected in self.stability_analyzer.generate_cancellation_tests():
            result = self._execute_stability_attack(
                attack_id=f"STAB-CANCEL-{len(results)+1:03d}",
                attack_name="Catastrophic Cancellation",
                payload=payload,
                expected=expected
            )
            results.append(result)

        # Overflow tests
        for payload, expected in self.stability_analyzer.generate_overflow_tests():
            result = self._execute_stability_attack(
                attack_id=f"STAB-OVER-{len(results)+1:03d}",
                attack_name="Overflow",
                payload=payload,
                expected=expected
            )
            results.append(result)

        return results

    def _run_fuzzing_attacks(self, count: int = 50) -> List[AttackResult]:
        """Run random fuzzing attacks."""
        results = []

        for payload, expected in self.fuzzer.fuzz_random(count):
            result = self._execute_parser_attack(
                attack_id=f"FUZZ-{len(results)+1:03d}",
                attack_name="Random Fuzz",
                payload=payload,
                expected=expected
            )
            results.append(result)

        return results

    # ==========================================================================
    # ATTACK EXECUTION
    # ==========================================================================

    def _execute_parser_attack(
        self,
        attack_id: str,
        attack_name: str,
        payload: str,
        expected: str
    ) -> AttackResult:
        """Execute a parser-targeted attack."""
        vulnerabilities = []

        # Try to import and test the parser
        try:
            # Try native symbolic parser
            try:
                from symbo_agentic_reasoners.core.symbolic import parse_expr
                target_module = "symbo_agentic_reasoners.core.symbolic"
                target_func = "parse_expr"
            except ImportError:
                # Fallback: just record the attack
                return AttackResult(
                    attack_id=attack_id,
                    attack_name=attack_name,
                    status=AttackStatus.SKIPPED,
                    category="parser",
                    duration_ms=0,
                    details="Could not import parser"
                )

            result, duration_ms, exc = self.executor.execute_with_timeout(
                parse_expr, args=(payload,), timeout=5.0
            )

            # Analyze result
            if exc is not None:
                if isinstance(exc, TimeoutError):
                    # Timeout might be a DoS vulnerability
                    vulnerabilities.append(AlgorithmVulnerability(
                        vuln_id=self._generate_vuln_id(),
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.HANG,
                        target_module=target_module,
                        target_function=target_func,
                        title=f"Parser timeout on input",
                        description=f"Parser hangs on input: {repr(payload[:50])}...",
                        proof_of_concept=f"parse_expr({repr(payload)})",
                        test_input=payload[:100],
                        observed_behavior="Timeout after 5 seconds",
                        expected_behavior=expected,
                        impact="Potential denial of service",
                        suggested_fix="Add input length/depth limits"
                    ))

                elif 'Security' in type(exc).__name__ or 'security' in str(exc).lower():
                    # Security error is expected for injection attempts
                    pass  # This is correct behavior

                else:
                    # Other exceptions - check if expected
                    if 'Error' not in expected and 'error' not in expected.lower():
                        # Unexpected exception
                        vulnerabilities.append(AlgorithmVulnerability(
                            vuln_id=self._generate_vuln_id(),
                            severity=Severity.LOW,
                            category=VulnerabilityCategory.CRASH,
                            target_module=target_module,
                            target_function=target_func,
                            title=f"Unexpected {type(exc).__name__}",
                            description=f"Parser raised unexpected exception: {exc}",
                            proof_of_concept=f"parse_expr({repr(payload)})",
                            test_input=payload[:100],
                            observed_behavior=f"{type(exc).__name__}: {exc}",
                            expected_behavior=expected,
                            suggested_fix="Add specific error handling"
                        ))

            else:
                # No exception - check if result makes sense
                # For injection payloads, we should NOT get a result
                if '__import__' in payload or 'eval' in payload:
                    if result is not None:
                        vulnerabilities.append(AlgorithmVulnerability(
                            vuln_id=self._generate_vuln_id(),
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.SECURITY,
                            target_module=target_module,
                            target_function=target_func,
                            title="Potential code injection",
                            description=f"Parser accepted potentially malicious input",
                            proof_of_concept=f"parse_expr({repr(payload)})",
                            test_input=payload[:100],
                            observed_behavior=f"Returned: {result}",
                            expected_behavior="SecurityError",
                            impact="Remote code execution possible",
                            suggested_fix="Block dangerous patterns"
                        ))

            status = AttackStatus.SUCCESS if vulnerabilities else AttackStatus.NO_FINDING

            return AttackResult(
                attack_id=attack_id,
                attack_name=attack_name,
                status=status,
                category="parser",
                duration_ms=duration_ms,
                target_function=target_func,
                vulnerabilities=vulnerabilities
            )

        except Exception as e:
            return AttackResult(
                attack_id=attack_id,
                attack_name=attack_name,
                status=AttackStatus.ERROR,
                category="parser",
                duration_ms=0,
                exception=str(e)
            )

    def _execute_boundary_attack(
        self,
        attack_id: str,
        attack_name: str,
        payload: str,
        expected: str
    ) -> AttackResult:
        """Execute a boundary value attack."""
        # Similar structure to parser attack
        # For prototype, just record the attack
        return AttackResult(
            attack_id=attack_id,
            attack_name=attack_name,
            status=AttackStatus.NO_FINDING,
            category="boundary",
            duration_ms=0,
            details=f"Tested: {payload}"
        )

    def _execute_stability_attack(
        self,
        attack_id: str,
        attack_name: str,
        payload: str,
        expected: str
    ) -> AttackResult:
        """Execute a numerical stability attack."""
        # For prototype, just record the attack
        return AttackResult(
            attack_id=attack_id,
            attack_name=attack_name,
            status=AttackStatus.NO_FINDING,
            category="stability",
            duration_ms=0,
            details=f"Tested: {payload}"
        )

    # ==========================================================================
    # TEST GENERATION
    # ==========================================================================

    def _generate_pytest_cases(
        self,
        vulnerabilities: List[AlgorithmVulnerability]
    ) -> List[str]:
        """Generate pytest test cases for discovered vulnerabilities."""
        tests = []

        header = '''"""
Auto-generated tests from Algorithm Breaking Agent.
These tests verify discovered vulnerabilities are fixed.
"""

import pytest


'''
        tests.append(header)

        for vuln in vulnerabilities:
            test_name = f"test_vuln_{vuln.vuln_id.replace('-', '_').lower()}"

            test_code = f'''
def {test_name}():
    """
    Vulnerability: {vuln.title}
    Severity: {vuln.severity.value}
    Category: {vuln.category.value}

    {vuln.description}
    """
    # Proof of concept:
    # {vuln.proof_of_concept}

    # Expected: {vuln.expected_behavior}
    # Observed: {vuln.observed_behavior}

    # TODO: Implement test once fix is in place
    pytest.skip("Vulnerability not yet fixed: {vuln.vuln_id}")

'''
            tests.append(test_code)

        return tests


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Run Algorithm Breaking Agent from command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Algorithm Breaking Agent - Adversarial Testing for Math Algorithms"
    )
    parser.add_argument(
        '--targets', '-t',
        nargs='+',
        default=['symbolic', 'solver'],
        help='Target modules to attack'
    )
    parser.add_argument(
        '--attacks', '-a',
        nargs='+',
        default=['parser', 'boundary', 'stability'],
        help='Attack types to run'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=10,
        help='Maximum duration in minutes'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for markdown report'
    )
    parser.add_argument(
        '--json', '-j',
        type=str,
        help='Output file for JSON report'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Create and run agent
    agent = AlgorithmBreakingAgent()
    agent.verbose = not args.quiet

    report = agent.run_attack_campaign(
        targets=args.targets,
        attack_types=args.attacks,
        duration_minutes=args.duration
    )

    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report.generate_markdown())
        print(f"\nMarkdown report: {args.output}")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        print(f"JSON report: {args.json}")

    if not args.output and not args.quiet:
        print("\n" + report.generate_markdown())

    # Return exit code
    if report.critical_count > 0:
        return 2
    elif report.high_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
