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

"""RIEMANNIAN GEOMETRY SUPERVISOR (Tier 2) - Phase 2"""

from typing import List, Dict, Any, Optional
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard

class RiemannianGeometrySupervisor(BDIAgent):
    """Riemannian Geometry Supervisor - Routes differential geometry tasks"""

    def __init__(self, agent_id='riemannian_geometry_supervisor_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_routed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian', agent_id=self.agent_id, algorithm='routing',
                cost='low', instance=self, type='supervisor', domain='riemannian_geometry', tier='2'))

    def process(self, task_entry):
        self.tasks_routed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        if 'metric tensor' in raw_input or 'riemannian metric' in raw_input:
            service_type = 'math.riemannian.metric'
        elif 'curvature' in raw_input or 'ricci' in raw_input:
            service_type = 'math.riemannian.curvature'
        elif 'geodesic' in raw_input:
            service_type = 'math.riemannian.geodesic'
        elif 'comparison' in raw_input or 'rauch' in raw_input:
            service_type = 'math.riemannian.comparison'
        elif 'holonomy' in raw_input or 'parallel transport' in raw_input:
            service_type = 'math.riemannian.holonomy'
        else:
            service_type = 'math.riemannian.metric'

        specialists = self.df.search(service_type=service_type) if self.df else []
        if specialists and hasattr(specialists[0], 'process'):
            return specialists[0].process(task_entry)
        return {'error': 'No specialist found'}

    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_routed': self.tasks_routed}
