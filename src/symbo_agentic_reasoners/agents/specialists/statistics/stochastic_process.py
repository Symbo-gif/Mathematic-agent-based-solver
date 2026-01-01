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

"""
PHASE 2 - PROB-4: STOCHASTIC PROCESS ANALYZER (Tier 3)
======================================================

Specializes in stochastic process analysis including Markov chains,
Poisson processes, and Brownian motion.

CAPABILITIES:
------------
- Markov chain analysis (discrete and continuous time)
- Stationary distribution computation
- Transition matrix operations
- Poisson process simulation and analysis
- Brownian motion/Wiener process modeling
- Parameter estimation for stochastic models

ALGORITHMIC BACKING:
-------------------
- SymPy for symbolic probability
- NumPy for numerical computations
- Custom implementations for stochastic models

REFERENCE:
---------
- Agent_System_Audit.docx.md: PROB-4 Stochastic Process Analyzer
- Phase_2_Build_Order_Breakdown.md: Probability & Statistics Team
"""

import sys
import os
import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, symbols, parse_expr, Expr, Integer, Float, Rational,
    Add, Mul, Pow, Exp, Log, Sqrt, pi
)

# Try to import numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

logger = logging.getLogger('symbo_agentic_reasoners.phase2.stochastic_process')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class ProcessType(Enum):
    """Types of stochastic processes"""
    DISCRETE_MARKOV = "discrete_markov"
    CONTINUOUS_MARKOV = "continuous_markov"
    POISSON = "poisson"
    BROWNIAN = "brownian"
    RANDOM_WALK = "random_walk"
    BIRTH_DEATH = "birth_death"


@dataclass
class MarkovChainProperties:
    """
    Properties of a Markov chain.
    
    Attributes:
        num_states: Number of states
        is_irreducible: Whether all states communicate
        is_aperiodic: Whether chain is aperiodic
        is_ergodic: Whether chain is ergodic (irreducible + aperiodic)
        stationary_distribution: Stationary distribution if exists
        absorption_probabilities: Absorption probabilities for absorbing chains
    """
    num_states: int
    is_irreducible: bool = True
    is_aperiodic: bool = True
    is_ergodic: bool = True
    stationary_distribution: Optional[List[float]] = None
    absorption_probabilities: Optional[Dict[int, float]] = None
    mean_first_passage_times: Optional[Dict[Tuple[int, int], float]] = None
    
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
            'num_states': self.num_states,
            'is_irreducible': self.is_irreducible,
            'is_aperiodic': self.is_aperiodic,
            'is_ergodic': self.is_ergodic,
            'has_stationary': self.stationary_distribution is not None
        }


@dataclass
class ProcessAnalysisResult:
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    """Result of stochastic process analysis"""
    process_type: ProcessType
    parameters: Dict[str, Any]
    predictions: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    
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
            'process_type': self.process_type.value,
            'parameters': {k: str(v) for k, v in self.parameters.items()},
            'predictions': {k: str(v) for k, v in self.predictions.items()},
            'properties': self.properties
        }


