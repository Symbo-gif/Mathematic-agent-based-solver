import os
import ast
import re
from pathlib import Path

# Expected agents from the audit document
EXPECTED_AGENTS = {
    "Phase 0": {
        "AMS": ["AgentManagementSystem", "AMS"],
        "DF": ["DirectoryFacilitator", "DF"],
        "ACC": ["AgentCommunicationChannel", "ACC"]
    },
    "Phase 1": {
        "PA-1": ["ProblemParser", "PA1", "SyntaxParserAgent"],
        "PA-2": ["ComplexityEstimator", "PA2", "StructureRecognizerAgent"],
        "CNS-1": ["Orchestrator", "CNS1", "CentralNervousSystem", "MainOrchestrator"],
        "PS-1": ["FastHeuristicSolver", "PilotSolver", "PS1", "PilotSolverAgent"],
        "VC-1": ["ProofChecker", "VC1", "LogicCheckerAgent"],
        "VC-2": ["ConsistencyValidator", "VC2", "SimplifiedVerifierAgent"]
    },
    "Phase 2": {
        "ALG-1": ["PolynomialSolver", "ALG1", "PolynomialSpecialist"],
        "ALG-2": ["SymbolicSimplifier", "ALG2", "ArithmeticSpecialist", "NumberTheorySpecialist"], # Mapping Arithmetic/NumberTheory here as partial coverage
        "ALG-3": ["EquationSystemSolver", "ALG3"],
        "ALG-4": ["GroupRingTheoryAgent", "ALG4"],
        "CAL-1": ["DifferentiationEngine", "CAL1", "DifferentiationSpecialist"],
        "CAL-2": ["IntegrationEngine", "CAL2", "IntegrationSpecialist"],
        "CAL-3": ["LimitEvaluator", "CAL3"],
        "CAL-4": ["SeriesAnalyzer", "CAL4", "SeriesSpecialist"],
        "CAL-5": ["DifferentialEquationsSolver", "CAL5", "ODESolver"],
        "LA-1": ["MatrixOperationsEngine", "LA1", "MatrixOperationsSpecialist"],
        "LA-2": ["EigenvalueSolver", "LA2", "DecompositionSpecialist"],
        "LA-3": ["VectorSpaceAnalyzer", "LA3", "VectorSpaceAnalyst"],
        "LA-4": ["TensorOperationsAgent", "LA4"],
        "PROB-1": ["DistributionModeler", "PROB1", "DistributionSpecialist"],
        "PROB-2": ["BayesianInferenceEngine", "PROB2"],
        "PROB-3": ["HypothesisTestingAgent", "PROB3", "FrequentistAgent"],
        "PROB-4": ["StochasticProcessAnalyzer", "PROB4"],
        "NUM-1": ["NumericalMethodsEngine", "NUM1", "NumericalComputationUtility"]
    },
    "Phase 3": {
        "PV-1": ["DomainChecker", "PV1", "DomainCheckerAgent"],
        "PV-2": ["TypeVerifier", "PV2", "AssumptionValidatorAgent"],
        "PV-3": ["ConstraintSatisfiabilityChecker", "PV3", "ConstraintPropagatorAgent"],
        "PV-4": ["InvariantMonitor", "PV4", "EdgeCaseDetectorAgent"],
        "KM-1": ["KnowledgeBaseManager", "KM1", "ContextExtractorAgent", "MemoryIndexerAgent", "RetrievalSpecialistAgent"], # Team mapping
        "KM-2": ["PatternIndexer", "KM2"],
        "KM-3": ["TheoremLibraryManager", "KM3"],
        "HG-1": ["ConjectureGenerator", "HG1", "HypothesisGeneratorAgent"],
        "HG-2": ["CounterexampleSearcher", "HG2", "PathEvaluatorAgent"],
        "HG-3": ["AnalogyEngine", "HG3", "BacktrackingManagerAgent"]
    },
    "Phase 4": {
        "CR-1": ["SolutionArbiter", "CR1", "DebateModerator"],
        "CR-2": ["ResourceContentionManager", "CR2", "EvidenceWeigher"],
        "CR-3": ["ConsensusCoordinator", "CR3", "ConsensusBuilder"],
        "FA-1": ["ErrorDiagnostician", "FA1", "ErrorClassifier"],
        "FA-2": ["RecoveryOrchestrator", "FA2", "RootCauseAnalyzer"],
        "FA-3": ["FaultPredictor", "FA3", "AlternativePathGenerator"],
        "ML-1": ["StrategyOptimizer", "ML1", "AgentSelectorOptimizer"],
        "ML-2": ["SolverPortfolioManager", "ML2", "AdaptiveDispatcher"],
        "ML-3": ["HyperparameterTuner", "ML3", "PerformanceMonitor"]
    },
    "Phase 5": {
        "DH-1": ["KnowledgeDistiller", "DH1", "StudentModelTrainer", "DistillationPipeline"],
        "DH-2": ["PatternHarvester", "DH2", "ThoughtTraceHarvester"],
        "HD-1": ["GPUScheduler", "HD1"],
        "HD-2": ["ComputeOptimizer", "HD2"],
        "OH-1": ["SecurityMonitor", "OH1"],
        "OH-2": ["ResilienceTester", "OH2"]
    },
    "Phase 6": {
        "CG-1": ["PatternExtrapolator", "CG1", "PatternRecognizer"],
        "CG-2": ["StructuralSynthesizer", "CG2", "CodeEvolutionaryProposer"],
        "CG-3": ["BoundaryExplorer", "CG3"],
        "DS-1": ["ExhaustiveEnumerator", "DS1"],
        "DS-2": ["HeuristicSearchCoordinator", "DS2", "HeuristicDistiller"],
        "DS-3": ["ParallelSearchManager", "DS3"],
        "AD-1": ["AlgorithmSynthesizer", "AD1"],
        "AD-2": ["ComplexityAnalyzer", "AD2"],
        "AD-3": ["OptimizationTransformer", "AD3"],
        "UN-1": ["DecidabilityClassifier", "UN1", "DecidabilityChecker"],
        "UN-2": ["ApproximationStrategist", "UN2", "InteractiveGuidanceLiaison"],
        "FKI-1": ["ProofAssistantBridge", "FKI1", "AutoFormalizationPipeline"],
        "FKI-2": ["MathematicalOntologyManager", "FKI2", "VectorDatabaseUpdater"]
    }
}

