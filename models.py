"""
models.py - Data Classes for Assignment Scheduler

This module defines the core data structures used throughout the application:
- Assignment: Represents a single assignment with its properties
- State: Represents the current state during DFS search

Author: AAI Assignment 1
"""

from dataclasses import dataclass, field
from typing import Set, Tuple, List


@dataclass(frozen=True)
class Assignment:
    """
    Represents a single assignment in the scheduling problem.
    
    Attributes:
        id: Unique identifier for the assignment
        prompt_count: Number of LLM prompts required to complete this assignment
        dependencies: Set of assignment IDs that must be completed before this one
    
    Note: frozen=True makes this hashable, allowing use in sets and as dict keys
    """
    id: int
    prompt_count: int
    dependencies: frozenset = field(default_factory=frozenset)
    
    def __repr__(self) -> str:
        deps = list(self.dependencies) if self.dependencies else []
        return f"A{self.id}(prompts={self.prompt_count}, deps={deps})"


@dataclass
class State:
    """
    Represents the current state during the DFS search.
    
    This tracks:
    - Which day we're currently on
    - Which assignments have been completed
    - How many prompts each student has remaining today
    
    Attributes:
        day: Current day number (1-indexed)
        completed: Set of completed assignment IDs
        student_remaining: Tuple of remaining prompts for each student
                          (tuple for immutability/hashability)
    """
    day: int
    completed: frozenset
    student_remaining: Tuple[int, ...]
    
    def __hash__(self):
        """Allow state to be used in sets for duplicate detection."""
        return hash((self.day, self.completed, self.student_remaining))
    
    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.day == other.day and 
                self.completed == other.completed and
                self.student_remaining == other.student_remaining)
    
    def copy_with_new_day(self, new_day: int, N: int, K: int) -> 'State':
        """
        Create a new state for the next day with reset student capacities.
        
        Args:
            new_day: The new day number
            N: Number of students
            K: Prompts per student per day
        
        Returns:
            New State with fresh student capacities
        """
        return State(
            day=new_day,
            completed=self.completed,
            student_remaining=tuple([K] * N)
        )


def create_initial_state(N: int, K: int) -> State:
    """
    Create the initial state for the search.
    
    Args:
        N: Number of students
        K: Prompts per student per day
    
    Returns:
        Initial state: Day 1, no assignments completed, all students have K prompts
    """
    return State(
        day=1,
        completed=frozenset(),
        student_remaining=tuple([K] * N)
    )
