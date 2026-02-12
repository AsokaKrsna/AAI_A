import sys

def parse_input(filename):
    N, K, assignments = None, None, {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'): continue
            parts = line.split()
            if parts[0].upper() == 'N': N = int(parts[1])
            elif parts[0].upper() == 'K': K = int(parts[1])
            elif parts[0].upper() == 'A':
                aid, prompts = int(parts[1]), int(parts[2])
                deps = frozenset(int(d) for d in parts[3:] if int(d) != 0)
                assignments[aid] = {'prompts': prompts, 'deps': deps}
    return N, K, assignments

def has_cycle(assignments):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {aid: WHITE for aid in assignments}
    def dfs(node):
        color[node] = GRAY
        for other, data in assignments.items():
            if node in data['deps']:
                if color[other] == GRAY: return True
                if color[other] == WHITE and dfs(other): return True
        color[node] = BLACK
        return False
    return any(color[a] == WHITE and dfs(a) for a in assignments)

# getting assignments which are ready to be assigned
def get_ready(completed, assignments):
    return [aid for aid, data in assignments.items() 
            if aid not in completed and data['deps'].issubset(completed)]

#Try to fit assignment into a student, return (success, new_remaining)
def can_fit(prompts, remaining):
    for i, r in enumerate(remaining):
        if r >= prompts:
            return True, remaining[:i] + (r - prompts,) + remaining[i+1:]
    return False, remaining
# dfs with backtracking to find all valid schedules
def solve(assignments, N, K, M):
    solutions = []
    total = len(assignments)
    
    def dfs(day, completed, remaining, today, schedule):
        if len(completed) == total:
            final = schedule + ([today[:]] if today else [])
            solutions.append(final)
            return
        if day > M: return
        
        ready = get_ready(completed, assignments)
        for aid in ready:
            fits, new_rem = can_fit(assignments[aid]['prompts'], remaining)
            if fits:
                dfs(day, completed | {aid}, new_rem, today + [aid], schedule)
        
        if today:  # Try ending day (Relaxed)
            dfs(day + 1, completed, tuple([K]*N), [], schedule + [today[:]])
    
    dfs(1, frozenset(), tuple([K]*N), [], [])
    
    # Remove duplicates (same assignments per day, different order is same as students are identical in capacity)
    seen, unique = set(), []
    for sched in solutions:
        key = tuple(tuple(sorted(day)) for day in sched)
        if key not in seen:
            seen.add(key)
            unique.append([sorted(day) for day in sched])
    return unique

def main():
    if len(sys.argv) != 3:
        print("Usage: python minimal_implementation.py <input-file> <days>")
        sys.exit(1)
    
    filename, M = sys.argv[1], int(sys.argv[2])
    N, K, assignments = parse_input(filename)
    
    # feasibility checks
    for aid, data in assignments.items():
        if data['prompts'] > K:
            print(f"Error: Assignment {aid} needs {data['prompts']} prompts but K={K}")
            sys.exit(1)
    if has_cycle(assignments):
        print("Error: Cyclic dependencies detected")
        sys.exit(1)
    
    solutions = solve(assignments, N, K, M)
    
    if not solutions:
        print("No valid schedules found.")
    else:
        print(f"Found {len(solutions)} valid schedule(s):\n")
        for i, sched in enumerate(solutions, 1):
            print(f"Schedule {i}:")
            for d, day in enumerate(sched, 1):
                print(f"  Day {d}: {', '.join(f'A{a}' for a in day)}")
            print()

if __name__ == "__main__":
    main()