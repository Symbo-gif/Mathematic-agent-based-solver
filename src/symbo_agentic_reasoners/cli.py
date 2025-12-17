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
SYMBO AGENTIC REASONERS - Command Line Interface
=================================================

Interactive CLI for the Mathematical Agent-Based Solver system.

Features:
- Interactive problem solving (type individual math problems)
- Batch processing from files or folders
- System status monitoring (CPU, GPU, RAM)
- Emergency shutdown controls

Color Theme:
- Gold: Primary text, highlights, success
- Teal: Info, system messages, prompts
- Vibrant Green: Success indicators
- Blood Red: Errors

Usage:
    python -m symbo_agentic_reasoners.cli                    # Interactive mode
    python -m symbo_agentic_reasoners.cli solve "2+2"        # Single problem
    python -m symbo_agentic_reasoners.cli batch ./problems/  # Process folder
    python -m symbo_agentic_reasoners.cli status             # System status
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('symbo_agentic_reasoners.cli')

# Import terminal colors
from symbo_agentic_reasoners.utils.terminal_colors import (
    C, gold, teal, green, red, info, success, error, warning, dim, bold,
    format_ok, format_error, format_info, format_init, format_batch, format_warn,
    format_prompt, format_result_success, format_result_failure,
    format_banner, format_divider, COLORS_ENABLED
)


class MathSolverCLI:
    """
    Command Line Interface for the Mathematical Agent-Based Solver.

    Provides interactive and batch modes for solving mathematical problems
    using the 65-agent multi-phase architecture.

    Color Theme:
    - Gold: Primary text, highlights, results
    - Teal: Info, system messages, prompts
    - Vibrant Green: Success checkmarks
    - Blood Red: Errors
    """

    # Banner constant for test compatibility
    BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SYMBO AGENTIC MATHEMATICAL REASONER                       ║
