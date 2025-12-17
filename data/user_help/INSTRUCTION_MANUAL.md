# SYMBO_AGENTIC_REASONERS Instruction Manual
## Agent-Based Mathematical Discovery Engine

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Running the System](#running-the-system)
5. [Using the Mathematical Solver](#using-the-mathematical-solver)
6. [Running Audits](#running-audits)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Getting Started

The SYMBO_AGENTIC_REASONERS system is a multi-phase agent-based mathematical problem solver. Each phase builds on the previous, providing increasingly sophisticated capabilities.

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run system health check
python -m tests.test_phase0

# 3. Start solving problems (Phase 1+)
python -m symbo_agentic_reasoners_phase1.phase1_system
```

---

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **RAM**: 8GB minimum (16GB recommended for Phase 5+)
- **Storage**: 2GB free space
- **OS**: Windows 10/11, Linux, macOS

### Required Python Packages

```
sympy>=1.12          # Symbolic mathematics
numpy>=1.24          # Numerical computing
scipy>=1.11          # Scientific computing
```

### Optional Packages (Enhanced Features)

```
chromadb>=0.4        # Vector database (production mode)
torch>=2.0           # Neural network training (Phase 5+)
transformers>=4.30   # LLM integration (Phase 5+)
python-docx>=0.8     # Document conversion
```

---

## Installation

### Step 1: Clone or Download

Ensure you have the complete project directory structure.

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Core dependencies
pip install sympy numpy scipy

# Optional: Full installation
pip install chromadb torch transformers python-docx
```

### Step 4: Verify Installation

```bash
python scripts/verify_installation.py
```

---

## Running the System

### Phase-by-Phase Startup

Each phase can be run independently for testing:

```bash
# Phase 0: Infrastructure only
python -m symbo_agentic_reasoners_phase0.phase0_system

# Phase 1: Basic solving
python -m symbo_agentic_reasoners_phase1.phase1_system

# Phase 2: Domain specialists
python -m symbo_agentic_reasoners_phase2.phase2_system

# Phase 3: Meta-cognitive
python -m symbo_agentic_reasoners_phase3.phase3_system

# Phase 4: Governance
python -m symbo_agentic_reasoners_phase4.phase4_system

# Phase 5: Production optimization
python -m symbo_agentic_reasoners_phase5.phase5_system

# Phase 6: Discovery engine
python -m symbo_agentic_reasoners_phase6.phase6_system
```

### Full System Startup

```bash
# Start complete system (Phase 6 includes all lower phases)
python scripts/start_full_system.py
```

---

## Using the Mathematical Solver

### Basic Problem Solving

```python
from symbo_agentic_reasoners_phase1.phase1_system import Phase1System

# Initialize
system = Phase1System()
system.start()

# Solve a problem
result = system.solve("Integrate x^2 from 0 to 1")
print(result)

# Shutdown
system.shutdown()
```

### Using Phase 2 Specialists

```python
from symbo_agentic_reasoners_phase2.phase2_system import Phase2System

system = Phase2System()
system.start()

# Calculus problem
result = system.solve("Find the derivative of sin(x) * e^x")

# Linear algebra problem
result = system.solve("Find eigenvalues of matrix [[1,2],[3,4]]")

# Algebra problem
result = system.solve("Factor x^3 - 1")

system.shutdown()
```

### Using Phase 3 with Knowledge Management

```python
from symbo_agentic_reasoners_phase3.phase3_system import Phase3System

system = Phase3System()
system.start()

# Problem validation
validation = system.validate_problem(problem, "conv_001")

# Solve with hypothesis generation
result = system.solve(problem, "conv_001")

# Check for similar solved problems
context = system.get_context(problem, "conv_001")

system.shutdown()
```

### Problem Types Supported

| Category | Examples |
|----------|----------|
| **Calculus** | Integration, differentiation, limits, series |
| **Algebra** | Equation solving, factorization, polynomial operations |
| **Linear Algebra** | Matrix operations, eigenvalues, decompositions |
| **Number Theory** | GCD, prime factorization, modular arithmetic |
| **Statistics** | Distributions, Bayesian inference, hypothesis testing |
| **Discrete Math** | Combinatorics, graph algorithms |

---

## Running Audits

### Quick Audit (Single Phase)

```bash
# Run Phase 0 audit
python -m audit.audit_runner

# Run specific phase audit
python -m audit.phase1.audit_runner
python -m audit.phase2.audit_runner
python -m audit.phase3.audit_runner
python -m audit.phase4.audit_runner
python -m audit.phase5.audit_runner
python -m audit.phase6.audit_runner
```

### Full System Audit

```bash
python scripts/run_all_audits.py
```

### Audit Reports

Reports are generated in markdown format:
- `audit/reports/` - Phase 0 reports
- `audit/phase1/reports/` - Phase 1 reports
- etc.

---

## Troubleshooting

### Common Issues

#### ChromaDB Not Installed

```
WARNING: ChromaDB not installed. Vector database will run in mock mode.
```

**Solution**: This is a warning, not an error. The system runs in mock mode. To use full features:
```bash
pip install chromadb
```

#### Import Errors

```
ModuleNotFoundError: No module named 'symbo_agentic_reasoners_phase0'
```

**Solution**: Ensure you're running from the project root:
```bash
cd "c:\dev\Mathematic agent based solver"
python -m symbo_agentic_reasoners_phase0.phase0_system
```

#### Memory Issues (Phase 5+)

```
CUDA out of memory / Memory allocation failed
```

**Solution**: Phase 5+ can be memory intensive. Options:
1. Reduce batch sizes in configuration
2. Use CPU-only mode
3. Increase system RAM/VRAM

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Advanced Configuration

### Environment Variables

```bash
# Set ChromaDB path
set CHROMA_DB_PATH=./data/chromadb

# Set thought trace directory
set THOUGHT_TRACE_PATH=./traces

# Enable debug mode
set SYMBO_AGENTIC_REASONERS_DEBUG=1
```

### Custom Agent Configuration

Agents can be customized through their constructors:

```python
from symbo_agentic_reasoners_phase2.agents.calculus.integration_specialist import IntegrationSpecialist

# Custom configuration
specialist = IntegrationSpecialist(
    blackboard=custom_blackboard,
    vector_db=custom_vector_db
)
```

### Extending the System

#### Adding New Specialists

1. Create new agent in appropriate domain folder
2. Inherit from `BDIAgent` base class
3. Register with Directory Facilitator
4. Update supervisor routing

#### Adding New Domain

1. Create new folder under `symbo_agentic_reasoners_phase2/agents/`
2. Create domain supervisor under `symbo_agentic_reasoners_phase2/supervisors/`
3. Register domain tag in Phase 1 recognizer
4. Update orchestrator routing

---

## Performance Tips

1. **Use Phase 2 for Complex Math**: Phase 1's Pilot Solver is basic
2. **Enable Vector DB**: Install ChromaDB for better knowledge retrieval
3. **Batch Operations**: Use conversation IDs to group related problems
4. **Monitor Blackboard**: Large blackboards can slow operations

---

## Support

For issues and feature requests:
1. Check `audit/reports/` for diagnostic information
2. Enable debug logging
3. Review the system schematic for architecture understanding
4. Consult the commands reference for available operations

---

## Version Information

- **System Version**: 1.0.0
- **Phase 0-6**: Complete
- **Last Updated**: December 2024
