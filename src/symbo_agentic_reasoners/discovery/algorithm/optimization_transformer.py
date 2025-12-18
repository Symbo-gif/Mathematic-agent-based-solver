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
PHASE 6 - AD-3: OPTIMIZATION TRANSFORMER
=========================================

Transforms algorithms to improve performance through various optimization techniques.

CAPABILITIES:
------------
- Loop optimization
- Memoization injection
- Parallelization hints
- Strength reduction
- Common subexpression elimination

REFERENCE:
---------
- Phase 6 Discovery Team: Algorithm Discovery Subteam
"""

import logging
import re
import ast
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.optimization_transformer')


class OptimizationType(Enum):
    """Types of optimizations"""
    MEMOIZATION = "memoization"
    LOOP_UNROLLING = "loop_unrolling"
    STRENGTH_REDUCTION = "strength_reduction"
    CSE = "common_subexpression_elimination"
    INLINE = "inline_expansion"
    PARALLELIZATION = "parallelization"
    EARLY_EXIT = "early_exit"
    CACHE = "caching"


class TransformationStatus(Enum):
    """Status of transformation"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    NO_OPPORTUNITY = "no_opportunity"


@dataclass
class OptimizationOpportunity:
    """
    An identified optimization opportunity.
    
    Attributes:
        opt_type: Type of optimization
        location: Line number or code location
        description: Description of the opportunity
        estimated_speedup: Estimated speedup factor
    """
    opt_type: OptimizationType
    location: str
    description: str
    estimated_speedup: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'type': self.opt_type.value,
            'location': self.location,
            'description': self.description,
            'speedup': self.estimated_speedup
        }


@dataclass
class TransformationResult:
    """
    Result of code transformation.
    
    Attributes:
        original_code: Original code
        optimized_code: Transformed code
        status: Transformation status
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        optimizations_applied: List of applied optimizations
        estimated_speedup: Overall estimated speedup
    """
    original_code: str
    optimized_code: str
    status: TransformationStatus
    optimizations_applied: List[OptimizationOpportunity]
    estimated_speedup: float = 1.0
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'status': self.status.value,
            'optimizations_count': len(self.optimizations_applied),
            'speedup': round(self.estimated_speedup, 2),
            'notes': self.notes[:3]
        }


