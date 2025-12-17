# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
BDI Integration Tests
=====================

Tests that verify the BDI (Belief-Desire-Intention) implementation
actually works end-to-end through the full agent pipeline.

These are NOT unit tests - they test the integrated system.
"""

import pytest
from unittest.mock import Mock, patch


class TestArithmeticSpecialistBDI:
    """Test ArithmeticSpecialist with real BDI implementation"""

    def test_update_beliefs_finds_pending_tasks(self):
        """Test that update_beliefs reads tasks from Blackboard"""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        # Setup
        blackboard = Blackboard()
        specialist = ArithmeticSpecialist(blackboard=blackboard)

        # Post a task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("2 + 2"),
            author_agent='test',
            conversation_id='test_001',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': '2 + 2', 'operation': 'compute'}
        )
        blackboard.post(task)

        # Run update_beliefs
        specialist.update_beliefs()

        # Should have belief about the pending task
        assert specialist.has_belief(f'pending_task_{task.entry_id}')

    def test_deliberate_creates_intention_for_pending_task(self):
        """Test that deliberate creates a plan for pending tasks"""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        # Setup
        blackboard = Blackboard()
        specialist = ArithmeticSpecialist(blackboard=blackboard)

        # Post a task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("3 * 4"),
            author_agent='test',
            conversation_id='test_002',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': '3 * 4', 'operation': 'compute'}
        )
        blackboard.post(task)

        # Run BDI cycle
        specialist.update_beliefs()
        new_intentions = specialist.deliberate()

        # Should create an intention
        assert len(new_intentions) == 1
        assert new_intentions[0].plan_id == f'solve_{task.entry_id}'
        assert 'claim_task' in new_intentions[0].steps
        assert 'compute_exact' in new_intentions[0].steps

    def test_execute_step_claims_task(self):
        """Test that execute_step can claim a task"""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        # Setup
        blackboard = Blackboard()
        specialist = ArithmeticSpecialist(blackboard=blackboard)

        # Post a task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("5 + 5"),
            author_agent='test',
            conversation_id='test_003',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': '5 + 5', 'operation': 'compute'}
        )
        blackboard.post(task)

        # Create intention manually
        intention = Intention(
            plan_id=f'solve_{task.entry_id}',
            steps=['claim_task', 'parse_expression', 'compute_exact', 'verify_result', 'post_result'],
            target_desire='solve_arithmetic',
            metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': 'compute'}
        )

        # Execute claim step
        specialist.execute_step(intention)

        # Task should be claimed
        assert specialist.has_belief(f'claimed_task_{task.entry_id}')
        assert intention.current_step == 1  # Advanced to next step

    def test_full_bdi_cycle_solves_problem(self):
        """Test complete BDI cycle solving a problem"""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        # Setup
        blackboard = Blackboard()
        specialist = ArithmeticSpecialist(blackboard=blackboard)

        # Post a task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("2**10"),
            author_agent='test',
            conversation_id='test_004',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': '2**10', 'sympy_expr': '2**10', 'operation': 'compute'}
        )
        blackboard.post(task)

        # Run BDI cycles until complete
        max_cycles = 20
        for _ in range(max_cycles):
            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            specialist.intentions.extend(new_intentions)

            if specialist.intentions:
                current = specialist.intentions[0]
                specialist.execute_step(current)

                if current.is_complete():
                    specialist.intentions.remove(current)
                    break

        # Check result on Blackboard
        results = blackboard.query_entries(tags=['result'])
        assert len(results) >= 1

        # Should have correct result (2^10 = 1024)
        result_entry = results[0]
        assert '1024' in str(result_entry.metadata.get('result', ''))

    def test_factor_operation_uses_transform_algebraic(self):
        """Test that factor operation uses transform_algebraic step"""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        # Setup
        blackboard = Blackboard()
        specialist = ArithmeticSpecialist(blackboard=blackboard)

        # Post a factor task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("x**2 - 4"),
            author_agent='test',
            conversation_id='test_005',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': 'x**2 - 4', 'sympy_expr': 'x**2 - 4', 'operation': 'factor'}
        )
        blackboard.post(task)

        # Run update and deliberate
        specialist.update_beliefs()
        new_intentions = specialist.deliberate()

        # Plan should include transform_algebraic for factor operation
        assert len(new_intentions) == 1
        assert 'transform_algebraic' in new_intentions[0].steps


class TestHardwareDetector:
    """Test hardware detection"""

    def test_hardware_detection_runs(self):
        """Test that hardware detection doesn't crash"""
        from symbo_agentic_reasoners.infrastructure.hardware_detector import (
            HardwareDetector, HardwareProfile
        )

        detector = HardwareDetector()
        profile = detector.detect()

        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_cores >= 1
        assert profile.ram_total_gb > 0
        assert profile.max_parallel_symbolic_agents >= 1

    def test_can_spawn_symbolic_agent(self):
        """Test symbolic agent spawn check"""
        from symbo_agentic_reasoners.infrastructure.hardware_detector import (
            HardwareDetector
        )

        detector = HardwareDetector()
        # Should almost always be true on any reasonable system
        can_spawn = detector.can_spawn_symbolic_agent()
        assert isinstance(can_spawn, bool)


