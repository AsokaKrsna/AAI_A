================================================================================
                    ASSIGNMENT SCHEDULER
                    
        CS5205 - Advanced Artificial Intelligence Lab
                      Assignment 1
================================================================================


1. PROBLEM DESCRIPTION
------------------------------------------------------------------------------

This solution addresses the assignment scheduling problem where N students 
must complete a set of assignments using an LLM assistant with limited 
daily prompts.

Constraints:
  - Each student has K prompts per day (resets daily)
  - Assignments have prerequisite dependencies
  - All work must be completed within M days
  - Assignments cannot be split across days

Objective:
  - Find ALL valid schedules satisfying these constraints


2. EXECUTION
------------------------------------------------------------------------------

Command format:
    python main.py <input-file> <number-of-days>

Examples:
    python main.py sample_pdf.txt 4      # 8 assignments, 4 days
    python main.py input1.txt 5          # 12 assignments, 5 days
    python main.py input2.txt 3          # 11 assignments, 3 days


3. INPUT FILE FORMAT
------------------------------------------------------------------------------

Structure:
    % Comment (lines beginning with % are ignored)
    N <integer>                              -- Number of students
    K <integer>                              -- Prompts per student per day
    A <id> <prompts> <dep1> <dep2> ... 0     -- Assignment specification

The terminating 0 indicates the end of the dependency list.

Example:
    % Sample input
    N 3
    K 5
    A 1 2 0              -- Assignment 1: 2 prompts, no dependencies
    A 2 4 1 0            -- Assignment 2: 4 prompts, requires A1
    A 3 3 1 2 0          -- Assignment 3: 3 prompts, requires A1 and A2


4. OUTPUT FORMAT
------------------------------------------------------------------------------

The output consists of:
  1. Problem summary (number of assignments, students, prompts)
  2. Feasibility analysis results
  3. All valid schedules with classification labels

Classification:
  - Packed:  Schedule where every day was fully utilized
  - Relaxed: Schedule where at least one day ended with unused capacity

Example output:
    Found 257 valid schedule(s):
      - Packed: 2 (days fully utilized)
      - Relaxed: 255 (advanced day early)

    Schedule 1 (Packed):
    ------------------------------
    Day 1: A1, A2, A4, A7
    Day 2: A3, A5, A6, A8


5. PROJECT STRUCTURE
------------------------------------------------------------------------------

Source Code:
    main.py           Entry point and CLI interface
    models.py         Data structures (Assignment, State)
    parser.py         Input file parsing and validation
    graph.py          Dependency graph operations
    feasibility.py    Pre-search feasibility checks
    solver.py         DFS with backtracking algorithm

Documentation:
    README.txt        This file
    approach.md       Design decisions and approach analysis
    algorithm.md      Formal algorithm specification
    flowchart.md      Mermaid flowchart specifications

Sample Inputs:
    sample_pdf.txt    8 assignments (from problem statement)
    input1.txt        12 assignments (linear with branches)
    input2.txt        11 assignments (diamond pattern)
    input3.txt        10 assignments (wide parallel)


6. ALGORITHM OVERVIEW
------------------------------------------------------------------------------

The solution employs DFS (Depth-First Search) with backtracking:

Phase 1: PARSING
    - Input file is read and parsed
    - Dependency graph is constructed

Phase 2: FEASIBILITY VALIDATION
    - Check: No assignment exceeds K prompts
    - Check: Total prompts do not exceed M × N × K
    - Check: Dependency graph is acyclic

Phase 3: STATE SPACE SEARCH
    - State: (day, completed_set, remaining_prompts)
    - Transitions: Assign ready assignment OR end current day
    - Pruning: Branches exceeding M days are terminated

Phase 4: POST-PROCESSING
    - Schedules are normalized (sorted within days)
    - Duplicates are removed via hashing
    - Packed/Relaxed classification is applied


7. REQUIREMENTS
------------------------------------------------------------------------------

  - Python 3.7 or higher (dataclasses required)
  - No external dependencies


8. ERROR MESSAGES
------------------------------------------------------------------------------

"Assignment X requires Y prompts but K = Z"
    An assignment cannot be completed in a single day.
    Resolution: Increase K or reduce assignment size.

"Dependency graph contains a cycle"
    Circular dependency detected.
    Resolution: Fix the input file to remove cycles.

"Total prompts exceeds capacity"
    M × N × K is insufficient for all assignments.
    Resolution: Increase M (days) or N (students).


================================================================================