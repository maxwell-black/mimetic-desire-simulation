"""
exp_small_n_param_sensitivity.py
=================================
Does the phase boundary gamma* remain robust across parameter
settings at small N, as it does at N=50?

Sweeps alpha x decay at N=10 and N=20 (representative small-N values),
finding gamma* (lowest gamma with >= 50% convergence).

Uses adaptive convergence threshold throughout.

Design:
  N:      {10, 20}  (N=10: near-complete graph, N=20: threshold=0.95)
  alpha:  {0.05, 0.10, 0.15, 0.20, 0.30}
  decay:  {0.01, 0.03, 0.05, 0.10}
  gamma:  fine sweep around known boundary
  Seeds:  10 per combo
  Steps:  800 (no expulsion)

Run:
    python exp_small_n_param_sensitivity.py 2>&1 | Tee-Object -FilePath exp_small_n_param_sensitivity_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
"""

import sys, os, time
import numpy as np
from itertools import product

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation
from small_n_utils import adaptive_k, adaptive_unanimity_threshold


def time_to_convergence(modal_series, n_agents, consecutive=10):
    """Check convergence using adaptive threshold."""
    threshold = adaptive_unanimity_threshold(n_agents)
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def find_boundary(n_agents, alpha, decay, gammas, n_seeds, n_steps):
    """Sweep gammas, return dict mapping gamma -> convergence_rate."""
    k = adaptive_k(n_agents)
    results = {}

    for gamma in gammas:
        converged = 0
        for r in range(n_seeds):
            seed = 42 + r * 1000
            cfg = GirardConfig(
                n_agents=n_agents,
                n_neighbors=k,
                rewire_prob=0.15,
                alpha=alpha,
                salience_exponent=gamma,
                aggression_decay=decay,
                expulsion_threshold=None,
                n_steps=n_steps,
                record_history=True,
                seed=seed,
            )
            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()
            modal = sim.history["modal_agreement"]
            tc = time_to_convergence(modal, n_agents)
            if tc is not None:
                converged += 1

        results[gamma] = converged / n_seeds
    return results


def find_gamma_star(gamma_rates, threshold=0.5):
    for gamma in sorted(gamma_rates.keys()):
        if gamma_rates[gamma] >= threshold:
            return gamma
    return None


def main():
    alphas = [0.05, 0.10, 0.15, 0.20, 0.30]
    decays = [0.01, 0.03, 0.05, 0.10]
    gammas = [0.95, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.25, 2.00]
    Ns = [10, 20]  # representative small-N values
    N_SEEDS = 10
    N_STEPS = 800

    print("=" * 110)
    print("SMALL-N PARAMETER SENSITIVITY: PHASE BOUNDARY ROBUSTNESS")
    print(f"Ns: {Ns}, Seeds: {N_SEEDS}, Steps: {N_STEPS}")
    print(f"Gammas: {gammas}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)

    for N in Ns:
        k = adaptive_k(N)
        thresh = adaptive_unanimity_threshold(N)

        print(f"\n{'=' * 110}")
        print(f"N={N}, k={k}, convergence threshold={thresh:.3f}")
        print(f"{'=' * 110}")

        boundary_map = {}
        combo_count = 0
        total_combos = len(alphas) * len(decays)

        print(f"\n{'alpha':<8} {'decay':<8} {'gamma*':>8}  convergence rates by gamma...")
        print("-" * 110)

        for alpha, decay in product(alphas, decays):
            combo_count += 1
            t0 = time.time()

            rates = find_boundary(N, alpha, decay, gammas, N_SEEDS, N_STEPS)
            gamma_star = find_gamma_star(rates)
            boundary_map[(alpha, decay)] = gamma_star
            elapsed = time.time() - t0

            rates_str = "  ".join(f"{g}:{rates[g]:.0%}" for g in sorted(rates.keys()))
            gs_str = f"{gamma_star}" if gamma_star is not None else ">2.0"
            print(f"{alpha:<8.2f} {decay:<8.2f} {gs_str:>8}  {rates_str}  "
                  f"({elapsed:.0f}s) [{combo_count}/{total_combos}]")

        # Boundary map summary
        print(f"\n\n  BOUNDARY MAP: gamma* by (alpha, decay) for N={N}")
        print(f"  {'':>8}" + "".join(f"{'d='+str(d):>10}" for d in decays))
        for alpha in alphas:
            row = f"  a={alpha:<5.2f}"
            for decay in decays:
                gs = boundary_map.get((alpha, decay))
                row += f"{str(gs) if gs else '>2.0':>10}"
            print(row)

        # Compare with N=50 baseline
        print(f"\n  Reference: at N=50 (from exp3), boundary is uniformly in [1.02, 1.05]")
        all_stars = [v for v in boundary_map.values() if v is not None]
        if all_stars:
            print(f"  At N={N}: range=[{min(all_stars)}, {max(all_stars)}], "
                  f"median={np.median(all_stars)}")
            in_range = sum(1 for g in all_stars if 1.02 <= g <= 1.05)
            print(f"  In [1.02, 1.05]: {in_range}/{len(all_stars)}")
        else:
            print(f"  At N={N}: no convergence found at any gamma")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
