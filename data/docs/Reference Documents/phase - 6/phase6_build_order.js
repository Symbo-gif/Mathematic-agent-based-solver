/*
 * Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, TabStopType, 
        TabStopPosition, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// Table styling
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "2d4a6f", font: "Arial" },
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "3d5a80", font: "Arial" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
      { id: "Code", name: "Code", basedOn: "Normal",
        run: { size: 20, font: "Courier New", color: "2d3748" },
        paragraph: { spacing: { before: 100, after: 100 } } },
      { id: "Reference", name: "Reference", basedOn: "Normal",
        run: { size: 20, italics: true, color: "4a5568", font: "Arial" },
        paragraph: { spacing: { before: 50, after: 50 }, indent: { left: 360 } } }
    ]
  },
  numbering: {
    config: [
      { reference: "main-bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }
        ] },
      { reference: "step-numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "agent-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "team1-agents",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "team2-agents",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "team3-agents",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "team4-agents",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "team5-agents",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "completion-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "doc-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        size: { orientation: PageOrientation.PORTRAIT }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Phase 6 Build Order Breakdown", italics: true, size: 20, color: "666666" })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 }), 
                   new TextRun({ text: " of ", size: 20 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 })]
      })] })
    },
    children: [
      // TITLE
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Phase 6 Build Order Breakdown")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "The Mathematical Discovery Engine", size: 32, italics: true, color: "4a5568" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: [new TextRun({ text: "Autonomous Mathematical Discovery Engine — 65-Agent Architecture", size: 22, color: "718096" })] }),
      
      // SECTION 1: EXECUTIVE SUMMARY
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Executive Summary")] }),
      new Paragraph({ children: [new TextRun("Phase 6 represents the culmination of the Autonomous Mathematical Discovery Engine — the architectural transition from a "),
        new TextRun({ text: "Problem Solving Engine", bold: true }), new TextRun(" (answering known queries) to a "),
        new TextRun({ text: "Discovery Engine", bold: true }), new TextRun(" (generating new mathematical knowledge). While Phases 1-5 focused on mastering decidable and computable mathematics through specialization, verification, and optimization, Phase 6 must confront the \"Hard Limits\" of mathematics — specifically undecidability and the infinite search space of open problems.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx; phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx, Phase 6 Section")] }),
      
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun("This phase operationalizes the architectures of "),
        new TextRun({ text: "AlphaProof", bold: true }), new TextRun(", "), new TextRun({ text: "FunSearch", bold: true }), 
        new TextRun(", and "), new TextRun({ text: "AlphaGeometry", bold: true }), 
        new TextRun(" to allow the system to function as an autonomous researcher capable of formulating conjectures, discovering novel algorithms, and expanding the boundaries of formalized mathematics.")] }),
      
      // 1.1 Core Objectives
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Core Objectives")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Proactive Knowledge Synthesis: ", bold: true }), new TextRun("Evolve from reactive problem solving to autonomous conjecture generation")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Infinite Search Navigation: ", bold: true }), new TextRun("Deploy Reinforcement Learning-guided search for open problems with unknown solution paths")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Algorithm Discovery: ", bold: true }), new TextRun("Find algorithms (functions) rather than just answers using the FunSearch evolutionary paradigm")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Undecidability Management: ", bold: true }), new TextRun("Protect the system from Gödel/Turing limits with graceful mode-switching")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Knowledge Integration: ", bold: true }), new TextRun("Close the evolutionary loop by auto-formalizing discoveries into the system's axiom set")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx")] }),

      // 1.2 Agent Population
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Agent Population")] }),
      new Paragraph({ children: [new TextRun("Phase 6 deploys "), new TextRun({ text: "13 new agents", bold: true }), 
        new TextRun(" organized into "), new TextRun({ text: "5 specialized teams", bold: true }), 
        new TextRun(", bringing the cumulative system total to "), new TextRun({ text: "65 agents", bold: true }),
        new TextRun(" (3 + 6 + 18 + 10 + 9 + 6 + 13 from Phases 0-6):")] }),
      
      // Agent Population Table
      new Table({
        columnWidths: [3600, 1800, 3960],
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Team", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Agents", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Primary Function", bold: true, color: "FFFFFF" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Conjecture Generation Team")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Synthetic theorem generation, pattern filtering, conjecture formalization")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Deep Search Team")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("RL-guided proof search, branch evaluation, search tree management")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Algorithm Discovery Unit")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Code evolution, sandbox evaluation, heuristic distillation")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Undecidability Navigator")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Decidability classification, Human-in-the-Loop interface")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Formal Knowledge Integration")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Auto-formalization, Vector DB updates")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 3600, type: WidthType.DXA }, shading: { fill: "e2e8f0", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "TOTAL", bold: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, shading: { fill: "e2e8f0", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "13", bold: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 3960, type: WidthType.DXA }, shading: { fill: "e2e8f0", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Complete Discovery Engine", bold: true })] })] })
          ]})
        ]
      }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: architectural_roadmap.docx, Phase 6 Section; Phased_Evolution_of_the_65-Agent_System_Architecture.docx")] }),
      
      // SECTION 2: FOUNDATIONAL DEPENDENCIES
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Foundational Dependencies: Phase 5 Infrastructure")] }),
      new Paragraph({ children: [new TextRun("The Discovery Engine agents of Phase 6 operate atop the Production-Optimized system established in Phase 5. Critical dependencies include:")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "ThoughtTraceHarvester: ", bold: true }), new TextRun("Captures successful reasoning chains from the Teacher system for training new discovery agents")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "ComplexityGatekeeper: ", bold: true }), new TextRun("Routes standard queries to Student, freeing computational resources for discovery operations")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "DistillationPipeline: ", bold: true }), new TextRun("Provides the framework for compressing discovered knowledge into usable primitives")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "EvolutionaryFlywheel: ", bold: true }), new TextRun("Active learning infrastructure for continuous improvement from discovery successes")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Verification Core (Phase 1): ", bold: true }), new TextRun("All discoveries must pass through the Ax-Prover/Logic Checker for formal verification")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Knowledge Management Team (Phase 3): ", bold: true }), new TextRun("RAG infrastructure for retrieving existing theorems before attempting re-discovery")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase_5_Build_Order_Breakdown.docx; phase5_symbo_integration_architecture.py")] }),

      // SECTION 3: STEP 1 - CONJECTURE GENERATION TEAM
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Step 1: The Conjecture Generation Team (\"The Theorist\")")] }),
      
      // WHY
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("WHY: Addressing Proactive Knowledge Synthesis")] }),
      new Paragraph({ children: [new TextRun("Standard agents only retrieve existing knowledge (RAG) rather than creating new propositions. The Conjecture Generation Team evolves the system from reactive problem solving (answering a query) to proactive knowledge synthesis (asking \"What else is true?\"). This team upgrades the Phase 3 Hypothesis Generator into a true Conjecture Engine that autonomously scans the Knowledge Graph to identify \"holes\" or patterns in existing theorems.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1")] }),

      // HOW
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("HOW: Three-Agent AlphaGeometry-Style Architecture")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 1.1: Synthetic Data Generator (\"The Dreamer\")")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Based on the AlphaGeometry paradigm, continuously generates random geometric or algebraic premises and attempts to derive conclusions using the Phase 2 symbolic engines")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Produces millions of \"synthetic theorems\" — statements that are logically true but potentially trivial. Creates a massive dataset of premise-conclusion pairs to train downstream agent intuition")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Output: ", bold: true }), new TextRun("Stream of SyntheticTheorem objects containing premises, derivation steps, and conclusions")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 1.2: Pattern Recognizer (\"The Filter\")")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Sifts through millions of synthetic theorems from the Dreamer")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Uses heuristics to filter out trivial tautologies (e.g., x=x) and identifies \"interesting\" non-trivial relationships that appear frequently but lack formal names. Elevates promising patterns to \"Candidate Conjectures\"")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Filtering Criteria: ", bold: true }), new TextRun("Novelty score, structural complexity, cross-domain applicability, theorem-space density analysis")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 1.3: Conjecture Formalizer")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Takes raw relationships from the Filter and translates them into rigorous Lean or Isabelle statements")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Prepares candidate conjectures for formal verification attempts by the Deep Search Team")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Output: ", bold: true }), new TextRun("FormalConjecture objects with Lean4 code, OMDoc representation, and verification priority score")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx, Phase 6 Step 1")] }),

      // CODE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CODE: Conjecture Generation Team Implementation")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("# conjecture_generation_team.py")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from dataclasses import dataclass, field")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from typing import List, Dict, Optional, Generator")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from enum import Enum")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import sympy as sp")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import random")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class ConjectureStatus(Enum):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    GENERATED = 'generated'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    FILTERED = 'filtered'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    FORMALIZED = 'formalized'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    PROVEN = 'proven'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    REFUTED = 'refuted'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("@dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class SyntheticTheorem:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    theorem_id: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    premises: List[sp.Expr]")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    conclusion: sp.Expr")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    derivation_steps: List[str]")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    domain: str  # 'algebra', 'geometry', 'number_theory'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    complexity_score: float")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    novelty_score: float = 0.0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class SyntheticDataGenerator:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('    """The Dreamer - AlphaGeometry-style synthetic theorem generator"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    def __init__(self, symbolic_engine, df_client):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.symbolic_engine = symbolic_engine")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.df = df_client  # Directory Facilitator")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.theorem_count = 0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    def generate_stream(self, batch_size=1000) -> Generator:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('        """Generate synthetic theorems continuously"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        while True:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("            batch = [self._generate_single() for _ in range(batch_size)]")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("            yield from [t for t in batch if t is not None]")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "[Full implementation continues in source file...]", italics: true, color: "718096" })] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),
      
      // SECTION 4: DEEP SEARCH TEAM
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Step 2: The Deep Search Team (\"The Explorer\")")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("WHY: Navigating Infinite Search Spaces")] }),
      new Paragraph({ children: [new TextRun("Standard \"Tree-of-Thoughts\" reasoning (Phase 3) is insufficient for open problems where the solution path is completely unknown. The Deep Search Team implements a "),
        new TextRun({ text: "Product-Node Search Tree architecture", bold: true }), new TextRun(" as utilized by AlphaProof, using Reinforcement Learning to guide search in high-complexity domains like the IMO Grand Challenge.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 2")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("HOW: Three-Agent AlphaProof-Style Architecture")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 2.1: Policy Network Agent (\"The Tactician\")")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Specialized implementation of the AlphaProof Prover")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Generates massive search trees of potential proof steps (tactics). Operates probabilistically, suggesting the \"next move\" based on patterns learned from synthetic theorem training")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Output: ", bold: true }), new TextRun("ProofStep candidates with action probabilities and tactical annotations")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 2.2: Critic Network Agent (\"The Evaluator\")")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Value-function agent estimating proof branch success probability")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Evaluates the \"promise\" of each branch without fully expanding it. Enables early pruning of dead ends, managing computational explosion in undecidable domains")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Architecture: ", bold: true }), new TextRun("Transformer-based value estimator with proof-state embeddings")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 2.3: Search Tree Manager")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Manages the Product-Node search architecture")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Tracks state of thousands of parallel proof attempts, prioritizing \"promising\" branches (per Critic) and suspending low-value paths")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Key Methods: ", bold: true }), new TextRun("MCTS-style expansion, UCB1 selection, parallel proof state checkpointing")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CODE: Deep Search Team Implementation")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("# deep_search_team.py")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import torch")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import torch.nn as nn")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from dataclasses import dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from typing import List, Dict, Tuple, Optional")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import numpy as np")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from enum import Enum")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("@dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class ProofState:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    state_id: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    goal: str  # Current proof goal in Lean4 syntax")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    hypotheses: List[str]  # Available hypotheses")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    depth: int")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    parent_id: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    tactic_applied: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    value_estimate: float = 0.0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    visit_count: int = 0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class PolicyNetwork(nn.Module):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('    """The Tactician - generates proof step probabilities"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    def __init__(self, hidden_dim=512, num_tactics=256):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        super().__init__()")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.encoder = nn.TransformerEncoder(...)")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.policy_head = nn.Linear(hidden_dim, num_tactics)")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "[Full implementation continues in source file...]", italics: true, color: "718096" })] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 5: ALGORITHM DISCOVERY UNIT
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Step 3: The Algorithm Discovery Unit (\"FunSearch\" Pattern)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("WHY: Finding Algorithms, Not Just Answers")] }),
      new Paragraph({ children: [new TextRun("Standard mathematical systems find "), new TextRun({ text: "answers", italics: true }), 
        new TextRun(" (numbers, proofs). The Algorithm Discovery Unit shifts focus to finding "), 
        new TextRun({ text: "algorithms", italics: true }), new TextRun(" (functions). Based on the FunSearch paradigm, the output is executable code that solves a "),
        new TextRun({ text: "class", italics: true }), new TextRun(" of problems more efficiently. This allows the system to solve open problems in Combinatorics (a known weakness of standard solvers) by discovering new, verifiable algorithmic approaches.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 3")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("HOW: Three-Agent Evolutionary Code Search")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 3.1: Code Evolutionary Proposer")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("LLM-based agent generating Python/Julia code snippets representing heuristics")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Does not solve the math — writes the program to solve the math. Uses evolutionary logic, taking best code from previous generation and mutating to find optimizations")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Examples: ", bold: true }), new TextRun("\"A new way to pack bins\", \"A faster matrix multiplication algorithm\", \"An improved primality test\"")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 3.2: Sandbox Evaluator")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Secure execution environment running proposed code against rigorous test sets")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Returns scalar scores (execution speed, compression ratio, accuracy) to the Proposer. Filters out incorrect code immediately, ensuring Proposer only learns from valid programs")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Security: ", bold: true }), new TextRun("Containerized execution with resource limits, no network access, automatic timeout")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 3.3: Heuristic Distiller")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Analyzes successful code to extract underlying mathematical principles")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Converts \"black box\" code success into human-readable mathematical heuristic. Adds distilled knowledge to the Knowledge Base for future use")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Output: ", bold: true }), new TextRun("DistilledHeuristic objects with prose explanation, formal specification, and applicable problem classes")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CODE: Algorithm Discovery Unit Implementation")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("# algorithm_discovery_unit.py")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import subprocess")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import tempfile")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from dataclasses import dataclass, field")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from typing import List, Dict, Callable, Optional")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import time")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("@dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class CodeCandidate:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    candidate_id: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    code: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    generation: int")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    parent_id: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    fitness_score: float = 0.0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    execution_time_ms: float = 0.0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    correctness_score: float = 0.0")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    mutation_type: str = 'initial'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class CodeEvolutionaryProposer:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('    """FunSearch-style code evolution proposer"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    def __init__(self, llm_client, problem_spec):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.llm = llm_client")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.problem_spec = problem_spec")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.population: List[CodeCandidate] = []")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.elite_size = 10")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "[Full implementation continues in source file...]", italics: true, color: "718096" })] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 6: UNDECIDABILITY NAVIGATOR
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Step 4: The Undecidability Navigator (\"Boundary Watcher\")")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("WHY: Protecting Against the Hard Limits of Mathematics")] }),
      new Paragraph({ children: [new TextRun("As the system explores unknown territory, it will inevitably encounter undecidable problems (Gödel's Incompleteness, Halting Problem). The Undecidability Navigator protects the system from infinite loops and resource exhaustion by classifying problems "),
        new TextRun({ text: "before", italics: true }), new TextRun(" committing search resources, and switching from \"Solver Mode\" to \"Heuristic Search Mode\" when theoretical walls are hit.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 4; Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 4")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("HOW: Two-Agent Boundary Detection System")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 4.1: Decidability Checker")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Meta-analyst inspecting logical structure of problems before Deep Search commits resources")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Classifies theories into Decidable (e.g., Presburger Arithmetic, Real Closed Fields) and Undecidable (e.g., Peano Arithmetic, Diophantine Equations)")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Protocol: ", bold: true }), new TextRun("If undecidable, flags system to switch from Solver Mode to Heuristic Search Mode with resource bounds")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Semi-Decision Procedures: ", bold: true }), new TextRun("Instead of proving true/false (may loop forever), searches for counter-examples or approximate solutions")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 4.2: Interactive Guidance Liaison")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Human-in-the-Loop interface agent")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("When Deep Search hits a theoretical wall, generates a Proof State Summary and requests specific guidance from human mathematician")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Example Output: ", bold: true }), new TextRun("\"I am stuck on this lemma; should I apply induction or contradiction?\"")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Acknowledgment: ", bold: true }), new TextRun("System cannot be fully autonomous in undecidable fields — this agent operationalizes that constraint")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CODE: Undecidability Navigator Implementation")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("# undecidability_navigator.py")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from enum import Enum")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from dataclasses import dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from typing import List, Dict, Optional, Set")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class DecidabilityClass(Enum):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    DECIDABLE = 'decidable'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    SEMI_DECIDABLE = 'semi_decidable'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    UNDECIDABLE = 'undecidable'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    UNKNOWN = 'unknown'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class DecidabilityChecker:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('    """Classifies problems by decidability before committing resources"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    DECIDABLE_THEORIES = {")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'presburger_arithmetic',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'real_closed_fields',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'propositional_logic',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'monadic_second_order_logic_trees'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    }")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    UNDECIDABLE_THEORIES = {")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'peano_arithmetic',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'diophantine_equations',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'first_order_logic',")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        'word_problem_groups'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    }")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "[Full implementation continues in source file...]", italics: true, color: "718096" })] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 7: FORMAL KNOWLEDGE INTEGRATION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Step 5: The Formal Knowledge Integration Team (\"The Archivist\")")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("WHY: Closing the Evolutionary Loop")] }),
      new Paragraph({ children: [new TextRun("New theorems proven by the Explorer or algorithms discovered by the FunSearch unit must be "),
        new TextRun({ text: "permanently integrated", bold: true }), new TextRun(" into the system's capability set. This creates a "),
        new TextRun({ text: "compounding intelligence effect", bold: true }), new TextRun(" — if the system discovers a new identity for Prime Numbers today, the Algebra Supervisor (Phase 2) can utilize that identity as a primitive tool tomorrow.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Action 5")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("HOW: Two-Agent Knowledge Formalization Pipeline")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 5.1: Auto-Formalization Pipeline")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Converts natural language or code outputs from discovery teams into strict OMDoc/OpenMath entries")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Ensures new discoveries (e.g., \"Theorem X\") are rigorously encoded so Phase 2 Supervisors can utilize them as primitive tools")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Output Formats: ", bold: true }), new TextRun("OMDoc XML, Lean4 theorem statements, SymPy implementations")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Verification: ", bold: true }), new TextRun("All formalizations must pass through Phase 1 Verification Core before integration")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Agent 5.2: Vector Database Updater")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Role: ", bold: true }), new TextRun("Updates the RAG memory infrastructure")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Function: ", bold: true }), new TextRun("Re-indexes system memory with new discoveries, effectively \"teaching\" the entire Phase 2 workforce the new mathematics Phase 6 just discovered")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Integration Points: ", bold: true }), new TextRun("Phase 3 Knowledge Management Team (Retrieval Specialist), Phase 5 DistillationPipeline")] }),
      new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
        new TextRun({ text: "Result: ", bold: true }), new TextRun("System gets smarter with every discovery through permanent axiom expansion")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 5")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CODE: Formal Knowledge Integration Implementation")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("# formal_knowledge_integration.py")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from dataclasses import dataclass, field")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from typing import List, Dict, Optional")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("from datetime import datetime")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("import json")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("@dataclass")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class FormalizedDiscovery:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    discovery_id: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    discovery_type: str  # 'theorem', 'algorithm', 'lemma'")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    natural_language_statement: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    omdoc_representation: str")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    lean4_code: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    sympy_implementation: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    proof_trace_id: Optional[str] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    verified: bool = False")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    applicable_domains: List[str] = field(default_factory=list)")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    embedding_vector: Optional[List[float]] = None")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("class AutoFormalizationPipeline:")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun('    """Converts discoveries to formal representations"""')] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("    def __init__(self, verification_core, omdoc_encoder):")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.verifier = verification_core")] }),
      new Paragraph({ style: "Code", shading: { fill: "f7fafc", type: ShadingType.CLEAR }, children: [new TextRun("        self.omdoc = omdoc_encoder")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "[Full implementation continues in source file...]", italics: true, color: "718096" })] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 8: COMPLETION CRITERIA
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Phase 6 Completion Criteria")] }),
      new Paragraph({ children: [new TextRun("Phase 6 is complete when the following verification checkpoints are satisfied:")] }),
      
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Synthetic Theorem Generation: ", bold: true }), new TextRun("System can generate 10,000+ synthetic theorems per hour with <5% trivial tautology rate")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Conjecture Formalization: ", bold: true }), new TextRun("Candidate conjectures successfully compile to valid Lean4 statements")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Deep Search Navigation: ", bold: true }), new TextRun("Policy/Critic networks successfully guide proof search on IMO-level geometry problems")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Algorithm Evolution: ", bold: true }), new TextRun("FunSearch loop discovers improved heuristics for benchmark combinatorics problems")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Decidability Detection: ", bold: true }), new TextRun("System correctly classifies 95%+ of test problems into decidable/undecidable categories")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Human-in-the-Loop Protocol: ", bold: true }), new TextRun("Proof State Summaries successfully generated and guidance incorporated")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Knowledge Integration: ", bold: true }), new TextRun("New discoveries successfully formalized to OMDoc and indexed in Vector Database")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "Compounding Effect: ", bold: true }), new TextRun("Phase 2 Supervisors can successfully retrieve and apply Phase 6 discoveries as primitives")] }),
      new Paragraph({ numbering: { reference: "completion-list", level: 0 }, children: [
        new TextRun({ text: "End-to-End Discovery: ", bold: true }), new TextRun("System autonomously discovers a novel (previously unknown) mathematical result")] }),
      
      // SECTION 9: DELIVERABLE
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Phase 6 Deliverable: The \"Researcher\" System")] }),
      new Paragraph({ children: [new TextRun("At the conclusion of Phase 6, the system is no longer just a calculator or a tutor — it is a "),
        new TextRun({ text: "Junior Research Associate", bold: true }), new TextRun(".")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Capability")] }),
      new Paragraph({ children: [new TextRun("The system can be given an open problem (e.g., \"Find a more efficient matrix multiplication algorithm\") and run for days, exploring millions of potential code variations (FunSearch) or proof paths (AlphaProof), formally verifying every step through the Verification Core, and reporting only "),
        new TextRun({ text: "mathematically Truthful", italics: true }), new TextRun(" discoveries.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Safety")] }),
      new Paragraph({ children: [new TextRun("The system recognizes the boundaries of its own logic, flagging undecidable problems rather than hallucinating solutions. This ensures it remains a trusted tool for high-stakes mathematical inquiry — never claiming certainty where none exists.")] }),
      new Paragraph({ style: "Reference", children: [new TextRun("📚 Reference: Phase 6 represents the transition from a Problem Solving Engine.docx, Phase 6 Deliverable Section")] }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 10: SOURCE DOCUMENTATION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("10. Source Documentation Reference")] }),
      new Paragraph({ children: [new TextRun("This build order document synthesizes information from the following project documentation:")] }),
      
      // Documentation Table
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Document", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Content Scope", bold: true, color: "FFFFFF" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Phase 6 represents the transition from a Problem Solving Engine.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Primary technical specification with Actions 1-5 detailing all Phase 6 teams")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Phase 6 must engineer the capacity for novel mathematical discovery.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Detailed agent specifications with AlphaProof, FunSearch, AlphaGeometry integration patterns")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Overall roadmap and phase integration context, Phase 6 steps 1-5")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "architectural_roadmap.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("65-agent system architecture overview, Phase 6 agent counts (13 agents across 5 teams)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Phased_Evolution_of_the_65-Agent_System_Architecture.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Phase-by-phase agent population breakdown confirming Phase 6 deploys 13 discovery agents")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Phase_5_Build_Order_Breakdown.docx", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Phase 5 infrastructure dependencies (ThoughtTraceHarvester, DistillationPipeline) that Phase 6 extends")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "phase5_symbo_integration_architecture.py", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Reference implementation code for integration patterns Phase 6 builds upon")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "phase_6_Mathematical_Discovery_Engine.pdf", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Visual blueprint and architectural diagrams for Phase 6 components")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "phase_6_mindmap.png, phase_6.png", italics: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Visual mind maps of Phase 6 pillars (Theorist, Explorer, FunSearch, Boundary Watcher, Archivist)")] })] })
          ]})
        ]
      }),
      
      new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "— End of Phase 6 Build Order Breakdown —", italics: true, color: "718096" })] })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/Phase_6_Build_Order_Breakdown.docx", buffer);
  console.log("Phase 6 Build Order Breakdown created successfully!");
});
