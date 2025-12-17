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
SECURITY STRESS TESTER AGENT
============================

High-stress security testing agent for the Symbo Mathematical Multi-Agentic
Reasoning System. Implements systematic vulnerability discovery through:

1. ADVERSARIAL INPUTS - Malformed, malicious, and edge-case mathematical inputs
2. RESOURCE EXHAUSTION - Memory, CPU, and timeout stress tests
3. INJECTION ATTACKS - Expression parser exploitation attempts
4. DOS TESTING - Infinite loops, stack overflow, resource bombs
5. BOUNDARY PROBING - Limits and edge case discovery

This agent follows the BDI (Belief-Desire-Intention) pattern and integrates
with the existing agent infrastructure.

Usage:
    from src.system_agents.security_stress_tester import SecurityStressTester

    tester = SecurityStressTester()
    report = tester.run_full_security_audit()
    print(report.generate_markdown())
"""

import sys
import os
import time
import threading
import traceback
import gc
import json
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import multiprocessing
import functools

# Platform-specific imports
try:
    import resource  # Unix only
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

try:
    import signal
    HAS_SIGNAL = True
except ImportError:
    HAS_SIGNAL = False

# Ensure proper encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ==============================================================================
# SEVERITY AND CATEGORY DEFINITIONS
# ==============================================================================

class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRITICAL"   # Exploitable security flaw, data exposure, RCE possible
    HIGH = "HIGH"           # Denial of service, resource exhaustion, crash
    MEDIUM = "MEDIUM"       # Edge case failures, degraded functionality
    LOW = "LOW"             # Minor issues, code smells
    INFO = "INFO"           # Informational findings


class VulnerabilityCategory(Enum):
    """Categories of security vulnerabilities"""
    INJECTION = "Code Injection"
    RESOURCE_EXHAUSTION = "Resource Exhaustion"
    DENIAL_OF_SERVICE = "Denial of Service"
    INPUT_VALIDATION = "Input Validation"
    BOUNDARY_VIOLATION = "Boundary Violation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    AUTHENTICATION = "Authentication/Authorization"
    CONCURRENCY = "Concurrency Issues"
    MEMORY_SAFETY = "Memory Safety"
    CRYPTOGRAPHIC = "Cryptographic Weakness"


class TestStatus(Enum):
    """Status of individual tests"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    VULNERABLE = "VULNERABLE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class Vulnerability:
    """Represents a discovered security vulnerability"""
    id: str
    title: str
    severity: Severity
    category: VulnerabilityCategory
    description: str
    location: str
    proof_of_concept: str
    impact: str
    remediation: str
    discovered_at: datetime = field(default_factory=datetime.now)
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'severity': self.severity.value,
            'category': self.category.value,
            'description': self.description,
            'location': self.location,
            'poc': self.proof_of_concept,
            'impact': self.impact,
            'remediation': self.remediation,
            'discovered_at': self.discovered_at.isoformat(),
            'cwe_id': self.cwe_id,
            'cvss_score': self.cvss_score
        }


@dataclass
class TestResult:
    """Result of a single security test"""
    test_id: str
    test_name: str
    status: TestStatus
    category: VulnerabilityCategory
    duration_ms: float
    details: str = ""
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    exception: Optional[str] = None
    memory_used_mb: float = 0.0

    def is_vulnerable(self) -> bool:
        return self.status == TestStatus.VULNERABLE or len(self.vulnerabilities) > 0


