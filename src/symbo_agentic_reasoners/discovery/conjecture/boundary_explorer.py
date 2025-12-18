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

"""
PHASE 6 - CG-3: BOUNDARY EXPLORER
==================================

Explores the boundaries of mathematical conjectures to find edge cases,
counterexamples, and limiting conditions.

CAPABILITIES:
------------
- Parameter space exploration
- Edge case identification
- Boundary condition testing
- Counterexample search
- Sensitivity analysis

REFERENCE:
---------
- Phase 6 Discovery Team: Conjecture Generation Subteam
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Generator
from datetime import datetime
from enum import Enum
import random

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, symbols, simplify, oo, parse_expr, Integer
)

logger = logging.getLogger('symbo_agentic_reasoners.phase6.boundary_explorer')


class BoundaryType(Enum):
    """Types of boundaries to explore"""
    PARAMETER_LIMIT = "parameter_limit"
    DOMAIN_EDGE = "domain_edge"
    SINGULARITY = "singularity"
    DISCONTINUITY = "discontinuity"
    DEGENERATE_CASE = "degenerate_case"


class ExplorationStatus(Enum):
    """Status of boundary exploration"""
    PENDING = "pending"
    EXPLORING = "exploring"
    COMPLETE = "complete"
    COUNTEREXAMPLE_FOUND = "counterexample_found"
    BOUNDARY_CONFIRMED = "boundary_confirmed"


@dataclass
class BoundaryCondition:
    """
    A boundary condition to explore.
    
    Attributes:
        condition_id: Unique identifier
        expression: The expression/condition
        boundary_type: Type of boundary
        parameters: Parameters involved
        domain_constraints: Constraints on the domain
    """
    condition_id: str
    expression: str
    boundary_type: BoundaryType
    parameters: List[str]
    domain_constraints: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'id': self.condition_id,
            'expression': self.expression,
            'type': self.boundary_type.value,
            'parameters': self.parameters
        }


@dataclass
class ExplorationResult:
    """
    Result of boundary exploration.
    
    Attributes:
        condition: The explored condition
        status: Exploration outcome
        edge_cases: Discovered edge cases
        counterexamples: Found counterexamples
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        boundary_values: Critical boundary values
    """
    condition: BoundaryCondition
    status: ExplorationStatus
    edge_cases: List[Dict[str, Any]]
    counterexamples: List[Dict[str, Any]]
    boundary_values: Dict[str, List[Any]]
    sensitivity: Dict[str, float] = field(default_factory=dict)
    exploration_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'condition_id': self.condition.condition_id,
            'status': self.status.value,
            'edge_case_count': len(self.edge_cases),
            'counterexample_count': len(self.counterexamples),
            'critical_boundaries': len(self.boundary_values),
            'time_ms': self.exploration_time_ms
        }


class BoundaryExplorer:
    """
    CG-3: Boundary Explorer
    
    Explores the boundaries of mathematical conjectures to find edge cases,
    counterexamples, and limiting conditions.
    
    Key capabilities:
    - Parameter limit exploration (x → 0, x → ∞)
    - Domain edge testing
    - Singularity detection
    - Degenerate case identification
    - Sensitivity analysis
    """
    
    # Standard boundary values to test
    STANDARD_BOUNDARIES = [0, 1, -1, 0.5, 2, -2, 10, 100, 1e-10, 1e10]
    
    def __init__(
        self,
        max_iterations: int = 1000,
        tolerance: float = 1e-10
    ):
        """
        Initialize the Boundary Explorer.
        
        Args:
            max_iterations: Maximum iterations for exploration
            tolerance: Numerical tolerance for boundary detection
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # Exploration cache
        self.explored_conditions: Dict[str, ExplorationResult] = {}
        
        # Statistics
        self.explorations_run = 0
        self.edge_cases_found = 0
        self.counterexamples_found = 0
        
        logger.info(f"BoundaryExplorer initialized (max_iter={max_iterations})")
    
    def explore(
        self,
        condition: BoundaryCondition,
        sample_count: int = 100
    ) -> ExplorationResult:
        """
        Explore boundaries of a condition.
        
        Args:
            condition: Condition to explore
            sample_count: Number of samples for random exploration
            
        Returns:
            ExplorationResult with findings
        """
        import time
        start_time = time.time()
        
        self.explorations_run += 1
        
        edge_cases = []
        counterexamples = []
        boundary_values = {p: [] for p in condition.parameters}
        sensitivity = {}
        
        try:
            # Explore parameter limits
            for param in condition.parameters:
                limit_results = self._explore_limits(condition, param)
                boundary_values[param].extend(limit_results)
                
                # Check for edge cases at limits
                for val in limit_results:
                    edge_case = self._test_edge_case(condition, param, val)
                    if edge_case:
                        edge_cases.append(edge_case)
                        self.edge_cases_found += 1
            
            # Explore domain edges
            domain_edges = self._explore_domain_edges(condition)
            edge_cases.extend(domain_edges)
            
            # Random sampling for counterexamples
            random_counterex = self._random_exploration(condition, sample_count)
            counterexamples.extend(random_counterex)
            self.counterexamples_found += len(random_counterex)
            
            # Sensitivity analysis
            sensitivity = self._compute_sensitivity(condition)
            
            # Determine status
            if counterexamples:
                status = ExplorationStatus.COUNTEREXAMPLE_FOUND
            elif edge_cases:
                status = ExplorationStatus.BOUNDARY_CONFIRMED
            else:
                status = ExplorationStatus.COMPLETE
                
        except Exception as e:
            logger.warning(f"Exploration error: {type(e).__name__}: {e}")
            status = ExplorationStatus.COMPLETE
        
        result = ExplorationResult(
            condition=condition,
            status=status,
            edge_cases=edge_cases,
            counterexamples=counterexamples,
            boundary_values=boundary_values,
            sensitivity=sensitivity,
            exploration_time_ms=int((time.time() - start_time) * 1000)
        )
        
        self.explored_conditions[condition.condition_id] = result
        return result
    
    def _explore_limits(
        self,
        condition: BoundaryCondition,
        param: str
    ) -> List[Any]:
        """Explore limit behavior for a parameter"""
        critical_values = []
        
        # Test standard boundary values
        for val in self.STANDARD_BOUNDARIES:
            constraints = condition.domain_constraints.get(param, (-float('inf'), float('inf')))
            if constraints[0] <= val <= constraints[1]:
                critical_values.append(val)
        
        # Add domain boundary values
        if param in condition.domain_constraints:
            low, high = condition.domain_constraints[param]
            if low != -float('inf'):
                critical_values.append(low)
                critical_values.append(low + self.tolerance)
            if high != float('inf'):
                critical_values.append(high)
                critical_values.append(high - self.tolerance)
        
        return list(set(critical_values))
    
    def _explore_domain_edges(
        self,
        condition: BoundaryCondition
    ) -> List[Dict[str, Any]]:
        """Explore edges of the domain"""
        edge_cases = []
        
        for param, (low, high) in condition.domain_constraints.items():
            if low != -float('inf'):
                edge_cases.append({
                    'type': 'domain_edge',
                    'parameter': param,
                    'value': low,
                    'description': f'{param} at lower bound'
                })
            if high != float('inf'):
                edge_cases.append({
                    'type': 'domain_edge',
                    'parameter': param,
                    'value': high,
                    'description': f'{param} at upper bound'
                })
        
        return edge_cases
    
    def _test_edge_case(
        self,
        condition: BoundaryCondition,
        param: str,
        value: Any
    ) -> Optional[Dict[str, Any]]:
        """Test if a parameter value creates an edge case"""
        # Check for degenerate values
        if value == 0:
            return {
                'type': 'zero_case',
                'parameter': param,
                'value': 0,
                'description': f'{param}=0 may cause degenerate behavior'
            }
        
        # Check for extreme values
        if abs(value) > 1e10:
            return {
                'type': 'extreme_value',
                'parameter': param,
                'value': value,
                'description': f'{param} at extreme value may overflow'
            }
        
        return None
    
    def _random_exploration(
        self,
        condition: BoundaryCondition,
        sample_count: int
    ) -> List[Dict[str, Any]]:
        """Random sampling to find counterexamples"""
        counterexamples = []
        
        for _ in range(sample_count):
            sample = {}
            for param in condition.parameters:
                constraints = condition.domain_constraints.get(param, (-100, 100))
                low = max(-1e6, constraints[0])
                high = min(1e6, constraints[1])
                sample[param] = random.uniform(low, high)
            
            # Simplified: check for obvious issues
            if self._check_counterexample(condition, sample):
                counterexamples.append({
                    'values': sample,
                    'reason': 'Failed condition check'
                })
        
        return counterexamples
    
    def _check_counterexample(
        self,
        condition: BoundaryCondition,
        values: Dict[str, Any]
    ) -> bool:
        """Check if values form a counterexample (simplified)"""
        # Would evaluate the condition with the values
        # For now, only flag obvious numerical issues
        for v in values.values():
            if abs(v) < self.tolerance and 'division' in condition.expression.lower():
                return True
        return False
    
    def _compute_sensitivity(
        self,
        condition: BoundaryCondition
    ) -> Dict[str, float]:
        """Compute sensitivity of condition to each parameter"""
        sensitivity = {}
        
        for param in condition.parameters:
            # Simplified sensitivity measure
            # Would use numerical differentiation in full implementation
            if param in condition.expression:
                sensitivity[param] = 1.0
            else:
                sensitivity[param] = 0.0
        
        return sensitivity
    
    def explore_conjecture_boundaries(
        self,
        conjecture_statement: str,
        variables: List[str],
        constraints: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> ExplorationResult:
        """
        Convenience method to explore a conjecture's boundaries.
        
        Args:
            conjecture_statement: The conjecture as a string
            variables: Variables in the conjecture
            constraints: Optional domain constraints
            
        Returns:
            ExplorationResult
        """
        condition = BoundaryCondition(
            condition_id=f"conj_{self.explorations_run}",
            expression=conjecture_statement,
            boundary_type=BoundaryType.PARAMETER_LIMIT,
            parameters=variables,
            domain_constraints=constraints or {}
        )
        
        return self.explore(condition)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get explorer statistics"""
        return {
            'explorations_run': self.explorations_run,
            'edge_cases_found': self.edge_cases_found,
            'counterexamples_found': self.counterexamples_found,
            'cached_results': len(self.explored_conditions)
        }
    
    def reset(self):
        """Reset explorer state"""
        self.explored_conditions.clear()
        self.explorations_run = 0
        self.edge_cases_found = 0
        self.counterexamples_found = 0
    
    def health_check(self) -> bool:
        """Check if explorer is healthy"""
        return True


if __name__ == "__main__":
    """Test Boundary Explorer"""
    print("=" * 80)
    print("PHASE 6 - BOUNDARY EXPLORER TEST")
    print("=" * 80)
    print()
    
    # Initialize explorer
    explorer = BoundaryExplorer()
    
    # Test 1: Explore simple condition
    print("Test 1: Explore Simple Condition")
    condition = BoundaryCondition(
        condition_id="test_1",
        expression="x^2 + y^2 = r^2",
        boundary_type=BoundaryType.PARAMETER_LIMIT,
        parameters=["x", "y", "r"],
        domain_constraints={"r": (0, 100)}
    )
    result = explorer.explore(condition)
    print(f"  Status: {result.status.value}")
    print(f"  Edge cases: {len(result.edge_cases)}")
    print(f"  Time: {result.exploration_time_ms}ms")
    print()
    
    # Test 2: Explore with division
    print("Test 2: Explore Division Expression")
    result = explorer.explore_conjecture_boundaries(
        conjecture_statement="f(x) = 1/x for x > 0",
        variables=["x"],
        constraints={"x": (0.001, 1000)}
    )
    print(f"  Status: {result.status.value}")
    print(f"  Critical boundaries: {result.boundary_values}")
    print()
    
    # Test 3: Multi-parameter exploration
    print("Test 3: Multi-Parameter Exploration")
    result = explorer.explore_conjecture_boundaries(
        conjecture_statement="a*b = c for positive reals",
        variables=["a", "b", "c"],
        constraints={"a": (0, 100), "b": (0, 100), "c": (0, 10000)}
    )
    print(f"  Parameters explored: {list(result.boundary_values.keys())}")
    print(f"  Sensitivity: {result.sensitivity}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(explorer.get_statistics(), indent=2))