def find_classes_in_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return classes
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def scan_codebase(root_dir):
    found_classes = {}
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                classes = find_classes_in_file(file_path)
                for cls in classes:
                    found_classes[cls] = file_path
    return found_classes

def audit_agents(found_classes):
    report = []
    found_count = 0
    missing_count = 0
    
    report.append("# Agent System Audit Report\n")
    
    for phase, agents in EXPECTED_AGENTS.items():
        report.append(f"## {phase}")
        for agent_id, aliases in agents.items():
            found = False
            for alias in aliases:
                if alias in found_classes:
                    report.append(f"- [x] **{agent_id}**: Found as `{alias}` in `{found_classes[alias]}`")
                    found = True
                    break
                # Try partial match or fuzzy match if needed, but strict for now
            
            if not found:
                # Try to find by partial match in all found classes
                potential_matches = [cls for cls in found_classes.keys() if any(alias.lower() in cls.lower() for alias in aliases)]
                if potential_matches:
                     report.append(f"- [?] **{agent_id}**: Not found exactly. Potential candidates: {', '.join([f'`{m}`' for m in potential_matches])}")
                else:
                    report.append(f"- [ ] **{agent_id}**: MISSING")
                    missing_count += 1
            else:
                found_count += 1
        report.append("")

    report.append("## Summary")
    report.append(f"Total Expected: {sum(len(a) for a in EXPECTED_AGENTS.values())}")
    report.append(f"Found: {found_count}")
    report.append(f"Missing: {missing_count}")
    
    return "\n".join(report)

if __name__ == "__main__":
    root_dir = r"C:\dev\Mathematic agent based solver\src\symbo_agentic_reasoners"
    found_classes = scan_codebase(root_dir)
    report = audit_agents(found_classes)
    
    output_path = r"C:\dev\Mathematic agent based solver\docs\audit\Agent_System_Audit_Report.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Audit report generated at {output_path}")
    # print(report)
    print("Found classes:")
    for cls, path in found_classes.items():
        print(f"{cls}: {path}")
