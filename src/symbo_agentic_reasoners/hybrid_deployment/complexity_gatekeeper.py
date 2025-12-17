import logging
from enum import Enum
from typing import Tuple, Any, Optional

logger = logging.getLogger(__name__)

class QueryRoute(Enum):
    """Routing decision for a query"""
    STUDENT = "student"
    TEACHER = "teacher"

class ComplexityGatekeeper:
    """
    Routes queries between Student and Teacher models based on estimated complexity.
    """
    
    def __init__(self, student_model: Any, teacher_system: Any):
        self.student_model = student_model
        self.teacher_system = teacher_system
        
    def classify_query(self, query: str) -> Tuple[float, str]:
        """
        Classify a query to determine its complexity and type.
        
        Args:
            query: The user's query string
            
        Returns:
            Tuple of (complexity_score, query_type)
        """
        query_lower = query.lower()
        
        # Default values
        complexity_score = 0.1
        query_type = "general"
        
        # Heuristic classification
        if "prove" in query_lower or "theorem" in query_lower or "hypothesis" in query_lower:
            complexity_score = 0.8
            query_type = "proof"
        elif "algorithm" in query_lower or "discover" in query_lower or "novel" in query_lower:
            complexity_score = 0.9
            query_type = "optimization" # Discovery often falls under optimization/search
        elif "integrate" in query_lower or "derivative" in query_lower or "solve" in query_lower:
            complexity_score = 0.4
            query_type = "computation"
        elif "simplify" in query_lower or "calculate" in query_lower:
            complexity_score = 0.2
            query_type = "computation"
            
        # Adjust complexity based on length/structure
        if len(query) > 100:
            complexity_score += 0.1
            
        return min(complexity_score, 1.0), query_type
        
    def route_query(self, query: str) -> QueryRoute:
        """
        Decide where to route the query.
        
        Args:
            query: The user's query
            
        Returns:
            QueryRoute.STUDENT or QueryRoute.TEACHER
        """
        score, _ = self.classify_query(query)
        
        # Threshold for routing to teacher
        TEACHER_THRESHOLD = 0.7
        
        if score >= TEACHER_THRESHOLD:
            return QueryRoute.TEACHER
        return QueryRoute.STUDENT
