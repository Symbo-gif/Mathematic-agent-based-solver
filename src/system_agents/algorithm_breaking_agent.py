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
ALGORITHM BREAKING AGENT - System Agent
=======================================

A BDI agent for adversarial testing of mathematical algorithms.

CAPABILITIES:
-------------
1. FIND WEAKNESSES: Identify algorithmic weaknesses, edge cases, failure modes
2. FIND FLAWS: Detect logical errors, numerical instabilities, incorrect implementations
3. BREAK ALGORITHMS: Generate inputs that cause failures, expose bugs, trigger edge cases

ATTACK VECTORS:
---------------
- Boundary value fuzzing
- Numerical edge cases (inf, nan, very large/small numbers)
- Type coercion attacks
- Resource exhaustion inputs
- Precision loss triggers
- Division by zero traps
- Overflow/underflow conditions
- Special mathematical values (0, 1, -1, pi, e)

INTEGRATION:
------------
- Works with CrackfinderTestingAgent for vulnerability scanning
- Interacts with MathematicalCrackfinder for adversarial test cases
- Uses Blackboard for reporting discovered vulnerabilities

ARCHITECTURE:
-------------
Follows BDI (Belief-Desire-Intention) pattern:
- Beliefs: Known vulnerabilities, algorithm behaviors, failure patterns
- Desires: Break algorithms, find all weaknesses, expose flaws
- Intentions: Attack strategies, fuzzing campaigns, stability tests
"""

import logging
import math
import random
import time
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('system_agents.algorithm_breaking_agent')


class VulnerabilityType(Enum):
    """Types of vulnerabilities the agent can find."""
    EDGE_CASE = "edge_case"
    NUMERICAL_INSTABILITY = "numerical_instability"
    OVERFLOW = "overflow"
    UNDERFLOW = "underflow"
    DIVISION_BY_ZERO = "division_by_zero"
    INFINITE_LOOP = "infinite_loop"
    INCORRECT_RESULT = "incorrect_result"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TYPE_ERROR = "type_error"
    PRECISION_LOSS = "precision_loss"


class AttackStrategy(Enum):
    """Attack strategies for breaking algorithms."""
    BOUNDARY_FUZZING = "boundary_fuzzing"
    RANDOM_FUZZING = "random_fuzzing"
    NUMERICAL_EDGE_CASES = "numerical_edge_cases"
    MATHEMATICAL_CONSTANTS = "mathematical_constants"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PRECISION_ATTACK = "precision_attack"
    TYPE_COERCION = "type_coercion"
    SYMBOLIC_ATTACK = "symbolic_attack"


@dataclass
class Vulnerability:
    """A discovered vulnerability in an algorithm."""
    algorithm_name: str
    vulnerability_type: VulnerabilityType
    severity: str  # "critical", "high", "medium", "low"
    description: str
    triggering_input: Any
    actual_output: Any
    expected_behavior: str
    stack_trace: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AttackResult:
    """Result of an attack campaign against an algorithm."""
    algorithm_name: str
    strategy: AttackStrategy
    inputs_tested: int
    vulnerabilities_found: List[Vulnerability]
    success_rate: float  # 0.0 to 1.0 (fraction that didn't break)
    execution_time: float
    summary: str


@dataclass
class FuzzingCampaign:
    """Configuration for a fuzzing campaign."""
    algorithm_name: str
    strategies: List[AttackStrategy]
    max_iterations: int = 1000
    timeout_per_input: float = 5.0
    seed: Optional[int] = None


class AlgorithmBreakingAgent(BDIAgent):
    """
    Algorithm Breaking Agent - System Agent

    DIRECTIVE:
    ----------
    Find weaknesses, flaws, and break mathematical algorithms through
    adversarial testing while maintaining ethical boundaries (only test
    our own codebase for improvement purposes).

    OPERATIONS:
    -----------
    - fuzz_algorithm: Run fuzzing campaign against an algorithm
    - find_edge_cases: Identify edge cases that break the algorithm
    - test_numerical_stability: Test for numerical instabilities
    - test_performance: Find performance degradation inputs
    - break_algorithm: Systematic attempt to find breaking inputs
    """

    def __init__(
        self,
        agent_id: str = "algorithm_breaking_agent",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)

        self.agent_type = "algorithm_breaking_agent"
        self.df = directory_facilitator
        self.blackboard = blackboard

        # Known vulnerabilities discovered
        self._vulnerabilities: List[Vulnerability] = []
        self._attack_history: List[AttackResult] = []

        # Statistics
        self._stats = {
            'algorithms_attacked': 0,
            'vulnerabilities_found': 0,
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'medium_vulnerabilities': 0,
            'low_vulnerabilities': 0,
            'inputs_tested': 0,
            'fuzzing_campaigns': 0,
        }

        # Pre-computed attack inputs
        self._attack_inputs = self._generate_attack_inputs()

        self._register_services()

        logger.info(f"[{agent_id}] Algorithm Breaking Agent initialized")

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="algorithm_fuzzing",
                    description="Fuzz mathematical algorithms"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="vulnerability_scanning",
                    description="Scan for algorithm vulnerabilities"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="adversarial_testing",
                    description="Adversarial testing of algorithms"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    def _generate_attack_inputs(self) -> Dict[str, List[Any]]:
        """Generate pre-computed attack inputs for various scenarios."""
        return {
            'numerical_edge_cases': [
                0, -0.0, 0.0,
                1, -1,
                float('inf'), float('-inf'),
                float('nan'),
                sys.float_info.max,
                sys.float_info.min,
                sys.float_info.epsilon,
                -sys.float_info.max,
                1e308, -1e308,
                1e-308, -1e-308,
                1e-324,  # Smallest subnormal
            ],
            'mathematical_constants': [
                math.pi, -math.pi,
                math.e, -math.e,
                math.sqrt(2), -math.sqrt(2),
                math.log(2), math.log(10),
                0.5, -0.5,
                1.0 / 3.0,  # Repeating decimal
                math.tau,
            ],
            'boundary_integers': [
                0, 1, -1, 2, -2,
                2**31 - 1, -(2**31),  # 32-bit limits
                2**63 - 1, -(2**63),  # 64-bit limits
                2**128, -(2**128),
                10**100,  # Very large
            ],
            'precision_attacks': [
                1.0 + 1e-15,
                1.0 - 1e-15,
                0.1 + 0.2,  # Famous float issue
                (1.0 / 3.0) * 3.0,
                math.sqrt(2) ** 2,
                1e-300 * 1e-100,  # Underflow risk
            ],
            'string_attacks': [
                "", " ", "  ",
                "x", "X", "abc",
                "0", "1", "-1",
                "inf", "-inf", "nan",
                "1e1000", "1e-1000",
                "1/0", "0/0",
            ],
            'list_attacks': [
                [], [0], [1],
                [0, 0], [1, 1],
                list(range(1000)),
                list(range(-100, 100)),
                [float('inf')],
                [float('nan')],
                [[]], [[[]]],
            ],
        }

    # ==================== CORE ATTACK CAPABILITIES ====================

    def fuzz_algorithm(
        self,
        func: Callable,
        algorithm_name: str,
        campaign: Optional[FuzzingCampaign] = None,
    ) -> AttackResult:
        """
        Run a fuzzing campaign against an algorithm.

        Args:
            func: Function to fuzz
            algorithm_name: Name of the algorithm
            campaign: Fuzzing campaign configuration

        Returns:
            AttackResult with findings
        """
        logger.info(f"Fuzzing algorithm: {algorithm_name}")

        if campaign is None:
            campaign = FuzzingCampaign(
                algorithm_name=algorithm_name,
                strategies=[s for s in AttackStrategy],
                max_iterations=500
            )

        if campaign.seed is not None:
            random.seed(campaign.seed)

        vulnerabilities = []
        inputs_tested = 0
        start_time = time.time()

        for strategy in campaign.strategies:
            attack_inputs = self._get_inputs_for_strategy(strategy)

            for i, attack_input in enumerate(attack_inputs):
                if inputs_tested >= campaign.max_iterations:
                    break

                vuln = self._test_input(func, algorithm_name, attack_input, strategy)
                if vuln:
                    vulnerabilities.append(vuln)

                inputs_tested += 1
                self._stats['inputs_tested'] += 1

        execution_time = time.time() - start_time

        # Calculate success rate (inputs that didn't break)
        success_rate = 1.0 - (len(vulnerabilities) / max(inputs_tested, 1))

        self._stats['algorithms_attacked'] += 1
        self._stats['vulnerabilities_found'] += len(vulnerabilities)
        self._stats['fuzzing_campaigns'] += 1

        # Update severity counts
        for vuln in vulnerabilities:
            self._vulnerabilities.append(vuln)
            if vuln.severity == 'critical':
                self._stats['critical_vulnerabilities'] += 1
            elif vuln.severity == 'high':
                self._stats['high_vulnerabilities'] += 1
            elif vuln.severity == 'medium':
                self._stats['medium_vulnerabilities'] += 1
            else:
                self._stats['low_vulnerabilities'] += 1

        result = AttackResult(
            algorithm_name=algorithm_name,
            strategy=campaign.strategies[0] if len(campaign.strategies) == 1 else AttackStrategy.RANDOM_FUZZING,
            inputs_tested=inputs_tested,
            vulnerabilities_found=vulnerabilities,
            success_rate=success_rate,
            execution_time=execution_time,
            summary=self._generate_attack_summary(vulnerabilities, inputs_tested)
        )

        self._attack_history.append(result)
        return result

    def _get_inputs_for_strategy(self, strategy: AttackStrategy) -> List[Any]:
        """Get attack inputs for a specific strategy."""
        if strategy == AttackStrategy.NUMERICAL_EDGE_CASES:
            return self._attack_inputs['numerical_edge_cases']
        elif strategy == AttackStrategy.MATHEMATICAL_CONSTANTS:
            return self._attack_inputs['mathematical_constants']
        elif strategy == AttackStrategy.BOUNDARY_FUZZING:
            return self._attack_inputs['boundary_integers']
        elif strategy == AttackStrategy.PRECISION_ATTACK:
            return self._attack_inputs['precision_attacks']
        elif strategy == AttackStrategy.RANDOM_FUZZING:
            return self._generate_random_inputs(100)
        elif strategy == AttackStrategy.RESOURCE_EXHAUSTION:
            return self._generate_resource_exhaustion_inputs()
        elif strategy == AttackStrategy.TYPE_COERCION:
            return self._attack_inputs['string_attacks'] + self._attack_inputs['list_attacks']
        else:
            return self._attack_inputs['numerical_edge_cases']

    def _generate_random_inputs(self, count: int) -> List[Any]:
        """Generate random fuzzing inputs."""
        inputs = []
        for _ in range(count):
            choice = random.random()
            if choice < 0.3:
                inputs.append(random.uniform(-1e10, 1e10))
            elif choice < 0.5:
                inputs.append(random.randint(-10**9, 10**9))
            elif choice < 0.7:
                inputs.append(random.uniform(-1e-10, 1e-10))
            elif choice < 0.9:
                inputs.append(random.choice(self._attack_inputs['numerical_edge_cases']))
            else:
                inputs.append(random.choice(self._attack_inputs['mathematical_constants']))
        return inputs

    def _generate_resource_exhaustion_inputs(self) -> List[Any]:
        """Generate inputs designed to exhaust resources."""
        return [
            list(range(10000)),
            list(range(100000)),
            [1] * 50000,
            10**1000,  # Very large integer
            "x" * 100000,
            [[1] * 1000] * 1000,  # Large nested structure
        ]

    def _test_input(
        self,
        func: Callable,
        algorithm_name: str,
        attack_input: Any,
        strategy: AttackStrategy,
    ) -> Optional[Vulnerability]:
        """Test a single input against the algorithm."""
        try:
            start_time = time.time()

            # Try to call the function
            if isinstance(attack_input, (list, tuple)) and len(attack_input) > 1:
                result = func(*attack_input)
            else:
                result = func(attack_input)

            execution_time = time.time() - start_time

            # Check for suspicious results
            if isinstance(result, float):
                if math.isnan(result):
                    return Vulnerability(
                        algorithm_name=algorithm_name,
                        vulnerability_type=VulnerabilityType.NUMERICAL_INSTABILITY,
                        severity="medium",
                        description="Function returned NaN",
                        triggering_input=attack_input,
                        actual_output=result,
                        expected_behavior="Valid numerical result",
                        recommendations=["Add NaN checking", "Validate intermediate computations"]
                    )
                if math.isinf(result):
                    return Vulnerability(
                        algorithm_name=algorithm_name,
                        vulnerability_type=VulnerabilityType.OVERFLOW,
                        severity="medium",
                        description="Function returned infinity",
                        triggering_input=attack_input,
                        actual_output=result,
                        expected_behavior="Finite numerical result",
                        recommendations=["Add overflow protection", "Use arbitrary precision arithmetic"]
                    )

            # Check for slow execution (potential DoS)
            if execution_time > 5.0:
                return Vulnerability(
                    algorithm_name=algorithm_name,
                    vulnerability_type=VulnerabilityType.PERFORMANCE_DEGRADATION,
                    severity="low",
                    description=f"Slow execution: {execution_time:.2f}s",
                    triggering_input=attack_input,
                    actual_output=f"Time: {execution_time:.2f}s",
                    expected_behavior="Fast execution (< 5s)",
                    recommendations=["Add early exit conditions", "Optimize algorithm", "Add timeout"]
                )

            return None

        except ZeroDivisionError as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.DIVISION_BY_ZERO,
                severity="high",
                description="Division by zero",
                triggering_input=attack_input,
                actual_output=str(e),
                expected_behavior="Handle zero division gracefully",
                stack_trace=str(e),
                recommendations=["Add zero check before division", "Return None or raise ValueError"]
            )

        except OverflowError as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.OVERFLOW,
                severity="high",
                description="Numerical overflow",
                triggering_input=attack_input,
                actual_output=str(e),
                expected_behavior="Handle large numbers gracefully",
                stack_trace=str(e),
                recommendations=["Use arbitrary precision", "Add bounds checking"]
            )

        except RecursionError as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.RESOURCE_EXHAUSTION,
                severity="critical",
                description="Stack overflow (infinite recursion)",
                triggering_input=attack_input,
                actual_output=str(e),
                expected_behavior="Bounded recursion depth",
                stack_trace=str(e),
                recommendations=["Add recursion depth limit", "Convert to iterative"]
            )

        except MemoryError as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.RESOURCE_EXHAUSTION,
                severity="critical",
                description="Memory exhaustion",
                triggering_input=repr(attack_input)[:100],
                actual_output=str(e),
                expected_behavior="Bounded memory usage",
                stack_trace=str(e),
                recommendations=["Add input size limits", "Use generators", "Stream processing"]
            )

        except ValueError as e:
            # ValueError is often expected for edge cases, classify based on message
            error_msg = str(e).lower()
            if 'domain' in error_msg or 'negative' in error_msg:
                return Vulnerability(
                    algorithm_name=algorithm_name,
                    vulnerability_type=VulnerabilityType.EDGE_CASE,
                    severity="low",
                    description=f"Domain error: {e}",
                    triggering_input=attack_input,
                    actual_output=str(e),
                    expected_behavior="Handle domain errors gracefully",
                    stack_trace=str(e),
                    recommendations=["Add input validation", "Document domain restrictions"]
                )
            return None  # Expected ValueError, not a vulnerability

        except TypeError as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.TYPE_ERROR,
                severity="medium",
                description=f"Type error: {e}",
                triggering_input=attack_input,
                actual_output=str(e),
                expected_behavior="Handle type mismatches gracefully",
                stack_trace=str(e),
                recommendations=["Add type checking", "Use type hints", "Validate inputs"]
            )

        except Exception as e:
            return Vulnerability(
                algorithm_name=algorithm_name,
                vulnerability_type=VulnerabilityType.EDGE_CASE,
                severity="medium",
                description=f"Unhandled exception: {type(e).__name__}: {e}",
                triggering_input=attack_input,
                actual_output=str(e),
                expected_behavior="No unhandled exceptions",
                stack_trace=str(e),
                recommendations=["Add comprehensive error handling", "Test edge cases"]
            )

    def _generate_attack_summary(self, vulnerabilities: List[Vulnerability], inputs_tested: int) -> str:
        """Generate a summary of the attack results."""
        if not vulnerabilities:
            return f"No vulnerabilities found in {inputs_tested} inputs tested."

        severity_counts = {}
        for v in vulnerabilities:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        summary_parts = [f"Found {len(vulnerabilities)} vulnerabilities in {inputs_tested} inputs:"]
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in severity_counts:
                summary_parts.append(f"  - {severity.upper()}: {severity_counts[severity]}")

        return "\n".join(summary_parts)

    def find_edge_cases(self, func: Callable, algorithm_name: str) -> List[Vulnerability]:
        """Find edge cases that break the algorithm."""
        logger.info(f"Finding edge cases for: {algorithm_name}")

        campaign = FuzzingCampaign(
            algorithm_name=algorithm_name,
            strategies=[
                AttackStrategy.NUMERICAL_EDGE_CASES,
                AttackStrategy.BOUNDARY_FUZZING,
                AttackStrategy.MATHEMATICAL_CONSTANTS
            ],
            max_iterations=200
        )

        result = self.fuzz_algorithm(func, algorithm_name, campaign)
        return result.vulnerabilities_found

    def test_numerical_stability(self, func: Callable, algorithm_name: str) -> List[Vulnerability]:
        """Test for numerical instabilities."""
        logger.info(f"Testing numerical stability: {algorithm_name}")

        campaign = FuzzingCampaign(
            algorithm_name=algorithm_name,
            strategies=[
                AttackStrategy.PRECISION_ATTACK,
                AttackStrategy.NUMERICAL_EDGE_CASES
            ],
            max_iterations=100
        )

        result = self.fuzz_algorithm(func, algorithm_name, campaign)

        # Filter for numerical instability vulnerabilities
        return [v for v in result.vulnerabilities_found
                if v.vulnerability_type in [
                    VulnerabilityType.NUMERICAL_INSTABILITY,
                    VulnerabilityType.OVERFLOW,
                    VulnerabilityType.UNDERFLOW,
                    VulnerabilityType.PRECISION_LOSS
                ]]

    def test_performance(self, func: Callable, algorithm_name: str) -> List[Vulnerability]:
        """Find inputs that cause performance degradation."""
        logger.info(f"Testing performance: {algorithm_name}")

        campaign = FuzzingCampaign(
            algorithm_name=algorithm_name,
            strategies=[AttackStrategy.RESOURCE_EXHAUSTION],
            max_iterations=20
        )

        result = self.fuzz_algorithm(func, algorithm_name, campaign)

        # Filter for performance vulnerabilities
        return [v for v in result.vulnerabilities_found
                if v.vulnerability_type in [
                    VulnerabilityType.PERFORMANCE_DEGRADATION,
                    VulnerabilityType.RESOURCE_EXHAUSTION,
                    VulnerabilityType.INFINITE_LOOP
                ]]

    def break_algorithm(self, func: Callable, algorithm_name: str) -> AttackResult:
        """Systematic attempt to break an algorithm."""
        logger.info(f"Attempting to break: {algorithm_name}")

        campaign = FuzzingCampaign(
            algorithm_name=algorithm_name,
            strategies=[s for s in AttackStrategy],
            max_iterations=1000
        )

        return self.fuzz_algorithm(func, algorithm_name, campaign)

    def scan_codebase_vulnerabilities(
        self,
        modules: Dict[str, Callable]
    ) -> Dict[str, AttackResult]:
        """Scan multiple modules for vulnerabilities."""
        logger.info(f"Scanning {len(modules)} modules for vulnerabilities")

        results = {}
        for name, func in modules.items():
            try:
                results[name] = self.break_algorithm(func, name)
            except Exception as e:
                logger.error(f"Failed to scan {name}: {e}")

        return results

    def generate_vulnerability_report(self) -> str:
        """Generate a comprehensive vulnerability report."""
        report_lines = [
            "=" * 60,
            "ALGORITHM VULNERABILITY REPORT",
            "=" * 60,
            "",
            f"Total Algorithms Tested: {self._stats['algorithms_attacked']}",
            f"Total Inputs Tested: {self._stats['inputs_tested']}",
            f"Total Vulnerabilities Found: {self._stats['vulnerabilities_found']}",
            "",
            "SEVERITY BREAKDOWN:",
            f"  - Critical: {self._stats['critical_vulnerabilities']}",
            f"  - High: {self._stats['high_vulnerabilities']}",
            f"  - Medium: {self._stats['medium_vulnerabilities']}",
            f"  - Low: {self._stats['low_vulnerabilities']}",
            "",
            "=" * 60,
            "DETAILED FINDINGS:",
            "=" * 60,
        ]

        for vuln in self._vulnerabilities:
            report_lines.extend([
                "",
                f"Algorithm: {vuln.algorithm_name}",
                f"Type: {vuln.vulnerability_type.value}",
                f"Severity: {vuln.severity.upper()}",
                f"Description: {vuln.description}",
                f"Triggering Input: {vuln.triggering_input}",
                f"Recommendations: {', '.join(vuln.recommendations)}",
                "-" * 40,
            ])

        return "\n".join(report_lines)

    # ==================== BDI IMPLEMENTATION ====================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for attack targets."""
        if not self.blackboard:
            return

        try:
            # Find algorithms to test
            tasks = self.blackboard.query_entries(
                tags=['break', 'algorithm'],
                status=EntryStatus.PENDING
            ) if hasattr(self.blackboard, 'query_entries') else []

            fuzz_tasks = self.blackboard.query_entries(
                tags=['fuzz', 'algorithm'],
                status=EntryStatus.PENDING
            ) if hasattr(self.blackboard, 'query_entries') else []

            all_tasks = tasks + fuzz_tasks

            for task in all_tasks:
                belief_key = f'pending_attack_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.warning(f"update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create attack plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_attack_task_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            attack_type = metadata.get('attack_type', 'full')

            if attack_type == 'edge_cases':
                steps = ['claim_task', 'load_target', 'find_edge_cases', 'post_report']
            elif attack_type == 'stability':
                steps = ['claim_task', 'load_target', 'test_stability', 'post_report']
            elif attack_type == 'performance':
                steps = ['claim_task', 'load_target', 'test_performance', 'post_report']
            else:
                steps = ['claim_task', 'load_target', 'full_attack', 'post_report']

            intention = Intention(
                plan_id=f'attack_{attack_type}_{task_id}',
                steps=steps,
                target_desire=f'break_algorithm_{attack_type}',
                metadata={'task_id': task_id, 'task_entry': task, 'attack_type': attack_type}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute attack steps."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_attack_{task_id}', True)
                self.remove_belief(f'pending_attack_task_{task_id}')
                intention.advance()

            elif action == 'load_target':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                func = metadata.get('function')
                name = metadata.get('algorithm_name', 'unknown')
                intention.metadata['target_func'] = func
                intention.metadata['target_name'] = name
                intention.advance()

            elif action == 'find_edge_cases':
                func = intention.metadata.get('target_func')
                name = intention.metadata.get('target_name')
                if func:
                    vulns = self.find_edge_cases(func, name)
                    intention.metadata['vulnerabilities'] = vulns
                intention.advance()

            elif action == 'test_stability':
                func = intention.metadata.get('target_func')
                name = intention.metadata.get('target_name')
                if func:
                    vulns = self.test_numerical_stability(func, name)
                    intention.metadata['vulnerabilities'] = vulns
                intention.advance()

            elif action == 'test_performance':
                func = intention.metadata.get('target_func')
                name = intention.metadata.get('target_name')
                if func:
                    vulns = self.test_performance(func, name)
                    intention.metadata['vulnerabilities'] = vulns
                intention.advance()

            elif action == 'full_attack':
                func = intention.metadata.get('target_func')
                name = intention.metadata.get('target_name')
                if func:
                    result = self.break_algorithm(func, name)
                    intention.metadata['attack_result'] = result
                    intention.metadata['vulnerabilities'] = result.vulnerabilities_found
                intention.advance()

            elif action == 'post_report':
                vulns = intention.metadata.get('vulnerabilities', [])
                attack_result = intention.metadata.get('attack_result')

                if self.blackboard:
                    report_data = {
                        'vulnerabilities': [v.__dict__ for v in vulns] if vulns else [],
                        'attack_result': attack_result.__dict__ if attack_result else None,
                        'stats': dict(self._stats)
                    }

                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=str(report_data),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['vulnerability', 'report', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'report': report_data}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            logger.error(f"execute_step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        stats = super().get_statistics()
        stats.update(self._stats)
        stats['vulnerabilities_in_memory'] = len(self._vulnerabilities)
        stats['attack_history_size'] = len(self._attack_history)
        return stats

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'fuzz':
            func = params.get('function')
            name = params.get('name', 'unknown')
            if func:
                result = self.fuzz_algorithm(func, name)
                return {'status': 'success', 'result': result.__dict__}
            return {'status': 'error', 'message': 'No function provided'}

        elif action == 'edge_cases':
            func = params.get('function')
            name = params.get('name', 'unknown')
            if func:
                vulns = self.find_edge_cases(func, name)
                return {'status': 'success', 'vulnerabilities': [v.__dict__ for v in vulns]}
            return {'status': 'error', 'message': 'No function provided'}

        elif action == 'stability':
            func = params.get('function')
            name = params.get('name', 'unknown')
            if func:
                vulns = self.test_numerical_stability(func, name)
                return {'status': 'success', 'vulnerabilities': [v.__dict__ for v in vulns]}
            return {'status': 'error', 'message': 'No function provided'}

        elif action == 'break':
            func = params.get('function')
            name = params.get('name', 'unknown')
            if func:
                result = self.break_algorithm(func, name)
                return {'status': 'success', 'result': result.__dict__}
            return {'status': 'error', 'message': 'No function provided'}

        elif action == 'report':
            report = self.generate_vulnerability_report()
            return {'status': 'success', 'report': report}

        elif action == 'stats':
            return {'status': 'success', 'stats': self.get_statistics()}

        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}


__all__ = [
    'AlgorithmBreakingAgent',
    'Vulnerability',
    'AttackResult',
    'FuzzingCampaign',
    'VulnerabilityType',
    'AttackStrategy',
]