║                     Multi-Agent Discovery Engine v0.6.0                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def get_banner() -> str:
        """Get the formatted banner with colors."""
        return format_banner()

    def __init__(self):
        """Initialize the CLI with lazy-loaded system components."""
        self._system = None
        self._solver = None
        self._coordinator = None
        self._initialized = False

    def _initialize_system(self, verbose: bool = True):
        """
        Lazy initialization of the full system.

        This bootstraps all 65 agents across 6 phases.
        """
        if self._initialized:
            return

        if verbose:
            print(format_init("Bootstrapping Mathematical Agent System..."))
            print(teal("       This may take a moment on first run.\n"))

        try:
            # Import system components
            from symbo_agentic_reasoners.core.system import Phase0System, Phase2System
            from symbo_agentic_reasoners.core.solver_engine import SolverEngine, get_solver_engine
            from symbo_agentic_reasoners.core.resource_coordinator import get_coordinator

            # Initialize resource coordinator for hardware monitoring
            self._coordinator = get_coordinator()

            # Get or create solver engine
            self._solver = get_solver_engine()

            # Initialize Phase 0 infrastructure
            self._system = Phase0System()
            self._system.start()

            # Initialize Phase 2 agents (mathematical workforce)
            self._phase2 = Phase2System(phase0_system=self._system)
            self._phase2.start()

            self._initialized = True

            if verbose:
                stats = self._phase2.get_statistics()
                print(format_ok("System initialized successfully!"))
                print(gold(f"     Agents registered: ") + teal(f"{stats.get('agents_registered', 'N/A')}"))
                print(gold(f"     Teams active: ") + teal(f"{stats.get('teams_active', 'N/A')}"))
                print()

        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            if verbose:
                print(format_error(f"Failed to initialize system: {e}"))
                print(red("        Some features may be limited.\n"))
            # Continue with limited functionality
            self._initialized = True

    def solve_problem(self, problem: str, show_details: bool = False) -> Dict[str, Any]:
        """
        Solve a single mathematical problem.

        Args:
            problem: The mathematical problem as a string
            show_details: Whether to show detailed solution steps

        Returns:
            Dictionary with solution result
        """
        self._initialize_system(verbose=False)

        start_time = time.time()

        try:
            if self._solver:
                result = self._solver.solve(problem)
                solve_time = (time.time() - start_time) * 1000

                return {
                    'status': result.status.value,
                    'result': result.result,
                    'problem_type': result.problem_type,
                    'domain': result.domain,
                    'specialist': result.specialist_used,
                    'time_ms': round(solve_time, 2),
                    'error': result.error
                }
            else:
                # Fallback to native symbolic engine
                from symbo_agentic_reasoners.core.native_symbolic import sympify, simplify
                try:
                    # Try to parse and evaluate using native engine
                    expr = sympify(problem)
                    result = simplify(expr)
                    solve_time = (time.time() - start_time) * 1000

                    return {
                        'status': 'success',
                        'result': str(result),
                        'problem_type': 'expression',
                        'domain': 'algebra',
                        'specialist': 'native_symbolic',
                        'time_ms': round(solve_time, 2),
                        'error': None
                    }
                except Exception as e:
                    return {
                        'status': 'failed',
                        'result': None,
                        'error': str(e),
                        'time_ms': round((time.time() - start_time) * 1000, 2)
                    }

        except Exception as e:
            return {
                'status': 'failed',
                'result': None,
                'error': str(e),
                'time_ms': round((time.time() - start_time) * 1000, 2)
            }

    def interactive_mode(self):
        """
        Run the interactive REPL mode.

        Users can type math problems and get solutions in real-time.
        """
        print(self.get_banner())
        print(gold("Type a math problem and press Enter to solve."))
        print(teal("Commands: ") + gold(":status") + teal(", ") + gold(":help") + teal(", ") + gold(":quit") + teal(", ") + gold(":batch <path>"))
        print(format_divider())
        print()

        self._initialize_system(verbose=True)

        while True:
            try:
                # Get user input with colored prompt
                user_input = input(format_prompt()).strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith(':'):
                    self._handle_command(user_input)
                    continue

                # Solve the problem
                print()
                result = self.solve_problem(user_input, show_details=True)
                self._display_result(user_input, result)
                print()

            except KeyboardInterrupt:
                print("\n" + format_info("Use :quit to exit gracefully."))
            except EOFError:
                print("\n" + format_info("Goodbye!"))
                break

    def _handle_command(self, command: str):
        """Handle CLI commands starting with ':'"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == ':quit' or cmd == ':q' or cmd == ':exit':
            print("\n" + format_info("Shutting down system..."))
            self._shutdown()
            print(format_info("Goodbye!"))
            sys.exit(0)

        elif cmd == ':help' or cmd == ':h':
            self._show_help()

        elif cmd == ':status' or cmd == ':s':
            self._show_status()

        elif cmd == ':batch' or cmd == ':b':
            if args:
                self.batch_process(args)
            else:
                print(format_error("Usage: :batch <path_to_folder_or_file>"))

        elif cmd == ':clear' or cmd == ':c':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.get_banner())

        elif cmd == ':agents':
            self._show_agents()

        elif cmd == ':emergency':
            self._emergency_shutdown()

        else:
            print(format_error(f"Unknown command: {cmd}"))
            print(teal("        Type :help for available commands."))

    def _show_help(self):
        """Display help information."""
        print()
        print(gold("Available Commands:"))
        print(teal("─" * 65))
        print(f"  {gold(':help, :h')}       {teal('Show this help message')}")
        print(f"  {gold(':status, :s')}     {teal('Show system status (CPU, GPU, RAM, agents)')}")
        print(f"  {gold(':batch <path>')}   {teal('Process a folder or file of math problems')}")
        print(f"  {gold(':agents')}         {teal('List all registered agents')}")
        print(f"  {gold(':clear, :c')}      {teal('Clear the screen')}")
        print(f"  {gold(':emergency')}      {red('Emergency shutdown (kills all agents)')}")
        print(f"  {gold(':quit, :q')}       {teal('Exit the program')}")
        print()
        print(gold("Problem Input:"))
        print(teal("─" * 65))
        print(teal("  Just type any mathematical expression or problem:"))
        print()
        print(dim("  Examples:"))
        print(f"    {gold('2 + 2')}                          {teal('Simple arithmetic')}")
        print(f"    {gold('solve(x**2 - 4, x)')}             {teal('Equation solving')}")
        print(f"    {gold('diff(sin(x), x)')}                {teal('Differentiation')}")
        print(f"    {gold('integrate(x**2, x)')}             {teal('Integration')}")
        print(f"    {gold('limit(sin(x)/x, x, 0)')}          {teal('Limits')}")
        print(f"    {gold('Matrix([[1,2],[3,4]]).det()')}    {teal('Linear algebra')}")
        print(f"    {gold('factorial(10)')}                  {teal('Combinatorics')}")
        print()
        print(dim("  Natural language (experimental):"))
        print(f"    {gold('\"Find the derivative of x^2\"')}")
        print(f"    {gold('\"Solve x squared equals 9\"')}")
        print()

    def _show_status(self):
        """Display system status including hardware metrics."""
        print()
        print(gold("=" * 60))
        print(gold("SYSTEM STATUS"))
        print(gold("=" * 60))

        # Hardware status
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()

            print(f"\n  {gold('CPU Usage:')}    {teal(f'{cpu_percent:5.1f}%')}")
            print(f"  {gold('RAM Usage:')}    {teal(f'{memory.percent:5.1f}%')} ({memory.used // (1024**3)}/{memory.total // (1024**3)} GB)")

            # Try to get GPU info
            try:
                import subprocess
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split(', ')
                    if len(parts) >= 3:
                        print(f"  {gold('GPU Usage:')}    {teal(f'{parts[0]:>5}%')}")
                        print(f"  {gold('VRAM Usage:')}   {teal(f'{int(parts[1]):>5}/{int(parts[2])} MB')}")
            except (subprocess.SubprocessError, OSError, ValueError, IndexError):
                print(f"  {gold('GPU:')}          {dim('N/A (nvidia-smi not available)')}")

        except ImportError:
            print("\n  " + dim("[psutil not installed - hardware stats unavailable]"))

        # System status
        if self._initialized and self._system:
            try:
                health = self._system.health_check()
                status = green('✓ Running') if health.get('overall') else red('✗ Stopped')
                print(f"\n  {gold('Phase 0:')}      {status}")

                if hasattr(self, '_phase2') and self._phase2:
                    stats = self._phase2.get_statistics()
                    status = green('✓ Running') if stats else red('✗ Stopped')
                    print(f"  {gold('Phase 2:')}      {status}")
                    agents_count = stats.get('agents_registered', 0)
                    print(f"  {gold('Agents:')}       {teal(f'{agents_count} registered')}")
            except Exception:
                print(f"\n  {gold('System:')}       {dim('Status unavailable')}")
        else:
            print(f"\n  {gold('System:')}       {dim('Not initialized')}")

        print("\n" + gold("=" * 60) + "\n")

    def _show_agents(self):
        """Display list of registered agents."""
        print()
        print(gold("=" * 60))
        print(gold("REGISTERED AGENTS"))
        print(gold("=" * 60))

        if self._initialized and hasattr(self, '_phase2') and self._phase2:
            try:
                # Get agent list from DF
                df = self._system.df
                services = df.list_all_services() if hasattr(df, 'list_all_services') else []

                if services:
                    print(f"\n{gold('Total:')} {teal(f'{len(services)} agents')}\n")
                    for svc in services[:20]:  # Show first 20
                        print(f"  {teal('•')} {gold(svc)}")
                    if len(services) > 20:
                        print(dim(f"  ... and {len(services) - 20} more"))
                else:
                    print("\n  " + dim("No agents currently registered."))
            except Exception as e:
                print(format_error(f"Error listing agents: {e}"))
        else:
            print("\n  " + dim("System not initialized. Run a problem first."))

        print("\n" + gold("=" * 60) + "\n")

    def _display_result(self, problem: str, result: Dict[str, Any]):
        """Display a solution result."""
        status = result.get('status', 'unknown')

        if status == 'success':
            print(format_result_success(
                result=result.get('result', 'N/A'),
                domain=result.get('domain'),
                specialist=result.get('specialist'),
                time_ms=result.get('time_ms', 0)
            ))
        else:
            print(format_result_failure(
                error=result.get('error', 'Unknown error'),
                time_ms=result.get('time_ms', 0)
            ))

    def batch_process(self, path: str, output_path: Optional[str] = None):
        """
        Process a batch of problems from a file or folder.

        Supported formats:
        - .txt files (one problem per line)
        - .json files (array of problem strings or objects with 'problem' key)
        - Folders (processes all supported files recursively)

        Args:
            path: Path to file or folder
            output_path: Optional path for results output
        """
        print(format_batch(f"Processing: {path}"))

        self._initialize_system(verbose=True)

        path = Path(path)

        if not path.exists():
            print(format_error(f"Path does not exist: {path}"))
            return

        problems = []

        if path.is_file():
            problems = self._load_problems_from_file(path)
        elif path.is_dir():
            print(format_info("Scanning folder for problem files..."))
            for file_path in path.rglob('*'):
                if file_path.suffix.lower() in ['.txt', '.json', '.md']:
                    file_problems = self._load_problems_from_file(file_path)
                    for p in file_problems:
                        p['source_file'] = str(file_path)
                    problems.extend(file_problems)

        if not problems:
            print(format_error("No problems found in the specified path."))
            return

        print(format_info(f"Found {len(problems)} problems to solve.\n"))

        results = []
        success_count = 0

        for i, problem_data in enumerate(problems, 1):
            if isinstance(problem_data, str):
                problem = problem_data
                source = "input"
            else:
                problem = problem_data.get('problem', str(problem_data))
                source = problem_data.get('source_file', 'input')

            print(teal(f"[{i}/{len(problems)}]") + " " + gold(f"{problem[:50]}{'...' if len(problem) > 50 else ''}"))

            result = self.solve_problem(problem)
            result['original_problem'] = problem
            result['source'] = source
            results.append(result)

            if result.get('status') == 'success':
                success_count += 1
                print(f"        {green('✓')} {gold(result.get('result', 'OK'))}")
            else:
                print(f"        {red('✗')} {red(result.get('error', 'Failed'))}")

        # Summary
        print()
        print(gold("=" * 60))
        print(gold("BATCH COMPLETE: ") + green(f"{success_count}") + gold("/") + teal(f"{len(problems)}") + gold(" solved successfully"))
        print(gold("=" * 60))

        # Save results
        if output_path:
            output_file = Path(output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"batch_results_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'source': str(path),
                'total_problems': len(problems),
                'solved': success_count,
                'failed': len(problems) - success_count,
                'results': results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n{gold('Results saved to:')} {teal(str(output_file))}\n")

    def _load_problems_from_file(self, file_path: Path) -> List[Dict]:
        """Load problems from a file."""
        problems = []

        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                problems.append({'problem': item})
                            elif isinstance(item, dict) and 'problem' in item:
                                problems.append(item)
                    elif isinstance(data, dict) and 'problems' in data:
                        problems = data['problems']

            elif file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            problems.append({'problem': line})

        except Exception as e:
            print(format_warn(f"Failed to load {file_path}: {e}"))

        return problems

    def _emergency_shutdown(self):
        """Execute emergency shutdown of all agents."""
        print()
        print(red("!" * 60))
        print(red("EMERGENCY SHUTDOWN INITIATED"))
        print(red("!" * 60))

        try:
            if self._coordinator:
                self._coordinator.stop(save_state=False)
            if self._system:
                self._system.shutdown()
            print("\n" + format_ok("All agents terminated."))
        except Exception as e:
            print(format_error(f"Emergency shutdown error: {e}"))

        print(red("!" * 60) + "\n")

    def _shutdown(self):
        """Gracefully shutdown the system."""
        try:
            if self._coordinator:
                self._coordinator.stop(save_state=True)
            if self._system:
                self._system.shutdown()
        except Exception:
            pass  # Ignore errors during shutdown cleanup


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='SYMBO AGENTIC REASONERS - Mathematical Agent-Based Solver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Start interactive mode
  %(prog)s solve "2 + 2"            Solve a single problem
  %(prog)s solve "diff(x**2, x)"    Differentiate x^2
  %(prog)s batch ./problems/        Process folder of problems
  %(prog)s batch problems.txt       Process file of problems
  %(prog)s status                   Show system status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Solve command
    solve_parser = subparsers.add_parser('solve', help='Solve a single math problem')
    solve_parser.add_argument('problem', help='The math problem to solve')
    solve_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process batch of problems')
    batch_parser.add_argument('path', help='Path to file or folder')
    batch_parser.add_argument('-o', '--output', help='Output file path')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    args = parser.parse_args()

    cli = MathSolverCLI()

    if args.command == 'solve':
        cli._initialize_system(verbose=False)
        result = cli.solve_problem(args.problem, show_details=args.verbose)
        if result.get('status') == 'success':
            print(gold("Result: ") + teal(f"{result.get('result')}"))
            if args.verbose:
                print(gold("Domain: ") + teal(f"{result.get('domain', 'N/A')}"))
                print(gold("Specialist: ") + teal(f"{result.get('specialist', 'N/A')}"))
                print(gold("Time: ") + teal(f"{result.get('time_ms', 0):.1f}ms"))
        else:
            print(red(f"Error: {result.get('error', 'Unknown error')}"))
            sys.exit(1)

    elif args.command == 'batch':
        cli.batch_process(args.path, args.output)

    elif args.command == 'status':
        cli._initialize_system(verbose=False)
        cli._show_status()

    else:
        # Default to interactive mode
        cli.interactive_mode()


if __name__ == '__main__':
    main()
