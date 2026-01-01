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
SYMBO_AGENTIC_REASONERS Full Audit Runner
======================
Runs audit tests for all phases and generates a combined report.

Usage:
    python scripts/run_all_audits.py [--phase N] [--verbose]

Options:
    --phase N    Run audit for specific phase only (0-6)
    --verbose    Show detailed test output
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_args():
    parser = argparse.ArgumentParser(description='Run SYMBO_AGENTIC_REASONERS Audits')
    parser.add_argument('--phase', type=int, choices=range(0, 7),
                        help='Run audit for specific phase only (0-6)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed test output')
    return parser.parse_args()


def run_audit(phase: int, verbose: bool = False) -> dict:
    """Run audit for a specific phase"""

    if phase == 0:
        module = "audit.audit_runner"
        name = "Phase 0: Infrastructure"
    else:
        module = f"audit.phase{phase}.audit_runner"
        name = f"Phase {phase}"

    print(f"\n{'='*60}")
    print(f"Running {name} Audit")
    print('='*60)

    try:
        # Run the audit as a subprocess
        cmd = [sys.executable, "-m", module]

        if verbose:
            result = subprocess.run(cmd, cwd=str(project_root))
        else:
            result = subprocess.run(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True
            )

        success = result.returncode == 0

        if not verbose and not success:
            print(f"STDERR: {result.stderr}")

        return {
            'phase': phase,
            'name': name,
            'success': success,
            'returncode': result.returncode
        }

    except Exception as e:
        print(f"Error running {name} audit: {e}")
        return {
            'phase': phase,
            'name': name,
            'success': False,
            'error': str(e)
        }


def generate_summary_report(results: list, output_dir: Path):
    """Generate a combined summary report"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"full_audit_report_{timestamp}.md"

    with open(report_path, 'w') as f:
        f.write("# SYMBO_AGENTIC_REASONERS Full System Audit Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")

        # Summary table
        f.write("## Summary\n\n")
        f.write("| Phase | Status | Details |\n")
        f.write("|-------|--------|--------|\n")

        passed = 0
        failed = 0

        for result in results:
            if result['success']:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1

            details = result.get('error', '')
            f.write(f"| {result['name']} | {status} | {details} |\n")

        f.write(f"\n**Total**: {passed} passed, {failed} failed\n\n")

        # Individual phase reports
        f.write("## Phase Reports\n\n")
        f.write("Individual phase reports are located in:\n\n")

        report_locations = [
            ("Phase 0", "audit/reports/"),
            ("Phase 1", "audit/phase1/reports/"),
            ("Phase 2", "audit/phase2/reports/"),
            ("Phase 3", "audit/phase3/reports/"),
            ("Phase 4", "audit/phase4/reports/"),
            ("Phase 5", "audit/phase5/reports/"),
            ("Phase 6", "audit/phase6/reports/"),
        ]

        for name, path in report_locations:
            f.write(f"- **{name}**: `{path}`\n")

    return report_path


def main():
    args = parse_args()

    print("=" * 60)
    print("SYMBO_AGENTIC_REASONERS Full System Audit")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")

    results = []

    if args.phase is not None:
        # Run single phase
        result = run_audit(args.phase, args.verbose)
        results.append(result)
    else:
        # Run all phases
        for phase in range(7):
            result = run_audit(phase, args.verbose)
            results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed

    for result in results:
        status = "PASS" if result['success'] else "FAIL"
        print(f"  [{status}] {result['name']}")

    print()
    print(f"Total: {passed} passed, {failed} failed")

    # Generate combined report
    reports_dir = project_root / "audit" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = generate_summary_report(results, reports_dir)
    print(f"\nCombined report: {report_path}")

    if failed > 0:
        print("\n[WARNING] Some audits failed. Check individual reports for details.")
        return 1
    else:
        print("\n[SUCCESS] All audits passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