class TestMathSolver:
    """Test the MathSolver facade"""

    def test_math_solver_initialization(self):
        """Test MathSolver can be created"""
        from symbo_agentic_reasoners.core.math_solver import MathSolver

        solver = MathSolver(
            enable_parallel=False,  # Simpler for testing
            enable_harvesting=False,
            enable_verification=False
        )

        assert solver is not None
        assert solver.enable_parallel is False

    def test_solve_result_dataclass(self):
        """Test SolveResult dataclass"""
        from symbo_agentic_reasoners.core.math_solver import SolveResult, SolveStatus

        result = SolveResult(
            status=SolveStatus.SUCCESS,
            result="4",
            problem_type="arithmetic",
            domain="algebra",
            operation="compute",
            verified=True,
            solve_time_ms=10.5
        )

        assert result.status == SolveStatus.SUCCESS
        assert result.result == "4"

        # Test to_dict
        d = result.to_dict()
        assert d['status'] == 'success'
        assert d['result'] == '4'


class TestBlackboardIntegration:
    """Test Blackboard query methods used by BDI agents"""

    def test_query_entries_by_tag(self):
        """Test querying Blackboard by tag"""
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        bb = Blackboard()

        # Post entries with different tags
        task1 = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("task1"),
            author_agent='test',
            conversation_id='c1',
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING
        )
        bb.post(task1)

        task2 = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("task2"),
            author_agent='test',
            conversation_id='c2',
            tags=['calculus', 'task'],
            status=EntryStatus.PENDING
        )
        bb.post(task2)

        # Query arithmetic tasks
        arithmetic_tasks = bb.query_entries(tags=['arithmetic'])
        assert len(arithmetic_tasks) == 1
        assert arithmetic_tasks[0].entry_id == task1.entry_id

    def test_query_entries_by_status(self):
        """Test querying Blackboard by status"""
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        bb = Blackboard()

        # Post entries with different statuses
        pending = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("pending"),
            author_agent='test',
            conversation_id='c1',
            tags=['test'],
            status=EntryStatus.PENDING
        )
        bb.post(pending)

        completed = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("completed"),
            author_agent='test',
            conversation_id='c2',
            tags=['test'],
            status=EntryStatus.COMPLETED
        )
        bb.post(completed)

        # Query pending only
        pending_tasks = bb.query_entries(status=EntryStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].entry_id == pending.entry_id


