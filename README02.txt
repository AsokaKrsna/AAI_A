CS5205 - Advanced Artificial Intelligence Lab
Assignment 2 | Assignment Scheduler | State Space 2


# HOW TO RUN

Usage:
    python assg02.py <input-file> --mode <1|2> --N <students> [--find-days --K <prompts>] [--find-prompts --M <days>]

# MODES

Mode 1: Instant Sharing
    - Results are shared immediately when an assignment is completed.
    - Any student can start dependent assignments on the same day.

Mode 2: Next-Day Sharing  
    - Results are shared at 6am the next day.
    - Only the student who completed an assignment can use it on the same day.
    - Other students must wait until the next day.

# QUERIES

--find-days: Find minimum days to complete all assignments
    Requires: --K (prompts per student per day)

--find-prompts: Find minimum prompts per student per day
    Requires: --M (number of days available)

# EXAMPLES

Find minimum days with Mode 1 (instant sharing), 3 students, 5 prompts/day:
    python assg02.py input.txt --mode 1 --find-days --N 3 --K 5

Find minimum prompts with Mode 1, 3 students, 4 days:
    python assg02.py input.txt --mode 1 --find-prompts --N 3 --M 4

Find minimum days with Mode 2 (next-day sharing), 3 students, 5 prompts/day:
    python assg02.py input.txt --mode 2 --find-days --N 3 --K 5

Find minimum prompts with Mode 2, 3 students, 4 days:
    python assg02.py input.txt --mode 2 --find-prompts --N 3 --M 4

# INPUT FILE FORMAT <Same as assignment 1>

% Comment lines start with %
N 3
K 5
A <id> <prompt-count> <dependency1> <dependency2> ... 0

Example:
    A 1 2 0
    A 2 4 1 0
    A 3 2 4 0

Note: N and K in the file are ignored. Use command line arguments instead.

# OUTPUT

Minimum Days: <value>     or    Impossible
Minimum Prompts: <value>  or    Impossible
