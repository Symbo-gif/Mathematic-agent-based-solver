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

from pathlib import Path

# Create __init__.py for Phase 3-4
ROOT = Path(__file__).resolve().parents[2]
inits = {
    ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / 'algebraic_topology' / '__init__.py':
        '__all__ = ["HomotopySpecialist", "HomologySpecialist", "CohomologySpecialist", "FundamentalGroupSpecialist", "SpectralSequencesSpecialist"]',
    ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / 'ergodic' / '__init__.py':
        '__all__ = ["InvariantMeasureSpecialist", "MixingSpecialist", "ErgodicTheoremSpecialist", "DynamicalEntropySpecialist"]',
    ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / 'geometric_measure' / '__init__.py':
        '__all__ = ["HausdorffMeasureSpecialist", "RectifiabilitySpecialist", "CurrentsSpecialist", "MinimalSurfacesSpecialist"]',
    ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / 'tda' / '__init__.py':
        '__all__ = ["PersistentHomologySpecialist", "MapperSpecialist", "SimplicialComplexSpecialist", "TopologicalInferenceSpecialist"]',
    ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / 'optimization' / 'advanced' / '__init__.py':
        '__all__ = ["NonconvexOptimizationSpecialist", "GlobalOptimizationSpecialist", "VariationalCalculusSpecialist", "OptimalControlSpecialist", "GameTheoryOptimizationSpecialist", "MultiobjectiveOptimizationSpecialist"]',
}

for path, content in inits.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(f'# Copyright 2025\n{content}\n')
    print(f'Created: {path.parent.name}/__init__.py')
