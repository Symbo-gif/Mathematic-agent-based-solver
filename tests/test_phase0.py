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
PHASE 0 VERIFICATION TEST
=========================

Standalone test runner for Phase 0 system verification.
"""

import sys
import os

# Add parent directory to path for imports

# Import Phase 0 system
from symbo_agentic_reasoners.core.system import Phase0System

if __name__ == "__main__":
    print()
    print("=" * 80)
    print(" " * 20 + "PHASE 0 VERIFICATION TEST")
    print("=" * 80)
    print()

    try:
        # Initialize and start system
        system = Phase0System()
        system.start()

        # Perform health check
        print("Performing comprehensive health check...")
        print()
        health = system.health_check()

        # Display statistics
        system.print_statistics()

        # Shutdown
        system.shutdown()

        print()
        print("=" * 80)
        print(" " * 20 + "VERIFICATION COMPLETE")
        print("=" * 80)
        print()

        if health['overall']:
            print("[SUCCESS] PHASE 0 COMPLETE AND VERIFIED")
            print()
            print("All Definition of Done criteria met:")
            print("  [OK] The Office Building is Built (AMS, DF, ACC operational)")
            print("  [OK] The City Manager is Hired (AMS monitoring & enforcement active)")
            print("  [OK] The Laws are Written (FIPA-ACL and OMDoc protocols enforced)")
            print("  [OK] The Library is Open (Blackboard & Vector DB operational)")
            print()
            print("SYSTEM STATUS: Computationally Alive, Mathematically Inert")
            print()
            print("-" * 80)
            print("NEXT STEPS:")
            print("-" * 80)
            print("  Phase 1: Cognitive Chassis")
            print("    - Implement Orchestrator (Tier 1)")
            print("    - Implement CNS (VRAM coordinator)")
            print("    - Implement Specialist Agents (Algebra, Calculus)")
            print("    - Implement Verification Agent")
            print("    - Test with actual mathematical problems")
            print()
            sys.exit(0)
        else:
            print("[FAILED] PHASE 0 VERIFICATION FAILED")
            print()
            print("Some Definition of Done criteria not met.")
            print("Review health check output above for details.")
            print()
            sys.exit(1)

    except Exception as e:
        print()
        print("[ERROR] PHASE 0 VERIFICATION ERROR")
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
