"""
Reproduce Table 2: Fine-grained gamma sweep
=============================================
Phase boundary identification near gamma = 1.0.
AC variant (object rivalry + attentional concentration), no expulsion.

Usage:  python reproduce_table_2.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~5 minutes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation, VARIANT_MAP


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def main():
    gammas = [0.75, 0.90, 0.95, 1.00, 1.01, 1.02, 1.05, 1.08,
              1.10, 1.15, 1.25, 1.50, 2.00]

    N_RUNS = 8
    N_STEPS = 600
    SEED0 = 42

    print("=" * 95)
    print("TABLE 2: Fine-grained gamma sweep")
    print(f"  N=50, WS k=6 p=0.15, alpha=0.15, no expulsion, {N_RUNS} runs x {N_STEPS} steps")
    print("=" * 95)
    print()
    print(f"{'gamma':>6} | {'Pk Modal':>10} {'(sd)':>6} | {'Fin Modal':>10} {'(sd)':>6} | "
          f"{'Pk Gini':>8} | {'Med t95':>8} | {'Conv%':>6}")
    print("-" * 80)

    for gamma in gammas:
        peak_modals = []
        final_modals = []
        peak_ginis = []
        t95_values = []

        for r in range(N_RUNS):
            seed = SEED0 + r * 1000

            cfg = GirardConfig(
                n_agents=50, n_neighbors=6, rewire_prob=0.15,
                alpha=0.15, salience_exponent=gamma,
                expulsion_threshold=None,   # no expulsion
                n_steps=N_STEPS,
                record_history=True, seed=seed,
            )

            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()

            modal = sim.history["modal_agreement"]
            gini = sim.history["aggression_gini"]

            peak_modals.append(max(modal))
            final_modals.append(np.mean(modal[-50:]))
            peak_ginis.append(max(gini))

            t95 = time_to_95(modal)
            t95_values.append(t95)

        pk_m = np.mean(peak_modals)
        pk_sd = np.std(peak_modals)
        fn_m = np.mean(final_modals)
        fn_sd = np.std(final_modals)
        pk_g = np.mean(peak_ginis)

        converged = [t for t in t95_values if t is not None]
        conv_rate = len(converged) / N_RUNS
        med_t95 = int(np.median(converged)) if converged else None
        t95_str = str(med_t95) if med_t95 is not None else "--"

        print(f"{gamma:>6.2f} | {pk_m:>10.3f} {pk_sd:>6.3f} | {fn_m:>10.3f} {fn_sd:>6.3f} | "
              f"{pk_g:>8.3f} | {t95_str:>8} | {conv_rate*100:>5.0f}%")


if __name__ == "__main__":
    main()
