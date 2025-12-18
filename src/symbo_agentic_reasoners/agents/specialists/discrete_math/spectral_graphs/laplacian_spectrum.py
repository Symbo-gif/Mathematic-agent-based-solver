# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""LAPLACIAN SPECTRUM SPECIALIST - Graph Laplacian eigenvalues, Fiedler value"""

import numpy as np
from typing import Dict, Any, List
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

class LaplacianSpectrumSpecialist(BDIAgent):
    """Laplacian Spectrum Specialist - Eigenvalues of graph Laplacian, algebraic connectivity"""

    def __init__(self, agent_id='laplacian_spectrum_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = 0
        self.spectra_computed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.graphs.spectral.laplacian', agent_id=self.agent_id,
                algorithm='laplacian_eigenvalues', cost='medium', instance=self, type='specialist', tier='3'))

    def process(self, task_entry):
        self.tasks_executed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        adj_matrix = np.array(metadata.get('adjacency_matrix', [[0, 1], [1, 0]]))
        result = self._compute_laplacian_spectrum(adj_matrix)
        self.tasks_succeeded += 1
        return result

    def _compute_laplacian_spectrum(self, A: np.ndarray) -> Dict[str, Any]:
        """Compute Laplacian L = D - A and its eigenvalues"""
        self.spectra_computed += 1

        # Degree matrix
        degrees = np.sum(A, axis=1)
        D = np.diag(degrees)

        # Laplacian L = D - A
        L = D - A

        # Compute eigenvalues
        eigenvalues = np.linalg.eigvalsh(L)  # Symmetric matrix
        eigenvalues = np.sort(eigenvalues)

        # Fiedler value (second smallest eigenvalue)
        fiedler = eigenvalues[1] if len(eigenvalues) > 1 else 0

        return {
            'operation': 'laplacian_spectrum',
            'adjacency_matrix': A.tolist(),
            'degree_matrix': D.tolist(),
            'laplacian': L.tolist(),
            'eigenvalues': eigenvalues.tolist(),
            'fiedler_value': float(fiedler),
            'algebraic_connectivity': float(fiedler),
            'is_connected': fiedler > 1e-10,
            'explanation': f'Laplacian spectrum: λ₀=0, λ₁(Fiedler)={fiedler:.4f}'
        }

    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_executed': self.tasks_executed,
                                      'spectra_computed': self.spectra_computed}
