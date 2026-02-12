import sys, argparse, heapq, math
from itertools import combinations

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

def get_ready(completed, assignments):
    return [aid for aid, data in assignments.items()
            if aid not in completed and data['deps'].issubset(completed)]

def llm_type(aid): return 'chatgpt' if aid % 2 == 0 else 'gemini'

def critical_path_len(assignments, completed):
    memo = {}
    def depth(aid):
        if aid in memo: return memo[aid]
        children = [o for o, d in assignments.items() if aid in d['deps'] and o not in completed]
        memo[aid] = 1 + max((depth(c) for c in children), default=0)
        return memo[aid]
    remaining = [a for a in assignments if a not in completed]
    return max((depth(a) for a in remaining), default=0)

def h_days(asgn, done, g, h):
    rg = sum(asgn[a]['prompts'] for a in asgn if a not in done and llm_type(a)=='chatgpt')
    rm = sum(asgn[a]['prompts'] for a in asgn if a not in done and llm_type(a)=='gemini')
    cg = math.ceil(rg/g) if g > 0 else (float('inf') if rg > 0 else 0)
    cm = math.ceil(rm/h) if h > 0 else (float('inf') if rm > 0 else 0)
    return max(critical_path_len(asgn, done), cg, cm)

# Case-A: one assignment per student per day
def schedule_A(asgn, N, g, h, M, algo='dfs'):
    total, best, nodes = len(asgn), [float('inf')], [0]
    def dfs(day, done):
        nodes[0] += 1
        if len(done) == total:
            best[0] = min(best[0], day-1); return True
        if day > M: return False
        if algo=='dfbb' and day-1+h_days(asgn,done,g,h) >= best[0]: return False
        ready = get_ready(done, asgn)
        if not ready: return False
        found = False
        for sz in range(min(N,len(ready)), 0, -1):
            for combo in combinations(ready, sz):
                gn = sum(asgn[a]['prompts'] for a in combo if llm_type(a)=='chatgpt')
                mn = sum(asgn[a]['prompts'] for a in combo if llm_type(a)=='gemini')
                if gn <= g and mn <= h:
                    if dfs(day+1, done|frozenset(combo)):
                        found = True
                        if algo != 'dfs': return True
        return found
    if algo == 'astar': return astar_A(asgn, N, g, h, M, nodes)
    dfs(1, frozenset())
    return (best[0] if best[0] != float('inf') else -1), nodes[0]

def astar_A(asgn, N, g, h, M, nodes):
    total = len(asgn)
    pq = [(h_days(asgn, frozenset(), g, h), 0, frozenset())]
    visited = set()
    while pq:
        f, day, done = heapq.heappop(pq)
        nodes[0] += 1
        if len(done) == total: return day, nodes[0]
        if day >= M: continue
        if done in visited: continue
        visited.add(done)
        ready = get_ready(done, asgn)
        for sz in range(1, min(N,len(ready))+1):
            for combo in combinations(ready, sz):
                gn = sum(asgn[a]['prompts'] for a in combo if llm_type(a)=='chatgpt')
                mn = sum(asgn[a]['prompts'] for a in combo if llm_type(a)=='gemini')
                if gn <= g and mn <= h:
                    nd = done | frozenset(combo)
                    heapq.heappush(pq, (day+1+h_days(asgn,nd,g,h), day+1, nd))
    return -1, nodes[0]

# Case-B helpers: next-day sharing
def ready_B(done, prev, asgn, sd):
    ready = []
    for aid, data in asgn.items():
        if aid in done: continue
        if data['deps'].issubset(prev):
            ready.append((aid, list(range(len(sd)))))
        else:
            ok = [i for i,d in sd.items() if all(x in prev or x in d for x in data['deps'])]
            if ok: ready.append((aid, ok))
    return ready

def schedule_B(asgn, N, g, h, M, algo='dfs'):
    total, best, nodes = len(asgn), [float('inf')], [0]
    def dfs(day, done, prev, rg, rm, sd, hw):
        nodes[0] += 1
        if len(done) == total:
            best[0] = min(best[0], day); return True
        if day > M: return False
        if algo=='dfbb' and day-1+h_days(asgn,done,g,h) >= best[0]: return False
        found = False
        for aid, allowed in ready_B(done, prev, asgn, sd):
            p = asgn[aid]['prompts']
            gpt = llm_type(aid)=='chatgpt'
            if (rg if gpt else rm) >= p:
                s = allowed[0]
                nrg, nrm = rg-(p if gpt else 0), rm-(p if not gpt else 0)
                nsd = {k:v.copy() for k,v in sd.items()}; nsd[s].add(aid)
                if dfs(day, done|{aid}, prev, nrg, nrm, nsd, True):
                    found = True
                    if algo != 'dfs': return True
        if hw and dfs(day+1, done, done, g, h, {i:set() for i in range(N)}, False):
            found = True
            if algo != 'dfs': return True
        return found
    if algo == 'astar': return astar_B(asgn, N, g, h, M, nodes)
    dfs(1, frozenset(), frozenset(), g, h, {i:set() for i in range(N)}, False)
    return (best[0] if best[0] != float('inf') else -1), nodes[0]

