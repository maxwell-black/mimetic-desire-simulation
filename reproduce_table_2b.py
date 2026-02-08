"""
Reproduce Table 2b: Phase boundary N-invariance
=================================================
Does the convergence boundary gamma* shift with N?
AC variant, no expulsion.

Usage:  python reproduce_table_2b.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~20-30 minutes (N=200 is slow).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def main():
    gammas = [1.01, 1.02, 1.03, 1.04, 1.05]
    Ns = [50, 100, 200]
    N_RUNS = 20
    N_STEPS = 800

    print("=" * 90)
    print("TABLE 2b: Phase boundary N-invariance")
    print(f"  AC variant, no expulsion, {N_RUNS} seeds x {N_STEPS} steps")
    print("=" * 90)
    print()
    print(f"{'N':<6} {'k':<4} {'gamma':<8} {'Conv Rate':>10} {'Med t95':>8}")
    print("-" * 45)

    for N in Ns:
        k = max(6, min(int(N * 0.12), 20))
        if k % 2 == 1:
            k -= 1

        for gamma in gammas:
            t95_vals = []

            for r in range(N_RUNS):
                seed = 42 + r * 1000
                cfg = GirardConfig(
                    n_agents=N, n_neighbors=k, rewire_prob=0.15,
                    alpha=0.15, salience_exponent=gamma,
                    expulsion_threshold=None,
                    n_steps=N_STEPS, record_history=True, seed=seed,
                )
                sim = GirardSimulation(cfg, source="object", spread="attention")
                sim.run()
                modal = sim.history["modal_agreement"]
                t95_vals.append(time_to_95(modal))

            converged = [t for t in t95_vals if t is not None]
            conv_rate = len(converged) / N_RUNS * 100
            med_t95 = f"{np.median(converged):.0f}" if converged else "--"

            print(f"{N:<6} {k:<4} {gamma:<8} {conv_rate:>9.0f}% {med_t95:>8}")

        print()


if __name__ == "__main__":
    main()
