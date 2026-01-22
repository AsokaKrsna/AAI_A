"""
solver.py - DFS Backtracking Solver

This module implements the core algorithm to find all valid schedules.

Algorithm Overview:
1. Use DFS with backtracking to explore all possible assignment orderings
2. At each state, find "ready" assignments (dependencies satisfied)
3. Try adding each ready assignment to the current day if it fits
4. When no more assignments fit today, advance to the next day
5. Collect all complete schedules that finish within M days

Key Concepts:
- Bin-packing: Fitting assignments into student capacities each day
- State pruning: Stop exploring if we exceed M days
- Backtracking: Undo moves to explore alternative paths

Author: AAI Assignment 1
"""

from typing import Dict, List, Tuple, Set
from models import Assignment, State, create_initial_state
from graph import get_ready_assignments


def can_fit_assignment(
    assignment: Assignment,
    student_remaining: Tuple[int, ...]
) -> Tuple[bool, Tuple[int, ...], int]:
    """
    Check if an assignment can be assigned to any student today.
    
    Uses First-Fit strategy: assign to the first student who has capacity.
    Since students are equivalent, the specific student doesn't matter for output.
    
    Args:
        assignment: The assignment to try to fit
        student_remaining: Current remaining prompts for each student
    
    Returns:
        Tuple of (can_fit, new_remaining, student_index)
        - can_fit: True if assignment can be done today
        - new_remaining: Updated capacity tuple after assignment
        - student_index: Which student was assigned (for tracking)
    """
    for i, remaining in enumerate(student_remaining):
        if remaining >= assignment.prompt_count:
            # This student can do it
            new_remaining = list(student_remaining)
            new_remaining[i] -= assignment.prompt_count
            return True, tuple(new_remaining), i
    
    return False, student_remaining, -1


def solve(
    assignments: Dict[int, Assignment],
    N: int,
    K: int,
    M: int
) -> List[List[List[int]]]:
    """
    Find all valid schedules using DFS with backtracking.
    
    A schedule is represented as a list of days, where each day contains
    a list of assignment IDs completed that day.
    
    Args:
        assignments: Dictionary of all assignments
        N: Number of students
        K: Prompts per student per day
        M: Maximum number of days allowed
    
    Returns:
        List of valid schedules. Each schedule is:
        [[day1_assignments], [day2_assignments], ...]
    
    Example:
        [[1, 7], [2, 5], [4, 6, 3], [8]]
        Means: Day 1: A1, A7; Day 2: A2, A5; Day 3: A4, A6, A3; Day 4: A8
    """
    # Solutions now include (schedule, is_packed) tuples
    # is_packed = True if no day was ended early (always exhausted capacity or finished)
    all_solutions: List[Tuple[List[List[int]], bool]] = []
    total_assignments = len(assignments)
    
    def dfs(
        day: int,
        completed: frozenset,
        student_remaining: Tuple[int, ...],
        current_day_assignments: List[int],
        schedule: List[List[int]],
        is_packed: bool  # Track if all days so far were fully packed
    ):
        """
        Recursive DFS function to explore all valid schedules.
        
        Args:
            day: Current day number (1-indexed)
            completed: Set of completed assignment IDs
            student_remaining: Remaining prompts for each student today
            current_day_assignments: Assignments done so far today
            schedule: Schedule built so far (list of completed days)
            is_packed: True if no early day-advances occurred so far
        """
        # =====================================================================
        # Goal Check: All assignments completed?
        # =====================================================================
        if len(completed) == total_assignments:
            # Build final schedule including current day's work
            final_schedule = schedule.copy()
            if current_day_assignments:
                final_schedule.append(current_day_assignments.copy())
            all_solutions.append((final_schedule, is_packed))
            return
        
        # =====================================================================
        # Pruning: Exceeded day limit?
        # =====================================================================
        if day > M:
            return  # Not a valid solution
        
        # =====================================================================
        # Find Ready Assignments
        # =====================================================================
        ready = get_ready_assignments(completed, assignments)
        
        # =====================================================================
        # Try Each Ready Assignment
        # =====================================================================
        made_a_move = False
        
        for assignment in ready:
            can_fit, new_remaining, _ = can_fit_assignment(
                assignment, student_remaining
            )
            
            if can_fit:
                made_a_move = True
                
                # Make the move
                new_completed = completed | {assignment.id}
                new_day_assignments = current_day_assignments + [assignment.id]
                
                # Recurse: continue on the same day with reduced capacity
                dfs(
                    day,
                    new_completed,
                    new_remaining,
                    new_day_assignments,
                    schedule,
                    is_packed  # Carry forward packed status
                )
        
        # =====================================================================
        # Try Advancing to Next Day
        # =====================================================================
        # We can advance to the next day if:
        # 1. We did some work today (current_day_assignments not empty), OR
        # 2. We couldn't make any moves (forced to wait)
        if current_day_assignments:
            # Check if this is an early advance (relaxed) or forced advance (packed)
            # It's packed only if NO ready assignment could fit any student
            ready_after_work = get_ready_assignments(completed, assignments)
            could_do_more = False
            for a in ready_after_work:
                can_fit_more, _, _ = can_fit_assignment(a, student_remaining)
                if can_fit_more:
                    could_do_more = True
                    break
            
            # If we're advancing but could do more, this path becomes "relaxed"
            new_is_packed = is_packed and (not could_do_more)
            
            # Finish current day, start fresh tomorrow
            new_schedule = schedule + [current_day_assignments.copy()]
            new_remaining = tuple([K] * N)  # Reset all students
            
            dfs(
                day + 1,
                completed,
                new_remaining,
                [],
                new_schedule,
                new_is_packed
            )
        elif not made_a_move and len(completed) < total_assignments:
            # Stuck: no ready assignments fit, but we haven't done anything today
            # This can happen if all ready assignments need more prompts than
            # any student has remaining, but we haven't done anything yet
            # This is actually a dead end (shouldn't happen if feasibility passed)
            pass
    
    # Start DFS from initial state
    initial_remaining = tuple([K] * N)
    dfs(
        day=1,
        completed=frozenset(),
        student_remaining=initial_remaining,
        current_day_assignments=[],
        schedule=[],
        is_packed=True  # Start assuming packed until proven otherwise
    )
    
    # Remove duplicate schedules (same day groupings, different order within day)
    unique_solutions = remove_duplicate_schedules(all_solutions)
    
    return unique_solutions


