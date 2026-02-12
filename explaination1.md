# Explanation of assg01.py - Assignment Scheduling Solver

## Overview
This program finds ALL valid schedules to complete a set of assignments with dependencies,
given N students, K prompts per student per day, and M maximum days.

---

## Data Flow

```
Input File → parse_input() → assignments dict
                                    ↓
                            has_cycle() → validation
                                    ↓
                              solve() → DFS backtracking
                                    ↓
                         Deduplicate → Print all valid schedules
```

---

## Line-by-Line Explanation

### Lines 1-2: Imports
```python
import sys
```
- `sys` module for command line arguments and exit functionality.

---

### Lines 3-16: parse_input()
```python
def parse_input(filename):
    N, K, assignments = None, None, {}
```
- Initializes N (students), K (prompts/day), and empty assignments dict.

```python
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'): continue
```
- Opens file, iterates lines, strips whitespace, skips empty/comment lines.

```python
            parts = line.split()
            if parts[0].upper() == 'N': N = int(parts[1])
            elif parts[0].upper() == 'K': K = int(parts[1])
```
- Parses N and K values from lines starting with 'N' or 'K'.

```python
            elif parts[0].upper() == 'A':
                aid, prompts = int(parts[1]), int(parts[2])
                deps = frozenset(int(d) for d in parts[3:] if int(d) != 0)
                assignments[aid] = {'prompts': prompts, 'deps': deps}
```
- For assignment lines: extracts ID, prompt count, and dependencies.
- `frozenset` makes dependencies hashable (immutable set).
- `0` is terminator, filtered out.

---

### Lines 18-29: has_cycle()
```python
def has_cycle(assignments):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {aid: WHITE for aid in assignments}
```
- Uses 3-color DFS for cycle detection:
  - WHITE = unvisited
  - GRAY = currently visiting (in recursion stack)
  - BLACK = fully processed

```python
    def dfs(node):
        color[node] = GRAY
        for other, data in assignments.items():
            if node in data['deps']:
```
- Marks node as GRAY (in progress).
- Finds all assignments that depend on current node.

```python
                if color[other] == GRAY: return True
                if color[other] == WHITE and dfs(other): return True
        color[node] = BLACK
        return False
```
- If dependent is GRAY → cycle detected (back edge).
- If dependent is WHITE → recursively visit.
- After all dependents processed, mark BLACK.

```python
    return any(color[a] == WHITE and dfs(a) for a in assignments)
```
- Starts DFS from any unvisited node, returns True if any cycle found.

---

### Lines 31-34: get_ready()
```python
def get_ready(completed, assignments):
    return [aid for aid, data in assignments.items() 
            if aid not in completed and data['deps'].issubset(completed)]
```
- Returns assignments that:
  1. Are not yet completed
  2. Have all dependencies already completed
- `issubset()` checks if all deps are in completed set.

---

### Lines 36-41: can_fit()
```python
def can_fit(prompts, remaining):
    for i, r in enumerate(remaining):
        if r >= prompts:
            return True, remaining[:i] + (r - prompts,) + remaining[i+1:]
    return False, remaining
```
- Tries to assign an assignment to any student with enough prompts.
- `remaining` is a tuple of remaining prompts for each student.
- Returns (success, updated_remaining_tuple).
- Uses tuple slicing to create new immutable tuple (important for backtracking).

---

### Lines 43-72: solve() - Core DFS with Backtracking
```python
def solve(assignments, N, K, M):
    solutions = []
    total = len(assignments)
```
- `solutions` accumulates all valid schedules.
- `total` is target: all assignments must be completed.

```python
    def dfs(day, completed, remaining, today, schedule):
        if len(completed) == total:
            final = schedule + ([today[:]] if today else [])
            solutions.append(final)
            return
```
- **Base case**: All completed → save schedule.
- `today[:]` creates a copy of today's assignments.

```python
        if day > M: return
```
- **Pruning**: Exceeded allowed days → abandon branch.

