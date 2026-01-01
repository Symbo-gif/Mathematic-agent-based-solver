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

"""
Conjecture Formalizer
======================

Agent 1.3 of the Conjecture Generation Team

Takes raw relationships from the Filter and translates them into rigorous
Lean4 or Isabelle statements. Prepares candidate conjectures for formal
verification attempts by the Deep Search Team.

Output:
- FormalConjecture objects with Lean4 code
- OMDoc/OpenMath representation
- Verification priority score

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1
Reference: Phase_6_Build_Order_Breakdown.md, Step 1
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt, Abs,
    parse_expr, simplify
)

from .pattern_recognizer import CandidateConjecture, ConjectureStatus
from .synthetic_data_generator import Eq, Gt, Ge, Ne

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.conjecture_generation.conjecture_formalizer')
except ImportError:
    logger = logging.getLogger(__name__)


class ConjectureFormalizer:
    """
    Agent 1.3: Conjecture Formalizer

    Converts candidate conjectures into formal mathematical representations
    suitable for automated theorem proving.

    Key capabilities:
    - Native symbolic to Lean4 translation
    - Native symbolic to OMDoc/OpenMath XML generation
    - Type inference for variable declarations
    - Verification priority scoring

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Lean4 type mappings
    TYPE_MAPPINGS = {
        'real': 'R',
        'integer': 'Z',
        'natural': 'N',
        'complex': 'C',
        'positive': 'R>0',
        'nonnegative': 'R>=0',
        'boolean': 'Bool'
    }

    # Native symbolic to Lean4 operator mappings
    OPERATOR_MAPPINGS = {
        Add: '+',
        Mul: '*',
        Pow: '^',
        Sin: 'Real.sin',
        Cos: 'Real.cos',
        Exp: 'Real.exp',
        Log: 'Real.log',
        Sqrt: 'Real.sqrt',
        Abs: 'abs'
    }

    def __init__(self, omdoc_encoder=None, lean_translator=None):
        """
        Initialize the Conjecture Formalizer.

        Args:
            omdoc_encoder: Optional OMDoc encoder from Phase 0
            lean_translator: Optional Lean4 translator
        """
        self.omdoc_encoder = omdoc_encoder
        self.lean_translator = lean_translator

        # Statistics
        self.stats = {
            'formalized': 0,
            'lean4_generated': 0,
            'omdoc_generated': 0,
            'formalization_errors': 0
        }

    def formalize(self, candidate: CandidateConjecture) -> CandidateConjecture:
        """
        Formalize a candidate conjecture into Lean4 and OMDoc representations.

        Args:
            candidate: The candidate conjecture to formalize

        Returns:
            Updated CandidateConjecture with formal representations
        """
        try:
            # Generate Lean4 statement
            candidate.lean4_statement = self._to_lean4(candidate)
            self.stats['lean4_generated'] += 1

            # Generate OMDoc representation
            candidate.omdoc_representation = self._to_omdoc(candidate)
            self.stats['omdoc_generated'] += 1

            # Store native symbolic form
            candidate.native_form = candidate.source_theorem.conclusion

            # Update status
            candidate.status = ConjectureStatus.FORMALIZED
            self.stats['formalized'] += 1

        except (TypeError, ValueError, AttributeError, KeyError) as e:
            # Data/conversion errors during formalization
            logger.warning(f"Formalization data error: {e}")
            self.stats['formalization_errors'] += 1
            candidate.lean4_statement = f"-- Formalization error (data): {str(e)}"
            candidate.omdoc_representation = f"<!-- Error (data): {str(e)} -->"
            candidate.status = ConjectureStatus.FORMALIZED
        except (RuntimeError, RecursionError) as e:
            # System errors during formalization
            logger.error(f"Formalization system error: {e}", exc_info=True)
            self.stats['formalization_errors'] += 1
            candidate.lean4_statement = f"-- Formalization error (system): {str(e)}"
            candidate.omdoc_representation = f"<!-- Error (system): {str(e)} -->"
            candidate.status = ConjectureStatus.FORMALIZED

        return candidate

    def formalize_batch(self, candidates: List[CandidateConjecture]) -> List[CandidateConjecture]:
        """
        Formalize a batch of candidates.

        Args:
            candidates: List of candidates to formalize

        Returns:
            List of formalized candidates
        """
        return [self.formalize(c) for c in candidates]

    def _to_lean4(self, candidate: CandidateConjecture) -> str:
        """
        Convert conjecture to Lean4 theorem statement.

        Generates a syntactically valid Lean4 theorem with:
        - Variable declarations with inferred types
        - Hypothesis statements from premises
        - Goal statement from conclusion
        """
        theorem = candidate.source_theorem

        # Collect and type all variables
        var_types = self._infer_variable_types(theorem)
        var_decls = self._format_lean_var_declarations(var_types)

        # Build hypotheses
        hypotheses = self._format_lean_hypotheses(theorem.premises)

        # Build conclusion
        conclusion = self._sympy_to_lean(theorem.conclusion)

        # Construct theorem name
        theorem_name = self._sanitize_lean_name(candidate.conjecture_id)

        # Build full theorem
        if hypotheses:
            hyp_str = " ".join(hypotheses)
            lean_code = f"""
-- Auto-generated from synthetic theorem
-- Domain: {theorem.domain}
-- Complexity: {theorem.complexity_score}
theorem {theorem_name} {var_decls} {hyp_str} :
    {conclusion} := by
  sorry -- To be proven by Deep Search Team
"""
        else:
            lean_code = f"""
-- Auto-generated from synthetic theorem
-- Domain: {theorem.domain}
-- Complexity: {theorem.complexity_score}
theorem {theorem_name} {var_decls} :
    {conclusion} := by
  sorry -- To be proven by Deep Search Team
"""
        return lean_code.strip()

    def _infer_variable_types(self, theorem) -> Dict[Symbol, str]:
        """Infer Lean4 types for variables in the theorem"""
        var_types = {}

        # Collect all symbols
        all_symbols = set()
        for expr in theorem.premises + [theorem.conclusion]:
            if hasattr(expr, 'free_symbols'):
                all_symbols.update(expr.free_symbols)

        # Infer types based on domain and symbol properties
        for sym in all_symbols:
            if hasattr(sym, 'assumptions') and sym.assumptions:
                assumptions = sym.assumptions
                if assumptions.get('integer'):
                    var_types[sym] = 'Z'
                elif assumptions.get('positive'):
                    var_types[sym] = 'R'
                elif assumptions.get('real'):
                    var_types[sym] = 'R'
                else:
                    var_types[sym] = 'R'  # Default to real
            else:
                # Infer from domain
                domain_types = {
                    'number_theory': 'Z',
                    'combinatorics': 'N',
                    'geometry': 'R',
                    'algebra': 'R',
                    'analysis': 'R',
                    'linear_algebra': 'R'
                }
                var_types[sym] = domain_types.get(theorem.domain, 'R')

        return var_types

    def _format_lean_var_declarations(self, var_types: Dict[Symbol, str]) -> str:
        """Format variable declarations for Lean4"""
        if not var_types:
            return ""

        # Group by type
        type_groups: Dict[str, List[str]] = {}
        for sym, typ in var_types.items():
            if typ not in type_groups:
                type_groups[typ] = []
            type_groups[typ].append(str(sym))

        # Format declarations
        decls = []
        for typ, vars in type_groups.items():
            var_list = " ".join(sorted(vars))
            decls.append(f"({var_list} : {typ})")

        return " ".join(decls)

    def _format_lean_hypotheses(self, premises: List[Expr]) -> List[str]:
        """Format hypotheses for Lean4"""
        hypotheses = []
        for i, premise in enumerate(premises):
            try:
                hyp = self._sympy_to_lean(premise)
                hypotheses.append(f"(h{i} : {hyp})")
            except (TypeError, AttributeError, ValueError) as e:
                # Skip problematic hypotheses
                logger.debug(f"Could not convert hypothesis {i}: {e}")
                continue
        return hypotheses

    def _expr_to_lean(self, expr: Expr) -> str:
        """Convert native symbolic expression to Lean4 syntax"""
        if expr is None:
            return "True"

        # Handle equality
        if isinstance(expr, Eq):
            lhs = self._expr_to_lean(expr.lhs)
            rhs = self._expr_to_lean(expr.rhs)
            return f"{lhs} = {rhs}"

        # Handle inequalities
        if isinstance(expr, Gt):
            lhs = self._expr_to_lean(expr.lhs)
            rhs = self._expr_to_lean(expr.rhs)
            return f"{lhs} > {rhs}"

        if isinstance(expr, Ge):
            lhs = self._expr_to_lean(expr.lhs)
            rhs = self._expr_to_lean(expr.rhs)
            return f"{lhs} >= {rhs}"

        if isinstance(expr, Ne):
            lhs = self._expr_to_lean(expr.lhs)
            rhs = self._expr_to_lean(expr.rhs)
            return f"{lhs} != {rhs}"

        # Handle addition
        if isinstance(expr, Add):
            terms = [self._expr_to_lean(arg) for arg in expr.args]
            return " + ".join(terms)

        # Handle multiplication
        if isinstance(expr, Mul):
            terms = [self._expr_to_lean(arg) for arg in expr.args]
            formatted_terms = []
            for t in terms:
                if ' + ' in t or ' - ' in t:
                    formatted_terms.append(f"({t})")
                else:
                    formatted_terms.append(t)
            return " * ".join(formatted_terms)

        # Handle power
        if isinstance(expr, Pow):
            base = self._expr_to_lean(expr.base)
            exp = self._expr_to_lean(expr.exp)
            if ' ' in base:
                base = f"({base})"
            return f"{base} ^ {exp}"

        # Handle symbols
        if isinstance(expr, Symbol):
            return str(expr)

        # Handle numbers
        if isinstance(expr, (int, float)):
            return str(expr)
        if isinstance(expr, Integer):
            return str(expr.value)
        if isinstance(expr, Float):
            return str(expr.value)
        if isinstance(expr, Rational):
            return f"({expr.p} / {expr.q})"

        # Handle functions
        if isinstance(expr, Sin):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.sin ({arg})"

        if isinstance(expr, Cos):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.cos ({arg})"

        if isinstance(expr, Tan):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.tan ({arg})"

        if isinstance(expr, Exp):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.exp ({arg})"

        if isinstance(expr, Log):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.log ({arg})"

        if isinstance(expr, Sqrt):
            arg = self._expr_to_lean(expr.args[0])
            return f"Real.sqrt ({arg})"

        if isinstance(expr, Abs):
            arg = self._expr_to_lean(expr.args[0])
            return f"abs ({arg})"

        # Fallback: use string representation
        return str(expr)

    # Alias for backward compatibility
    def _sympy_to_lean(self, expr: Expr) -> str:
        """Backward compatibility alias - convert expression to Lean4 syntax"""
        return self._expr_to_lean(expr)

    def _sanitize_lean_name(self, name: str) -> str:
        """Sanitize a name for use as a Lean4 identifier"""
        # Replace non-alphanumeric characters with underscores
        sanitized = ''.join(c if c.isalnum() else '_' for c in name)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = 'thm_' + sanitized
        return sanitized

    def _to_omdoc(self, candidate: CandidateConjecture) -> str:
        """Convert conjecture to OMDoc/OpenMath XML"""
        theorem = candidate.source_theorem

        # Build OpenMath content
        openmath_content = self._sympy_to_openmath(theorem.conclusion)

        # Build hypothesis section
        hypothesis_content = ""
        for i, premise in enumerate(theorem.premises):
            premise_om = self._sympy_to_openmath(premise)
            hypothesis_content += f"""
        <hypothesis id="h{i}">
          <OMOBJ xmlns="http://www.openmath.org/OpenMath">
            {premise_om}
          </OMOBJ>
        </hypothesis>"""

        omdoc = f"""<?xml version="1.0" encoding="UTF-8"?>
<omdoc xmlns="http://www.mathweb.org/omdoc" version="1.6">
  <theory name="{self._sanitize_lean_name(candidate.conjecture_id)}">
    <metadata>
      <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{candidate.conjecture_id}</dc:title>
      <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">
        {theorem.to_natural_language()}
      </dc:description>
      <meta name="domain">{theorem.domain}</meta>
      <meta name="complexity">{theorem.complexity_score}</meta>
      <meta name="novelty">{theorem.novelty_score}</meta>
      <meta name="generated">Phase 6 Synthetic Data Generator</meta>
    </metadata>

    <assertion type="conjecture" id="{candidate.conjecture_id}">
      <CMP>{theorem.to_natural_language()}</CMP>{hypothesis_content}
      <FMP>
        <OMOBJ xmlns="http://www.openmath.org/OpenMath">
          {openmath_content}
        </OMOBJ>
      </FMP>
    </assertion>

    <proof id="{candidate.conjecture_id}_proof" for="{candidate.conjecture_id}" status="pending">
      <derive>
        <CMP>To be proven by Deep Search Team</CMP>
      </derive>
    </proof>
  </theory>
</omdoc>"""
        return omdoc.strip()

    def _expr_to_openmath(self, expr: Expr) -> str:
        """Convert native symbolic expression to OpenMath XML"""
        if expr is None:
            return '<OMS cd="logic1" name="true"/>'

        # Handle symbols
        if isinstance(expr, Symbol):
            return f'<OMV name="{str(expr)}"/>'

        # Handle integers
        if isinstance(expr, int):
            return f'<OMI>{expr}</OMI>'
        if isinstance(expr, Integer):
            return f'<OMI>{expr.value}</OMI>'

        # Handle floats
        if isinstance(expr, float):
            return f'<OMF dec="{expr}"/>'
        if isinstance(expr, Float):
            return f'<OMF dec="{expr.value}"/>'

        # Handle rationals
        if isinstance(expr, Rational):
            return f'''<OMA>
  <OMS cd="nums1" name="rational"/>
  <OMI>{expr.p}</OMI>
  <OMI>{expr.q}</OMI>
</OMA>'''

        # Handle equality
        if isinstance(expr, Eq):
            return f'''<OMA>
  <OMS cd="relation1" name="eq"/>
  {self._expr_to_openmath(expr.lhs)}
  {self._expr_to_openmath(expr.rhs)}
</OMA>'''

        # Handle inequality
        if isinstance(expr, Gt):
            return f'''<OMA>
  <OMS cd="relation1" name="gt"/>
  {self._expr_to_openmath(expr.lhs)}
  {self._expr_to_openmath(expr.rhs)}
</OMA>'''

        if isinstance(expr, Ge):
            return f'''<OMA>
  <OMS cd="relation1" name="geq"/>
  {self._expr_to_openmath(expr.lhs)}
  {self._expr_to_openmath(expr.rhs)}
</OMA>'''

        if isinstance(expr, Ne):
            return f'''<OMA>
  <OMS cd="relation1" name="neq"/>
  {self._expr_to_openmath(expr.lhs)}
  {self._expr_to_openmath(expr.rhs)}
</OMA>'''

        # Handle addition
        if isinstance(expr, Add):
            args = ''.join(self._expr_to_openmath(arg) for arg in expr.args)
            return f'''<OMA>
  <OMS cd="arith1" name="plus"/>
  {args}
</OMA>'''

        # Handle multiplication
        if isinstance(expr, Mul):
            args = ''.join(self._expr_to_openmath(arg) for arg in expr.args)
            return f'''<OMA>
  <OMS cd="arith1" name="times"/>
  {args}
</OMA>'''

        # Handle power
        if isinstance(expr, Pow):
            return f'''<OMA>
  <OMS cd="arith1" name="power"/>
  {self._expr_to_openmath(expr.base)}
  {self._expr_to_openmath(expr.exp)}
</OMA>'''

        # Handle trig functions
        if isinstance(expr, Sin):
            return f'''<OMA>
  <OMS cd="transc1" name="sin"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        if isinstance(expr, Cos):
            return f'''<OMA>
  <OMS cd="transc1" name="cos"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        if isinstance(expr, Tan):
            return f'''<OMA>
  <OMS cd="transc1" name="tan"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        # Handle exp and log
        if isinstance(expr, Exp):
            return f'''<OMA>
  <OMS cd="transc1" name="exp"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        if isinstance(expr, Log):
            return f'''<OMA>
  <OMS cd="transc1" name="ln"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        if isinstance(expr, Sqrt):
            return f'''<OMA>
  <OMS cd="arith1" name="root"/>
  {self._expr_to_openmath(expr.args[0])}
  <OMI>2</OMI>
</OMA>'''

        if isinstance(expr, Abs):
            return f'''<OMA>
  <OMS cd="arith1" name="abs"/>
  {self._expr_to_openmath(expr.args[0])}
</OMA>'''

        # Fallback: represent as unknown symbol
        return f'<OMS cd="unknown" name="{type(expr).__name__}"/>'

    # Alias for backward compatibility
    def _sympy_to_openmath(self, expr: Expr) -> str:
        """Backward compatibility alias - convert expression to OpenMath XML"""
        return self._expr_to_openmath(expr)

    def get_statistics(self) -> Dict[str, Any]:
        """Get formalizer statistics"""
        return {
            **self.stats,
            'success_rate': round(
                self.stats['formalized'] / max(1, self.stats['formalized'] + self.stats['formalization_errors']) * 100, 2
            )
        }

    def reset(self):
        """Reset formalizer state"""
        for key in self.stats:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if formalizer is healthy"""
        return True
