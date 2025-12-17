import random


class RainbowDeployment:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.active_versions = {1: orchestrator}
        self.traffic_distribution = {1: 1.0}  # All traffic to version 1 initially
        self.new_version = None
        
    def deploy_new_version(self, new_orchestrator):
        """Deploy a new version without disrupting active sessions"""
        version_id = max(self.active_versions.keys()) + 1
        self.new_version = new_orchestrator
        self.active_versions[version_id] = new_orchestrator
        
        # Start with 0% traffic to new version
        self.traffic_distribution[version_id] = 0.0
        self.traffic_distribution[max(self.traffic_distribution.keys())-1] = 1.0
        
        return version_id
        
    def shift_traffic(self, version_id, percentage):
        """Gradually shift traffic to new version"""
        if version_id not in self.active_versions:
            raise ValueError(f"Version {version_id} not deployed")
            
        # Calculate how much to reduce from current main version
        current_main = max(k for k, v in self.traffic_distribution.items() if v > 0)
        reduction = min(percentage, self.traffic_distribution[current_main])
        
        # Update distribution
        self.traffic_distribution[current_main] -= reduction
        self.traffic_distribution[version_id] += reduction
        
        return self.traffic_distribution
        
    def route_request(self, problem):
        """Route request based on current traffic distribution"""
        # Determine which version to use based on traffic distribution
        rand_val = random.random()
        cumulative = 0.0
        
        for version_id, percentage in self.traffic_distribution.items():
            cumulative += percentage
            if rand_val < cumulative:
                return self.active_versions[version_id].route_problem(problem)
                
        # Fallback to main version
        main_version = max(k for k, v in self.traffic_distribution.items() if v > 0)
        return self.active_versions[main_version].route_problem(problem)
        
    def complete_deployment(self, version_id):
        """Complete deployment by shifting all traffic to new version"""
        # First shift remaining traffic
        self.shift_traffic(version_id, 1.0)
        
        # Remove old versions (keeping previous version for rollback)
        versions_to_remove = [
            v for v in self.active_versions.keys() 
            if v < version_id - 1
        ]
        
        for version in versions_to_remove:
            del self.active_versions[version]
            del self.traffic_distribution[version]
            
        return len(versions_to_remove)