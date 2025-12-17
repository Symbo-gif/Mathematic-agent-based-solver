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
Mock Supervisor for Testing
============================

This mock supervisor is ONLY for testing purposes.
It should NEVER be used in production code.

Usage in tests:
    from tests.mocks.mock_supervisor import MockSupervisor
    
    supervisor = MockSupervisor('algebra')
    result = supervisor.execute(task_context)
"""

from typing import Dict, Any


class MockSupervisor:
    """
    Mock supervisor for testing when real supervisors are not available
    
    WARNING: This is for TESTING ONLY. Production code should fail-fast
    when supervisors are not found, not fall back to mocks.
    """

    def __init__(self, domain: str):
        """
        Initialize mock supervisor
        
        Args:
            domain: Domain name (e.g., 'algebra', 'calculus')
        """
        self.domain = domain
        self.agent_id = f"mock_{domain}_supervisor"
        self.tasks_executed = 0

    def execute(self, task_context: Dict) -> Dict[str, Any]:
        """
        Mock execution - returns fake success result
        
        Args:
            task_context: Task context dictionary
            
        Returns:
            Mock result dictionary
        """
        self.tasks_executed += 1
        
        return {
            'status': 'SUCCESS',
            'result': f"Mock result for {self.domain}",
            'method': 'mock_execution',
            'mock': True,
            'warning': 'This is a mock result - not real computation'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get mock supervisor statistics"""
        return {
            'domain': self.domain,
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'mock': True
        }

    def __repr__(self) -> str:
        return f"MockSupervisor({self.domain})"

    def __str__(self) -> str:
        return f"Mock Supervisor for {self.domain} domain (TESTING ONLY)"
