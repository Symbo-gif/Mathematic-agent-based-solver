# System Management Agents

Meta-level agents for system maintenance, documentation, auditing, and codebase health management.

## Overview

System agents are specialized utilities that operate at the meta-level, managing and maintaining the SYMBO codebase itself rather than solving mathematical problems. These agents help keep the system organized, documented, and healthy by performing automated analysis, cleanup, and documentation tasks.

**Agent Count**: 9 system agents
**Purpose**: System maintenance, documentation, code quality
**Architecture**: Standalone utility agents

## Core Philosophy

System agents embody the principle: **"The system that maintains itself"**

These are not mathematical agents - they are **development and maintenance tools** that:
- Keep codebase organized
- Generate documentation
- Find and fix issues
- Monitor system health
- Automate repetitive tasks

## Agent Inventory

### 1. Structure Cataloger

#### structure_cataloger.py
**Purpose**: Dynamically scan and catalog entire codebase structure

**Capabilities**:
- Scan all Python modules and extract metadata
- Identify agent hierarchies (orchestrator → supervisors → specialists)
- Map dependencies between modules
- Generate comprehensive system catalogs
- Track lines of code, classes, functions

**Output**: Comprehensive system structure catalog (see `sonar files/system_structure_catalog.txt`)

**Key Classes**:
- `ModuleInfo` - Metadata about a Python module
- `AgentInfo` - Information about an agent
- `StructureCataloger` - Main cataloging engine

**Usage**:
```python
from src.system_agents.structure_cataloger import StructureCataloger

cataloger = StructureCataloger(root_path="c:/dev/Mathematic agent based solver")

# Scan entire codebase
catalog = cataloger.scan_codebase()

print(f"Total modules: {len(catalog['modules'])}")
print(f"Total agents: {len(catalog['agents'])}")

# Generate report
report = cataloger.generate_report(output_path="system_catalog.txt")
```

**Generated Data**:
- Module inventory with line counts
- Agent hierarchy (tier 1, 2, 3)
- Dependency graphs
- Domain coverage analysis
- Statistics (LOC, agent count, etc.)

---

### 2. Documentation Agent

#### documentation_agent.py
**Purpose**: Generate and update documentation automatically

**Capabilities**:
- Generate README files for directories
- Extract docstrings and create API docs
- Update documentation with current system state
- Generate usage examples
- Create architectural diagrams (text-based)

**Usage**:
```python
from src.system_agents.documentation_agent import DocumentationAgent

doc_agent = DocumentationAgent(root_path="c:/dev/Mathematic agent based solver")

# Generate README for a directory
doc_agent.generate_readme(
    directory="src/symbo_agentic_reasoners/agents",
    output_path="src/symbo_agentic_reasoners/agents/README.md"
)

# Generate API documentation
doc_agent.generate_api_docs(
    module="symbo_agentic_reasoners.core.bdi_agent",
    output_path="docs/api/bdi_agent.md"
)
```

**Output Formats**:
- Markdown README files
- API documentation
- Architecture diagrams
- Usage guides

---

### 3. Audit Agent

#### audit_agent.py
**Purpose**: Audit system integrity and compliance with architectural patterns

**Capabilities**:
- Check system integrity (missing components)
- Evaluate agent performance metrics
- Verify compliance with architecture patterns
- Identify deviations from design principles
- Generate improvement recommendations

**Checks**:
- **Integrity**: All required modules present?
- **Compliance**: Following hub-and-spoke pattern?
- **Performance**: Agents within acceptable performance ranges?
- **Architecture**: BDI implementation correct?
- **Dependencies**: Appropriate separation of concerns?

**Usage**:
```python
from src.system_agents.audit_agent import AuditAgent

auditor = AuditAgent(system_path="c:/dev/Mathematic agent based solver")

# Conduct full audit
audit_report = auditor.conduct_audit(output_path="audit_report.txt")

print(f"System integrity: {audit_report['system_integrity']['status']}")
print(f"Compliance score: {audit_report['compliance']['score']}")
print(f"Recommendations: {audit_report['recommendations']}")
```

**Output**: Comprehensive audit report with findings and recommendations

---

### 4. Cleanup Agent

#### cleanup_agent.py
**Purpose**: Clean up and organize codebase

**Capabilities**:
- Find and remove temporary files (*.tmp, *.bak, *~)
- Identify and consolidate duplicate files
- Organize loose files into appropriate folders
- Remove orphaned files
- Calculate space recovered

