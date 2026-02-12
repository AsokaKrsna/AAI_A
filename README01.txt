CS5205 - Advanced Artificial Intelligence Lab
Assignment 1 | Assignment Scheduler | State Space 1

## How to Run

```bash
python assg01.py <input-file> <max-days>

or

python3 assg01.py <input-file> <max-days>     # if facing error
```

Example:
```bash
python assg01.py ProvidedInput.txt 5
```

## Input Format

```
N <students>              -- Number of students
K <prompts>               -- Prompts per student per day  
A <id> <prompts> <deps> 0 -- Assignment (0 = end of deps)
```

Example:
```
N 3
K 5
A 1 2 0
A 2 4 1 0
```

## Problem Summary

| Constraint | Description |
|------------|-------------|
| N students | Each has K prompts/day |
| Dependencies | Some assignments require others first |
| Day limit M | Must finish within M days |
| Atomicity | Cannot split assignment across days |

**Goal**: Find ALL valid schedules


## Approach: State Space Search

### State Representation
```
State = (day, completed_set, remaining_prompts_per_student)
```

### Why DFS with Backtracking?
- Memory efficient (only stores current path)
- Natural fit for finding ALL solutions
- Constraints prune invalid branches early

### Transitions
1. **Assign**: Add ready assignment to a student with capacity
2. **End Day**: Reset all prompts, increment day


## Algorithm

```
DFS(day, completed, remaining, today_work, schedule):
    if all_done: save(schedule); return
    if day > M: return  # Prune
    
    ready = {a : dependencies ⊆ completed}
    
    for a in ready:
        if fits(a, remaining):
            DFS(same day, a added, reduced capacity)
    
    if today_work not empty:
        DFS(day+1, completed, reset capacity)
```

### Key Functions
| Function | Purpose |
|----------|---------|
| `get_ready()` | Find assignments with satisfied deps |
| `can_fit()` | First-fit bin packing for students |
| `has_cycle()` | DFS cycle detection (feasibility) |


## Complexity

| Aspect | Complexity |
|--------|------------|
| Time (worst) | O(A! × M × N) |
| Space | O(A + S×D) |
| Practical | Constraints prune most branches |


## Feasibility Checks

1. No assignment needs more than K prompts
2. Total prompts ≤ M × N × K
3. No cyclic dependencies


## Output Format

```
Found 650 valid schedule(s):

Schedule 1:
  Day 1: A1, A2, A5
  Day 2: A3, A4, A6, A7, A8

Schedule 2:
  Day 1: A1, A2, A5
  Day 2: A3, A4, A6, A7
  Day 3: A8
...
```

## Files

| File | Description |
|------|-------------|
| `assg01.py` | Main implementation |
| `ProvidedInput.txt` | Sample input |
| `README.md` | This file |


## Requirements

- Python 3.7+
- No external dependencies