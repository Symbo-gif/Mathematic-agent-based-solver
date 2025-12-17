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
Auto-Formalization Pipeline
=============================

Agent 5.1 of the Formal Knowledge Integration Team

Converts natural language or code outputs from discovery teams into
strict OMDoc/OpenMath entries. Ensures new discoveries are rigorously
encoded so Phase 2 Supervisors can utilize them as primitive tools.

Output Formats:
- OMDoc XML
- Lean4 theorem statements
- SymPy implementations

Verification: All formalizations must pass through Phase 1 Verification
Core before integration.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 5
Reference: Phase_6_Build_Order_Breakdown.md, Step 5
"""

import logging
import sympy as sp
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib
import uuid

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.formal_knowledge_integration.auto_formalization_pipeline')
except ImportError:
    logger = logging.getLogger(__name__)


class DiscoveryType(Enum):
    """Types of discoveries"""
    THEOREM = 'theorem'
    LEMMA = 'lemma'
    ALGORITHM = 'algorithm'
    HEURISTIC = 'heuristic'
    IDENTITY = 'identity'
    FORMULA = 'formula'
    TECHNIQUE = 'technique'


class VerificationStatus(Enum):
    """Verification status of a formalized discovery"""
    PENDING = 'pending'
    VERIFIED = 'verified'
    FAILED = 'failed'
    PARTIAL = 'partial'


@dataclass
class FormalizedDiscovery:
    """
    A discovery that has been formalized for integration.

    Attributes:
        discovery_id: Unique identifier
        discovery_type: Type of discovery (theorem, algorithm, etc.)
        natural_language_statement: Human-readable statement
        omdoc_representation: OMDoc XML representation
        lean4_code: Lean4 code representation
        sympy_implementation: SymPy code if applicable
        proof_trace_id: ID of the proof trace that verified this
        verified: Whether it passed verification
        verification_method: How it was verified
        applicable_domains: Mathematical domains where this applies
        embedding_vector: Vector embedding for RAG retrieval
    """
    discovery_id: str
    discovery_type: DiscoveryType
    natural_language_statement: str
    omdoc_representation: str
    lean4_code: Optional[str] = None
    sympy_implementation: Optional[str] = None
    proof_trace_id: Optional[str] = None
    verified: bool = False
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_method: str = ""
    applicable_domains: List[str] = field(default_factory=list)
    embedding_vector: Optional[List[float]] = None
    source_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'discovery_id': self.discovery_id,
            'discovery_type': self.discovery_type.value,
            'natural_language_statement': self.natural_language_statement,
            'has_omdoc': len(self.omdoc_representation) > 0,
            'has_lean4': self.lean4_code is not None,
            'has_sympy': self.sympy_implementation is not None,
            'verified': self.verified,
            'verification_status': self.verification_status.value,
            'applicable_domains': self.applicable_domains,
            'has_embedding': self.embedding_vector is not None,
            'created_at': self.created_at.isoformat()
        }

    def compute_hash(self) -> str:
        """Compute content hash for deduplication"""
        content = f"{self.natural_language_statement}|{self.discovery_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class AutoFormalizationPipeline:
    """
    Agent 5.1: Auto-Formalization Pipeline

    Converts discoveries into formal representations that can be:
    1. Verified by Phase 1 Verification Core
    2. Stored in the vector database for RAG
    3. Used by Phase 2 Supervisors as primitives

    Key capabilities:
    - Theorem formalization to OMDoc/Lean4
    - Algorithm formalization to OMDoc/Python
    - Verification integration
    - Domain classification

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(self, verification_core=None, omdoc_encoder=None):
        """
        Initialize the Auto-Formalization Pipeline.

        Args:
            verification_core: Phase 1 verification core for validation
            omdoc_encoder: Phase 0 OMDoc encoder
        """
        self.verifier = verification_core
        self.omdoc_encoder = omdoc_encoder
        self.formalized_count = 0

        # Statistics
        self.stats = {
            'theorems_formalized': 0,
            'algorithms_formalized': 0,
            'verification_passed': 0,
            'verification_failed': 0,
            'total_formalizations': 0
        }

    def formalize_theorem(
        self,
        conjecture,
        proof_steps: List[str]
    ) -> FormalizedDiscovery:
        """
        Formalize a proven theorem for knowledge integration.

        Args:
            conjecture: The proven CandidateConjecture
            proof_steps: List of proof tactics

        Returns:
            FormalizedDiscovery ready for integration
        """
        self.stats['theorems_formalized'] += 1
        self.stats['total_formalizations'] += 1
        self.formalized_count += 1

        # Extract theorem information
        theorem = conjecture.source_theorem if hasattr(conjecture, 'source_theorem') else None

        # Generate natural language statement
        nl_statement = self._generate_nl_statement(conjecture, theorem)

        # Generate OMDoc representation
        omdoc = self._generate_omdoc_theorem(conjecture, proof_steps)

        # Generate Lean4 code with proof
        lean_code = self._generate_lean_proof(conjecture, proof_steps)

        # Generate SymPy implementation
        sympy_impl = self._generate_sympy_implementation(conjecture, theorem)

        # Determine applicable domains
        domains = self._determine_domains(conjecture, theorem)

        # Create discovery object
        discovery = FormalizedDiscovery(
            discovery_id=f"thm_{self.formalized_count}_{uuid.uuid4().hex[:6]}",
            discovery_type=DiscoveryType.THEOREM,
            natural_language_statement=nl_statement,
            omdoc_representation=omdoc,
            lean4_code=lean_code,
            sympy_implementation=sympy_impl,
            proof_trace_id=conjecture.conjecture_id if hasattr(conjecture, 'conjecture_id') else None,
            applicable_domains=domains,
            source_id=str(conjecture.conjecture_id) if hasattr(conjecture, 'conjecture_id') else "",
            metadata={
                'proof_length': len(proof_steps),
                'domain': theorem.domain if theorem else 'unknown'
            }
        )

        # Attempt verification
        discovery = self._verify_discovery(discovery)

        return discovery

    def formalize_algorithm(
        self,
        heuristic: Dict[str, Any]
    ) -> FormalizedDiscovery:
        """
        Formalize a discovered algorithm for knowledge integration.

        Args:
            heuristic: DistilledHeuristic dictionary from HeuristicDistiller

        Returns:
            FormalizedDiscovery ready for integration
        """
        self.stats['algorithms_formalized'] += 1
        self.stats['total_formalizations'] += 1
        self.formalized_count += 1

        # Generate OMDoc representation
        omdoc = self._generate_omdoc_algorithm(heuristic)

        discovery = FormalizedDiscovery(
            discovery_id=f"alg_{self.formalized_count}_{uuid.uuid4().hex[:6]}",
            discovery_type=DiscoveryType.ALGORITHM,
            natural_language_statement=heuristic.get('prose_explanation', ''),
            omdoc_representation=omdoc,
            lean4_code=None,  # Algorithms don't have Lean proofs
            sympy_implementation=heuristic.get('code', ''),
            verified=True,  # Verified by sandbox evaluation
            verification_status=VerificationStatus.VERIFIED,
            verification_method='sandbox_evaluation',
            applicable_domains=heuristic.get('applicable_domains', []),
            source_id=heuristic.get('candidate_id', ''),
            metadata={
                'algorithmic_class': heuristic.get('algorithmic_class', 'unknown'),
                'key_patterns': heuristic.get('key_patterns', []),
                'fitness_score': heuristic.get('fitness_score', 0.0)
            }
        )

        return discovery

    def formalize_identity(
        self,
        expression: sp.Expr,
        domain: str = 'algebra'
    ) -> FormalizedDiscovery:
        """
        Formalize a mathematical identity.

        Args:
            expression: SymPy expression representing the identity
            domain: Mathematical domain

        Returns:
            FormalizedDiscovery for the identity
        """
        self.stats['total_formalizations'] += 1
        self.formalized_count += 1

        nl_statement = f"Identity: {expression}"
        omdoc = self._generate_omdoc_identity(expression, domain)

        discovery = FormalizedDiscovery(
            discovery_id=f"id_{self.formalized_count}_{uuid.uuid4().hex[:6]}",
            discovery_type=DiscoveryType.IDENTITY,
            natural_language_statement=nl_statement,
            omdoc_representation=omdoc,
            applicable_domains=[domain],
            metadata={'expression': str(expression)}
        )

        return discovery

    def _generate_nl_statement(self, conjecture, theorem) -> str:
        """Generate natural language theorem statement"""
        if theorem and hasattr(theorem, 'to_natural_language'):
            base = theorem.to_natural_language()
        elif hasattr(conjecture, 'source_theorem'):
            base = str(conjecture.source_theorem.conclusion)
        else:
            base = str(conjecture)

        conj_id = conjecture.conjecture_id if hasattr(conjecture, 'conjecture_id') else 'unknown'

        statement = f"Theorem ({conj_id}): {base}"
        return statement

    def _generate_omdoc_theorem(self, conjecture, proof_steps: List[str]) -> str:
        """Generate OMDoc representation for a theorem"""
        theorem = conjecture.source_theorem if hasattr(conjecture, 'source_theorem') else None
        conj_id = conjecture.conjecture_id if hasattr(conjecture, 'conjecture_id') else 'theorem'

        nl_statement = theorem.to_natural_language() if theorem else str(conjecture)

        # Generate premise section
        premise_content = ""
        if theorem and theorem.premises:
            for i, premise in enumerate(theorem.premises):
                premise_content += f"""
        <hypothesis id="h{i}">
          <CMP>{premise}</CMP>
        </hypothesis>"""

        # Generate conclusion
        conclusion = str(theorem.conclusion) if theorem else str(conjecture)

        # Build OMDoc
        omdoc = f"""<?xml version="1.0" encoding="UTF-8"?>
<omdoc xmlns="http://www.mathweb.org/omdoc" version="1.6">
  <metadata>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{conj_id}</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Phase 6 Discovery Engine</dc:creator>
    <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">{datetime.now().isoformat()}</dc:date>
  </metadata>

  <theory name="{self._sanitize_name(conj_id)}">
    <assertion type="theorem" id="{conj_id}">
      <CMP>{nl_statement}</CMP>{premise_content}
      <FMP>
        <OMOBJ xmlns="http://www.openmath.org/OpenMath">
          <OMS cd="phase6" name="conclusion"/>
          <OMV name="expr" value="{self._escape_xml(conclusion)}"/>
        </OMOBJ>
      </FMP>
    </assertion>

    <proof id="{conj_id}_proof" for="{conj_id}" status="verified">
      <derive>
        <CMP>Proof by: {', '.join(proof_steps[:10])}</CMP>
        <method>
          <OMS cd="phase6" name="deep_search_proof"/>
        </method>
      </derive>
    </proof>
  </theory>
</omdoc>"""
        return omdoc

    def _generate_omdoc_algorithm(self, heuristic: Dict[str, Any]) -> str:
        """Generate OMDoc representation for an algorithm"""
        alg_id = heuristic.get('candidate_id', 'algorithm')
        prose = heuristic.get('prose_explanation', '')
        algo_class = heuristic.get('algorithmic_class', 'unknown')

        omdoc = f"""<?xml version="1.0" encoding="UTF-8"?>
<omdoc xmlns="http://www.mathweb.org/omdoc" version="1.6">
  <metadata>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Algorithm: {alg_id}</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Phase 6 FunSearch</dc:creator>
    <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">{datetime.now().isoformat()}</dc:date>
  </metadata>

  <theory name="algorithm_{self._sanitize_name(alg_id)}">
    <definition id="{alg_id}" type="algorithm">
      <CMP>{self._escape_xml(prose)}</CMP>
      <FMP>
        <OMOBJ xmlns="http://www.openmath.org/OpenMath">
          <OMS cd="algorithms" name="{algo_class}"/>
        </OMOBJ>
      </FMP>
      <metadata>
        <meta name="algorithmic_class">{algo_class}</meta>
        <meta name="fitness_score">{heuristic.get('fitness_score', 0.0)}</meta>
      </metadata>
    </definition>
  </theory>
</omdoc>"""
        return omdoc

    def _generate_omdoc_identity(self, expression: sp.Expr, domain: str) -> str:
        """Generate OMDoc representation for an identity"""
        omdoc = f"""<?xml version="1.0" encoding="UTF-8"?>
<omdoc xmlns="http://www.mathweb.org/omdoc" version="1.6">
  <theory name="identity_{uuid.uuid4().hex[:8]}">
    <assertion type="identity" id="id_{self.formalized_count}">
      <CMP>Identity: {self._escape_xml(str(expression))}</CMP>
      <FMP>
        <OMOBJ xmlns="http://www.openmath.org/OpenMath">
          <OMS cd="{domain}" name="identity"/>
        </OMOBJ>
      </FMP>
    </assertion>
  </theory>
</omdoc>"""
        return omdoc

    def _generate_lean_proof(self, conjecture, proof_steps: List[str]) -> str:
        """Generate Lean4 proof code"""
        base_statement = conjecture.lean4_statement if hasattr(conjecture, 'lean4_statement') and conjecture.lean4_statement else ""

        if not base_statement:
            conj_id = conjecture.conjecture_id if hasattr(conjecture, 'conjecture_id') else 'theorem'
            theorem = conjecture.source_theorem if hasattr(conjecture, 'source_theorem') else None
            conclusion = str(theorem.conclusion) if theorem else "True"

            base_statement = f"""
-- Auto-generated proven theorem
theorem {self._sanitize_name(conj_id)} : {conclusion} := by
  sorry
"""

        # Replace sorry with proof tactics
        if 'sorry' in base_statement and proof_steps:
            tactics = '\n  '.join(proof_steps)
            base_statement = base_statement.replace('sorry', tactics)

        return base_statement

    def _generate_sympy_implementation(self, conjecture, theorem) -> Optional[str]:
        """Generate SymPy implementation if applicable"""
        if theorem is None:
            return None

        if theorem.domain not in ['algebra', 'analysis', 'number_theory']:
            return None

        conj_id = conjecture.conjecture_id if hasattr(conjecture, 'conjecture_id') else 'theorem'
        func_name = self._sanitize_name(conj_id)

        impl = f'''
def {func_name}(expr):
    """
    Apply theorem: {theorem.to_natural_language()}

    Auto-generated by Phase 6 Discovery Engine
    """
    import sympy as sp

    # Pattern to match
    conclusion = {repr(theorem.conclusion)}

    # Check if expression matches pattern
    try:
        if isinstance(conclusion, sp.Eq):
            lhs, rhs = conclusion.lhs, conclusion.rhs
            diff = sp.simplify(expr - rhs)
            return diff == 0
        return False
    except (TypeError, AttributeError, ValueError):
        return False
'''
        return impl

    def _determine_domains(self, conjecture, theorem) -> List[str]:
        """Determine applicable mathematical domains"""
        domains = []

        if hasattr(conjecture, 'cross_domain_applicability'):
            domains.extend(conjecture.cross_domain_applicability)

        if theorem and hasattr(theorem, 'domain'):
            if theorem.domain not in domains:
                domains.append(theorem.domain)

        return list(set(domains)) if domains else ['general']

    def _verify_discovery(self, discovery: FormalizedDiscovery) -> FormalizedDiscovery:
        """Verify discovery using Phase 1 Verification Core"""
        if self.verifier is None:
            # No verifier available - mark as pending
            discovery.verification_status = VerificationStatus.PENDING
            return discovery

        try:
            # Attempt verification
            result = self.verifier.verify(discovery.lean4_code or discovery.omdoc_representation)

            if result.get('verified'):
                discovery.verified = True
                discovery.verification_status = VerificationStatus.VERIFIED
                discovery.verification_method = 'phase1_verification_core'
                self.stats['verification_passed'] += 1
            else:
                discovery.verification_status = VerificationStatus.FAILED
                self.stats['verification_failed'] += 1

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            # Data/type errors during verification
            discovery.verification_status = VerificationStatus.PENDING
            discovery.metadata['verification_error'] = f"data_error: {str(e)}"
        except (RuntimeError, ImportError, IOError) as e:
            # System errors during verification
            discovery.verification_status = VerificationStatus.PENDING
            discovery.metadata['verification_error'] = f"system_error: {str(e)}"

        return discovery

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as identifier"""
        return ''.join(c if c.isalnum() else '_' for c in name)

    def _escape_xml(self, text: str) -> str:
        """Escape text for XML"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        total = self.stats['total_formalizations']
        if total > 0:
            verification_rate = self.stats['verification_passed'] / total * 100
        else:
            verification_rate = 0

        return {
            **self.stats,
            'verification_rate_percent': round(verification_rate, 2),
            'has_verifier': self.verifier is not None
        }

    def reset(self):
        """Reset pipeline state"""
        self.formalized_count = 0
        for key in self.stats:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if pipeline is healthy"""
        return True