def astar_B(asgn, N, g, h, M, nodes):
    total = len(asgn)
    pq = [(h_days(asgn,frozenset(),g,h), 0, 1, frozenset(), frozenset())]
    visited, ctr = set(), 0
    def day_expand(comp, prev, rg, rm, sd):
        results = set()
        for aid, allowed in ready_B(comp, prev, asgn, sd):
            p = asgn[aid]['prompts']
            gpt = llm_type(aid)=='chatgpt'
            if (rg if gpt else rm) >= p:
                s = allowed[0]
                nsd = {k:v.copy() for k,v in sd.items()}; nsd[s].add(aid)
                results |= day_expand(comp|{aid}, prev, rg-(p if gpt else 0), rm-(p if not gpt else 0), nsd)
        results.add(comp)
        return results
    while pq:
        f, _, day, done, prev = heapq.heappop(pq)
        nodes[0] += 1
        if len(done) == total: return day-1, nodes[0]
        if day > M: continue
        key = (day, done)
        if key in visited: continue
        visited.add(key)
        for nd in day_expand(done, prev, g, h, {i:set() for i in range(N)}):
            if nd != done:
                ctr += 1
                heapq.heappush(pq, (day+h_days(asgn,nd,g,h), ctr, day+1, nd, nd))
    return -1, nodes[0]

# Query drivers
def find_days(asgn, N, case, budget, c1, c2, M_up, algo):
    schemes = []
    for gg in range(0, int(budget//c1)+1):
        hh = int((budget-gg*c1)//c2) if c2>0 else 0
        if gg>0 or hh>0: schemes.append((gg,hh))
    mg = max((asgn[a]['prompts'] for a in asgn if llm_type(a)=='chatgpt'), default=0)
    mm = max((asgn[a]['prompts'] for a in asgn if llm_type(a)=='gemini'), default=0)
    schemes = [(g,h) for g,h in schemes if g>=mg and h>=mm]
    sched = schedule_A if case=='A' else schedule_B
    best, nc, bs = float('inf'), 0, None
    for gg, hh in schemes:
        d, n = sched(asgn, N, gg, hh, min(M_up,best-1) if best!=float('inf') else M_up, algo)
        nc += n
        if d != -1 and d < best: best, bs = d, (gg,hh)
    return (best if best!=float('inf') else -1), nc, bs

def find_cost(asgn, N, case, M, c1, c2, algo):
    mg = max((asgn[a]['prompts'] for a in asgn if llm_type(a)=='chatgpt'), default=0)
    mm = max((asgn[a]['prompts'] for a in asgn if llm_type(a)=='gemini'), default=0)
    tg = sum(asgn[a]['prompts'] for a in asgn if llm_type(a)=='chatgpt')
    tm = sum(asgn[a]['prompts'] for a in asgn if llm_type(a)=='gemini')
    sched = schedule_A if case=='A' else schedule_B
    best, nc, bs = float('inf'), 0, None
    for gg in range(mg, tg+1):
        for hh in range(mm, tm+1):
            cost = gg*c1 + hh*c2
            if cost >= best: continue
            d, n = sched(asgn, N, gg, hh, M, algo)
            nc += n
            if d != -1 and cost < best: best, bs = cost, (gg,hh)
    return (best if best!=float('inf') else -1), nc, bs

def main():
    p = argparse.ArgumentParser(description='Assignment 3: Dual-LLM scheduling')
    p.add_argument('input_file'); p.add_argument('--case', required=True, choices=['A','B'])
    p.add_argument('--N', type=int, required=True)
    p.add_argument('--c1', type=int, required=True); p.add_argument('--c2', type=int, required=True)
    q = p.add_mutually_exclusive_group(required=True)
    q.add_argument('--find-days', action='store_true'); q.add_argument('--find-cost', action='store_true')
    p.add_argument('--budget', type=int); p.add_argument('--M', type=int)
    p.add_argument('--algo', default='all', choices=['dfs','dfbb','astar','all'])
    args = p.parse_args()
    if args.find_days and args.budget is None: p.error('--budget required with --find-days')
    if args.find_cost and args.M is None: p.error('--M required with --find-cost')
    asgn = parse_input(args.input_file)
    if has_cycle(asgn): print("Error: Cyclic dependencies"); sys.exit(1)
    algos = ['dfs','dfbb','astar'] if args.algo=='all' else [args.algo]
    print(f"Case {args.case} | N={args.N} | c1={args.c1} c2={args.c2}")
    print("-"*50)
    for algo in algos:
        if args.find_days:
            r, nc, s = find_days(asgn, args.N, args.case, args.budget, args.c1, args.c2, len(asgn), algo)
        else:
            r, nc, s = find_cost(asgn, args.N, args.case, args.M, args.c1, args.c2, algo)
        lbl = f"[{algo.upper():>5}]"
        if r == -1: print(f"{lbl} Impossible | Nodes: {nc}")
        elif args.find_days: print(f"{lbl} Min Days: {r} | Scheme: g={s[0]},h={s[1]} | Nodes: {nc}")
        else: print(f"{lbl} Min Cost: {r} | Scheme: g={s[0]},h={s[1]} | Nodes: {nc}")

if __name__ == "__main__":
    main()
