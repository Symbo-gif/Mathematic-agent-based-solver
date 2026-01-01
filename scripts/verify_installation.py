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
SYMBO_AGENTIC_REASONERS Installation Verification
==================================================
Checks that all required dependencies are installed and the system
can be initialized properly.

Usage:
    python scripts/verify_installation.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_python_version():
    """Check Python version is 3.9+"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  [FAIL] Python {version.major}.{version.minor} - Requires 3.9+")
        return False


def check_core_dependencies():
    """Check core required packages"""
    print("\nChecking core dependencies...")

    required = {
        'sympy': 'Symbolic mathematics',
        'numpy': 'Numerical computing',
        'scipy': 'Scientific computing',
    }

    all_ok = True
    for package, description in required.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"  [OK] {package} ({version}) - {description}")
        except ImportError:
            print(f"  [FAIL] {package} - {description} (pip install {package})")
            all_ok = False

    return all_ok


def check_optional_dependencies():
    """Check optional packages"""
    print("\nChecking optional dependencies...")

    optional = {
        'chromadb': 'Vector database (production mode)',
        'torch': 'Neural network training (Phase 5+)',
        'transformers': 'LLM integration (Phase 5+)',
        'docx': 'Document conversion (python-docx)',
    }

    for package, description in optional.items():
        try:
            if package == 'docx':
                __import__('docx')
            else:
                __import__(package)
            print(f"  [OK] {package} - {description}")
        except ImportError:
            print(f"  [SKIP] {package} - {description} (optional)")


def check_module_imports():
    """Check all system modules can be imported"""
    print("\nChecking system modules...")

    modules = [
        ('symbo_agentic_reasoners.infrastructure.ams', 'Agent Management System'),
        ('symbo_agentic_reasoners.infrastructure.directory_facilitator', 'Directory Facilitator'),
        ('symbo_agentic_reasoners.infrastructure.acc', 'Agent Communication Channel'),
        ('symbo_agentic_reasoners.core.blackboard', 'Blackboard Memory'),
        ('symbo_agentic_reasoners.core.bdi_agent', 'BDI Agent Framework'),
        ('symbo_agentic_reasoners.protocols.fipa_acl', 'FIPA-ACL Messaging'),
        ('symbo_agentic_reasoners.agents.base.problem_analysis', 'Problem Analysis'),
        ('symbo_agentic_reasoners.agents.supervisors.algebra_supervisor', 'Algebra Supervisor'),
        ('symbo_agentic_reasoners.middleware.conflict_resolution', 'Conflict Resolution'),
        ('symbo_agentic_reasoners.optimization.symbo.symbo_llm', 'Symbo LLM'),
        ('symbo_agentic_reasoners.agents.synthesis.conjecture_generator', 'Conjecture Generator'),
        ('symbo_agentic_reasoners.cli', 'CLI Interface'),
    ]

    all_ok = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"  [OK] {description}")
        except ImportError as e:
            print(f"  [FAIL] {description}: {e}")
            all_ok = False

    return all_ok


def check_directory_structure():
    """Check required directories exist"""
    print("\nChecking directory structure...")

    required_dirs = [
        'src/symbo_agentic_reasoners',
        'src/symbo_agentic_reasoners/infrastructure',
        'src/symbo_agentic_reasoners/core',
        'src/symbo_agentic_reasoners/agents',
        'src/symbo_agentic_reasoners/middleware',
        'src/symbo_agentic_reasoners/optimization',
        'src/symbo_agentic_reasoners/discovery',
        'tests',
        'scripts',
        'docs',
    ]

    all_ok = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  [OK] {dir_name}/")
        else:
            print(f"  [FAIL] {dir_name}/ - Missing")
            all_ok = False

    return all_ok


def quick_functionality_test():
    """Quick test of basic functionality"""
    print("\nRunning quick functionality test...")

    try:
        # Test Blackboard
        from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType
        bb = Blackboard()
        entry = create_entry(
            entry_type=EntryType.TASK,
            content="Test 2+2",
            author_agent="verify_script",
            conversation_id="verify_test"
        )
        entry_id = bb.post(entry)
        print("  [OK] Blackboard memory")

        # Test FIPA-ACL
        from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage, create_inform
        from unittest.mock import MagicMock
        mock_content = MagicMock()
        mock_content.to_omdoc.return_value = "<omdoc/>"
        msg = create_inform('sender', 'receiver', mock_content)
        print("  [OK] FIPA-ACL messaging")

        # Test CLI
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        result = cli.solve_problem("2 + 2")
        if result['status'] == 'success':
            print(f"  [OK] CLI solve: 2+2 = {result['result']}")
        else:
            print(f"  [WARN] CLI solve returned: {result}")

        # Test AMS
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
        ams = AgentManagementSystem()
        print("  [OK] Agent Management System")

        return True

    except Exception as e:
        print(f"  [FAIL] Functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("SYMBO_AGENTIC_REASONERS Installation Verification")
    print("=" * 60)

    results = []

    results.append(("Python Version", check_python_version()))
    results.append(("Core Dependencies", check_core_dependencies()))
    check_optional_dependencies()  # Don't fail on optional
    results.append(("Directory Structure", check_directory_structure()))
    results.append(("Module Imports", check_module_imports()))
    results.append(("Functionality Test", quick_functionality_test()))

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("[SUCCESS] All verification checks passed!")
        print("The system is ready to use.")
        return 0
    else:
        print("[WARNING] Some checks failed.")
        print("Install missing dependencies and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
