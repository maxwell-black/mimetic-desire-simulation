"""
exp_small_n_topology.py
========================
Topology robustness at small N: does the founding murder mechanism
work across network structures at proto-group sizes?

At N=5-10, WS is nearly complete anyway. At N=20-30, topology starts
mattering. We test all four topologies at N={15, 20, 30, 40}.

Graph types:
  - Watts-Strogatz (small-world, default)
  - Barabasi-Albert (scale-free)
  - Erdos-Renyi (random)
  - Complete graph (mean-field limit)

AC variant, gamma=2.0, adaptive unanimity trigger.
10 seeds per (topology, N), 5000 steps.

Run:
    python exp_small_n_topology.py 2>&1 | Tee-Object -FilePath exp_small_n_topology_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
"""

import sys, os, time
import numpy as np
import networkx as nx

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation
from small_n_utils import (adaptive_k, adaptive_unanimity_threshold,
                           get_modal_target, count_fragments)


def build_graph(graph_type, n_agents, seed):
    """Build a graph of specified type, safe for small N."""
    rng = np.random.default_rng(seed)
    k = adaptive_k(n_agents)

    if graph_type == "watts_strogatz":
        return nx.watts_strogatz_graph(n_agents, k, 0.15, seed=seed)

    elif graph_type == "barabasi_albert":
        m = min(3, n_agents - 1)  # BA needs m < n
        return nx.barabasi_albert_graph(n_agents, m, seed=seed)

    elif graph_type == "erdos_renyi":
        p = k / max(1, n_agents - 1)
        p = min(p, 1.0)
        G = nx.erdos_renyi_graph(n_agents, p, seed=seed)
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            for i in range(1, len(components)):
                u = rng.choice(list(components[i - 1]))
                v = rng.choice(list(components[i]))
                G.add_edge(u, v)
        return G

    elif graph_type == "complete":
        return nx.complete_graph(n_agents)

    else:
        raise ValueError(f"Unknown graph type: {graph_type}")


def inject_graph(sim, G):
    """Replace sim's graph with custom one."""
    sim.graph = G
    sim.distances = dict(nx.all_pairs_shortest_path_length(G))
    sim.prestige_base = {}
    for i, j in G.edges():
        sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
        sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
    sim.prestige = dict(sim.prestige_base)


def run_topology(graph_type, n_agents, gamma, n_steps, seed, cooldown=5):
    """Run one simulation with custom topology and adaptive unanimity trigger."""
    k = adaptive_k(n_agents)

    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=k,
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=gamma,
        expulsion_threshold=None,
        n_steps=n_steps,
        record_history=False,
        seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    # Inject custom graph
    if graph_type != "watts_strogatz":
        G = build_graph(graph_type, n_agents, seed)
        inject_graph(sim, G)

    # Graph stats before simulation
    mean_degree = np.mean([d for _, d in sim.graph.degree()])
    clustering = nx.average_clustering(sim.graph)

    modal_series = []
    expulsion_steps = []
    steps_since_expulsion = cooldown + 1
    peak_modal = 0.0

    for step in range(n_steps):
        ma, mt = get_modal_target(sim)
        modal_series.append(ma)
        if ma > peak_modal:
            peak_modal = ma

        n_alive_now = len(sim._alive_ids())
        thresh = adaptive_unanimity_threshold(n_alive_now)
        if (ma >= thresh and
            steps_since_expulsion > cooldown and
            mt is not None and
            n_alive_now > 2):
            sim.alive[mt] = False
            for other in sim._alive_ids():
                sim.aggression[other][mt] = 0.0
            sim.aggression[mt][:] = 0.0
            expulsion_steps.append(step)
            steps_since_expulsion = 0
        else:
            steps_since_expulsion += 1

        sim._refresh_prestige()
        sim.step_desire()
        sim.step_aggression_source()
        sim._refresh_prestige()
        sim.step_aggression_spread()
        sim.step_decay()
        sim.step_status_update()
        sim.step_num += 1

    n_alive = sum(1 for v in sim.alive.values() if v)
    n_exp = len(expulsion_steps)
    pct_consumed = (n_agents - n_alive) / n_agents * 100.0

    # Self-exhaustion
    status = "no_expulsions"
    if n_exp > 0:
        last_exp = expulsion_steps[-1]
        remaining = n_steps - last_exp - 1
        final_thresh = adaptive_unanimity_threshold(n_alive)
        reconverged = any(modal_series[t] >= final_thresh
                         for t in range(last_exp + 1, n_steps))
        if reconverged:
            status = "still_cycling"
        elif remaining >= 500:
            status = "genuine_exhaustion"
        else:
            status = "censored"

    # Convergence (10 consecutive steps above adaptive threshold)
    orig_thresh = adaptive_unanimity_threshold(n_agents)
    converged = False
    for t in range(len(modal_series) - 10):
        if all(modal_series[t + i] >= orig_thresh for i in range(10)):
            converged = True
            break

    # Fragmentation
    n_frags, largest = count_fragments(sim)

    return {
        "n_exp": n_exp,
        "n_alive": n_alive,
        "pct_consumed": pct_consumed,
        "converged": converged,
        "peak_modal": peak_modal,
        "status": status,
        "mean_degree": mean_degree,
        "clustering": clustering,
        "n_fragments": n_frags,
        "largest_fragment": largest,
    }


