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
Pytest Configuration and Shared Fixtures
=========================================

Provides reusable fixtures for the SYMBO_AGENTIC_REASONERS test suite.

Fixture categories:
- Core Infrastructure: Blackboard, AMS, DirectoryFacilitator
- System Fixtures: Phase0System, Phase1System, Phase2System
- Agent Fixtures: Mock agents, supervisors, specialists
- Problem Analysis: ProblemAnalysisTeam, test problems
- Config & Utilities: Config reloading, temp directories, logging
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Generator


# =============================================================================
# COLLECTION IGNORES - Tests for aspirational/unimplemented code
# =============================================================================

# These files/directories contain tests for code that doesn't exist yet
collect_ignore = [
    # Property-based tests require hypothesis which is optional
    "test_property_based.py",
    "test_property_based_extended.py",
    # Word problem tests for unimplemented modules
    "word_problem",
    "core/word_problem",
    # Property-based tests directory
    "property_based",
]

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "phase0: marks tests for Phase 0 infrastructure")
    config.addinivalue_line("markers", "phase1: marks tests for Phase 1 cognitive chassis")
    config.addinivalue_line("markers", "phase2: marks tests for Phase 2 mathematical workforce")
    config.addinivalue_line("markers", "phase3: marks tests for Phase 3 meta-cognitive")
    config.addinivalue_line("markers", "phase4: marks tests for Phase 4 governance")
    config.addinivalue_line("markers", "phase5: marks tests for Phase 5 optimization")
    config.addinivalue_line("markers", "phase6: marks tests for Phase 6 discovery")
    config.addinivalue_line("markers", "security: marks security-related tests")


# =============================================================================
# CORE INFRASTRUCTURE FIXTURES
# =============================================================================

@pytest.fixture
def blackboard():
    """Create a fresh Blackboard instance for testing."""
    from symbo_agentic_reasoners.core.blackboard import Blackboard
    bb = Blackboard()
    yield bb
    # Cleanup
    bb.clear()


@pytest.fixture
def ams():
    """Create a fresh AgentManagementSystem instance."""
    from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
    ams_instance = AgentManagementSystem()
    yield ams_instance


@pytest.fixture
def directory_facilitator():
    """Create a fresh DirectoryFacilitator instance."""
    from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
    df = DirectoryFacilitator()
    yield df


@pytest.fixture
def blackboard_entry():
    """Factory fixture to create blackboard entries."""
    from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

    def _create_entry(
        entry_type=EntryType.TASK,
        content="test content",
        author_agent="test_agent",
        conversation_id="test_conv_001",
        tags=None,
        metadata=None
    ):
        return create_entry(
            entry_type=entry_type,
            content=content,
            author_agent=author_agent,
            conversation_id=conversation_id,
            tags=tags or [],
            metadata=metadata or {}
        )

    return _create_entry


# =============================================================================
# SYSTEM FIXTURES
# =============================================================================

@pytest.fixture
def phase0_system():
    """Create and start a Phase 0 system for testing."""
    from symbo_agentic_reasoners.core.system import Phase0System

    system = Phase0System()
    system.start()
    yield system
    system.shutdown()


@pytest.fixture
def phase1_system():
    """Create and start a Phase 1 system for testing."""
    from symbo_agentic_reasoners.core.system import Phase1System

    system = Phase1System()
    system.start()
    yield system
    system.shutdown()


@pytest.fixture
def solver_engine():
    """Create a SolverEngine instance for testing."""
    from symbo_agentic_reasoners.core.solver_engine import SolverEngine
    engine = SolverEngine()
    yield engine


# =============================================================================
# AGENT FIXTURES
# =============================================================================

@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = MagicMock()
    agent.agent_id = "mock_agent_001"
    agent.process = MagicMock(return_value=None)
    agent.get_statistics = MagicMock(return_value={})
    agent.health_check = MagicMock(return_value=True)
    return agent


@pytest.fixture
def mock_supervisor():
    """Create a mock supervisor agent."""
    supervisor = MagicMock()
    supervisor.agent_id = "mock_supervisor_001"
    supervisor.process = MagicMock(return_value=None)
    supervisor.get_statistics = MagicMock(return_value={'tasks_routed': 0})
    return supervisor


@pytest.fixture
def mock_specialist():
    """Create a mock specialist agent."""
    specialist = MagicMock()
    specialist.agent_id = "mock_specialist_001"
    specialist.process = MagicMock(return_value=MagicMock(
        metadata={'result_str': '2*x'},
        content='2*x'
    ))
    specialist.get_statistics = MagicMock(return_value={'problems_solved': 0})
    return specialist