```python
        ready = get_ready(completed, assignments)
        for aid in ready:
            fits, new_rem = can_fit(assignments[aid]['prompts'], remaining)
            if fits:
                dfs(day, completed | {aid}, new_rem, today + [aid], schedule)
```
- Get ready assignments, try assigning each.
- `completed | {aid}` creates new set with aid added.
- Recursively explore this branch.

```python
        if today:  # Try ending day
            dfs(day + 1, completed, tuple([K]*N), [], schedule + [today[:]])
```
- If we did work today, try ending the day.
- Reset prompts to K for all students.
- Move today's work to schedule.

```python
    dfs(1, frozenset(), tuple([K]*N), [], [])
```
- Start DFS: Day 1, nothing completed, full prompts, empty today, empty schedule.

```python
    # Remove duplicates
    seen, unique = set(), []
    for sched in solutions:
        key = tuple(tuple(sorted(day)) for day in sched)
        if key not in seen:
            seen.add(key)
            unique.append([sorted(day) for day in sched])
    return unique
```
- Deduplicates schedules since student order doesn't matter.
- Sorts each day's assignments to create canonical form.

---

### Lines 74-101: main()
- Validates command line arguments.
- Parses input file.
- Validates feasibility (K >= max prompts, no cycles).
- Runs solver and prints all valid schedules.

---

## Key Concepts

### 1. Backtracking
- Explores all possible assignment orderings.
- Backtracks when a branch fails (exceeds days).
- Natural recursion: each call explores one decision point.

### 2. State Representation
- `completed`: frozenset of done assignments (immutable for hashing).
- `remaining`: tuple of prompts left per student (immutable for backtracking).
- `today`: list of assignments done today.
- `schedule`: list of days, each day is list of assignments.

### 3. Why Tuples/Frozensets?
- Immutability ensures backtracking works correctly.
- Each recursive call gets its own state copy.
- No need to explicitly undo changes.

### 4. Deduplication
- Same assignments on same day = same schedule (students are identical).
- Sorting creates canonical form for comparison.

---

## Time Complexity Analysis

Let:
- **A** = number of assignments
- **N** = number of students  
- **K** = prompts per student per day
- **M** = maximum days allowed
- **D** = average dependencies per assignment

### Function-wise Analysis

| Function | Time Complexity | Explanation |
|----------|-----------------|-------------|
| `parse_input()` | O(A × D) | Reads each assignment and its dependencies once |
| `has_cycle()` | O(A² × D) | DFS visits each node, checks all edges |
| `get_ready()` | O(A × D) | Iterates all assignments, checks dependency subset |
| `can_fit()` | O(N) | Linear scan through N students |

### Core DFS Complexity: solve()

**State Space Size:**
- Each assignment can be: not done, done today, or done on a previous day
- At each state, we can assign any ready assignment to any student with capacity

**Worst Case:** O(A! × M × N)
- A! possible orderings of assignments
- M possible day boundaries
- N student choices for each assignment

**Practical Complexity:** Much better due to:
1. **Pruning**: Stops when day > M
2. **Dependency constraints**: Only "ready" assignments can be tried
3. **Capacity constraints**: Only students with enough prompts

**Tighter Bound:** O(C(A, k₁) × C(A-k₁, k₂) × ... × N^A)
- Where k₁, k₂, ... are assignments per day
- Still exponential, but significantly reduced

### Space Complexity

| Component | Space | Explanation |
|-----------|-------|-------------|
| `completed` | O(A) | Frozenset of completed assignments |
| `remaining` | O(N) | Tuple of prompts per student |
| `today` | O(A) | List of today's assignments |
| `schedule` | O(A) | List of days with assignments |
| Recursion stack | O(A) | Maximum depth = number of assignments |
| Solutions list | O(S × A) | S = number of solutions |

**Total Space:** O(A² + S × A)

### Why Exponential is Acceptable

1. **Problem is NP-hard**: No polynomial algorithm exists (reduction from bin packing)
2. **Small inputs**: Typical A ≤ 20, making exhaustive search feasible
3. **Pruning effectiveness**: Real-world instances have structure that cuts search space
4. **Finding ALL solutions**: Inherently requires exploring entire valid space
