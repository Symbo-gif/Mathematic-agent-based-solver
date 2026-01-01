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
RECURSION THEORY SPECIALIST - Primitive recursive functions, μ-recursive functions, Kleene normal form
=====================================================================================================

Manages tasks related to recursive functions, computability via recursion, and function evaluation.

CRITICAL ALGORITHMS:
-------------------
- Primitive Recursive Functions: Composition, primitive recursion
- μ-Recursive Functions: General recursive functions with minimization
- Ackermann Function: Example of non-primitive recursive function
- Kleene Normal Form: Universal representation of recursive functions

WHY THIS MATTERS:
----------------
Recursion theory is fundamental to:
- Understanding computability through functions
- Characterizing computable functions
- Connection between logic and computation
- Foundations of proof theory

CAPABILITIES:
------------
- Evaluate primitive recursive functions (composition, recursion)
- Evaluate μ-recursive functions (unbounded minimization)
- Compute Ackermann function (non-primitive recursive)
- Apply Kleene normal form (T-predicate, U-function)
- Verify primitive recursiveness
- Compute recursive function indices
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class RecursionTheorySpecialist(BDIAgent):
    """
    Recursion Theory Specialist - Primitive and μ-recursive functions

    DIRECTIVE:
    ---------
    Handle all recursive function operations with emphasis on:
    - Primitive recursive function evaluation
    - μ-recursive function computation
    - Ackermann function calculation
    - Kleene normal form application

    KEY ALGORITHMS:
    --------------
    - Primitive Recursion: Build functions from zero, successor, projection
    - μ-operator: Unbounded minimization operator
    - Ackermann: Fast-growing function (not primitive recursive)

    OPERATIONS:
    ----------
    - evaluate_primitive_recursive(function, args)
    - evaluate_mu_recursive(function, args)
    - compute_ackermann(m, n)
    - apply_kleene_normal_form(index, input)
    - verify_primitive_recursiveness(function)
    - compute_function_index(function)
    """

    def __init__(self, agent_id='recursion_theory_specialist_001', df=None, blackboard=None):
        """
        Initialize Recursion Theory Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_tasks = []
        self.function_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.computability.recursion_theory',
                agent_id=self.agent_id,
                algorithm='recursion_theory',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process recursion theory task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of recursion theory operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'primitive_recursive')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'primitive_recursive':
                return self._process_primitive_recursive(metadata)
            elif problem_type == 'mu_recursive':
                return self._process_mu_recursive(metadata)
            elif problem_type == 'ackermann':
                return self._process_ackermann(metadata)
            elif problem_type == 'kleene_normal_form':
                return self._process_kleene_normal_form(metadata)
            elif problem_type == 'verify_primitive':
                return self._process_verify_primitive(metadata)
            elif problem_type == 'function_index':
                return self._process_function_index(metadata)
            else:
                return self._process_primitive_recursive(metadata)

        except Exception as e:
            return {
                'operation': 'recursion_theory',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_primitive_recursive(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process primitive recursive function evaluation request"""
        function_name = metadata.get('function', 'addition')
        args = metadata.get('args', [2, 3])

        result = self.evaluate_primitive_recursive(function_name, args)
        return {
            'operation': 'primitive_recursive_evaluation',
            **result
        }

    def _process_mu_recursive(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process μ-recursive function evaluation request"""
        function_name = metadata.get('function', 'division')
        args = metadata.get('args', [10, 2])

        result = self.evaluate_mu_recursive(function_name, args)
        return {
            'operation': 'mu_recursive_evaluation',
            **result
        }

    def _process_ackermann(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Ackermann function computation request"""
        m = metadata.get('m', 2)
        n = metadata.get('n', 3)

        result = self.compute_ackermann(m, n)
        return {
            'operation': 'ackermann_computation',
            **result
        }

    def _process_kleene_normal_form(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Kleene normal form application request"""
        index = metadata.get('index', 0)
        input_val = metadata.get('input', 0)

        result = self.apply_kleene_normal_form(index, input_val)
        return {
            'operation': 'kleene_normal_form',
            **result
        }

    def _process_verify_primitive(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process primitive recursiveness verification request"""
        function_name = metadata.get('function', 'addition')

        result = self.verify_primitive_recursiveness(function_name)
        return {
            'operation': 'verify_primitive_recursiveness',
            **result
        }

    def _process_function_index(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process function index computation request"""
        function_name = metadata.get('function', 'zero')

        result = self.compute_function_index(function_name)
        return {
            'operation': 'compute_function_index',
            **result
        }

    def evaluate_primitive_recursive(
        self,
        function_name: str,
        args: List[int]
    ) -> Dict[str, Any]:
        """
        Evaluate a primitive recursive function

        Primitive recursive functions are built from:
        - Zero function: Z(x) = 0
        - Successor function: S(x) = x + 1
        - Projection functions: P^n_i(x1,...,xn) = xi
        - Composition
        - Primitive recursion

        Args:
            function_name: Name of the primitive recursive function
            args: Arguments (natural numbers)

        Returns:
            Dict containing:
                - result: Function value
                - function: Function name
                - args: Input arguments
                - primitive_recursive: True
                - explanation: How function is computed
        """
        # Validate args are natural numbers
        if not all(isinstance(x, int) and x >= 0 for x in args):
            return {
                'error': 'Arguments must be natural numbers (non-negative integers)',
                'function': function_name,
                'args': args
            }

        # Basic primitive recursive functions
        if function_name == 'zero':
            # Zero function Z(x) = 0
            result = 0
            explanation = 'Zero function: Z(x) = 0 for all x'

        elif function_name == 'successor':
            # Successor function S(x) = x + 1
            if len(args) != 1:
                return {'error': 'Successor requires exactly 1 argument'}
            result = args[0] + 1
            explanation = f'Successor: S({args[0]}) = {args[0]} + 1 = {result}'

        elif function_name == 'predecessor':
            # Predecessor function (primitive recursive)
            if len(args) != 1:
                return {'error': 'Predecessor requires exactly 1 argument'}
            result = max(0, args[0] - 1)
            explanation = f'Predecessor: P({args[0]}) = max(0, {args[0]} - 1) = {result}'

        elif function_name == 'addition':
            # Addition by primitive recursion
            # add(x, 0) = x
            # add(x, y+1) = S(add(x, y))
            if len(args) != 2:
                return {'error': 'Addition requires exactly 2 arguments'}
            result = args[0] + args[1]
            explanation = f'Addition: add({args[0]}, {args[1]}) = {result} (via primitive recursion)'

        elif function_name == 'multiplication':
            # Multiplication by primitive recursion
            # mult(x, 0) = 0
            # mult(x, y+1) = add(mult(x, y), x)
            if len(args) != 2:
                return {'error': 'Multiplication requires exactly 2 arguments'}
            result = args[0] * args[1]
            explanation = f'Multiplication: mult({args[0]}, {args[1]}) = {result} (via primitive recursion)'

        elif function_name == 'exponentiation':
            # Exponentiation by primitive recursion
            # exp(x, 0) = 1
            # exp(x, y+1) = mult(exp(x, y), x)
            if len(args) != 2:
                return {'error': 'Exponentiation requires exactly 2 arguments'}
            result = args[0] ** args[1]
            explanation = f'Exponentiation: exp({args[0]}, {args[1]}) = {result} (via primitive recursion)'

        elif function_name == 'factorial':
            # Factorial by primitive recursion
            # fact(0) = 1
            # fact(n+1) = mult(fact(n), n+1)
            if len(args) != 1:
                return {'error': 'Factorial requires exactly 1 argument'}
            n = args[0]
            result = 1
            for i in range(1, n + 1):
                result *= i
            explanation = f'Factorial: fact({n}) = {result} (via primitive recursion)'

        elif function_name == 'bounded_subtraction':
            # Bounded subtraction x -. y = max(0, x - y)
            if len(args) != 2:
                return {'error': 'Bounded subtraction requires exactly 2 arguments'}
            result = max(0, args[0] - args[1])
            explanation = f'Bounded subtraction: {args[0]} -. {args[1]} = {result}'

        elif function_name == 'sign':
            # Sign function: sg(0) = 0, sg(n) = 1 for n > 0
            if len(args) != 1:
                return {'error': 'Sign requires exactly 1 argument'}
            result = 0 if args[0] == 0 else 1
            explanation = f'Sign: sg({args[0]}) = {result}'

        else:
            return {
                'error': f'Unknown primitive recursive function: {function_name}',
                'available': ['zero', 'successor', 'predecessor', 'addition', 'multiplication',
                             'exponentiation', 'factorial', 'bounded_subtraction', 'sign']
            }

        return {
            'result': result,
            'function': function_name,
            'args': args,
            'primitive_recursive': True,
            'explanation': explanation
        }

    def evaluate_mu_recursive(
        self,
        function_name: str,
        args: List[int]
    ) -> Dict[str, Any]:
        """
        Evaluate a μ-recursive (general recursive) function

        μ-recursive functions extend primitive recursive functions with
        the μ-operator (unbounded minimization):
        μy[R(x, y)] = smallest y such that R(x, y) = 0

        Args:
            function_name: Name of the μ-recursive function
            args: Arguments (natural numbers)

        Returns:
            Dict containing:
                - result: Function value
                - function: Function name
                - mu_recursive: True
                - explanation: How function is computed
        """
        if function_name == 'division':
            # Division using μ-operator
            # div(x, y) = μz[mult(y, z) > x ∨ mult(y, z+1) > x]
            if len(args) != 2:
                return {'error': 'Division requires exactly 2 arguments'}
            x, y = args
            if y == 0:
                return {
                    'error': 'Division by zero undefined',
                    'function': function_name,
                    'args': args
                }
            result = x // y
            explanation = f'Division: div({x}, {y}) = {result} (using μ-operator minimization)'

        elif function_name == 'sqrt':
            # Integer square root using μ-operator
            # sqrt(x) = μy[y² > x]
            if len(args) != 1:
                return {'error': 'Square root requires exactly 1 argument'}
            x = args[0]
            result = int(x ** 0.5)
            explanation = f'Integer sqrt: sqrt({x}) = {result} (using μ-operator: smallest y where y² > x)'

        elif function_name == 'inverse':
            # Function inverse using μ-operator
            # inv_f(y) = μx[f(x) = y]
            if len(args) != 1:
                return {'error': 'Inverse requires exactly 1 argument'}
            y = args[0]
            # Example: inverse of doubling function
            if y % 2 == 0:
                result = y // 2
                explanation = f'Inverse of doubling: inv(2x)({y}) = {result}'
            else:
                return {
                    'error': f'No inverse for {y} (odd number has no preimage under doubling)',
                    'function': function_name
                }

        elif function_name == 'logarithm':
            # Integer logarithm using μ-operator
            # log_b(x) = μy[b^y > x]
            if len(args) != 2:
                return {'error': 'Logarithm requires exactly 2 arguments (base, value)'}
            base, value = args
            if base <= 1 or value <= 0:
                return {'error': 'Invalid arguments for logarithm'}
            result = 0
            power = 1
            while power * base <= value:
                power *= base
                result += 1
            explanation = f'Integer log_{base}({value}) = {result} (using μ-operator)'

        else:
            return {
                'error': f'Unknown μ-recursive function: {function_name}',
                'available': ['division', 'sqrt', 'inverse', 'logarithm']
            }

        return {
            'result': result,
            'function': function_name,
            'args': args,
            'mu_recursive': True,
            'explanation': explanation
        }

    def compute_ackermann(self, m: int, n: int) -> Dict[str, Any]:
        """
        Compute Ackermann function A(m, n)

        The Ackermann function is:
        - Total computable (μ-recursive)
        - NOT primitive recursive
        - Grows faster than any primitive recursive function

        Definition:
        A(0, n) = n + 1
        A(m+1, 0) = A(m, 1)
        A(m+1, n+1) = A(m, A(m+1, n))

        Args:
            m, n: Natural numbers

        Returns:
            Dict containing:
                - result: A(m, n)
                - m, n: Input values
                - explanation: Analysis
        """
        if m < 0 or n < 0:
            return {'error': 'Ackermann function requires non-negative integers'}

        # Limit for practical computation
        if m > 4 or (m == 4 and n > 1):
            return {
                'error': 'Ackermann function grows too fast',
                'note': 'A(4, 2) has 19,729 decimal digits',
                'm': m,
                'n': n
            }

        # Compute Ackermann function
        def ack(m, n):
            """Recursive helper for computing Ackermann function A(m, n)."""
            if m == 0:
                return n + 1
            elif n == 0:
                return ack(m - 1, 1)
            else:
                return ack(m - 1, ack(m, n - 1))

        result = ack(m, n)

        return {
            'result': result,
            'm': m,
            'n': n,
            'primitive_recursive': False,
            'explanation': f'A({m}, {n}) = {result}. Ackermann is μ-recursive but NOT primitive recursive',
            'note': 'Ackermann grows faster than any primitive recursive function'
        }

    def apply_kleene_normal_form(
        self,
        index: int,
        input_val: int
    ) -> Dict[str, Any]:
        """
        Apply Kleene normal form representation

        Kleene normal form: φ_e(x) = U(μy[T(e, x, y)])
        where:
        - e is the index of the function
        - T is the Kleene T-predicate (computation predicate)
        - U is the result extraction function
        - μy finds the shortest computation

        Args:
            index: Function index (Gödel number)
            input_val: Input value

        Returns:
            Dict containing:
                - index: Function index
                - input: Input value
                - result: Computed value (if converges)
                - explanation: Description
        """
        # Simple examples of indexed functions
        indexed_functions = {
            0: lambda x: 0,           # Zero function
            1: lambda x: x + 1,       # Successor
            2: lambda x: x * 2,       # Doubling
            3: lambda x: x * x,       # Squaring
            4: lambda x: max(0, x - 1),  # Predecessor
        }

        if index in indexed_functions:
            func = indexed_functions[index]
            result = func(input_val)
            return {
                'index': index,
                'input': input_val,
                'result': result,
                'converges': True,
                'explanation': f'φ_{index}({input_val}) = {result} via Kleene normal form',
                'note': 'Kleene normal form provides universal representation of recursive functions'
            }
        else:
            return {
                'index': index,
                'input': input_val,
                'result': None,
                'converges': None,
                'explanation': f'Function φ_{index} not in enumeration (or does not converge)',
                'note': 'Not all indices correspond to total functions'
            }

    def verify_primitive_recursiveness(self, function_name: str) -> Dict[str, Any]:
        """
        Verify if a function is primitive recursive

        Args:
            function_name: Name of function to verify

        Returns:
            Dict containing:
                - primitive_recursive: Boolean or None
                - function: Function name
                - explanation: Analysis
        """
        # Known primitive recursive functions
        primitive_recursive = {
            'zero', 'successor', 'predecessor', 'addition', 'multiplication',
            'exponentiation', 'factorial', 'bounded_subtraction', 'sign',
            'bounded_sum', 'bounded_product', 'gcd', 'lcm'
        }

        # Known non-primitive recursive functions
        not_primitive = {
            'ackermann', 'busy_beaver', 'tree_function'
        }

        if function_name in primitive_recursive:
            return {
                'primitive_recursive': True,
                'function': function_name,
                'explanation': f'{function_name} is primitive recursive',
                'constructible': 'Can be built from zero, successor, projection via composition and recursion'
            }
        elif function_name in not_primitive:
            return {
                'primitive_recursive': False,
                'function': function_name,
                'explanation': f'{function_name} is NOT primitive recursive (but may be μ-recursive)',
                'note': 'Grows faster than any primitive recursive function'
            }
        else:
            return {
                'primitive_recursive': None,
                'function': function_name,
                'explanation': f'Unknown function: {function_name}',
                'note': 'Cannot determine primitive recursiveness'
            }

    def compute_function_index(self, function_name: str) -> Dict[str, Any]:
        """
        Compute Gödel number / index for a recursive function

        Args:
            function_name: Name of function

        Returns:
            Dict containing:
                - index: Gödel number
                - function: Function name
                - explanation: Description
        """
        # Simple indexing scheme
        function_indices = {
            'zero': 0,
            'successor': 1,
            'doubling': 2,
            'squaring': 3,
            'predecessor': 4,
            'addition': 5,
            'multiplication': 6
        }

        if function_name in function_indices:
            index = function_indices[function_name]
            return {
                'index': index,
                'function': function_name,
                'explanation': f'Function {function_name} has Gödel number {index}',
                'note': 'Gödel numbering provides enumeration of all recursive functions'
            }
        else:
            return {
                'index': None,
                'function': function_name,
                'explanation': f'No index assigned to {function_name}',
                'note': 'Every recursive function has a Gödel number'
            }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new recursion theory problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.function_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old function cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.function_cache) > 50:
                keys = list(self.function_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.function_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.function_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