**Patterns Cleaned**:
- Temporary files: `*.tmp`, `*.bak`, `*~`, `*.swp`
- Cache directories: `__pycache__`, `.pytest_cache`
- Build artifacts: `build/`, `dist/`, `*.egg-info`
- Editor files: `.vscode/`, `.idea/`

**Usage**:
```python
from src.system_agents.cleanup_agent import CleanupAgent

cleanup = CleanupAgent(root_path="c:/dev/Mathematic agent based solver")

# Perform cleanup (dry run)
report = cleanup.perform_cleanup(dry_run=True)

print(f"Temp files found: {report['temp_files_found']}")
print(f"Duplicates found: {report['duplicates_found']}")
print(f"Space recoverable: {report['space_recoverable']} MB")

# Actually clean up
cleanup.perform_cleanup(dry_run=False)
```

**Safety**: Always performs dry run first, reports before deleting

---

### 5. Code Chunking Agent

#### code_chunking_agent.py
**Purpose**: Break large files into manageable chunks for analysis or processing

**Capabilities**:
- Chunk large Python files intelligently
- Preserve class and function boundaries
- Generate chunk metadata
- Support overlapping chunks for context

**Use Cases**:
- LLM context window management
- Parallel code analysis
- Incremental processing
- Code review preparation

**Usage**:
```python
from src.system_agents.code_chunking_agent import CodeChunkingAgent

chunker = CodeChunkingAgent()

# Chunk large file
chunks = chunker.chunk_file(
    file_path="src/symbo_agentic_reasoners/core/native_calculus.py",
    max_lines=500,
    overlap_lines=50
)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: lines {chunk.start_line}-{chunk.end_line}")
    print(f"Contains: {len(chunk.classes)} classes, {len(chunk.functions)} functions")
```

**Smart Chunking**: Never breaks in middle of class or function

---

### 6. Script Decomposer

#### script_decomposer.py
**Purpose**: Decompose monolithic scripts into modular components

**Capabilities**:
- Analyze script dependencies
- Identify reusable components
- Suggest module structure
- Generate refactored code

**Use Case**: Convert large scripts into proper modules

**Usage**:
```python
from src.system_agents.script_decomposer import ScriptDecomposer

decomposer = ScriptDecomposer()

# Analyze script
analysis = decomposer.analyze_script("scripts/math_solver.py")

print(f"Suggested modules: {analysis['suggested_modules']}")
print(f"Reusable functions: {analysis['reusable_functions']}")

# Generate refactored structure
decomposer.generate_refactored_structure(
    script="scripts/math_solver.py",
    output_dir="src/symbo_agentic_reasoners/refactored"
)
```

---

### 7. CrackFinder Agent

#### crackfinder_agent.py
**Purpose**: Find potential bugs, vulnerabilities, and code issues

**Capabilities**:
- Static code analysis
- Pattern-based bug detection
- Security vulnerability scanning
- Code smell detection
- Performance anti-pattern identification

**Checks**:
- Potential null pointer dereferences
- Unreachable code
- Infinite loop risks
- Resource leaks
- Security vulnerabilities (SQL injection, XSS, etc.)
- Performance issues (N+1 queries, unnecessary loops)

**Usage**:
```python
from src.system_agents.crackfinder_agent import CrackFinderAgent

crackfinder = CrackFinderAgent()

# Scan file for issues
issues = crackfinder.scan_file("src/symbo_agentic_reasoners/core/solver_engine.py")

for issue in issues:
    print(f"{issue.severity}: {issue.message}")
    print(f"  Line {issue.line}: {issue.code_snippet}")
    print(f"  Suggestion: {issue.suggestion}")
```

**Severity Levels**: CRITICAL, HIGH, MEDIUM, LOW, INFO

---

### 8. Mathematical Cracker

#### mathematical_cracker.py
**Purpose**: Test mathematical solver with challenging edge cases

**Capabilities**:
- Generate adversarial mathematical problems
- Test solver robustness
- Find solver weaknesses
- Benchmark performance on edge cases
- Stress test system limits

**Test Categories**:
- Edge cases (division by zero, undefined limits)
- Numerical instability (large numbers, precision loss)
- Pathological cases (non-convergent series)
- Performance limits (deeply nested expressions)
- Undecidable problems

