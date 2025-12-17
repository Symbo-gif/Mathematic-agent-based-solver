<!-- Converted from: Phase_6_Build_Order_Breakdown.docx -->

# Phase 6 Build Order Breakdown
*The Mathematical Discovery Engine*
Autonomous Mathematical Discovery Engine — 65-Agent Architecture
# 1. Executive Summary
Phase 6 represents the culmination of the Autonomous Mathematical Discovery Engine — the architectural transition from a **Problem Solving Engine** (answering known queries) to a **Discovery Engine** (generating new mathematical knowledge). While Phases 1-5 focused on mastering decidable and computable mathematics through specialization, verification, and optimization, Phase 6 must confront the "Hard Limits" of mathematics — specifically undecidability and the infinite search space of open problems.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx; phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx, Phase 6 Section
This phase operationalizes the architectures of **AlphaProof**, **FunSearch**, and **AlphaGeometry** to allow the system to function as an autonomous researcher capable of formulating conjectures, discovering novel algorithms, and expanding the boundaries of formalized mathematics.
## 1.1 Core Objectives
- Proactive Knowledge Synthesis: Evolve from reactive problem solving to autonomous conjecture generation
- Infinite Search Navigation: Deploy Reinforcement Learning-guided search for open problems with unknown solution paths
- Algorithm Discovery: Find algorithms (functions) rather than just answers using the FunSearch evolutionary paradigm
- Undecidability Management: Protect the system from Gödel/Turing limits with graceful mode-switching
- Knowledge Integration: Close the evolutionary loop by auto-formalizing discoveries into the system's axiom set
📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
## 1.2 Agent Population
Phase 6 deploys **13 new agents** organized into **5 specialized teams**, bringing the cumulative system total to **65 agents** (3 + 6 + 18 + 10 + 9 + 6 + 13 from Phases 0-6):

| Team | Agents | Primary Function |
| --- | --- | --- |
| Conjecture Generation Team | 3 | Synthetic theorem generation, pattern filtering, conjecture formalization |
| Deep Search Team | 3 | RL-guided proof search, branch evaluation, search tree management |
| Algorithm Discovery Unit | 3 | Code evolution, sandbox evaluation, heuristic distillation |
| Undecidability Navigator | 2 | Decidability classification, Human-in-the-Loop interface |
| Formal Knowledge Integration | 2 | Auto-formalization, Vector DB updates |
| TOTAL | 13 | Complete Discovery Engine |

📚 Reference: architectural_roadmap.docx, Phase 6 Section; Phased_Evolution_of_the_65-Agent_System_Architecture.docx

# 2. Foundational Dependencies: Phase 5 Infrastructure
The Discovery Engine agents of Phase 6 operate atop the Production-Optimized system established in Phase 5. Critical dependencies include:
- ThoughtTraceHarvester: Captures successful reasoning chains from the Teacher system for training new discovery agents
- ComplexityGatekeeper: Routes standard queries to Student, freeing computational resources for discovery operations
- DistillationPipeline: Provides the framework for compressing discovered knowledge into usable primitives
- EvolutionaryFlywheel: Active learning infrastructure for continuous improvement from discovery successes
- Verification Core (Phase 1): All discoveries must pass through the Ax-Prover/Logic Checker for formal verification
- Knowledge Management Team (Phase 3): RAG infrastructure for retrieving existing theorems before attempting re-discovery
📚 Reference: Phase_5_Build_Order_Breakdown.docx; phase5_symbo_integration_architecture.py
# 3. Step 1: The Conjecture Generation Team ("The Theorist")
## WHY: Addressing Proactive Knowledge Synthesis
Standard agents only retrieve existing knowledge (RAG) rather than creating new propositions. The Conjecture Generation Team evolves the system from reactive problem solving (answering a query) to proactive knowledge synthesis (asking "What else is true?"). This team upgrades the Phase 3 Hypothesis Generator into a true Conjecture Engine that autonomously scans the Knowledge Graph to identify "holes" or patterns in existing theorems.
📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1
## HOW: Three-Agent AlphaGeometry-Style Architecture
### Agent 1.1: Synthetic Data Generator ("The Dreamer")
- Role: Based on the AlphaGeometry paradigm, continuously generates random geometric or algebraic premises and attempts to derive conclusions using the Phase 2 symbolic engines
- Function: Produces millions of "synthetic theorems" — statements that are logically true but potentially trivial. Creates a massive dataset of premise-conclusion pairs to train downstream agent intuition
- Output: Stream of SyntheticTheorem objects containing premises, derivation steps, and conclusions
### Agent 1.2: Pattern Recognizer ("The Filter")
- Role: Sifts through millions of synthetic theorems from the Dreamer
- Function: Uses heuristics to filter out trivial tautologies (e.g., x=x) and identifies "interesting" non-trivial relationships that appear frequently but lack formal names. Elevates promising patterns to "Candidate Conjectures"
- Filtering Criteria: Novelty score, structural complexity, cross-domain applicability, theorem-space density analysis
### Agent 1.3: Conjecture Formalizer
- Role: Takes raw relationships from the Filter and translates them into rigorous Lean or Isabelle statements
- Function: Prepares candidate conjectures for formal verification attempts by the Deep Search Team
- Output: FormalConjecture objects with Lean4 code, OMDoc representation, and verification priority score
📚 Reference: phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx, Phase 6 Step 1
## CODE: Conjecture Generation Team Implementation
# conjecture_generation_team.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Generator
from enum import Enum
import sympy as sp
import random

