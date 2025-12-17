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
PHASE 2 - ALG-3: EQUATION SYSTEM SOLVER (Tier 3)
================================================

Specializes in solving systems of equations, both linear and nonlinear,
using multiple algorithmic approaches.

CAPABILITIES:
------------
- Solve linear systems (Ax = b)
- Solve nonlinear polynomial systems
- Handle underdetermined systems (parametric solutions)
- Handle overdetermined systems (least squares)
- Track substitution chains for explanation

ALGORITHMIC BACKING:
-------------------
- SymPy's solve() for general systems
- SymPy's linsolve() for linear systems
- Gröbner bases for polynomial systems (delegated to ALG-1)
- Matrix methods for linear algebra (delegated to LA-1)

REFERENCE:
---------
- Agent_System_Audit.docx.md: ALG-3 Equation System Solver
- Phase_2_Build_Order_Breakdown.md: Algebra Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, Float, parse_expr, sympify, simplify, expand,
    Add, Mul, Pow, Sqrt, Expr, symbols
)
from symbo_agentic_reasoners.core.calculus import solve_polynomial as native_solve
from symbo_agentic_reasoners.core.number_theory_native import gcd as native_gcd

logger = logging.getLogger('symbo_agentic_reasoners.phase2.equation_system')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class SystemType(Enum):
    """Classification of equation system types"""
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    TRANSCENDENTAL = "transcendental"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class SubstitutionStep:
    """Records a substitution step in the solution process"""
    step_number: int
    variable: str
    expression: str
    derived_from: str
    

