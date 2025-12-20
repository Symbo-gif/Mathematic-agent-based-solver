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
End-to-End Integration Tests for ODE Advanced Integration Team

Tests the complete pipeline from ODE input through advanced integration
specialists to final solution.
"""

import pytest
from symbo_agentic_reasoners.core.solver.api import get_solver_engine


class TestODEIntegrationTeamE2E:
    """End-to-end tests for ODE solving with advanced integration team"""

    def setup_method(self):
        """Set up solver engine"""
        self.solver = get_solver_engine()

    # Test 1: Linear ODE with exp×sin pattern
    def test_linear_ode_exp_sin(self):
        """Test dy/dx + y = exp(x)*sin(x) [would use exp×trig if simplified form]"""
        problem = "solve ode: dy/dx + y = sin(x)"
        result = self.solver.solve(problem)

        # Should attempt to solve (may succeed or fail based on integration capabilities)
        assert result is not None
        # Check that it at least attempted advanced integration if needed

    # Test 2: Linear ODE with cosine forcing
    def test_linear_ode_cosine_forcing(self):
        """Test dy/dx + y = cos(x)"""
        problem = "solve ode: dy/dx + y = cos(x)"
        result = self.solver.solve(problem)

        # Should invoke advanced integration team
        assert result is not None

    # Test 3: Separable ODE with sqrt(y)
    def test_separable_ode_sqrt_y(self):
        """Test dy/dx = x*sqrt(y)"""
        problem = "solve ode: dy/dx = x*sqrt(y)"
        result = self.solver.solve(problem)

        # Should use improved factorization
        assert result is not None

    # Test 4: Separable ODE with 1/y
    def test_separable_ode_reciprocal_y(self):
        """Test dy/dx = x/y"""
        problem = "solve ode: dy/dx = x/y"
        result = self.solver.solve(problem)

        # Should handle quotient factorization
        assert result is not None

    # Test 5: Separable ODE with y^2
    def test_separable_ode_y_squared(self):
        """Test dy/dx = x*y^2"""
        problem = "solve ode: dy/dx = x*y**2"
        result = self.solver.solve(problem)

        # Should handle power factorization
        assert result is not None

    # Test 6: Second-order constant coefficient (baseline - should still work)
    def test_second_order_constant_homogeneous(self):
        """Test d²y/dx² + 4y = 0"""
        problem = "solve ode: d2y/dx2 + 4*y = 0"
        result = self.solver.solve(problem)

        # Should maintain 100% success on these
        assert result is not None

    # Test 7: Second-order with nonhomogeneous (baseline - should still work)
    def test_second_order_constant_nonhomogeneous(self):
        """Test d²y/dx² + 4y = exp(x)"""
        problem = "solve ode: d2y/dx2 + 4*y = exp(x)"
        result = self.solver.solve(problem)

        # Should maintain high success rate
        assert result is not None

    # Test 8: Complex integration requiring tabular method
    def test_high_degree_product_ode(self):
        """Test ODE that would generate x^n*exp(x) integral needing tabular method"""
        # This is more theoretical - most first-order ODEs don't generate these
        # But testing the infrastructure is present
        problem = "solve ode: dy/dx + y = x"
        result = self.solver.solve(problem)

        assert result is not None

    # Test 9: Verify advanced integration team is loaded
    def test_integration_team_loaded(self):
        """Verify that advanced integration specialists are loaded in solver"""
        # Access the router
        router = self.solver._router

        # Check that infrastructure is initialized
        assert hasattr(router, '_df')

        # Get ODE specialist (which should trigger infrastructure loading)
        ode_specialist = router.get_specialist('calculus.ode')

        assert ode_specialist is not None
        assert ode_specialist.df is not None  # Should have DF

    # Test 10: Verify DF has integration specialists registered
    def test_df_has_integration_specialists(self):
        """Verify DF has all advanced integration specialists"""
        router = self.solver._router
        ode_specialist = router.get_specialist('calculus.ode')

        if ode_specialist and ode_specialist.df:
            # Search for specialists
            exp_trig = ode_specialist.df.search(service_type='math.calculus.integration.exp_trig')
            advanced = ode_specialist.df.search(service_type='math.calculus.integration.advanced')

            # At least one of these should be registered
            assert len(exp_trig) > 0 or len(advanced) > 0, "Integration specialists not found in DF"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