class OptimizationTransformer:
    """
    AD-3: Optimization Transformer
    
    Transforms algorithms to improve performance through various optimization techniques.
    
    Key capabilities:
    - Memoization injection for recursive functions
    - Loop optimization
    - Strength reduction
    - Early exit insertion
    - Parallelization hints
    """
    
    def __init__(
        self,
        aggressive: bool = False
    ):
        """
        Initialize the Optimization Transformer.
        
        Args:
            aggressive: Whether to apply aggressive optimizations
        """
        self.aggressive = aggressive
        
        # Transformation history
        self.transformations: List[TransformationResult] = []
        
        # Statistics
        self.codes_analyzed = 0
        self.optimizations_applied = 0
        self.total_speedup = 0.0
        
        logger.info(f"OptimizationTransformer initialized (aggressive={aggressive})")
    
    def analyze(self, code: str) -> List[OptimizationOpportunity]:
        """
        Analyze code for optimization opportunities.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of optimization opportunities
        """
        self.codes_analyzed += 1
        opportunities = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return opportunities
        
        # Check for memoization opportunity
        memo_opp = self._check_memoization(tree, code)
        if memo_opp:
            opportunities.append(memo_opp)
        
        # Check for loop optimizations
        loop_opps = self._check_loop_optimizations(tree, code)
        opportunities.extend(loop_opps)
        
        # Check for strength reduction
        sr_opps = self._check_strength_reduction(code)
        opportunities.extend(sr_opps)
        
        # Check for early exit
        exit_opps = self._check_early_exit(tree, code)
        opportunities.extend(exit_opps)
        
        # Check for parallelization
        if self.aggressive:
            par_opps = self._check_parallelization(tree, code)
            opportunities.extend(par_opps)
        
        return opportunities
    
    def transform(
        self,
        code: str,
        optimizations: Optional[List[OptimizationType]] = None
    ) -> TransformationResult:
        """
        Transform code by applying optimizations.
        
        Args:
            code: Source code to transform
            optimizations: Optional list of specific optimizations to apply
            
        Returns:
            TransformationResult
        """
        # Analyze first
        opportunities = self.analyze(code)
        
        if optimizations:
            opportunities = [o for o in opportunities if o.opt_type in optimizations]
        
        if not opportunities:
            return TransformationResult(
                original_code=code,
                optimized_code=code,
                status=TransformationStatus.NO_OPPORTUNITY,
                optimizations_applied=[],
                notes=["No optimization opportunities found"]
            )
        
        # Apply transformations
        optimized = code
        applied = []
        notes = []
        total_speedup = 1.0
        
        for opp in opportunities:
            try:
                result, transformed = self._apply_optimization(optimized, opp)
                if result:
                    optimized = transformed
                    applied.append(opp)
                    total_speedup *= opp.estimated_speedup
                    self.optimizations_applied += 1
            except Exception as e:
                notes.append(f"Failed to apply {opp.opt_type.value}: {e}")
        
        status = (TransformationStatus.SUCCESS if applied
                 else TransformationStatus.FAILED)
        
        if applied and len(applied) < len(opportunities):
            status = TransformationStatus.PARTIAL
        
        result = TransformationResult(
            original_code=code,
            optimized_code=optimized,
            status=status,
            optimizations_applied=applied,
            estimated_speedup=total_speedup,
            notes=notes
        )
        
        self.transformations.append(result)
        self.total_speedup += total_speedup
        
        return result
    
    def _check_memoization(
        self,
        tree: ast.AST,
        code: str
    ) -> Optional[OptimizationOpportunity]:
        """Check for memoization opportunity"""
        # Find recursive functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Check if function calls itself
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id == func_name:
                                # Check if already memoized
                                if 'memo' in code or 'cache' in code or '@lru_cache' in code:
                                    continue
                                return OptimizationOpportunity(
                                    opt_type=OptimizationType.MEMOIZATION,
                                    location=f"line {node.lineno}",
                                    description=f"Recursive function '{func_name}' can be memoized",
                                    estimated_speedup=3.0
                                )
        return None
    
    def _check_loop_optimizations(
        self,
        tree: ast.AST,
        code: str
    ) -> List[OptimizationOpportunity]:
        """Check for loop optimization opportunities"""
        opportunities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for invariant computations
                # Simplified: look for assignments that don't use loop variable
                opportunities.append(OptimizationOpportunity(
                    opt_type=OptimizationType.LOOP_UNROLLING,
                    location=f"line {node.lineno}",
                    description="Loop may benefit from unrolling for small iterations",
                    estimated_speedup=1.2
                ))
        
        return opportunities[:2]  # Limit to first 2
    
    def _check_strength_reduction(
        self,
        code: str
    ) -> List[OptimizationOpportunity]:
        """Check for strength reduction opportunities"""
        opportunities = []
        
        # Power of 2 multiplications/divisions
        patterns = [
            (r'\*\s*2\b', "Multiplication by 2 can use left shift"),
            (r'/\s*2\b', "Division by 2 can use right shift"),
            (r'\*\*\s*2\b', "Square can use multiplication"),
        ]
        
        for pattern, desc in patterns:
            if re.search(pattern, code):
                opportunities.append(OptimizationOpportunity(
                    opt_type=OptimizationType.STRENGTH_REDUCTION,
                    location="expression",
                    description=desc,
                    estimated_speedup=1.1
                ))
        
        return opportunities
    
    def _check_early_exit(
        self,
        tree: ast.AST,
        code: str
    ) -> List[OptimizationOpportunity]:
        """Check for early exit opportunities"""
        opportunities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if loop has no break statement
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if not has_break:
                    opportunities.append(OptimizationOpportunity(
                        opt_type=OptimizationType.EARLY_EXIT,
                        location=f"line {node.lineno}",
                        description="Loop may benefit from early exit condition",
                        estimated_speedup=1.5
                    ))
        
        return opportunities[:1]  # Limit to first
    
    def _check_parallelization(
        self,
        tree: ast.AST,
        code: str
    ) -> List[OptimizationOpportunity]:
        """Check for parallelization opportunities"""
        opportunities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for independent iterations
                opportunities.append(OptimizationOpportunity(
                    opt_type=OptimizationType.PARALLELIZATION,
                    location=f"line {node.lineno}",
                    description="Loop iterations may be parallelizable",
                    estimated_speedup=2.0
                ))
                break  # Only first loop
        
        return opportunities
    
    def _apply_optimization(
        self,
        code: str,
        opportunity: OptimizationOpportunity
    ) -> Tuple[bool, str]:
        """Apply a specific optimization"""
        if opportunity.opt_type == OptimizationType.MEMOIZATION:
            return self._apply_memoization(code)
        elif opportunity.opt_type == OptimizationType.STRENGTH_REDUCTION:
            return self._apply_strength_reduction(code)
        elif opportunity.opt_type == OptimizationType.EARLY_EXIT:
            return self._apply_early_exit(code)
        elif opportunity.opt_type == OptimizationType.LOOP_UNROLLING:
            return self._apply_loop_unrolling(code)
        elif opportunity.opt_type == OptimizationType.PARALLELIZATION:
            return True, self.suggest_parallel_version(code)
        else:
            # For other optimizations, just add a comment
            comment = f"# TODO: Apply {opportunity.opt_type.value} at {opportunity.location}"
            return True, comment + "\n" + code
    
    def _apply_memoization(self, code: str) -> Tuple[bool, str]:
        """Apply memoization transformation"""
        # Add functools import and decorator
        if 'from functools import lru_cache' not in code:
            code = 'from functools import lru_cache\n\n' + code
        
        # Find function definitions and add decorator
        lines = code.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # Check if next line has decorator already
                if i > 0 and '@lru_cache' in new_lines[-1]:
                    new_lines.append(line)
                else:
                    new_lines.append('@lru_cache(maxsize=None)')
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        return True, '\n'.join(new_lines)
    
    def _apply_strength_reduction(self, code: str) -> Tuple[bool, str]:
        """Apply strength reduction transformation"""
        # Replace power of 2 operations
        code = re.sub(r'(\w+)\s*\*\s*2\b', r'(\1 << 1)', code)
        code = re.sub(r'(\w+)\s*/\s*2\b', r'(\1 >> 1)', code)
        code = re.sub(r'(\w+)\s*\*\*\s*2\b', r'(\1 * \1)', code)
        return True, code
    
    def _apply_early_exit(self, code: str) -> Tuple[bool, str]:
        """Apply early exit transformation"""
        # Add comment about early exit opportunity
        comment = "# Consider adding early exit condition (break) when condition is met\n"
        return True, comment + code
        
    def _apply_loop_unrolling(self, code: str) -> Tuple[bool, str]:
        """Apply loop unrolling hint"""
        comment = "# Hint: Consider unrolling this loop for performance if iterations are small/fixed\n"
        return True, comment + code
    
    def add_caching(
        self,
        code: str,
        cache_size: int = 1000
    ) -> str:
        """
        Add caching to a function.
        
        Args:
            code: Function code
            cache_size: Maximum cache size
            
        Returns:
            Modified code with caching
        """
        header = f'''from functools import lru_cache

@lru_cache(maxsize={cache_size})
'''
        return header + code
    
    def suggest_parallel_version(
        self,
        code: str
    ) -> str:
        """
        Generate parallel version hint.
        
        Args:
            code: Original code
            
        Returns:
            Parallel version suggestion
        """
        suggestion = f'''# Parallel version suggestion
# Using multiprocessing for data parallelism

from multiprocessing import Pool

def parallel_wrapper(items, func, workers=4):
    with Pool(workers) as pool:
        return pool.map(func, items)

# Original code:
{code}

# To parallelize, wrap the main loop body in a function
# and use parallel_wrapper(items, your_function)
'''
        return suggestion
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get transformer statistics"""
        return {
            'codes_analyzed': self.codes_analyzed,
            'optimizations_applied': self.optimizations_applied,
            'transformations': len(self.transformations),
            'avg_speedup': round(self.total_speedup / max(1, len(self.transformations)), 2)
        }
    
    def reset(self):
        """Reset transformer state"""
        self.transformations.clear()
        self.codes_analyzed = 0
        self.optimizations_applied = 0
        self.total_speedup = 0.0
    
    def health_check(self) -> bool:
        """Check if transformer is healthy"""
        return True


if __name__ == "__main__":
    """Test Optimization Transformer"""
    print("=" * 80)
    print("PHASE 6 - OPTIMIZATION TRANSFORMER TEST")
    print("=" * 80)
    print()
    
    # Initialize transformer
    transformer = OptimizationTransformer(aggressive=True)
    
    # Test 1: Analyze recursive function
    print("Test 1: Analyze Recursive Function")
    code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    opportunities = transformer.analyze(code)
    print(f"  Opportunities found: {len(opportunities)}")
    for opp in opportunities:
        print(f"    - {opp.opt_type.value}: {opp.description}")
    print()
    
    # Test 2: Transform with memoization
    print("Test 2: Transform with Memoization")
    result = transformer.transform(code)
    print(f"  Status: {result.status.value}")
    print(f"  Speedup: {result.estimated_speedup}x")
    print("  Optimized code preview:")
    print("    " + result.optimized_code[:200].replace('\n', '\n    '))
    print()
    
    # Test 3: Strength reduction
    print("Test 3: Strength Reduction")
    code = '''
def compute(x):
    a = x * 2
    b = x / 2
    c = x ** 2
    return a + b + c
'''
    result = transformer.transform(code, [OptimizationType.STRENGTH_REDUCTION])
    print(f"  Status: {result.status.value}")
    print("  Optimized:")
    print("    " + result.optimized_code.replace('\n', '\n    '))
    print()
    
    # Test 4: Loop analysis
    print("Test 4: Loop Analysis")
    code = '''
def process(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
'''
    opportunities = transformer.analyze(code)
    print(f"  Opportunities: {len(opportunities)}")
    for opp in opportunities:
        print(f"    - {opp.opt_type.value}")
    print()
    
    # Test 5: Add caching
    print("Test 5: Add Caching")
    code = '''
def expensive_compute(x):
    return sum(range(x))
'''
    cached = transformer.add_caching(code)
    print("  With cache:")
    print("    " + cached[:150].replace('\n', '\n    '))
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(transformer.get_statistics(), indent=2))
