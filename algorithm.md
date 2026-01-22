# Assignment Scheduler: Algorithm Specification

**Course**: CS5205 - Advanced Artificial Intelligence Lab  
**Assignment**: 1 - State Space Search

---

## 1. Overview

This document provides a formal specification of the algorithm used to solve the assignment scheduling problem. The algorithm is a **Depth-First Search (DFS) with Backtracking**, chosen for its memory efficiency and suitability for exhaustive enumeration.

---

## 2. Notation and Definitions

### 2.1 Input Variables

| Symbol | Type | Description |
|--------|------|-------------|
| N | Integer | Number of students in the group |
| K | Integer | Maximum prompts per student per day |
| M | Integer | Maximum number of days allowed |
| A | Set | Set of all assignments |

### 2.2 Assignment Structure

Each assignment a ∈ A is defined as:

```
a = (id, prompts, dependencies)
```

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier |
| prompts | Integer | Number of prompts required |
| dependencies | Set of Integer | IDs of prerequisite assignments |

### 2.3 State Definition

The search state is represented as a tuple:

```
S = (day, completed, remaining)
```

| Component | Type | Domain | Purpose |
|-----------|------|--------|---------|
| day | Integer | [1, M+1] | Tracks current day for limit checking |
| completed | Set | ⊆ {a.id : a ∈ A} | Determines which assignments are ready |
| remaining | Tuple | (r₁, ..., rₙ) where rᵢ ∈ [0, K] | Determines if an assignment can be assigned |

**Justification for this representation**:
- These three components constitute the minimum information needed to determine all valid next actions
- The representation is path-independent: how the state was reached does not affect future decisions
- Immutable types enable hashing for efficient duplicate detection

---

## 3. Core Algorithm

### 3.1 Main Procedure

```
ALGORITHM: AssignmentScheduler

INPUT:  N, K, M, A (as defined above)
OUTPUT: List of all valid schedules with Packed/Relaxed labels

BEGIN
    // Phase 1: Feasibility Checks
    IF ∃a ∈ A : a.prompts > K THEN
        RETURN Error("Assignment too large")
    IF HasCycle(A) THEN
        RETURN Error("Cyclic dependency")
    IF Σ(a.prompts : a ∈ A) > M × N × K THEN
        RETURN Error("Insufficient capacity")
    
    // Phase 2: Initialize Search
    solutions ← empty list
    S₀ ← (day=1, completed=∅, remaining=(K,...,K))
    
    // Phase 3: Execute DFS
    DFS(S₀, today_work=[], schedule=[], is_packed=True, solutions)
    
    // Phase 4: Remove Duplicates
    solutions ← Deduplicate(solutions)
    
    RETURN solutions
END
```

### 3.2 DFS Procedure

The DFS procedure is the core of the algorithm. It recursively explores all valid paths through the state space.

```
PROCEDURE: DFS(S, today_work, schedule, is_packed, solutions)

INPUT:
    S = (day, completed, remaining) -- Current state
    today_work                      -- Assignments done so far today
    schedule                        -- Completed days so far
    is_packed                       -- Whether all previous days were fully utilized
    solutions                       -- Accumulator for valid schedules

BEGIN
    // ─────────────────────────────────────────────────────────────
    // BASE CASE 1: Goal Reached
    // All assignments completed - this is a valid schedule
    // ─────────────────────────────────────────────────────────────
    IF |completed| = |A| THEN
        final_schedule ← schedule
        IF today_work ≠ [] THEN
            final_schedule ← final_schedule ⊕ [today_work]
        solutions.add((final_schedule, is_packed))
        RETURN
    
    // ─────────────────────────────────────────────────────────────
    // BASE CASE 2: Day Limit Exceeded (Pruning)
    // This branch cannot lead to a valid solution
    // ─────────────────────────────────────────────────────────────
    IF day > M THEN
        RETURN
    
    // ─────────────────────────────────────────────────────────────
    // Compute Ready Assignments
    // An assignment is ready iff:
    //   (1) It has not been completed
    //   (2) All its dependencies have been completed
    // ─────────────────────────────────────────────────────────────
    ready ← {a ∈ A : a.id ∉ completed ∧ a.dependencies ⊆ completed}
    
    // ─────────────────────────────────────────────────────────────
    // TRANSITION TYPE 1: Assign a Ready Assignment
    // For each ready assignment that fits, explore that branch
    // ─────────────────────────────────────────────────────────────
    FOR EACH a ∈ ready DO
        (can_fit, new_remaining, student) ← TryFit(a, remaining)
        IF can_fit THEN
            new_S ← (day, completed ∪ {a.id}, new_remaining)
            DFS(new_S, today_work ⊕ [a.id], schedule, is_packed, solutions)
    
    // ─────────────────────────────────────────────────────────────
    // TRANSITION TYPE 2: End the Current Day
    // Only valid if at least one assignment was done today
    // ─────────────────────────────────────────────────────────────
    IF today_work ≠ [] THEN
        // Determine if this is a "packed" or "relaxed" transition
        // Packed: no ready assignment could fit (forced to end day)
        // Relaxed: at least one ready assignment could fit but we chose to end
        could_do_more ← ∃a ∈ ready : CanFit(a, remaining)
        new_is_packed ← is_packed ∧ ¬could_do_more
        
        // Reset state for new day
        new_S ← (day + 1, completed, (K, K, ..., K))
        new_schedule ← schedule ⊕ [today_work]
        DFS(new_S, [], new_schedule, new_is_packed, solutions)
END
```

