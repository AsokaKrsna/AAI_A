"""
graph.py - Dependency Graph Utilities

This module provides graph-based operations for the assignment dependency structure:
- Cycle detection (validate DAG property)
- Critical path computation (longest dependency chain)
- Finding "ready" assignments (dependencies satisfied)

The dependency structure forms a Directed Acyclic Graph (DAG).

Author: AAI Assignment 1
"""

from typing import Dict, List, Set
from models import Assignment


def has_cycle(assignments: Dict[int, Assignment]) -> bool:
    """
    Detect if the dependency graph contains a cycle.
    
    Uses DFS-based cycle detection with three colors:
    - WHITE (0): Unvisited
    - GRAY (1): Currently being processed (in recursion stack)
    - BLACK (2): Fully processed
    
    A cycle exists if we encounter a GRAY node during DFS.
    
    Args:
        assignments: Dictionary mapping assignment ID to Assignment
    
    Returns:
        True if a cycle exists, False otherwise
    
    Example:
        If A1 → A2 → A3 → A1, this forms a cycle and returns True.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {aid: WHITE for aid in assignments}
    
    def dfs(node_id: int) -> bool:
        """Return True if cycle is found starting from this node."""
        color[node_id] = GRAY
        
        # Explore all nodes that depend on this one
        for other_id, other in assignments.items():
            if node_id in other.dependencies:
                if color[other_id] == GRAY:
                    # Found a back edge → cycle!
                    return True
                if color[other_id] == WHITE:
                    if dfs(other_id):
                        return True
        
        color[node_id] = BLACK
        return False
    
    # Run DFS from each unvisited node
    for assignment_id in assignments:
        if color[assignment_id] == WHITE:
            if dfs(assignment_id):
                return True
    
    return False


def compute_critical_path(assignments: Dict[int, Assignment]) -> int:
    """
    Compute the critical path as dependency depth (number of 'levels' in the DAG).
    
    IMPORTANT: This counts the NUMBER OF DEPENDENCY LEVELS, not individual assignments.
    Multiple assignments at the same level can be done in parallel (or cascaded
    within the same day if students have capacity).
    
    However, this is NOT a strict lower bound on days because:
    - Multiple levels CAN be completed in a single day if capacity allows
    - The DFS algorithm allows cascading within a day
    
    This is provided as INFORMATIONAL only, not as a hard constraint.
    
    Args:
        assignments: Dictionary mapping assignment ID to Assignment
    
    Returns:
        Number of dependency levels (depth of the DAG)
    
    Example:
        A1 → A2 → A4 → A8 is 4 levels deep
        But A1, A2, A4, A8 could potentially all be done on ONE day
        if different students work on them and capacity allows!
    """
    # Memoization cache: assignment_id → depth level
    memo: Dict[int, int] = {}
    
    def depth_of(assignment_id: int) -> int:
        """Compute the depth level of this assignment."""
        if assignment_id in memo:
            return memo[assignment_id]
        
        assignment = assignments[assignment_id]
        
        if not assignment.dependencies:
            # Base case: no dependencies, this is level 1
            memo[assignment_id] = 1
        else:
            # Recursive case: 1 + max depth of dependencies
            max_dep_depth = 0
            for dep_id in assignment.dependencies:
                max_dep_depth = max(max_dep_depth, depth_of(dep_id))
            memo[assignment_id] = 1 + max_dep_depth
        
        return memo[assignment_id]
    
    # Compute for all assignments and return maximum depth
    if not assignments:
        return 0
    
    return max(depth_of(aid) for aid in assignments)


def get_ready_assignments(
    completed: frozenset,
    assignments: Dict[int, Assignment]
) -> List[Assignment]:
    """
    Find all assignments that are ready to be worked on.
    
    An assignment is "ready" if:
    1. It has not been completed yet
    2. All of its dependencies have been completed
    
    Args:
        completed: Set of completed assignment IDs
        assignments: Dictionary of all assignments
    
    Returns:
        List of Assignment objects that are ready to be started
    
    Example:
        If A1 is completed and A2 depends only on A1, then A2 is ready.
    """
    ready = []
    
    for assignment in assignments.values():
        # Skip if already completed
        if assignment.id in completed:
            continue
        
        # Check if all dependencies are satisfied
        if assignment.dependencies.issubset(completed):
            ready.append(assignment)
    
    return ready


def topological_sort(assignments: Dict[int, Assignment]) -> List[int]:
    """
    Perform topological sort on assignments based on dependencies.
    
    Returns assignments in an order where dependencies come before
    the assignments that depend on them.
    
    Uses Kahn's algorithm (BFS-based).
    
    Args:
        assignments: Dictionary mapping assignment ID to Assignment
    
    Returns:
        List of assignment IDs in topological order
    
    Raises:
        ValueError: If the graph has a cycle (no valid topological order)
    """
    # Compute in-degree for each node
    in_degree = {aid: 0 for aid in assignments}
    for assignment in assignments.values():
        for dep_id in assignment.dependencies:
            # dep_id → assignment.id edge exists
            pass  # We need reverse direction
    
    # Build adjacency list (dependency → dependent)
    adj: Dict[int, List[int]] = {aid: [] for aid in assignments}
    for assignment in assignments.values():
        for dep_id in assignment.dependencies:
            adj[dep_id].append(assignment.id)
            in_degree[assignment.id] = in_degree.get(assignment.id, 0)
    
    # Recalculate in-degrees properly
    in_degree = {aid: len(assignments[aid].dependencies) for aid in assignments}
    
    # Start with nodes that have no dependencies
    queue = [aid for aid, deg in in_degree.items() if deg == 0]
    result = []
    
    while queue:
        current = queue.pop(0)
        result.append(current)
        
        # Reduce in-degree of dependents
        for dependent in adj[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    if len(result) != len(assignments):
        raise ValueError("Graph has a cycle, topological sort not possible")
    
    return result
