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
Test Runner for 100 LLM Killer Equations
=========================================

This script tests the symbo-agentic-reasoners solver against the
100 most difficult equations for LLMs.

Usage:
    python scripts/test_llm_killers.py [options]

Options:
    --category <name>       Test only specific category
    --difficulty <min-max>  Test only difficulty range (e.g., 9-10)
    --tag <tag>             Test only equations with specific tag
    --limit <n>             Test only first n equations
    --verbose               Show detailed output
    --save-results          Save results to JSON file
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))

from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus
from llm_killer_equations import (
    ALL_LLM_KILLER_EQUATIONS,
    get_equations_by_category,
    get_equations_by_difficulty,
    get_equations_by_tag,
    CATEGORIES
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test LLM Killer Equations against symbo solver"
    )
    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()),
        help="Test only specific category"
    )
    parser.add_argument(
        "--difficulty",
        help="Test only difficulty range (e.g., '9-10')"
    )
    parser.add_argument(
        "--tag",
        help="Test only equations with specific tag"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Test only first n equations"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Save results to JSON file"
    )
    return parser.parse_args()


def filter_equations(args):
    """Filter equations based on command line arguments."""
    equations = ALL_LLM_KILLER_EQUATIONS

    if args.category:
        equations = get_equations_by_category(args.category)

    if args.difficulty:
        try:
            min_diff, max_diff = map(int, args.difficulty.split('-'))
            equations = [eq for eq in equations
                        if min_diff <= eq["difficulty"] <= max_diff]
        except ValueError:
            print(f"Invalid difficulty range: {args.difficulty}")
            sys.exit(1)

    if args.tag:
        equations = [eq for eq in equations if args.tag in eq["tags"]]

    if args.limit:
        equations = equations[:args.limit]

    return equations


def test_equation(solver, equation, verbose=False):
    """Test a single equation and return results."""
    eq_id = equation["id"]
    expr = equation["expr"]
    expected = equation["answer"]
    difficulty = equation["difficulty"]

    if verbose:
        print(f"\n{'='*70}")
        print(f"Testing Equation #{eq_id}")
        print(f"Expression: {expr}")
        print(f"Expected: {expected}")
        print(f"Difficulty: {difficulty}/10")
        print(f"Why LLMs fail: {equation['why_fails']}")
        print(f"{'='*70}")

    try:
        start_time = time.time()
        result = solver.solve(expr)
        elapsed = time.time() - start_time

        status = result.status.name if hasattr(result, 'status') else str(result.status)
        result_str = str(result.result) if result.result else "None"

        # Determine success
        is_error = False
        if status in ["ERROR", "FAILURE"]:
            is_error = True
        elif any(word in result_str.lower() for word in ["error", "failed", "notimplementederror"]):
            is_error = True
        elif result_str in ["None", ""]:
            is_error = True

        success = not is_error

        if verbose:
            print(f"Status: {status}")
            print(f"Result: {result_str[:200]}")
            print(f"Time: {elapsed:.3f}s")
            print(f"Success: {'✓' if success else '✗'}")

        return {
            "id": eq_id,
            "expr": expr,
            "expected": expected,
            "status": status,
            "result": result_str[:500],  # Truncate long results
            "time": elapsed,
            "success": success,
            "difficulty": difficulty,
            "tags": equation["tags"],
        }

    except Exception as e:
        if verbose:
            print(f"EXCEPTION: {str(e)}")

        return {
            "id": eq_id,
            "expr": expr,
            "expected": expected,
            "status": "EXCEPTION",
            "result": str(e)[:500],
            "time": 0,
            "success": False,
            "difficulty": difficulty,
            "tags": equation["tags"],
        }


def run_tests(equations, verbose=False, save_results=False):
    """Run all tests and generate report."""
    print("="*70)
    print("TESTING 100 LLM KILLER EQUATIONS")
    print("="*70)
    print(f"Total equations to test: {len(equations)}")
    print()

    solver = get_solver_engine()
    results = []
    passed = 0
    failed = 0

    for i, equation in enumerate(equations, 1):
        if not verbose:
            print(f"[{i:3d}/{len(equations)}] Testing #{equation['id']:3d} "
                  f"(diff={equation['difficulty']}) ", end="", flush=True)

        result = test_equation(solver, equation, verbose=verbose)
        results.append(result)

        if result["success"]:
            passed += 1
            if not verbose:
                print(f"✓ ({result['time']:.2f}s)")
        else:
            failed += 1
            if not verbose:
                print(f"✗ ({result['status']})")

    # Generate summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total tested: {len(equations)}")
    print(f"Passed: {passed} ({100*passed/len(equations):.1f}%)")
    print(f"Failed: {failed} ({100*failed/len(equations):.1f}%)")
    print()

    # Statistics by difficulty
    print("By Difficulty:")
    for diff_range in ["1-3", "4-6", "7-8", "9-10"]:
        min_d, max_d = map(int, diff_range.split('-'))
        range_results = [r for r in results if min_d <= r["difficulty"] <= max_d]
        if range_results:
            range_passed = sum(1 for r in range_results if r["success"])
            range_total = len(range_results)
            print(f"  {diff_range}: {range_passed}/{range_total} "
                  f"({100*range_passed/range_total:.1f}%)")

    # Statistics by category
    print("\nBy Category:")
    for cat_name, cat_equations in CATEGORIES.items():
        cat_ids = {eq["id"] for eq in cat_equations}
        cat_results = [r for r in results if r["id"] in cat_ids]
        if cat_results:
            cat_passed = sum(1 for r in cat_results if r["success"])
            cat_total = len(cat_results)
            print(f"  {cat_name}: {cat_passed}/{cat_total} "
                  f"({100*cat_passed/cat_total:.1f}%)")

    # Show failures
    failures = [r for r in results if not r["success"]]
    if failures and not verbose:
        print(f"\n{len(failures)} FAILURES:")
        print("-"*70)
        for r in failures[:10]:  # Show first 10
            print(f"#{r['id']:3d} (diff={r['difficulty']}) {r['expr'][:50]}...")
            print(f"      Status: {r['status']}")
            print(f"      Error: {r['result'][:100]}")
            print()
        if len(failures) > 10:
            print(f"... and {len(failures) - 10} more failures")

    # Save results if requested
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llm_killer_results_{timestamp}.json"
        output = {
            "timestamp": timestamp,
            "total": len(equations),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(equations),
            "results": results,
        }
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {filename}")

    return results, passed, len(equations)


def main():
    """Main entry point."""
    args = parse_args()

    # Filter equations
    equations = filter_equations(args)

    if not equations:
        print("No equations matched the filter criteria")
        sys.exit(1)

    # Run tests
    results, passed, total = run_tests(
        equations,
        verbose=args.verbose,
        save_results=args.save_results
    )

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
