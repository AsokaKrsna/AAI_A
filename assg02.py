import sys
import argparse

def parse_input(filename):
    assignments = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'): continue
            parts = line.split()
            if parts[0].upper() == 'A':
                aid, prompts = int(parts[1]), int(parts[2])
                deps = frozenset(int(d) for d in parts[3:] if int(d) != 0)
                assignments[aid] = {'prompts': prompts, 'deps': deps}
    return assignments

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

def can_fit(prompts, remaining):
    for i, r in enumerate(remaining):
        if r >= prompts:
            return True, remaining[:i] + (r - prompts,) + remaining[i+1:]
    return False, remaining

def get_ready(completed, assignments):
    return [aid for aid, data in assignments.items() 
            if aid not in completed and data['deps'].issubset(completed)]

def can_complete_mode1(assignments, N, K, M):
    total = len(assignments)
    def dfs(day, completed, remaining, today):
        if len(completed) == total: return True
        if day > M: return False
        for aid in get_ready(completed, assignments):
            fits, new_rem = can_fit(assignments[aid]['prompts'], remaining)
            if fits and dfs(day, completed | {aid}, new_rem, True): return True
        if today and dfs(day + 1, completed, tuple([K]*N), False): return True
        return False
    return dfs(1, frozenset(), tuple([K]*N), False)

def get_ready_mode2(completed, prev_done, assignments, student_done):
    ready = []
    for aid, data in assignments.items():
        if aid in completed: continue
        if data['deps'].issubset(prev_done):
            ready.append((aid, list(range(len(student_done)))))
        else:
            allowed = [i for i, done in student_done.items() 
                       if all(d in prev_done or d in done for d in data['deps'])]
            if allowed: ready.append((aid, allowed))
    return ready

def can_complete_mode2(assignments, N, K, M):
    total = len(assignments)
    def dfs(day, completed, prev_done, remaining, student_done, today):
        if len(completed) == total: return True
        if day > M: return False
        for aid, allowed in get_ready_mode2(completed, prev_done, assignments, student_done):
            p = assignments[aid]['prompts']
            for s in allowed:
                if remaining[s] >= p:
                    new_rem = remaining[:s] + (remaining[s] - p,) + remaining[s+1:]
                    new_sd = {k: v.copy() for k, v in student_done.items()}
                    new_sd[s].add(aid)
                    if dfs(day, completed | {aid}, prev_done, new_rem, new_sd, True): return True
        if today and dfs(day + 1, completed, completed, tuple([K]*N), {i: set() for i in range(N)}, False): return True
        return False
    return dfs(1, frozenset(), frozenset(), tuple([K]*N), {i: set() for i in range(N)}, False)

def find_min_days(assignments, N, K, mode):
    if max(d['prompts'] for d in assignments.values()) > K: return -1
    check = can_complete_mode1 if mode == 1 else can_complete_mode2
    low, high, result = 1, len(assignments), -1
    while low <= high:
        mid = (low + high) // 2
        if check(assignments, N, K, mid): result, high = mid, mid - 1
        else: low = mid + 1
    return result

def find_min_prompts(assignments, N, M, mode):
    check = can_complete_mode1 if mode == 1 else can_complete_mode2
    low = max(d['prompts'] for d in assignments.values())
    high = sum(d['prompts'] for d in assignments.values())
    result = -1
    while low <= high:
        mid = (low + high) // 2
        if check(assignments, N, mid, M): result, high = mid, mid - 1
        else: low = mid + 1
    return result

def main():
    parser = argparse.ArgumentParser(description='Assignment 2: Optimal scheduling')
    parser.add_argument('input_file')
    parser.add_argument('--mode', type=int, required=True, choices=[1, 2])
    parser.add_argument('--N', type=int, required=True)
    query = parser.add_mutually_exclusive_group(required=True)
    query.add_argument('--find-days', action='store_true')
    query.add_argument('--find-prompts', action='store_true')
    parser.add_argument('--K', type=int)
    parser.add_argument('--M', type=int)
    args = parser.parse_args()

    if args.find_days and args.K is None: parser.error('--K required with --find-days')
    if args.find_prompts and args.M is None: parser.error('--M required with --find-prompts')

    assignments = parse_input(args.input_file)
    if has_cycle(assignments): print("Error: Cyclic dependencies"); sys.exit(1)

    if args.find_days:
        result = find_min_days(assignments, args.N, args.K, args.mode)
        print(f"Minimum Days: {result}" if result != -1 else "Impossible")
    else:
        result = find_min_prompts(assignments, args.N, args.M, args.mode)
        print(f"Minimum Prompts: {result}" if result != -1 else "Impossible")

if __name__ == "__main__":
    main()