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
LEARNING ENHANCEMENT SUPERVISOR - Tier 2 Orchestrator (Dec 2025)
=================================================================

Orchestrates the Learning Enhancement Team to optimize SymboLLM's
mathematical learning capabilities. Routes tasks to appropriate
specialists and coordinates multi-specialist workflows.

ARCHITECTURE:
------------
LearningEnhancementSupervisor (this file) - Tier 2 routing
  ├── ComplexityScorerSpecialist - Complexity-weighted learning
  ├── NegativeLearnerSpecialist - Contrastive learning from failures
  ├── CurriculumSpecialist - Progressive difficulty scheduling
  ├── BPETokenizerSpecialist - Mathematical subword tokenization
  ├── ModelArchitectSpecialist - Neural architecture optimization
  └── KnowledgeGraphSpecialist - Graph-structured knowledge

ROUTING STRATEGY:
----------------
- complexity_scoring → ComplexityScorerSpecialist
- negative_learning → NegativeLearnerSpecialist
- curriculum → CurriculumSpecialist
- tokenization → BPETokenizerSpecialist
- architecture → ModelArchitectSpecialist
- knowledge_graph → KnowledgeGraphSpecialist
- full_optimization → All specialists in dependency order

NEVER COMPUTES DIRECTLY - Only routes to specialists.

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Agentic Architecture
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('symbo_agentic_reasoners.supervisors.learning_enhancement')


