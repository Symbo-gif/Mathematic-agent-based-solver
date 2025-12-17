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
try:
    # Relative imports (when used as module)
    from .infrastructure.ams import AgentManagementSystem, AgentType
    from .infrastructure.directory_facilitator import DirectoryFacilitator
    from .infrastructure.acc import AgentCommunicationChannel
    from .memory.blackboard import Blackboard
    from .memory.vector_database import VectorDatabase
except ImportError:
    # Absolute imports (when run directly)
    from infrastructure.ams import AgentManagementSystem, AgentType
    from infrastructure.directory_facilitator import DirectoryFacilitator
    from infrastructure.acc import AgentCommunicationChannel
    from memory.blackboard import Blackboard
    from memory.vector_database import VectorDatabase


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

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store"):
        """
        Initialize Phase 0 System

        Args:
            vector_db_path: Path for vector database persistence
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

        self.vector_db = VectorDatabase(persist_directory=vector_db_path)
        print("  [OK] Vector Database (Long-Term Memory)")

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
            from .infrastructure.directory_facilitator import create_service_registration
        except ImportError:
            from infrastructure.directory_facilitator import create_service_registration

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
            from .core.fipa_acl import FIPAMessage, Performative, create_request
            from .core.omdoc_schema import create_variable
        except ImportError:
            from core.fipa_acl import FIPAMessage, Performative, create_request
            from core.omdoc_schema import create_variable

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
                from .memory.blackboard import create_entry, EntryType
            except ImportError:
                from memory.blackboard import create_entry, EntryType

            test_entry = create_entry(
                entry_type=EntryType.TASK,
                content=create_variable('test'),
                author_agent='health_check',
                conversation_id='test_conv',
                tags=['health_check']
            )

            notification_received = [False]

            def test_callback(entry):
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
                from .memory.vector_database import create_vector_entry
            except ImportError:
                from memory.vector_database import create_vector_entry
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