def remove_duplicate_schedules(
    schedules: List[Tuple[List[List[int]], bool]]
) -> List[Tuple[List[List[int]], bool]]:
    """
    Remove duplicate schedules that differ only in order within a day.
    
    Since students are equivalent, [A1, A7] on day 1 is the same as [A7, A1].
    We normalize by sorting assignments within each day.
    
    Args:
        schedules: List of schedules (may contain duplicates)
    
    Returns:
        List of unique schedules
    """
    seen = set()
    unique = []
    
    for schedule, is_packed in schedules:
        # Normalize: sort assignments within each day
        normalized = tuple(tuple(sorted(day)) for day in schedule)
        key = (normalized, is_packed)
        
        if key not in seen:
            seen.add(key)
            # Store with sorted days for consistency
            unique.append(([sorted(day) for day in schedule], is_packed))
    
    return unique


def format_schedule(schedule: List[List[int]]) -> str:
    """
    Format a schedule for printing.
    
    Args:
        schedule: A valid schedule (list of day assignments)
    
    Returns:
        Human-readable string representation
    """
    lines = []
    for day_num, day_assignments in enumerate(schedule, 1):
        assignment_strs = [f"A{aid}" for aid in day_assignments]
        lines.append(f"Day {day_num}: {', '.join(assignment_strs)}")
    return '\n'.join(lines)


def print_all_solutions(solutions: List[Tuple[List[List[int]], bool]]) -> None:
    """
    Print all solutions in a readable format.
    
    Args:
        solutions: List of (schedule, is_packed) tuples
    """
    if not solutions:
        print("No valid schedules found.")
        return
    
    # Count packed vs relaxed
    packed_count = sum(1 for _, is_packed in solutions if is_packed)
    relaxed_count = len(solutions) - packed_count
    
    print(f"\nFound {len(solutions)} valid schedule(s):")
    print(f"  - Packed: {packed_count} (days fully utilized)")
    print(f"  - Relaxed: {relaxed_count} (advanced day early)\n")
    print("=" * 50)
    
    for i, (schedule, is_packed) in enumerate(solutions, 1):
        label = "Packed" if is_packed else "Relaxed"
        print(f"\nSchedule {i} ({label}):")
        print("-" * 30)
        print(format_schedule(schedule))
    
    print("\n" + "=" * 50)
