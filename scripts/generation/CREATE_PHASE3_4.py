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

# Create all Phase 3 and 4 agents

SUPERVISORS = [
    ('AlgebraicTopologySupervisor', 'algebraic_topology', 'algebraictopology'),
    ('ErgodicTheorySupervisor', 'ergodic_theory', 'ergodic'),
    ('GeometricMeasureTheorySupervisor', 'geometric_measure', 'geometricmeasure'),
    ('TopologicalDataAnalysisSupervisor', 'tda', 'tda'),
]

SPECIALISTS = {
    'algebraic_topology': [
        ('HomotopySpecialist', 'homotopy', 'Homotopy groups, fibrations'),
        ('HomologySpecialist', 'homology', 'Singular homology, Mayer-Vietoris'),
        ('CohomologySpecialist', 'cohomology', 'Cohomology rings, cup product'),
        ('FundamentalGroupSpecialist', 'fundamental_group', 'pi_1 computation, van Kampen'),
        ('SpectralSequencesSpecialist', 'spectral_sequences', 'Serre spectral sequence'),
    ],
    'ergodic': [
        ('InvariantMeasureSpecialist', 'invariant_measures', 'Existence, uniqueness, ergodicity'),
        ('MixingSpecialist', 'mixing', 'Weak mixing, strong mixing'),
        ('ErgodicTheoremSpecialist', 'ergodic_theorems', 'Birkhoff, von Neumann theorems'),
        ('DynamicalEntropySpecialist', 'dynamical_entropy', 'Kolmogorov-Sinai entropy'),
    ],
    'geometric_measure': [
        ('HausdorffMeasureSpecialist', 'hausdorff_measure', 'Hausdorff dimension, measure'),
        ('RectifiabilitySpecialist', 'rectifiability', 'Rectifiable sets, tangent spaces'),
        ('CurrentsSpecialist', 'currents', 'Integration over currents, varifolds'),
        ('MinimalSurfacesSpecialist', 'minimal_surfaces', 'Plateau problem, mean curvature flow'),
    ],
    'tda': [
        ('PersistentHomologySpecialist', 'persistent_homology', 'Persistence diagrams, barcodes'),
        ('MapperSpecialist', 'mapper', 'Mapper algorithm, cover construction'),
        ('SimplicialComplexSpecialist', 'simplicial_complex', 'Vietoris-Rips, Cech complexes'),
        ('TopologicalInferenceSpecialist', 'topological_inference', 'Confidence sets, bootstrap'),
    ],
    'optimization/advanced': [
        ('NonconvexOptimizationSpecialist', 'nonconvex', 'Trust region, SQP'),
        ('GlobalOptimizationSpecialist', 'global_optimization', 'Branch and bound, simulated annealing'),
        ('VariationalCalculusSpecialist', 'variational_calculus', 'Euler-Lagrange equations'),
        ('OptimalControlSpecialist', 'optimal_control', 'Pontryagin maximum principle'),
        ('GameTheoryOptimizationSpecialist', 'game_theory', 'Nash equilibrium, Stackelberg games'),
        ('MultiobjectiveOptimizationSpecialist', 'multiobjective', 'Pareto optimality, NSGA-II'),
    ],
}

sup_template = """# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

\"\"\"{NAME} SUPERVISOR (Tier 2) - Phase 3/4\"\"\"

from typing import List, Dict, Any, Optional
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard

class {NAME}(BDIAgent):
    def __init__(self, agent_id='{AGENT_ID}', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_routed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.{SERVICE}', agent_id=self.agent_id, algorithm='routing',
                cost='low', instance=self, type='supervisor', domain='{DOMAIN}', tier='2'))
    def process(self, task_entry):
        self.tasks_routed += 1
        specialists = self.df.search(service_type='math.{SERVICE}') if self.df else []
        if specialists and hasattr(specialists[0], 'process'):
            return specialists[0].process(task_entry)
        return {{'error': 'No specialist found'}}
    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {{**super().get_statistics(), 'tasks_routed': self.tasks_routed}}
"""

spec_template = """# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

\"\"\"{NAME} - {DESC}\"\"\"

from typing import Dict
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

class {NAME}(BDIAgent):
    def __init__(self, agent_id='{AGENT_ID}', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.{SERVICE}', agent_id=self.agent_id,
                algorithm='{ALGO}', cost='medium', instance=self, type='specialist', tier='3'))
    def process(self, task_entry):
        self.tasks_executed += 1
        return {{'operation': '{OPERATION}', 'explanation': '{DESC}'}}
    def update_beliefs(self): pass
    def deliberate(self): return []
    def execute_step(self, i): pass
    def get_statistics(self): return {{**super().get_statistics(), 'tasks_executed': self.tasks_executed}}
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sup_dir = ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'supervisors'
spec_root = ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists'

# Create supervisors
for name, domain, service in SUPERVISORS:
    content = sup_template.format(NAME=name, DOMAIN=domain, SERVICE=service, AGENT_ID=f'{domain}_supervisor_001')
    path = sup_dir / f'{domain}_supervisor.py'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f'[SUP] {name}')

# Create specialists
total = 0
for domain, specs in SPECIALISTS.items():
    domain_dir = spec_root / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    for name, file, desc in specs:
        service = domain.replace('/', '.') + '.' + file
        content = spec_template.format(
            NAME=name, DESC=desc, AGENT_ID=f'{file}_specialist_001',
            SERVICE=service, ALGO=file, OPERATION=file.replace('_', ' ')
        )
        with open(domain_dir / f'{file}.py', 'w') as f:
            f.write(content)
        total += 1
    print(f'[{domain.upper()}] {len(specs)} specialists')

print(f'\nTOTAL: 4 supervisors + {total} specialists = {4 + total} agents')
