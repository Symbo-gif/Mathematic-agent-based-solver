# Create Riemannian specialists
SPECIALISTS = [
    ('MetricTensorSpecialist', 'metric', 'Riemannian metrics, isometries'),
    ('CurvatureSpecialist', 'curvature', 'Riemann tensor, Ricci, sectional curvature'),
    ('GeodesicSpecialist', 'geodesic', 'Geodesic equations, exponential map'),
    ('ComparisonTheoremsSpecialist', 'comparison', 'Rauch, Toponogov comparison theorems'),
    ('HolonomySpecialist', 'holonomy', 'Parallel transport, holonomy groups'),
]

template = '''# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""{NAME} - {DESC}"""

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
                service_type='math.riemannian.{FILE}', agent_id=self.agent_id,
                algorithm='{FILE}', cost='high', instance=self, type='specialist', tier='3'))
    def process(self, task_entry):
        self.tasks_executed += 1
        return {{'operation': '{FILE}', 'explanation': '{DESC}'}}
    def update_beliefs(self): pass
    def deliberate(self): return []
    def execute_step(self, i): pass
    def get_statistics(self): return {{**super().get_statistics(), 'tasks_executed': self.tasks_executed}}
'''

import os
os.makedirs('src/symbo_agentic_reasoners/agents/specialists/riemannian', exist_ok=True)

for name, file, desc in SPECIALISTS:
    content = template.format(NAME=name, FILE=file, DESC=desc, AGENT_ID=f'{file}_specialist_001')
    with open(f'src/symbo_agentic_reasoners/agents/specialists/riemannian/{file}.py', 'w') as f:
        f.write(content)
    print(f'Created: {name}')

print(f'Total: {len(SPECIALISTS)} Riemannian specialists')