class TestPolynomialSpecialistBDI:
    """Test PolynomialSpecialist with real BDI implementation"""

    def test_polynomial_bdi_cycle(self):
        """Test PolynomialSpecialist BDI perceive-deliberate-execute"""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
            PolynomialSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        # Setup
        blackboard = Blackboard()
        specialist = PolynomialSpecialist(blackboard=blackboard)

        # Post a polynomial task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("x**2 - 4"),
            author_agent='test',
            conversation_id='poly_001',
            tags=['polynomial', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': 'x**2 - 4', 'sympy_expr': 'x**2 - 4', 'operation': 'factor'}
        )
        blackboard.post(task)

        # Run BDI cycle
        specialist.update_beliefs()
        assert specialist.has_belief(f'pending_task_{task.entry_id}')

        new_intentions = specialist.deliberate()
        assert len(new_intentions) == 1
        assert 'factor' in new_intentions[0].plan_id

    def test_polynomial_expand_operation(self):
        """Test polynomial expand operation"""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
            PolynomialSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        blackboard = Blackboard()
        specialist = PolynomialSpecialist(blackboard=blackboard)

        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("(x+1)**2"),
            author_agent='test',
            conversation_id='poly_002',
            tags=['polynomial', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': '(x+1)**2', 'sympy_expr': '(x+1)**2', 'operation': 'expand'}
        )
        blackboard.post(task)

        specialist.update_beliefs()
        new_intentions = specialist.deliberate()

        assert len(new_intentions) == 1
        assert 'expand' in new_intentions[0].plan_id


class TestDifferentiationSpecialistBDI:
    """Test DifferentiationSpecialist with real BDI implementation"""

    def test_differentiation_bdi_cycle(self):
        """Test DifferentiationSpecialist BDI cycle"""
        from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import (
            DifferentiationSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        blackboard = Blackboard()
        specialist = DifferentiationSpecialist(blackboard=blackboard)

        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("x**2"),
            author_agent='test',
            conversation_id='diff_001',
            tags=['diff', 'task'],  # Use 'diff' - what the agent looks for
            status=EntryStatus.PENDING,
            metadata={'raw_input': 'x**2', 'sympy_expr': 'x**2', 'operation': 'differentiate'}
        )
        blackboard.post(task)

        specialist.update_beliefs()
        assert specialist.has_belief(f'pending_task_{task.entry_id}')

        new_intentions = specialist.deliberate()
        assert len(new_intentions) == 1
        # Plan_id contains 'diff_' prefix
        assert 'diff' in new_intentions[0].plan_id


