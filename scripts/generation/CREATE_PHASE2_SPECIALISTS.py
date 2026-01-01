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

# Quick script to create Phase 2 specialists

SPECIALISTS = [
    # Computability (4 more)
    ('RecursionTheorySpecialist', 'computability', 'recursion_theory', 'Primitive recursive functions'),
    ('TuringDegreesSpecialist', 'computability', 'turing_degrees', 'Turing degrees, jump operator'),
    ('ComplexityTheorySpecialist', 'computability', 'complexity_theory', 'P vs NP, complexity classes'),
    ('KolmogorovComplexitySpecialist', 'computability', 'kolmogorov_complexity', 'Descriptive complexity'),

    # Bayesian Decision (3)
    ('UtilityTheorySpecialist', 'statistics/bayesian_decision', 'utility_theory', 'Utility functions, expected utility'),
    ('DecisionRulesSpecialist', 'statistics/bayesian_decision', 'decision_rules', 'Bayes rules, minimax, admissibility'),
    ('SequentialDecisionSpecialist', 'statistics/bayesian_decision', 'sequential_decision', 'Multi-armed bandits, optimal stopping'),

    # Time Series (4)
    ('ARIMASpecialist', 'statistics/timeseries', 'arima', 'ARIMA modeling, Box-Jenkins'),
    ('KalmanFilterSpecialist', 'statistics/timeseries', 'kalman_filter', 'State-space models, Kalman filtering'),
    ('SpectralAnalysisSpecialist', 'statistics/timeseries', 'spectral_analysis', 'Power spectral density, periodogram'),
    ('NonlinearTimeSeriesSpecialist', 'statistics/timeseries', 'nonlinear_timeseries', 'GARCH, threshold models'),
]

from pathlib import Path

template = '''# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""{SPECIALIST_NAME} - {DESCRIPTION}"""

from typing import Dict, Any
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

class {SPECIALIST_NAME}(BDIAgent):
    def __init__(self, agent_id='{AGENT_ID}', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.{SERVICE_TYPE}', agent_id=self.agent_id,
                algorithm='{ALGORITHM}', cost='medium', instance=self, type='specialist', tier='3'))

    def process(self, task_entry):
        self.tasks_executed += 1
        return {{'operation': '{OPERATION}', 'explanation': '{DESCRIPTION}'}}

    def update_beliefs(self): pass
    def deliberate(self): return []
    def execute_step(self, i): pass
    def get_statistics(self): return {{**super().get_statistics(), 'tasks_executed': self.tasks_executed}}
'''

ROOT = Path(__file__).resolve().parents[2]

for spec_name, domain, file_name, description in SPECIALISTS:
    # Create directory
    dir_path = ROOT / 'src' / 'symbo_agentic_reasoners' / 'agents' / 'specialists' / domain
    dir_path.mkdir(parents=True, exist_ok=True)

    # Generate file
    service_type = domain.replace('/', '.') + '.' + file_name
    agent_id = file_name + '_specialist_001'
    content = template.format(
        SPECIALIST_NAME=spec_name,
        DESCRIPTION=description,
        AGENT_ID=agent_id,
        SERVICE_TYPE=service_type,
        ALGORITHM=file_name,
        OPERATION=file_name.replace('_', ' ')
    )

    file_path = dir_path / f'{file_name}.py'
    with open(file_path, 'w') as f:
        f.write(content)
    print(f'Created: {file_path}')

print(f'\nTotal specialists created: {len(SPECIALISTS)}')
