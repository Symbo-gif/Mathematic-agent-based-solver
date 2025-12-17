# SYMBO AGENTIC REASONERS - Quick Start Guide

## Essential Commands

### Starting the System

```bash
# Interactive Mode (REPL)
python main.py

# Or use the scripts directly
python scripts/math_solver.py
```

### Solving Problems

```bash
# Single problem from command line
python main.py solve "2 + 2"
python main.py solve "factor(x^2 - 4)"
python main.py solve "integrate(x^2, x)"
python main.py solve "diff(sin(x), x)"

# Batch processing (multiple problems from file)
python main.py batch ./problems.txt
python main.py batch ./exam.txt --output results.json
```

### System Status
```bash
python main.py status
```

---

## Keyboard Shortcuts & Controls

| Action | Key/Command |
|--------|-------------|
| **Graceful Exit** | `Ctrl+C` - Saves state and exits cleanly |
| **Save Session** | Automatic on exit, or type `save` in REPL |
| **Resume Session** | `python scripts/math_solver.py --resume` |
| **Help** | Type `help` in interactive mode |
| **Exit** | Type `exit`, `quit`, or press `Ctrl+C` |
| **System Status** | Type `status` - Show hardware and solver metrics |
| **Hardware Info** | Type `hardware` - Detailed hardware status |
| **Explore Math** | Type `explore` or `explore 60` - Autonomous exploration! |
| **View Discoveries** | Type `discover` - See what the system has learned |

---

## Entering Mathematics

The system accepts multiple mathematical notation formats:

### Standard Text Format
```
2 + 2
x^2 - 4
sin(x) + cos(x)
```

### SymPy Format (Recommended)
```
factor(x**2 - 4)
integrate(x**2, x)
diff(sin(x), x)
solve(x**2 - 4, x)
limit(sin(x)/x, x, 0)
series(exp(x), x, 0, 5)
Matrix([[1, 2], [3, 4]])
```

### Common Operations

| Operation | Syntax |
|-----------|--------|
| Addition | `a + b` |
| Subtraction | `a - b` |
| Multiplication | `a * b` or `a*b` |
| Division | `a / b` |
| Power | `x**2` or `x^2` |
| Square root | `sqrt(x)` |
| Factorial | `factorial(n)` |
| Absolute value | `Abs(x)` |

### Calculus

| Operation | Syntax |
|-----------|--------|
| Differentiate | `diff(expr, x)` |
| Integrate | `integrate(expr, x)` |
| Definite integral | `integrate(expr, (x, a, b))` |
| Limit | `limit(expr, x, value)` |
| Taylor series | `series(expr, x, point, order)` |

### Algebra

| Operation | Syntax |
|-----------|--------|
| Solve equation | `solve(equation, x)` |
| Factor | `factor(expr)` |
| Expand | `expand(expr)` |
| Simplify | `simplify(expr)` |
| Partial fractions | `apart(expr)` |

### Linear Algebra

| Operation | Syntax |
|-----------|--------|
| Matrix | `Matrix([[1, 2], [3, 4]])` |
| Determinant | `Matrix(...).det()` |
| Inverse | `Matrix(...).inv()` |
| Eigenvalues | `Matrix(...).eigenvals()` |

---

## Example Session

```
$ python main.py

================================================================================
SYMBO AGENTIC REASONERS - Mathematical Problem Solver
================================================================================

Enter mathematical problems. Type 'help' for commands, 'exit' to quit.

>>> 2 + 2
Result: 4

>>> factor(x**2 - 4)
Result: (x - 2)*(x + 2)

>>> integrate(x**2, x)
Result: x**3/3

>>> diff(sin(x), x)
Result: cos(x)

>>> solve(x**2 - 4, x)
Result: [-2, 2]

>>> exit
Saving session... Done.
Goodbye!
```

---

## Batch Processing Format

Create a text file with one problem per line:

**problems.txt:**
```
2 + 2
factor(x**2 - 1)
integrate(x, x)
diff(x**3, x)
solve(x + 5 = 10, x)
```

**Run:**
```bash
python main.py batch problems.txt --output results.json
```

---

## Autonomous Exploration (Curiosity Engine)

The system can explore mathematics on its own when you're not giving it problems!

### Start Exploration
```
>>> explore        # Explore for 30 seconds (default)
>>> explore 60     # Explore for 60 seconds
>>> explore 300    # Explore for 5 minutes
```

### What Happens During Exploration
1. The system generates random mathematical problems across categories:
   - Algebra (factoring, solving, simplification)
   - Calculus (derivatives, integrals, limits, series)
   - Number Theory (factorization, primes, GCD/LCM)
   - Linear Algebra (matrices, determinants, eigenvalues)
   - Combinatorics (binomials, factorials)
   - Analysis (infinite series, products)
   - Geometry (analytic geometry)

2. It solves each problem and evaluates how "interesting" the result is

3. Interesting discoveries are saved for later review

### View What It Learned
```
>>> discover       # Show recent interesting discoveries
```

Discoveries are rated by interest level:
- `*` - Notable
- `**` - Interesting
- `***` - Surprising
- `****` - Remarkable

### Persistence
Discoveries are saved to `data/curiosity/discoveries.jsonl` and persist across sessions!

---

## Troubleshooting

### Common Issues

1. **"ChromaDB not found"** - This is a warning, not an error. The system works without it.

2. **"Expression not recognized"** - Try using SymPy syntax with `**` for powers.

3. **Ctrl+C doesn't work** - Wait a moment, the system is saving state.

### Verify Installation
```bash
python scripts/verify_installation.py
```

### Run Tests
```bash
python -m pytest tests/ -v
```

---

## More Help

- Full documentation: `user_help/INSTRUCTION_MANUAL.md`
- API reference: `user_help/COMMANDS_REFERENCE.md`
- System architecture: `user_help/SYSTEM_SCHEMATIC.md`
