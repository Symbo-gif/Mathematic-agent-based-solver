# CrackFinder Agent

A code vulnerability and weakness probing agent for Claude Code. It systematically searches your codebase for potential failure points, security vulnerabilities, and edge cases before they become production incidents.

## Installation

### Option 1: Project-Level Agent
Copy the `CLAUDE.md` file to your project root. Claude Code will automatically pick it up.

```bash
cp path/to/crackfinder-agent/CLAUDE.md /your/project/CLAUDE.md
```

### Option 2: Include as Reference
From your project, reference this agent:

```bash
# In your project's CLAUDE.md, add:
# See also: C:\dev\crackfinder-agent\CLAUDE.md
```

### Option 3: Direct Invocation
Point Claude Code at this directory:

```bash
cd C:\dev\crackfinder-agent
claude
```

---

## Usage

### Basic Scanning

```
# Scan a specific file
> Probe auth.py for cracks

# Scan a directory
> Find weaknesses in the src/api directory

# Quick security audit
> Do a security probe on the authentication module
```

### Targeted Analysis

```
# Focus on specific vulnerability types
> Look for input validation cracks in user_input.py

> Find race conditions in the queue processor

> Probe for resource leaks in connection_pool.py
```

### Deep Dives

```
# Comprehensive audit
> Do a deep probe of the entire payments module, check all categories

# Trace data flow
> Trace user input from the API endpoint through to the database, find all sanitization gaps
```

### Adversarial Testing

```
# Think like an attacker
> If you were trying to bypass authentication, where would you look?

> What's the fastest way to crash this service with malformed input?

> Find TOCTOU vulnerabilities in the file upload handler
```

---

## Probe Categories

The agent systematically checks for:

| Category | What It Finds |
|----------|---------------|
| **Input Validation** | Injection vectors, boundary violations, type confusion |
| **Logic** | Off-by-one errors, state machine gaps, assumption violations |
| **Concurrency** | Race conditions, deadlocks, non-atomic operations |
| **Error Handling** | Swallowed exceptions, inconsistent states, missing paths |
| **Resource Management** | Leaks, exhaustion, unbounded growth |
| **Security** | Auth bypass, data exposure, crypto misuse |
| **API Contracts** | Undocumented assumptions, breaking changes |
| **Environmental** | Hardcoded values, platform assumptions |

---

## Output Format

Each finding includes:

- **Severity**: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- **Location**: Exact file and line number
- **Category**: Which probe category identified it
- **The Crack**: Clear explanation
- **Attack Vector**: How it could be exploited or fail
- **Proof of Concept**: Minimal reproduction
- **Suggested Fix**: Concrete remediation

---

## Example Output

```
## 🟠 HIGH Crack Found: SQL Injection in User Lookup

**Location:** `api/users.py:47` - `get_user_by_name()`

**Category:** Input Validation / Security

**The Crack:**
User input is interpolated directly into SQL query without parameterization.

**Attack Vector:**
Attacker supplies username: `' OR '1'='1' --`
Results in query: `SELECT * FROM users WHERE name = '' OR '1'='1' --'`
Returns all users, bypassing intended filtering.

**Proof of Concept:**
```python
get_user_by_name("' OR '1'='1' --")  # Returns entire user table
```

**Suggested Fix:**
```python
# Before (vulnerable)
query = f"SELECT * FROM users WHERE name = '{name}'"

# After (safe)
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```
```

---

## Tips for Effective Probing

1. **Start broad, then focus**: Do a quick scan first, then deep-dive into concerning areas

2. **Provide context**: Tell the agent about your threat model
   ```
   > This is a payment processing service, focus on data integrity and auth
   ```

3. **Ask follow-ups**: 
   ```
   > That SQL injection you found - are there other places with the same pattern?
   ```

4. **Challenge assumptions**:
   ```
   > What happens if the database connection drops mid-transaction?
   ```

5. **Request attack scenarios**:
   ```
   > Generate test inputs that would exploit these cracks
   ```

---

## Integration with Testing

Use findings to generate test cases:

```
> Take the cracks you found and generate pytest test cases that verify the fixes
```

Or generate fuzzing inputs:

```
> Generate malformed inputs that target the input validation cracks you identified
```

---

## Limitations

- Cannot execute code or run actual tests
- Analysis is static; some runtime issues may be missed
- Severity estimates are heuristic, not definitive
- May produce false positives in complex metaprogramming scenarios

---

## Philosophy

> "Every line of code is a liability until proven otherwise."

CrackFinder assumes hostility. It doesn't give your code the benefit of the doubt. This adversarial mindset catches issues that optimistic review misses.

**Find the cracks. Break it first.**