@pytest.fixture
def mock_solver():
    """Create a mock solver for testing components that need a solver."""
    solver = MagicMock()
    solver.solve = MagicMock(return_value=MagicMock(
        status=MagicMock(value='success'),
        result='2*x',
        solve_time_ms=10.0
    ))
    solver.get_statistics = MagicMock(return_value={})
    return solver


# =============================================================================
# PROBLEM ANALYSIS FIXTURES
# =============================================================================

@pytest.fixture
def problem_analysis_team():
    """Create a ProblemAnalysisTeam instance."""
    from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
    team = ProblemAnalysisTeam()
    yield team


@pytest.fixture
def sample_problems():
    """Provide a collection of sample mathematical problems for testing."""
    return {
        'derivative': {
            'input': 'differentiate x^2 + 1',
            'expected_domain': 'calculus',
            'expected_result': '2*x'
        },
        'integral': {
            'input': 'integrate x^2',
            'expected_domain': 'calculus',
            'expected_result': 'x**3/3'
        },
        'solve_quadratic': {
            'input': 'solve x^2 - 4 = 0',
            'expected_domain': 'algebra',
            'expected_result': '[-2, 2]'
        },
        'factor': {
            'input': 'factor x^2 - 1',
            'expected_domain': 'algebra',
            'expected_result': '(x - 1)*(x + 1)'
        },
        'ode': {
            'input': "dsolve y' = y",
            'expected_domain': 'calculus',
            'expected_result_contains': 'exp'
        },
        'simplify': {
            'input': 'simplify (x^2 - 1)/(x - 1)',
            'expected_domain': 'algebra',
            'expected_result': 'x + 1'
        }
    }


@pytest.fixture
def calculus_problems():
    """Provide calculus-specific test problems."""
    return [
        ('diff x**2', '2*x'),
        ('diff sin(x)', 'cos(x)'),
        ('diff exp(x)', 'exp(x)'),
        ('integrate x', 'x**2/2'),
        ('integrate cos(x)', 'sin(x)'),
    ]


@pytest.fixture
def algebra_problems():
    """Provide algebra-specific test problems."""
    return [
        ('solve x - 5', '[5]'),
        ('solve x**2 - 9', '[-3, 3]'),
        ('factor x**2 - 4', '(x - 2)*(x + 2)'),
        ('expand (x + 1)**2', 'x**2 + 2*x + 1'),
    ]


# =============================================================================
# CONFIG FIXTURES
# =============================================================================

