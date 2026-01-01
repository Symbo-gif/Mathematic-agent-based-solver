#!/usr/bin/env python
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
Code Coverage Script
====================

Runs the test suite with code coverage reporting.

Usage:
    python scripts/run_coverage.py              # Run with terminal report
    python scripts/run_coverage.py --html       # Generate HTML report
    python scripts/run_coverage.py --xml        # Generate XML report (for CI)
    python scripts/run_coverage.py --full       # Generate all report formats
    python scripts/run_coverage.py --quick      # Quick run on core tests only
"""

import subprocess
import sys
import os
from pathlib import Path

# Ensure we're in the project root
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


def run_coverage(html: bool = False, xml: bool = False, full: bool = False, quick: bool = False):
    """Run pytest with coverage."""

    # Base command
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src/symbo_agentic_reasoners",
        "--cov-branch",
    ]

    # Add report formats
    if html or full:
        cmd.append("--cov-report=html")

    if xml or full:
        cmd.append("--cov-report=xml")

    # Always include terminal report
    cmd.append("--cov-report=term-missing")

    # Test selection
    if quick:
        # Quick mode: only run core tests
        cmd.extend([
            "tests/test_config.py",
            "tests/test_security.py",
            "tests/test_phase5_optimization.py",
            "tests/test_phase6_discovery.py",
        ])
    else:
        # Full test suite
        cmd.append("tests/")

    # Additional options
    cmd.extend([
        "-v",
        "--tb=short",
    ])

    print("=" * 70)
    print("SYMBO_AGENTIC_REASONERS Coverage Report")
    print("=" * 70)
    print()
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print()
        print("=" * 70)
        print("Coverage run completed successfully!")
        print("=" * 70)

        if html or full:
            html_path = PROJECT_ROOT / "htmlcov" / "index.html"
            print(f"\nHTML report: {html_path}")
            print("Open in browser to view detailed coverage.")

        if xml or full:
            xml_path = PROJECT_ROOT / "coverage.xml"
            print(f"\nXML report: {xml_path}")
            print("Use with CI/CD tools like Codecov or Coveralls.")
    else:
        print()
        print("=" * 70)
        print("Coverage run completed with failures.")
        print("=" * 70)

    return result.returncode


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run tests with code coverage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_coverage.py              # Terminal report only
    python scripts/run_coverage.py --html       # Terminal + HTML report
    python scripts/run_coverage.py --xml        # Terminal + XML report
    python scripts/run_coverage.py --full       # All reports
    python scripts/run_coverage.py --quick      # Quick core tests only
    python scripts/run_coverage.py --quick --html  # Quick with HTML
"""
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report (in htmlcov/)"
    )

    parser.add_argument(
        "--xml",
        action="store_true",
        help="Generate XML coverage report (for CI integration)"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate all report formats (HTML, XML, terminal)"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only core tests for quick coverage check"
    )

    args = parser.parse_args()

    return run_coverage(
        html=args.html,
        xml=args.xml,
        full=args.full,
        quick=args.quick
    )


if __name__ == "__main__":
    sys.exit(main())
