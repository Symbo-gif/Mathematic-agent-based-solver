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

"""Test script to verify dependencies are installed correctly"""

import sys
print(f"Python: {sys.version}")
print("-" * 80)

# Test core dependencies
dependencies = [
    ('sympy', 'SymPy'),
    ('numpy', 'NumPy'),
    ('scipy', 'SciPy'),
    ('mpmath', 'mpmath'),
]

optional_dependencies = [
    ('chromadb', 'ChromaDB'),
    ('sentence_transformers', 'sentence-transformers'),
    ('torch', 'PyTorch'),
    ('networkx', 'NetworkX'),
    ('matplotlib', 'Matplotlib'),
    ('plotly', 'Plotly'),
]

print("\nCORE DEPENDENCIES:")
print("-" * 80)
for module_name, display_name in dependencies:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name:20s} {version}")
    except ImportError as e:
        print(f"❌ {display_name:20s} NOT INSTALLED")

print("\nOPTIONAL DEPENDENCIES:")
print("-" * 80)
for module_name, display_name in optional_dependencies:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name:20s} {version}")
    except ImportError as e:
        print(f"⚠️  {display_name:20s} NOT INSTALLED (optional)")
    except (RuntimeError, OSError) as e:
        # RuntimeError: torch version incompatible with Python version
        # OSError: library loading issues
        print(f"⚠️  {display_name:20s} INCOMPATIBLE ({type(e).__name__})")

print("\n" + "=" * 80)
print("Dependency check complete!")
