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
Bootstrap Strategy Library
===========================

Initialize KnowledgeGraph with 12 fundamental problem-solving strategies.

USAGE:
------
Run this script once to populate the knowledge graph with base strategies:
    python scripts/bootstrap_strategy_library.py

STRATEGIES INITIALIZED:
-----------------------
Structural (3): Pólya Cycle, Problem Re-encoding, Local-Global Analysis
Heuristic (4): Invariant Method, Extremal Elements, Symmetrization, Functional Viewpoint
Nonstandard (3): Infinite Descent, Graphical Re-visualization, Fixed-Point Methods
Meta (2): Template Mining, Multiple-Solution Synthesis

REFERENCE:
----------
Plan: Strategy Learning Teams Integration Plan
Target: Cold-start strategy library with optimistic priors
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.infrastructure.knowledge_graph import (
    get_knowledge_graph,
    StrategyNode,
    NodeType,
    SuccessMetrics
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_patterns import (
    STRATEGY_KEYWORDS,
    get_strategy_keywords
)
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_domain_prior(strategy_name: str, domain: str) -> float:
    """
    Get prior success rate for strategy in domain.

    Uses domain knowledge to set optimistic but realistic priors.
    """
    domain_priors = {
        ('Invariant Method', 'algebra'): 0.8,
        ('Invariant Method', 'topology'): 0.75,
        ('Invariant Method', 'physics'): 0.7,
        ('Infinite Descent', 'number_theory'): 0.85,
        ('Infinite Descent', 'algebra'): 0.3,
        ('Extremal Elements', 'combinatorics'): 0.8,
        ('Extremal Elements', 'graph_theory'): 0.75,
        ('Symmetrization', 'geometry'): 0.82,
        ('Symmetrization', 'algebra'): 0.7,
        ('Functional Viewpoint', 'analysis'): 0.75,
        ('Functional Viewpoint', 'calculus'): 0.72,
        ('Graphical Re-visualization', 'discrete_math'): 0.78,
        ('Graphical Re-visualization', 'graph_theory'): 0.85,
        ('Fixed-Point Methods', 'analysis'): 0.75,
        ('Fixed-Point Methods', 'topology'): 0.7,
    }

    key = (strategy_name, domain)
    return domain_priors.get(key, 0.65)  # Default optimistic prior


def create_strategy(
    name: str,
    category: str,
    domain: str,
    abstract_description: str,
    applicability_conditions: list,
    composition_compatible: list = None,
    typical_domains: list = None
) -> StrategyNode:
    """
    Create a strategy node with proper initialization.

    Args:
        name: Strategy name
        category: 'structural', 'heuristic', 'nonstandard', 'meta'
        domain: Primary domain
        abstract_description: Domain-agnostic description
        applicability_conditions: When to apply
        composition_compatible: Compatible strategy names
        typical_domains: Domains where this works well

    Returns:
        StrategyNode ready for insertion
    """
    # Get detection signals from vocabulary
    strategy_key = name.lower().replace(' ', '_').replace('-', '_')
    keywords_data = get_strategy_keywords(strategy_key)

    detection_signals = (
        keywords_data.get('keywords', [])[:5] +  # Top 5 keywords
        keywords_data.get('agent_patterns', []) +
        keywords_data.get('metadata_signals', [])
    )

    # Initialize success rates for typical domains
    success_rates = {}
    if typical_domains:
        for dom in typical_domains:
            prior_rate = get_domain_prior(name, dom)
            success_rates[dom] = SuccessMetrics(
                domain=dom,
                applications=0,  # Will learn from experience
                successes=0,
                avg_time_ms=0.0,
                avg_complexity_reduction=0.0,
                last_success=None
            )

    node = StrategyNode(
        node_id=f"strategy_{strategy_key}",
        node_type=NodeType.STRATEGY,
        statement=name,
        domain=domain,
        category=category,
        abstract_description=abstract_description,
        detection_signals=detection_signals,
        applicability_conditions=applicability_conditions,
        composition_compatible=composition_compatible or [],
        success_rates_by_domain=success_rates,
        typical_agent_sequence=[],  # Will learn from experience
        reformulation_pattern=None,
        metadata={'bootstrapped': True, 'version': '1.0'}
    )

    return node


def bootstrap_strategy_library():
    """Initialize KnowledgeGraph with 12 fundamental strategies."""
    logger.info("=" * 80)
    logger.info("BOOTSTRAPPING STRATEGY LIBRARY")
    logger.info("=" * 80)

    kg = get_knowledge_graph()

    # Check if already bootstrapped
    stats = kg.get_statistics()
    strategy_count = stats.get('nodes_by_type', {}).get('strategy', 0)
    if strategy_count > 0:
        logger.warning(f"Strategy library already contains {strategy_count} strategies.")
        logger.warning("Skipping bootstrap to avoid duplicates.")
        return

    strategies = []

    # ========================================================================
    # STRUCTURAL STRATEGIES (3)
    # ========================================================================

    strategies.append(create_strategy(
        name="Pólya Cycle",
        category="structural",
        domain="general",
        abstract_description="Four-phase problem-solving: understand → plan → execute → retrospect. Weaponized version with recursive application.",
        applicability_conditions=[
            "problem_complexity=high",
            "domain=any",
            "novel_problem=true"
        ],
        composition_compatible=["strategy_invariant_method", "strategy_problem_re_encoding"],
        typical_domains=["algebra", "analysis", "geometry", "number_theory"]
    ))

    strategies.append(create_strategy(
        name="Problem Re-encoding",
        category="structural",
        domain="general",
        abstract_description="Transform problem representation between algebraic, geometric, combinatorial, or probabilistic formulations until one becomes trivial.",
        applicability_conditions=[
            "stuck=true",
            "alternative_encoding_exists",
            "domain=any"
        ],
        composition_compatible=["strategy_functional_viewpoint", "strategy_graphical_revisualization"],
        typical_domains=["algebra", "geometry", "discrete_math", "analysis"]
    ))

    strategies.append(create_strategy(
        name="Local-Global Analysis",
        category="structural",
        domain="general",
        abstract_description="Solve special cases (small n, extremal configurations, symmetric subcases), identify invariants, then generalize.",
        applicability_conditions=[
            "decomposable=true",
            "has_special_cases",
            "domain=any"
        ],
        composition_compatible=["strategy_symmetrization", "strategy_invariant_method"],
        typical_domains=["algebra", "topology", "analysis", "number_theory"]
    ))

    # ========================================================================
    # HEURISTIC STRATEGIES (4)
    # ========================================================================

    strategies.append(create_strategy(
        name="Invariant Method",
        category="heuristic",
        domain="algebra",
        abstract_description="Track quantities that are preserved or strictly improve under transformations. Core in combinatorics, games, algorithms, dynamical systems.",
        applicability_conditions=[
            "has_symmetry=true",
            "domain=algebra|topology|physics",
            "transformations_present"
        ],
        composition_compatible=["strategy_symmetrization", "strategy_polya_cycle"],
        typical_domains=["algebra", "topology", "physics", "discrete_math"]
    ))

    strategies.append(create_strategy(
        name="Extremal Elements",
        category="heuristic",
        domain="combinatorics",
        abstract_description="Pick element with maximal/minimal property and argue by modifying it. Core in combinatorics, graph theory, inequalities.",
        applicability_conditions=[
            "domain=combinatorics|graph_theory|optimization",
            "has_ordering",
            "optimization_possible"
        ],
        composition_compatible=["strategy_greedy"],  # Note: greedy is heuristic-level
        typical_domains=["combinatorics", "graph_theory", "optimization"]
    ))

    strategies.append(create_strategy(
        name="Symmetrization",
        category="heuristic",
        domain="geometry",
        abstract_description="Replace arbitrary configuration by more symmetric one that is no harder. Steiner symmetrization, rearrangement, averaging tricks.",
        applicability_conditions=[
            "has_symmetry=true",
            "domain=geometry|algebra|analysis",
            "extremization_needed"
        ],
        composition_compatible=["strategy_invariant_method", "strategy_local_global_analysis"],
        typical_domains=["geometry", "algebra", "analysis"]
    ))

    strategies.append(create_strategy(
        name="Functional Viewpoint",
        category="heuristic",
        domain="analysis",
        abstract_description="Turn recurrences or combinatorial structures into functional equations or generating functions, attack with complex analysis/algebraic manipulations.",
        applicability_conditions=[
            "domain=analysis|calculus|combinatorics",
            "has_recurrence|has_sequence",
            "algebraic_manipulation_hard"
        ],
        composition_compatible=["strategy_problem_re_encoding"],
        typical_domains=["analysis", "calculus", "combinatorics"]
    ))

    # ========================================================================
    # NONSTANDARD STRATEGIES (3)
    # ========================================================================

    strategies.append(create_strategy(
        name="Infinite Descent",
        category="nonstandard",
        domain="number_theory",
        abstract_description="Derive strictly smaller counterexample or use limiting argument to kill bad configurations. Method of infinite descent.",
        applicability_conditions=[
            "domain=number_theory|algebra",
            "well_ordered_set",
            "proof_by_contradiction"
        ],
        composition_compatible=[],
        typical_domains=["number_theory", "algebra"]
    ))

    strategies.append(create_strategy(
        name="Graphical Re-visualization",
        category="nonstandard",
        domain="discrete_math",
        abstract_description="Encode algebraic constraints as graphs, polytopes, or diagrams to let structure pop out. Inequality → regions, number theory → lattice points.",
        applicability_conditions=[
            "relational_structure=true",
            "domain=discrete_math|graph_theory|number_theory",
            "visualization_helpful"
        ],
        composition_compatible=["strategy_problem_re_encoding"],
        typical_domains=["discrete_math", "graph_theory", "number_theory"]
    ))

    strategies.append(create_strategy(
        name="Fixed-Point Methods",
        category="nonstandard",
        domain="analysis",
        abstract_description="Recast problem as finding fixed points of operators, use contraction or monotonicity arguments. Banach/Brouwer fixed-point theorems.",
        applicability_conditions=[
            "domain=analysis|topology",
            "complete_metric_space|compact_space",
            "iterative_process"
        ],
        composition_compatible=["strategy_functional_viewpoint"],
        typical_domains=["analysis", "topology"]
    ))

    # ========================================================================
    # META STRATEGIES (2)
    # ========================================================================

    strategies.append(create_strategy(
        name="Template Mining",
        category="meta",
        domain="general",
        abstract_description="Consciously classify solved problems by 'principle that cracked it', maintain library of templates. Transfer to similar problems.",
        applicability_conditions=[
            "similar_problems_exist",
            "domain=any",
            "pattern_recognition_possible"
        ],
        composition_compatible=["strategy_multi_solution_synthesis"],
        typical_domains=["algebra", "geometry", "analysis", "number_theory"]
    ))

    strategies.append(create_strategy(
        name="Multi-Solution Synthesis",
        category="meta",
        domain="general",
        abstract_description="Deliberately find 2-3 different solutions to same problem, abstract common core. Yields reusable lemmas/heuristics.",
        applicability_conditions=[
            "high_importance=true",
            "time_available",
            "multiple_approaches_possible"
        ],
        composition_compatible=["strategy_template_mining"],
        typical_domains=["algebra", "geometry", "analysis", "combinatorics"]
    ))

    # ========================================================================
    # INSERT ALL STRATEGIES
    # ========================================================================

    logger.info(f"\nInserting {len(strategies)} strategies into KnowledgeGraph...")

    for strategy in strategies:
        kg._insert_node(strategy)
        kg.nodes_cache[strategy.node_id] = strategy
        logger.info(f"  ✓ {strategy.statement} ({strategy.category})")

    # Add composition edges
    logger.info("\nAdding strategy composition relationships...")
    from symbo_agentic_reasoners.infrastructure.knowledge_graph import EdgeType

    composition_count = 0
    for strategy in strategies:
        for compatible_id in strategy.composition_compatible:
            if compatible_id in kg.nodes_cache or any(s.node_id == compatible_id for s in strategies):
                kg.add_relationship(
                    source_id=strategy.node_id,
                    target_id=compatible_id,
                    relationship=EdgeType.COMPOSED_WITH,
                    strength=0.75,
                    metadata={'bootstrapped': True}
                )
                composition_count += 1
                logger.info(f"  ✓ {strategy.statement} → {compatible_id}")

    # Final statistics
    logger.info("\n" + "=" * 80)
    logger.info("BOOTSTRAP COMPLETE")
    logger.info("=" * 80)
    stats = kg.get_statistics()
    logger.info(f"Total strategies: {stats.get('nodes_by_type', {}).get('strategy', 0)}")
    logger.info(f"Composition edges: {composition_count}")
    logger.info(f"Categories: Structural (3), Heuristic (4), Nonstandard (3), Meta (2)")
    logger.info("\nStrategy library ready for learning!")


if __name__ == "__main__":
    bootstrap_strategy_library()