@pytest.fixture
def fresh_config():
    """Reload and return a fresh configuration."""
    from symbo_agentic_reasoners.config import reload_config
    config = reload_config()
    yield config
    # Reset to defaults after test
    reload_config()


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    import json

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "hardware": {"max_vram_gb": 8.0},
            "limits": {"max_agents": 10}
        }
        json.dump(config_data, f)
        config_path = f.name

    yield Path(config_path)

    # Cleanup
    os.unlink(config_path)


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def temp_directory():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def suppress_logging():
    """Suppress logging during tests for cleaner output."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def capture_logs():
    """Capture log output for assertion."""
    import io

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    yield log_capture

    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


# =============================================================================
# SYMBOLIC FIXTURES (using native symbolic module)
# =============================================================================

@pytest.fixture
def sympy_symbols():
    """Provide commonly used native symbolic symbols."""
    from symbo_agentic_reasoners.core.symbolic import Symbol
    return {
        'x': Symbol('x'),
        'y': Symbol('y'),
        'z': Symbol('z'),
        'n': Symbol('n'),
        't': Symbol('t'),
    }


@pytest.fixture
def sympy_expressions(sympy_symbols):
    """Provide commonly used native symbolic expressions."""
    from symbo_agentic_reasoners.core.symbolic import sin, cos, exp, log
    x = sympy_symbols['x']
    return {
        'quadratic': x**2 + 2*x + 1,
        'cubic': x**3 - x,
        'trig': sin(x) + cos(x),
        'exponential': exp(x),
        'logarithmic': log(x),
        'rational': (x**2 - 1)/(x - 1),
    }


# =============================================================================
# SECURITY TEST FIXTURES
# =============================================================================

@pytest.fixture
def dangerous_inputs():
    """Provide dangerous input strings for security testing."""
    return [
        "__import__('os').system('ls')",
        "exec('import os')",
        "eval('__import__(\"subprocess\")')",
        "open('/etc/passwd').read()",
        "().__class__.__bases__[0].__subclasses__()",
        "__builtins__.__dict__['__import__']('os')",
    ]


@pytest.fixture
def safe_expressions():
    """Provide safe mathematical expressions."""
    return [
        "x**2 + 2*x + 1",
        "sin(x) + cos(x)",
        "sqrt(x**2 + y**2)",
        "pi * r**2",
        "exp(-x**2)",
        "log(1 + x)",
    ]


# =============================================================================
# PHASE 5-6 FIXTURES
# =============================================================================

@pytest.fixture
def thought_trace_harvester():
    """Create a ThoughtTraceHarvester for testing."""
    from symbo_agentic_reasoners.optimization.distillation.harvester import (
        ThoughtTraceHarvester
    )
    harvester = ThoughtTraceHarvester()
    yield harvester


@pytest.fixture
def mock_proof_state():
    """Create a mock proof state for testing deep search components."""
    from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
    return ProofState(
        state_id="test_proof_state",
        goal="x = x",
        hypotheses=["h1: x is natural"],
        depth=0
    )


@pytest.fixture
def curiosity_engine(mock_solver):
    """Create a CuriosityEngine with mock solver."""
    from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine
    engine = CuriosityEngine(solver=mock_solver)
    yield engine


# =============================================================================
# FIPA PROTOCOL FIXTURES
# =============================================================================

@pytest.fixture
def fipa_message():
    """Factory fixture to create FIPA-ACL messages."""
    from symbo_agentic_reasoners.protocols.fipa_acl import create_request

    def _create_message(
        sender="agent_a",
        receiver="agent_b",
        content=None
    ):
        return create_request(
            sender=sender,
            receiver=receiver,
            content=content or {"action": "test"}
        )

    return _create_message


# =============================================================================
# RESOURCE COORDINATION FIXTURES
# =============================================================================

@pytest.fixture
def resource_coordinator():
    """Create a ResourceCoordinator for testing."""
    from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
    coordinator = ResourceCoordinator()
    yield coordinator


@pytest.fixture
def mock_resource_coordinator():
    """Create a mock ResourceCoordinator."""
    coordinator = MagicMock()
    coordinator.can_proceed_with_task = MagicMock(return_value=True)
    coordinator.get_status = MagicMock(return_value={'vram_used': 0, 'vram_total': 16})
    return coordinator


# =============================================================================
# ORCHESTRATOR FIXTURES
# =============================================================================

@pytest.fixture
def orchestrator(blackboard, directory_facilitator):
    """Create a MainOrchestrator instance for testing."""
    from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
    orch = MainOrchestrator(df=directory_facilitator, blackboard=blackboard)
    yield orch


@pytest.fixture
def full_system():
    """Create a fully initialized system with supervisors for integration testing."""
    from symbo_agentic_reasoners.core.system import Phase0System
    from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
    from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
    from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor

    phase0 = Phase0System(allow_mock=True)
    phase0.start()

    # Register supervisors
    algebra_sup = AlgebraSupervisor(df=phase0.df, blackboard=phase0.blackboard)
    calculus_sup = CalculusSupervisor(df=phase0.df, blackboard=phase0.blackboard)

    orchestrator = MainOrchestrator(df=phase0.df, blackboard=phase0.blackboard)

    yield {
        'phase0': phase0,
        'orchestrator': orchestrator,
        'algebra_supervisor': algebra_sup,
        'calculus_supervisor': calculus_sup,
        'blackboard': phase0.blackboard,
        'df': phase0.df
    }

    phase0.shutdown()


# =============================================================================
# ADDITIONAL DOMAIN PROBLEM FIXTURES
# =============================================================================

@pytest.fixture
def physics_problems():
    """Provide physics-specific test problems."""
    return [
        ('F = m * a, m=5, a=10', '50'),  # Newton's second law
        ('v = d / t, d=100, t=10', '10'),  # velocity
        ('KE = 0.5 * m * v**2, m=2, v=3', '9'),  # kinetic energy
    ]


@pytest.fixture
def linalg_problems():
    """Provide linear algebra test problems."""
    return [
        ('det [[1, 2], [3, 4]]', '-2'),
        ('trace [[1, 0], [0, 2]]', '3'),
        ('eigenvalues [[2, 0], [0, 3]]', '[2, 3]'),
    ]


@pytest.fixture
def statistics_problems():
    """Provide statistics test problems."""
    return [
        ('mean [1, 2, 3, 4, 5]', '3'),
        ('variance [1, 2, 3, 4, 5]', '2'),
        ('std [1, 2, 3, 4, 5]', 'sqrt(2)'),
    ]
