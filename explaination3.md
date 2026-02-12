# Explanation of assg03.py - Dual-LLM Scheduling with DFS, DFBB, A*

## Overview
Extension of Assignment 2. Two LLMs: ChatGPT (even-indexed) and Gemini (odd-indexed).
Group-wide subscription of g ChatGPT + h Gemini prompts per day. Uses three search algorithms
(DFS, DFBB, A*) to find optimal schedules, comparing node counts.

---

## What's New vs Assignment 2

| Aspect | Assignment 2 | Assignment 3 |
|--------|-------------|--------------|
| LLMs | Single prompt pool | ChatGPT (even) + Gemini (odd) |
| Prompts | Per-student | Group-wide pool |
| Cost | None | c1 per ChatGPT, c2 per Gemini |
| Algorithms | Backtracking only | DFS, DFBB, A* |
| Optimization | Binary search wrapper | Search over subscription schemes |

---

## Data Flow

```
CLI Args → parse arguments (case, N, c1, c2, budget/M)
              ↓
Input File → parse_input() → assignments dict
              ↓
          has_cycle() → validation
              ↓
     ┌─ find_days(): enumerate (g,h) schemes within budget
     │    └─ For each (g,h): schedule_caseA/B → min days
     │
     └─ find_cost(): enumerate (g,h) schemes
          └─ For each (g,h): schedule_caseA/B → check feasibility
              ↓
         Print optimal value + node count comparison
```

---

## Two Cases Explained

### Case-A: One Assignment per Student per Day
- Each student picks at most one assignment per day.
- With N students, at most N assignments per day.
- Modeled as: pick a subset of ready assignments (size ≤ N), check prompt feasibility.

### Case-B: Multiple Assignments, Next-Day Sharing
- Students can do multiple assignments if group prompts available.
- Results shared only at 6am next day.
- Same student can chain: if student 0 finishes A1, they can start A3 (depends on A1) same day.
- Other students must wait until next day to use A1's result.

---

## Three Algorithms

### DFS (Depth-First Search)
- Plain backtracking.
- Explores ALL valid schedules to find optimal.
- Most nodes explored, guarantees optimal answer.

### DFBB (Depth-First Branch & Bound)
- Same as DFS but with pruning.
- Maintains `best_so_far` (best answer found so far).
- Before exploring a branch: compute heuristic lower bound.
- If `current + heuristic >= best_so_far`, prune that branch.
- Fewer nodes than DFS, same optimal answer.

### A* (Best-First Search)
- Priority queue ordered by `f(n) = g(n) + h(n)`.
- `g(n)` = days used so far.
- `h(n)` = heuristic estimate of remaining days.
- Expands most promising states first.
- Fewest nodes, same optimal answer.

---

## Heuristics

### heuristic_days(assignments, completed, g, h)
Returns lower bound on remaining days. Takes the max of:

1. **Critical Path**: Longest remaining dependency chain in the DAG.
   - Even with unlimited resources, can't do better than this.
   - Computed via recursive DFS on dependency graph.

2. **ChatGPT Capacity**: `ceil(remaining_chatgpt_prompts / g)`
   - Minimum days to consume all remaining ChatGPT prompts.

3. **Gemini Capacity**: `ceil(remaining_gemini_prompts / h)`
   - Minimum days to consume all remaining Gemini prompts.

**Why this is admissible**: Each component is a true lower bound. The max of lower bounds is still a lower bound. This guarantees A* finds optimal solution.

---

## Line-by-Line Explanation

### Lines 1-2: Imports
```python
import sys, argparse, heapq, math
from itertools import combinations
```
- `heapq` for A* priority queue.
- `combinations` for Case-A subset selection.
- `math.ceil` for capacity heuristic.

### Lines 4-15: parse_input() — Identical to assg02

### Lines 17-28: has_cycle() — Identical to assg02

### Lines 30-32: get_ready() — Identical to assg02

### Line 34-35: llm_type()
```python
def llm_type(aid):
    return 'chatgpt' if aid % 2 == 0 else 'gemini'
```
- Even assignments → ChatGPT, odd → Gemini.