class ConjectureStatus(Enum):
    GENERATED = 'generated'
    FILTERED = 'filtered'
    FORMALIZED = 'formalized'
    PROVEN = 'proven'
    REFUTED = 'refuted'

@dataclass
class SyntheticTheorem:
    theorem_id: str
    premises: List[sp.Expr]
    conclusion: sp.Expr
    derivation_steps: List[str]
    domain: str  # 'algebra', 'geometry', 'number_theory'
    complexity_score: float
    novelty_score: float = 0.0

class SyntheticDataGenerator:
    """The Dreamer - AlphaGeometry-style synthetic theorem generator"""
    def __init__(self, symbolic_engine, df_client):
        self.symbolic_engine = symbolic_engine
        self.df = df_client  # Directory Facilitator
        self.theorem_count = 0

    def generate_stream(self, batch_size=1000) -> Generator:
        """Generate synthetic theorems continuously"""
        while True:
            batch = [self._generate_single() for _ in range(batch_size)]
            yield from [t for t in batch if t is not None]
*[Full implementation continues in source file...]*

# 4. Step 2: The Deep Search Team ("The Explorer")
## WHY: Navigating Infinite Search Spaces
Standard "Tree-of-Thoughts" reasoning (Phase 3) is insufficient for open problems where the solution path is completely unknown. The Deep Search Team implements a **Product-Node Search Tree architecture** as utilized by AlphaProof, using Reinforcement Learning to guide search in high-complexity domains like the IMO Grand Challenge.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 2
## HOW: Three-Agent AlphaProof-Style Architecture
### Agent 2.1: Policy Network Agent ("The Tactician")
- Role: Specialized implementation of the AlphaProof Prover
- Function: Generates massive search trees of potential proof steps (tactics). Operates probabilistically, suggesting the "next move" based on patterns learned from synthetic theorem training
- Output: ProofStep candidates with action probabilities and tactical annotations
### Agent 2.2: Critic Network Agent ("The Evaluator")
- Role: Value-function agent estimating proof branch success probability
- Function: Evaluates the "promise" of each branch without fully expanding it. Enables early pruning of dead ends, managing computational explosion in undecidable domains
- Architecture: Transformer-based value estimator with proof-state embeddings
### Agent 2.3: Search Tree Manager
- Role: Manages the Product-Node search architecture
- Function: Tracks state of thousands of parallel proof attempts, prioritizing "promising" branches (per Critic) and suspending low-value paths
- Key Methods: MCTS-style expansion, UCB1 selection, parallel proof state checkpointing
📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2
## CODE: Deep Search Team Implementation
# deep_search_team.py
import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np
from enum import Enum

@dataclass
class ProofState:
    state_id: str
    goal: str  # Current proof goal in Lean4 syntax
    hypotheses: List[str]  # Available hypotheses
    depth: int
    parent_id: Optional[str] = None
    tactic_applied: Optional[str] = None
    value_estimate: float = 0.0
    visit_count: int = 0

class PolicyNetwork(nn.Module):
    """The Tactician - generates proof step probabilities"""
    def __init__(self, hidden_dim=512, num_tactics=256):
        super().__init__()
        self.encoder = nn.TransformerEncoder(...)
        self.policy_head = nn.Linear(hidden_dim, num_tactics)
*[Full implementation continues in source file...]*

