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

"""SPECTRAL CLUSTERING SPECIALIST - Normalized cuts, k-way partitioning"""

import numpy as np
from typing import Dict, Any
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

class SpectralClusteringSpecialist(BDIAgent):
    def __init__(self, agent_id='spectral_clustering_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.graphs.spectral.clustering', agent_id=self.agent_id,
                algorithm='spectral_clustering', cost='high', instance=self, type='specialist', tier='3'))

    def process(self, task_entry):
        self.tasks_executed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        A = np.array(metadata.get('adjacency_matrix', [[0, 1, 1], [1, 0, 1], [1, 1, 0]]))
        k = metadata.get('k', 2)  # Number of clusters

        # Compute normalized Laplacian
        degrees = np.sum(A, axis=1)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees + 1e-10))
        L_norm = np.eye(len(A)) - D_inv_sqrt @ A @ D_inv_sqrt

        # Get k smallest eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(L_norm)
        idx = np.argsort(eigenvalues)
        embedding = eigenvectors[:, idx[:k]]

        # K-means on embedding (simplified)
        labels = np.argmax(embedding, axis=1)

        return {'operation': 'spectral_clustering', 'k': k, 'labels': labels.tolist(),
                'eigenvalues': eigenvalues[idx[:k]].tolist(),
                'explanation': f'Clustered graph into {k} partitions using spectral method'}

    def update_beliefs(self): pass
    def deliberate(self): return []
    def execute_step(self, i): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_executed': self.tasks_executed}
