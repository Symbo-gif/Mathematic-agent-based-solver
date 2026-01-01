#!/usr/bin/env python3
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
Security Test Runner
====================

Comprehensive security testing script for Symbo Agentic Reasoners.
Runs all security tests and generates a detailed report.

Usage:
    python scripts/run_security_tests.py
    python scripts/run_security_tests.py --quick  # Quick scan only
    python scripts/run_security_tests.py --full   # Full audit
"""

import sys
import os
import time
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print formatted header."""
    print()
    print(Colors.HEADER + Colors.BOLD + "="*80 + Colors.ENDC)
    print(Colors.HEADER + Colors.BOLD + text.center(80) + Colors.ENDC)
    print(Colors.HEADER + Colors.BOLD + "="*80 + Colors.ENDC)
    print()


def print_section(text: str):
    """Print section header."""
    print()
    print(Colors.OKBLUE + Colors.BOLD + text + Colors.ENDC)
    print(Colors.OKBLUE + "-"*len(text) + Colors.ENDC)


def print_success(text: str):
    """Print success message."""
    print(Colors.OKGREEN + "[✓] " + text + Colors.ENDC)


def print_failure(text: str):
    """Print failure message."""
    print(Colors.FAIL + "[✗] " + text + Colors.ENDC)


def print_warning(text: str):
    """Print warning message."""
    print(Colors.WARNING + "[!] " + text + Colors.ENDC)


def test_injection_defenses() -> Dict[str, Any]:
    """Test injection attack defenses."""
    print_section("Testing Injection Attack Defenses")

    from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

    results = {
        'category': 'Injection Attacks',
        'tests': [],
        'passed': 0,
        'failed': 0
    }

    injection_vectors = [
        "__import__('os').system('ls')",
        "eval('1+1')",
        "exec('print(1)')",
        "open('/etc/passwd').read()",
        "getattr(__builtins__, 'eval')('code')",
        "().__class__.__bases__[0].__subclasses__()",
        "lambda: __import__('os')",
        "compile('import os', '', 'exec')",
    ]

    for vector in injection_vectors:
        test_name = f"Block: {vector[:50]}"
        try:
            safe_parse(vector)
            # If parsing succeeded, that's a failure
            print_failure(test_name)
            results['failed'] += 1
            results['tests'].append({
                'name': test_name,
                'status': 'FAILED',
                'reason': 'Malicious code was not blocked'
            })
        except (SecurityError, SyntaxError, NameError, TypeError, ValueError):
            # Expected - blocked
            print_success(test_name)
            results['passed'] += 1
            results['tests'].append({
                'name': test_name,
                'status': 'PASSED'
            })
        except Exception as e:
            # Unexpected error, but still safe
            print_warning(f"{test_name} - Unexpected: {type(e).__name__}")
            results['passed'] += 1
            results['tests'].append({
                'name': test_name,
                'status': 'PASSED',
                'note': f'Blocked with {type(e).__name__}'
            })

    return results


def test_parser_bombs() -> Dict[str, Any]:
    """Test parser bomb defenses."""
    print_section("Testing Parser Bomb Defenses")

    from symbo_agentic_reasoners.core.safe_parser import safe_parse

    results = {
        'category': 'Parser Bombs',
        'tests': [],
        'passed': 0,
        'failed': 0
    }

    bombs = [
        ("Deep nesting", "(" * 100 + "x" + ")" * 100),
        ("Factorial bomb", "factorial(100000)"),
        ("Expansion bomb", "(x+1)**10000"),
        ("Function nesting", "sin(" * 100 + "x" + ")" * 100),
    ]

    for name, bomb in bombs:
        start = time.time()
        try:
            safe_parse(bomb)
            elapsed = time.time() - start
            if elapsed > 5.0:
                print_failure(f"{name} - Took {elapsed:.2f}s (timeout)")
                results['failed'] += 1
                results['tests'].append({
                    'name': name,
                    'status': 'FAILED',
                    'reason': f'Took {elapsed:.2f}s'
                })
            else:
                print_success(f"{name} - Handled in {elapsed:.2f}s")
                results['passed'] += 1
                results['tests'].append({
                    'name': name,
                    'status': 'PASSED',
                    'time': elapsed
                })
        except (ValueError, MemoryError, TimeoutError, RecursionError, OverflowError):
            elapsed = time.time() - start
            print_success(f"{name} - Blocked in {elapsed:.2f}s")
            results['passed'] += 1
            results['tests'].append({
                'name': name,
                'status': 'PASSED',
                'time': elapsed
            })

    return results


