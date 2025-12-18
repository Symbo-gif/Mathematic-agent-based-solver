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
PHASE 6 - DS-1: EXHAUSTIVE ENUMERATOR
======================================

Systematically enumerates mathematical structures and search spaces
for complete exploration.

CAPABILITIES:
------------
- Systematic structure enumeration
- Bounded exhaustive search
- Combinatorial generation
- Progress tracking
- Early termination conditions

REFERENCE:
---------
- Phase 6 Discovery Team: Deep Search Subteam
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Generator, Callable, Tuple, Iterator
from datetime import datetime
from enum import Enum
import itertools

logger = logging.getLogger('symbo_agentic_reasoners.phase6.exhaustive_enumerator')


class EnumerationStrategy(Enum):
    """Enumeration strategies"""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    FAIR = "fair"  # Interleaves across dimensions
    RANDOM_SAMPLE = "random_sample"


class EnumerationStatus(Enum):
    """Status of enumeration"""
    RUNNING = "running"
    COMPLETE = "complete"
    TERMINATED = "terminated"
    TIMEOUT = "timeout"


@dataclass
class EnumerationSpace:
    """
    Definition of a space to enumerate.
    
    Attributes:
        space_id: Unique identifier
        dimensions: Named dimensions with their domains
        constraints: Constraints between dimensions
        size_estimate: Estimated total size
    """
    space_id: str
    dimensions: Dict[str, List[Any]]
    constraints: List[Callable[[Dict[str, Any]], bool]] = field(default_factory=list)
    size_estimate: Optional[int] = None
    
    def __post_init__(self):
        if self.size_estimate is None:
            self.size_estimate = 1
            for dim_values in self.dimensions.values():
                self.size_estimate *= len(dim_values)
    
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
            'id': self.space_id,
            'dimensions': list(self.dimensions.keys()),
            'size_estimate': self.size_estimate
        }


@dataclass
class EnumerationResult:
    """
    Result of an enumeration task.
    
    Attributes:
        space: The enumerated space
        status: Final status
        items_generated: Total items generated
        items_accepted: Items passing constraints
        matches_found: Items matching target condition
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        sample: Sample of generated items
    """
    space: EnumerationSpace
    status: EnumerationStatus
    items_generated: int
    items_accepted: int
    matches_found: List[Dict[str, Any]]
    sample: List[Dict[str, Any]] = field(default_factory=list)
    elapsed_time_ms: int = 0
    
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
            'space_id': self.space.space_id,
            'status': self.status.value,
            'generated': self.items_generated,
            'accepted': self.items_accepted,
            'matches': len(self.matches_found),
            'time_ms': self.elapsed_time_ms
        }


