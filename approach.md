# Assignment Scheduler: Approach and Design Analysis

**Course**: CS5205 - Advanced Artificial Intelligence Lab  
**Assignment**: 1 - State Space Search

---

## 1. Problem Analysis

### 1.1 Problem Statement

The problem involves scheduling assignments for a group of N students who must complete their work using an LLM (Large Language Model) assistant. The following constraints govern the problem:

| Constraint | Description | Implication |
|------------|-------------|-------------|
| **Prompt Limit (K)** | Each student can send at most K prompts per day | Limits work capacity per student per day |
| **Daily Reset** | Prompt counts reset at the start of each day | Unused prompts cannot be carried over |
| **Dependencies** | Some assignments require others to be completed first | Creates a partial ordering on assignments |
| **Day Limit (M)** | All assignments must be completed within M days | Defines the feasibility boundary |
| **Atomicity** | An assignment cannot be split across days | Must fit entirely within a student's daily capacity |
| **Non-transferability** | Students cannot share prompts | Each student's capacity is independent |

### 1.2 Objective

The goal is to enumerate **all valid schedules** that satisfy these constraints. This is fundamentally different from finding a single optimal schedule—the requirement is for exhaustive enumeration.

---

## 2. State Space Formulation

### 2.1 Why State Space Search?

The problem exhibits characteristics that make it suitable for state space search:

1. **Discrete decisions**: At any point, there is a finite set of valid actions (assign a ready assignment or end the day)
2. **Sequential nature**: Decisions must respect temporal ordering (dependencies, day progression)
3. **Complete enumeration required**: All valid end states must be discovered, not just one

Alternative approaches such as greedy algorithms or heuristic search are unsuitable because they do not guarantee finding all solutions.

### 2.2 State Representation

The state is represented as a tuple with three components:

```
State = (day, completed, remaining)
```

| Component | Type | Description | Justification |
|-----------|------|-------------|---------------|
| `day` | Integer | Current day (1-indexed) | Required to check against the M-day limit |
| `completed` | Set of Integers | IDs of finished assignments | Required to determine which assignments are now "ready" (dependencies satisfied) |
| `remaining` | Tuple of Integers | Prompts remaining for each student today | Required to check if an assignment can fit within a student's capacity |

**Why this representation?**

- **Minimality**: These three components are the minimum information needed to determine valid next actions. Removing any component would make it impossible to correctly identify valid transitions.

- **Hashability**: Using immutable types (`frozenset` for completed, `tuple` for remaining) allows states to be used as dictionary keys for duplicate detection.

- **Independence from path**: The state captures only "what matters now," not how the system arrived at this point. This is essential for state space search—two different paths leading to the same state are equivalent.

### 2.3 Initial and Goal States

**Initial State**:
```
(day=1, completed=∅, remaining=(K, K, ..., K))
```
- Day 1, no assignments completed, all N students have full K prompts

**Goal States**:
```
(day ≤ M, completed = all_assignments, remaining = any)
```
- All assignments completed within the day limit

### 2.4 State Transitions

Two types of transitions are possible:

**Type 1: Assign an Assignment**
```
(d, C, R) → (d, C ∪ {a}, R')
```
Preconditions:
- Assignment `a` is not in `C` (not yet completed)
- All dependencies of `a` are in `C` (prerequisites satisfied)
- Some student `i` has `R[i] ≥ a.prompts` (capacity available)

Effect:
- Assignment added to completed set
- Corresponding student's remaining prompts reduced

**Type 2: End the Day**
```
(d, C, R) → (d+1, C, (K, K, ..., K))
```
Preconditions:
- At least one assignment was done on day `d` (otherwise, infinite loop possible)

Effect:
- Day counter incremented
- All students' prompts reset to K

---

## 3. Algorithm Design

### 3.1 Algorithm Selection

Several algorithmic approaches were considered:

| Approach | Suitability | Reason |
|----------|-------------|--------|
| **Brute Force Permutation** | Poor | Generates all A! orderings, most of which are invalid due to dependencies |
| **Breadth-First Search (BFS)** | Possible | Finds shortest solutions first, but requires storing all states at each level—memory intensive |
| **Depth-First Search (DFS)** | Selected | Memory efficient, naturally explores complete paths before backtracking |
| **Constraint Satisfaction (CSP)** | Possible | Powerful but obscures the algorithm—less suitable for educational purposes |

**DFS with Backtracking is selected** for the following reasons:

1. **Memory Efficiency**: Only the current path needs to be stored, not all explored states
2. **Natural fit for exhaustive enumeration**: The recursive structure naturally collects all valid paths
3. **Effective pruning**: Invalid branches (day > M) are detected and abandoned immediately
4. **Algorithmic transparency**: The logic is explicit and understandable

### 3.2 The Bin-Packing Sub-Problem

Within each day, assigning assignments to students is a variant of the **bin-packing problem**:
- **Bins**: Students, each with capacity K (or remaining capacity)
- **Items**: Assignments, each with a "size" (prompt count)

For this sub-problem, a **First-Fit** strategy is employed:

```
For each assignment to be placed:
    For each student in order:
        If student has sufficient remaining capacity:
            Assign to this student
            Break
```

**Why First-Fit instead of optimal bin-packing?**

