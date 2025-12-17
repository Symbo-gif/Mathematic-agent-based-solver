import time
import logging
from collections import defaultdict
from typing import Dict, Any, List, Tuple
import psutil
import GPUtil
from datetime import datetime


class AgentMonitor:
    """Monitors agent performance, resource usage, and communication"""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.start_time = time.time()
        
        # Performance metrics
        self.performance_metrics = {
            'request_count': 0,
            'response_count': 0,
            'error_count': 0,
            'processing_times': [],
            'throughput': 0.0
        }
        
        # Resource metrics
        self.resource_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'gpu_usage': []
        }
        
        # Agent-specific metrics
        self.agent_metrics = defaultdict(lambda: {
            'request_count': 0,
            'response_count': 0,
            'error_count': 0,
            'processing_times': [],
            'last_active': 0
        })
        
        # Communication metrics
        self.comm_metrics = {
            'message_queue_length': [],
            'message_processing_times': [],
            'failed_messages': []
        }
        
        self.logger = logging.getLogger('agent_monitor')
        
    def record_request(self, agent_id: str):
        """Record an incoming request for an agent"""
        self.performance_metrics['request_count'] += 1
        self.agent_metrics[agent_id]['request_count'] += 1
        self.agent_metrics[agent_id]['last_active'] = time.time()
        
    def record_response(self, agent_id: str, processing_time: float):
        """Record a response from an agent"""
        self.performance_metrics['response_count'] += 1
        self.performance_metrics['processing_times'].append(processing_time)
        self.agent_metrics[agent_id]['response_count'] += 1
        self.agent_metrics[agent_id]['processing_times'].append(processing_time)
        
    def record_error(self, agent_id: str, error_type: str, message: str):
        """Record an error from an agent"""
        self.performance_metrics['error_count'] += 1
        self.agent_metrics[agent_id]['error_count'] += 1
        self.logger.error(f"Agent {agent_id} error [{error_type}]: {message}")
        
    def record_communication(self, message_id: str, processing_time: float, success: bool):
        """Record communication metrics"""
        self.comm_metrics['message_processing_times'].append(processing_time)
        if not success:
            self.comm_metrics['failed_messages'].append(message_id)
        
    def sample_resources(self):
        """Sample system resource usage"""
        # CPU and memory
        self.resource_metrics['cpu_usage'].append(psutil.cpu_percent())
        self.resource_metrics['memory_usage'].append(psutil.virtual_memory().percent)
        
        # GPU if available
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                self.resource_metrics['gpu_usage'].append(gpus[0].load * 100)
        except:
            pass
        
    def calculate_throughput(self):
        """Calculate current system throughput"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.performance_metrics['throughput'] = self.performance_metrics['response_count'] / elapsed
        return self.performance_metrics['throughput']
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        self.calculate_throughput()
        
        # Calculate averages
        avg_processing_time = sum(self.performance_metrics['processing_times']) / len(self.performance_metrics['processing_times']) \
            if self.performance_metrics['processing_times'] else 0
            
        # Determine health status
        cpu_avg = sum(self.resource_metrics['cpu_usage']) / len(self.resource_metrics['cpu_usage']) \
            if self.resource_metrics['cpu_usage'] else 0
            
        health_status = 'healthy'
        if cpu_avg > 90 or self.performance_metrics['error_count'] > 10:
            health_status = 'degraded'
        if cpu_avg > 95 or self.performance_metrics['error_count'] > 50:
            health_status = 'critical'
            
        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'throughput': self.performance_metrics['throughput'],
                'avg_processing_time': avg_processing_time,
                'error_rate': self.performance_metrics['error_count'] / self.performance_metrics['request_count'] \
                    if self.performance_metrics['request_count'] > 0 else 0,
                'cpu_usage': cpu_avg,
                'memory_usage': sum(self.resource_metrics['memory_usage']) / len(self.resource_metrics['memory_usage']) \
                    if self.resource_metrics['memory_usage'] else 0
            },
            'agent_status': self._get_agent_status()
        }
        
    def _get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all agents"""
        status = {}
        for agent_id, metrics in self.agent_metrics.items():
            status[agent_id] = {
                'request_count': metrics['request_count'],
                'response_count': metrics['response_count'],
                'error_count': metrics['error_count'],
                'avg_processing_time': sum(metrics['processing_times']) / len(metrics['processing_times']) \
                    if metrics['processing_times'] else 0,
                'last_active': metrics['last_active'],
                'status': 'active' if (time.time() - metrics['last_active']) < 300 else 'inactive'
            }
        return status
        
    def generate_report(self) -> str:
        """Generate a human-readable system report"""
        health = self.get_system_health()
        report = f"""SYSTEM HEALTH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {health['status'].upper()}

METRICS:
  Throughput: {health['metrics']['throughput']:.2f} responses/sec
  Avg Processing Time: {health['metrics']['avg_processing_time']:.4f} sec
  Error Rate: {health['metrics']['error_rate']:.2%}
  CPU Usage: {health['metrics']['cpu_usage']:.1f}%
  Memory Usage: {health['metrics']['memory_usage']:.1f}%

AGENT STATUS:"""

        for agent_id, status in health['agent_status'].items():
            report += f"\n  - {agent_id}: {status['status'].upper()}"
            report += f"\n    Requests: {status['request_count']}, Responses: {status['response_count']}, Errors: {status['error_count']}"
            report += f"\n    Avg Processing: {status['avg_processing_time']:.4f} sec"
            
        return report