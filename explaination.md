# Explanation of assg02.py - Extended Assignment Scheduling Solver

## Overview
Extension of Assignment 1. Finds OPTIMAL values (minimum days or minimum prompts)
instead of all schedules. Supports two modes of result sharing.

---

## What's New vs Assignment 1

| Aspect | Assignment 1 | Assignment 2 |
|--------|-------------|--------------|
| Goal | Find ALL valid schedules | Find MINIMUM days or prompts |
| Input | N, K, M from file + CLI | N, K or M from CLI only |
| Modes | Single mode | Mode 1 (instant) + Mode 2 (next-day) |
| Output | All schedules | Single optimal value |

---

## Data Flow

```
CLI Args → parse arguments
              ↓
Input File → parse_input() → assignments dict
                                    ↓
                            has_cycle() → validation
                                    ↓
        ┌─────────────────────────────────────────┐
        │  Binary Search on Days or Prompts       │
        │         ↓                               │
        │  can_complete_mode1/mode2() → bool      │
        │         ↓                               │
        │  Adjust search bounds                   │
        └─────────────────────────────────────────┘
                                    ↓
                            Print optimal value
```

---

## Two Modes Explained

### Mode 1: Instant Sharing
- Same as Assignment 1.
- When a student completes an assignment, ALL students can immediately use that result.
- Dependency satisfied → assignment becomes ready for anyone.

### Mode 2: Next-Day Sharing
- Results are shared only at 6am next day.
- If Student A completes Assignment X on Day 1:
  - Student A can start Assignment Y (depends on X) on Day 1 (they have the answer).
  - Student B must wait until Day 2 to start Y (gets answer at 6am Day 2).
- Adds complexity: must track WHO completed WHAT on WHICH day.

---

## Line-by-Line Explanation

### Lines 1-2: Imports
```python
import sys
import argparse
```
- `argparse` for flexible command-line argument parsing with flags.

---

### Lines 4-14: parse_input()
Identical to Assignment 1, but ignores N and K from file (taken from CLI).

---

### Lines 16-26: has_cycle()
Identical to Assignment 1. Detects cyclic dependencies.

---

### Lines 28-32: can_fit()
Identical to Assignment 1. Tries to assign to a student with enough prompts.

---

### Lines 34-36: get_ready()
Identical to Assignment 1. Gets assignments with all dependencies completed.

---

### Lines 38-47: can_complete_mode1()
```python
def can_complete_mode1(assignments, N, K, M):
    total = len(assignments)
    def dfs(day, completed, remaining, today):
        if len(completed) == total: return True
        if day > M: return False
```
- Modified from Assignment 1's `solve()`.
- Returns `True/False` instead of collecting all schedules.
- **Early termination**: Returns immediately when solution found.

```python
        for aid in get_ready(completed, assignments):
            fits, new_rem = can_fit(assignments[aid]['prompts'], remaining)
            if fits and dfs(day, completed | {aid}, new_rem, True): return True
```
- Tries each ready assignment.
- If any branch succeeds, immediately return True.

```python
        if today and dfs(day + 1, completed, tuple([K]*N), False): return True
        return False
```
- Try ending day. Return False only if all branches fail.

---

### Lines 49-61: get_ready_mode2()
```python
def get_ready_mode2(completed, prev_done, assignments, student_done):
    ready = []
    for aid, data in assignments.items():
        if aid in completed: continue
```
- `prev_done`: Assignments completed on previous days (shareable to all).
- `student_done`: Dict mapping student_id → set of assignments they did today.

```python
        if data['deps'].issubset(prev_done):
            ready.append((aid, list(range(len(student_done)))))
```
- If all deps from previous days → any student can do it.

```python
        else:
            allowed = [i for i, done in student_done.items() 
                       if all(d in prev_done or d in done for d in data['deps'])]
            if allowed: ready.append((aid, allowed))
```
- Otherwise, only students who completed missing deps today can do it.
- Returns list of (assignment_id, list_of_allowed_students).

---

### Lines 63-75: can_complete_mode2()
```python
def can_complete_mode2(assignments, N, K, M):
    total = len(assignments)
    def dfs(day, completed, prev_done, remaining, student_done, today):
```
- Extra state: `prev_done` (shareable results), `student_done` (per-student today).

```python
        for aid, allowed in get_ready_mode2(completed, prev_done, assignments, student_done):
            p = assignments[aid]['prompts']
            for s in allowed:
                if remaining[s] >= p:
```
- Iterates ready assignments and their allowed students.
- Checks if student `s` has enough prompts.

```python
                    new_rem = remaining[:s] + (remaining[s] - p,) + remaining[s+1:]
                    new_sd = {k: v.copy() for k, v in student_done.items()}
                    new_sd[s].add(aid)
```
- Updates remaining prompts for student `s`.
- Deep copies `student_done` and adds assignment to student `s`.

```python
        if today and dfs(day + 1, completed, completed, tuple([K]*N), {i: set() for i in range(N)}, False): return True
```
- When day ends: `completed` becomes `prev_done` (now shareable).
- Reset `student_done` to empty sets for new day.

---

### Lines 77-85: find_min_days()
```python
def find_min_days(assignments, N, K, mode):
    if max(d['prompts'] for d in assignments.values()) > K: return -1
```
- Early check: If any assignment needs more than K prompts, impossible.

```python
    check = can_complete_mode1 if mode == 1 else can_complete_mode2
    low, high, result = 1, len(assignments), -1
```
- Select appropriate feasibility checker.
- Binary search range: 1 day to N assignments (worst case).

