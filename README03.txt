README - Assignment 3

================================================================================
HOW TO RUN
================================================================================

Usage:
    python assg03.py <input-file> --case <A|B> --N <students> --c1 <cost> --c2 <cost> [--find-days --budget <B>] [--find-cost --M <days>] [--algo <dfs|dfbb|astar|all>]

--------------------------------------------------------------------------------
CASES
--------------------------------------------------------------------------------

Case A: One assignment per student per day
    - Each student can solve at most one assignment per day.
    - With N students, at most N assignments per day.

Case B: Multiple assignments per student, next-day sharing
    - A student can solve multiple assignments if group has sufficient prompts.
    - Solutions are shared only at 6am the next day.
    - Same student can chain dependent assignments within a day.

--------------------------------------------------------------------------------
LLM ASSIGNMENT
--------------------------------------------------------------------------------

Even-indexed assignments (A2, A4, A6, ...) → ChatGPT (cost c1 per prompt)
Odd-indexed assignments  (A1, A3, A5, ...) → Gemini  (cost c2 per prompt)

Subscription is group-wide: g ChatGPT + h Gemini prompts per day.
Daily cost = g * c1 + h * c2.

--------------------------------------------------------------------------------
QUERIES
--------------------------------------------------------------------------------

--find-days: Find minimum days to complete all assignments
    Requires: --budget (maximum daily subscription cost)
    Finds best (g, h) split within budget that minimizes days.

--find-cost: Find minimum daily subscription cost
    Requires: --M (number of days available)
    Finds cheapest (g, h) that allows completion in M days.

--------------------------------------------------------------------------------
ALGORITHMS
--------------------------------------------------------------------------------

--algo dfs    : Plain depth-first search (exhaustive)
--algo dfbb   : Depth-first branch and bound (pruned)
--algo astar  : A* best-first search (heuristic-guided)
--algo all    : Run all three and compare node counts (default)

--------------------------------------------------------------------------------
EXAMPLES
--------------------------------------------------------------------------------

Case A, find minimum days with budget 50:
    python assg03.py input01.txt --case A --find-days --N 3 --budget 50 --c1 5 --c2 3

Case A, find minimum cost for 6 days:
    python assg03.py input01.txt --case A --find-cost --N 3 --M 6 --c1 5 --c2 3

Case B, find minimum days with budget 50 (DFBB only):
    python assg03.py input01.txt --case B --find-days --N 3 --budget 50 --c1 5 --c2 3 --algo dfbb

Case B, find minimum cost for 4 days (all algorithms):
    python assg03.py input01.txt --case B --find-cost --N 3 --M 4 --c1 5 --c2 3 --algo all

--------------------------------------------------------------------------------
INPUT FILE FORMAT
--------------------------------------------------------------------------------

% Comment lines start with %
N 3        (ignored - use --N from command line)
K 5        (ignored - use --budget or --M from command line)
A <id> <prompt-count> <dep1> <dep2> ... 0

--------------------------------------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------------------------------------

Case A | N=3 | c1=5 c2=3
--------------------------------------------------
[  DFS] Min Days: 6 | Scheme: g=7,h=5 | Nodes: 2014
[ DFBB] Min Days: 6 | Scheme: g=7,h=5 | Nodes: 677
[ASTAR] Min Days: 6 | Scheme: g=7,h=5 | Nodes: 258

Scheme: g = ChatGPT prompts/day, h = Gemini prompts/day
Nodes: Number of states explored by the algorithm

--------------------------------------------------------------------------------
INFEASIBLE CASES
--------------------------------------------------------------------------------

If no valid schedule exists (e.g., budget too low), output:
    [ALGO] Impossible | Nodes: <count>
