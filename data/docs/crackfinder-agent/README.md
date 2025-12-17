# CrackFinder

Python code vulnerability probe for Claude Code. Finds every angle where your code might fail.

## Setup

Copy to your project root:
```bash
cp C:\dev\crackfinder-agent\CLAUDE.md your-project/CLAUDE.md
```

Or run from here:
```bash
cd C:\dev\crackfinder-agent && claude
```

## Usage

```
probe app.py                      # quick scan
probe src/ --deep                 # comprehensive  
probe api.py --focus security     # targeted
```

## Probe Vectors

| Vector | Finds |
|--------|-------|
| **Input Surface** | None, boundaries, injection, unicode bombs, deserialization |
| **Type System** | Missing None checks, mutable defaults, coercion traps |
| **Logic Flaws** | Off-by-one, float precision, boolean blindness |
| **Control Flow** | Broad except, silent pass, generator exhaustion |
| **State & Mutation** | Shared mutables, iteration mutation, closure capture |
| **Concurrency** | Races, deadlocks, unawaited coroutines, blocking in async |
| **Resource Management** | Unclosed handles, missing timeouts, memory growth |
| **Error Handling** | Swallowed exceptions, partial failure, assert validation |
| **Security** | SQLi, command injection, SSTI, pickle, hardcoded secrets, regex DoS |
| **API & Boundaries** | Missing validation, side-effect properties, MRO issues |
| **Dependencies** | Unpinned versions, deprecated APIs, import side effects |
| **Environment** | Hardcoded paths, timezone assumptions, encoding issues |
| **Data Integrity** | Missing validation, truncation, precision loss |
| **Observability** | Untestable code, logged secrets, dead code |

## Example Prompts

```
probe auth.py
find every place I forgot to handle None
what's the fastest way to crash this?
trace user input end to end
where are the injection points?
find race conditions in the worker
what exceptions am I swallowing?
audit for hardcoded secrets
find mutable default arguments
where do I assume UTF-8?
```

## Output

Each finding:
- Severity (🔴 Critical → 🟢 Low)
- Exact location
- What breaks and when
- Proof of concept
- Fix

**Find the cracks. Break it first.**
