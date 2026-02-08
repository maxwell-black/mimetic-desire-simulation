"""
phase_boundary_large_N.py
==========================
Does the phase boundary gamma* shift with N?

Currently we only know gamma* in [1.02, 1.05] at N=50.
This runs the same fine-grained sweep at N=100 and N=200,
20 seeds each, no expulsion.

Run from repo root:
    python phase_boundary_large_N.py 2>&1 | tee phase_boundary_large_N_results.txt

Runtime: ~15-25 minutes.
"""

import sys, os, time
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
    gammas = [0.95, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.25, 2.00]
    Ns = [50, 100, 200]
    N_RUNS = 20
    N_STEPS = 800

    print("=" * 80)
    print("PHASE BOUNDARY SWEEP: DOES GAMMA* SHIFT WITH N?")
    print(f"{N_RUNS} seeds per condition, {N_STEPS} steps, no expulsion")
    print("=" * 80)

    for N in Ns:
        # Scale k with N, same rule as other experiments
        k = max(6, min(int(N * 0.12), 20))
        if k % 2 == 1:
            k -= 1

        t0 = time.time()
        print(f"\n--- N={N}, k={k} ---")
        print(f"{'gamma':<8} {'Conv Rate':>10} {'Med t95':>10} "
              f"{'Min t95':>10} {'Max t95':>10} {'Med Peak':>10}")
        print("-" * 65)

        for gamma in gammas:
            t95_vals = []
            peak_vals = []

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
                t95 = time_to_95(modal)
                t95_vals.append(t95)
                peak_vals.append(max(modal))

            converged = [t for t in t95_vals if t is not None]
            conv_rate = len(converged) / N_RUNS * 100
            med_t95 = f"{np.median(converged):.0f}" if converged else "--"
            min_t95 = f"{min(converged):.0f}" if converged else "--"
            max_t95 = f"{max(converged):.0f}" if converged else "--"
            med_peak = f"{np.median(peak_vals):.3f}"

            print(f"{gamma:<8} {conv_rate:>9.0f}% {med_t95:>10} "
                  f"{min_t95:>10} {max_t95:>10} {med_peak:>10}")

        elapsed = time.time() - t0
        print(f"  (N={N} completed in {elapsed/60:.1f} min)")

    # Summary comparison
    print("\n" + "=" * 80)
    print("BOUNDARY COMPARISON")
    print("=" * 80)
    print("""
Look for: the gamma value where convergence jumps from 0% to >0%,
and where it reaches 100%.

If gamma* is N-invariant, the boundary should be [1.02, 1.05]
at all three N values.

If gamma* shifts left with N (easier convergence at large N),
that would mean larger communities are MORE susceptible to
scapegoating -- a Girard-consistent finding.

If gamma* shifts right (harder at large N), the opposite.
""")


if __name__ == "__main__":
    main()