### Lines 39-55: Heuristics
- `critical_path_len()`: Recursive DFS with memoization to find longest chain.
- `heuristic_days()`: Combines critical path + capacity bounds.

### Lines 60-94: Case-A Scheduler
```python
def schedule_caseA(assignments, N, g, h, M, algo='dfs'):
```
- For each day: try all combinations of up to N ready assignments.
- Check ChatGPT and Gemini prompt pools separately.
- DFS: explores all, tracks best.
- DFBB: prunes branches with heuristic.
- A*: delegates to `_astar_caseA`.

### Lines 96-125: A* for Case-A
```python
def _astar_caseA(assignments, N, g, h, M, nodes):
```
- Priority queue with `(f_score, day, state)`.
- State = `(day, completed_set)`.
- Expands by trying all valid day-combos, pushing next-day states.
- Visited set prevents re-expansion.

### Lines 129-139: get_ready_caseB() — Reused from assg02
- Adds per-student "allowed" list for dependency tracking.

### Lines 141-181: Case-B Scheduler
```python
def schedule_caseB(assignments, N, g, h, M, algo='dfs'):
```
- Key difference: `rem_g` and `rem_m` are group-wide pools (not per-student).
- `student_done[s]` tracks what student s completed today.
- Assigns to `allowed[0]` (first allowed student) — since prompts are group-wide, student choice only affects dependency chaining.

### Lines 183-229: A* for Case-B
```python
def _astar_caseB(assignments, N, g, h, M, nodes):
```
- Uses `get_day_completions()`: recursively enumerates all possible end-of-day states.
- Day-level A*: each node in PQ represents a day boundary.
- Within-day expansion happens inside `get_day_completions()`.

### Lines 232-247: enum_subscriptions()
```python
def enum_subscriptions(assignments, budget, c1, c2):
```
- Enumerates (g, h) pairs where `g*c1 + h*c2 <= budget`.
- Iterates g from 0 to budget//c1, computes max h from remaining budget.

### Lines 249-261: find_days()
- Filters schemes: `g >= max_single_chatgpt_prompt` and `h >= max_single_gemini_prompt`.
- Tests each scheme, returns the one with fewest days.

### Lines 263-280: find_cost()
- Iterates all valid (g, h) combinations.
- Skips if cost >= current best (pruning).
- Returns cheapest scheme that completes in M days.

---

## Time Complexity Analysis

### Per-Algorithm Complexity (for one (g,h) scheme)

| Algorithm | Case-A | Case-B |
|-----------|--------|--------|
| DFS | O(C(A,N)^M × M) | O(A! × M) |
| DFBB | Same worst-case, much better average | Same worst-case, much better average |
| A* | Depends on heuristic quality | Depends on heuristic quality |

Where A = number of assignments, N = students, M = max days, C(A,N) = combinations.

### Subscription Enumeration
- find_days: O(budget/c1) schemes tested
- find_cost: O(total_gpt × total_gem) schemes tested (with pruning)

### Heuristic Computation
- `critical_path_len()`: O(A²) per call (memoized within call)
- `heuristic_days()`: O(A) per call

### Node Count Comparison (observed)

| Scenario | DFS | DFBB | A* |
|----------|-----|------|----|
| Case-A, find-days | 2014 | 677 | 258 |
| Case-A, find-cost | 9127 | 8769 | 2950 |
| Case-B, find-days | 45397 | 8030 | 331 |

**A* consistently uses fewest nodes. DFBB is intermediate. DFS is worst.**

### Space Complexity
| Algorithm | Space |
|-----------|-------|
| DFS | O(A) recursion stack |
| DFBB | O(A) recursion stack |
| A* | O(2^A) for priority queue + visited set |

A* trades space for time.

---

## Why It Works

1. **Heuristic is admissible**: Never overestimates remaining days → A* is optimal.
2. **DFBB prunes correctly**: Only prunes when lower bound proves branch can't beat best.
3. **DFS is exhaustive**: Explores everything, guarantees finding optimal (but slowly).
4. **Group-wide prompts**: Simplifies can_fit to pool checks instead of per-student.
5. **First-allowed-student assignment**: In Case-B, since prompts are group-wide, which student gets assigned only matters for same-day dependency chaining — first allowed student is sufficient.