class StochasticProcessAnalyzer(BDIAgent):
    """
    PROB-4: Stochastic Process Analyzer
    
    DIRECTIVE:
    ---------
    Analyze stochastic processes including Markov chains, Poisson processes,
    and Brownian motion.
    
    INPUTS:
    ------
    - Time series data
    - Stochastic process models
    - Parameter specifications
    
    OUTPUTS:
    -------
    - Process parameter estimation
    - Prediction results
    - Process properties
    
    DEPENDENCIES:
    ------------
    - PROB-1 (DistributionSpecialist): For distribution fitting
    - CAL-5 (ODESolver): For continuous-time processes
    
    FAILURE MODE: RECOVERABLE
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 327-337
    """
    
    def __init__(
        self,
        agent_id: str = 'stochastic_process_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Stochastic Process Analyzer
        
        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Process state history
        self.process_history: Dict[str, List[Any]] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.markov_chains_analyzed = 0
        self.processes_simulated = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Stochastic Process Analyzer initialized")
        print(f"  Capabilities: Markov chains, Poisson, Brownian motion")
        print(f"  NumPy available: {HAS_NUMPY}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.probability.stochastic',
            agent_id=self.agent_id,
            algorithm='stochastic_analysis',
            cost='high',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            algorithms='markov_poisson_brownian'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.probability.stochastic")
    
    def analyze_markov_chain(
        self,
        transition_matrix: Union[List[List[float]], 'np.ndarray']
    ) -> Tuple[MarkovChainProperties, 'np.ndarray']:
        """
        Analyze a discrete-time Markov chain.

        Uses numpy for matrix operations - NO SYMPY.

        Args:
            transition_matrix: Row-stochastic transition matrix P

        Returns:
            Tuple of (MarkovChainProperties, transition matrix as numpy array)
        """
        self.tasks_executed += 1
        self.markov_chains_analyzed += 1

        try:
            # Require numpy for matrix operations
            if not HAS_NUMPY:
                raise ImportError("NumPy required for Markov chain analysis")

            # Convert to numpy array
            if isinstance(transition_matrix, np.ndarray):
                P = transition_matrix.astype(float)
            else:
                P = np.array(transition_matrix, dtype=float)
            
            n = P.shape[0]

            print(f"  Analyzing {n}-state Markov chain")

            # Check row-stochastic property
            for i in range(n):
                row_sum = P[i, :].sum()
                if abs(row_sum - 1) > 1e-10:
                    logger.warning(f"Row {i} sum = {row_sum}, not 1")

            # Compute stationary distribution
            # Solve pi P = pi, or (P^T - I) pi = 0 with sum(pi) = 1
            stationary = self._compute_stationary_distribution(P)

            # Check irreducibility (simplified check)
            is_irreducible = self._check_irreducibility(P)

            # Check aperiodicity (simplified)
            is_aperiodic = self._check_aperiodicity(P)

            properties = MarkovChainProperties(
                num_states=n,
                is_irreducible=is_irreducible,
                is_aperiodic=is_aperiodic,
                is_ergodic=is_irreducible and is_aperiodic,
                stationary_distribution=stationary
            )

            self.tasks_succeeded += 1
            return properties, P

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Markov chain analysis failed: {type(e).__name__}: {e}")
            raise
    
    def _compute_stationary_distribution(self, P: 'np.ndarray') -> Optional[List[float]]:
        """Compute stationary distribution of Markov chain using numpy - NO SYMPY"""
        try:
            if not HAS_NUMPY:
                return None

            n = P.shape[0]

            # Set up system: (P^T - I) pi = 0, sum(pi) = 1
            # We replace last equation with normalization
            A = P.T - np.eye(n)

            # Replace last row with normalization constraint
            A[n-1, :] = 1

            b = np.zeros(n)
            b[n-1] = 1

            # Solve using numpy
            try:
                pi = np.linalg.solve(A, b)

                # Verify non-negative
                if np.all(pi >= -1e-10):
                    return [max(0, x) for x in pi.tolist()]
            except np.linalg.LinAlgError as e:
                logger.debug(f"Direct solve failed: {e}")

            # Fallback: power iteration
            pi = np.ones(n) / n
            for _ in range(1000):
                pi_new = pi @ P
                if np.allclose(pi, pi_new, atol=1e-10):
                    break
                pi = pi_new
            return list(pi)

        except Exception as e:
            logger.debug(f"Stationary distribution computation failed: {e}")
            return None
    
    def _check_irreducibility(self, P: 'np.ndarray') -> bool:
        """Check if Markov chain is irreducible (all states communicate) - NO SYMPY"""
        try:
            if not HAS_NUMPY:
                return True  # Assume irreducible if no numpy

            n = P.shape[0]

            # Check if P^(n-1) has all positive entries
            # (sufficient but not necessary condition)
            P_power = np.linalg.matrix_power(P, n - 1) if n > 1 else P

            return np.all(P_power > 0)

        except Exception as e:
            logger.debug(f"Irreducibility check failed: {e}")
            return True  # Assume irreducible

    def _check_aperiodicity(self, P: 'np.ndarray') -> bool:
        """Check if Markov chain is aperiodic - NO SYMPY"""
        try:
            if not HAS_NUMPY:
                return True  # Assume aperiodic if no numpy

            n = P.shape[0]

            # A chain is aperiodic if gcd of return times is 1
            # Quick check: if any state has self-loop, likely aperiodic
            for i in range(n):
                if P[i, i] > 0:
                    return True

            return False  # Conservative

        except Exception as e:
            logger.debug(f"Aperiodicity check failed: {e}")
            return True  # Assume aperiodic
    
    def transition_probability(
        self,
        P: 'np.ndarray',
        steps: int,
        start: int,
        end: int
    ) -> float:
        """
        Compute n-step transition probability P^n(start, end).

        Uses numpy for matrix power - NO SYMPY.

        Args:
            P: Transition matrix (numpy array)
            steps: Number of steps
            start: Starting state
            end: Ending state

        Returns:
            Transition probability
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for transition probability")

            # Convert to numpy if needed
            if not isinstance(P, np.ndarray):
                P = np.array(P, dtype=float)

            P_n = np.linalg.matrix_power(P, steps)
            result = float(P_n[start, end])

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Transition probability failed: {type(e).__name__}: {e}")
            raise
    
    def poisson_process_analysis(
        self,
        rate: float,
        time_horizon: float,
        events: Optional[List[float]] = None
    ) -> ProcessAnalysisResult:
        """
        Analyze a Poisson process.

        Uses native math functions - NO SYMPY.

        Args:
            rate: Event rate lambda
            time_horizon: Time horizon T
            events: Optional observed event times

        Returns:
            ProcessAnalysisResult with Poisson properties
        """
        self.tasks_executed += 1

        try:
            # Expected number of events
            expected_count = rate * time_horizon

            # Probability of k events in [0, T]
            # P(k) = (lambda*T)^k * e^(-lambda*T) / k!
            lam = rate * time_horizon

            # If events provided, estimate rate
            estimated_rate = None
            if events:
                num_events = len(events)
                if time_horizon > 0:
                    estimated_rate = num_events / time_horizon

            parameters = {
                'rate': rate,
                'time_horizon': time_horizon,
                'expected_count': expected_count,
                'variance': expected_count  # Var = lambda*T for Poisson
            }

            if estimated_rate:
                parameters['estimated_rate'] = estimated_rate

            predictions = {
                'prob_0_events': math.exp(-lam),
                'prob_1_event': lam * math.exp(-lam),
                'mean_interarrival': 1 / rate if rate > 0 else float('inf')
            }

            properties = {
                'is_stationary': True,
                'independent_increments': True,
                'orderly': True  # P(2+ events in dt) = o(dt)
            }

            self.tasks_succeeded += 1

            return ProcessAnalysisResult(
                process_type=ProcessType.POISSON,
                parameters=parameters,
                predictions=predictions,
                properties=properties
            )

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Poisson analysis failed: {type(e).__name__}: {e}")
            raise
    
    def brownian_motion_properties(
        self,
        drift: float = 0.0,
        volatility: float = 1.0,
        initial_value: float = 0.0,
        time: float = 1.0
    ) -> ProcessAnalysisResult:
        """
        Analyze Brownian motion / Wiener process properties.

        Uses native math functions - NO SYMPY.

        dX = mu dt + sigma dW

        Args:
            drift: Drift coefficient mu
            volatility: Volatility coefficient sigma
            initial_value: Initial value X(0)
            time: Time point t

        Returns:
            ProcessAnalysisResult with Brownian motion properties
        """
        self.tasks_executed += 1

        try:
            # X(t) ~ N(X(0) + mu*t, sigma^2 * t)
            mean = initial_value + drift * time
            variance = volatility ** 2 * time
            std_dev = volatility * math.sqrt(time)

            parameters = {
                'drift': drift,
                'volatility': volatility,
                'initial_value': initial_value,
                'time': time
            }

            predictions = {
                'expected_value': mean,
                'variance': variance,
                'std_dev': std_dev,
                'prob_positive': 0.5 if mean == 0 else None  # Simplified
            }

            properties = {
                'continuous_paths': True,
                'independent_increments': True,
                'stationary_increments': True,
                'gaussian_increments': True,
                'quadratic_variation': volatility ** 2 * time
            }

            self.tasks_succeeded += 1

            return ProcessAnalysisResult(
                process_type=ProcessType.BROWNIAN,
                parameters=parameters,
                predictions=predictions,
                properties=properties
            )

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Brownian motion analysis failed: {type(e).__name__}: {e}")
            raise
    
    def simulate_random_walk(
        self,
        steps: int,
        p_up: float = 0.5,
        step_size: float = 1.0
    ) -> List[float]:
        """
        Simulate a simple random walk.
        
        Args:
            steps: Number of steps
            p_up: Probability of up move
            step_size: Size of each step
            
        Returns:
            List of positions
        """
        self.tasks_executed += 1
        self.processes_simulated += 1
        
        try:
            if HAS_NUMPY:
                moves = np.random.choice(
                    [step_size, -step_size],
                    size=steps,
                    p=[p_up, 1 - p_up]
                )
                positions = np.cumsum(np.concatenate([[0], moves]))
                result = positions.tolist()
            else:
                import random
                positions = [0.0]
                for _ in range(steps):
                    move = step_size if random.random() < p_up else -step_size
                    positions.append(positions[-1] + move)
                result = positions
            
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Random walk simulation failed: {type(e).__name__}: {e}")
            raise
    
    def estimate_parameters(
        self,
        time_series: List[float],
        process_type: ProcessType
    ) -> Dict[str, float]:
        """
        Estimate process parameters from time series data.
        
        Args:
            time_series: Observed values
            process_type: Type of process to fit
            
        Returns:
            Estimated parameters
        """
        self.tasks_executed += 1
        
        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for parameter estimation")
            
            data = np.array(time_series)
            
            if process_type == ProcessType.RANDOM_WALK:
                # Estimate drift and volatility from increments
                increments = np.diff(data)
                drift = np.mean(increments)
                volatility = np.std(increments)
                
                result = {
                    'drift': float(drift),
                    'volatility': float(volatility),
                    'samples': len(increments)
                }
                
            elif process_type == ProcessType.POISSON:
                # Estimate rate from event count
                # Assume data is event counts per unit time
                rate = np.mean(data)
                
                result = {
                    'rate': float(rate),
                    'variance': float(np.var(data)),
                    'samples': len(data)
                }
                
            else:
                # Generic: compute mean and variance
                result = {
                    'mean': float(np.mean(data)),
                    'variance': float(np.var(data)),
                    'samples': len(data)
                }
            
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Parameter estimation failed: {type(e).__name__}: {e}")
            raise
    
    def process(self, task_entry: Any) -> Any:
        """Process stochastic process task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing stochastic process task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'analyze_markov')
            
            if operation == 'analyze_markov':
                matrix = metadata.get('transition_matrix')
                properties, _ = self.analyze_markov_chain(matrix)
                result = properties.to_dict()
                if properties.stationary_distribution:
                    result['stationary_distribution'] = properties.stationary_distribution
                    
            elif operation == 'poisson':
                rate = metadata.get('rate', 1.0)
                horizon = metadata.get('time_horizon', 1.0)
                analysis = self.poisson_process_analysis(rate, horizon)
                result = analysis.to_dict()
                
            elif operation == 'brownian':
                drift = metadata.get('drift', 0.0)
                vol = metadata.get('volatility', 1.0)
                analysis = self.brownian_motion_properties(drift, vol)
                result = analysis.to_dict()
                
            elif operation == 'random_walk':
                steps = metadata.get('steps', 100)
                p_up = metadata.get('p_up', 0.5)
                path = self.simulate_random_walk(steps, p_up)
                result = {
                    'path_length': len(path),
                    'final_position': path[-1],
                    'max_position': max(path),
                    'min_position': min(path)
                }
                
            elif operation == 'estimate':
                data = metadata.get('time_series', [])
                proc_type = ProcessType(metadata.get('process_type', 'random_walk'))
                result = self.estimate_parameters(data, proc_type)
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Stochastic task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['stochastic', 'probability'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'stochastic'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for stochastic process tasks"""
        if not self.blackboard:
            return
        try:
            stoch_tasks = self.blackboard.query_entries(tags=['stochastic'], status=EntryStatus.PENDING) + \
                         self.blackboard.query_entries(tags=['markov'], status=EntryStatus.PENDING)
            delegated_tasks = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in stoch_tasks:
                        stoch_tasks.append(task)
            for task in stoch_tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self):
        """DELIBERATE: Generate computation plans for stochastic processes"""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'analyze_markov')
            steps = ['claim_task', 'parse_parameters', 'compute_process', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'stochastic_{operation}_{task_id}',
                steps=steps,
                target_desire='stochastic_analysis',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute stochastic process computation step"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()
            elif action == 'parse_parameters':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['params'] = metadata
                intention.advance()
            elif action == 'compute_process':
                operation = intention.metadata.get('operation', 'analyze_markov')
                params = intention.metadata.get('params', {})
                if operation == 'analyze_markov':
                    matrix = params.get('transition_matrix', [[0.7, 0.3], [0.4, 0.6]])
                    properties, _ = self.analyze_markov_chain(matrix)
                    result = properties.to_dict()
                    if properties.stationary_distribution:
                        result['stationary_distribution'] = properties.stationary_distribution
                elif operation == 'poisson':
                    rate = params.get('rate', 1.0)
                    horizon = params.get('time_horizon', 1.0)
                    analysis = self.poisson_process_analysis(rate, horizon)
                    result = analysis.to_dict()
                elif operation == 'brownian':
                    drift = params.get('drift', 0.0)
                    vol = params.get('volatility', 1.0)
                    analysis = self.brownian_motion_properties(drift, vol)
                    result = analysis.to_dict()
                elif operation == 'random_walk':
                    steps = params.get('steps', 100)
                    p_up = params.get('p_up', 0.5)
                    path = self.simulate_random_walk(steps, p_up)
                    result = {'path_length': len(path), 'final_position': path[-1], 'max': max(path), 'min': min(path)}
                else:
                    result = {'operation': operation, 'computed': False}
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()
            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None
                intention.metadata['verified'] = verified
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['stochastic', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': str(result), 'task_id': task_id}
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.add_belief(f'completed_task_{task_id}', True)
                self.remove_belief(f'claimed_task_{task_id}')
                self.tasks_succeeded += 1
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')
            self.tasks_failed += 1
            while not intention.is_complete():
                intention.advance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'markov_chains_analyzed': self.markov_chains_analyzed,
            'processes_simulated': self.processes_simulated,
            'numpy_available': HAS_NUMPY
        })
        return stats


if __name__ == "__main__":
    """Test Stochastic Process Analyzer"""
    print("=" * 80)
    print("PHASE 2 - STOCHASTIC PROCESS ANALYZER TEST")
    print("=" * 80)
    print()
    
    # Initialize analyzer
    analyzer = StochasticProcessAnalyzer()
    print()
    
    # Test 1: Markov chain analysis
    print("Test 1: Markov Chain Analysis")
    P = [[0.7, 0.2, 0.1],
         [0.3, 0.5, 0.2],
         [0.2, 0.3, 0.5]]
    properties, _ = analyzer.analyze_markov_chain(P)
    print(f"  States: {properties.num_states}")
    print(f"  Ergodic: {properties.is_ergodic}")
    print(f"  Stationary: {properties.stationary_distribution}")
    print()
    
    # Test 2: Poisson process
    print("Test 2: Poisson Process Analysis")
    result = analyzer.poisson_process_analysis(rate=5.0, time_horizon=2.0)
    print(f"  Rate: {result.parameters['rate']}")
    print(f"  Expected events: {result.parameters['expected_count']}")
    print(f"  P(0 events): {result.predictions['prob_0_events']:.4f}")
    print()
    
    # Test 3: Brownian motion
    print("Test 3: Brownian Motion Properties")
    result = analyzer.brownian_motion_properties(drift=0.1, volatility=0.2, time=1.0)
    print(f"  Expected value: {result.predictions['expected_value']}")
    print(f"  Variance: {result.predictions['variance']}")
    print()
    
    # Test 4: Random walk simulation
    print("Test 4: Random Walk Simulation")
    path = analyzer.simulate_random_walk(100, p_up=0.5)
    print(f"  Steps: {len(path) - 1}")
    print(f"  Final position: {path[-1]}")
    print(f"  Max: {max(path)}, Min: {min(path)}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(analyzer.get_statistics(), indent=2))
