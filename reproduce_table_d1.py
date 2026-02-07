"""
Reproduce Table D1: Fixed-Scale Convex Map Ablation (Appendix D)
=================================================================
Replaces AC's per-step throughput-conserving normalization with a fixed
multiplicative constant C, calibrated from a linear burn-in.

Usage:  python reproduce_table_d1.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~5 minutes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation


def compute_modal_agreement(sim):
    alive = sim._alive_ids()
    if len(alive) < 2:
        return 0.0
    thresh = 1e-8
    top_targets = []
    for i in alive:
        targets = [j for j in alive if j != i]
        if not targets:
            continue
        vec = sim.aggression[i][targets]
        if float(np.sum(vec)) < thresh:
            continue
        top_j = targets[int(np.argmax(vec))]
        top_targets.append(top_j)
    if not top_targets:
        return 0.0
    counts = Counter(top_targets)
    _, modal_count = counts.most_common(1)[0]
    return modal_count / len(top_targets)


def calibrate_C(n_runs=8, n_burnin=100, gamma=2.0, seed0=42):
    """
    Run linear baseline for n_burnin steps, compute mean H_i / sum(h^gamma)
    across agents and runs. This gives the fixed constant that would match
    linear-regime throughput.
    """
    cal_ratios = []
    for r in range(n_runs):
        cfg = GirardConfig(
            alpha=0.15, salience_exponent=1.0,  # linear
            expulsion_threshold=None, n_steps=n_burnin,
            record_history=True, seed=seed0 + r * 1000,
        )
        sim = GirardSimulation(cfg, source="object", spread="linear")
        sim.run()

        alive = sim._alive_ids()
        ratios = []
        for i in alive:
            neighbors = [n for n in sim.graph.neighbors(i) if sim.alive.get(n, False)]
            if not neighbors:
                continue
            nh = np.zeros(cfg.n_agents, dtype=float)
            tw = 0.0
            for k in neighbors:
                w = sim.prestige.get((i, k), 0.0)
                nh += w * sim.aggression[k]
                tw += w
            if tw > 0:
                nh /= tw
            nh[i] = 0.0
            for d in range(cfg.n_agents):
                if not sim.alive.get(d, False):
                    nh[d] = 0.0
            H_i = float(np.sum(nh))
            if H_i > 0:
                sharpened_sum = float(np.sum(nh ** gamma))
                if sharpened_sum > 0:
                    ratios.append(H_i / sharpened_sum)
        if ratios:
            cal_ratios.append(np.mean(ratios))

    return float(np.mean(cal_ratios))


def run_fixed_scale(C, gamma=2.0, n_runs=8, n_steps=600, seed0=42):
    """Run fixed-scale convex map: pull_i(j) = C * h_i(j)^gamma."""
    peak_modals = []
    peak_ginis = []
    diverged_count = 0
    div_steps_list = []

    for r in range(n_runs):
        seed = seed0 + r * 1000
        cfg = GirardConfig(
            alpha=0.15, salience_exponent=gamma,
            expulsion_threshold=None, n_steps=n_steps,
            record_history=False, seed=seed,
        )
        sim = GirardSimulation(cfg, source="object", spread="attention")

        peak_modal = 0.0
        peak_gini = 0.0
        diverged = False

        for step in range(n_steps):
            sim._refresh_prestige()
            sim.step_desire()
            sim.step_aggression_source()
            sim._refresh_prestige()

            # CUSTOM SPREAD: fixed-scale convex map
            alive = sim._alive_ids()
            new_agg = {}
            for i in alive:
                neighbors = [n for n in sim.graph.neighbors(i) if sim.alive.get(n, False)]
                if not neighbors:
                    new_agg[i] = sim.aggression[i].copy()
                    continue
                nh = np.zeros(cfg.n_agents, dtype=float)
                tw = 0.0
                for k in neighbors:
                    w = sim.prestige.get((i, k), 0.0)
                    nh += w * sim.aggression[k]
                    tw += w
                if tw > 0:
                    nh /= tw
                nh[i] = 0.0
                for d in range(cfg.n_agents):
                    if not sim.alive.get(d, False):
                        nh[d] = 0.0
                pull = C * (nh ** gamma)
                result = cfg.alpha * sim.aggression[i] + (1.0 - cfg.alpha) * pull
                result[i] = 0.0
                for d in range(cfg.n_agents):
                    if not sim.alive.get(d, False):
                        result[d] = 0.0
                new_agg[i] = result
            for i, a in new_agg.items():
                sim.aggression[i] = a

            sim.step_decay()
            sim.step_num += 1

            # Metrics
            _, received = sim._received_aggression_vector()
            if float(np.max(received)) > 1e4:
                diverged = True
                div_steps_list.append(step)
                break

            cur_gini = sim._gini(received)
            cur_modal = compute_modal_agreement(sim)
            peak_modal = max(peak_modal, cur_modal)
            peak_gini = max(peak_gini, cur_gini)

        peak_modals.append(peak_modal)
        peak_ginis.append(peak_gini)
        if diverged:
            diverged_count += 1

    return {
        'peak_modal': np.mean(peak_modals),
        'peak_gini': np.mean(peak_ginis),
        'n_diverged': diverged_count,
        'div_steps': div_steps_list,
    }


def main():
    print("=" * 80)
    print("TABLE D1: Fixed-Scale Convex Map Ablation")
    print("  N=50, alpha=0.15, gamma=2.0, no expulsion, 600 steps, 8 runs")
    print("=" * 80)
    print()

    # Calibrate C
    C_cal = calibrate_C()
    print(f"Calibrated C_cal = {C_cal:.4f}")
    print()

    # Sweep C from 0.5*C_cal to 2.0*C_cal in 20 increments
    C_multipliers = np.linspace(0.5, 2.0, 20)

    print(f"{'C/C_cal':>8} | {'Pk Modal':>9} | {'Pk Gini':>8} | {'Diverged':>9}")
    print("-" * 45)

    for mult in C_multipliers:
        C = mult * C_cal
        r = run_fixed_scale(C)
        print(f"{mult:>8.3f} | {r['peak_modal']:>9.3f} | {r['peak_gini']:>8.3f} | "
              f"{r['n_diverged']:>5d}/8")

    # Find and report C_crit
    print()
    print("--- Divergence timing for above-threshold C ---")
    for mult in [1.2, 1.5, 2.0]:
        C = mult * C_cal
        r = run_fixed_scale(C)
        if r['div_steps']:
            print(f"  C/C_cal={mult:.1f}: divergence at steps "
                  f"range [{min(r['div_steps'])}-{max(r['div_steps'])}]")
        else:
            print(f"  C/C_cal={mult:.1f}: no divergence")


if __name__ == "__main__":
    main()
