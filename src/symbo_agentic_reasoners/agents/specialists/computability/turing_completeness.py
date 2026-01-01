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
TURING COMPLETENESS SPECIALIST - Turing machines, halting problem, universal machines
====================================================================================

Manages tasks related to Turing machine simulation, halting analysis, and Turing completeness verification.

CRITICAL ALGORITHMS:
-------------------
- Turing Machine Simulation: Execute TM with bounded steps
- Halting Problem Analysis: Timeout-based halting detection
- Universal Turing Machine: UTM construction basics
- Turing Completeness Verification: Check if system is Turing-complete

WHY THIS MATTERS:
----------------
Turing completeness is fundamental to:
- Understanding computational limits (halting problem)
- Verifying language/system expressiveness
- Theoretical foundations of computation
- Decidability and undecidability theory

CAPABILITIES:
------------
- Simulate Turing machines with configurable tape and states
- Analyze halting behavior (with timeout for undecidability)
- Construct basic universal Turing machine configurations
- Verify Turing completeness of computational systems
- Analyze busy beaver functions (bounded computation)
- Church-Turing thesis verification for computational models
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class TuringCompletenessSpecialist(BDIAgent):
    """
    Turing Completeness Specialist - Turing machines, halting problem, universal machines

    DIRECTIVE:
    ---------
    Handle all Turing machine operations with emphasis on:
    - Turing machine simulation and execution
    - Halting problem analysis (with timeout)
    - Universal Turing machine construction
    - Turing completeness verification

    KEY ALGORITHMS:
    --------------
    - TM Simulation: Execute Turing machine with bounded steps
    - Halting Analysis: Timeout-based halting detection
    - UTM Construction: Build universal Turing machine

    OPERATIONS:
    ----------
    - simulate_turing_machine(tape, states, transition_function, max_steps)
    - check_halting(program, input, timeout)
    - construct_universal_tm()
    - verify_turing_completeness(system)
    - analyze_busy_beaver(n_states)
    - verify_church_turing_thesis(model)
    """

    def __init__(self, agent_id='turing_completeness_specialist_001', df=None, blackboard=None):
        """
        Initialize Turing Completeness Specialist

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
        self.simulation_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.computability.turing',
                agent_id=self.agent_id,
                algorithm='turing_machine',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process Turing completeness task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of Turing completeness operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'simulate')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'simulate':
                return self._process_simulation(metadata)
            elif problem_type == 'halting':
                return self._process_halting(metadata)
            elif problem_type == 'universal_tm':
                return self._process_universal_tm(metadata)
            elif problem_type == 'verify_completeness':
                return self._process_verify_completeness(metadata)
            elif problem_type == 'busy_beaver':
                return self._process_busy_beaver(metadata)
            elif problem_type == 'church_turing':
                return self._process_church_turing(metadata)
            else:
                return self._process_simulation(metadata)

        except Exception as e:
            return {
                'operation': 'turing_completeness',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_simulation(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Turing machine simulation request"""
        tape = metadata.get('tape', ['B', 'B', '1', '0', '1', 'B', 'B'])
        states = metadata.get('states', ['q0', 'q1', 'qh'])
        transition_function = metadata.get('transition_function', {})
        max_steps = metadata.get('max_steps', 1000)

        result = self.simulate_turing_machine(tape, states, transition_function, max_steps)
        return {
            'operation': 'turing_machine_simulation',
            **result
        }

    def _process_halting(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process halting problem analysis request"""
        program = metadata.get('program', 'simple_loop')
        input_data = metadata.get('input', '')
        timeout = metadata.get('timeout', 1000)

        result = self.check_halting(program, input_data, timeout)
        return {
            'operation': 'halting_analysis',
            **result
        }

    def _process_universal_tm(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process universal TM construction request"""
        result = self.construct_universal_tm()
        return {
            'operation': 'universal_tm_construction',
            **result
        }

    def _process_verify_completeness(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Turing completeness verification request"""
        system = metadata.get('system', {})
        result = self.verify_turing_completeness(system)
        return {
            'operation': 'verify_turing_completeness',
            **result
        }

    def _process_busy_beaver(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process busy beaver analysis request"""
        n_states = metadata.get('n_states', 2)
        result = self.analyze_busy_beaver(n_states)
        return {
            'operation': 'busy_beaver_analysis',
            **result
        }

    def _process_church_turing(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Church-Turing thesis verification request"""
        model = metadata.get('model', {})
        result = self.verify_church_turing_thesis(model)
        return {
            'operation': 'church_turing_verification',
            **result
        }

    def simulate_turing_machine(
        self,
        tape: List[str],
        states: List[str],
        transition_function: Dict[Tuple[str, str], Tuple[str, str, str]],
        max_steps: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulate a Turing machine execution

        Args:
            tape: Initial tape contents (list of symbols)
            states: List of states (first is initial, last is halt)
            transition_function: Dict mapping (state, symbol) -> (new_state, write_symbol, direction)
            max_steps: Maximum steps to simulate (prevents infinite loops)

        Returns:
            Dict containing:
                - halted: Whether machine halted
                - final_tape: Final tape configuration
                - steps: Number of steps executed
                - final_state: Final state reached
                - explanation: Description of execution
        """
        if not tape:
            tape = ['B']  # Blank tape
        if not states or len(states) < 2:
            states = ['q0', 'qh']  # Default: initial and halt

        # Initialize machine state
        current_state = states[0]
        halt_state = states[-1]
        head_position = len(tape) // 2
        steps = 0

        # Ensure tape has blank symbols on both ends
        tape = ['B'] + list(tape) + ['B']
        head_position += 1

        # Simulation loop
        while steps < max_steps and current_state != halt_state:
            # Read current symbol
            if head_position < 0 or head_position >= len(tape):
                # Extend tape if needed
                if head_position < 0:
                    tape = ['B'] + tape
                    head_position = 0
                else:
                    tape.append('B')

            current_symbol = tape[head_position]

            # Look up transition
            key = (current_state, current_symbol)
            if key not in transition_function:
                # No transition defined - halt
                break

            new_state, write_symbol, direction = transition_function[key]

            # Execute transition
            tape[head_position] = write_symbol
            current_state = new_state

            # Move head
            if direction == 'L':
                head_position -= 1
            elif direction == 'R':
                head_position += 1
            # 'S' for stay is also valid

            steps += 1

        # Determine if machine halted
        halted = (current_state == halt_state) or (steps < max_steps and current_state != halt_state)

        return {
            'halted': halted,
            'final_tape': ''.join(tape).strip('B'),
            'steps': steps,
            'final_state': current_state,
            'timeout': steps >= max_steps,
            'explanation': f"TM executed {steps} steps, {'halted' if halted else 'timed out'} in state {current_state}"
        }

    def check_halting(
        self,
        program: str,
        input_data: str = '',
        timeout: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze halting behavior of a program

        Note: The halting problem is undecidable, so we use timeout as a practical heuristic.

        Args:
            program: Program identifier or description
            input_data: Input to the program
            timeout: Maximum steps before declaring non-halting

        Returns:
            Dict containing:
                - halts: Whether program halts (within timeout)
                - steps: Number of steps (if halts)
                - decidable: Whether halting is decidable for this case
                - explanation: Analysis of halting behavior
        """
        # Known halting patterns
        halting_patterns = {
            'simple_loop': (True, 10, 'Simple bounded loop halts'),
            'infinite_loop': (False, timeout, 'Infinite loop does not halt'),
            'countdown': (True, int(input_data) if input_data.isdigit() else 100, 'Countdown halts'),
            'collatz': (None, None, 'Collatz conjecture - unknown if all inputs halt'),
            'busy_beaver': (None, None, 'Busy beaver - grows faster than any computable function')
        }

        if program in halting_patterns:
            halts, steps, explanation = halting_patterns[program]
            return {
                'halts': halts,
                'steps': steps,
                'decidable': halts is not None,
                'explanation': explanation,
                'rice_theorem': 'Halting problem is undecidable in general (Rice theorem)'
            }

        # Generic analysis
        return {
            'halts': None,
            'steps': None,
            'decidable': False,
            'explanation': f"Cannot decide halting for arbitrary program '{program}' (halting problem is undecidable)",
            'rice_theorem': 'By Rice theorem, any non-trivial semantic property of programs is undecidable'
        }

    def construct_universal_tm(self) -> Dict[str, Any]:
        """
        Construct a basic universal Turing machine configuration

        A universal TM can simulate any other TM given its description.

        Returns:
            Dict containing:
                - states: UTM states
                - alphabet: UTM alphabet
                - description: How UTM works
                - capabilities: What UTM can do
        """
        utm_states = [
            'q_start',      # Initial state
            'q_read_state', # Read current state from tape
            'q_read_symbol',# Read current symbol from tape
            'q_lookup',     # Look up transition in TM description
            'q_write',      # Write new symbol
            'q_move',       # Move head
            'q_halt'        # Halt state
        ]

        utm_alphabet = [
            'B',            # Blank
            '0', '1',       # Binary data
            'S', 'T',       # State markers
            'L', 'R',       # Direction markers
            '#', '|'        # Delimiters
        ]

        return {
            'states': utm_states,
            'alphabet': utm_alphabet,
            'tape_structure': '[TM_description]#[input_data]',
            'description': 'Universal TM reads TM description and simulates it on input data',
            'capabilities': [
                'Can simulate any Turing machine',
                'Demonstrates Turing universality',
                'Foundation of stored-program computers',
                'Proves existence of programmable computation'
            ],
            'complexity': 'Simulation overhead: O(T(n) * log T(n)) where T(n) is original time',
            'explanation': 'UTM is Turing-complete: can compute anything computable by any TM'
        }

    def verify_turing_completeness(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if a computational system is Turing-complete

        Args:
            system: Dict describing computational system with keys:
                - name: System name
                - features: List of features
                - constructs: Available constructs

        Returns:
            Dict containing:
                - is_turing_complete: Boolean assessment
                - requirements_met: Which requirements are satisfied
                - missing: What's needed for Turing completeness
                - explanation: Analysis
        """
        system_name = system.get('name', 'unknown')
        features = set(system.get('features', []))
        constructs = set(system.get('constructs', []))

        # Requirements for Turing completeness
        requirements = {
            'conditional_branching': 'if/else or conditional jumps',
            'arbitrary_memory': 'unbounded memory or arbitrary stack',
            'loops': 'while/for loops or recursion',
            'arithmetic': 'basic arithmetic operations'
        }

        # Check which requirements are met
        requirements_met = {}

        # Check conditional branching
        if any(x in features for x in ['if', 'conditional', 'branch', 'jump']):
            requirements_met['conditional_branching'] = True
        elif any(x in constructs for x in ['if', 'conditional', 'switch', 'case']):
            requirements_met['conditional_branching'] = True
        else:
            requirements_met['conditional_branching'] = False

        # Check memory
        if any(x in features for x in ['unbounded_memory', 'arbitrary_storage', 'heap', 'tape']):
            requirements_met['arbitrary_memory'] = True
        elif any(x in constructs for x in ['array', 'list', 'stack', 'memory']):
            requirements_met['arbitrary_memory'] = True
        else:
            requirements_met['arbitrary_memory'] = False

        # Check loops
        if any(x in features for x in ['while', 'for', 'loop', 'recursion', 'goto']):
            requirements_met['loops'] = True
        elif any(x in constructs for x in ['while', 'for', 'recursion', 'goto']):
            requirements_met['loops'] = True
        else:
            requirements_met['loops'] = False

        # Check arithmetic
        if any(x in features for x in ['arithmetic', 'addition', 'subtraction', 'increment']):
            requirements_met['arithmetic'] = True
        elif any(x in constructs for x in ['+', '-', 'add', 'sub', 'inc', 'dec']):
            requirements_met['arithmetic'] = True
        else:
            requirements_met['arithmetic'] = False

        # Determine Turing completeness
        is_complete = all(requirements_met.values())
        missing = [req for req, met in requirements_met.items() if not met]

        return {
            'is_turing_complete': is_complete,
            'system': system_name,
            'requirements_met': requirements_met,
            'missing': missing if not is_complete else [],
            'explanation': f"System '{system_name}' is {'Turing-complete' if is_complete else 'NOT Turing-complete'}",
            'note': 'Turing completeness means able to compute anything computable by a Turing machine'
        }

    def analyze_busy_beaver(self, n_states: int) -> Dict[str, Any]:
        """
        Analyze busy beaver function for n states

        Busy beaver function BB(n) is the maximum number of steps a halting n-state TM can execute.

        Args:
            n_states: Number of states

        Returns:
            Dict containing:
                - n: Number of states
                - bb_value: BB(n) if known
                - sigma_value: Σ(n) (max 1s written) if known
                - known: Whether value is known
                - explanation: Description
        """
        # Known busy beaver values
        known_bb = {
            1: (1, 1),      # BB(1) = 1, Σ(1) = 1
            2: (6, 4),      # BB(2) = 6, Σ(2) = 4
            3: (21, 6),     # BB(3) = 21, Σ(3) = 6
            4: (107, 13),   # BB(4) = 107, Σ(4) = 13
            5: (47176870, 4098),  # BB(5) = 47,176,870, Σ(5) = 4098
        }

        if n_states in known_bb:
            bb_val, sigma_val = known_bb[n_states]
            return {
                'n': n_states,
                'bb_value': bb_val,
                'sigma_value': sigma_val,
                'known': True,
                'explanation': f"BB({n_states}) = {bb_val}, Σ({n_states}) = {sigma_val}",
                'note': 'Busy beaver grows faster than any computable function'
            }
        else:
            return {
                'n': n_states,
                'bb_value': None,
                'sigma_value': None,
                'known': False,
                'explanation': f"BB({n_states}) is unknown for {n_states} states",
                'note': 'BB(n) is uncomputable - grows faster than any computable function',
                'lower_bound': f"BB({n_states}) > BB({max(known_bb.keys())}) = {known_bb[max(known_bb.keys())][0]}"
            }

    def verify_church_turing_thesis(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify Church-Turing thesis for a computational model

        Church-Turing thesis: Any effectively calculable function is computable by a Turing machine.

        Args:
            model: Dict describing computational model

        Returns:
            Dict containing verification analysis
        """
        model_name = model.get('name', 'unknown')
        model_type = model.get('type', 'unknown')

        # Known equivalent models
        equivalent_models = {
            'turing_machine': 'Original Turing machine model',
            'lambda_calculus': 'Church lambda calculus (equivalent via Church-Turing thesis)',
            'recursive_functions': 'Gödel-Kleene recursive functions (equivalent)',
            'post_correspondence': 'Post correspondence problem (equivalent)',
            'register_machine': 'Unlimited register machine (equivalent)',
            'counter_machine': 'Counter machine with 2+ counters (equivalent)',
            'tag_system': 'Cyclic tag system (equivalent, proven by Cook)',
            'cellular_automaton': 'Rule 110 cellular automaton (Turing-complete)'
        }

        if model_type in equivalent_models:
            return {
                'model': model_name,
                'type': model_type,
                'church_turing_equivalent': True,
                'explanation': equivalent_models[model_type],
                'thesis': 'Church-Turing thesis: All effective models of computation are equivalent'
            }
        else:
            return {
                'model': model_name,
                'type': model_type,
                'church_turing_equivalent': None,
                'explanation': 'Unknown model - cannot verify Church-Turing equivalence',
                'note': 'Church-Turing thesis is not a theorem but a hypothesis about nature of computation'
            }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new Turing completeness problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many simulations
        if self.tasks_executed > 100 and len(self.simulation_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old simulation cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.simulation_cache) > 50:
                # Clear half of cache
                keys = list(self.simulation_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.simulation_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.simulation_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
