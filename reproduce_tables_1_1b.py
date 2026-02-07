"""
Reproduce Tables 1 and 1b
===========================
Table 1:  Summary metrics (Gini, top-target share, convergence ratio, expulsions, catharsis)
Table 1b: Convergence outcomes under full dynamics (expulsions enabled)

Usage:  python reproduce_tables_1_1b.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~3 minutes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation, VARIANT_MAP, run_many


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    """First step where modal agreement >= threshold for `consecutive` steps."""
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def fraction_converged_steps(modal_series, threshold=0.95, consecutive=10):
    """Fraction of timesteps lying inside qualifying convergence episodes."""
    n = len(modal_series)
    in_episode = [False] * n
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            for k in range(consecutive):
                in_episode[t + k] = True
    return sum(in_episode) / n if n > 0 else 0.0


def main():
    cfg = GirardConfig(
        n_agents=50, n_neighbors=6, rewire_prob=0.15,
        alpha=0.15, salience_exponent=2.0,
        expulsion_threshold=8.0, n_steps=600,
        record_history=True, seed=42,
    )

    n_runs = 10
    seed0 = 42

    # ================================================================
    # TABLE 1
    # ================================================================
    print("=" * 90)
    print("TABLE 1: Summary metrics across 10 runs per variant")
    print("  alpha=0.15, gamma=2.0, 600 steps, tau=8.0, seeds spaced by 1000")
    print("=" * 90)
    print()
    print(f"{'Variant':<8} {'Mechanism':<28} {'Gini':>8} {'TopShr':>8} "
          f"{'ConvR':>8} {'Expuls':>8} {'Catharsis':>10}")
    print("-" * 90)

    all_results = {}

    for variant_name in ["LM", "AC", "RL", "RA"]:
        source, spread = VARIANT_MAP[variant_name]
        sims = run_many(cfg, source=source, spread=spread, n_runs=n_runs, seed0=seed0)

        run_catharsis = []
        run_gini = []
        run_top_share = []
        run_conv_ratio = []
        run_expulsions = []
        run_modal = []

        for sim in sims:
            cath_events = sim.history["catharsis_events"]
            if cath_events:
                drops = [e[2] for e in cath_events]
                run_catharsis.append(np.mean(drops))
            else:
                run_catharsis.append(0.0)

            run_expulsions.append(len(cath_events))
            run_gini.append(np.mean(sim.history["aggression_gini"]))
            run_top_share.append(np.mean(sim.history["aggression_max_share"]))
            run_conv_ratio.append(np.mean(sim.history["convergence_ratio"]))
            run_modal.append(sim.history["modal_agreement"])

        mean_cath = np.mean(run_catharsis)
        mean_gini = np.mean(run_gini)
        mean_top = np.mean(run_top_share)
        mean_conv = np.mean(run_conv_ratio)
        mean_exp = np.mean(run_expulsions)

        mechanism_labels = {
            "LM": "Linear mimesis",
            "AC": "Attentional concentration",
            "RL": "Rivalry + linear",
            "RA": "Rivalry + attention",
        }

        print(f"{variant_name:<8} {mechanism_labels[variant_name]:<28} "
              f"{mean_gini:>8.3f} {mean_top:>8.3f} {mean_conv:>8.2f} "
              f"{mean_exp:>8.1f} {mean_cath*100:>9.1f}%")

        all_results[variant_name] = {
            'modal_series': run_modal,
            'mean_gini': mean_gini,
        }

    # ================================================================
    # TABLE 1b
    # ================================================================
    print()
    print("=" * 90)
    print("TABLE 1b: Convergence outcomes under full dynamics (expulsions enabled)")
    print("  Convergence = modal agreement >= 0.95 for 10 consecutive steps")
    print("=" * 90)
    print()
    print(f"{'Variant':<8} {'ConvRate':>10} {'Med t1':>8} {'FracConv':>10} {'PeakModal':>10}")
    print("-" * 50)

    for variant_name in ["LM", "AC", "RL", "RA"]:
        modal_runs = all_results[variant_name]['modal_series']
        n = len(modal_runs)

        converged_count = 0
        t1_values = []
        frac_values = []
        peak_values = []

        for modal in modal_runs:
            t95 = time_to_95(modal)
            if t95 is not None:
                converged_count += 1
                t1_values.append(t95)
            frac_values.append(fraction_converged_steps(modal))
            peak_values.append(max(modal))

        conv_rate = converged_count / n
        med_t1 = int(np.median(t1_values)) if t1_values else None
        mean_frac = np.mean(frac_values)
        mean_peak = np.mean(peak_values)

        t1_str = str(med_t1) if med_t1 is not None else "--"
        print(f"{variant_name:<8} {conv_rate*100:>9.0f}% {t1_str:>8} "
              f"{mean_frac:>10.3f} {mean_peak:>10.3f}")


if __name__ == "__main__":
    main()