def main():
    Ns = [15, 20, 30, 40]
    GAMMA = 2.0
    N_STEPS = 5000
    N_SEEDS = 10
    SEED_BASE = 42
    SEED_STRIDE = 1000

    topologies = ["watts_strogatz", "barabasi_albert", "erdos_renyi", "complete"]

    print("=" * 130)
    print(f"SMALL-N TOPOLOGY ROBUSTNESS")
    print(f"AC variant, gamma={GAMMA}, Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    print(f"Ns: {Ns}")
    print(f"Trigger: adaptive unanimity threshold")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 130)

    all_results = {}

    for N in Ns:
        k = adaptive_k(N)
        thresh = adaptive_unanimity_threshold(N)
        print(f"\n{'=' * 130}")
        print(f"  N={N}, k={k}, threshold={thresh:.3f}")
        print(f"{'=' * 130}")

        print(f"\n  {'Topology':<18} {'MeanDeg':>8} {'Clust':>7} "
              f"{'MedExp':>7} {'Consumed':>9} {'Conv%':>6} "
              f"{'PkModal':>8} {'Exh':>5} {'Cyc':>5} {'NoExp':>6} "
              f"{'Frags':>6} {'LrgFrag':>8}")
        print(f"  " + "-" * 110)

        for topo in topologies:
            results = []
            t0 = time.time()

            for r in range(N_SEEDS):
                seed = SEED_BASE + r * SEED_STRIDE
                res = run_topology(topo, N, GAMMA, N_STEPS, seed)
                results.append(res)

            elapsed = time.time() - t0

            med_exp = np.median([r["n_exp"] for r in results])
            med_consumed = np.median([r["pct_consumed"] for r in results])
            conv_rate = sum(1 for r in results if r["converged"]) / N_SEEDS * 100
            med_pk = np.median([r["peak_modal"] for r in results])
            n_exh = sum(1 for r in results if r["status"] == "genuine_exhaustion")
            n_cyc = sum(1 for r in results if r["status"] == "still_cycling")
            n_noexp = sum(1 for r in results if r["status"] == "no_expulsions")
            med_deg = np.median([r["mean_degree"] for r in results])
            med_clust = np.median([r["clustering"] for r in results])
            med_frags = np.median([r["n_fragments"] for r in results])
            med_lrg = np.median([r["largest_fragment"] for r in results])

            print(f"  {topo:<18} {med_deg:>8.1f} {med_clust:>7.3f} "
                  f"{med_exp:>7.0f} {med_consumed:>8.1f}% {conv_rate:>5.0f}% "
                  f"{med_pk:>8.3f} {n_exh:>5} {n_cyc:>5} {n_noexp:>6} "
                  f"{med_frags:>6.0f} {med_lrg:>8.0f}  ({elapsed:.0f}s)")

            all_results[(N, topo)] = results

    # Cross-N comparison per topology
    print(f"\n\n{'=' * 130}")
    print("CROSS-N COMPARISON: Viability index by topology")
    print("  Generative = genuine_exhaustion AND pct_consumed < 50%")
    print(f"{'=' * 130}")

    print(f"\n  {'Topology':<18}", end="")
    for N in Ns:
        print(f"  {'N='+str(N):>8}", end="")
    print()
    print(f"  " + "-" * (18 + 10 * len(Ns)))

    for topo in topologies:
        print(f"  {topo:<18}", end="")
        for N in Ns:
            results = all_results.get((N, topo), [])
            if results:
                gen = sum(1 for r in results
                          if r["status"] == "genuine_exhaustion"
                          and r["pct_consumed"] < 50)
                pct = gen / len(results) * 100
                print(f"  {pct:>7.0f}%", end="")
            else:
                print(f"  {'--':>8}", end="")
        print()

    # Verdict
    print(f"\n\n{'=' * 130}")
    print("ROBUSTNESS VERDICTS")
    print(f"{'=' * 130}")

    for N in Ns:
        print(f"\n  N={N}:")
        for topo in topologies:
            results = all_results.get((N, topo), [])
            n_exh = sum(1 for r in results if r["status"] == "genuine_exhaustion")
            n_cyc = sum(1 for r in results if r["status"] == "still_cycling")
            n_conv = sum(1 for r in results if r["converged"])
            if n_exh >= N_SEEDS * 0.8:
                verdict = "FULL CONFIRMATION (exhaustion)"
            elif n_exh >= N_SEEDS * 0.4:
                verdict = f"PARTIAL ({n_exh}/{N_SEEDS} exhausted)"
            elif n_conv >= N_SEEDS * 0.5:
                verdict = f"CONVERGENCE WITHOUT EXHAUSTION ({n_conv}/{N_SEEDS})"
            elif n_cyc >= N_SEEDS * 0.5:
                verdict = "STILL CYCLING"
            else:
                verdict = "NO SCAPEGOATING"
            print(f"    {topo:<18}: {verdict}")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