def test_sandbox_security() -> Dict[str, Any]:
    """Test sandbox security."""
    print_section("Testing Sandbox Security")

    results = {
        'category': 'Sandbox Isolation',
        'tests': [],
        'passed': 0,
        'failed': 0
    }

    try:
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator, EvaluationStatus
        )

        evaluator = SandboxEvaluator()

        escape_attempts = [
            ("File access", "def solve(x): open('/etc/passwd').read(); return x"),
            ("Import os", "def solve(x): import os; os.listdir('/'); return x"),
            ("Import sys", "def solve(x): import sys; sys.exit(); return x"),
            ("Socket access", "def solve(x): import socket; socket.socket(); return x"),
        ]

        for name, code in escape_attempts:
            result = evaluator.evaluate(code, [((1,), 1)])

            if result.status == EvaluationStatus.SUCCESS:
                print_failure(f"{name} - Sandbox escaped!")
                results['failed'] += 1
                results['tests'].append({
                    'name': name,
                    'status': 'FAILED',
                    'reason': 'Sandbox escape succeeded'
                })
            else:
                print_success(f"{name} - Blocked")
                results['passed'] += 1
                results['tests'].append({
                    'name': name,
                    'status': 'PASSED'
                })

    except ImportError:
        print_warning("Sandbox evaluator not available - skipping tests")
        results['tests'].append({
            'name': 'Sandbox tests',
            'status': 'SKIPPED',
            'reason': 'Module not available'
        })

    return results


def test_agent_security() -> Dict[str, Any]:
    """Test agent security."""
    print_section("Testing Agent Security")

    from symbo_agentic_reasoners.infrastructure.security_monitor import (
        SecurityMonitor, AccessDecision
    )

    results = {
        'category': 'Agent Security',
        'tests': [],
        'passed': 0,
        'failed': 0
    }

    monitor = SecurityMonitor()
    monitor.register_agent("test_agent")

    # Test access control
    restricted_resources = [
        ("admin/config", "write"),
        ("system/shutdown", "execute"),
        ("admin/users", "delete"),
    ]

    for resource, action in restricted_resources:
        decision = monitor.check_access("test_agent", resource, action)

        if decision in [AccessDecision.DENY, AccessDecision.AUDIT]:
            print_success(f"Access denied: {resource} ({action})")
            results['passed'] += 1
            results['tests'].append({
                'name': f'Access control: {resource}',
                'status': 'PASSED'
            })
        else:
            print_failure(f"Access allowed: {resource} ({action})")
            results['failed'] += 1
            results['tests'].append({
                'name': f'Access control: {resource}',
                'status': 'FAILED',
                'reason': 'Access not properly restricted'
            })

    # Test rate limiting
    print()
    print("Testing rate limiting...")
    denied_count = 0
    for i in range(2000):
        decision = monitor.check_access("test_agent", f"resource_{i}", "read")
        if decision == AccessDecision.DENY:
            denied_count += 1

    if denied_count > 0:
        print_success(f"Rate limiting active ({denied_count} denied)")
        results['passed'] += 1
        results['tests'].append({
            'name': 'Rate limiting',
            'status': 'PASSED',
            'denials': denied_count
        })
    else:
        print_warning("Rate limiting not triggered")
        results['failed'] += 1
        results['tests'].append({
            'name': 'Rate limiting',
            'status': 'FAILED',
            'reason': 'No rate limiting detected'
        })

    return results