# 5. Step 3: The Algorithm Discovery Unit ("FunSearch" Pattern)
## WHY: Finding Algorithms, Not Just Answers
Standard mathematical systems find *answers* (numbers, proofs). The Algorithm Discovery Unit shifts focus to finding *algorithms* (functions). Based on the FunSearch paradigm, the output is executable code that solves a *class* of problems more efficiently. This allows the system to solve open problems in Combinatorics (a known weakness of standard solvers) by discovering new, verifiable algorithmic approaches.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 3
## HOW: Three-Agent Evolutionary Code Search
### Agent 3.1: Code Evolutionary Proposer
- Role: LLM-based agent generating Python/Julia code snippets representing heuristics
- Function: Does not solve the math — writes the program to solve the math. Uses evolutionary logic, taking best code from previous generation and mutating to find optimizations
- Examples: "A new way to pack bins", "A faster matrix multiplication algorithm", "An improved primality test"
### Agent 3.2: Sandbox Evaluator
- Role: Secure execution environment running proposed code against rigorous test sets
- Function: Returns scalar scores (execution speed, compression ratio, accuracy) to the Proposer. Filters out incorrect code immediately, ensuring Proposer only learns from valid programs
- Security: Containerized execution with resource limits, no network access, automatic timeout
### Agent 3.3: Heuristic Distiller
- Role: Analyzes successful code to extract underlying mathematical principles
- Function: Converts "black box" code success into human-readable mathematical heuristic. Adds distilled knowledge to the Knowledge Base for future use
- Output: DistilledHeuristic objects with prose explanation, formal specification, and applicable problem classes
📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3
## CODE: Algorithm Discovery Unit Implementation
# algorithm_discovery_unit.py
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional
import time

@dataclass
class CodeCandidate:
    candidate_id: str
    code: str
    generation: int
    parent_id: Optional[str] = None
    fitness_score: float = 0.0
    execution_time_ms: float = 0.0
    correctness_score: float = 0.0
    mutation_type: str = 'initial'

class CodeEvolutionaryProposer:
    """FunSearch-style code evolution proposer"""
    def __init__(self, llm_client, problem_spec):
        self.llm = llm_client
        self.problem_spec = problem_spec
        self.population: List[CodeCandidate] = []
        self.elite_size = 10
*[Full implementation continues in source file...]*

