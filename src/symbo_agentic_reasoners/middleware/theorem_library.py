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
PHASE 3 - KM-3: THEOREM LIBRARY MANAGER (Tier 3)
===============================================

Manages a library of mathematical theorems, providing lookup,
applicability checking, and proof sketch generation.

CAPABILITIES:
------------
- Theorem lookup by domain and keywords
- Applicability analysis for given problems
- Proof sketch generation
- Theorem dependency tracking
- Formal proof request handling

ALGORITHMIC BACKING:
-------------------
- Theorem database with domain classification
- Pattern matching for applicability
- Dependency graph for theorem relationships

REFERENCE:
---------
- Agent_System_Audit.docx.md: KM-3 Theorem Library Manager
- Phase_3_Meta_Cognition.md: Knowledge Management Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase3.theorem_library')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class MathDomain(Enum):
    """Mathematical domains for theorem classification"""
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    LINEAR_ALGEBRA = "linear_algebra"
    NUMBER_THEORY = "number_theory"
    TOPOLOGY = "topology"
    ANALYSIS = "analysis"
    COMBINATORICS = "combinatorics"
    GEOMETRY = "geometry"
    LOGIC = "logic"
    SET_THEORY = "set_theory"
    GENERAL = "general"


class ProofTechnique(Enum):
    """Common proof techniques"""
    DIRECT = "direct"
    CONTRADICTION = "contradiction"
    INDUCTION = "induction"
    CONTRAPOSITIVE = "contrapositive"
    CONSTRUCTION = "construction"
    EXHAUSTION = "exhaustion"
    PIGEONHOLE = "pigeonhole"
    DIAGONAL = "diagonal"


@dataclass
class Theorem:
    """
    Represents a mathematical theorem.
    
    Attributes:
        theorem_id: Unique identifier
        name: Theorem name
        statement: Formal statement
        domain: Mathematical domain
        hypotheses: Required conditions
        conclusion: What the theorem proves
        proof_technique: Common proof method
        dependencies: Theorems this depends on
        applications: Common applications
        difficulty: Difficulty level (1-10)
    """
    theorem_id: str
    name: str
    statement: str
    domain: MathDomain
    hypotheses: List[str]
    conclusion: str
    proof_technique: ProofTechnique = ProofTechnique.DIRECT
    dependencies: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    difficulty: int = 5
    keywords: Set[str] = field(default_factory=set)
    
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
            'theorem_id': self.theorem_id,
            'name': self.name,
            'domain': self.domain.value,
            'statement': self.statement[:200] + '...' if len(self.statement) > 200 else self.statement,
            'technique': self.proof_technique.value,
            'difficulty': self.difficulty,
            'dependency_count': len(self.dependencies)
        }


