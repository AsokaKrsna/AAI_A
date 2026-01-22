"""
parser.py - Input File Parser for Assignment Scheduler

This module handles parsing the input file format as specified in the assignment:
- Lines starting with '%' are comments
- 'N <number>' specifies number of students
- 'K <number>' specifies prompts per student per day
- 'A <id> <prompts> <dependencies...> 0' specifies an assignment

Author: AAI Assignment 1
"""

from typing import Dict, Tuple
from models import Assignment


def parse_input(filename: str) -> Tuple[int, int, Dict[int, Assignment]]:
    """
    Parse an input file and extract problem parameters.
    
    Input file format:
        % Comment line (ignored)
        N <number_of_students>
        K <prompts_per_day>
        A <id> <prompt_count> <dep1> <dep2> ... 0
    
    Args:
        filename: Path to the input file
    
    Returns:
        Tuple of (N, K, assignments_dict)
        - N: Number of students
        - K: Prompts per student per day
        - assignments_dict: Dictionary mapping assignment ID to Assignment object
    
    Raises:
        ValueError: If required parameters N or K are missing
        FileNotFoundError: If input file doesn't exist
    
    Example:
        >>> N, K, assignments = parse_input("sample.txt")
        >>> print(f"Students: {N}, Prompts/day: {K}")
        >>> print(f"Assignments: {len(assignments)}")
    """
    N = None  # Number of students
    K = None  # Prompts per student per day
    assignments: Dict[int, Assignment] = {}
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('%'):
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            command = parts[0].upper()
            
            if command == 'N':
                # Parse number of students
                if len(parts) < 2:
                    raise ValueError(f"Line {line_num}: N requires a value")
                N = int(parts[1])
                
            elif command == 'K':
                # Parse prompts per day
                if len(parts) < 2:
                    raise ValueError(f"Line {line_num}: K requires a value")
                K = int(parts[1])
                
            elif command == 'A':
                # Parse assignment: A <id> <prompts> <deps...> 0
                if len(parts) < 4:
                    raise ValueError(
                        f"Line {line_num}: Assignment format is 'A <id> <prompts> <deps...> 0'"
                    )
                
                assignment_id = int(parts[1])
                prompt_count = int(parts[2])
                
                # Dependencies are all numbers after prompt_count until we hit 0
                # The 0 is the terminating symbol
                dependencies = set()
                for dep_str in parts[3:]:
                    dep = int(dep_str)
                    if dep == 0:
                        break  # Terminating symbol
                    dependencies.add(dep)
                
                assignments[assignment_id] = Assignment(
                    id=assignment_id,
                    prompt_count=prompt_count,
                    dependencies=frozenset(dependencies)
                )
    
    # Validate that required parameters are present
    if N is None:
        raise ValueError("Input file missing 'N' (number of students)")
    if K is None:
        raise ValueError("Input file missing 'K' (prompts per day)")
    if not assignments:
        raise ValueError("Input file contains no assignments")
    
    return N, K, assignments


def validate_dependencies(assignments: Dict[int, Assignment]) -> None:
    """
    Validate that all dependencies reference existing assignments.
    
    Args:
        assignments: Dictionary of assignments
    
    Raises:
        ValueError: If any dependency references a non-existent assignment
    """
    all_ids = set(assignments.keys())
    
    for assignment in assignments.values():
        for dep_id in assignment.dependencies:
            if dep_id not in all_ids:
                raise ValueError(
                    f"Assignment {assignment.id} depends on non-existent "
                    f"assignment {dep_id}"
                )