**Usage**:
```python
from src.system_agents.mathematical_cracker import MathematicalCracker
from symbo_agentic_reasoners.core.system import SymboSystem

cracker = MathematicalCracker()
system = SymboSystem()

# Generate edge cases
edge_cases = cracker.generate_edge_cases(category="calculus", count=100)

# Test system
results = cracker.test_solver(system, edge_cases)

print(f"Passed: {results.passed}/{results.total}")
print(f"Failed: {results.failed}")
print(f"Errors: {results.errors}")

# Identify weaknesses
weaknesses = cracker.identify_weaknesses(results)
for weakness in weaknesses:
    print(f"Weakness: {weakness.category}")
    print(f"  Failure rate: {weakness.failure_rate}%")
```

**Output**: Comprehensive solver robustness report

---

## Usage Patterns

### System Maintenance Workflow

```python
from src.system_agents import (
    StructureCataloger, AuditAgent, CleanupAgent, CrackFinderAgent
)

# 1. Catalog system structure
cataloger = StructureCataloger("c:/dev/Mathematic agent based solver")
catalog = cataloger.scan_codebase()
cataloger.generate_report("system_catalog.txt")

# 2. Audit system integrity
auditor = AuditAgent("c:/dev/Mathematic agent based solver")
audit = auditor.conduct_audit("audit_report.txt")

# 3. Find code issues
crackfinder = CrackFinderAgent()
issues = crackfinder.scan_directory("src/symbo_agentic_reasoners")

# 4. Clean up
cleanup = CleanupAgent("c:/dev/Mathematic agent based solver")
cleanup.perform_cleanup(dry_run=False)

print("System maintenance complete!")
```

### Pre-Release Checklist

```python
# Run all system agents before release
def pre_release_check():
    # 1. Update documentation
    doc_agent.generate_all_readmes()

    # 2. Audit system
    audit = auditor.conduct_audit()
    assert audit['system_integrity']['status'] == 'healthy'

    # 3. Find critical issues
    issues = crackfinder.scan_directory("src")
    critical = [i for i in issues if i.severity == 'CRITICAL']
    assert len(critical) == 0

    # 4. Test robustness
    edge_cases = mathematical_cracker.generate_edge_cases(count=1000)
    results = mathematical_cracker.test_solver(system, edge_cases)
    assert results.passed / results.total > 0.95  # 95% pass rate

    # 5. Clean up
    cleanup.perform_cleanup()

    print("✓ System ready for release")
```

---

## Output Locations

System agents generate outputs in:

- **Catalogs**: `sonar files/system_structure_catalog.txt`
- **Audit Reports**: Root directory or `reports/`
- **Documentation**: `docs/` and per-directory `README.md`
- **Cleanup Reports**: `cleanup_report.txt`
- **Issue Reports**: `code_issues.json`

---

## Testing

System agents have their own tests:

```bash
# Test structure cataloger
pytest tests/test_system_agents.py -k cataloger

# Test audit agent
pytest tests/test_system_agents.py -k audit

# Test cleanup agent
pytest tests/test_system_agents.py -k cleanup

# Test all system agents
pytest tests/test_system_agents.py
```

---

## Running System Agents

### From Command Line

```bash
# Catalog system structure
python -m src.system_agents.structure_cataloger

# Conduct audit
python -m src.system_agents.audit_agent

# Clean up codebase
python -m src.system_agents.cleanup_agent

# Find code issues
python -m src.system_agents.crackfinder_agent

# Test solver robustness
python -m src.system_agents.mathematical_cracker
```

### From Scripts

See `scripts/run_all_audits.py` for comprehensive system agent execution.

---

## Design Principles

### 1. Non-Invasive

System agents observe and report, rarely modify:
- Read-only operations by default
- Require confirmation for destructive operations
- Always generate reports before acting

### 2. Standalone

Each agent is independent:
- No dependencies on other system agents
- Can run in isolation
- Self-contained functionality

### 3. Automated

Designed for automation:
- Scriptable interfaces
- Deterministic behavior
- Machine-readable output formats

### 4. Comprehensive

Thorough in analysis:
- Deep code inspection
- Exhaustive pattern matching
- Complete codebase coverage

---

## Future Enhancements

1. **Auto-Fix Agent**: Automatically fix common issues
2. **Performance Profiler**: Profile agent performance
3. **Test Generator**: Auto-generate test cases
4. **Refactoring Agent**: Suggest and apply refactorings
5. **Dependency Updater**: Update outdated dependencies
6. **Security Scanner**: Enhanced security analysis
7. **Documentation Validator**: Ensure docs match code

---

## Related Components

- `../symbo_agentic_reasoners/` - Main system being managed
- `../../tests/` - System agent tests
- `../../scripts/` - Scripts using system agents
- `../../sonar files/` - Output from system agents

---

Generated by SYMBO Documentation System
Last Updated: 2025-12-14
