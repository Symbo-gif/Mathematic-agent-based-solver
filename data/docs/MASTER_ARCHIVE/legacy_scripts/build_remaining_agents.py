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

# Phase 2 - Remaining Agents Build Script
import os

base_dir = "symbo_agentic_reasoners_phase2"

# Create Linear Algebra Supervisor
linalg_super = os.path.join(base_dir, "supervisors", "linalg_supervisor.py")
print(f"Creating {linalg_super}...")

# Create Matrix Ops Specialist
matrix_ops = os.path.join(base_dir, "agents", "linear_algebra", "matrix_ops_specialist.py")
print(f"Creating {matrix_ops}...")

# Create Decomposition Specialist  
decomp = os.path.join(base_dir, "agents", "linear_algebra", "decomposition_specialist.py")
print(f"Creating {decomp}...")

# Create Vector Space Analyst
vector = os.path.join(base_dir, "agents", "linear_algebra", "vector_space_analyst.py")
print(f"Creating {vector}...")

# Create Combinatorics Agent
comb = os.path.join(base_dir, "agents", "discrete_math", "combinatorics_agent.py")
print(f"Creating {comb}...")

# Create Graph Theory Agent
graph = os.path.join(base_dir, "agents", "discrete_math", "graph_theory_agent.py")
print(f"Creating {graph}...")

# Create Stats Supervisor
stats_super = os.path.join(base_dir, "supervisors", "stats_supervisor.py")
print(f"Creating {stats_super}...")

# Create Distribution Specialist
dist = os.path.join(base_dir, "agents", "statistics", "distribution_specialist.py")
print(f"Creating {dist}...")

# Create Bayesian Engine
bayes = os.path.join(base_dir, "agents", "statistics", "bayesian_engine.py")
print(f"Creating {bayes}...")

# Create Frequentist Agent
freq = os.path.join(base_dir, "agents", "statistics", "frequentist_agent.py")
print(f"Creating {freq}...")

# Create Numerical Utility
num = os.path.join(base_dir, "agents", "numerical", "numerical_utility.py")
print(f"Creating {num}...")

print("All remaining agents mapped!")