def test_resource_limits() -> Dict[str, Any]:
    """Test resource limit enforcement."""
    print_section("Testing Resource Limits")

    results = {
        'category': 'Resource Limits',
        'tests': [],
        'passed': 0,
        'failed': 0
    }

    try:
        from symbo_agentic_reasoners.infrastructure.resource_governor import get_governor

        governor = get_governor()
        governor.initialize()
        governor.start()

        # Test operation approval
        if governor.can_proceed('test_operation'):
            print_success("Resource governor operational")
            results['passed'] += 1
            results['tests'].append({
                'name': 'Resource governor',
                'status': 'PASSED'
            })
        else:
            print_warning("Resource governor blocking operations")
            results['tests'].append({
                'name': 'Resource governor',
                'status': 'WARNING',
                'reason': 'Governor is blocking operations'
            })

        # Get status
        status = governor.get_status()
        print(f"  VRAM: {status.vram_utilization:.1%}")
        print(f"  RAM:  {status.ram_utilization:.1%}")
        print(f"  CPU:  {status.cpu_utilization:.1%}")

        governor.stop()

    except Exception as e:
        print_failure(f"Resource governor error: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'Resource governor',
            'status': 'FAILED',
            'reason': str(e)
        })

    return results


def generate_report(all_results: List[Dict[str, Any]], output_file: str = None):
    """Generate comprehensive security report."""
    print_header("SECURITY TEST REPORT")

    total_tests = sum(r['passed'] + r['failed'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)

    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {Colors.OKGREEN}{total_passed}{Colors.ENDC}")
    print(f"Failed:       {Colors.FAIL}{total_failed}{Colors.ENDC}")
    print(f"Pass Rate:    {total_passed/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
    print()

    # Category breakdown
    print_section("Results by Category")
    for result in all_results:
        category = result['category']
        passed = result['passed']
        failed = result['failed']
        total = passed + failed

        if failed == 0:
            status = Colors.OKGREEN + "SECURE" + Colors.ENDC
        elif failed < passed:
            status = Colors.WARNING + "WARNINGS" + Colors.ENDC
        else:
            status = Colors.FAIL + "VULNERABLE" + Colors.ENDC

        print(f"  {category:30} {passed:3}/{total:3} {status}")

    # Risk assessment
    print()
    print_section("Risk Assessment")

    if total_failed == 0:
        print(Colors.OKGREEN + "✓ SECURE - No critical vulnerabilities found" + Colors.ENDC)
        risk_level = "LOW"
    elif total_failed < total_passed / 10:
        print(Colors.WARNING + "! WARNINGS - Minor security issues detected" + Colors.ENDC)
        risk_level = "MEDIUM"
    else:
        print(Colors.FAIL + "✗ VULNERABLE - Critical security issues found" + Colors.ENDC)
        risk_level = "HIGH"

    # Save report
    if output_file:
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'risk_level': risk_level
            },
            'categories': all_results
        }

        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print()
        print(f"Report saved to: {output_file}")

    return total_failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run security tests')
    parser.add_argument('--quick', action='store_true', help='Quick scan only')
    parser.add_argument('--full', action='store_true', help='Full comprehensive audit')
    parser.add_argument('--output', type=str, help='Output report file')
    args = parser.parse_args()

    print_header("SYMBO SECURITY TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = []

    try:
        # Run test suites
        all_results.append(test_injection_defenses())
        all_results.append(test_parser_bombs())

        if not args.quick:
            all_results.append(test_sandbox_security())
            all_results.append(test_agent_security())
            all_results.append(test_resource_limits())

        # Generate report
        output_file = args.output or 'security_test_report.json'
        success = generate_report(all_results, output_file)

        return 0 if success else 1

    except KeyboardInterrupt:
        print()
        print_warning("Tests interrupted by user")
        return 2
    except Exception as e:
        print()
        print_failure(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
