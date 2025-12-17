# Security Quick Reference Card

**Symbo Agentic Reasoners - Security Testing & Best Practices**

---

## 🚀 Quick Start (5 Minutes)

```bash
# Run security scan
python scripts/run_security_tests.py --quick

# Run full audit
python scripts/run_security_tests.py --full

# Run specific tests
pytest tests/test_security_injection_advanced.py -v
pytest tests/test_security_parser_bombs.py -v
pytest tests/test_security_agent_isolation.py -v
```

---

## 🔒 Security Checklist for Developers

### Before Accepting User Input

- [ ] Use `safe_parse()` instead of direct parsing
- [ ] Validate input length (< 10,000 chars)
- [ ] Check for null bytes
- [ ] Normalize Unicode (if non-ASCII)
- [ ] Estimate complexity before processing

### Example:
```python
from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

try:
    expr = safe_parse(user_input)
except SecurityError as e:
    log_security_event(e)
    return sanitized_error_message()
```

---

## ⚠️ Common Vulnerabilities & Fixes

### 1. Code Injection
**DON'T:**
```python
eval(user_input)  # NEVER!
exec(user_input)  # NEVER!
```

**DO:**
```python
from symbo_agentic_reasoners.core.safe_parser import safe_parse
expr = safe_parse(user_input)  # Safe
```

### 2. Computation Bombs
**DON'T:**
```python
result = simplify((x+1)**100000)  # May hang forever
```

**DO:**
```python
from symbo_agentic_reasoners.infrastructure.resource_governor import get_governor

governor = get_governor()
if governor.can_proceed('simplify'):
    with timeout(30):
        result = simplify(expr)
```

### 3. Information Disclosure
**DON'T:**
```python
return f"Error: {exception}"  # May leak paths
```

**DO:**
```python
log_full_error(exception)  # Log internally
return "Invalid expression"  # Return generic message
```

### 4. Agent Impersonation
**DON'T:**
```python
# Accept any agent_id without validation
process_message(sender_id=user_provided_id)
```

**DO:**
```python
from symbo_agentic_reasoners.infrastructure.security_monitor import SecurityMonitor

monitor = SecurityMonitor()
decision = monitor.check_access(agent_id, resource, action)
if decision == AccessDecision.ALLOW:
    process_message()
```

---

## 🛡️ Defense Layers

### Layer 1: Input Validation (`safe_parser.py`)
- Pattern blacklist (30+ dangerous patterns)
- Length limits (10,000 chars)
- Nesting depth (50 levels)
- Null byte rejection

### Layer 2: Resource Limits (`resource_governor.py`)
- Operation timeouts
- Memory monitoring
- CPU/VRAM tracking
- Emergency shutdown

### Layer 3: Access Control (`security_monitor.py`)
- Agent authentication
- Rate limiting
- Privilege enforcement
- Audit logging

### Layer 4: Sandbox (`sandbox_evaluator.py`)
- Restricted builtins
- No file/network access
- Process isolation
- Timeout enforcement

---

## 📊 Test Your Code

### Unit Test Template
```python
import pytest
from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

def test_my_feature_security():
    """Test that my feature rejects malicious input."""
    malicious_inputs = [
        "__import__('os')",
        "(x+1)**100000",
        "eval('code')"
    ]

    for inp in malicious_inputs:
        with pytest.raises((SecurityError, ValueError)):
            safe_parse(inp)
```

### Integration Test Template
```python
def test_end_to_end_security():
    """Test full pipeline security."""
    # 1. Check input validation
    with pytest.raises(SecurityError):
        solve("__import__('os')")

    # 2. Check resource limits
    with pytest.raises(TimeoutError):
        solve("(x+1)**100000")

    # 3. Check safe expressions work
    result = solve("x**2 + 2*x + 1")
    assert result is not None
```

---

## 🔥 Emergency Response

### If Security Alert Triggered

1. **Check Security Monitor**
   ```python
   from symbo_agentic_reasoners.infrastructure.security_monitor import SecurityMonitor

   monitor = SecurityMonitor()
   alerts = monitor.get_recent_alerts(severity_filter=AlertSeverity.HIGH)
   for alert in alerts:
       print(alert.description)
   ```

2. **Enable Lockdown Mode**
   ```python
   monitor.set_lockdown(True)  # Deny all access
   ```

3. **Review Logs**
   ```python
   # Check access logs
   for log in monitor.access_logs[-100:]:
       if log.decision == AccessDecision.DENY:
           print(f"{log.agent_id} -> {log.resource}")
   ```

