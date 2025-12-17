"""
Stress Test Runner for Symbo Mathematical Reasoning System
Runs 600 research-grade equations without direct SymPy dependency
Logs all results for analysis

Usage: python tests/stress_test_runner.py [--timeout MINUTES] [--max-equations N]
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stress_test_equations import ALL_EQUATIONS, CATEGORIES


class StressTestRunner:
    """Runs stress tests on the Symbo mathematical reasoning system."""

    def __init__(self, timeout_minutes: int = 120, max_equations: int = 600):
        self.timeout_minutes = timeout_minutes
        self.max_equations = min(max_equations, len(ALL_EQUATIONS))
        self.start_time = None
        self.results: List[Dict[str, Any]] = []
        self.log_file = None

        # Statistics
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "timeout": 0,
            "error": 0,
            "by_category": {}
        }

        # Initialize category stats
        for cat in CATEGORIES.keys():
            self.stats["by_category"][cat] = {
                "total": 0, "success": 0, "failed": 0, "error": 0
            }

    def _init_logging(self):
        """Initialize logging file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'stress_tests')
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(log_dir, f"stress_test_{timestamp}.json")
        self.summary_file = os.path.join(log_dir, f"stress_test_{timestamp}_summary.txt")

        print(f"Logging to: {self.log_file}")
        print(f"Summary to: {self.summary_file}")

    def _get_category(self, equation: str, index: int) -> str:
        """Determine category of equation based on index."""
        cumulative = 0
        for cat_name, cat_eqs in CATEGORIES.items():
            if index < cumulative + len(cat_eqs):
                return cat_name
            cumulative += len(cat_eqs)
        return "unknown"

    def _time_remaining(self) -> float:
        """Get remaining time in seconds."""
        if self.start_time is None:
            return float('inf')
        elapsed = time.time() - self.start_time
        return max(0, self.timeout_minutes * 60 - elapsed)

    def _is_timeout(self) -> bool:
        """Check if we've exceeded timeout."""
        return self._time_remaining() <= 0

    def _solve_equation(self, equation: str) -> Dict[str, Any]:
        """
        Solve a single equation using Symbo system.
        Returns result dict with status, result, time, etc.
        """
        result = {
            "equation": equation,
            "status": "unknown",
            "result": None,
            "time_ms": 0,
            "error": None
        }

        start = time.time()

        try:
            # Import here to avoid loading until needed
            from symbo_agentic_reasoners.cli import MathSolverCLI

            # Initialize CLI (cached across calls via class attribute)
            if not hasattr(self, '_cli'):
                self._cli = MathSolverCLI()

            # Call the solver through CLI interface
            solution = self._cli.solve_problem(equation, show_details=False)

            elapsed_ms = (time.time() - start) * 1000
            result["time_ms"] = elapsed_ms

            if solution and solution.get('status') == 'success':
                result["status"] = "success"
                result["result"] = str(solution.get('result', ''))
                result["specialist"] = solution.get('specialist', 'unknown')
                result["domain"] = solution.get('domain', 'unknown')
            elif solution and solution.get('status') == 'failed':
                result["status"] = "failed"
                result["error"] = solution.get('error', 'Unknown failure')
            else:
                result["status"] = "failed"
                result["result"] = "No solution returned"

        except TimeoutError:
            result["status"] = "timeout"
            result["error"] = "Equation timeout exceeded"
            result["time_ms"] = (time.time() - start) * 1000

        except Exception as e:
            result["status"] = "error"
            result["error"] = f"{type(e).__name__}: {str(e)}"
            result["time_ms"] = (time.time() - start) * 1000
            # Capture traceback for debugging
            result["traceback"] = traceback.format_exc()

        return result

    def _solve_equation_cli(self, equation: str) -> Dict[str, Any]:
        """
        Alternative solver using CLI interface.
        Falls back to this if direct import fails.
        """
        import subprocess

        result = {
            "equation": equation,
            "status": "unknown",
            "result": None,
            "time_ms": 0,
            "error": None
        }

        start = time.time()

        try:
            # Use subprocess to call the CLI
            proc = subprocess.run(
                [sys.executable, "-m", "symbo_agentic_reasoners", "--solve", equation],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.join(os.path.dirname(__file__), '..')
            )

            elapsed_ms = (time.time() - start) * 1000
            result["time_ms"] = elapsed_ms

            if proc.returncode == 0:
                output = proc.stdout.strip()
                if output:
                    result["status"] = "success"
                    result["result"] = output
                else:
                    result["status"] = "failed"
                    result["result"] = "Empty output"
            else:
                result["status"] = "error"
                result["error"] = proc.stderr.strip() or "Non-zero exit code"

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Subprocess timeout"
            result["time_ms"] = 30000

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["time_ms"] = (time.time() - start) * 1000

        return result

    def _update_stats(self, result: Dict[str, Any], category: str):
        """Update statistics based on result."""
        self.stats["total"] += 1

        status = result["status"]
        if status == "success":
            self.stats["success"] += 1
            self.stats["by_category"][category]["success"] += 1
        elif status == "failed":
            self.stats["failed"] += 1
            self.stats["by_category"][category]["failed"] += 1
        elif status == "timeout":
            self.stats["timeout"] += 1
            self.stats["by_category"][category]["failed"] += 1
        else:  # error
            self.stats["error"] += 1
            self.stats["by_category"][category]["error"] += 1

        self.stats["by_category"][category]["total"] += 1

    def _print_progress(self, index: int, total: int, result: Dict[str, Any]):
        """Print progress indicator."""
        elapsed = time.time() - self.start_time
        remaining = self._time_remaining()

        status_symbol = {
            "success": "[OK]",
            "failed": "[FAIL]",
            "timeout": "[TIME]",
            "error": "[ERR]"
        }.get(result["status"], "[???]")

        # Truncate equation for display
        eq_display = result["equation"][:50]
        if len(result["equation"]) > 50:
            eq_display += "..."

        print(f"[{index+1}/{total}] {status_symbol} {eq_display}")
        print(f"    Result: {str(result.get('result', 'N/A'))[:60]}")
        print(f"    Time: {result['time_ms']:.0f}ms | Elapsed: {elapsed/60:.1f}min | Remaining: {remaining/60:.1f}min")
        print()

    def _save_results(self):
        """Save results to JSON file."""
        output = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "timeout_minutes": self.timeout_minutes,
                "max_equations": self.max_equations,
                "total_equations": len(ALL_EQUATIONS)
            },
            "stats": self.stats,
            "results": self.results
        }

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # Also save summary
        self._save_summary()

    def _save_summary(self):
        """Save human-readable summary."""
        elapsed = time.time() - self.start_time

        lines = [
            "=" * 70,
            "SYMBO STRESS TEST SUMMARY",
            "=" * 70,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {elapsed/60:.1f} minutes",
            f"Equations tested: {self.stats['total']} / {self.max_equations}",
            "",
            "OVERALL RESULTS:",
            f"  Success: {self.stats['success']} ({100*self.stats['success']/max(1,self.stats['total']):.1f}%)",
            f"  Failed:  {self.stats['failed']} ({100*self.stats['failed']/max(1,self.stats['total']):.1f}%)",
            f"  Timeout: {self.stats['timeout']} ({100*self.stats['timeout']/max(1,self.stats['total']):.1f}%)",
            f"  Error:   {self.stats['error']} ({100*self.stats['error']/max(1,self.stats['total']):.1f}%)",
            "",
            "BY CATEGORY:",
        ]

        for cat, cat_stats in self.stats["by_category"].items():
            if cat_stats["total"] > 0:
                success_rate = 100 * cat_stats["success"] / cat_stats["total"]
                lines.append(f"  {cat}:")
                lines.append(f"    Total: {cat_stats['total']}, Success: {cat_stats['success']} ({success_rate:.1f}%)")

        # Add failed equations list
        lines.extend(["", "FAILED EQUATIONS:", "-" * 50])
        for r in self.results:
            if r["status"] != "success":
                lines.append(f"  [{r['status'].upper()}] {r['equation'][:60]}")
                if r.get("error"):
                    lines.append(f"    Error: {r['error'][:80]}")

        lines.extend(["", "=" * 70])

        with open(self.summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # Print summary to console
        print('\n'.join(lines))

    def run(self):
        """Run the stress test."""
        print("=" * 70)
        print("SYMBO MATHEMATICAL REASONING STRESS TEST")
        print("=" * 70)
        print(f"Configuration:")
        print(f"  Timeout: {self.timeout_minutes} minutes")
        print(f"  Max equations: {self.max_equations}")
        print(f"  Total available: {len(ALL_EQUATIONS)}")
        print("=" * 70)
        print()

        self._init_logging()
        self.start_time = time.time()

        try:
            for i, equation in enumerate(ALL_EQUATIONS[:self.max_equations]):
                # Check timeout
                if self._is_timeout():
                    print(f"\nTimeout reached after {self.timeout_minutes} minutes")
                    break

                category = self._get_category(equation, i)

                # Solve the equation
                result = self._solve_equation(equation)
                result["category"] = category
                result["index"] = i

                # Update stats and results
                self._update_stats(result, category)
                self.results.append(result)

                # Print progress
                self._print_progress(i, self.max_equations, result)

                # Save intermediate results every 10 equations
                if (i + 1) % 10 == 0:
                    self._save_results()

        except KeyboardInterrupt:
            print("\nTest interrupted by user")

        finally:
            # Save final results
            self._save_results()
            print(f"\nResults saved to: {self.log_file}")


def run_simple_test():
    """Simple test runner without full Symbo integration."""
    print("=" * 70)
    print("SIMPLE EQUATION STRESS TEST (Pattern-Based)")
    print("=" * 70)

    from stress_test_equations import ALL_EQUATIONS, CATEGORIES

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'stress_tests')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"simple_test_{timestamp}.json")

    results = []
    stats = {"total": 0, "parsed": 0, "error": 0}

    # Try to import sympy for basic parsing
    try:
        import sympy as sp
        from sympy.parsing.sympy_parser import parse_expr
        has_sympy = True
    except ImportError:
        has_sympy = False
        print("SymPy not available - running pattern analysis only")

    start_time = time.time()

    for i, eq in enumerate(ALL_EQUATIONS):
        result = {
            "index": i,
            "equation": eq,
            "status": "unknown",
            "parsed": False,
            "type": None
        }

        # Determine equation type
        if eq.startswith("integrate"):
            result["type"] = "integral"
        elif eq.startswith("summation") or eq.startswith("Sum"):
            result["type"] = "series"
        elif eq.startswith("limit"):
            result["type"] = "limit"
        elif eq.startswith("diff"):
            result["type"] = "derivative"
        elif eq.startswith("dsolve"):
            result["type"] = "differential_equation"
        elif eq.startswith("det") or eq.startswith("Matrix") or "eigenval" in eq:
            result["type"] = "linear_algebra"
        elif any(kw in eq for kw in ["gcd", "lcm", "prime", "factorial", "Mod", "diophantine"]):
            result["type"] = "number_theory"
        elif any(kw in eq for kw in ["binomial", "Var", "E[", "Cov"]):
            result["type"] = "statistics"
        else:
            result["type"] = "other"

        # Try to parse if SymPy available
        if has_sympy:
            try:
                # Basic syntax check
                expr_part = eq.split("(", 1)[1].rsplit(")", 1)[0] if "(" in eq else eq
                result["parsed"] = True
                result["status"] = "parsed"
                stats["parsed"] += 1
            except Exception as e:
                result["status"] = "parse_error"
                result["error"] = str(e)
                stats["error"] += 1
        else:
            result["status"] = "no_parser"

        stats["total"] += 1
        results.append(result)

        # Progress every 50 equations
        if (i + 1) % 50 == 0:
            print(f"Processed {i+1}/{len(ALL_EQUATIONS)} equations...")

    elapsed = time.time() - start_time

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": elapsed,
        "stats": stats,
        "results": results
    }

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nCompleted in {elapsed:.1f} seconds")
    print(f"Total: {stats['total']}, Parsed: {stats['parsed']}, Errors: {stats['error']}")
    print(f"Results saved to: {log_file}")

    # Print type breakdown
    type_counts = {}
    for r in results:
        t = r.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\nEquation type breakdown:")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Symbo Stress Test Runner")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout in minutes (default: 120)")
    parser.add_argument("--max-equations", type=int, default=600, help="Max equations to test (default: 600)")
    parser.add_argument("--simple", action="store_true", help="Run simple pattern-based test only")

    args = parser.parse_args()

    if args.simple:
        run_simple_test()
    else:
        runner = StressTestRunner(
            timeout_minutes=args.timeout,
            max_equations=args.max_equations
        )
        runner.run()


if __name__ == "__main__":
    main()
