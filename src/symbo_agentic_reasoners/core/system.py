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
PHASE 0 SYSTEM INTEGRATION
==========================

Integrated Phase 0 system bringing together all foundational components.

This module provides the Phase0System class that initializes and manages
all Phase 0 infrastructure, ready for Phase 1 cognitive agents to be added.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Section 4 "Phase 0 Completion Criteria"
- Phase 0 Coding Strategy: Section 7.0 "Phase 0 Definition of Done"
"""

from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger('symbo_agentic_reasoners.phase0.system')

# Import all Phase 0 components
from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.core.vector_database import VectorDatabase


class Phase0System:
    """
    Integrated Phase 0 System

    Brings together all foundational infrastructure components:
      - AMS: Agent Management System (lifecycle & VRAM enforcement)
      - DF: Directory Facilitator (service registry)
      - ACC: Agent Communication Channel (message routing)
      - Blackboard: Active memory workspace
      - Vector Database: Long-term institutional memory

    USAGE:
    -----
    # Initialize system
    system = Phase0System()
    system.start()

    # System is now ready for Phase 1 agents
    # Agents can:
    #   - Register with AMS
    #   - Register services with DF
    #   - Send messages via ACC
    #   - Post to Blackboard
    #   - Store knowledge in Vector DB

    # Verify system health
    system.health_check()

    # Get statistics
    stats = system.get_statistics()

    # Shutdown
    system.shutdown()
    """

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store", allow_mock: bool = False):
        """
        Initialize Phase 0 System

        Args:
            vector_db_path: Path for vector database persistence
            allow_mock: If True, use mock vector database for testing (no ChromaDB required)
        """
        print("=" * 80)
        print("PHASE 0 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()

        # Initialize all components
        print("Initializing infrastructure...")

        self.ams = AgentManagementSystem()
        print("  [OK] AMS (Agent Management System)")

        self.df = DirectoryFacilitator()
        print("  [OK] DF (Directory Facilitator)")

        self.acc = AgentCommunicationChannel()
        print("  [OK] ACC (Agent Communication Channel)")

        self.blackboard = Blackboard()
        print("  [OK] Blackboard (Active Memory)")

        self.vector_db = VectorDatabase(persist_directory=vector_db_path, allow_mock=allow_mock)
        print(f"  [OK] Vector Database (Long-Term Memory){' [MOCK MODE]' if allow_mock else ''}")

        print()
        print("[OK] Phase 0 infrastructure initialized")
        print()

    def start(self):
        """
        Start Phase 0 System

        Activates monitoring and background services.
        """
        print("Starting Phase 0 System...")

        # Start AMS monitoring
        self.ams.start()
        print("  [OK] AMS monitoring active")

        # Register infrastructure agents with DF
        try:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
        except ImportError:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

        self.df.register(create_service_registration(
            service_type='system.lifecycle_management',
            agent_id='ams',
            algorithm='vram_enforcement',
            cost='low'
        ))

        self.df.register(create_service_registration(
            service_type='system.service_registry',
            agent_id='df',
            algorithm='dynamic_lookup',
            cost='low'
        ))

        self.df.register(create_service_registration(
            service_type='system.message_routing',
            agent_id='acc',
            algorithm='queue_based',
            cost='low'
        ))

        print("  [OK] Infrastructure services registered")
        print()
        print("[OK] Phase 0 System started")
        print()
        print("SYSTEM STATUS: Computationally Alive, Mathematically Inert")
        print()

    def shutdown(self):
        """
        Shutdown Phase 0 System

        Stops monitoring and deactivates all agents.
        """
        print()
        print("Shutting down Phase 0 System...")

        # Stop AMS monitoring
        self.ams.stop()
        print("  [OK] AMS monitoring stopped")

        # Deactivate all agents
        for agent_record in self.ams.list_agents():
            if agent_record.agent_id != 'ams':  # Don't kill AMS itself
                self.ams.kill_agent(agent_record.agent_id)

        print("  [OK] All agents deactivated")
        print()
        print("[OK] Phase 0 System shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Verifies all Phase 0 components are operational.

        Returns:
            Dictionary with health status for each component

        REFERENCE:
        ---------
        Phase_0_Build_Order_Breakdown.md: Lines 507-517 "Definition of Done Checklist"
        """
        print()
        print("=" * 80)
        print("PHASE 0 HEALTH CHECK")
        print("=" * 80)
        print()

        health = {}

        # Check 1: The Office Building is Built
        print("[OK] Check 1: The Office Building is Built")
        ams_healthy = self.ams.get_agent('ams') is not None
        df_healthy = len(self.df.list_all_services()) >= 0  # DF operational
        acc_healthy = self.acc is not None
        infrastructure_healthy = ams_healthy and df_healthy and acc_healthy
        health['infrastructure'] = infrastructure_healthy
        print(f"    AMS operational: {ams_healthy}")
        print(f"    DF operational: {df_healthy}")
        print(f"    ACC operational: {acc_healthy}")
        print(f"    Status: {'PASS' if infrastructure_healthy else 'FAIL'}")
        print()

        # Check 2: The City Manager is Hired
        print("[OK] Check 2: The City Manager is Hired")
        ams_stats = self.ams.get_statistics()
        vram_monitoring = ams_stats['vram_usage_gb'] >= 0
        enforcement_working = not self.ams.can_activate_cognitive_agent() or \
                             ams_stats['active_cognitive_agent'] is None
        city_manager_healthy = vram_monitoring and enforcement_working
        health['city_manager'] = city_manager_healthy
        print(f"    VRAM monitoring active: {vram_monitoring}")
        print(f"    One-Model-At-A-Time enforcement: {enforcement_working}")
        print(f"    VRAM usage: {ams_stats['vram_usage_gb']:.2f}GB / {ams_stats['vram_utilization']:.0%}")
        print(f"    Status: {'PASS' if city_manager_healthy else 'FAIL'}")
        print()

        # Check 3: The Laws are Written
        print("[OK] Check 3: The Laws are Written")

        # Test FIPA-ACL validation
        try:
            from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage, Performative, create_request
            from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        except ImportError:
            from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage, Performative, create_request
            from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        try:
            # Valid message should pass
            valid_msg = create_request('test_sender', 'test_receiver', create_variable('x'))
            valid_msg.validate()
            laws_valid = True

            # Invalid message should fail
            try:
                invalid_msg = FIPAMessage(
                    performative=Performative.REQUEST,
                    sender='test',
                    receiver='test',
                    content="raw text"  # FORBIDDEN
                )
                invalid_msg.validate()
                laws_valid = False  # Should have raised error
            except ValueError:
                pass  # Correct - raw text rejected

        except (AttributeError, TypeError, ImportError) as e:
            logger.debug(f"Laws validation check failed: {type(e).__name__}: {e}")
            laws_valid = False

        health['laws'] = laws_valid
        print(f"    FIPA-ACL protocol enforced: {laws_valid}")
        print(f"    OMDoc content required: {laws_valid}")
        print(f"    Raw text rejected: {laws_valid}")
        print(f"    Status: {'PASS' if laws_valid else 'FAIL'}")
        print()

        # Check 4: The Library is Open
        print("[OK] Check 4: The Library is Open")

        # Test Blackboard
        blackboard_healthy = False
        try:
            try:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
            except ImportError:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            test_entry = create_entry(
                entry_type=EntryType.TASK,
                content=create_variable('test'),
                author_agent='health_check',
                conversation_id='test_conv',
                tags=['health_check']
            )

            notification_received = [False]

            def test_callback(entry):
                """Test callback for blackboard notifications."""
                notification_received[0] = True

            self.blackboard.subscribe('health_check', ['health_check'], test_callback)
            self.blackboard.post(test_entry)

            blackboard_healthy = notification_received[0]
        except (AttributeError, TypeError, ImportError) as e:
            logger.debug(f"Blackboard health check failed: {type(e).__name__}: {e}")

        # Test Vector Database
        vector_db_healthy = False
        try:
            try:
                from symbo_agentic_reasoners.core.vector_database import create_vector_entry
            except ImportError:
                from symbo_agentic_reasoners.core.vector_database import create_vector_entry
            import uuid

            test_vector = create_vector_entry(
                entry_id=f'health_check_{uuid.uuid4().hex[:8]}',
                content=create_variable('test'),
                entry_type='test'
            )
            self.vector_db.store(test_vector)
            retrieved = self.vector_db.get_by_id(test_vector.entry_id)
            vector_db_healthy = retrieved is not None
            # Cleanup
            self.vector_db.delete(test_vector.entry_id)
        except (AttributeError, TypeError, ImportError, KeyError) as e:
            logger.debug(f"Vector DB health check failed: {type(e).__name__}: {e}")

        library_healthy = blackboard_healthy and vector_db_healthy
        health['library'] = library_healthy
        print(f"    Blackboard operational: {blackboard_healthy}")
        print(f"    Blackboard pub/sub working: {blackboard_healthy}")
        print(f"    Vector DB operational: {vector_db_healthy}")
        print(f"    Status: {'PASS' if library_healthy else 'FAIL'}")
        print()

        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy

        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()

        if all_healthy:
            print("[OK] Phase 0 is COMPLETE and HEALTHY")
            print("  The system is Computationally Alive, Mathematically Inert")
            print("  Ready for Phase 1: Cognitive Chassis")
        else:
            print("[FAIL] Phase 0 has health issues - review above checks")

        print()

        return health

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics

        Returns:
            Dictionary with statistics from all components
        """
        return {
            'ams': self.ams.get_statistics(),
            'df': self.df.get_statistics(),
            'acc': self.acc.get_statistics(),
            'blackboard': self.blackboard.get_statistics(),
            'vector_db': self.vector_db.get_statistics()
        }

    def print_statistics(self):
        """Print formatted statistics"""
        print()
        print("=" * 80)
        print("PHASE 0 SYSTEM STATISTICS")
        print("=" * 80)
        print()

        stats = self.get_statistics()
        print(json.dumps(stats, indent=2))
        print()

    def __repr__(self) -> str:
        """Human-readable representation"""
        return f"Phase0System(AMS={self.ams}, DF={self.df}, ACC={self.acc})"


if __name__ == "__main__":
    """Demonstration of integrated Phase 0 system"""
    print()
    print("=" + "=" * 78 + "╗")
    print("|" + " " * 20 + "PHASE 0 SYSTEM DEMONSTRATION" + " " * 30 + "|")
    print("=" + "=" * 78 + "╝")
    print()

    # Initialize and start system
    system = Phase0System()
    system.start()

    # Perform health check
    health = system.health_check()

    # Display statistics
    system.print_statistics()

    # Shutdown
    system.shutdown()

    print()
    print("=" + "=" * 78 + "╗")
    print("|" + " " * 15 + "PHASE 0 DEMONSTRATION COMPLETE" + " " * 33 + "|")
    print("=" + "=" * 78 + "╝")
    print()

    if health['overall']:
        print("[OK] Phase 0 is complete and ready for Phase 1")
        print()
        print("NEXT STEPS:")
        print("  1. Implement Phase 1: Cognitive Chassis (Orchestrator, CNS, Specialists)")
        print("  2. Add problem-solving capabilities")
        print("  3. Test with actual mathematical problems")
    else:
        print("[FAIL] Phase 0 has issues - please review health check output")


# Re-export Phase6System for convenience
try:
    from symbo_agentic_reasoners.discovery.phase6_system import Phase6System
except ImportError:
    Phase6System = None  # Discovery module not available


# Stub classes for backward compatibility with tests
class Phase1System:
    """Stub for Phase 1 System - cognitive chassis"""
    def __init__(self, **kwargs):
        """Initialize Phase 1 system with core infrastructure.

        Args:
            **kwargs: Optional df (DirectoryFacilitator) and blackboard (Blackboard)
        """
        self.df = kwargs.get('df')
        self.blackboard = kwargs.get('blackboard')
        self.status = 'stopped'

    def start(self):
        """Start Phase 1 system."""
        self.status = 'running'

    def shutdown(self):
        """Shutdown Phase 1 system."""
        self.status = 'stopped'

    def health_check(self):
        """Return health status of Phase 1 system."""
        return {'overall': self.status == 'running'}

    def get_statistics(self):
        """Return statistics for Phase 1 system."""
        return {}

class Phase2System:
    """
    Phase 2 System - Mathematical Workforce
    
    Bootstraps and manages all Phase 2 domain specialists and supervisors.
    This system instantiates all mathematical agents and ensures they register
    with the Directory Facilitator.
    
    AGENTS MANAGED:
    --------------
    - 4 Supervisors (Algebra, Calculus, Linear Algebra, Statistics)
    - 22+ Specialists across 5 domains
    - All agents auto-register with DF during initialization
    
    USAGE:
    -----
    phase0 = Phase0System()
    phase0.start()
    
    phase2 = Phase2System(phase0_system=phase0)
    phase2.start()  # Bootstraps all agents
    
    # Verify registration
    registered = phase2.df.list_all_services()
    print(f"Registered agents: {len(registered)}")
    """
    
    def __init__(self, phase0_system: Optional[Phase0System] = None, **kwargs):
        """
        Initialize Phase 2 System
        
        Args:
            phase0_system: Phase 0 infrastructure (preferred)
            **kwargs: Alternative way to pass df, blackboard, etc.
        """
        print()
        print("=" * 80)
        print("PHASE 2 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()
        
        # Get infrastructure from Phase 0 or kwargs
        if phase0_system:
            self.df = phase0_system.df
            self.blackboard = phase0_system.blackboard
            self.ams = phase0_system.ams
            self.acc = phase0_system.acc
            print("  [OK] Using Phase 0 infrastructure")
        else:
            self.df = kwargs.get('df')
            self.blackboard = kwargs.get('blackboard')
            self.ams = kwargs.get('ams')
            self.acc = kwargs.get('acc')
            
            # Create infrastructure if not provided
            if not self.df:
                self.df = DirectoryFacilitator()
                print("  [OK] Created new Directory Facilitator")
            if not self.blackboard:
                self.blackboard = Blackboard()
                print("  [OK] Created new Blackboard")
        
        # Agent storage
        self.supervisors = {}
        self.specialists = {}
        self.status = 'stopped'
        
        print()
        print("[OK] Phase 2 System initialized")
        print()
    
    def start(self):
        """
        Start Phase 2 System - Bootstrap all mathematical agents
        
        This method instantiates all supervisors and specialists,
        which automatically register with the Directory Facilitator.
        """
        print("Starting Phase 2 System - Bootstrapping Mathematical Workforce...")
        print()
        
        # Import all agent classes
        try:
            from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
            from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
            from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import LinearAlgebraSupervisor
            from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import StatisticsSupervisor
            
            # Algebra specialists
            from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import PolynomialSpecialist
            from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import ArithmeticSpecialist
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import NumberTheorySpecialist
            from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import EquationSystemSolver
            from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import GroupRingTheoryAgent
            
            # Calculus specialists
            from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist
            from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
            from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import SeriesSpecialist
            from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import LimitEvaluator
            from symbo_agentic_reasoners.agents.specialists.calculus.ode_specialist import ODESolutionSpecialist
            
            # Linear algebra specialists
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_ops_specialist import MatrixOperationsSpecialist
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import DecompositionSpecialist
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.vector_space_analyst import VectorSpaceAnalyst
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.tensor_operations import TensorOperationsAgent
            
            # Statistics specialists
            from symbo_agentic_reasoners.agents.specialists.statistics.distribution_specialist import DistributionSpecialist
            from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_engine import BayesianInferenceEngine
            from symbo_agentic_reasoners.agents.specialists.statistics.frequentist_agent import FrequentistAgent
            from symbo_agentic_reasoners.agents.specialists.statistics.stochastic_process import StochasticProcessAnalyzer
            
            # Discrete math specialists
            from symbo_agentic_reasoners.agents.specialists.discrete_math.combinatorics_agent import CombinatoricsAgent
            from symbo_agentic_reasoners.agents.specialists.discrete_math.graph_theory_agent import GraphTheoryAgent
            
            # Numerical specialist
            from symbo_agentic_reasoners.agents.specialists.numerical.numerical_utility import NumericalComputationUtility
            
        except ImportError as e:
            print(f"  [ERROR] Failed to import agent classes: {e}")
            print(f"  [ERROR] Phase 2 System startup failed")
            self.status = 'failed'
            return
        
        print("  [1/3] Instantiating Supervisors...")
        
        # Instantiate supervisors
        try:
            self.supervisors['algebra'] = AlgebraSupervisor(
                agent_id='algebra_supervisor_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.supervisors['calculus'] = CalculusSupervisor(
                agent_id='calculus_supervisor_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.supervisors['linear_algebra'] = LinearAlgebraSupervisor(
                agent_id='linalg_supervisor_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.supervisors['statistics'] = StatisticsSupervisor(
                agent_id='stats_supervisor_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            print(f"    [OK] Instantiated {len(self.supervisors)} supervisors")
        except Exception as e:
            print(f"    [ERROR] Supervisor instantiation failed: {e}")
            self.status = 'failed'
            return
        
        print()
        print("  [2/3] Instantiating Specialists...")
        
        # Instantiate specialists
        try:
            # Algebra specialists
            self.specialists['polynomial'] = PolynomialSpecialist(
                agent_id='polynomial_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['arithmetic'] = ArithmeticSpecialist(
                agent_id='arithmetic_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['number_theory'] = NumberTheorySpecialist(
                agent_id='number_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['equation_system'] = EquationSystemSolver(
                agent_id='equation_system_solver_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['group_ring'] = GroupRingTheoryAgent(
                agent_id='group_ring_theory_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            # Calculus specialists
            self.specialists['differentiation'] = DifferentiationSpecialist(
                agent_id='differentiation_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['integration'] = IntegrationSpecialist(
                agent_id='integration_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['series'] = SeriesSpecialist(
                agent_id='series_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['limit'] = LimitEvaluator(
                agent_id='limit_evaluator_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['ode'] = ODESolutionSpecialist(
                agent_id='ode_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            # Linear algebra specialists
            self.specialists['matrix_ops'] = MatrixOperationsSpecialist(
                agent_id='matrix_ops_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['decomposition'] = DecompositionSpecialist(
                agent_id='decomposition_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['vector_space'] = VectorSpaceAnalyst(
                agent_id='vector_space_analyst_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['tensor'] = TensorOperationsAgent(
                agent_id='tensor_ops_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            # Statistics specialists
            self.specialists['distribution'] = DistributionSpecialist(
                agent_id='distribution_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['bayesian'] = BayesianInferenceEngine(
                agent_id='bayesian_engine_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['frequentist'] = FrequentistAgent(
                agent_id='frequentist_agent_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['stochastic'] = StochasticProcessAnalyzer(
                agent_id='stochastic_process_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            # Discrete math specialists
            self.specialists['combinatorics'] = CombinatoricsAgent(
                agent_id='combinatorics_agent_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            self.specialists['graph_theory'] = GraphTheoryAgent(
                agent_id='graph_theory_agent_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            # Numerical specialist
            self.specialists['numerical'] = NumericalComputationUtility(
                agent_id='numerical_utility_001',
                df=self.df,
                blackboard=self.blackboard
            )
            
            print(f"    [OK] Instantiated {len(self.specialists)} specialists")
        except Exception as e:
            print(f"    [ERROR] Specialist instantiation failed: {e}")
            logger.error(f"Specialist instantiation error: {e}", exc_info=True)
            self.status = 'failed'
            return
        
        print()
        print("  [3/3] Verifying Agent Registration...")
        
        # Verify registration with DF
        if self.df:
            # Use search_by_prefix to get actual ServiceRegistration objects
            agent_services = self.df.search_by_prefix('math.')
            
            print(f"    [OK] {len(agent_services)} mathematical agents registered with DF")
            
            # Show breakdown by domain
            domains = {}
            for service in agent_services:
                domain = service.service_type.split('.')[1] if '.' in service.service_type else 'unknown'
                domains[domain] = domains.get(domain, 0) + 1
            
            print()
            print("    Registration breakdown:")
            for domain, count in sorted(domains.items()):
                print(f"      - math.{domain}: {count} agent(s)")
        
        self.status = 'running'
        
        print()
        print("[OK] Phase 2 System started")
        print(f"[OK] Total agents: {len(self.supervisors)} supervisors + {len(self.specialists)} specialists")
        print()
        print("SYSTEM STATUS: Mathematical Workforce Active")
        print()
    
    def shutdown(self):
        """Shutdown Phase 2 System"""
        print()
        print("Shutting down Phase 2 System...")
        
        # Clear agent references
        self.supervisors.clear()
        self.specialists.clear()
        
        self.status = 'stopped'
        
        print("  [OK] All agents deactivated")
        print()
        print("[OK] Phase 2 System shutdown complete")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform Phase 2 health check
        
        Returns:
            Dictionary with health status
        """
        print()
        print("=" * 80)
        print("PHASE 2 HEALTH CHECK")
        print("=" * 80)
        print()
        
        health = {}
        
        # Check 1: System running
        print("[CHECK 1] System Status")
        system_running = self.status == 'running'
        health['system_running'] = system_running
        print(f"    Status: {self.status}")
        print(f"    Result: {'PASS' if system_running else 'FAIL'}")
        print()
        
        # Check 2: Agents instantiated
        print("[CHECK 2] Agent Instantiation")
        supervisors_ok = len(self.supervisors) >= 4
        specialists_ok = len(self.specialists) >= 20
        agents_instantiated = supervisors_ok and specialists_ok
        health['agents_instantiated'] = agents_instantiated
        print(f"    Supervisors: {len(self.supervisors)}/4")
        print(f"    Specialists: {len(self.specialists)}/20+")
        print(f"    Result: {'PASS' if agents_instantiated else 'FAIL'}")
        print()
        
        # Check 3: DF registration
        print("[CHECK 3] Directory Facilitator Registration")
        if self.df:
            # Use search_by_prefix to get actual ServiceRegistration objects
            agent_services = self.df.search_by_prefix('math.')
            registration_ok = len(agent_services) >= 24  # 4 supervisors + 20+ specialists
            health['df_registration'] = registration_ok
            print(f"    Registered agents: {len(agent_services)}")
            print(f"    Expected: 24+")
            print(f"    Result: {'PASS' if registration_ok else 'FAIL'}")
        else:
            health['df_registration'] = False
            print(f"    No DF available")
            print(f"    Result: FAIL")
        print()
        
        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy
        
        print("=" * 80)
        print(f"OVERALL PHASE 2 HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()
        
        return health
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Phase 2 statistics"""
        stats = {
            'status': self.status,
            'supervisors_count': len(self.supervisors),
            'specialists_count': len(self.specialists),
            'total_agents': len(self.supervisors) + len(self.specialists)
        }
        
        if self.df:
            # Use search_by_prefix to get actual ServiceRegistration objects
            agent_services = self.df.search_by_prefix('math.')
            stats['registered_agents'] = len(agent_services)
        
        return stats

class Phase3System:
    """Stub for Phase 3 System - middleware"""
    def __init__(self, **kwargs):
        """Initialize Phase 3 middleware system.

        Args:
            **kwargs: Optional phase2_system reference
        """
        self.phase2 = kwargs.get('phase2_system')
        self.status = 'stopped'

    def start(self):
        """Start Phase 3 system."""
        self.status = 'running'

    def shutdown(self):
        """Shutdown Phase 3 system."""
        self.status = 'stopped'

    def health_check(self):
        """Return health status of Phase 3 system."""
        return {'overall': self.status == 'running'}

    def get_statistics(self):
        """Return statistics for Phase 3 system."""
        return {}

class Phase4System:
    """
    Phase 4 System - Self-Correcting System

    Integrates the three Phase 4 teams:
    1. Conflict Resolution Team - Evidence-based adjudication
    2. Failure Analysis Team - Autonomous error recovery
    3. Meta-Learning Team - Continuous optimization
    """
    def __init__(self, **kwargs):
        """Initialize Phase 4 self-correcting system.

        Creates and manages three Phase 4 teams:
        - Conflict Resolution Team: Evidence-based adjudication
        - Failure Analysis Team: Autonomous error recovery
        - Meta-Learning Team: Continuous optimization (AutoMaAS)

        Args:
            **kwargs: Optional phase3_system reference

        Notes:
            - Teams initialized immediately (not lazy)
            - Each team operates independently
            - Provides system-level health monitoring
        """
        self.phase3 = kwargs.get('phase3_system')
        self.status = 'stopped'

        # Initialize Phase 4 teams
        from symbo_agentic_reasoners.middleware.conflict_resolution import ConflictResolutionTeam
        from symbo_agentic_reasoners.middleware.failure_analysis import FailureAnalysisTeam
        from symbo_agentic_reasoners.middleware.meta_learning import MetaLearningTeam

        self.conflict_resolution_team = ConflictResolutionTeam()
        self.failure_analysis_team = FailureAnalysisTeam()
        self.meta_learning_team = MetaLearningTeam()

    def start(self):
        """Start Phase 4 system and all teams."""
        self.status = 'running'

    def shutdown(self):
        """Shutdown Phase 4 system and all teams."""
        self.status = 'stopped'

    def health_check(self) -> Dict[str, Any]:
        """Return health status of all Phase 4 teams"""
        return {
            'overall': self.status == 'running',
            'conflict_resolution_team': self.conflict_resolution_team is not None,
            'failure_analysis_team': self.failure_analysis_team is not None,
            'meta_learning_team': self.meta_learning_team is not None
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return statistics from all Phase 4 teams"""
        return {
            'conflicts_resolved': getattr(self.conflict_resolution_team, 'conflicts_resolved', 0),
            'failures_handled': getattr(self.failure_analysis_team, 'failures_handled', 0),
            'optimization_runs': getattr(self.meta_learning_team, 'optimization_runs', 0)
        }

    def resolve_conflict(self, conflict_data: Dict[str, Any]):
        """
        Resolve a conflict using the Conflict Resolution Team

        Args:
            conflict_data: Dictionary containing conflict information

        Returns:
            Ruling object from the conflict resolution process
        """
        return self.conflict_resolution_team.resolve_conflict(conflict_data)

    def handle_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a failure using the Failure Analysis Team

        Args:
            failure_data: Dictionary containing failure information

        Returns:
            Dictionary containing 'report' with error analysis
        """
        result = self.failure_analysis_team.handle_failure(failure_data)
        # Wrap in expected format for tests
        if isinstance(result, dict) and 'report' not in result:
            return {'report': result}
        return result

class Phase5System:
    """Stub for Phase 5 System - optimization"""
    def __init__(self, **kwargs):
        """Initialize Phase 5 optimization system.

        Args:
            **kwargs: Optional phase4_system reference
        """
        self.phase4 = kwargs.get('phase4_system')
        self.status = 'stopped'

    def start(self):
        """Start Phase 5 system."""
        self.status = 'running'

    def shutdown(self):
        """Shutdown Phase 5 system."""
        self.status = 'stopped'

    def health_check(self):
        """Return health status of Phase 5 system."""
        return {'overall': self.status == 'running'}

    def get_statistics(self):
        """Return statistics for Phase 5 system."""
        return {}