1. **Optimality is unnecessary**: The goal is to determine whether assignments *can* fit, not to minimize bins
2. **NP-hardness**: Optimal bin-packing requires exponential time; First-Fit is O(N)
3. **Exhaustive search compensates**: DFS explores all valid combinations anyway—suboptimal packing on one path does not prevent finding all solutions

### 3.3 Packed vs. Relaxed Classification

Each schedule is classified as either **Packed** or **Relaxed**:

| Classification | Definition | Characteristic |
|----------------|------------|----------------|
| **Packed** | Every day-end transition occurred only when no ready assignment could fit | Days were fully utilized |
| **Relaxed** | At least one day-end transition occurred when more work could have been done | Days were not fully utilized |

**Why this classification?**

- Packed schedules represent "optimal" resource utilization
- Relaxed schedules may be valid but use more days than necessary
- The classification allows immediate identification of the most efficient schedules

---

## 4. Feasibility Analysis

Before executing the search, feasibility checks are performed to avoid wasted computation.

### 4.1 Individual Assignment Check

**Check**: For each assignment `a`, verify that `a.prompts ≤ K`

**Rationale**: If any single assignment requires more prompts than a student has per day, that assignment can never be completed (since assignments cannot be split across days).

### 4.2 Total Capacity Check

**Check**: Verify that `Σ(a.prompts) ≤ M × N × K`

**Rationale**: The total prompts needed must not exceed the total capacity available across all students and all days. This is a necessary (but not sufficient) condition.

### 4.3 Cycle Detection

**Check**: Verify that the dependency graph is acyclic

**Rationale**: A cycle in dependencies (A requires B, B requires A) makes completion impossible. The graph must be a DAG (Directed Acyclic Graph).

### 4.4 Note on Dependency Depth

The "dependency depth" (longest chain of dependencies) is computed and reported, but **is not used as a feasibility constraint**. 

**Reason**: Multiple assignments in a dependency chain can potentially be completed on the same day. For example, with sufficient students:
- Student 1 completes A1, making A2 ready
- Student 2 completes A2, making A3 ready
- This cascading can continue within a single day

Thus, dependency depth does not directly limit the minimum number of days required.

---

## 5. Correctness Analysis

### 5.1 Completeness

**Claim**: The algorithm finds all valid schedules.

**Argument**: 
- At each state, all valid transitions are explored (every ready assignment that fits, plus day-end if applicable)
- No valid transition is omitted
- Therefore, every reachable goal state is discovered

### 5.2 Soundness

**Claim**: Every schedule output is valid.

**Argument**:
- Assignments are only added when dependencies are satisfied (checked via `completed` set)
- Assignments are only assigned when capacity exists (checked via `remaining` tuple)
- Schedules are only output when day ≤ M (checked before adding to solutions)

### 5.3 Uniqueness

**Claim**: No duplicate schedules appear in the output.

**Argument**:
- Schedules are normalized by sorting assignments within each day
- A hash set tracks seen normalized schedules
- Only unseen schedules are added to the output

---

## 6. Complexity Analysis

### 6.1 Time Complexity

| Component | Complexity | Explanation |
|-----------|------------|-------------|
| Branching factor | O(A) | At most A assignments can be ready at any state |
| Tree depth | O(A + M) | Each assignment is completed once, plus up to M day transitions |
| Per-node operations | O(A × N) | Checking ready assignments and fitting capacity |

**Worst-case**: O(A! × M × N) — exponential in the number of assignments

**Practical performance**: Dependency constraints and capacity limits prune most branches, making the search tractable for moderate problem sizes.

### 6.2 Space Complexity

| Component | Complexity | Explanation |
|-----------|------------|-------------|
| Recursion stack | O(A + M) | Maximum depth of DFS |
| State storage | O(A + N) per frame | Completed set and remaining tuple |
| Solution storage | O(S × A) | Where S is the number of solutions |

---

## 7. Implementation Notes

### 7.1 Module Structure

The implementation is organized into focused modules:

| Module | Responsibility |
|--------|----------------|
| `models.py` | Data structures (Assignment, State) |
| `parser.py` | Input file parsing |
| `graph.py` | Dependency graph operations |
| `feasibility.py` | Pre-search validation |
| `solver.py` | Core DFS algorithm |
| `main.py` | CLI interface |

This separation follows the **Single Responsibility Principle**, making the code easier to understand, test, and maintain.

### 7.2 Key Design Choices in Implementation

| Choice | Implementation | Reason |
|--------|----------------|--------|
| Completed set | `frozenset` | Immutable, hashable for state comparison |
| Remaining prompts | `tuple` | Immutable, hashable for state comparison |
| Ready assignments | Computed on-demand | Avoids maintaining separate data structure |
| Duplicate removal | Post-processing | Simpler than preventing duplicates during search |

---

## 8. Conclusion

The assignment scheduling problem is formulated as a state space search problem, solved using DFS with backtracking. Key aspects of the solution include:

1. **State representation** designed for minimality and hashability
2. **First-Fit bin-packing** for efficient within-day assignment
3. **Feasibility pre-checks** to fail fast on impossible inputs
4. **Packed/Relaxed classification** to identify optimal schedules
5. **Formal correctness arguments** ensuring completeness and soundness

The approach demonstrates how constraint-based scheduling problems can be systematically solved using fundamental AI search techniques.
