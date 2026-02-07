"""
Reproduce Table 3: Operator Ablation
======================================
Three conditions isolating the contributions of convex transform vs normalization:
  Condition 1: Linear baseline (gamma=1)
  Condition 2: Raw h^gamma, no normalization
  Condition 3: Full AC operator (convex redistribution, throughput conserved)

Usage:  python reproduce_table_3.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~2 minutes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation


def compute_modal_agreement(sim):
    """Compute modal-target agreement from simulation state."""
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


def run_condition(label, spread_fn, gamma, n_runs=8, n_steps=600):
    """
    Run a condition with a custom spread function.
    spread_fn: callable(sim, cfg) that performs one spread step in-place.
    """
    peak_ginis = []
    peak_modals = []
    final_masses = []
    max_aggs = []

    for r in range(n_runs):
        seed = 42 + r * 1000
        cfg = GirardConfig(
            n_agents=50, n_neighbors=6, rewire_prob=0.15,
            alpha=0.15, salience_exponent=gamma,
            expulsion_threshold=None,  # no expulsion
            n_steps=n_steps, record_history=False, seed=seed,
        )
        sim = GirardSimulation(cfg, source="object", spread="linear")
        # We override the spread step manually in the loop

        peak_modal = 0.0
        peak_gini = 0.0
        final_mass = 0.0
        max_agg = 0.0

        for step in range(n_steps):
            sim._refresh_prestige()
            sim.step_desire()
            sim.step_aggression_source()
            sim._refresh_prestige()

            # Custom spread step
            spread_fn(sim, cfg, gamma)

            sim.step_decay()
            sim.step_num += 1

            # Metrics
            _, received = sim._received_aggression_vector()
            total_mass = float(np.sum(received))
            cur_max = float(np.max(received)) if len(received) > 0 else 0.0
            cur_gini = sim._gini(received)
            cur_modal = compute_modal_agreement(sim)

            peak_modal = max(peak_modal, cur_modal)
            peak_gini = max(peak_gini, cur_gini)
            final_mass = total_mass
            max_agg = max(max_agg, cur_max)

        peak_ginis.append(peak_gini)
        peak_modals.append(peak_modal)
        final_masses.append(final_mass)
        max_aggs.append(max_agg)

    return {
        'peak_gini': np.mean(peak_ginis),
        'peak_modal': np.mean(peak_modals),
        'final_mass': np.mean(final_masses),
        'max_agg': np.mean(max_aggs),
    }


def spread_linear(sim, cfg, gamma):
    """Condition 1: Linear baseline (standard LM spread)."""
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
        result = cfg.alpha * sim.aggression[i] + (1.0 - cfg.alpha) * nh
        result[i] = 0.0
        new_agg[i] = result
    for i, a in new_agg.items():
        sim.aggression[i] = a


def spread_raw_convex(sim, cfg, gamma):
    """Condition 2: Raw h^gamma, no normalization."""
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
        # Raw convex: pull = h^gamma (no normalization)
        pull = nh ** gamma
        result = cfg.alpha * sim.aggression[i] + (1.0 - cfg.alpha) * pull
        result[i] = 0.0
        for d in range(cfg.n_agents):
            if not sim.alive.get(d, False):
                result[d] = 0.0
        new_agg[i] = result
    for i, a in new_agg.items():
        sim.aggression[i] = a


def spread_full_ac(sim, cfg, gamma):
    """Condition 3: Full AC operator (convex redistribution, throughput conserved)."""
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
        H_i = float(np.sum(nh))
        if H_i > 0:
            sharpened = nh ** gamma
            Z = float(np.sum(sharpened))
            if Z > 0:
                attention = sharpened / Z
                pull = attention * H_i
            else:
                pull = np.zeros(cfg.n_agents, dtype=float)
        else:
            pull = np.zeros(cfg.n_agents, dtype=float)
        result = cfg.alpha * sim.aggression[i] + (1.0 - cfg.alpha) * pull
        result[i] = 0.0
        for d in range(cfg.n_agents):
            if not sim.alive.get(d, False):
                result[d] = 0.0
        new_agg[i] = result
    for i, a in new_agg.items():
        sim.aggression[i] = a


def main():
    print("=" * 80)
    print("TABLE 3: Operator Ablation")
    print("  N=50, alpha=0.15, no expulsion, 600 steps, 8 runs")
    print("  Conditions 2 and 3 use gamma=2.0")
    print("=" * 80)
    print()
    print(f"{'Cond':>4} {'Description':<40} {'Pk Gini':>8} {'Pk Modal':>9} "
          f"{'Fin Mass':>9} {'Max Agg':>9}")
    print("-" * 85)

    r1 = run_condition("1", spread_linear, 1.0)
    print(f"{'1':>4} {'Linear baseline (gamma=1)':<40} "
          f"{r1['peak_gini']:>8.3f} {r1['peak_modal']:>9.3f} "
          f"{r1['final_mass']:>9.0f} {r1['max_agg']:>9.3f}")

    r2 = run_condition("2", spread_raw_convex, 2.0)
    print(f"{'2':>4} {'Raw h^gamma (no normalization)':<40} "
          f"{r2['peak_gini']:>8.3f} {r2['peak_modal']:>9.3f} "
          f"{r2['final_mass']:>9.1f} {r2['max_agg']:>9.3f}")

    r3 = run_condition("3", spread_full_ac, 2.0)
    print(f"{'3':>4} {'Full AC (convex redistribution)':<40} "
          f"{r3['peak_gini']:>8.3f} {r3['peak_modal']:>9.3f} "
          f"{r3['final_mass']:>9.0f} {r3['max_agg']:>9.1f}")


if __name__ == "__main__":
    main()