**Analysis of the DFS procedure**:

1. **Exhaustiveness**: Every valid transition is explored—both assigning each ready assignment and ending the day. This ensures completeness.

2. **Pruning**: The check `day > M` immediately terminates branches that cannot yield valid solutions.

3. **State independence**: The procedure depends only on the current state, not on how it was reached.

---

## 4. Supporting Procedures

### 4.1 TryFit: First-Fit Bin Packing

This procedure attempts to find a student who can accommodate an assignment.

```
PROCEDURE: TryFit(a, remaining)

INPUT:
    a         -- Assignment to fit
    remaining -- Current remaining prompts per student (r₁, ..., rₙ)

OUTPUT:
    (success, new_remaining, student_index)

BEGIN
    FOR i ← 0 TO N-1 DO
        IF remaining[i] ≥ a.prompts THEN
            new_remaining ← copy(remaining)
            new_remaining[i] ← remaining[i] - a.prompts
            RETURN (True, new_remaining, i)
    RETURN (False, remaining, -1)
END
```

**Complexity**: O(N)

**Justification for First-Fit**:
- The goal is to determine whether an assignment *can* be placed, not to optimize placement
- Optimal bin-packing is NP-hard; First-Fit provides a polynomial-time heuristic
- Since DFS explores all valid branches, suboptimal fitting on one branch does not prevent finding all solutions

### 4.2 HasCycle: Cycle Detection

A cycle in the dependency graph would make the problem unsolvable. This procedure detects cycles using DFS with three-color marking.

```
PROCEDURE: HasCycle(A)

INPUT:  A -- Set of assignments with dependencies
OUTPUT: True if a cycle exists, False otherwise

BEGIN
    color ← {a.id → WHITE : a ∈ A}  // WHITE = unvisited
    
    PROCEDURE Visit(node)
        color[node] ← GRAY  // GRAY = in current path
        FOR EACH a ∈ A such that node ∈ a.dependencies DO
            IF color[a.id] = GRAY THEN
                RETURN True  // Back edge found
            IF color[a.id] = WHITE THEN
                IF Visit(a.id) THEN RETURN True
        color[node] ← BLACK  // BLACK = fully explored
        RETURN False
    
    FOR EACH a ∈ A DO
        IF color[a.id] = WHITE THEN
            IF Visit(a.id) THEN RETURN True
    RETURN False
END
```

**Complexity**: O(|A| + |E|) where E is the number of dependency edges

### 4.3 Deduplicate: Remove Equivalent Schedules

Different DFS paths may produce schedules that differ only in the order of assignments within a day. Since students are treated as equivalent, such schedules are considered duplicates.

```
PROCEDURE: Deduplicate(schedules)

INPUT:  List of (schedule, is_packed) pairs
OUTPUT: List with duplicates removed

BEGIN
    seen ← empty hash set
    result ← empty list
    
    FOR EACH (schedule, is_packed) ∈ schedules DO
        // Normalize by sorting assignments within each day
        normalized ← tuple(sort(day) for day in schedule)
        key ← (normalized, is_packed)
        
        IF key ∉ seen THEN
            seen.add(key)
            result.add((schedule, is_packed))
    
    RETURN result
END
```