@dataclass
class ProofSketch:
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    """A sketch of a proof for a theorem"""
    theorem_id: str
    steps: List[str]
    technique: ProofTechnique
    key_lemmas: List[str]
    estimated_difficulty: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        >>> result = obj.to_dict(...)
        """
        return {
            'theorem_id': self.theorem_id,
            'step_count': len(self.steps),
            'technique': self.technique.value,
            'difficulty': self.estimated_difficulty
        }


@dataclass
class ApplicabilityResult:
    """Result of checking theorem applicability"""
    theorem: Theorem
    is_applicable: bool
    satisfaction_level: float  # 0-1
    missing_hypotheses: List[str]
    matching_conditions: List[str]
    
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
            'theorem_id': self.theorem.theorem_id,
            'name': self.theorem.name,
            'is_applicable': self.is_applicable,
            'satisfaction': self.satisfaction_level,
            'missing': self.missing_hypotheses
        }


class TheoremLibraryManager(BDIAgent):
    """
    KM-3: Theorem Library Manager
    
    DIRECTIVE:
    ---------
    Manage mathematical theorem library, providing lookup and
    proof sketch generation capabilities.
    
    INPUTS:
    ------
    - Theorem queries
    - Formal proof requests
    - Applicability checks
    
    OUTPUTS:
    -------
    - Applicable theorems
    - Proof sketch generation
    - Theorem dependencies
    
    DEPENDENCIES:
    ------------
    - KM-1 (ContextExtractorAgent): For context access
    - KM-2 (PatternIndexer): For pattern matching
    - VC-1 (LogicCheckerAgent): For proof verification
    
    FAILURE MODE: DEGRADED - Reduced theorem coverage
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 415-424
    """
    
    def __init__(
        self,
        agent_id: str = 'theorem_library_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Theorem Library Manager
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Theorem storage
        self.theorems: Dict[str, Theorem] = {}
        
        # Dependency graph (theorem_id -> list of dependent theorem_ids)
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # Domain index (domain -> list of theorem_ids)
        self.domain_index: Dict[MathDomain, List[str]] = {d: [] for d in MathDomain}
        
        # Keyword index
        self.keyword_index: Dict[str, List[str]] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.lookups_performed = 0
        self.proofs_sketched = 0
        
        # Initialize with foundational theorems
        self._initialize_theorem_library()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Theorem Library Manager initialized")
        print(f"  Theorems loaded: {len(self.theorems)}")
        print(f"  Domains covered: {len([d for d in self.domain_index if self.domain_index[d]])}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='meta.knowledge.theorem',
            agent_id=self.agent_id,
            algorithm='theorem_lookup',
            cost='medium',
            type='exact',
            tier='3',
            algorithms='lookup_applicability_proof_sketch'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: meta.knowledge.theorem")
    
    def _initialize_theorem_library(self):
        """Initialize with foundational theorems"""
        foundational_theorems = [
            # Algebra
            Theorem(
                theorem_id="fundamental_algebra",
                name="Fundamental Theorem of Algebra",
                statement="Every non-constant polynomial with complex coefficients has at least one complex root",
                domain=MathDomain.ALGEBRA,
                hypotheses=["P(x) is a polynomial", "deg(P) >= 1", "coefficients in C"],
                conclusion="exists z in C: P(z) = 0",
                dependencies=[],
                applications=["polynomial factorization", "root finding"],
                difficulty=7,
                keywords={"polynomial", "root", "complex", "fundamental"}
            ),
            Theorem(
                theorem_id="quadratic_formula",
                name="Quadratic Formula",
                statement="For ax^2 + bx + c = 0 with a ≠ 0, x = (-b ± √(b²-4ac)) / 2a",
                domain=MathDomain.ALGEBRA,
                hypotheses=["a ≠ 0", "quadratic equation"],
                conclusion="explicit solution formula",
                proof_technique=ProofTechnique.DIRECT,
                dependencies=[],
                applications=["solving quadratics"],
                difficulty=3,
                keywords={"quadratic", "formula", "roots", "polynomial"}
            ),
            
            # Calculus
            Theorem(
                theorem_id="fundamental_calculus",
                name="Fundamental Theorem of Calculus",
                statement="∫[a,b] f(x)dx = F(b) - F(a) where F' = f",
                domain=MathDomain.CALCULUS,
                hypotheses=["f continuous on [a,b]", "F is antiderivative of f"],
                conclusion="definite integral equals antiderivative difference",
                dependencies=[],
                applications=["definite integrals", "area computation"],
                difficulty=5,
                keywords={"integral", "derivative", "antiderivative", "fundamental"}
            ),
            Theorem(
                theorem_id="mean_value_theorem",
                name="Mean Value Theorem",
                statement="If f continuous on [a,b] and differentiable on (a,b), exists c: f'(c) = (f(b)-f(a))/(b-a)",
                domain=MathDomain.CALCULUS,
                hypotheses=["f continuous on [a,b]", "f differentiable on (a,b)"],
                conclusion="exists c in (a,b) with tangent parallel to secant",
                proof_technique=ProofTechnique.CONSTRUCTION,
                dependencies=["rolle_theorem"],
                applications=["rate of change", "optimization"],
                difficulty=5,
                keywords={"derivative", "continuous", "mean", "value"}
            ),
            Theorem(
                theorem_id="rolle_theorem",
                name="Rolle's Theorem",
                statement="If f continuous on [a,b], differentiable on (a,b), f(a)=f(b), then exists c: f'(c)=0",
                domain=MathDomain.CALCULUS,
                hypotheses=["f continuous on [a,b]", "f differentiable on (a,b)", "f(a) = f(b)"],
                conclusion="exists c in (a,b): f'(c) = 0",
                proof_technique=ProofTechnique.CONTRADICTION,
                dependencies=[],
                applications=["root existence", "critical points"],
                difficulty=4,
                keywords={"derivative", "zero", "rolle", "continuous"}
            ),
            Theorem(
                theorem_id="chain_rule",
                name="Chain Rule",
                statement="d/dx[f(g(x))] = f'(g(x)) · g'(x)",
                domain=MathDomain.CALCULUS,
                hypotheses=["f differentiable at g(x)", "g differentiable at x"],
                conclusion="derivative of composition",
                proof_technique=ProofTechnique.DIRECT,
                dependencies=[],
                applications=["composite functions", "implicit differentiation"],
                difficulty=3,
                keywords={"derivative", "composition", "chain"}
            ),
            Theorem(
                theorem_id="lhopital_rule",
                name="L'Hôpital's Rule",
                statement="lim f(x)/g(x) = lim f'(x)/g'(x) for 0/0 or ∞/∞ forms",
                domain=MathDomain.CALCULUS,
                hypotheses=["lim f(x) = lim g(x) = 0 or ±∞", "f, g differentiable", "g'(x) ≠ 0 near limit"],
                conclusion="limit of ratio equals limit of derivative ratio",
                dependencies=["mean_value_theorem"],
                applications=["indeterminate forms", "limits"],
                difficulty=5,
                keywords={"limit", "derivative", "indeterminate", "lhopital"}
            ),
            
            # Linear Algebra
            Theorem(
                theorem_id="spectral_theorem",
                name="Spectral Theorem",
                statement="Every symmetric matrix is diagonalizable with orthonormal eigenvectors",
                domain=MathDomain.LINEAR_ALGEBRA,
                hypotheses=["A is symmetric (A = A^T)", "A is real matrix"],
                conclusion="A = QDQ^T where Q orthogonal, D diagonal",
                proof_technique=ProofTechnique.INDUCTION,
                dependencies=[],
                applications=["eigendecomposition", "PCA", "quadratic forms"],
                difficulty=7,
                keywords={"symmetric", "eigenvalue", "orthogonal", "diagonal"}
            ),
            Theorem(
                theorem_id="rank_nullity",
                name="Rank-Nullity Theorem",
                statement="dim(ker(A)) + dim(im(A)) = n for A: R^n → R^m",
                domain=MathDomain.LINEAR_ALGEBRA,
                hypotheses=["A is linear transformation", "finite dimensional spaces"],
                conclusion="nullity + rank = dimension of domain",
                proof_technique=ProofTechnique.DIRECT,
                dependencies=[],
                applications=["solution existence", "system analysis"],
                difficulty=5,
                keywords={"rank", "nullity", "dimension", "kernel", "image"}
            ),
            
            # Number Theory
            Theorem(
                theorem_id="euclid_primes",
                name="Euclid's Theorem on Primes",
                statement="There are infinitely many prime numbers",
                domain=MathDomain.NUMBER_THEORY,
                hypotheses=[],
                conclusion="prime numbers are infinite",
                proof_technique=ProofTechnique.CONTRADICTION,
                dependencies=[],
                applications=["prime distribution"],
                difficulty=4,
                keywords={"prime", "infinite", "euclid"}
            ),
            Theorem(
                theorem_id="fundamental_arithmetic",
                name="Fundamental Theorem of Arithmetic",
                statement="Every integer > 1 has unique prime factorization",
                domain=MathDomain.NUMBER_THEORY,
                hypotheses=["n is integer", "n > 1"],
                conclusion="n = p1^a1 · p2^a2 · ... · pk^ak uniquely",
                proof_technique=ProofTechnique.INDUCTION,
                dependencies=[],
                applications=["factorization", "GCD/LCM"],
                difficulty=5,
                keywords={"prime", "factorization", "unique", "fundamental"}
            ),
            
            # Set Theory / Logic
            Theorem(
                theorem_id="cantor_diagonal",
                name="Cantor's Diagonal Argument",
                statement="The real numbers are uncountable",
                domain=MathDomain.SET_THEORY,
                hypotheses=["assume reals are countable"],
                conclusion="reals are uncountable, |R| > |N|",
                proof_technique=ProofTechnique.DIAGONAL,
                dependencies=[],
                applications=["cardinality", "computability"],
                difficulty=6,
                keywords={"uncountable", "diagonal", "cantor", "cardinality"}
            ),
            
            # General
            Theorem(
                theorem_id="pigeonhole",
                name="Pigeonhole Principle",
                statement="If n+1 objects go into n boxes, at least one box has ≥ 2 objects",
                domain=MathDomain.COMBINATORICS,
                hypotheses=["n boxes", "n+1 objects"],
                conclusion="some box contains at least 2 objects",
                proof_technique=ProofTechnique.PIGEONHOLE,
                dependencies=[],
                applications=["existence proofs", "combinatorics"],
                difficulty=2,
                keywords={"pigeonhole", "existence", "count"}
            ),
            Theorem(
                theorem_id="well_ordering",
                name="Well-Ordering Principle",
                statement="Every non-empty subset of natural numbers has a least element",
                domain=MathDomain.SET_THEORY,
                hypotheses=["S ⊆ N", "S ≠ ∅"],
                conclusion="exists min(S)",
                proof_technique=ProofTechnique.DIRECT,
                dependencies=[],
                applications=["induction", "minimal counterexample"],
                difficulty=4,
                keywords={"minimum", "natural", "well-ordering"}
            ),
        ]
        
        for thm in foundational_theorems:
            self.add_theorem(thm)
    
    def add_theorem(self, theorem: Theorem) -> str:
        """
        Add a theorem to the library.
        
        Args:
            theorem: The theorem to add
            
        Returns:
            Theorem ID
        """
        self.theorems[theorem.theorem_id] = theorem
        
        # Update domain index
        self.domain_index[theorem.domain].append(theorem.theorem_id)
        
        # Update dependency graph
        self.dependency_graph[theorem.theorem_id] = theorem.dependencies
        
        # Update keyword index
        for keyword in theorem.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            self.keyword_index[keyword].append(theorem.theorem_id)
        
        return theorem.theorem_id
    
    def lookup_theorems(
        self,
        query: Optional[str] = None,
        domain: Optional[MathDomain] = None,
        keywords: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Theorem]:
        """
        Look up theorems by various criteria.
        
        Args:
            query: Free-text query
            domain: Filter by domain
            keywords: Filter by keywords
            max_results: Maximum results to return
            
        Returns:
            List of matching theorems
        """
        self.tasks_executed += 1
        self.lookups_performed += 1
        
        try:
            candidates = set(self.theorems.keys())
            
            # Filter by domain
            if domain:
                domain_theorems = set(self.domain_index.get(domain, []))
                candidates &= domain_theorems
            
            # Filter by keywords
            if keywords:
                keyword_theorems = set()
                for kw in keywords:
                    kw_lower = kw.lower()
                    if kw_lower in self.keyword_index:
                        keyword_theorems.update(self.keyword_index[kw_lower])
                if keyword_theorems:
                    candidates &= keyword_theorems
            
            # Filter by query (simple text matching)
            if query:
                query_lower = query.lower()
                query_matches = set()
                for tid in candidates:
                    thm = self.theorems[tid]
                    if (query_lower in thm.name.lower() or 
                        query_lower in thm.statement.lower() or
                        any(query_lower in h.lower() for h in thm.hypotheses)):
                        query_matches.add(tid)
                candidates &= query_matches if query_matches else candidates
            
            result = [self.theorems[tid] for tid in list(candidates)[:max_results]]
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Theorem lookup failed: {type(e).__name__}: {e}")
            return []
    
    def check_applicability(
        self,
        theorem_id: str,
        given_conditions: List[str]
    ) -> ApplicabilityResult:
        """
        Check if a theorem is applicable given conditions.
        
        Args:
            theorem_id: ID of theorem to check
            given_conditions: List of known conditions
            
        Returns:
            ApplicabilityResult with analysis
        """
        self.tasks_executed += 1
        
        try:
            theorem = self.theorems.get(theorem_id)
            if not theorem:
                raise ValueError(f"Unknown theorem: {theorem_id}")
            
            given_lower = [c.lower() for c in given_conditions]
            
            matching = []
            missing = []
            
            for hyp in theorem.hypotheses:
                hyp_lower = hyp.lower()
                # Check if hypothesis is satisfied (simple substring matching)
                is_satisfied = any(
                    hyp_lower in g or g in hyp_lower 
                    for g in given_lower
                )
                if is_satisfied:
                    matching.append(hyp)
                else:
                    missing.append(hyp)
            
            satisfaction = len(matching) / len(theorem.hypotheses) if theorem.hypotheses else 1.0
            is_applicable = satisfaction >= 0.5  # At least 50% satisfied
            
            self.tasks_succeeded += 1
            
            return ApplicabilityResult(
                theorem=theorem,
                is_applicable=is_applicable,
                satisfaction_level=satisfaction,
                missing_hypotheses=missing,
                matching_conditions=matching
            )
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Applicability check failed: {type(e).__name__}: {e}")
            raise
    
    def generate_proof_sketch(
        self,
        theorem_id: str
    ) -> ProofSketch:
        """
        Generate a proof sketch for a theorem.
        
        Args:
            theorem_id: ID of theorem to sketch
            
        Returns:
            ProofSketch with steps
        """
        self.tasks_executed += 1
        self.proofs_sketched += 1
        
        try:
            theorem = self.theorems.get(theorem_id)
            if not theorem:
                raise ValueError(f"Unknown theorem: {theorem_id}")
            
            steps = []
            
            # Generate steps based on proof technique
            if theorem.proof_technique == ProofTechnique.DIRECT:
                steps = [
                    f"1. Assume the hypotheses: {', '.join(theorem.hypotheses[:3])}",
                    "2. Apply definitions and known results",
                    f"3. Derive intermediate results using algebraic/logical manipulation",
                    f"4. Conclude: {theorem.conclusion}"
                ]
            elif theorem.proof_technique == ProofTechnique.CONTRADICTION:
                steps = [
                    f"1. Assume the hypotheses: {', '.join(theorem.hypotheses[:3])}",
                    f"2. Suppose for contradiction that NOT({theorem.conclusion})",
                    "3. Derive consequences of this assumption",
                    "4. Reach a contradiction with hypotheses or known facts",
                    f"5. Conclude: {theorem.conclusion}"
                ]
            elif theorem.proof_technique == ProofTechnique.INDUCTION:
                steps = [
                    "1. Base case: Prove for n = 1 (or n = 0)",
                    "2. Inductive hypothesis: Assume true for n = k",
                    "3. Inductive step: Prove for n = k + 1",
                    f"4. Conclude: {theorem.conclusion} for all n"
                ]
            else:
                steps = [
                    f"1. Assume: {', '.join(theorem.hypotheses[:2])}",
                    f"2. Apply {theorem.proof_technique.value} technique",
                    f"3. Conclude: {theorem.conclusion}"
                ]
            
            # Get dependency theorems
            key_lemmas = []
            for dep_id in theorem.dependencies:
                if dep_id in self.theorems:
                    key_lemmas.append(self.theorems[dep_id].name)
            
            self.tasks_succeeded += 1
            
            return ProofSketch(
                theorem_id=theorem_id,
                steps=steps,
                technique=theorem.proof_technique,
                key_lemmas=key_lemmas,
                estimated_difficulty=theorem.difficulty
            )
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Proof sketch generation failed: {type(e).__name__}: {e}")
            raise
    
    def get_dependencies(self, theorem_id: str) -> List[Theorem]:
        """Get all theorems that a theorem depends on"""
        deps = []
        visited = set()
        
        def collect_deps(tid):
            """Perform collect deps operation.

            Args:
            tid: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.collect_deps(...)
            """
            if tid in visited:
                return
            visited.add(tid)
            for dep_id in self.dependency_graph.get(tid, []):
                if dep_id in self.theorems:
                    deps.append(self.theorems[dep_id])
                    collect_deps(dep_id)
        
        collect_deps(theorem_id)
        return deps
    
    def process(self, task_entry: Any) -> Any:
        """Process theorem library task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing theorem task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'lookup')
            
            if operation == 'lookup':
                query = metadata.get('query')
                domain_str = metadata.get('domain')
                domain = MathDomain(domain_str) if domain_str else None
                keywords = metadata.get('keywords')
                
                theorems = self.lookup_theorems(query, domain, keywords)
                result = {
                    'theorems': [t.to_dict() for t in theorems],
                    'count': len(theorems)
                }
                
            elif operation == 'applicability':
                theorem_id = metadata.get('theorem_id')
                conditions = metadata.get('conditions', [])
                app_result = self.check_applicability(theorem_id, conditions)
                result = app_result.to_dict()
                
            elif operation == 'proof_sketch':
                theorem_id = metadata.get('theorem_id')
                sketch = self.generate_proof_sketch(theorem_id)
                result = sketch.to_dict()
                result['steps'] = sketch.steps
                
            elif operation == 'dependencies':
                theorem_id = metadata.get('theorem_id')
                deps = self.get_dependencies(theorem_id)
                result = {
                    'dependencies': [d.to_dict() for d in deps],
                    'count': len(deps)
                }
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Theorem task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['theorem', 'knowledge'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'theorem'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for theorem tasks"""
        pass
    
    def deliberate(self):
        """Generate lookup plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute lookup step"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'theorems_stored': len(self.theorems),
            'domains_covered': len([d for d in self.domain_index if self.domain_index[d]]),
            'lookups_performed': self.lookups_performed,
            'proofs_sketched': self.proofs_sketched
        })
        return stats


