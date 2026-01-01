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

class PerformanceTracker:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0,
            'error_types': defaultdict(int)
        }
        self.start_time = time.time()
        
    def record_request(self, success, response_time, error_type=None):
        """Perform record request operation.

        Args:
        success: Description needed
        response_time: Description needed
        error_type: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.record_request(...)
        """
        """Perform record request operation.

        Args:
        success: Description needed
        response_time: Description needed
        error_type: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.record_request(...)
        """
        self.metrics['request_count'] += 1
        if success:
            """Get system health.

            Returns:
            System health value or data

            Example:
            >>> result = obj.get_system_health()
            """
            self.metrics['success_rate'] = (
                (self.metrics['request_count'] - 1) * self.metrics['success_rate'] + 1
            ) / self.metrics['request_count']
        else:
            self.metrics['error_types'][error_type] += 1
            
        # Update average response time
        self.metrics['avg_response_time'] = (
            (self.metrics['request_count'] - 1) * self.metrics['avg_response_time'] + response_time
        ) / self.metrics['request_count']
        
    def get_system_health(self):
        """Get system health.

        Returns:
        System health value or data

        Example:
        >>> result = obj.get_system_health()
        """
        uptime = time.time() - self.start_time
        return {
            'uptime': uptime,
            'requests_per_minute': self.metrics['request_count'] / (uptime / 60),
            **self.metrics
        }