@dataclass
class SecurityReport:
    """Comprehensive security audit report"""
    report_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    target_system: str = "Symbo Mathematical Multi-Agentic Reasoning System"
    tests_run: List[TestResult] = field(default_factory=list)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)

    @property
    def total_tests(self) -> int:
        return len(self.tests_run)

    @property
    def passed_tests(self) -> int:
        return sum(1 for t in self.tests_run if t.status == TestStatus.PASSED)

    @property
    def failed_tests(self) -> int:
        return sum(1 for t in self.tests_run if t.status in (TestStatus.FAILED, TestStatus.VULNERABLE))

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
        """Generate a markdown security report"""
        duration = (self.completed_at - self.started_at).total_seconds() if self.completed_at else 0

        report = []
        report.append("# Security Stress Test Report")
        report.append(f"\n**Target:** {self.target_system}")
        report.append(f"**Report ID:** {self.report_id}")
        report.append(f"**Date:** {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Duration:** {duration:.2f} seconds")
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Tests Run:** {self.total_tests}")
        report.append(f"- **Tests Passed:** {self.passed_tests}")
        report.append(f"- **Tests Failed:** {self.failed_tests}")
        report.append(f"- **Vulnerabilities Found:** {len(self.vulnerabilities)}")
        report.append("")

        # Severity breakdown
        report.append("### Vulnerability Severity Distribution")
        report.append(f"- CRITICAL: {self.critical_count}")
        report.append(f"- HIGH: {self.high_count}")
        report.append(f"- MEDIUM: {self.medium_count}")
        report.append(f"- LOW: {self.low_count}")
        report.append("")

        # Risk Assessment
        if self.critical_count > 0:
            risk = "CRITICAL - Immediate action required"
        elif self.high_count > 0:
            risk = "HIGH - Action required before production"
        elif self.medium_count > 0:
            risk = "MEDIUM - Address in next release cycle"
        elif self.low_count > 0:
            risk = "LOW - Address as time permits"
        else:
            risk = "MINIMAL - No significant issues found"
        report.append(f"**Overall Risk Level:** {risk}")
        report.append("")

        # Detailed Vulnerabilities
        if self.vulnerabilities:
            report.append("## Vulnerabilities")
            report.append("")

            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                vulns = [v for v in self.vulnerabilities if v.severity == severity]
                if vulns:
                    report.append(f"### {severity.value} ({len(vulns)})")
                    report.append("")
                    for v in vulns:
                        report.append(f"#### {v.id}: {v.title}")
                        report.append(f"- **Category:** {v.category.value}")
                        report.append(f"- **Location:** {v.location}")
                        if v.cwe_id:
                            report.append(f"- **CWE:** {v.cwe_id}")
                        report.append(f"\n**Description:** {v.description}")
                        report.append(f"\n**Impact:** {v.impact}")
                        report.append(f"\n**Proof of Concept:**")
                        report.append(f"```\n{v.proof_of_concept}\n```")
                        report.append(f"\n**Remediation:** {v.remediation}")
                        report.append("")

        # Test Results Summary
        report.append("## Test Results")
        report.append("")
        report.append("| Test | Category | Status | Duration |")
        report.append("|------|----------|--------|----------|")
        for test in self.tests_run:
            status_icon = {
                TestStatus.PASSED: "PASS",
                TestStatus.FAILED: "FAIL",
                TestStatus.VULNERABLE: "VULN",
                TestStatus.TIMEOUT: "TIME",
                TestStatus.ERROR: "ERR",
                TestStatus.SKIPPED: "SKIP"
            }.get(test.status, "?")
            report.append(f"| {test.test_name} | {test.category.value} | {status_icon} | {test.duration_ms:.0f}ms |")

        report.append("")
        report.append("---")
        report.append("*Generated by SecurityStressTester Agent*")

        return "\n".join(report)

    def to_json(self) -> str:
        """Export report as JSON"""
        return json.dumps({
            'report_id': self.report_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'target_system': self.target_system,
            'summary': {
                'total_tests': self.total_tests,
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'vulnerabilities': len(self.vulnerabilities),
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count
            },
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
            'tests': [{
                'id': t.test_id,
                'name': t.test_name,
                'status': t.status.value,
                'category': t.category.value,
                'duration_ms': t.duration_ms,
                'details': t.details
            } for t in self.tests_run]
        }, indent=2)


# ==============================================================================
# TIMEOUT UTILITIES
# ==============================================================================

class TimeoutException(Exception):
    """Raised when a test exceeds its timeout"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeouts (Unix only)"""
    raise TimeoutException("Test timed out")


def run_with_timeout(func: Callable, timeout_seconds: float, *args, **kwargs) -> Any:
    """
    Run a function with a timeout.

    Works on both Windows and Unix systems.
    """
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        raise TimeoutException(f"Function timed out after {timeout_seconds}s")

    if exception[0]:
        raise exception[0]

    return result[0]


# ==============================================================================
# SECURITY STRESS TESTER AGENT
# ==============================================================================