```python
    while low <= high:
        mid = (low + high) // 2
        if check(assignments, N, K, mid): result, high = mid, mid - 1
        else: low = mid + 1
    return result
```
- Standard binary search.
- If feasible at `mid` days, try fewer (search left).
- If not feasible, need more days (search right).

---

### Lines 87-97: find_min_prompts()
```python
def find_min_prompts(assignments, N, M, mode):
    check = can_complete_mode1 if mode == 1 else can_complete_mode2
    low = max(d['prompts'] for d in assignments.values())
    high = sum(d['prompts'] for d in assignments.values())
```
- Lower bound: At least max single assignment's prompts.
- Upper bound: Total prompts (one student does everything).

```python
    while low <= high:
        mid = (low + high) // 2
        if check(assignments, N, mid, M): result, high = mid, mid - 1
        else: low = mid + 1
    return result
```
- Binary search for minimum K that works.

---

### Lines 99-119: main()
```python
    parser = argparse.ArgumentParser(description='Assignment 2: Optimal scheduling')
    parser.add_argument('input_file')
    parser.add_argument('--mode', type=int, required=True, choices=[1, 2])
    parser.add_argument('--N', type=int, required=True)
```
- Sets up argument parser with required flags.

```python
    query = parser.add_mutually_exclusive_group(required=True)
    query.add_argument('--find-days', action='store_true')
    query.add_argument('--find-prompts', action='store_true')
```
- Mutually exclusive: Either find days OR find prompts.

```python
    parser.add_argument('--K', type=int)
    parser.add_argument('--M', type=int)
```
- K required for find-days, M required for find-prompts.

---

## Key Concepts

### 1. Binary Search for Optimization
- Instead of trying all values, binary search finds minimum.
- O(log N) calls to feasibility checker.
- Feasibility checker is the expensive part (backtracking).

### 2. Mode 2: Per-Student Tracking
- `student_done[i]` = set of assignments student i completed today.
- This set resets each day.
- At day end, all `completed` become shareable (`prev_done`).

### 3. Code Reuse Strategy
- `parse_input`, `has_cycle`, `can_fit`, `get_ready` are identical.
- `can_complete_mode1` is simplified `solve()` with early termination.
- `can_complete_mode2` extends mode1 with per-student tracking.

### 4. Why Early Termination?
- Assignment 1: Need ALL schedules → must explore everything.
- Assignment 2: Need existence → stop at first success.
- Huge performance gain for large inputs.

---

## Time Complexity Analysis

Let:
- **A** = number of assignments
- **N** = number of students  
- **K** = prompts per student per day
- **M** = maximum days
- **D** = average dependencies per assignment
- **P_total** = sum of all prompt requirements

### Function-wise Analysis

| Function | Time Complexity | Explanation |
|----------|-----------------|-------------|
| `parse_input()` | O(A × D) | Reads each assignment once |
| `has_cycle()` | O(A² × D) | DFS cycle detection |
| `get_ready()` | O(A × D) | Mode 1: check all assignments |
| `get_ready_mode2()` | O(A × N × D) | Mode 2: check per-student availability |
| `can_fit()` | O(N) | Linear scan through students |

### Binary Search Layer

| Query | Binary Search Range | Iterations |
|-------|---------------------|------------|
| `find_min_days()` | [1, A] | O(log A) |
| `find_min_prompts()` | [max_prompt, P_total] | O(log P_total) |

### Feasibility Check Complexity

**Mode 1: can_complete_mode1()**
- Same as Assignment 1 DFS, but with **early termination**
- Worst case: O(A! × M × N) — but rarely hit due to early exit
- Average case: Much faster, exits on first valid schedule found

**Mode 2: can_complete_mode2()**
- Additional state: `student_done` dictionary
- Per-step overhead: O(N) for copying student_done
- Worst case: O(A! × M × N²)
- The extra N factor comes from per-student tracking

### Overall Complexity

| Query | Mode 1 | Mode 2 |
|-------|--------|--------|
| find_min_days | O(log A × A! × M × N) | O(log A × A! × M × N²) |
| find_min_prompts | O(log P × A! × M × N) | O(log P × A! × M × N²) |

**Where P = P_total (sum of prompts)**

### Space Complexity

| Mode | Space | Explanation |
|------|-------|-------------|
| Mode 1 | O(A + N) | completed set + remaining tuple + recursion |
| Mode 2 | O(A + N × A) | Additional: student_done dict with sets |

**Recursion Stack:** O(A) for both modes

### Comparison: Assignment 1 vs Assignment 2

| Aspect | Assignment 1 | Assignment 2 |
|--------|-------------|--------------|
| Goal | Find ALL | Find ONE (existence) |
| DFS behavior | Explore everything | Early termination |
| Practical speed | Slow for large inputs | Much faster |
| Binary search | None | O(log X) wrapper |

### Why Mode 2 is Slower

1. **More state**: Must track per-student completions
2. **Less sharing**: Fewer assignments become "ready" each step
3. **More branching**: Must try different student assignments

**Example from tests:**
- Mode 1: 3 days (instant sharing allows parallelism)
- Mode 2: 6 days (waiting for next-day sharing creates bottleneck)

### Optimizations Applied

1. **Early termination**: Exit DFS on first success
2. **Binary search**: O(log X) vs O(X) linear search
3. **Immutable state**: Tuples/frozensets avoid explicit backtracking
4. **Pruning**: Stop when day > M
