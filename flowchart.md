## 2. System Architecture Flowchart

This flowchart illustrates the overall system pipeline from input processing to output generation.

---

## 3. DFS Algorithm Flowchart

This flowchart details the recursive DFS procedure that forms the core of the search algorithm.


---

## 4. Feasibility Check Flowchart

This flowchart shows the three pre-search validation checks performed before executing the DFS.


---

## 5. State Transition Diagram

This state diagram models the valid transitions in the state space.


---

## 6. First-Fit Bin Packing Flowchart

This flowchart illustrates the TryFit procedure used to assign an assignment to a student.



**Analysis**: The First-Fit strategy is employed because:
- Determining whether an assignment can be placed is sufficient; optimality is not required
- Time complexity is O(N), compared to O(2^N) for optimal bin-packing
- The exhaustive DFS naturally explores all valid placements

---

## 7. Cycle Detection Flowchart

This flowchart shows the three-color DFS algorithm used for cycle detection.

---

## 8. Packed vs Relaxed Classification

This flowchart shows how the algorithm determines whether a day-end transition is "packed" or "relaxed".



**Interpretation**:
- A schedule is classified as **Packed** if and only if every day-end transition was forced (no ready assignment could fit)
- A schedule is classified as **Relaxed** if at least one day-end transition occurred when more work could have been done
- This classification enables immediate identification of optimally-packed schedules

---