class LearningEnhancementSupervisor(BDIAgent):
    """
    Learning Enhancement Supervisor - Tier 2

    Orchestrates the Learning Enhancement Team to optimize SymboLLM's
    mathematical learning capabilities.

    ROLE:
    ----
    - Route learning optimization tasks to appropriate specialists
    - Coordinate multi-specialist workflows
    - Aggregate results from parallel specialist execution
    - Monitor overall learning system health

    NEVER COMPUTES DIRECTLY - Only routes to specialists.

    SPECIALISTS:
    -----------
    1. ComplexityScorerSpecialist - Score problem complexity
    2. NegativeLearnerSpecialist - Learn from failures
    3. CurriculumSpecialist - Progressive difficulty
    4. BPETokenizerSpecialist - Math tokenization
    5. ModelArchitectSpecialist - Architecture optimization
    6. KnowledgeGraphSpecialist - Graph knowledge

    Example:
        >>> supervisor = LearningEnhancementSupervisor(df, blackboard)
        >>> result = supervisor.optimize_learning({
        ...     'problem': 'solve x^2 = 4',
        ...     'answer': 'x = ±2',
        ...     'domain': 'algebra'
        ... })
    """

    # Task type to specialist mapping
    SPECIALIST_ROUTING = {
        'complexity_scoring': 'complexity_scorer',
        'negative_learning': 'negative_learner',
        'curriculum': 'curriculum',
        'tokenization': 'bpe_tokenizer',
        'architecture': 'model_architect',
        'knowledge_graph': 'knowledge_graph',
    }

    def __init__(
        self,
        agent_id: str = 'learning_enhancement_supervisor',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Learning Enhancement Supervisor.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._specialists: Dict[str, Any] = {}

        # Statistics
        self.tasks_routed = 0
        self.specialist_calls: Dict[str, int] = {
            name: 0 for name in self.SPECIALIST_ROUTING.values()
        }
        self.workflow_runs = 0

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'specialists_healthy': True,
            'optimization_needed': False,
            'last_workflow': None
        }

        # Subscribe to blackboard if available
        if self.blackboard:
            self._subscribe_to_tasks()

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Learning Enhancement Supervisor initialized")

    def _register_services(self) -> None:
        """Register supervisor services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.enhancement.supervisor',
            description='Orchestrates learning optimization specialists',
            capabilities=['route', 'optimize', 'analyze', 'workflow']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def _subscribe_to_tasks(self) -> None:
        """Subscribe to learning-related blackboard entries."""
        if self.blackboard:
            self.blackboard.subscribe(
                agent_id=self.agent_id,
                tags=['learning', 'optimization', 'training'],
                callback=self._on_learning_task
            )

    def _on_learning_task(self, entry: Any) -> None:
        """Callback for blackboard learning tasks."""
        logger.debug(f"Received learning task: {entry}")
        # Process the task
        if hasattr(entry, 'content'):
            self.route_task(entry.content)

    def _get_specialist(self, name: str) -> Any:
        """
        Get or create a specialist by name (lazy loading).

        Args:
            name: Specialist name

        Returns:
            Specialist instance
        """
        if name not in self._specialists:
            # Lazy import and instantiate
            if name == 'complexity_scorer':
                from symbo_agentic_reasoners.agents.specialists.learning.complexity_scorer_specialist import \
                    ComplexityScorerSpecialist
                self._specialists[name] = ComplexityScorerSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            elif name == 'negative_learner':
                from symbo_agentic_reasoners.agents.specialists.learning.negative_learner_specialist import \
                    NegativeLearnerSpecialist
                self._specialists[name] = NegativeLearnerSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            elif name == 'curriculum':
                from symbo_agentic_reasoners.agents.specialists.learning.curriculum_specialist import \
                    CurriculumSpecialist
                self._specialists[name] = CurriculumSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            elif name == 'bpe_tokenizer':
                from symbo_agentic_reasoners.agents.specialists.learning.bpe_tokenizer_specialist import \
                    BPETokenizerSpecialist
                self._specialists[name] = BPETokenizerSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            elif name == 'model_architect':
                from symbo_agentic_reasoners.agents.specialists.learning.model_architect_specialist import \
                    ModelArchitectSpecialist
                self._specialists[name] = ModelArchitectSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            elif name == 'knowledge_graph':
                from symbo_agentic_reasoners.agents.specialists.learning.knowledge_graph_specialist import \
                    KnowledgeGraphSpecialist
                self._specialists[name] = KnowledgeGraphSpecialist(
                    df=self.df, blackboard=self.blackboard
                )
            else:
                raise ValueError(f"Unknown specialist: {name}")

            logger.info(f"[{self.agent_id}] Loaded specialist: {name}")

        return self._specialists[name]

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the appropriate specialist.

        Args:
            task: Task dictionary with 'type' and relevant data

        Returns:
            Result from specialist
        """
        self.tasks_routed += 1

        task_type = task.get('type', task.get('action', 'unknown'))

        # Determine specialist
        specialist_name = self.SPECIALIST_ROUTING.get(task_type)

        if not specialist_name:
            # Check if it's a full optimization request
            if task_type in ['full_optimization', 'optimize']:
                return self.run_full_optimization(task)

            return {'error': f'Unknown task type: {task_type}'}

        # Route to specialist
        specialist = self._get_specialist(specialist_name)
        self.specialist_calls[specialist_name] += 1

        try:
            result = specialist.process(task)
            return {
                'status': 'success',
                'specialist': specialist_name,
                'result': result
            }
        except Exception as e:
            logger.error(f"Specialist {specialist_name} error: {e}")
            return {
                'status': 'error',
                'specialist': specialist_name,
                'error': str(e)
            }

    def run_full_optimization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run full optimization workflow with all specialists.

        Args:
            task: Task with problem/answer data

        Returns:
            Aggregated results from all specialists
        """
        self.workflow_runs += 1
        results = {}

        problem = task.get('problem', '')
        answer = task.get('answer', '')
        domain = task.get('domain', 'unknown')

        logger.info(f"[{self.agent_id}] Starting full optimization workflow")

        # Phase 1: Independent specialists (can run in parallel conceptually)
        # Step 1: Score complexity
        try:
            complexity_scorer = self._get_specialist('complexity_scorer')
            complexity_result = complexity_scorer.score(
                problem=problem,
                answer=answer,
                domain=domain
            )
            results['complexity'] = complexity_result.to_dict()
            self.specialist_calls['complexity_scorer'] += 1
        except Exception as e:
            results['complexity'] = {'error': str(e)}

        # Step 2: Check for bad patterns
        try:
            negative_learner = self._get_specialist('negative_learner')
            is_bad, reason = negative_learner.is_known_bad(answer)
            results['negative_check'] = {
                'is_bad': is_bad,
                'reason': reason
            }
            self.specialist_calls['negative_learner'] += 1
        except Exception as e:
            results['negative_check'] = {'error': str(e)}

        # Step 3: Tokenization analysis
        try:
            tokenizer = self._get_specialist('bpe_tokenizer')
            tokens = tokenizer.encode(problem + ' ' + answer)
            results['tokenization'] = {
                'token_count': len(tokens),
                'tokens': tokens[:20]  # First 20 tokens
            }
            self.specialist_calls['bpe_tokenizer'] += 1
        except Exception as e:
            results['tokenization'] = {'error': str(e)}

        # Phase 2: Dependent specialists
        # Step 4: Curriculum update (uses complexity)
        try:
            curriculum = self._get_specialist('curriculum')
            # Get current difficulty state
            curriculum_state = curriculum.get_state()
            results['curriculum'] = curriculum_state
            self.specialist_calls['curriculum'] += 1
        except Exception as e:
            results['curriculum'] = {'error': str(e)}

        # Step 5: Architecture analysis
        try:
            architect = self._get_specialist('model_architect')
            arch_analysis = architect.analyze_architecture()
            results['architecture'] = {
                'current_params': arch_analysis.get('estimated_parameters'),
                'issues_count': len(arch_analysis.get('issues', []))
            }
            self.specialist_calls['model_architect'] += 1
        except Exception as e:
            results['architecture'] = {'error': str(e)}

        # Phase 3: Knowledge graph integration
        try:
            knowledge_graph = self._get_specialist('knowledge_graph')
            node_result = knowledge_graph.add_node(
                problem=problem,
                answer=answer,
                domain=domain,
                complexity=results.get('complexity', {}).get('score', 0.5)
            )
            results['knowledge_graph'] = node_result
            self.specialist_calls['knowledge_graph'] += 1
        except Exception as e:
            results['knowledge_graph'] = {'error': str(e)}

        self.beliefs['last_workflow'] = datetime.now().isoformat()

        return {
            'status': 'success',
            'workflow': 'full_optimization',
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

    def optimize_learning(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize learning for a problem-answer pair.

        This is the main entry point for learning optimization.

        Args:
            entry: Dict with 'problem', 'answer', 'domain'

        Returns:
            Optimization results including:
            - complexity_score: Weighted learning signal
            - is_bad_pattern: Whether to skip learning
            - curriculum_difficulty: Current learning difficulty
            - graph_node_id: Knowledge graph node
        """
        return self.run_full_optimization({
            **entry,
            'type': 'full_optimization'
        })

    def get_specialist_stats(self) -> Dict[str, Any]:
        """Get statistics for all loaded specialists."""
        stats = {}

        for name, specialist in self._specialists.items():
            if hasattr(specialist, 'get_stats'):
                stats[name] = specialist.get_stats()
            else:
                stats[name] = {'loaded': True}

        return stats

    def get_stats(self) -> Dict[str, Any]:
        """Get supervisor statistics."""
        return {
            'tasks_routed': self.tasks_routed,
            'specialist_calls': self.specialist_calls,
            'workflow_runs': self.workflow_runs,
            'specialists_loaded': list(self._specialists.keys()),
            'beliefs': self.beliefs
        }

    def analyze_system(self) -> Dict[str, Any]:
        """
        Analyze the entire learning system.

        Returns:
            System-wide analysis and recommendations
        """
        analysis = {
            'supervisor_stats': self.get_stats(),
            'specialist_stats': {},
            'recommendations': []
        }

        # Get stats from all specialists
        for name in self.SPECIALIST_ROUTING.values():
            try:
                specialist = self._get_specialist(name)
                if hasattr(specialist, 'get_stats'):
                    analysis['specialist_stats'][name] = specialist.get_stats()
            except Exception as e:
                analysis['specialist_stats'][name] = {'error': str(e)}

        # Generate recommendations
        if self.workflow_runs == 0:
            analysis['recommendations'].append(
                "No optimization workflows run yet. Consider running full optimization."
            )

        # Check specialist balance
        max_calls = max(self.specialist_calls.values()) if self.specialist_calls else 0
        min_calls = min(self.specialist_calls.values()) if self.specialist_calls else 0
        if max_calls > 10 * (min_calls + 1):
            analysis['recommendations'].append(
                "Imbalanced specialist usage. Some specialists are underutilized."
            )

        return analysis

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs about specialist health."""
        self.beliefs['specialists_healthy'] = all(
            name in self._specialists
            for name in ['complexity_scorer', 'negative_learner']
        )

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('optimization_needed', False):
            return Intention(
                plan_id='run_optimization',
                steps=['analyze', 'route_tasks', 'aggregate'],
                target_desire='optimized_learning'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of supervisor processing."""
        if self.blackboard:
            # Would process pending tasks from blackboard
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task entry.

        Args:
            task_entry: Task with 'action'/'type' and data

        Returns:
            Processing result
        """
        action = task_entry.get('action', task_entry.get('type', 'route'))

        if action == 'route':
            return self.route_task(task_entry)

        elif action in ['optimize', 'full_optimization']:
            return self.optimize_learning(task_entry)

        elif action == 'get_stats':
            return self.get_stats()

        elif action == 'analyze':
            return self.analyze_system()

        elif action == 'specialist_stats':
            return self.get_specialist_stats()

        else:
            # Try to route based on action type
            return self.route_task(task_entry)
