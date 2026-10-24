#!/usr/bin/env python3
"""Reproducible *fictional graph-walk* scaling check; not extraction accuracy.

Measures only the predecessor-graph traversal, not complete audit runtime.
Timing varies with hardware/load; compare within the same process. No real
governance, archive-authenticity or production-performance inference.
"""
from time import perf_counter
from collections import Counter
import platform
import random
import sys
from supersession_graph import audit_supersession


def previous_walk(parents):
    """Frozen pre-optimization graph traversal (quadratic on long chains)."""
    issues = []
    for start in parents:
        seen = set()
        node = start
        while node in parents:
            if node in seen:
                issues.append('cyclic_supersession')
                break
            seen.add(node)
            node = parents[node]
    return sorted(set(issues))


def linear_walk(parents):
    """Independent graph-walk-only analogue of the candidate traversal."""
    issues = []
    state = {}
    for start in parents:
        if state.get(start, 0):
            continue
        path = []
        node = start
        while node in parents and state.get(node, 0) == 0:
            state[node] = 1
            path.append(node)
            node = parents[node]
        if state.get(node, 0) == 1:
            issues.append('cyclic_supersession')
        for visited in path:
            state[visited] = 2
    return sorted(set(issues))


def main():
    rng = random.Random(2401024)
    for n in (0, 1, 2, 10, 100, 1000):
        for trial in range(60):
            parents = {}
            for i in range(n):
                if rng.random() < .75:
                    parents[f'D{i}'] = f'D{rng.randrange(n)}'
            assert previous_walk(parents) == linear_walk(parents), (n, trial)
    print('equivalence: 360 seeded fictional graph fixtures PASS')
    print('runtime:', sys.version.split()[0], platform.platform())
    for n in (1000, 5000, 12000):
        parents = {f'D{i}': f'D{i-1}' for i in range(1, n)}
        t = perf_counter()
        old_result = previous_walk(parents)
        old_seconds = perf_counter() - t
        t = perf_counter()
        new_result = linear_walk(parents)
        new_seconds = perf_counter() - t
        assert old_result == new_result == []
        rows = [{'id': 'D0'}] + [
            {'id': f'D{i}', 'supersedes': f'D{i-1}'}
            for i in range(1, n)
        ]
        assert audit_supersession({'ground_truth': {'decisions': rows}}) == []
        print(f'chain={n} previous_walk={old_seconds:.6f}s '
              f'linear_walk={new_seconds:.6f}s '
              f'ratio={old_seconds / new_seconds:.1f}x; integrated=PASS')


if __name__ == '__main__':
    main()