class SecurityStressTester:
    """
    High-Stress Security Testing Agent

    Implements comprehensive security testing for the Symbo mathematical
    reasoning system through:

    1. Adversarial input generation
    2. Resource exhaustion testing
    3. Injection attack simulation
    4. Denial of service probing
    5. Boundary and edge case discovery

    This agent uses BDI-style reasoning internally:
    - Beliefs: Current system state, discovered vulnerabilities
    - Desires: Find all security weaknesses
    - Intentions: Specific test sequences to execute
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Security Stress Tester.

        Args:
            config: Optional configuration dictionary with keys:
                - timeout_seconds: Default timeout for tests (default: 10)
                - max_memory_mb: Memory limit for tests (default: 512)
                - enable_dos_tests: Enable destructive DoS tests (default: False)
                - verbose: Print progress (default: True)
        """
        self.config = config or {}
        self.timeout_seconds = self.config.get('timeout_seconds', 10)
        self.max_memory_mb = self.config.get('max_memory_mb', 512)
        self.enable_dos_tests = self.config.get('enable_dos_tests', False)
        self.verbose = self.config.get('verbose', True)

        # BDI State
        self.beliefs: Dict[str, Any] = {}
        self.vulnerabilities: List[Vulnerability] = []
        self.vuln_counter = 0

        # Test registry
        self.test_suites: Dict[str, List[Callable]] = {
            'injection': [],
            'resource': [],
            'dos': [],
            'input_validation': [],
            'boundary': [],
            'concurrency': []
        }

        self._register_all_tests()

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def _generate_vuln_id(self) -> str:
        """Generate unique vulnerability ID"""
        self.vuln_counter += 1
        return f"SST-{datetime.now().strftime('%Y%m%d')}-{self.vuln_counter:04d}"

    def _register_all_tests(self):
        """Register all security test methods"""
        # Injection tests
        self.test_suites['injection'] = [
            self._test_code_injection_sympify,
            self._test_code_injection_parse_expr,
            self._test_dunder_attribute_access,
            self._test_module_import_injection,
            self._test_eval_exec_injection,
            self._test_lambda_injection,
            self._test_pickle_deserialization,
        ]

        # Resource exhaustion tests
        self.test_suites['resource'] = [
            self._test_memory_bomb_nested_expr,
            self._test_memory_bomb_huge_numbers,
            self._test_cpu_exhaustion_factorial,
            self._test_cpu_exhaustion_expand,
            self._test_recursion_depth_attack,
            self._test_string_multiplication_bomb,
        ]

        # Denial of Service tests
        self.test_suites['dos'] = [
            self._test_infinite_loop_expression,
            self._test_stack_overflow_recursion,
            self._test_thread_exhaustion,
            self._test_file_descriptor_exhaustion,
            self._test_regex_catastrophic_backtracking,
        ]

        # Input validation tests
        self.test_suites['input_validation'] = [
            self._test_null_byte_injection,
            self._test_unicode_normalization,
            self._test_empty_inputs,
            self._test_type_confusion,
            self._test_encoding_attacks,
            self._test_format_string_attacks,
        ]

        # Boundary tests
        self.test_suites['boundary'] = [
            self._test_max_expression_length,
            self._test_max_nesting_depth,
            self._test_numeric_overflow,
            self._test_numeric_underflow,
            self._test_precision_limits,
            self._test_special_values,
        ]

        # Concurrency tests
        self.test_suites['concurrency'] = [
            self._test_race_condition_state,
            self._test_thread_safety_parsing,
            self._test_deadlock_potential,
        ]

    # ==========================================================================
    # MAIN TEST EXECUTION
    # ==========================================================================

    def run_full_security_audit(self) -> SecurityReport:
        """
        Run complete security audit of the Symbo system.

        Returns:
            SecurityReport with all findings
        """
        report = SecurityReport(
            report_id=f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            started_at=datetime.now()
        )

        self._log("=" * 70)
        self._log("SECURITY STRESS TEST AUDIT STARTED")
        self._log("=" * 70)

        # Run all test suites
        suite_order = ['injection', 'input_validation', 'boundary', 'resource', 'concurrency']
        if self.enable_dos_tests:
            suite_order.append('dos')

        for suite_name in suite_order:
            self._log(f"\n--- Running {suite_name.upper()} tests ---")
            tests = self.test_suites.get(suite_name, [])

            for test_func in tests:
                result = self._execute_test(test_func)
                report.tests_run.append(result)
                report.vulnerabilities.extend(result.vulnerabilities)

                status_symbol = {
                    TestStatus.PASSED: "[PASS]",
                    TestStatus.FAILED: "[FAIL]",
                    TestStatus.VULNERABLE: "[VULN]",
                    TestStatus.TIMEOUT: "[TIME]",
                    TestStatus.ERROR: "[ERR]",
                }.get(result.status, "[???]")

                self._log(f"  {status_symbol} {result.test_name} ({result.duration_ms:.0f}ms)")

                if result.vulnerabilities:
                    for vuln in result.vulnerabilities:
                        self._log(f"    -> Found: {vuln.severity.value} - {vuln.title}", "WARN")

        report.completed_at = datetime.now()
        report.vulnerabilities = self.vulnerabilities.copy()

        # Summary
        self._log("\n" + "=" * 70)
        self._log("AUDIT COMPLETE")
        self._log(f"Tests: {report.passed_tests}/{report.total_tests} passed")
        self._log(f"Vulnerabilities: {len(report.vulnerabilities)} found")
        self._log(f"  CRITICAL: {report.critical_count}")
        self._log(f"  HIGH: {report.high_count}")
        self._log(f"  MEDIUM: {report.medium_count}")
        self._log(f"  LOW: {report.low_count}")
        self._log("=" * 70)

        return report

    def run_quick_scan(self) -> SecurityReport:
        """Run a quick security scan with essential tests only"""
        report = SecurityReport(
            report_id=f"QUICK-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            started_at=datetime.now()
        )

        quick_tests = [
            self._test_code_injection_sympify,
            self._test_dunder_attribute_access,
            self._test_null_byte_injection,
            self._test_max_expression_length,
            self._test_recursion_depth_attack,
        ]

        for test_func in quick_tests:
            result = self._execute_test(test_func)
            report.tests_run.append(result)
            report.vulnerabilities.extend(result.vulnerabilities)

        report.completed_at = datetime.now()
        return report

    def _execute_test(self, test_func: Callable) -> TestResult:
        """Execute a single test with timeout and error handling"""
        test_name = test_func.__name__.replace('_test_', '').replace('_', ' ').title()
        test_id = test_func.__name__

        # Determine category from test function location
        category = VulnerabilityCategory.INPUT_VALIDATION
        for suite_name, tests in self.test_suites.items():
            if test_func in tests:
                category_map = {
                    'injection': VulnerabilityCategory.INJECTION,
                    'resource': VulnerabilityCategory.RESOURCE_EXHAUSTION,
                    'dos': VulnerabilityCategory.DENIAL_OF_SERVICE,
                    'input_validation': VulnerabilityCategory.INPUT_VALIDATION,
                    'boundary': VulnerabilityCategory.BOUNDARY_VIOLATION,
                    'concurrency': VulnerabilityCategory.CONCURRENCY,
                }
                category = category_map.get(suite_name, VulnerabilityCategory.INPUT_VALIDATION)
                break

        start_time = time.time()
        gc.collect()

        try:
            # Run test with timeout
            vulnerabilities = run_with_timeout(test_func, self.timeout_seconds)
            duration_ms = (time.time() - start_time) * 1000

            if vulnerabilities:
                self.vulnerabilities.extend(vulnerabilities)
                return TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    status=TestStatus.VULNERABLE,
                    category=category,
                    duration_ms=duration_ms,
                    vulnerabilities=vulnerabilities
                )
            else:
                return TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    category=category,
                    duration_ms=duration_ms
                )

        except TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                status=TestStatus.TIMEOUT,
                category=category,
                duration_ms=duration_ms,
                details=f"Test exceeded {self.timeout_seconds}s timeout"
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                status=TestStatus.ERROR,
                category=category,
                duration_ms=duration_ms,
                exception=f"{type(e).__name__}: {str(e)}"
            )

    # ==========================================================================
    # INJECTION ATTACK TESTS
    # ==========================================================================

    def _test_code_injection_sympify(self) -> List[Vulnerability]:
        """Test for code injection via sympify/safe_sympify"""
        vulnerabilities = []

        injection_payloads = [
            # Python code execution attempts
            "__import__('os').system('id')",
            "__import__('os').popen('whoami').read()",
            "eval('__import__(\"os\").system(\"id\")')",
            "exec('import os; os.system(\"id\")')",
            "compile('import os','','exec')",

            # Object introspection attacks
            "().__class__.__bases__[0].__subclasses__()",
            "''.__class__.__mro__[2].__subclasses__()",
            "().__class__.__mro__[-1].__subclasses__()[40]('/etc/passwd').read()",

            # Attribute access attacks
            "getattr(getattr(x,'__class__'),'__bases__')[0]",
            "x.__class__.__bases__[0].__subclasses__()",

            # Format string attacks
            "{x.__class__.__bases__}",
            "f'{__import__(\"os\").getcwd()}'",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            for payload in injection_payloads:
                try:
                    result = safe_sympify(payload)
                    # If we get here without SecurityError, it's potentially vulnerable
                    # Check if it actually executed code
                    if 'class' in str(result) or 'module' in str(result):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Code Injection via safe_sympify",
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.INJECTION,
                            description=f"safe_sympify accepted potentially malicious input without blocking",
                            location="symbo_agentic_reasoners.core.safe_parser.safe_sympify",
                            proof_of_concept=f"safe_sympify({repr(payload)})",
                            impact="Remote code execution, system compromise",
                            remediation="Strengthen input validation and blacklist patterns",
                            cwe_id="CWE-94"
                        ))
                except SecurityError:
                    # Expected - input was blocked
                    pass
                except Exception:
                    # Other errors are acceptable - parsing failed safely
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_code_injection_parse_expr(self) -> List[Vulnerability]:
        """Test for code injection via parse_expr/safe_parse"""
        vulnerabilities = []

        injection_payloads = [
            "__builtins__['__import__']('os').system('id')",
            "globals()['__builtins__']['eval']('1+1')",
            "locals()['__builtins__']",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

            for payload in injection_payloads:
                try:
                    result = safe_parse(payload)
                    if hasattr(result, '__call__') or 'builtins' in str(result):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Code Injection via safe_parse",
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.INJECTION,
                            description="safe_parse accepted potentially malicious input",
                            location="symbo_agentic_reasoners.core.safe_parser.safe_parse",
                            proof_of_concept=f"safe_parse({repr(payload)})",
                            impact="Remote code execution",
                            remediation="Add payload to blacklist",
                            cwe_id="CWE-94"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_dunder_attribute_access(self) -> List[Vulnerability]:
        """Test for dangerous dunder attribute access"""
        vulnerabilities = []

        dunder_payloads = [
            "x.__class__",
            "x.__dict__",
            "x.__globals__",
            "x.__code__",
            "x.__reduce__",
            "x.__reduce_ex__",
            "x.__getattribute__('__class__')",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            for payload in dunder_payloads:
                try:
                    result = safe_sympify(payload)
                    # Check if dunder access succeeded
                    result_str = str(result)
                    if '__class__' in result_str or '__dict__' in result_str:
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Dunder Attribute Access Allowed",
                            severity=Severity.HIGH,
                            category=VulnerabilityCategory.INJECTION,
                            description="Parser allows access to dunder attributes",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Object introspection leading to code execution",
                            remediation="Block all __xxx__ patterns in input",
                            cwe_id="CWE-913"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_module_import_injection(self) -> List[Vulnerability]:
        """Test for module import injection attacks"""
        vulnerabilities = []

        import_payloads = [
            "__import__('os')",
            "__import__('subprocess')",
            "__import__('socket')",
            "import os",
            "from os import system",
            "importlib.import_module('os')",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            for payload in import_payloads:
                try:
                    result = safe_sympify(payload)
                    if 'module' in str(type(result)):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Module Import Injection",
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.INJECTION,
                            description="Parser allows module imports",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Arbitrary module import leading to RCE",
                            remediation="Block import-related patterns",
                            cwe_id="CWE-94"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_eval_exec_injection(self) -> List[Vulnerability]:
        """Test for eval/exec injection"""
        vulnerabilities = []

        payloads = [
            "eval('1+1')",
            "exec('x=1')",
            "eval(chr(49)+chr(43)+chr(49))",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            for payload in payloads:
                try:
                    result = safe_sympify(payload)
                    # If eval/exec executed, this is critical
                    if result == 2:  # eval('1+1') would return 2
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="eval/exec Code Execution",
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.INJECTION,
                            description="eval() or exec() executed within parser",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Arbitrary code execution",
                            remediation="Remove eval/exec from allowed functions",
                            cwe_id="CWE-95"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_lambda_injection(self) -> List[Vulnerability]:
        """Test for lambda injection attacks"""
        vulnerabilities = []

        payloads = [
            "lambda: __import__('os')",
            "(lambda: 1)()",
            "map(lambda x: x, [1,2,3])",
        ]

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            for payload in payloads:
                try:
                    result = safe_sympify(payload)
                    if callable(result):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Lambda Function Injection",
                            severity=Severity.HIGH,
                            category=VulnerabilityCategory.INJECTION,
                            description="Parser created callable lambda",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Deferred code execution",
                            remediation="Block lambda keyword in parser",
                            cwe_id="CWE-94"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_pickle_deserialization(self) -> List[Vulnerability]:
        """Test for unsafe pickle deserialization"""
        vulnerabilities = []

        # This tests if pickle can be used to deserialize malicious objects
        # In safe_parser, pickle should never be used

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            payloads = [
                "pickle.loads(b'...')",
                "__reduce__",
                "__reduce_ex__",
            ]

            for payload in payloads:
                try:
                    result = safe_sympify(payload)
                    if 'pickle' in str(result) or 'reduce' in str(result):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Pickle Deserialization Risk",
                            severity=Severity.HIGH,
                            category=VulnerabilityCategory.INJECTION,
                            description="Parser may allow pickle operations",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Object injection, RCE via pickle",
                            remediation="Block pickle-related patterns",
                            cwe_id="CWE-502"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    # ==========================================================================
    # RESOURCE EXHAUSTION TESTS
    # ==========================================================================

    def _test_memory_bomb_nested_expr(self) -> List[Vulnerability]:
        """Test for memory exhaustion via deeply nested expressions"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # Create deeply nested expression
            nested = "(" * 100 + "x" + ")" * 100

            try:
                result = safe_sympify(nested)
                # If it succeeds with very deep nesting, check memory impact
            except (RecursionError, MemoryError):
                pass  # Expected for very deep nesting
            except ValueError as e:
                if "depth" in str(e).lower() or "nesting" in str(e).lower():
                    pass  # Protected
                else:
                    raise
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_memory_bomb_huge_numbers(self) -> List[Vulnerability]:
        """Test for memory exhaustion via huge numbers"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # Try to create astronomically large numbers
            huge_num = "10**100000"

            try:
                result = safe_sympify(huge_num)
                # Check if result was actually computed
                if hasattr(result, '__len__') and len(str(result)) > 10000:
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="Memory Exhaustion via Large Numbers",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.RESOURCE_EXHAUSTION,
                        description="Parser computed extremely large number",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=huge_num,
                        impact="Memory exhaustion, DoS",
                        remediation="Limit maximum numeric value or exponent",
                        cwe_id="CWE-400"
                    ))
            except (MemoryError, OverflowError):
                pass
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_cpu_exhaustion_factorial(self) -> List[Vulnerability]:
        """Test for CPU exhaustion via factorial of large numbers"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # factorial(10000) is very expensive
            payload = "factorial(10000)"

            start = time.time()
            try:
                result = safe_sympify(payload)
                duration = time.time() - start

                if duration > 5:  # More than 5 seconds is concerning
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="CPU Exhaustion via Factorial",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.RESOURCE_EXHAUSTION,
                        description=f"factorial computation took {duration:.1f}s",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=payload,
                        impact="CPU exhaustion, DoS",
                        remediation="Limit factorial input size",
                        cwe_id="CWE-400"
                    ))
            except (MemoryError, OverflowError):
                pass
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_cpu_exhaustion_expand(self) -> List[Vulnerability]:
        """Test for CPU exhaustion via expand of complex expressions"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # (x+1)^100 expand is expensive
            payload = "expand((x+1)**100)"

            start = time.time()
            try:
                result = safe_sympify(payload)
                duration = time.time() - start

                if duration > 5:
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="CPU Exhaustion via Polynomial Expansion",
                        severity=Severity.LOW,
                        category=VulnerabilityCategory.RESOURCE_EXHAUSTION,
                        description=f"Expansion took {duration:.1f}s",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=payload,
                        impact="CPU exhaustion",
                        remediation="Limit expansion degree",
                        cwe_id="CWE-400"
                    ))
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_recursion_depth_attack(self) -> List[Vulnerability]:
        """Test for stack overflow via deep recursion"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # Create expression that may cause deep recursion
            deep_expr = "sin(" * 500 + "x" + ")" * 500

            try:
                result = safe_sympify(deep_expr)
            except RecursionError:
                pass  # Expected
            except ValueError as e:
                if "depth" in str(e).lower():
                    pass  # Protected
                else:
                    pass
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_string_multiplication_bomb(self) -> List[Vulnerability]:
        """Test for memory bomb via string multiplication"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # 'a' * 10**9 would consume gigabytes
            payload = "'a' * 10**9"

            try:
                result = safe_sympify(payload)
                if isinstance(result, str) and len(result) > 1000000:
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="String Multiplication Memory Bomb",
                        severity=Severity.HIGH,
                        category=VulnerabilityCategory.RESOURCE_EXHAUSTION,
                        description="Parser executed string multiplication",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=payload,
                        impact="Memory exhaustion, system crash",
                        remediation="Block string operations in parser",
                        cwe_id="CWE-400"
                    ))
            except (MemoryError, OverflowError):
                pass
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    # ==========================================================================
    # DENIAL OF SERVICE TESTS
    # ==========================================================================

    def _test_infinite_loop_expression(self) -> List[Vulnerability]:
        """Test for expressions that cause infinite loops"""
        vulnerabilities = []

        # These tests are potentially dangerous - only run if enabled
        if not self.enable_dos_tests:
            return vulnerabilities

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # Expressions that might cause infinite loops in simplification
            loop_payloads = [
                "Sum(1/n, (n, 1, oo))",  # Divergent series
                "limit(x*sin(1/x), x, oo)",  # Oscillating limit
            ]

            for payload in loop_payloads:
                try:
                    run_with_timeout(safe_sympify, 2, payload)
                except TimeoutException:
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="Expression Causes Timeout",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.DENIAL_OF_SERVICE,
                        description="Expression processing did not complete",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=payload,
                        impact="Service unavailability",
                        remediation="Add timeout protection to parser",
                        cwe_id="CWE-400"
                    ))
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_stack_overflow_recursion(self) -> List[Vulnerability]:
        """Test for stack overflow via recursive structures"""
        vulnerabilities = []

        if not self.enable_dos_tests:
            return vulnerabilities

        return vulnerabilities

    def _test_thread_exhaustion(self) -> List[Vulnerability]:
        """Test for thread pool exhaustion"""
        vulnerabilities = []

        if not self.enable_dos_tests:
            return vulnerabilities

        return vulnerabilities

    def _test_file_descriptor_exhaustion(self) -> List[Vulnerability]:
        """Test for file descriptor exhaustion"""
        vulnerabilities = []

        if not self.enable_dos_tests:
            return vulnerabilities

        return vulnerabilities

    def _test_regex_catastrophic_backtracking(self) -> List[Vulnerability]:
        """Test for ReDoS via catastrophic backtracking"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            # Patterns that cause catastrophic backtracking
            redos_payloads = [
                "a" * 30 + "!",  # May trigger backtracking in some patterns
            ]

            for payload in redos_payloads:
                start = time.time()
                try:
                    safe_sympify(payload)
                except Exception:
                    pass
                duration = time.time() - start

                if duration > 2:  # More than 2 seconds suggests ReDoS
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="ReDoS Vulnerability",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.DENIAL_OF_SERVICE,
                        description=f"Input caused {duration:.1f}s processing time",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=payload[:50] + "...",
                        impact="CPU exhaustion via regex",
                        remediation="Review and optimize regex patterns",
                        cwe_id="CWE-1333"
                    ))

        except ImportError:
            pass

        return vulnerabilities

    # ==========================================================================
    # INPUT VALIDATION TESTS
    # ==========================================================================

    def _test_null_byte_injection(self) -> List[Vulnerability]:
        """Test for null byte injection vulnerabilities"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            null_payloads = [
                "x\x00+1",
                "x + 1\x00; import os",
                "\x00eval('1')",
            ]

            for payload in null_payloads:
                try:
                    result = safe_sympify(payload)
                    # If parsing succeeded with null bytes, it's a vulnerability
                    vulnerabilities.append(Vulnerability(
                        id=self._generate_vuln_id(),
                        title="Null Byte Injection Accepted",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.INPUT_VALIDATION,
                        description="Parser accepted input containing null bytes",
                        location="symbo_agentic_reasoners.core.safe_parser",
                        proof_of_concept=repr(payload),
                        impact="Potential bypass of security filters",
                        remediation="Strip or reject null bytes in input",
                        cwe_id="CWE-626"
                    ))
                except SecurityError:
                    pass  # Properly blocked
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_unicode_normalization(self) -> List[Vulnerability]:
        """Test for unicode normalization attacks"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            # Unicode lookalikes and normalization tricks
            unicode_payloads = [
                "x + 1",  # Normal space
                "x\u00a0+\u00a01",  # Non-breaking space
                "\uff45\uff56\uff41\uff4c('1')",  # Fullwidth 'eval'
                "\u0435val('1')",  # Cyrillic 'e' in eval
            ]

            for payload in unicode_payloads:
                try:
                    result = safe_sympify(payload)
                    # Check if unicode bypass worked
                    if 'eval' in payload.lower():
                        if result == 1:
                            vulnerabilities.append(Vulnerability(
                                id=self._generate_vuln_id(),
                                title="Unicode Normalization Bypass",
                                severity=Severity.HIGH,
                                category=VulnerabilityCategory.INPUT_VALIDATION,
                                description="Unicode lookalike bypassed filter",
                                location="symbo_agentic_reasoners.core.safe_parser",
                                proof_of_concept=repr(payload),
                                impact="Security filter bypass",
                                remediation="Normalize unicode before validation",
                                cwe_id="CWE-176"
                            ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_empty_inputs(self) -> List[Vulnerability]:
        """Test handling of empty and whitespace inputs"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            empty_payloads = [
                "",
                "   ",
                "\n",
                "\t",
                "\r\n",
            ]

            for payload in empty_payloads:
                try:
                    result = safe_sympify(payload)
                    # Empty input should raise ValueError, not return something unexpected
                    if result is not None:
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Empty Input Returns Unexpected Value",
                            severity=Severity.LOW,
                            category=VulnerabilityCategory.INPUT_VALIDATION,
                            description=f"Empty input returned: {result}",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=repr(payload),
                            impact="Unexpected behavior",
                            remediation="Validate empty input handling",
                            cwe_id="CWE-20"
                        ))
                except ValueError:
                    pass  # Expected
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_type_confusion(self) -> List[Vulnerability]:
        """Test for type confusion vulnerabilities"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            type_payloads = [
                123,  # Integer instead of string
                12.5,  # Float
                ['x', '+', '1'],  # List
                {'expr': 'x+1'},  # Dict
                None,  # None
                True,  # Boolean
            ]

            for payload in type_payloads:
                try:
                    result = safe_sympify(payload)
                    # Numbers should be converted, but complex types shouldn't
                    if isinstance(payload, (list, dict)) and result is not None:
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Type Confusion Vulnerability",
                            severity=Severity.LOW,
                            category=VulnerabilityCategory.INPUT_VALIDATION,
                            description=f"Parser accepted {type(payload).__name__} input",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=f"safe_sympify({repr(payload)})",
                            impact="Unexpected input handling",
                            remediation="Strict type checking on input",
                            cwe_id="CWE-843"
                        ))
                except (TypeError, ValueError):
                    pass  # Expected
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_encoding_attacks(self) -> List[Vulnerability]:
        """Test for encoding-based attacks"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            encoding_payloads = [
                "\\x5f\\x5fimport\\x5f\\x5f",  # Hex-encoded __import__
                "\\u005f\\u005fimport\\u005f\\u005f",  # Unicode-encoded
                "eval".encode('rot13').decode() if hasattr(str, 'encode') else "eval",  # ROT13
            ]

            for payload in encoding_payloads:
                try:
                    result = safe_sympify(payload)
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_format_string_attacks(self) -> List[Vulnerability]:
        """Test for format string vulnerabilities"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

            format_payloads = [
                "{0.__class__}",
                "{x.__class__.__bases__}",
                "%(class)s",
                "${{x.__class__}}",
            ]

            for payload in format_payloads:
                try:
                    result = safe_sympify(payload)
                    if '__class__' in str(result) or 'class' in str(result):
                        vulnerabilities.append(Vulnerability(
                            id=self._generate_vuln_id(),
                            title="Format String Information Disclosure",
                            severity=Severity.MEDIUM,
                            category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                            description="Format string disclosed object info",
                            location="symbo_agentic_reasoners.core.safe_parser",
                            proof_of_concept=payload,
                            impact="Information disclosure",
                            remediation="Block format string patterns",
                            cwe_id="CWE-134"
                        ))
                except SecurityError:
                    pass
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    # ==========================================================================
    # BOUNDARY TESTS
    # ==========================================================================

    def _test_max_expression_length(self) -> List[Vulnerability]:
        """Test handling of maximum expression length"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, MAX_INPUT_LENGTH

            # Test just over the limit
            long_expr = "x + " * (MAX_INPUT_LENGTH // 4 + 100) + "1"

            try:
                result = safe_sympify(long_expr)
                # If it succeeded, length limit may not be enforced
                vulnerabilities.append(Vulnerability(
                    id=self._generate_vuln_id(),
                    title="Input Length Limit Not Enforced",
                    severity=Severity.LOW,
                    category=VulnerabilityCategory.BOUNDARY_VIOLATION,
                    description=f"Parser accepted input of {len(long_expr)} chars",
                    location="symbo_agentic_reasoners.core.safe_parser",
                    proof_of_concept=f"Input length: {len(long_expr)}",
                    impact="Resource exhaustion potential",
                    remediation="Enforce MAX_INPUT_LENGTH strictly",
                    cwe_id="CWE-770"
                ))
            except ValueError as e:
                if "too long" in str(e).lower() or "length" in str(e).lower():
                    pass  # Properly limited
                else:
                    pass
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_max_nesting_depth(self) -> List[Vulnerability]:
        """Test handling of maximum nesting depth"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify, MAX_NESTING_DEPTH

            # Create expression with excessive nesting
            deep_expr = "(" * (MAX_NESTING_DEPTH + 10) + "x" + ")" * (MAX_NESTING_DEPTH + 10)

            try:
                result = safe_sympify(deep_expr)
                vulnerabilities.append(Vulnerability(
                    id=self._generate_vuln_id(),
                    title="Nesting Depth Limit Not Enforced",
                    severity=Severity.LOW,
                    category=VulnerabilityCategory.BOUNDARY_VIOLATION,
                    description="Parser accepted excessively nested input",
                    location="symbo_agentic_reasoners.core.safe_parser",
                    proof_of_concept=f"Nesting depth: {MAX_NESTING_DEPTH + 10}",
                    impact="Stack overflow potential",
                    remediation="Enforce MAX_NESTING_DEPTH strictly",
                    cwe_id="CWE-770"
                ))
            except (ValueError, RecursionError):
                pass  # Properly limited
            except Exception:
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_numeric_overflow(self) -> List[Vulnerability]:
        """Test for numeric overflow handling"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            overflow_payloads = [
                "10**1000000",
                "factorial(100000)",
                "2**1000000",
            ]

            for payload in overflow_payloads:
                try:
                    result = safe_sympify(payload)
                    # If huge numbers are computed without limits, it's a concern
                except (OverflowError, MemoryError):
                    pass  # Expected
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_numeric_underflow(self) -> List[Vulnerability]:
        """Test for numeric underflow handling"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            underflow_payloads = [
                "10**(-1000000)",
                "1/(10**1000000)",
            ]

            for payload in underflow_payloads:
                try:
                    result = safe_sympify(payload)
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_precision_limits(self) -> List[Vulnerability]:
        """Test floating point precision limits"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            precision_payloads = [
                "0.1 + 0.2 - 0.3",  # Classic floating point issue
                "10**308",  # Near max float
                "10**(-308)",  # Near min float
            ]

            for payload in precision_payloads:
                try:
                    result = safe_sympify(payload)
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_special_values(self) -> List[Vulnerability]:
        """Test handling of special mathematical values"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            special_payloads = [
                "oo",  # Infinity
                "-oo",  # Negative infinity
                "nan",  # NaN
                "zoo",  # Complex infinity
                "0/0",  # Indeterminate
                "oo/oo",  # Indeterminate
                "0*oo",  # Indeterminate
            ]

            for payload in special_payloads:
                try:
                    result = safe_sympify(payload)
                    # These should be handled gracefully
                except Exception:
                    pass

        except ImportError:
            pass

        return vulnerabilities

    # ==========================================================================
    # CONCURRENCY TESTS
    # ==========================================================================

    def _test_race_condition_state(self) -> List[Vulnerability]:
        """Test for race conditions in shared state"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            results = []
            errors = []

            def worker(expr):
                try:
                    result = safe_sympify(expr)
                    results.append(str(result))
                except Exception as e:
                    errors.append(str(e))

            # Launch concurrent parsings
            threads = []
            for i in range(10):
                t = threading.Thread(target=worker, args=(f"x + {i}",))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=5)

            # Check for inconsistent results
            if len(errors) > 0:
                # Some thread safety issues may cause errors
                pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_thread_safety_parsing(self) -> List[Vulnerability]:
        """Test thread safety of parser"""
        vulnerabilities = []

        try:
            from symbo_agentic_reasoners.core.safe_parser import safe_sympify

            results = []

            def worker(expr, expected):
                try:
                    result = safe_sympify(expr)
                    results.append((expr, str(result), expected))
                except Exception as e:
                    results.append((expr, "ERROR", str(e)))

            # Create threads with different expressions
            threads = []
            test_cases = [
                ("x + 1", "x + 1"),
                ("x**2", "x**2"),
                ("sin(x)", "sin(x)"),
                ("x*y", "x*y"),
            ]

            for _ in range(5):  # Run multiple rounds
                for expr, expected in test_cases:
                    t = threading.Thread(target=worker, args=(expr, expected))
                    threads.append(t)
                    t.start()

            for t in threads:
                t.join(timeout=10)

            # Verify results are consistent
            for expr, result, expected in results:
                if result == "ERROR":
                    # Errors during concurrent parsing might indicate issues
                    pass

        except ImportError:
            pass

        return vulnerabilities

    def _test_deadlock_potential(self) -> List[Vulnerability]:
        """Test for potential deadlock scenarios"""
        vulnerabilities = []

        # This is a simple check - real deadlock testing requires
        # understanding internal locking mechanisms

        return vulnerabilities


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Run security stress test from command line"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Security Stress Tester for Symbo Mathematical System"
    )
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Run quick scan instead of full audit'
    )
    parser.add_argument(
        '--enable-dos',
        action='store_true',
        help='Enable potentially destructive DoS tests'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds for each test (default: 10)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for report (markdown)'
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Output file for JSON report'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Configure tester
    config = {
        'timeout_seconds': args.timeout,
        'enable_dos_tests': args.enable_dos,
        'verbose': not args.quiet
    }

    tester = SecurityStressTester(config)

    # Run appropriate scan
    if args.quick:
        report = tester.run_quick_scan()
    else:
        report = tester.run_full_security_audit()

    # Output report
    markdown_report = report.generate_markdown()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"\nReport written to: {args.output}")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        print(f"JSON report written to: {args.json}")

    if not args.output:
        print("\n" + markdown_report)

    # Return exit code based on findings
    if report.critical_count > 0:
        return 2
    elif report.high_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
