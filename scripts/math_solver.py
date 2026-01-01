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
Math Solver CLI
================

Main entry point for the SYMBO_AGENTIC_REASONERS system.

Usage:
    Interactive mode (chat):
        python scripts/math_solver.py

    Batch mode (document):
        python scripts/math_solver.py --batch problems.txt
        python scripts/math_solver.py --batch problems.txt --output results.json

Features:
- Full solver integration with SymPy-powered specialist agents
- Hardware monitoring (CPU, RAM, disk)
- Automatic agent activation/deactivation
- Automatic partitioning strategy selection
- Graceful shutdown with Ctrl+C (saves state)
- Resume from previous session
"""

import sys
import os
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.core.resource_coordinator import (
    ResourceCoordinator, get_coordinator, shutdown_coordinator
)
from symbo_agentic_reasoners.core.solver_engine import (
    SolverEngine, SolveResult, SolveStatus, get_solver_engine
)
from symbo_agentic_reasoners.discovery.curiosity_engine import (
    CuriosityEngine, ExplorationCategory, InterestLevel
)


BANNER = """
================================================================================
     SYMBO AGENTIC REASONERS - Mathematical Discovery Engine
================================================================================
     Version: 0.6.0
     Mode: {mode}

     Commands:
       - Type a math problem to solve
       - 'status'    - Show system & hardware status
       - 'hardware'  - Show detailed hardware metrics
       - 'explore'   - Start autonomous exploration (learns math on its own!)
       - 'explore N' - Explore for N seconds
       - 'discover'  - Show recent discoveries
       - 'help'      - Show help
       - 'quit'      - Exit (saves state)

     Press Ctrl+C at any time to save and exit gracefully.
