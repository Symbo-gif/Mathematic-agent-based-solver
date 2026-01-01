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
SYMBO_AGENTIC_REASONERS Full System Startup
========================
Initializes and starts the complete SYMBO_AGENTIC_REASONERS system with all phases.

Usage:
    python scripts/start_full_system.py [--phase N] [--interactive]

Options:
    --phase N      Start up to phase N only (0-6, default: 6)
    --interactive  Start in interactive mode for solving problems
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_args():
    parser = argparse.ArgumentParser(description='Start SYMBO_AGENTIC_REASONERS System')
    parser.add_argument('--phase', type=int, default=6, choices=range(0, 7),
                        help='Maximum phase to initialize (0-6, default: 6)')
    parser.add_argument('--interactive', action='store_true',
                        help='Start in interactive problem-solving mode')
    return parser.parse_args()


def print_banner():
    print()
    print("=" * 70)
    print("     SYMBO_AGENTIC_REASONERS - Agent-Based Mathematical Discovery Engine")
    print("=" * 70)
    print()


def start_phase0():
    """Start Phase 0 infrastructure"""
    print("[Phase 0] Starting FIPA-compliant infrastructure...")
    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System
    system = Phase0System()
    system.start()
    print("[Phase 0] Infrastructure ready")
    return system


def start_phase1():
    """Start Phase 1 cognitive chassis"""
    print("[Phase 1] Starting Cognitive Chassis...")
    from symbo_agentic_reasoners_phase1.phase1_system import Phase1System
    system = Phase1System()
    system.start()
    print("[Phase 1] Cognitive Chassis ready")
    return system


def start_phase2():
    """Start Phase 2 mathematical workforce"""
    print("[Phase 2] Starting Mathematical Workforce...")
    from symbo_agentic_reasoners_phase2.phase2_system import Phase2System
    system = Phase2System()
    system.start()
    print("[Phase 2] Mathematical Workforce ready")
    return system


def start_phase3():
    """Start Phase 3 meta-cognitive middleware"""
    print("[Phase 3] Starting Meta-Cognitive Middleware...")
    from symbo_agentic_reasoners_phase3.phase3_system import Phase3System
    system = Phase3System()
    system.start()
    print("[Phase 3] Meta-Cognitive Middleware ready")
    return system


def start_phase4():
    """Start Phase 4 dynamic governance"""
    print("[Phase 4] Starting Dynamic Governance...")
    from symbo_agentic_reasoners_phase4.phase4_system import Phase4System
    system = Phase4System()
    system.start()
    print("[Phase 4] Dynamic Governance ready")
    return system


def start_phase5():
    """Start Phase 5 production optimization"""
    print("[Phase 5] Starting Production Optimization...")
    from symbo_agentic_reasoners_phase5.phase5_system import Phase5System
    system = Phase5System()
    system.start()
    print("[Phase 5] Production Optimization ready")
    return system


def start_phase6():
    """Start Phase 6 discovery engine"""
    print("[Phase 6] Starting Mathematical Discovery Engine...")
    from symbo_agentic_reasoners_phase6.phase6_system import Phase6System
    system = Phase6System()
    system.start()
    print("[Phase 6] Discovery Engine ready")
    return system


def interactive_mode(system):
    """Run interactive problem-solving session"""
    print()
    print("=" * 70)
    print("Interactive Mode - Enter mathematical problems to solve")
    print("Commands: 'quit' to exit, 'stats' for statistics, 'help' for help")
    print("=" * 70)
    print()

    conversation_id = "interactive_session"

    while True:
        try:
            problem = input("Problem> ").strip()

            if not problem:
                continue

            if problem.lower() in ('quit', 'exit', 'q'):
                print("Shutting down...")
                break

            if problem.lower() == 'stats':
                stats = system.get_statistics()
                print("\nSystem Statistics:")
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    else:
                        print(f"  {key}: {value}")
                print()
                continue

            if problem.lower() == 'help':
                print("\nSupported problem types:")
                print("  - Calculus: 'Integrate x^2 dx', 'Find derivative of sin(x)'")
                print("  - Algebra: 'Solve x^2 + 2x + 1 = 0', 'Factor x^3 - 1'")
                print("  - Linear Algebra: 'Find eigenvalues of [[1,2],[3,4]]'")
                print("  - And more...\n")
                continue

            # Solve the problem
            print(f"\nSolving: {problem}")
            print("-" * 50)

            try:
                if hasattr(system, 'solve'):
                    result = system.solve(problem, conversation_id)
                else:
                    result = system.solve(problem)

                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")

            print()

        except KeyboardInterrupt:
            print("\n\nInterrupted. Shutting down...")
            break
        except EOFError:
            print("\nShutting down...")
            break


def main():
    args = parse_args()

    print_banner()

    phase_starters = [
        start_phase0,
        start_phase1,
        start_phase2,
        start_phase3,
        start_phase4,
        start_phase5,
        start_phase6,
    ]

    system = None

    try:
        print(f"Starting system up to Phase {args.phase}...")
        print("-" * 50)

        for i in range(args.phase + 1):
            system = phase_starters[i]()

        print()
        print("=" * 50)
        print(f"[SUCCESS] System ready (Phase 0-{args.phase})")
        print("=" * 50)

        if system:
            # Run health check
            if hasattr(system, 'health_check'):
                health = system.health_check()
                print(f"\nHealth Check: {'PASSED' if health.get('healthy', True) else 'ISSUES DETECTED'}")

            if args.interactive:
                interactive_mode(system)
            else:
                print("\nSystem is running. Use --interactive for problem solving.")
                print("Press Ctrl+C to shutdown.")
                try:
                    # Keep running until interrupted
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\nShutting down...")

    except Exception as e:
        print(f"\n[ERROR] Failed to start system: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if system and hasattr(system, 'shutdown'):
            print("Cleaning up...")
            system.shutdown()
            print("System shutdown complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
