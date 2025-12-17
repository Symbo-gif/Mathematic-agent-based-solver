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
        self.metrics['request_count'] += 1
        if success:
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
        uptime = time.time() - self.start_time
        return {
            'uptime': uptime,
            'requests_per_minute': self.metrics['request_count'] / (uptime / 60),
            **self.metrics
        }