class TestIntegrationSpecialistBDI:
    """Test IntegrationSpecialist with real BDI implementation"""

    def test_integration_bdi_cycle(self):
        """Test IntegrationSpecialist BDI cycle"""
        from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import (
            IntegrationSpecialist
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        blackboard = Blackboard()
        specialist = IntegrationSpecialist(blackboard=blackboard)

        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("x"),
            author_agent='test',
            conversation_id='int_001',
            tags=['integration', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': 'x', 'sympy_expr': 'x', 'operation': 'integrate'}
        )
        blackboard.post(task)

        specialist.update_beliefs()
        assert specialist.has_belief(f'pending_task_{task.entry_id}')

        new_intentions = specialist.deliberate()
        assert len(new_intentions) == 1
        # Plan_id uses 'int_symbolic' or similar prefix
        assert 'int' in new_intentions[0].plan_id.lower()


class TestThoughtTraceHarvesterIntegration:
    """Test ThoughtTraceHarvester integration"""

    def test_harvester_add_trace(self):
        """Test adding traces to harvester"""
        from symbo_agentic_reasoners.optimization.distillation.harvester import (
            ThoughtTraceHarvester, ThoughtTrace, VerificationStatus
        )
        from datetime import datetime
        import uuid

        harvester = ThoughtTraceHarvester()
        initial_count = len(harvester.verified_traces)

        # Use unique trace_id and query to avoid deduplication
        unique_id = str(uuid.uuid4())
        trace = ThoughtTrace(
            trace_id=f'test_integration_{unique_id}',
            timestamp=datetime.now(),
            original_query=f'test_query_{unique_id}',
            query_type='arithmetic',
            complexity_score=0.1,
            orchestrator_decomposition=[],
            supervisor_strategy='AlgebraSupervisor',
            specialist_agents_invoked=['ArithmeticSpecialist'],
            symbolic_expressions=['2 + 2 = 4'],
            fitted_coefficients={},
            taylor_expansion_order=0,
            groebner_basis_used=False,
            verification_status=VerificationStatus.VERIFIED,
            formal_proof_lean4=None,
            debate_consensus_score=None,
            final_answer=f'result_{unique_id}',  # Unique answer for dedup
            confidence_score=1.0,
            total_latency_ms=10.0,
            agents_activated=1,
            symbolic_ops_count=1
        )

        result = harvester.add_trace(trace)
        assert result is True
        assert len(harvester.verified_traces) == initial_count + 1

    def test_harvester_rejects_unverified(self):
        """Test that unverified traces are rejected"""
        from symbo_agentic_reasoners.optimization.distillation.harvester import (
            ThoughtTraceHarvester, ThoughtTrace, VerificationStatus
        )
        from datetime import datetime

        harvester = ThoughtTraceHarvester()
        initial_count = len(harvester.verified_traces)

        trace = ThoughtTrace(
            trace_id='test_rejected_001',
            timestamp=datetime.now(),
            original_query='invalid',
            query_type='unknown',
            complexity_score=0.0,
            orchestrator_decomposition=[],
            supervisor_strategy='',
            specialist_agents_invoked=[],
            symbolic_expressions=[],
            fitted_coefficients={},
            taylor_expansion_order=0,
            groebner_basis_used=False,
            verification_status=VerificationStatus.REJECTED,  # Not verified
            formal_proof_lean4=None,
            debate_consensus_score=None,
            final_answer='',
            confidence_score=0.0,
            total_latency_ms=0.0,
            agents_activated=0,
            symbolic_ops_count=0
        )

        result = harvester.add_trace(trace)
        assert result is False
        assert len(harvester.verified_traces) == initial_count

    def test_harvester_get_training_corpus(self):
        """Test getting training corpus from harvester"""
        from symbo_agentic_reasoners.optimization.distillation.harvester import (
            ThoughtTraceHarvester
        )

        harvester = ThoughtTraceHarvester()
        corpus = harvester.get_training_corpus()

        assert isinstance(corpus, list)
        # Should have some traces (either from storage or none if empty)
        for example in corpus:
            assert 'prompt' in example
            assert 'response' in example


class TestAlgebraSupervisorBDI:
    """Test AlgebraSupervisor BDI routing"""

    def test_supervisor_routes_to_specialist(self):
        """Test that supervisor routes tasks to specialists"""
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import (
            AlgebraSupervisor
        )
        from symbo_agentic_reasoners.core.blackboard import (
            Blackboard, create_entry, EntryType, EntryStatus
        )
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator

        blackboard = Blackboard()
        df = DirectoryFacilitator()
        supervisor = AlgebraSupervisor(df=df, blackboard=blackboard)

        task = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("x + 1"),
            author_agent='test',
            conversation_id='super_001',
            tags=['algebra', 'task'],
            status=EntryStatus.PENDING,
            metadata={'raw_input': 'x + 1', 'operation': 'simplify', 'domain': 'algebra'}
        )
        blackboard.post(task)

        supervisor.update_beliefs()
        # Supervisor uses 'pending_algebra_' not 'pending_task_'
        assert supervisor.has_belief(f'pending_algebra_{task.entry_id}')

        new_intentions = supervisor.deliberate()
        assert len(new_intentions) == 1
        # Supervisor plans involve routing, not direct computation
        assert 'analyze_task' in new_intentions[0].steps or 'find_specialist' in new_intentions[0].steps


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