================================================================================
"""


class MathSolverCLI:
    """
    Interactive and batch CLI for solving mathematical problems.

    Handles:
    - Interactive chat mode for single problems
    - Batch mode for processing documents
    - Graceful shutdown with state persistence
    - Automatic resource management
    - Hardware monitoring and status display
    """

    def __init__(self):
        self.coordinator = get_coordinator()
        self.solver = get_solver_engine(self.coordinator)
        self.results: List[Dict[str, Any]] = []
        self.session_start = datetime.now()
        self.curiosity_engine: Optional[CuriosityEngine] = None
        self._idle_exploration_active = False

    def _init_curiosity_engine(self):
        """Initialize the curiosity engine for autonomous exploration."""
        if self.curiosity_engine is None:
            self.curiosity_engine = CuriosityEngine(
                solver=self.solver,
                save_dir=Path(__file__).parent.parent / "data" / "curiosity"
            )
        return self.curiosity_engine

    def run_interactive(self):
        """Run interactive chat mode."""
        print(BANNER.format(mode="Interactive"))

        self.coordinator.start()

        # Show initial hardware status
        self._show_hardware_brief()

        # SECURITY: Input limits
        MAX_INPUT_LENGTH = 10000

        try:
            while not self.coordinator.is_shutdown_requested():
                try:
                    # Get input
                    user_input = input("\n[math]> ").strip()

                    if not user_input:
                        continue

                    # SECURITY: Enforce input length limit
                    if len(user_input) > MAX_INPUT_LENGTH:
                        print(f"Error: Input too long ({len(user_input)} chars). Max: {MAX_INPUT_LENGTH}")
                        continue

                    # Handle commands
                    cmd = user_input.lower()
                    if cmd == 'quit':
                        break
                    elif cmd == 'status':
                        self._show_status()
                        continue
                    elif cmd == 'hardware':
                        self._show_hardware_detailed()
                        continue
                    elif cmd == 'help':
                        self._show_help()
                        continue
                    elif cmd.startswith('explore'):
                        # Parse duration if provided: "explore 60" means 60 seconds
                        parts = cmd.split()
                        duration = 30  # default
                        if len(parts) > 1:
                            try:
                                duration = int(parts[1])
                            except ValueError:
                                pass
                        self._run_exploration(duration)
                        continue
                    elif cmd == 'discover' or cmd == 'discoveries':
                        self._show_discoveries()
                        continue

                    # Process math problem
                    self._process_problem(user_input)

                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n")
                    break

        finally:
            self._shutdown()

    def run_batch(self, input_file: Path, output_file: Optional[Path] = None):
        """
        Run batch mode on a document.

        Args:
            input_file: Path to file with problems (one per line or separated by blank lines)
            output_file: Optional path for JSON results
        """
        print(BANNER.format(mode=f"Batch: {input_file.name}"))

        if not input_file.exists():
            print(f"Error: File not found: {input_file}")
            return

        # Parse problems from file
        problems = self._parse_problems_file(input_file)
        print(f"Found {len(problems)} problems to solve.\n")

        if not problems:
            print("No problems found in file.")
            return

        self.coordinator.start()

        # Add all problems to queue
        for problem in problems:
            self.coordinator.add_pending_problem(problem)

        try:
            solved = 0
            total = len(problems)

            while not self.coordinator.is_shutdown_requested():
                problem = self.coordinator.get_next_problem()
                if problem is None:
                    break

                solved += 1
                print(f"[{solved}/{total}] Processing...")
                print(f"  Problem: {problem[:80]}{'...' if len(problem) > 80 else ''}")

                result = self._process_problem(problem, verbose=False)
                self.results.append(result)

                self.coordinator.mark_problem_completed(result.get('success', False))

                # Check for shutdown
                if self.coordinator.is_shutdown_requested():
                    print("\nShutdown requested. Saving progress...")
                    break

            # Summary
            print("\n" + "=" * 60)
            print("BATCH COMPLETE")
            print("=" * 60)
            print(f"Solved: {len(self.results)}/{total}")
            success_count = sum(1 for r in self.results if r.get('success'))
            print(f"Success: {success_count}")
            print(f"Failed: {len(self.results) - success_count}")

            # Save results
            if output_file:
                self._save_results(output_file)
            else:
                default_output = input_file.with_suffix('.results.json')
                self._save_results(default_output)

        finally:
            self._shutdown()

    def _process_problem(self, problem: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Process a single math problem using the solver engine.

        Args:
            problem: The math problem text
            verbose: Whether to print detailed output

        Returns:
            Result dictionary
        """
        result = {
            'problem': problem,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'solution': None,
            'error': None,
            'metadata': {}
        }

        try:
            if verbose:
                print(f"\nProcessing: {problem}")

            # Use solver engine for actual solving
            solve_result = self.solver.solve(problem)

            if solve_result.status == SolveStatus.SUCCESS:
                result['success'] = True
                result['solution'] = solve_result.result
                result['metadata'] = {
                    'domain': solve_result.domain,
                    'operation': solve_result.operation,
                    'specialist': solve_result.specialist_used,
                    'solve_time_ms': solve_result.solve_time_ms
                }

                if verbose:
                    print(f"Solution: {solve_result.result}")
                    print(f"  ({solve_result.operation} via {solve_result.specialist_used}, "
                          f"{solve_result.solve_time_ms:.1f}ms)")

            else:
                result['error'] = solve_result.error or "Unknown error"
                if verbose:
                    print(f"Error: {result['error']}")

        except Exception as e:
            result['error'] = str(e)
            if verbose:
                print(f"Error: {e}")

        self.results.append(result)
        return result

    def _solve_problem(self, problem: str) -> str:
        """
        Solve a math problem using the solver engine.

        This is the direct solve path that uses:
        1. Problem analysis (parse and classify)
        2. Specialist dispatch (route to correct agent)
        3. SymPy computation (solve)
        """
        solve_result = self.solver.solve(problem)

        if solve_result.status == SolveStatus.SUCCESS:
            return solve_result.result
        else:
            raise RuntimeError(solve_result.error or "Solve failed")

    def _parse_problems_file(self, file_path: Path) -> List[str]:
        """
        Parse problems from a file.

        Supports:
        - One problem per line
        - Problems separated by blank lines
        - Numbered problems (1. problem, 2. problem)
        - Problems after "Problem:" header
        """
        problems = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to detect format

        # Format 1: Numbered problems
        numbered = re.findall(r'^\s*\d+[.)]\s*(.+?)(?=\n\s*\d+[.)]|\Z)', content, re.MULTILINE | re.DOTALL)
        if numbered:
            problems = [p.strip() for p in numbered if p.strip()]
            return problems

        # Format 2: "Problem:" headers
        headers = re.findall(r'Problem[:\s]+(.+?)(?=Problem[:\s]|\Z)', content, re.IGNORECASE | re.DOTALL)
        if headers:
            problems = [p.strip() for p in headers if p.strip()]
            return problems

        # Format 3: Separated by blank lines
        blocks = content.split('\n\n')
        if len(blocks) > 1:
            problems = [b.strip() for b in blocks if b.strip() and len(b.strip()) > 5]
            return problems

        # Format 4: One per line
        lines = content.strip().split('\n')
        problems = [line.strip() for line in lines if line.strip() and len(line.strip()) > 3]

        return problems

    def _show_status(self):
        """Show system status including hardware."""
        stats = self.coordinator.get_statistics()
        solver_stats = self.solver.get_statistics()

        print("\n" + "=" * 50)
        print("SYSTEM STATUS")
        print("=" * 50)

        # System state
        print(f"\nSystem: {'Running' if stats['running'] else 'Stopped'}")
        print(f"Agents: {stats['agents']['active']} active, {stats['agents']['standby']} standby")
        print(f"Problems: {stats['problems']['completed']} completed, {stats['problems']['pending']} pending")

        # Solver stats
        print(f"\nSolver: {solver_stats['problems_solved']}/{solver_stats['total_problems']} "
              f"({solver_stats['success_rate']:.1f}% success)")
        if solver_stats['avg_solve_time_ms'] > 0:
            print(f"Avg solve time: {solver_stats['avg_solve_time_ms']:.1f}ms")

        # Hardware metrics
        if 'hardware' in stats:
            hw = stats['hardware']
            print(f"\nHardware:")
            print(f"  CPU:    {hw['cpu_percent']:5.1f}%  | Process: {hw['process_cpu_percent']:.1f}%")
            print(f"  Memory: {hw['memory_percent']:5.1f}%  | Process: {hw['process_memory_mb']:.0f}MB")
            print(f"  Disk:   {hw['disk_percent']:5.1f}%  | Free: {hw['disk_free_gb']:.1f}GB")

            # Warnings
            warnings = stats.get('hardware_warnings', [])
            if warnings:
                print(f"\nWarnings:")
                for w in warnings:
                    print(f"  ! {w}")

        # Partition strategy
        partition_info = stats.get('partition_strategy', {})
        if partition_info.get('strategy'):
            print(f"\nPartition: {partition_info['strategy']}")
            if partition_info.get('reason'):
                print(f"  Reason: {partition_info['reason']}")

        print("=" * 50)

    def _show_hardware_brief(self):
        """Show brief hardware status on startup."""
        metrics = self.coordinator.get_hardware_metrics()
        if metrics:
            print(f"\nHardware: CPU {metrics.cpu_percent:.0f}% | "
                  f"RAM {metrics.memory_percent:.0f}% | "
                  f"Disk {metrics.disk_percent:.0f}%")

    def _show_hardware_detailed(self):
        """Show detailed hardware status."""
        status = self.coordinator.get_hardware_status()
        metrics = status['metrics']

        print("\n" + "=" * 50)
        print("HARDWARE STATUS")
        print("=" * 50)

        # Progress bars
        def bar(pct, width=20):
            filled = int(pct / 100 * width)
            return "█" * filled + "░" * (width - filled)

        print(f"\nCPU:     {metrics['cpu_percent']:5.1f}% {bar(metrics['cpu_percent'])}")
        print(f"Memory:  {metrics['memory_percent']:5.1f}% {bar(metrics['memory_percent'])}")
        print(f"  Used:  {metrics['memory_used_mb']:.0f} MB")
        print(f"  Avail: {metrics['memory_available_mb']:.0f} MB")
        print(f"Disk:    {metrics['disk_percent']:5.1f}% {bar(metrics['disk_percent'])}")
        print(f"  Free:  {metrics['disk_free_gb']:.1f} GB")

        print(f"\nProcess:")
        print(f"  CPU:   {metrics['process_cpu_percent']:.1f}%")
        print(f"  RAM:   {metrics['process_memory_mb']:.0f} MB")

        # Status
        print(f"\nCan proceed: {'Yes' if status['can_proceed'] else 'NO'}")

        # Warnings
        if status['warnings']:
            print(f"\nWarnings:")
            for w in status['warnings']:
                print(f"  ! {w}")

        # Recommendations
        if status['recommendations']:
            print(f"\nRecommendations:")
            for r in status['recommendations']:
                print(f"  → {r}")

        print("=" * 50)

    def _show_help(self):
        """Show help message."""
        print("""
Math Solver Help
----------------

Input:
  Type any mathematical expression or problem, e.g.:
    - derivative of x^2 + 3x
    - integrate sin(x)
    - solve x^2 - 5x + 6 = 0
    - factor x^3 - 1
    - expand (x + 1)^3
    - simplify x^2/x

Supported Operations:
  - derivative/diff: Compute derivatives
  - integrate:       Compute integrals
  - solve:           Solve equations
  - factor:          Factor polynomials
  - expand:          Expand expressions
  - simplify:        Simplify expressions
  - limit:           Evaluate limits
  - series:          Taylor series expansion

Commands:
  status   - Show system & hardware status
  hardware - Show detailed hardware metrics
  explore  - Start autonomous exploration (default: 30s)
  explore N - Explore for N seconds
  discover - Show recent interesting discoveries
  help     - Show this help
  quit     - Exit (saves state)

Batch mode:
  python scripts/math_solver.py --batch problems.txt
  python scripts/math_solver.py --batch problems.txt --output results.json

The system automatically:
  - Activates specialist agents as needed
  - Monitors hardware resources (CPU, RAM, disk)
  - Selects optimal partitioning strategy
  - Saves state on Ctrl+C for resume

Autonomous Exploration:
  The system can explore mathematics on its own when idle!
  Use 'explore' to have it generate and solve random problems,
  learning patterns and recording interesting discoveries.
  Discoveries are persisted and can be viewed with 'discover'.
""")

    def _run_exploration(self, duration_seconds: int = 30):
        """
        Run autonomous mathematical exploration.

        Args:
            duration_seconds: How long to explore
        """
        engine = self._init_curiosity_engine()

        print(f"\n{'=' * 60}")
        print("AUTONOMOUS EXPLORATION MODE")
        print(f"{'=' * 60}")
        print(f"Duration: {duration_seconds} seconds")
        print("The system will generate and solve random math problems,")
        print("recording any interesting discoveries...")
        print("Press Ctrl+C to stop early.\n")

        try:
            discoveries = engine.explore_session(duration_seconds, verbose=True)

            # Show summary
            stats = engine.get_statistics()
            print(f"\n{'=' * 60}")
            print("EXPLORATION SUMMARY")
            print(f"{'=' * 60}")
            print(f"Total explored: {stats['problems_generated']}")
            print(f"Solved: {stats['problems_solved']} ({stats['success_rate']:.1f}%)")
            print(f"Interesting finds: {stats['interesting_discoveries']}")
            print(f"Avg solve time: {stats['avg_solve_time_ms']:.1f}ms")

            if stats['categories_explored']:
                print("\nCategories explored:")
                for cat, count in sorted(stats['categories_explored'].items(),
                                        key=lambda x: -x[1]):
                    print(f"  {cat}: {count}")

        except KeyboardInterrupt:
            print("\n\nExploration stopped by user.")

    def _show_discoveries(self, limit: int = 10):
        """Show recent interesting discoveries."""
        engine = self._init_curiosity_engine()

        print(f"\n{'=' * 60}")
        print("RECENT DISCOVERIES")
        print(f"{'=' * 60}")

        discoveries = engine.get_discoveries(
            min_interest=InterestLevel.NOTABLE,
            limit=limit
        )

        if not discoveries:
            print("No interesting discoveries yet.")
            print("Use 'explore' to start autonomous exploration!")
            return

        for i, d in enumerate(discoveries, 1):
            interest_stars = '*' * (d.interest_level.value + 1)
            print(f"\n{i}. [{interest_stars}] {d.category.value.upper()}")
            print(f"   Problem: {d.problem[:60]}{'...' if len(d.problem) > 60 else ''}")
            print(f"   Solution: {d.solution}")
            if d.notes:
                print(f"   Note: {d.notes}")
            print(f"   ({d.solve_time_ms:.1f}ms)")

        # Show stats
        stats = engine.get_statistics()
        print(f"\n{'=' * 60}")
        print(f"Total explorations: {stats['problems_generated']}")
        print(f"Total discoveries: {stats['total_discoveries']}")

    def _save_results(self, output_file: Path):
        """Save results to JSON file."""
        output = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'total_problems': len(self.results),
            'success_count': sum(1 for r in self.results if r.get('success')),
            'results': self.results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def _shutdown(self):
        """Graceful shutdown with session summary."""
        print("\n" + "-" * 50)
        print("Shutting down...")

        # Show session summary
        stats = self.coordinator.get_statistics()
        solver_stats = self.solver.get_statistics()

        print(f"\nSession Summary:")
        print(f"  Problems solved: {solver_stats['problems_solved']}")
        print(f"  Problems failed: {solver_stats['problems_failed']}")
        if solver_stats['total_problems'] > 0:
            print(f"  Success rate: {solver_stats['success_rate']:.1f}%")
            print(f"  Avg solve time: {solver_stats['avg_solve_time_ms']:.1f}ms")

        # Hardware summary
        metrics = self.coordinator.get_hardware_metrics()
        if metrics:
            print(f"\nFinal Hardware State:")
            print(f"  CPU: {metrics.cpu_percent:.1f}% | RAM: {metrics.memory_percent:.1f}%")

        shutdown_coordinator()
        print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description='SYMBO Agentic Reasoners - Math Solver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python scripts/math_solver.py

  Batch mode:
    python scripts/math_solver.py --batch problems.txt
    python scripts/math_solver.py --batch exam.txt --output exam_solutions.json
"""
    )

    parser.add_argument(
        '--batch', '-b',
        type=Path,
        help='Path to file with problems for batch processing'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for batch results (default: <input>.results.json)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from previous session'
    )

    args = parser.parse_args()

    cli = MathSolverCLI()

    if args.batch:
        cli.run_batch(args.batch, args.output)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()