4. **Block Malicious Agent**
   ```python
   monitor.block_agent("suspicious_agent_id", "Attempted code injection")
   ```

---

## 📈 Monitoring Metrics

### Key Metrics to Track

```python
from symbo_agentic_reasoners.infrastructure.security_monitor import SecurityMonitor

monitor = SecurityMonitor()
stats = monitor.get_statistics()

print(f"Access checks: {stats['access_checks']}")
print(f"Denials: {stats['access_denials']}")
print(f"Denial rate: {stats['denial_rate']:.1f}%")
print(f"Alerts: {stats['alerts_generated']}")
```

**Normal Baselines:**
- Denial rate: < 1%
- Alerts per hour: < 5
- Unknown agents: 0
- Lockdown events: 0

**Alert Thresholds:**
- Denial rate > 5% → Investigate
- Alerts per hour > 20 → Possible attack
- Unknown agents > 10 → Policy issue
- Any lockdown event → Critical incident

---

## 🎯 Common Attack Patterns

### Pattern 1: Injection via Unicode
**Attack:** `__іmport__('os')`  (Cyrillic 'і')
**Defense:** Unicode normalization
**Detection:** `test_unicode_homoglyph_blocked()`

### Pattern 2: Computation Bomb
**Attack:** `(x+1)**100000`
**Defense:** Complexity estimation + timeout
**Detection:** `test_exponential_expansion_bomb()`

### Pattern 3: Sandbox Escape
**Attack:** `import os; os.system('ls')`
**Defense:** Restricted builtins
**Detection:** `test_filesystem_access_blocked()`

### Pattern 4: Agent Impersonation
**Attack:** Send message as "ams_001"
**Defense:** Message authentication (TODO)
**Detection:** `test_infrastructure_agent_cannot_be_spoofed()`

### Pattern 5: Resource Exhaustion
**Attack:** 1000s of rapid requests
**Defense:** Rate limiting
**Detection:** `test_rate_limiting_enforced()`

---

## 💡 Best Practices

### DO:
- ✅ Always use `safe_parse()` for user input
- ✅ Check `can_proceed()` before expensive ops
- ✅ Use timeouts for all operations
- ✅ Log security events
- ✅ Sanitize error messages
- ✅ Validate agent IDs
- ✅ Monitor resource usage

### DON'T:
- ❌ Use `eval()` or `exec()` on user input
- ❌ Trust agent IDs without validation
- ❌ Return full stack traces to users
- ❌ Skip input validation "just once"
- ❌ Ignore security alerts
- ❌ Disable timeouts "temporarily"
- ❌ Allow unlimited recursion

---

## 🔧 Quick Fixes for Common Issues

### "SecurityError: Dangerous pattern detected"
**Cause:** Input contains blacklisted pattern
**Fix:** User input is malicious - reject and log

### "ValueError: Nesting too deep"
**Cause:** Expression has > 50 nesting levels
**Fix:** Legitimate? Increase `MAX_NESTING_DEPTH`. Otherwise reject.

### "TimeoutError: Operation exceeded limit"
**Cause:** Operation took too long
**Fix:** Check if expression is too complex or timeout too short

### "AccessDecision.DENY"
**Cause:** Agent doesn't have permission
**Fix:** Check access control policy or register agent

---

## 📚 Full Documentation

- **Comprehensive Research:** `SECURITY_TESTING_RESEARCH.md` (15,000+ words)
- **Summary:** `SECURITY_TESTING_SUMMARY.md` (Quick overview)
- **This Card:** `SECURITY_QUICK_REFERENCE.md` (You are here)

---

## 🚨 Security Contacts

**For Security Issues:**
1. DO NOT post security vulnerabilities publicly
2. Report to development team privately
3. Enable lockdown mode if actively exploited
4. Review `SECURITY_TESTING_RESEARCH.md` for details

---

## ✅ Daily Security Checks

```bash
# Morning checklist (5 min)
python scripts/run_security_tests.py --quick

# Weekly audit (20 min)
python scripts/run_security_tests.py --full --output weekly_report.json

# Review alerts
python -c "
from symbo_agentic_reasoners.infrastructure.security_monitor import SecurityMonitor
m = SecurityMonitor()
alerts = m.get_recent_alerts()
print(f'Alerts: {len(alerts)}')
"
```

---

**Last Updated:** 2025-12-15
**Version:** 1.0
**Status:** ✅ Production Ready