if __name__ == "__main__":
    """Test Theorem Library Manager"""
    print("=" * 80)
    print("PHASE 3 - THEOREM LIBRARY MANAGER TEST")
    print("=" * 80)
    print()
    
    # Initialize manager
    manager = TheoremLibraryManager()
    print()
    
    # Test 1: Lookup by domain
    print("Test 1: Lookup Calculus Theorems")
    theorems = manager.lookup_theorems(domain=MathDomain.CALCULUS)
    print(f"  Found: {len(theorems)}")
    for t in theorems[:3]:
        print(f"    - {t.name}")
    print()
    
    # Test 2: Lookup by query
    print("Test 2: Lookup 'derivative' Theorems")
    theorems = manager.lookup_theorems(query="derivative")
    print(f"  Found: {len(theorems)}")
    for t in theorems:
        print(f"    - {t.name}")
    print()
    
    # Test 3: Check applicability
    print("Test 3: Check Mean Value Theorem Applicability")
    result = manager.check_applicability(
        "mean_value_theorem",
        ["f is continuous on [0,1]", "f is differentiable on (0,1)"]
    )
    print(f"  Applicable: {result.is_applicable}")
    print(f"  Satisfaction: {result.satisfaction_level:.0%}")
    print(f"  Missing: {result.missing_hypotheses}")
    print()
    
    # Test 4: Generate proof sketch
    print("Test 4: Generate Proof Sketch for Rolle's Theorem")
    sketch = manager.generate_proof_sketch("rolle_theorem")
    print(f"  Technique: {sketch.technique.value}")
    print(f"  Steps:")
    for step in sketch.steps:
        print(f"    {step}")
    print()
    
    # Test 5: Get dependencies
    print("Test 5: Get L'Hôpital's Rule Dependencies")
    deps = manager.get_dependencies("lhopital_rule")
    print(f"  Dependencies: {len(deps)}")
    for d in deps:
        print(f"    - {d.name}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(manager.get_statistics(), indent=2))
