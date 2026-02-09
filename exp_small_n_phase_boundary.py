"""
exp_small_n_phase_boundary.py
==============================
Does the phase boundary gamma* shift at very small N?

Known: gamma* in [1.02, 1.05] at N=50, 100, 200 (N-invariant).
Question: does it hold at N=5-40? At N=5 the network is complete --
does that change the boundary?

AC variant, no expulsion, fine-grained gamma sweep.
Uses adaptive convergence threshold (same as viability experiment).

Run:
    python exp_small_n_phase_boundary.py 2>&1 | Tee-Object -FilePath exp_small_n_phase_boundary_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
"""

import sys, os, time
import numpy as np

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation
from small_n_utils import adaptive_k, adaptive_unanimity_threshold


def time_to_convergence(modal_series, n_agents, consecutive=10):
    """Check if modal agreement reaches adaptive threshold for consecutive steps.
    Uses the ORIGINAL N (no expulsion in this experiment)."""
    threshold = adaptive_unanimity_threshold(n_agents)
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def main():
    gammas = [0.95, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.25, 2.00]
    Ns = [5, 10, 15, 20, 25, 30, 35, 40]
    N_RUNS = 20
    N_STEPS = 800

    print("=" * 100)
    print("SMALL-N PHASE BOUNDARY: DOES GAMMA* SHIFT AT VERY SMALL N?")
    print(f"AC variant, no expulsion, {N_RUNS} seeds x {N_STEPS} steps")
    print(f"Convergence = adaptive threshold sustained {10} steps")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    for N in Ns:
        k = adaptive_k(N)
        thresh = adaptive_unanimity_threshold(N)
        t0_N = time.time()

        print(f"\n--- N={N}, k={k}, threshold={thresh:.3f} ---")
        print(f"{'gamma':<8} {'Conv Rate':>10} {'Med t_conv':>11} "
              f"{'Min t_conv':>11} {'Max t_conv':>11} {'Med Peak':>10}")
        print("-" * 70)

        for gamma in gammas:
            t_conv_vals = []
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
                tc = time_to_convergence(modal, N)
                t_conv_vals.append(tc)
                peak_vals.append(max(modal))

            converged = [t for t in t_conv_vals if t is not None]
            conv_rate = len(converged) / N_RUNS * 100
            med_tc = f"{np.median(converged):.0f}" if converged else "--"
            min_tc = f"{min(converged):.0f}" if converged else "--"
            max_tc = f"{max(converged):.0f}" if converged else "--"
            med_peak = f"{np.median(peak_vals):.3f}"

            print(f"{gamma:<8} {conv_rate:>9.0f}% {med_tc:>11} "
                  f"{min_tc:>11} {max_tc:>11} {med_peak:>10}")

        elapsed_N = time.time() - t0_N
        print(f"  (N={N} completed in {elapsed_N:.0f}s)")

    # Summary: boundary comparison
    print("\n\n" + "=" * 100)
    print("BOUNDARY COMPARISON: gamma* (lowest gamma with >= 50% convergence)")
    print("=" * 100)

    print(f"\n{'N':<6} {'k':<4} {'thresh':<8} {'gamma*':>8}")
    print("-" * 30)

    for N in Ns:
        k = adaptive_k(N)
        thresh = adaptive_unanimity_threshold(N)
        gamma_star = None

        for gamma in gammas:
            converged = 0
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
                if time_to_convergence(modal, N) is not None:
                    converged += 1

            if converged / N_RUNS >= 0.5 and gamma_star is None:
                gamma_star = gamma

        gs_str = f"{gamma_star}" if gamma_star is not None else ">2.0"
        print(f"{N:<6} {k:<4} {thresh:<8.3f} {gs_str:>8}")

    print(f"\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
