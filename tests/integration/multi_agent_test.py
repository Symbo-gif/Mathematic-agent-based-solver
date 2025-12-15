import pytest
import time
from unittest.mock import MagicMock
from src.symbo_agentic_reasoners.core.message_bus import message_bus, AgentMessage, MessageType, MessagePriority
# NOTE: supervisor/ and specialists/ directories have been archived
# Orchestrator is now in core.orchestrator
# This test file references deprecated modules and may need updating
from src.symbo_agentic_reasoners.core.orchestrator import MainOrchestrator as OrchestratorAgent
# CalculusSpecialist, SymbolicSpecialist, VerificationSpecialist no longer exist
# Consider updating this test to use current architecture


def setup_test_environment():
    """Set up a test environment with mock agents"""
    # Clear existing handlers
    message_bus._handlers = {}
    message_bus._message_queue = []
    message_bus._message_store = {}
    
    # Create mock agents
    supervisor = OrchestratorAgent()
    calculus = CalculusSpecialist()
    symbolic = SymbolicSpecialist()
    verification = VerificationSpecialist()
    
    return supervisor, calculus, symbolic, verification


def test_agent_communication():
    """Test basic agent communication"""
    supervisor, calculus, symbolic, verification = setup_test_environment()
    
    # Test message routing
    problem = "limit((x^2 + 1)/(x - 1), x, ∞)"
    result = supervisor.solve(problem)
    
    # Verify message flow
    assert len(message_bus._message_store) > 0
    assert calculus._last_problem == problem
    assert calculus._last_result is not None


def test_calculus_specialist():
    """Test calculus specialist functionality"""
    _, calculus, _, _ = setup_test_environment()
    
    # Test limit calculation
    problem = "limit((x^2 + 1)/(x - 1), x, ∞)"
    result = calculus.solve(problem)
    assert result['value'] == "∞"
    
    # Test derivative
    problem = "derivative(x^2 + 3x + 2, x)"
    result = calculus.solve(problem)
    assert result['value'] == "2x + 3"


def test_symbolic_specialist():
    """Test symbolic specialist functionality"""
    _, _, symbolic, _ = setup_test_environment()
    
    # Test equation solving
    problem = "solve(x^2 + 5x + 6 = 0, x)"
    result = symbolic.solve(problem)
    assert set(result['solutions']) == set(["-2", "-3"])
    
    # Test simplification
    problem = "simplify((x^2 - 1)/(x - 1))"
    result = symbolic.solve(problem)
    assert result['value'] == "x + 1"


def test_verification_specialist():
    """Test verification specialist functionality"""
    _, _, _, verification = setup_test_environment()
    
    # Test valid solution
    problem = "limit((x^2 + 1)/(x - 1), x, ∞)"
    solution = {"value": "∞", "steps": ["step1", "step2"]}
    result = verification.validate_solution(problem, solution)
    assert result['valid'] is True
    assert result['confidence'] > 0.9
    
    # Test invalid solution
    problem = "derivative(x^2, x)"
    solution = {"value": "x", "steps": ["step1"]}
    result = verification.validate_solution(problem, solution)
    assert result['valid'] is False
    assert "Mathematical inconsistency" in result['issues'][0]


def test_error_handling():
    """Test system error handling"""
    supervisor, _, _, _ = setup_test_environment()
    
    # Test invalid problem
    problem = "limit((x^2 + 1)/(x - 1)"  # Missing closing parenthesis
    result = supervisor.solve(problem)
    assert "error" in result
    assert "Parentheses mismatch" in result['error']


def test_performance_under_load():
    """Test system performance under load"""
    supervisor, _, _, _ = setup_test_environment()
    
    # Generate multiple problems
    problems = [
        "limit((x^2 + {i})/(x - 1), x, ∞)" for i in range(50)
    ]
    
    start_time = time.time()
    results = [supervisor.solve(p) for p in problems]
    elapsed = time.time() - start_time
    
    # Verify performance metrics
    assert elapsed < 10.0  # Should handle 50 problems in under 10 seconds
    assert all('value' in r or 'error' in r for r in results)


def test_agent_failure_recovery():
    """Test system behavior when an agent fails"""
    supervisor, calculus, _, _ = setup_test_environment()
    
    # Mock calculus specialist to fail
    calculus.solve = MagicMock(side_effect=Exception("Simulated failure"))
    
    # Test problem routing
    problem = "limit((x^2 + 1)/(x - 1), x, ∞)"
    result = supervisor.solve(problem)
    
    # Verify fallback mechanism
    assert "error" in result
    assert "Calculus specialist failed" in result['error']
    assert "attempting fallback" in result['error']