**Complexity**: O(S × D × A log A) where S = schedules, D = days, A = assignments

---

## 5. Complexity Analysis

### 5.1 Time Complexity

The algorithm explores a search tree where:
- Each node represents a state
- Branching factor is at most |A| (trying each ready assignment)
- Depth is at most |A| + M (each assignment done once, plus day transitions)

| Component | Complexity |
|-----------|------------|
| Tree size (worst case) | O(|A|!) |
| Per-node: find ready | O(|A| × max_deps) |
| Per-node: try fit | O(N) |
| Deduplication | O(S × |A| log |A|) |

**Worst-case total**: O(|A|! × N)

**In practice**: Dependency and capacity constraints prune most branches, making the search tractable.

### 5.2 Space Complexity

| Component | Complexity |
|-----------|------------|
| Recursion stack depth | O(|A| + M) |
| State per stack frame | O(|A| + N) |
| Solution storage | O(S × D × A) |

**Total**: O(|A|² + S × |A|)

---

## 6. Correctness Proof

### 6.1 Theorem: Completeness

**Statement**: Every valid schedule is found by the algorithm.

**Proof**:
- Let σ be any valid schedule (a sequence of days, each containing assignments)
- At each step in σ, the corresponding transition is either:
  - Assigning a ready assignment (covered by the first FOR loop)
  - Ending a day (covered by the IF block for day advancement)
- Since DFS explores all such transitions, the path corresponding to σ is explored
- Therefore, σ is added to solutions ∎

### 6.2 Theorem: Soundness

**Statement**: Every schedule output by the algorithm is valid.

**Proof**:
- A schedule is added to solutions only when |completed| = |A| (BASE CASE 1)
- Each assignment added to completed has:
  - Dependencies satisfied (checked in ready computation)
  - Capacity available (checked by TryFit)
- Day counter never exceeds M (pruned in BASE CASE 2)
- Therefore, all output schedules satisfy all constraints ∎

### 6.3 Theorem: No Duplicates

**Statement**: The output contains no duplicate schedules.

**Proof**:
- Deduplicate uses a hash set with normalized schedule as key
- Two schedules have the same key iff they have the same assignments on each day (order-independent)
- Therefore, each unique schedule appears exactly once ∎

---

## 7. Example Execution

**Input**:
```
N = 2, K = 5, M = 2
Assignments: A₁(2 prompts, no deps), A₂(3 prompts, depends on A₁)
```

**Execution Trace**:

```
Initial: S₀ = (day=1, completed=∅, remaining=(5,5))

├── Try A₁ (ready, fits student 0)
│   S₁ = (1, {1}, (3,5)), today=[1]
│   │
│   ├── Try A₂ (now ready, fits student 0)
│   │   S₂ = (1, {1,2}, (0,5)), today=[1,2]
│   │   │
│   │   └── BASE CASE 1: All done!
│   │       Output: [[1,2]], is_packed=True
│   │
│   └── End day (could_do_more=True since A₂ fits)
│       S₃ = (2, {1}, (5,5)), schedule=[[1]], is_packed=False
│       │
│       └── Try A₂
│           S₄ = (2, {1,2}, (2,5)), today=[2]
│           │
│           └── BASE CASE 1: All done!
│               Output: [[1],[2]], is_packed=False
│
└── End day (today_work empty, skipped)
```

**Final Output**:
```
Schedule 1 (Packed):  Day 1: A1, A2
Schedule 2 (Relaxed): Day 1: A1 | Day 2: A2
```

---

## 8. Conclusion

The algorithm specification presented in this document formalizes the DFS with Backtracking approach to the assignment scheduling problem. Key properties include:

- **Completeness**: All valid schedules are guaranteed to be found
- **Soundness**: All output schedules are guaranteed to be valid
- **Polynomial per-node cost**: Each node in the search tree is processed in O(|A| × N) time
- **Effective pruning**: Constraints significantly reduce the explored state space

The formal specification enables verification of correctness and provides a foundation for implementation.
