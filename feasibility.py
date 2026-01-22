"""
feasibility.py - Pre-Search Feasibility Checks

This module validates that a solution is even possible before running
the expensive DFS search. It catches common issues early with clear error messages.

Checks performed:
1. No single assignment requires more prompts than K
2. Total prompts don't exceed theoretical capacity (N * K * M)
3. Critical path doesn't exceed M days
4. Dependency graph has no cycles

Author: AAI Assignment 1
"""

from math import ceil
from typing import Dict, List
from models import Assignment
from graph import has_cycle, compute_critical_path


def check_feasibility(
    assignments: Dict[int, Assignment],
    N: int,
    K: int,
    M: int
) -> List[str]:
    """
    Perform all feasibility checks before starting the search.
    
    Args:
        assignments: Dictionary of all assignments
        N: Number of students
        K: Prompts per student per day
        M: Maximum number of days allowed
    
    Returns:
        List of error messages. Empty list means the problem is feasible.
    
    Example:
        >>> errors = check_feasibility(assignments, 3, 5, 4)
        >>> if errors:
        ...     for err in errors:
        ...         print(f"Error: {err}")
        ... else:
        ...     print("Problem is feasible, proceeding with search...")
    """
    errors = []
    
    # =========================================================================
    # Check 1: No assignment requires more prompts than K
    # =========================================================================
    # If any single assignment needs more than K prompts, it can never
    # be completed by any student in a single day.
    for assignment in assignments.values():
        if assignment.prompt_count > K:
            errors.append(
                f"Assignment {assignment.id} requires {assignment.prompt_count} "
                f"prompts, but maximum prompts per student per day is K={K}. "
                f"This assignment can never be completed."
            )
    
    # =========================================================================
    # Check 2: Total capacity check (lower bound on days)
    # =========================================================================
    # The minimum number of days needed is at least:
    # ceil(total_prompts / (N * K))
    # If this exceeds M, the problem is impossible.
    total_prompts = sum(a.prompt_count for a in assignments.values())
    max_prompts_per_day = N * K
    min_days_needed = ceil(total_prompts / max_prompts_per_day)
    
    if min_days_needed > M:
        errors.append(
            f"Total prompts needed: {total_prompts}. "
            f"Maximum prompts per day: {max_prompts_per_day} (N={N} × K={K}). "
            f"Minimum days required: {min_days_needed}, but M={M}. "
            f"Not enough days to complete all assignments."
        )
    
    # =========================================================================
    # Check 3: Critical path - INFORMATIONAL ONLY
    # =========================================================================
    # NOTE: The critical path (dependency depth) is NOT a hard constraint!
    # Multiple dependency levels can be completed in a single day because:
    # - Different students can work on different assignments in parallel
    # - Once a student finishes A1, another student can start A2 the same day
    # 
    # Example: A1 → A2 → A4 → A8 has depth 4, but could be done in 1 day
    # if students complete them sequentially and have enough prompts.
    #
    # We keep this calculation for informational purposes only.
    # The DFS algorithm will naturally find if solutions exist.
    
    # =========================================================================
    # Check 4: Cycle detection
    # =========================================================================
    # A cycle in dependencies means the problem is ill-formed.
    if has_cycle(assignments):
        errors.append(
            "Dependency graph contains a cycle. "
            "This is an invalid problem definition - assignments cannot "
            "have circular dependencies."
        )
    
    return errors


def print_feasibility_report(
    assignments: Dict[int, Assignment],
    N: int,
    K: int,
    M: int
) -> bool:
    """
    Print a detailed feasibility report and return whether problem is feasible.
    
    Args:
        assignments: Dictionary of all assignments
        N: Number of students
        K: Prompts per student per day
        M: Maximum number of days allowed
    
    Returns:
        True if feasible, False otherwise
    """
    print("=" * 60)
    print("FEASIBILITY CHECK")
    print("=" * 60)
    
    # Print problem summary
    total_prompts = sum(a.prompt_count for a in assignments.values())
    max_daily_capacity = N * K
    critical_path = compute_critical_path(assignments)
    
    print(f"\nProblem Summary:")
    print(f"  - Assignments: {len(assignments)}")
    print(f"  - Students (N): {N}")
    print(f"  - Prompts/student/day (K): {K}")
    print(f"  - Target days (M): {M}")
    print(f"  - Total prompts needed: {total_prompts}")
    print(f"  - Max daily capacity: {max_daily_capacity}")
    print(f"  - Dependency depth (levels, not days!): {critical_path}")
    print(f"  - Theoretical min days: {ceil(total_prompts / max_daily_capacity)}")
    
    # Run checks
    errors = check_feasibility(assignments, N, K, M)
    
    if errors:
        print(f"\n[X] INFEASIBLE - {len(errors)} issue(s) found:\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}\n")
        return False
    else:
        print(f"\n[OK] FEASIBLE - All checks passed!")
        return True