class ExhaustiveEnumerator:
    """
    DS-1: Exhaustive Enumerator
    
    Systematically enumerates mathematical structures and search spaces
    for complete exploration.
    
    Key capabilities:
    - Product space enumeration
    - Constraint filtering
    - Multiple enumeration strategies
    - Progress tracking
    - Early termination
    """
    
    def __init__(
        self,
        max_items: int = 1000000,
        timeout_seconds: float = 60.0
    ):
        """
        Initialize the Exhaustive Enumerator.
        
        Args:
            max_items: Maximum items to generate before stopping
            timeout_seconds: Maximum time before timeout
        """
        self.max_items = max_items
        self.timeout_seconds = timeout_seconds
        
        # Statistics
        self.total_enumerations = 0
        self.total_items_generated = 0
        self.total_matches_found = 0
        
        logger.info(f"ExhaustiveEnumerator initialized (max={max_items})")
    
    def enumerate(
        self,
        space: EnumerationSpace,
        target_condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        strategy: EnumerationStrategy = EnumerationStrategy.BREADTH_FIRST,
        max_matches: int = 100
    ) -> EnumerationResult:
        """
        Enumerate a space looking for items matching a condition.
        
        Args:
            space: The space to enumerate
            target_condition: Condition to match (None = collect all)
            strategy: Enumeration strategy
            max_matches: Stop after finding this many matches
            
        Returns:
            EnumerationResult with findings
        """
        import time
        start_time = time.time()
        
        self.total_enumerations += 1
        
        items_generated = 0
        items_accepted = 0
        matches = []
        sample = []
        
        try:
            # Get appropriate iterator
            if strategy == EnumerationStrategy.RANDOM_SAMPLE:
                iterator = self._random_iterator(space)
            elif strategy == EnumerationStrategy.FAIR:
                iterator = self._fair_iterator(space)
            else:
                iterator = self._product_iterator(space)
            
            for item in iterator:
                items_generated += 1
                self.total_items_generated += 1
                
                # Check constraints
                if not self._check_constraints(item, space.constraints):
                    continue
                
                items_accepted += 1
                
                # Keep sample
                if len(sample) < 10:
                    sample.append(item.copy())
                
                # Check target condition
                if target_condition is None or target_condition(item):
                    matches.append(item.copy())
                    self.total_matches_found += 1
                    
                    if len(matches) >= max_matches:
                        return EnumerationResult(
                            space=space,
                            status=EnumerationStatus.TERMINATED,
                            items_generated=items_generated,
                            items_accepted=items_accepted,
                            matches_found=matches,
                            sample=sample,
                            elapsed_time_ms=int((time.time() - start_time) * 1000)
                        )
                
                # Check limits
                if items_generated >= self.max_items:
                    return EnumerationResult(
                        space=space,
                        status=EnumerationStatus.TERMINATED,
                        items_generated=items_generated,
                        items_accepted=items_accepted,
                        matches_found=matches,
                        sample=sample,
                        elapsed_time_ms=int((time.time() - start_time) * 1000)
                    )
                
                # Check timeout
                if time.time() - start_time > self.timeout_seconds:
                    return EnumerationResult(
                        space=space,
                        status=EnumerationStatus.TIMEOUT,
                        items_generated=items_generated,
                        items_accepted=items_accepted,
                        matches_found=matches,
                        sample=sample,
                        elapsed_time_ms=int((time.time() - start_time) * 1000)
                    )
            
            # Completed full enumeration
            status = EnumerationStatus.COMPLETE
            
        except Exception as e:
            logger.warning(f"Enumeration error: {type(e).__name__}: {e}")
            status = EnumerationStatus.TERMINATED
        
        return EnumerationResult(
            space=space,
            status=status,
            items_generated=items_generated,
            items_accepted=items_accepted,
            matches_found=matches,
            sample=sample,
            elapsed_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _product_iterator(
        self,
        space: EnumerationSpace
    ) -> Iterator[Dict[str, Any]]:
        """Generate Cartesian product of all dimensions"""
        dim_names = list(space.dimensions.keys())
        dim_values = [space.dimensions[name] for name in dim_names]
        
        for combo in itertools.product(*dim_values):
            yield dict(zip(dim_names, combo))
    
    def _random_iterator(
        self,
        space: EnumerationSpace
    ) -> Iterator[Dict[str, Any]]:
        """Generate random samples from the space"""
        import random
        
        dim_names = list(space.dimensions.keys())
        dim_values = [space.dimensions[name] for name in dim_names]
        
        for _ in range(self.max_items):
            combo = [random.choice(vals) for vals in dim_values]
            yield dict(zip(dim_names, combo))
    
    def _fair_iterator(
        self,
        space: EnumerationSpace
    ) -> Iterator[Dict[str, Any]]:
        """Fair interleaving across dimensions"""
        # Use diagonal enumeration for fair coverage
        dim_names = list(space.dimensions.keys())
        dim_values = [space.dimensions[name] for name in dim_names]
        dim_sizes = [len(vals) for vals in dim_values]
        
        if not dim_sizes:
            return
        
        # Generate items by increasing "total index"
        max_total = sum(s - 1 for s in dim_sizes)
        
        for total_idx in range(max_total + 1):
            for combo in self._partitions(total_idx, dim_sizes):
                if all(c < s for c, s in zip(combo, dim_sizes)):
                    yield {
                        dim_names[i]: dim_values[i][combo[i]]
                        for i in range(len(dim_names))
                    }
    
    def _partitions(
        self,
        total: int,
        sizes: List[int]
    ) -> Iterator[List[int]]:
        """Generate partitions of total into len(sizes) parts"""
        if len(sizes) == 1:
            if total < sizes[0]:
                yield [total]
        else:
            for first in range(min(total + 1, sizes[0])):
                for rest in self._partitions(total - first, sizes[1:]):
                    yield [first] + rest
    
    def _check_constraints(
        self,
        item: Dict[str, Any],
        constraints: List[Callable]
    ) -> bool:
        """Check if item satisfies all constraints"""
        return all(c(item) for c in constraints)
    
    def enumerate_integers(
        self,
        n: int,
        dimensions: int = 1,
        target: Optional[Callable] = None
    ) -> EnumerationResult:
        """
        Convenience method to enumerate integer tuples.
        
        Args:
            n: Range for each dimension [0, n)
            dimensions: Number of dimensions
            target: Target condition
            
        Returns:
            EnumerationResult
        """
        space = EnumerationSpace(
            space_id=f"integers_{n}_{dimensions}",
            dimensions={
                f"x{i}": list(range(n))
                for i in range(dimensions)
            }
        )
        
        return self.enumerate(space, target)
    
    def enumerate_permutations(
        self,
        elements: List[Any],
        target: Optional[Callable] = None
    ) -> EnumerationResult:
        """
        Enumerate all permutations of elements.
        
        Args:
            elements: Elements to permute
            target: Target condition
            
        Returns:
            EnumerationResult
        """
        import time
        start_time = time.time()
        
        self.total_enumerations += 1
        
        items_generated = 0
        matches = []
        
        for perm in itertools.permutations(elements):
            items_generated += 1
            self.total_items_generated += 1
            
            item = {'permutation': list(perm)}
            
            if target is None or target(item):
                matches.append(item)
                self.total_matches_found += 1
            
            if items_generated >= self.max_items:
                break
        
        space = EnumerationSpace(
            space_id=f"permutations_{len(elements)}",
            dimensions={'permutation': []}
        )
        
        return EnumerationResult(
            space=space,
            status=EnumerationStatus.COMPLETE,
            items_generated=items_generated,
            items_accepted=items_generated,
            matches_found=matches,
            elapsed_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enumerator statistics"""
        return {
            'total_enumerations': self.total_enumerations,
            'total_items_generated': self.total_items_generated,
            'total_matches_found': self.total_matches_found
        }
    
    def reset(self):
        """Reset enumerator state"""
        self.total_enumerations = 0
        self.total_items_generated = 0
        self.total_matches_found = 0
    
    def health_check(self) -> bool:
        """Check if enumerator is healthy"""
        return True


if __name__ == "__main__":
    """Test Exhaustive Enumerator"""
    print("=" * 80)
    print("PHASE 6 - EXHAUSTIVE ENUMERATOR TEST")
    print("=" * 80)
    print()
    
    # Initialize enumerator
    enumerator = ExhaustiveEnumerator(max_items=10000)
    
    # Test 1: Simple enumeration
    print("Test 1: Enumerate 2D Space")
    space = EnumerationSpace(
        space_id="test_2d",
        dimensions={
            "x": list(range(5)),
            "y": list(range(5))
        }
    )
    result = enumerator.enumerate(space)
    print(f"  Status: {result.status.value}")
    print(f"  Generated: {result.items_generated}")
    print(f"  Sample: {result.sample[:3]}")
    print()
    
    # Test 2: With condition
    print("Test 2: Find Pythagorean Triples")
    space = EnumerationSpace(
        space_id="pythag",
        dimensions={
            "a": list(range(1, 20)),
            "b": list(range(1, 20)),
            "c": list(range(1, 25))
        }
    )
    result = enumerator.enumerate(
        space,
        target_condition=lambda x: x['a']**2 + x['b']**2 == x['c']**2 and x['a'] < x['b']
    )
    print(f"  Triples found: {len(result.matches_found)}")
    for t in result.matches_found[:5]:
        print(f"    ({t['a']}, {t['b']}, {t['c']})")
    print()
    
    # Test 3: Permutations
    print("Test 3: Enumerate Permutations")
    result = enumerator.enumerate_permutations([1, 2, 3, 4])
    print(f"  Permutations: {result.items_generated}")
    print()
    
    # Test 4: With constraints
    print("Test 4: Constrained Enumeration")
    space = EnumerationSpace(
        space_id="constrained",
        dimensions={
            "x": list(range(10)),
            "y": list(range(10))
        },
        constraints=[
            lambda p: p['x'] + p['y'] <= 10,
            lambda p: p['x'] <= p['y']
        ]
    )
    result = enumerator.enumerate(space)
    print(f"  Generated: {result.items_generated}")
    print(f"  Accepted: {result.items_accepted}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(enumerator.get_statistics(), indent=2))