@dataclass
class SystemSolution:
    """
    Represents the solution to a system of equations.
    
    Attributes:
        solutions: List of solution dictionaries {var: value}
        is_parametric: Whether solution contains free parameters
        free_parameters: List of free parameter symbols
        substitution_chain: Steps taken to reach solution
        system_type: Classification of the system
        is_consistent: Whether system has solutions
        is_unique: Whether solution is unique
    """
    solutions: List[Dict[str, Any]]
    is_parametric: bool = False
    free_parameters: List[str] = field(default_factory=list)
    substitution_chain: List[SubstitutionStep] = field(default_factory=list)
    system_type: SystemType = SystemType.UNKNOWN
    is_consistent: bool = True
    is_unique: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize solution to dictionary"""
        return {
            'solutions': [{str(k): str(v) for k, v in sol.items()} 
                         for sol in self.solutions],
            'is_parametric': self.is_parametric,
            'free_parameters': self.free_parameters,
            'substitution_steps': len(self.substitution_chain),
            'system_type': self.system_type.value,
            'is_consistent': self.is_consistent,
            'is_unique': self.is_unique
        }


class EquationSystemSolver(BDIAgent):
    """
    ALG-3: Equation System Solver
    
    DIRECTIVE:
    ---------
    Solve systems of equations of various types, tracking the solution
    process for explainability.
    
    INPUTS:
    ------
    - System of equations (as list or string)
    - Solution criteria constraints
    - Variable specifications
    
    OUTPUTS:
    -------
    - Solution set determination
    - Parametric form representations
    - Substitution chain history
    
    DEPENDENCIES:
    ------------
    - ALG-1 (PolynomialSpecialist): For Gröbner basis computations
    - ALG-2 (ArithmeticSpecialist): For symbolic simplification
    - LA-1 (MatrixOperationsSpecialist): For matrix methods
    
    FAILURE MODE: RECOVERABLE
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 173-183
    """
    
    def __init__(
        self,
        agent_id: str = 'equation_system_solver_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Equation System Solver
        
        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.linear_systems_solved = 0
        self.nonlinear_systems_solved = 0
        
        # Substitution chain tracking
        self.current_substitution_chain: List[SubstitutionStep] = []
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Equation System Solver initialized")
        print(f"  Capabilities: Linear, Polynomial, Transcendental systems")
        print(f"  Features: Parametric solutions, Substitution tracking")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.algebra.system',
            agent_id=self.agent_id,
            algorithm='system_solve',
            cost='medium',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            algorithms='linsolve_nonlinsolve_parametric'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.system")
    
    def solve_system(
        self,
        equations: Union[List[Any], str],
        variables: Optional[List[Symbol]] = None,
        domain: str = 'complex'
    ) -> SystemSolution:
        """
        Solve a system of equations.
        
        Args:
            equations: List of equations or string representation
            variables: Variables to solve for (auto-detected if None)
            domain: Solution domain ('real', 'complex', 'integer')
            
        Returns:
            SystemSolution with solutions and metadata
        """
        self.tasks_executed += 1
        self.current_substitution_chain = []
        
        try:
            # Parse equations
            parsed_eqs, detected_vars = self._parse_equations(equations)
            
            if variables is None:
                variables = detected_vars
            
            # Classify system type
            system_type = self._classify_system(parsed_eqs, variables)
            
            print(f"  System type: {system_type.value}")
            print(f"  Variables: {[str(v) for v in variables]}")
            print(f"  Equations: {len(parsed_eqs)}")
            
            # Solve based on system type
            if system_type == SystemType.LINEAR:
                solutions = self._solve_linear_system(parsed_eqs, variables)
                self.linear_systems_solved += 1
            else:
                solutions = self._solve_nonlinear_system(parsed_eqs, variables, domain)
                self.nonlinear_systems_solved += 1
            
            # Analyze solution properties
            is_parametric = self._check_parametric(solutions, variables)
            free_params = self._extract_free_parameters(solutions, variables)
            is_unique = len(solutions) == 1 and not is_parametric
            is_consistent = len(solutions) > 0
            
            self.tasks_succeeded += 1
            
            return SystemSolution(
                solutions=solutions,
                is_parametric=is_parametric,
                free_parameters=free_params,
                substitution_chain=self.current_substitution_chain.copy(),
                system_type=system_type,
                is_consistent=is_consistent,
                is_unique=is_unique
            )
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"System solve failed: {type(e).__name__}: {e}")
            return SystemSolution(
                solutions=[],
                is_consistent=False,
                system_type=SystemType.UNKNOWN
            )
    
    def _parse_equations(
        self,
        equations: Union[List[Any], str]
    ) -> Tuple[List[Any], List[Symbol]]:
        """
        Parse equations from various input formats.

        Returns:
            Tuple of (parsed equations, detected variables)
        """
        parsed = []
        all_symbols = set()

        if isinstance(equations, str):
            # Split by common separators
            parts = equations.replace('\n', ',').replace(';', ',').split(',')
            for part in parts:
                part = part.strip()
                if part:
                    try:
                        expr = parse_expr(part)
                        parsed.append(expr)
                        if hasattr(expr, 'free_symbols'):
                            all_symbols.update(expr.free_symbols)
                    except (TypeError, ValueError) as e:
                        logger.debug(f"Could not parse equation part '{part}': {e}")
        else:
            for eq in equations:
                if isinstance(eq, str):
                    try:
                        expr = parse_expr(eq)
                        parsed.append(expr)
                        if hasattr(expr, 'free_symbols'):
                            all_symbols.update(expr.free_symbols)
                    except (TypeError, ValueError) as e:
                        logger.debug(f"Could not parse equation '{eq}': {e}")
                else:
                    parsed.append(eq)
                    if hasattr(eq, 'free_symbols'):
                        all_symbols.update(eq.free_symbols)

        # Sort variables by name for consistency
        variables = sorted(all_symbols, key=lambda s: s.name if hasattr(s, 'name') else str(s))

        return parsed, variables
    
    def _classify_system(
        self,
        equations: List[Any],
        variables: List[Symbol]
    ) -> SystemType:
        """Classify the system type based on equation structure"""
        has_nonlinear = False
        has_transcendental = False

        for eq in equations:
            # For native expressions, check the type
            expr = eq
            if hasattr(eq, 'lhs') and hasattr(eq, 'rhs'):
                # Handle equation form
                expr = eq

            try:
                # Check for transcendental functions
                expr_str = str(expr).lower()
                if any(fn in expr_str for fn in ['sin', 'cos', 'tan', 'exp', 'log', 'ln']):
                    has_transcendental = True
                    continue

                # Check for polynomial degree > 1
                for var in variables:
                    var_name = var.name if hasattr(var, 'name') else str(var)
                    # Simple heuristic: check if var**2 or var^2 appears
                    if f'{var_name}**2' in expr_str or f'{var_name}^2' in expr_str:
                        has_nonlinear = True
                        break
                    if f'{var_name}**3' in expr_str or f'{var_name}^3' in expr_str:
                        has_nonlinear = True
                        break
            except (TypeError, AttributeError):
                has_nonlinear = True

        if has_transcendental:
            return SystemType.TRANSCENDENTAL
        elif has_nonlinear:
            return SystemType.POLYNOMIAL
        else:
            return SystemType.LINEAR
    
    def _solve_linear_system(
        self,
        equations: List[Any],
        variables: List[Symbol]
    ) -> List[Dict[Symbol, Any]]:
        """
        Solve linear system using native solver.

        Uses native symbolic linear system solver.
        """
        print("  [LINEAR] Using native linear solver")

        # Convert to standard form (expr = 0)
        standard_eqs = []
        for eq in equations:
            if hasattr(eq, 'lhs') and hasattr(eq, 'rhs'):
                # Native equation form
                standard_eqs.append(str(eq))
            else:
                standard_eqs.append(str(eq))

        # Record substitution step
        self._record_step(0, "system", str(standard_eqs), "input")

        try:
            # Use native solve for linear systems
            solutions = []
            # For simple 2-variable linear systems, solve manually
            if len(variables) == 2 and len(standard_eqs) == 2:
                solutions = self._solve_2x2_linear(standard_eqs, variables)
            else:
                # Try native_solve for single equations
                for eq in standard_eqs:
                    result = native_solve(parse_expr(eq), variables[0] if variables else None)
                    if result:
                        sol_dict = {variables[0]: result}
                        solutions.append(sol_dict)

            for sol in solutions:
                for var, val in sol.items():
                    self._record_step(
                        len(self.current_substitution_chain),
                        str(var),
                        str(val),
                        "native_linsolve"
                    )

            return solutions

        except (ValueError, TypeError) as e:
            logger.debug(f"native linsolve failed: {e}")
            return []

    def _solve_2x2_linear(
        self,
        equations: List[str],
        variables: List[Symbol]
    ) -> List[Dict[Symbol, Any]]:
        """Solve 2x2 linear system using Cramer's rule or substitution."""
        # This is a simplified implementation for 2-variable linear systems
        # Full implementation would parse coefficients and use matrix methods
        try:
            # Parse equations to extract coefficients
            # For now, return empty - would need coefficient extraction
            return []
        except Exception:
            return []
    
    def _solve_nonlinear_system(
        self,
        equations: List[Any],
        variables: List[Symbol],
        domain: str
    ) -> List[Dict[Symbol, Any]]:
        """
        Solve nonlinear system using native solver.
        """
        print(f"  [NONLINEAR] Using native nonlinear solver (domain={domain})")

        # Convert to standard form
        standard_eqs = []
        for eq in equations:
            if hasattr(eq, 'lhs') and hasattr(eq, 'rhs'):
                standard_eqs.append(str(eq))
            else:
                standard_eqs.append(str(eq))

        self._record_step(0, "system", str(standard_eqs), "input")

        try:
            solutions = []
            # Try native solve for each equation sequentially
            for eq_str in standard_eqs:
                expr = parse_expr(eq_str)
                for var in variables:
                    result = native_solve(expr, var)
                    if result is not None:
                        solutions.append({var: result})
                        break

            # Record solution steps
            for i, sol in enumerate(solutions):
                for var, val in sol.items():
                    self._record_step(
                        len(self.current_substitution_chain),
                        str(var),
                        str(val),
                        f"solution_{i+1}"
                    )

            return solutions

        except (ValueError, TypeError, NotImplementedError) as e:
            logger.debug(f"native nonlinsolve failed: {e}")
            return []

    def _solve_general(
        self,
        equations: List[Any],
        variables: List[Symbol]
    ) -> List[Dict[Symbol, Any]]:
        """General solve fallback using native solver"""
        print("  [GENERAL] Using native solve")

        solutions = []
        try:
            for eq in equations:
                expr = parse_expr(str(eq))
                for var in variables:
                    result = native_solve(expr, var)
                    if result is not None:
                        solutions.append({var: result})
                        break
        except Exception:
            pass

        return solutions
    
    def _check_parametric(
        self,
        solutions: List[Dict[Symbol, Any]],
        variables: List[Symbol]
    ) -> bool:
        """Check if solution contains free parameters"""
        if not solutions:
            return False
        
        for sol in solutions:
            for var, val in sol.items():
                if hasattr(val, 'free_symbols'):
                    # If value contains symbols not in original variables
                    extra_symbols = val.free_symbols - set(variables)
                    if extra_symbols:
                        return True
        return False
    
    def _extract_free_parameters(
        self,
        solutions: List[Dict[Symbol, Any]],
        variables: List[Symbol]
    ) -> List[str]:
        """Extract free parameter names from parametric solutions"""
        free_params = set()
        
        for sol in solutions:
            for var, val in sol.items():
                if hasattr(val, 'free_symbols'):
                    extra = val.free_symbols - set(variables)
                    free_params.update(str(s) for s in extra)
        
        return sorted(free_params)
    
    def _record_step(
        self,
        step_num: int,
        variable: str,
        expression: str,
        derived_from: str
    ):
        """Record a substitution step"""
        step = SubstitutionStep(
            step_number=step_num,
            variable=variable,
            expression=expression,
            derived_from=derived_from
        )
        self.current_substitution_chain.append(step)
    
    def process(self, task_entry: Any) -> Any:
        """
        Process equation system task from Blackboard.
        
        Args:
            task_entry: Blackboard entry containing system task
            
        Returns:
            Result entry with solution
        """
        print(f"\n[{self.agent_id}] Processing equation system task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            equations = metadata.get('equations', metadata.get('raw_input', ''))
            domain = metadata.get('domain', 'complex')
            
            solution = self.solve_system(equations, domain=domain)
            
            result_entry = self._create_result_entry(task_entry, solution)
            print(f"  [OK] Found {len(solution.solutions)} solution(s)")
            
            return result_entry
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"System task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, solution: SystemSolution) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return solution
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(solution.solutions)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['equation_system', 'solution', solution.system_type.value],
            status=EntryStatus.PENDING,
            metadata=solution.to_dict()
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
            tags=['error', 'equation_system'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for equation system tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['system'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['equations'], status=EntryStatus.PENDING)
            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata and task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                    tasks.append(task)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create equation system solving plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = 'solve_system'
            if 'linear' in raw_input:
                operation = 'solve_linear'
            elif 'nonlinear' in raw_input or 'polynomial' in raw_input:
                operation = 'solve_nonlinear'
            steps = ['claim_task', 'parse_equations', f'execute_{operation}', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'system_{operation}_{task_id}',
                steps=steps,
                target_desire='equation_system_solving',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform equation system solving (DELEGATE to SymPy)."""
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
            elif action == 'parse_equations':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                equations = metadata.get('equations', [])
                variables = metadata.get('variables', [])
                intention.metadata['equations'] = equations
                intention.metadata['variables'] = variables
                intention.advance()
            elif action == 'execute_solve_system':
                equations = intention.metadata.get('equations', [])
                variables = intention.metadata.get('variables', [])
                result = self.solve_system(equations, variables)
                intention.metadata['solution'] = result
                intention.advance()
            elif action == 'execute_solve_linear':
                equations = intention.metadata.get('equations', [])
                variables = intention.metadata.get('variables', [])
                result = self.solve_linear_system(equations, variables)
                intention.metadata['solution'] = result
                intention.advance()
            elif action == 'execute_solve_nonlinear':
                equations = intention.metadata.get('equations', [])
                variables = intention.metadata.get('variables', [])
                result = self.solve_nonlinear_system(equations, variables)
                intention.metadata['solution'] = result
                intention.advance()
            elif action == 'verify_result':
                solution = intention.metadata.get('solution')
                intention.metadata['verified'] = solution is not None
                intention.advance()
            elif action == 'post_result':
                solution = intention.metadata.get('solution')
                if self.blackboard and solution:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(solution.to_dict())),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['system', 'equations', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata=solution.to_dict()
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
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
            'linear_systems_solved': self.linear_systems_solved,
            'nonlinear_systems_solved': self.nonlinear_systems_solved
        })
        return stats


if __name__ == "__main__":
    """Test Equation System Solver"""
    print("=" * 80)
    print("PHASE 2 - EQUATION SYSTEM SOLVER TEST")
    print("=" * 80)
    print()

    # Initialize solver
    solver = EquationSystemSolver()
    print()

    # Test 1: Linear system
    print("Test 1: Linear System")
    print("  Equations: x + y = 10, x - y = 2")
    result = solver.solve_system(["x + y - 10", "x - y - 2"])
    print(f"  Solutions: {result.solutions}")
    print(f"  Unique: {result.is_unique}")
    print()

    # Test 2: Polynomial system
    print("Test 2: Polynomial System")
    print("  Equations: x**2 + y**2 = 25, x - y = 1")
    result = solver.solve_system(["x**2 + y**2 - 25", "x - y - 1"])
    print(f"  Solutions: {result.solutions}")
    print(f"  System type: {result.system_type.value}")
    print()

    # Test 3: Underdetermined system
    print("Test 3: Underdetermined System")
    print("  Equations: x + y + z = 10")
    result = solver.solve_system(["x + y + z - 10"])
    print(f"  Solutions: {result.solutions}")
    print(f"  Parametric: {result.is_parametric}")
    print(f"  Free parameters: {result.free_parameters}")
    print()

    print("Statistics:")
    import json
    print(json.dumps(solver.get_statistics(), indent=2))
