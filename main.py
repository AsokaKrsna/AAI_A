"""
main.py - CLI Entry Point for Assignment Scheduler

This is the main entry point that orchestrates the entire solution:
1. Parse command line arguments
2. Read and parse input file
3. Run feasibility checks
4. Execute DFS solver
5. Print all valid schedules

Usage:
    python main.py <input-file> <number-of-days>

Example:
    python main.py input1.txt 4

Author: AAI Assignment 1
"""

import sys
from parser import parse_input, validate_dependencies
from feasibility import check_feasibility, print_feasibility_report
from solver import solve, print_all_solutions


def main():
    """
    Main entry point for the assignment scheduler.
    
    Command line interface:
        python main.py <input-filename> <number-of-days>
    """
    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) != 3:
        print("Usage: python main.py <input-filename> <number-of-days>")
        print("Example: python main.py input1.txt 4")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    
    try:
        M = int(sys.argv[2])
        if M <= 0:
            raise ValueError("Number of days must be positive")
    except ValueError as e:
        print(f"Error: Invalid number of days: {sys.argv[2]}")
        print("Number of days must be a positive integer.")
        sys.exit(1)
    
    # =========================================================================
    # Parse Input File
    # =========================================================================
    print(f"\nReading input file: {input_filename}")
    print(f"Target days (M): {M}")
    
    try:
        N, K, assignments = parse_input(input_filename)
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing input file: {e}")
        sys.exit(1)
    
    # Validate that all dependencies reference existing assignments
    try:
        validate_dependencies(assignments)
    except ValueError as e:
        print(f"Error in dependency structure: {e}")
        sys.exit(1)
    
    print(f"\nParsed successfully:")
    print(f"  - Students (N): {N}")
    print(f"  - Prompts/day (K): {K}")
    print(f"  - Assignments: {len(assignments)}")
    
    # Print assignment details
    print("\nAssignments:")
    for aid in sorted(assignments.keys()):
        a = assignments[aid]
        deps = list(a.dependencies) if a.dependencies else ['none']
        print(f"  A{a.id}: {a.prompt_count} prompts, depends on: {deps}")
    
    # =========================================================================
    # Feasibility Checks
    # =========================================================================
    print("\n")
    is_feasible = print_feasibility_report(assignments, N, K, M)
    
    if not is_feasible:
        print("\nExiting due to infeasibility.")
        sys.exit(1)
    
    # =========================================================================
    # Run Solver
    # =========================================================================
    print("\n" + "=" * 60)
    print("RUNNING DFS SOLVER")
    print("=" * 60)
    
    solutions = solve(assignments, N, K, M)
    
    # =========================================================================
    # Print Results
    # =========================================================================
    print_all_solutions(solutions)
    
    if solutions:
        print(f"\nTotal valid schedules: {len(solutions)}")
    else:
        print("\nNo valid schedules exist within the given constraints.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
