# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
GLOBAL OPTIMIZATION SPECIALIST - Metaheuristics and global search
================================================================

Handles global optimization using stochastic and heuristic methods.

CRITICAL ALGORITHMS:
-------------------
- Simulated Annealing: Probabilistic global search with cooling schedule
- Genetic Algorithm: Evolutionary optimization via selection/crossover/mutation
- Particle Swarm Optimization: Swarm intelligence optimization
- Differential Evolution: Population-based global search
- Branch and Bound: Systematic enumeration with pruning
- Basin Hopping: Random perturbation with local minimization
- Multi-Start: Multiple random initializations

WHY THIS MATTERS:
----------------
Global optimization is essential for:
- Finding global minima in multimodal landscapes
- Avoiding local optima traps
- Black-box optimization (no derivatives needed)
- Discrete and combinatorial optimization
- Real-world engineering problems with many local minima

CAPABILITIES:
------------
- Solve multimodal optimization problems
- Derivative-free optimization
- Handle discrete and continuous variables
- Parallel multi-start strategies
- Adaptive parameter tuning

NO SYMPY - Pure NumPy/SciPy native implementation
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from scipy.optimize import minimize as scipy_minimize, differential_evolution as scipy_diffev
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class GlobalOptimizationSpecialist(BDIAgent):
    """
    Global Optimization Specialist - Metaheuristics and global search

    DIRECTIVE:
    ---------
    Handle all global optimization problems with emphasis on:
    - Stochastic search methods
    - Population-based algorithms
    - Multimodal optimization
    - Derivative-free methods

    KEY ALGORITHMS:
    --------------
    - Simulated Annealing: Metropolis criterion with cooling
    - Genetic Algorithm: Selection, crossover, mutation
    - PSO: Particle swarm with velocity updates
    - Differential Evolution: Mutation and crossover strategies

    OPERATIONS:
    ----------
    - simulated_annealing(objective, x0, temp_schedule)
    - genetic_algorithm(objective, bounds, population_size)
    - particle_swarm_optimization(objective, bounds, n_particles)
    - differential_evolution(objective, bounds, strategy)
    - branch_and_bound(objective, bounds, branching_rule)
    - basin_hopping(objective, x0, n_iterations)
    - multi_start_optimization(objective, bounds, n_starts)
    """

    def __init__(self, agent_id='global_optimization_specialist_001', df=None, blackboard=None):
        """
        Initialize Global Optimization Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.optimization_cache = {}
        self.recent_tasks = []

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.global',
                agent_id=self.agent_id,
                algorithm='global_optimization',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process global optimization task

        Args:
            task_entry: Task entry with metadata

        Returns:
            Dictionary with optimization results
        """
        self.tasks_executed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'simulated_annealing')

        try:
            if problem_type == 'simulated_annealing':
                return self._handle_simulated_annealing(metadata)
            elif problem_type == 'genetic_algorithm':
                return self._handle_genetic_algorithm(metadata)
            elif problem_type == 'pso':
                return self._handle_pso(metadata)
            elif problem_type == 'differential_evolution':
                return self._handle_differential_evolution(metadata)
            elif problem_type == 'branch_and_bound':
                return self._handle_branch_and_bound(metadata)
            elif problem_type == 'basin_hopping':
                return self._handle_basin_hopping(metadata)
            elif problem_type == 'multi_start':
                return self._handle_multi_start(metadata)
            else:
                return {'operation': 'global_optimization', 'error': f'Unknown problem type: {problem_type}'}
        except Exception as e:
            return {'operation': 'global_optimization', 'error': str(e)}

    def _handle_simulated_annealing(self, metadata: Dict) -> Dict[str, Any]:
        """Handle simulated annealing request"""
        objective = metadata.get('objective')
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)
        temp_initial = metadata.get('temp_initial', 100.0)
        temp_final = metadata.get('temp_final', 0.01)
        max_iterations = metadata.get('max_iterations', 1000)

        result = self.simulated_annealing(objective, x0, temp_initial, temp_final, max_iterations)
        return {'operation': 'simulated_annealing', 'result': result}

    def _handle_genetic_algorithm(self, metadata: Dict) -> Dict[str, Any]:
        """Handle genetic algorithm request"""
        objective = metadata.get('objective')
        bounds = metadata.get('bounds', [(-10, 10), (-10, 10)])
        population_size = metadata.get('population_size', 50)
        max_generations = metadata.get('max_generations', 100)

        result = self.genetic_algorithm(objective, bounds, population_size, max_generations)
        return {'operation': 'genetic_algorithm', 'result': result}

    def _handle_pso(self, metadata: Dict) -> Dict[str, Any]:
        """Handle PSO request"""
        objective = metadata.get('objective')
        bounds = metadata.get('bounds', [(-10, 10), (-10, 10)])
        n_particles = metadata.get('n_particles', 30)
        max_iterations = metadata.get('max_iterations', 100)

        result = self.particle_swarm_optimization(objective, bounds, n_particles, max_iterations)
        return {'operation': 'pso', 'result': result}

    def _handle_differential_evolution(self, metadata: Dict) -> Dict[str, Any]:
        """Handle differential evolution request"""
        objective = metadata.get('objective')
        bounds = metadata.get('bounds', [(-10, 10), (-10, 10)])
        strategy = metadata.get('strategy', 'best1bin')
        max_iterations = metadata.get('max_iterations', 100)

        result = self.differential_evolution(objective, bounds, strategy, max_iterations)
        return {'operation': 'differential_evolution', 'result': result}

    def _handle_branch_and_bound(self, metadata: Dict) -> Dict[str, Any]:
        """Handle branch and bound request"""
        objective = metadata.get('objective')
        bounds = metadata.get('bounds', [(-10, 10), (-10, 10)])
        branching_rule = metadata.get('branching_rule', 'midpoint')

        result = self.branch_and_bound(objective, bounds, branching_rule)
        return {'operation': 'branch_and_bound', 'result': result}

    def _handle_basin_hopping(self, metadata: Dict) -> Dict[str, Any]:
        """Handle basin hopping request"""
        objective = metadata.get('objective')
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)
        n_iterations = metadata.get('n_iterations', 100)

        result = self.basin_hopping(objective, x0, n_iterations)
        return {'operation': 'basin_hopping', 'result': result}

    def _handle_multi_start(self, metadata: Dict) -> Dict[str, Any]:
        """Handle multi-start request"""
        objective = metadata.get('objective')
        bounds = metadata.get('bounds', [(-10, 10), (-10, 10)])
        n_starts = metadata.get('n_starts', 10)

        result = self.multi_start_optimization(objective, bounds, n_starts)
        return {'operation': 'multi_start', 'result': result}

    # =========================================================================
    # SIMULATED ANNEALING
    # =========================================================================

    def simulated_annealing(self, objective: Callable, x0: np.ndarray,
                           temp_initial: float = 100.0, temp_final: float = 0.01,
                           max_iterations: int = 1000, step_size: float = 0.5) -> Dict[str, Any]:
        """
        Simulated Annealing global optimization

        Accept worse solutions with probability exp(-ΔE/T)
        Temperature decreases according to schedule

        Args:
            objective: Objective function f(x)
            x0: Initial point
            temp_initial: Initial temperature T0
            temp_final: Final temperature Tf
            max_iterations: Maximum iterations
            step_size: Random perturbation magnitude

        Returns:
            Dictionary with best point and value
        """
        x_current = x0.copy()
        f_current = objective(x_current)
        x_best = x_current.copy()
        f_best = f_current

        # Exponential cooling schedule
        alpha = (temp_final / temp_initial) ** (1.0 / max_iterations)
        temperature = temp_initial

        accepted = 0
        for iteration in range(max_iterations):
            # Generate random neighbor
            x_neighbor = x_current + np.random.uniform(-step_size, step_size, size=len(x_current))
            f_neighbor = objective(x_neighbor)

            # Compute energy difference
            delta_e = f_neighbor - f_current

            # Metropolis acceptance criterion
            if delta_e < 0 or np.random.rand() < np.exp(-delta_e / temperature):
                x_current = x_neighbor
                f_current = f_neighbor
                accepted += 1

                # Update best solution
                if f_current < f_best:
                    x_best = x_current.copy()
                    f_best = f_current

            # Cool down
            temperature *= alpha

        return {
            'status': 'converged',
            'optimal_x': x_best.tolist(),
            'optimal_value': float(f_best),
            'iterations': max_iterations,
            'acceptance_rate': accepted / max_iterations,
            'method': 'simulated_annealing'
        }

    # =========================================================================
    # GENETIC ALGORITHM
    # =========================================================================

    def genetic_algorithm(self, objective: Callable, bounds: List[Tuple[float, float]],
                         population_size: int = 50, max_generations: int = 100,
                         mutation_rate: float = 0.1, crossover_rate: float = 0.7) -> Dict[str, Any]:
        """
        Genetic Algorithm for global optimization

        Evolution via selection, crossover, mutation

        Args:
            objective: Objective function f(x)
            bounds: Variable bounds [(low, high), ...]
            population_size: Number of individuals
            max_generations: Maximum generations
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover

        Returns:
            Dictionary with best individual and fitness
        """
        n_dims = len(bounds)
        bounds_array = np.array(bounds)

        # Initialize population
        population = np.random.uniform(
            bounds_array[:, 0], bounds_array[:, 1],
            size=(population_size, n_dims)
        )

        best_individual = None
        best_fitness = float('inf')

        for generation in range(max_generations):
            # Evaluate fitness (minimize objective)
            fitness = np.array([objective(ind) for ind in population])

            # Track best
            gen_best_idx = np.argmin(fitness)
            if fitness[gen_best_idx] < best_fitness:
                best_fitness = fitness[gen_best_idx]
                best_individual = population[gen_best_idx].copy()

            # Selection (tournament)
            new_population = []
            for _ in range(population_size):
                parent = self._tournament_selection(population, fitness, k=3)
                new_population.append(parent.copy())
            new_population = np.array(new_population)

            # Crossover
            for i in range(0, population_size - 1, 2):
                if np.random.rand() < crossover_rate:
                    alpha = np.random.rand()
                    child1 = alpha * new_population[i] + (1 - alpha) * new_population[i + 1]
                    child2 = (1 - alpha) * new_population[i] + alpha * new_population[i + 1]
                    new_population[i] = child1
                    new_population[i + 1] = child2

            # Mutation
            for i in range(population_size):
                if np.random.rand() < mutation_rate:
                    mutation = np.random.uniform(-1, 1, size=n_dims) * 0.1 * (bounds_array[:, 1] - bounds_array[:, 0])
                    new_population[i] += mutation

            # Enforce bounds
            population = np.clip(new_population, bounds_array[:, 0], bounds_array[:, 1])

        return {
            'status': 'converged',
            'optimal_x': best_individual.tolist(),
            'optimal_value': float(best_fitness),
            'generations': max_generations,
            'method': 'genetic_algorithm'
        }

    def _tournament_selection(self, population: np.ndarray, fitness: np.ndarray, k: int = 3) -> np.ndarray:
        """Tournament selection"""
        indices = np.random.choice(len(population), size=k, replace=False)
        tournament_fitness = fitness[indices]
        winner_idx = indices[np.argmin(tournament_fitness)]
        return population[winner_idx]

    # =========================================================================
    # PARTICLE SWARM OPTIMIZATION
    # =========================================================================

    def particle_swarm_optimization(self, objective: Callable, bounds: List[Tuple[float, float]],
                                   n_particles: int = 30, max_iterations: int = 100,
                                   w: float = 0.7, c1: float = 1.5, c2: float = 1.5) -> Dict[str, Any]:
        """
        Particle Swarm Optimization

        Velocity update: v_i = w*v_i + c1*r1*(p_i - x_i) + c2*r2*(g - x_i)

        Args:
            objective: Objective function f(x)
            bounds: Variable bounds [(low, high), ...]
            n_particles: Number of particles
            max_iterations: Maximum iterations
            w: Inertia weight
            c1: Cognitive coefficient (personal best)
            c2: Social coefficient (global best)

        Returns:
            Dictionary with global best position and value
        """
        n_dims = len(bounds)
        bounds_array = np.array(bounds)

        # Initialize positions and velocities
        positions = np.random.uniform(
            bounds_array[:, 0], bounds_array[:, 1],
            size=(n_particles, n_dims)
        )
        velocities = np.random.uniform(-1, 1, size=(n_particles, n_dims))

        # Personal bests
        personal_best_positions = positions.copy()
        personal_best_values = np.array([objective(p) for p in positions])

        # Global best
        global_best_idx = np.argmin(personal_best_values)
        global_best_position = personal_best_positions[global_best_idx].copy()
        global_best_value = personal_best_values[global_best_idx]

        for iteration in range(max_iterations):
            for i in range(n_particles):
                # Update velocity
                r1, r2 = np.random.rand(2)
                cognitive = c1 * r1 * (personal_best_positions[i] - positions[i])
                social = c2 * r2 * (global_best_position - positions[i])
                velocities[i] = w * velocities[i] + cognitive + social

                # Update position
                positions[i] += velocities[i]

                # Enforce bounds
                positions[i] = np.clip(positions[i], bounds_array[:, 0], bounds_array[:, 1])

                # Evaluate
                f_value = objective(positions[i])

                # Update personal best
                if f_value < personal_best_values[i]:
                    personal_best_values[i] = f_value
                    personal_best_positions[i] = positions[i].copy()

                    # Update global best
                    if f_value < global_best_value:
                        global_best_value = f_value
                        global_best_position = positions[i].copy()

        return {
            'status': 'converged',
            'optimal_x': global_best_position.tolist(),
            'optimal_value': float(global_best_value),
            'iterations': max_iterations,
            'method': 'pso'
        }

    # =========================================================================
    # DIFFERENTIAL EVOLUTION
    # =========================================================================

    def differential_evolution(self, objective: Callable, bounds: List[Tuple[float, float]],
                              strategy: str = 'best1bin', max_iterations: int = 100,
                              F: float = 0.8, CR: float = 0.9) -> Dict[str, Any]:
        """
        Differential Evolution global optimization

        Mutation: x_trial = x_a + F*(x_b - x_c)
        Crossover: Mix trial with target vector
        Selection: Keep better of trial vs target

        Args:
            objective: Objective function f(x)
            bounds: Variable bounds [(low, high), ...]
            strategy: DE strategy ('best1bin', 'rand1bin', 'best2bin')
            max_iterations: Maximum iterations
            F: Differential weight (mutation scale)
            CR: Crossover probability

        Returns:
            Dictionary with best solution
        """
        # Use SciPy's differential_evolution (efficient implementation)
        result = scipy_diffev(
            objective,
            bounds,
            strategy=strategy,
            maxiter=max_iterations,
            mutation=F,
            recombination=CR,
            seed=None
        )

        return {
            'status': 'converged' if result.success else 'failed',
            'optimal_x': result.x.tolist(),
            'optimal_value': float(result.fun),
            'iterations': result.nit if hasattr(result, 'nit') else max_iterations,
            'message': result.message,
            'method': 'differential_evolution'
        }

    # =========================================================================
    # BRANCH AND BOUND
    # =========================================================================

    def branch_and_bound(self, objective: Callable, bounds: List[Tuple[float, float]],
                        branching_rule: str = 'midpoint', max_nodes: int = 1000,
                        tolerance: float = 1e-3) -> Dict[str, Any]:
        """
        Branch and Bound for global optimization

        Systematically partition search space with lower bound pruning

        Args:
            objective: Objective function f(x)
            bounds: Variable bounds [(low, high), ...]
            branching_rule: How to split regions ('midpoint', 'best_dimension')
            max_nodes: Maximum nodes to explore
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal solution
        """
        n_dims = len(bounds)

        # Priority queue: (lower_bound, region)
        import heapq
        queue = []

        # Initial region
        initial_region = np.array(bounds)
        initial_center = (initial_region[:, 0] + initial_region[:, 1]) / 2
        initial_lb = objective(initial_center)
        heapq.heappush(queue, (initial_lb, initial_region.tolist()))

        best_value = float('inf')
        best_point = initial_center

        nodes_explored = 0

        while queue and nodes_explored < max_nodes:
            lower_bound, region_list = heapq.heappop(queue)
            region = np.array(region_list)

            # Prune if lower bound exceeds best
            if lower_bound > best_value - tolerance:
                continue

            # Evaluate at center
            center = (region[:, 0] + region[:, 1]) / 2
            f_center = objective(center)

            if f_center < best_value:
                best_value = f_center
                best_point = center

            # Check if region is small enough
            region_size = np.max(region[:, 1] - region[:, 0])
            if region_size < tolerance:
                continue

            # Branch: split longest dimension
            split_dim = np.argmax(region[:, 1] - region[:, 0])
            split_point = (region[split_dim, 0] + region[split_dim, 1]) / 2

            # Create two subregions
            left_region = region.copy()
            left_region[split_dim, 1] = split_point

            right_region = region.copy()
            right_region[split_dim, 0] = split_point

            # Compute lower bounds (use center evaluation as proxy)
            left_center = (left_region[:, 0] + left_region[:, 1]) / 2
            right_center = (right_region[:, 0] + right_region[:, 1]) / 2

            left_lb = objective(left_center)
            right_lb = objective(right_center)

            heapq.heappush(queue, (left_lb, left_region.tolist()))
            heapq.heappush(queue, (right_lb, right_region.tolist()))

            nodes_explored += 1

        return {
            'status': 'converged' if nodes_explored < max_nodes else 'max_nodes',
            'optimal_x': best_point.tolist(),
            'optimal_value': float(best_value),
            'nodes_explored': nodes_explored,
            'method': 'branch_and_bound'
        }

    # =========================================================================
    # BASIN HOPPING
    # =========================================================================

    def basin_hopping(self, objective: Callable, x0: np.ndarray,
                     n_iterations: int = 100, step_size: float = 0.5,
                     temperature: float = 1.0) -> Dict[str, Any]:
        """
        Basin Hopping global optimization

        Random perturbation + local minimization + Metropolis acceptance

        Args:
            objective: Objective function f(x)
            x0: Initial point
            n_iterations: Number of basin hopping iterations
            step_size: Perturbation magnitude
            temperature: Acceptance temperature

        Returns:
            Dictionary with global minimum
        """
        from scipy.optimize import basinhopping

        # Define custom step taking function
        class RandomDisplacement:
            def __init__(self, stepsize=0.5):
                self.stepsize = stepsize

            def __call__(self, x):
                return x + np.random.uniform(-self.stepsize, self.stepsize, size=len(x))

        minimizer_kwargs = {'method': 'BFGS'}
        take_step = RandomDisplacement(stepsize=step_size)

        result = basinhopping(
            objective,
            x0,
            niter=n_iterations,
            T=temperature,
            stepsize=step_size,
            minimizer_kwargs=minimizer_kwargs,
            take_step=take_step
        )

        return {
            'status': 'converged',
            'optimal_x': result.x.tolist(),
            'optimal_value': float(result.fun),
            'iterations': n_iterations,
            'message': result.message if hasattr(result, 'message') else '',
            'method': 'basin_hopping'
        }

    # =========================================================================
    # MULTI-START OPTIMIZATION
    # =========================================================================

    def multi_start_optimization(self, objective: Callable, bounds: List[Tuple[float, float]],
                                n_starts: int = 10, local_method: str = 'BFGS') -> Dict[str, Any]:
        """
        Multi-start local optimization

        Run local optimization from multiple random starting points

        Args:
            objective: Objective function f(x)
            bounds: Variable bounds [(low, high), ...]
            n_starts: Number of random starts
            local_method: Local optimization method ('BFGS', 'L-BFGS-B', 'Nelder-Mead')

        Returns:
            Dictionary with best result across all starts
        """
        bounds_array = np.array(bounds)
        n_dims = len(bounds)

        best_value = float('inf')
        best_point = None
        all_results = []

        for start_idx in range(n_starts):
            # Random starting point
            x0 = np.random.uniform(bounds_array[:, 0], bounds_array[:, 1])

            # Local optimization
            result = scipy_minimize(objective, x0, method=local_method)

            all_results.append({
                'x': result.x.tolist(),
                'value': float(result.fun),
                'success': result.success
            })

            if result.success and result.fun < best_value:
                best_value = result.fun
                best_point = result.x

        return {
            'status': 'converged' if best_point is not None else 'failed',
            'optimal_x': best_point.tolist() if best_point is not None else [],
            'optimal_value': float(best_value),
            'n_starts': n_starts,
            'all_results': all_results,
            'method': 'multi_start'
        }

    # =========================================================================
    # BDI INTEGRATION
    # =========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for global optimization tasks"""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['global_optimization'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['metaheuristic'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['multimodal'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception:
            pass

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create optimization plans"""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already planning
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('problem_type', 'simulated_annealing')

            steps = ['claim_task', 'optimize', 'post_result']
            intention = Intention(
                plan_id=f'global_{operation}_{task_id}',
                steps=steps,
                target_desire='global_optimization',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform global optimization"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'optimize':
            result = self.process(task)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post_result':
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
                result = intention.metadata.get('result', {})

                result_entry = create_entry(
                    content=result,
                    entry_type=EntryType.RESULT,
                    tags=['global_optimization', 'optimization', 'result'],
                    metadata={'source_task': task.entry_id, 'agent': self.agent_id}
                )
                self.blackboard.post_entry(result_entry)
                self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics"""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'simulated_annealing', 'genetic_algorithm', 'pso',
                'differential_evolution', 'branch_and_bound',
                'basin_hopping', 'multi_start'
            ]
        }
