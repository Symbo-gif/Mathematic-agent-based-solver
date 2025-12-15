import pytest
# NOTE: supervisor/ and specialists/ directories have been archived
# Orchestrator is now in core.orchestrator
# This test file references deprecated modules and may need updating
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator as OrchestratorAgent
# CalculusSpecialist, SymbolicSpecialist, VerificationSpecialist no longer exist
# Consider updating this test to use current architecture


class TestMultiAgentIntegration:
    @pytest.fixture
    def orchestrator(self):
        return OrchestratorAgent()
    
    def test_calculus_routing(self, orchestrator):
        problem = "limit((x^2 + 1)/(x - 1), x, ∞)"
        result = orchestrator.route_problem(problem)
        
        assert result['agent'] == 'calculus'
        assert 'value' in result
        assert 'metadata' in result
        assert result['metadata']['assumptions'] == {'x': '→∞'}
        
        # Verify through multiple paths
        verification = VerificationSpecialist().validate_solution(problem, result['value'])
        assert verification['valid'] is True
        assert verification['confidence'] > 0.95
        
    def test_symbolic_routing(self, orchestrator):
        problem = "solve(x^2 + 5x + 6 = 0, x)"
        result = orchestrator.route_problem(problem)
        
        assert result['agent'] == 'symbolic'
        assert 'solutions' in result
        assert len(result['solutions']) == 2
        
        # Verify through multiple paths
        verification = VerificationSpecialist().validate_solution(problem, result['solutions'])
        assert verification['valid'] is True
        
    def test_error_recovery(self, orchestrator):
        # Test with deliberately malformed input
        problem = "limit((x^2 + 1)/(x - 1)"  # Missing closing parenthesis
        result = orchestrator.route_problem(problem)
        
        # Should have been auto-corrected by input normalizer
        assert 'corrected' in result['metadata']
        assert result['metadata']['original'] == "limit((x^2 + 1)/(x - 1)"
        assert result['metadata']['corrected'] == "limit((x^2 + 1)/(x - 1))"
        
        # Verify the solution is still valid
        verification = VerificationSpecialist().validate_solution(
            result['metadata']['corrected'], 
            result['value']
        )
        assert verification['valid'] is True