# 6. Step 4: The Undecidability Navigator ("Boundary Watcher")
## WHY: Protecting Against the Hard Limits of Mathematics
As the system explores unknown territory, it will inevitably encounter undecidable problems (Gödel's Incompleteness, Halting Problem). The Undecidability Navigator protects the system from infinite loops and resource exhaustion by classifying problems *before* committing search resources, and switching from "Solver Mode" to "Heuristic Search Mode" when theoretical walls are hit.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 4; Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 4
## HOW: Two-Agent Boundary Detection System
### Agent 4.1: Decidability Checker
- Role: Meta-analyst inspecting logical structure of problems before Deep Search commits resources
- Function: Classifies theories into Decidable (e.g., Presburger Arithmetic, Real Closed Fields) and Undecidable (e.g., Peano Arithmetic, Diophantine Equations)
- Protocol: If undecidable, flags system to switch from Solver Mode to Heuristic Search Mode with resource bounds
- Semi-Decision Procedures: Instead of proving true/false (may loop forever), searches for counter-examples or approximate solutions
### Agent 4.2: Interactive Guidance Liaison
- Role: Human-in-the-Loop interface agent
- Function: When Deep Search hits a theoretical wall, generates a Proof State Summary and requests specific guidance from human mathematician
- Example Output: "I am stuck on this lemma; should I apply induction or contradiction?"
- Acknowledgment: System cannot be fully autonomous in undecidable fields — this agent operationalizes that constraint
## CODE: Undecidability Navigator Implementation
# undecidability_navigator.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

class DecidabilityClass(Enum):
    DECIDABLE = 'decidable'
    SEMI_DECIDABLE = 'semi_decidable'
    UNDECIDABLE = 'undecidable'
    UNKNOWN = 'unknown'

class DecidabilityChecker:
    """Classifies problems by decidability before committing resources"""
    DECIDABLE_THEORIES = {
        'presburger_arithmetic',
        'real_closed_fields',
        'propositional_logic',
        'monadic_second_order_logic_trees'
    }
    UNDECIDABLE_THEORIES = {
        'peano_arithmetic',
        'diophantine_equations',
        'first_order_logic',
        'word_problem_groups'
    }
*[Full implementation continues in source file...]*

# 7. Step 5: The Formal Knowledge Integration Team ("The Archivist")
## WHY: Closing the Evolutionary Loop
New theorems proven by the Explorer or algorithms discovered by the FunSearch unit must be **permanently integrated** into the system's capability set. This creates a **compounding intelligence effect** — if the system discovers a new identity for Prime Numbers today, the Algebra Supervisor (Phase 2) can utilize that identity as a primitive tool tomorrow.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 5
## HOW: Two-Agent Knowledge Formalization Pipeline
### Agent 5.1: Auto-Formalization Pipeline
- Role: Converts natural language or code outputs from discovery teams into strict OMDoc/OpenMath entries
- Function: Ensures new discoveries (e.g., "Theorem X") are rigorously encoded so Phase 2 Supervisors can utilize them as primitive tools
- Output Formats: OMDoc XML, Lean4 theorem statements, SymPy implementations
- Verification: All formalizations must pass through Phase 1 Verification Core before integration
### Agent 5.2: Vector Database Updater
- Role: Updates the RAG memory infrastructure
- Function: Re-indexes system memory with new discoveries, effectively "teaching" the entire Phase 2 workforce the new mathematics Phase 6 just discovered
- Integration Points: Phase 3 Knowledge Management Team (Retrieval Specialist), Phase 5 DistillationPipeline
- Result: System gets smarter with every discovery through permanent axiom expansion
📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 5
## CODE: Formal Knowledge Integration Implementation
# formal_knowledge_integration.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json

@dataclass
class FormalizedDiscovery:
    discovery_id: str
    discovery_type: str  # 'theorem', 'algorithm', 'lemma'
    natural_language_statement: str
    omdoc_representation: str
    lean4_code: Optional[str] = None
    sympy_implementation: Optional[str] = None
    proof_trace_id: Optional[str] = None
    verified: bool = False
    applicable_domains: List[str] = field(default_factory=list)
    embedding_vector: Optional[List[float]] = None

class AutoFormalizationPipeline:
    """Converts discoveries to formal representations"""
    def __init__(self, verification_core, omdoc_encoder):
        self.verifier = verification_core
        self.omdoc = omdoc_encoder
*[Full implementation continues in source file...]*

# 8. Phase 6 Completion Criteria
Phase 6 is complete when the following verification checkpoints are satisfied:
- Synthetic Theorem Generation: System can generate 10,000+ synthetic theorems per hour with <5% trivial tautology rate
- Conjecture Formalization: Candidate conjectures successfully compile to valid Lean4 statements
- Deep Search Navigation: Policy/Critic networks successfully guide proof search on IMO-level geometry problems
- Algorithm Evolution: FunSearch loop discovers improved heuristics for benchmark combinatorics problems
- Decidability Detection: System correctly classifies 95%+ of test problems into decidable/undecidable categories
- Human-in-the-Loop Protocol: Proof State Summaries successfully generated and guidance incorporated
- Knowledge Integration: New discoveries successfully formalized to OMDoc and indexed in Vector Database
- Compounding Effect: Phase 2 Supervisors can successfully retrieve and apply Phase 6 discoveries as primitives
- End-to-End Discovery: System autonomously discovers a novel (previously unknown) mathematical result
# 9. Phase 6 Deliverable: The "Researcher" System
At the conclusion of Phase 6, the system is no longer just a calculator or a tutor — it is a **Junior Research Associate**.
## Capability
The system can be given an open problem (e.g., "Find a more efficient matrix multiplication algorithm") and run for days, exploring millions of potential code variations (FunSearch) or proof paths (AlphaProof), formally verifying every step through the Verification Core, and reporting only *mathematically Truthful* discoveries.
## Safety
The system recognizes the boundaries of its own logic, flagging undecidable problems rather than hallucinating solutions. This ensures it remains a trusted tool for high-stakes mathematical inquiry — never claiming certainty where none exists.
📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Phase 6 Deliverable Section

# 10. Source Documentation Reference
This build order document synthesizes information from the following project documentation:

| Document | Content Scope |
| --- | --- |
| Phase 6 represents the transition from a Problem Solving Engine.docx | Primary technical specification with Actions 1-5 detailing all Phase 6 teams |
| Phase 6 must engineer the capacity for novel mathematical discovery.docx | Detailed agent specifications with AlphaProof, FunSearch, AlphaGeometry integration patterns |
| phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx | Overall roadmap and phase integration context, Phase 6 steps 1-5 |
| architectural_roadmap.docx | 65-agent system architecture overview, Phase 6 agent counts (13 agents across 5 teams) |
| Phased_Evolution_of_the_65-Agent_System_Architecture.docx | Phase-by-phase agent population breakdown confirming Phase 6 deploys 13 discovery agents |
| Phase_5_Build_Order_Breakdown.docx | Phase 5 infrastructure dependencies (ThoughtTraceHarvester, DistillationPipeline) that Phase 6 extends |
| phase5_symbo_integration_architecture.py | Reference implementation code for integration patterns Phase 6 builds upon |
| phase_6_Mathematical_Discovery_Engine.pdf | Visual blueprint and architectural diagrams for Phase 6 components |
| phase_6_mindmap.png, phase_6.png | Visual mind maps of Phase 6 pillars (Theorist, Explorer, FunSearch, Boundary Watcher, Archivist) |

*— End of Phase 6 Build Order Breakdown —*