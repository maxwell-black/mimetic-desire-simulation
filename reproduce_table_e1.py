"""
Reproduce Table E1: Robustness Grid (Appendix E)
==================================================
Convergence outcomes across topologies, group sizes, and mimetic
susceptibility levels. AC variant, no expulsion.

Usage:  python reproduce_table_e1.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~8 minutes (9 conditions, some with N=100).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import networkx as nx
from girard_2x2_v3 import GirardConfig, GirardSimulation


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def run_condition(label, n_agents, k, alpha, gamma, topology,
                  n_runs=8, n_steps=600, seed0=42):
    """Run one condition and return summary stats."""
    all_peak_modal = []
    all_peak_gini = []
    all_t95 = []

    for r in range(n_runs):
        seed = seed0 + r * 1000
        cfg = GirardConfig(
            n_agents=n_agents, n_neighbors=k, rewire_prob=0.15,
            alpha=alpha, salience_exponent=gamma,
            expulsion_threshold=None, n_steps=n_steps,
            record_history=True, seed=seed,
        )
        sim = GirardSimulation(cfg, source="object", spread="attention")

        # Override graph topology if needed
        if topology == "barabasi_albert":
            sim.graph = nx.barabasi_albert_graph(n_agents, k, seed=seed)
            sim.distances = dict(nx.all_pairs_shortest_path_length(sim.graph))
            sim.prestige_base = {}
            for i, j in sim.graph.edges():
                sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
                sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
            sim.prestige = dict(sim.prestige_base)
        elif topology == "erdos_renyi":
            p_er = k / (n_agents - 1)
            sim.graph = nx.erdos_renyi_graph(n_agents, p_er, seed=seed)
            sim.distances = dict(nx.all_pairs_shortest_path_length(sim.graph))
            sim.prestige_base = {}
            for i, j in sim.graph.edges():
                sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
                sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
            sim.prestige = dict(sim.prestige_base)
        elif topology == "complete":
            sim.graph = nx.complete_graph(n_agents)
            sim.distances = dict(nx.all_pairs_shortest_path_length(sim.graph))
            sim.prestige_base = {}
            for i, j in sim.graph.edges():
                sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
                sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
            sim.prestige = dict(sim.prestige_base)
        # else: watts_strogatz (default)

        sim.run()

        modal = sim.history["modal_agreement"]
        gini = sim.history["aggression_gini"]
        all_peak_modal.append(max(modal))
        all_peak_gini.append(max(gini))
        all_t95.append(time_to_95(modal))

    conv_rate = sum(1 for t in all_t95 if t is not None) / n_runs
    converging = [t for t in all_t95 if t is not None]
    med_t95 = float(np.median(converging)) if converging else None

    return {
        'conv_rate': conv_rate,
        'med_t95': med_t95,
        'peak_gini': float(np.mean(all_peak_gini)),
    }


def main():
    conditions = [
        ("Watts-Strogatz",  20,  6, 0.15, 2.0, "watts_strogatz"),
        ("Watts-Strogatz",  50,  6, 0.15, 2.0, "watts_strogatz"),
        ("Watts-Strogatz", 100,  6, 0.15, 2.0, "watts_strogatz"),
        ("Barabasi-Albert",  50,  3, 0.15, 2.0, "barabasi_albert"),
        ("Erdos-Renyi",      50,  6, 0.15, 2.0, "erdos_renyi"),
        ("Complete",         50, 49, 0.15, 2.0, "complete"),
        ("Watts-Strogatz",   50,  6, 0.50, 2.0, "watts_strogatz"),
        ("Watts-Strogatz",   50,  6, 0.85, 1.5, "watts_strogatz"),
        ("Watts-Strogatz",   50,  6, 0.85, 2.0, "watts_strogatz"),
    ]

    print("=" * 90)
    print("TABLE E1: Robustness Grid")
    print("  AC variant, no expulsion, 600 steps, 8 runs per condition")
    print("=" * 90)
    print()
    print(f"{'Topology':<18} {'N':>3} {'k':>3} {'alpha':>6} {'gamma':>6} "
          f"{'Conv%':>6} {'t_95':>6} {'Pk Gini':>8}")
    print("-" * 65)

    for label, n, k, alpha, gamma, topo in conditions:
        print(f"  Running {label} N={n} a={alpha}...", end="", flush=True)
        r = run_condition(label, n, k, alpha, gamma, topo)
        t95_str = f"{r['med_t95']:.0f}" if r['med_t95'] is not None else "--"
        print(f"\r{label:<18} {n:>3} {k:>3} {alpha:>6.2f} {gamma:>6.1f} "
              f"{r['conv_rate']*100:>5.0f}% {t95_str:>6} {r['peak_gini']:>8.3f}")


if __name__ == "__main__":
    main()
