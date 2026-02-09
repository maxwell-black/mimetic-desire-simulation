"""
exp5_topology_n200.py
=====================
Topology robustness test at N=200: does scapegoat convergence
and self-exhaustion hold across different network structures?

Graph types:
  - Watts-Strogatz (small-world, default)
  - Barabasi-Albert (scale-free)
  - Erdos-Renyi (random)
  - Complete graph (mean-field limit)

AC variant (object source, attention spread), gamma=2.0,
10 seeds per topology, 5000 steps with expulsion.

Extends existing N=50 topology robustness to the population
size where self-exhaustion dynamics are confirmed.

Run from repo root:
    python exp5_topology_n200.py 2>&1 | tee exp5_topology_n200_results.txt

Estimated runtime: 3-5 hours.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import networkx as nx
from girard_2x2_v3 import GirardConfig, GirardSimulation


def build_custom_graph(graph_type, n_agents, seed):
    """Build a graph of the specified type."""
    rng = np.random.default_rng(seed)

    if graph_type == "watts_strogatz":
        k = max(6, min(int(n_agents * 0.12), 20))
        if k % 2 == 1:
            k -= 1
        return nx.watts_strogatz_graph(n_agents, k, 0.15, seed=seed)

    elif graph_type == "barabasi_albert":
        # m=3 gives mean degree ~6 (comparable to WS k=6)
        return nx.barabasi_albert_graph(n_agents, 3, seed=seed)

    elif graph_type == "erdos_renyi":
        # p chosen to match mean degree ~6: p = k/(n-1)
        target_k = max(6, min(int(n_agents * 0.12), 20))
        p = target_k / (n_agents - 1)
        G = nx.erdos_renyi_graph(n_agents, p, seed=seed)
        # Ensure connected
        if not nx.is_connected(G):
            # Add edges to connect components
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


def run_with_topology(graph_type, n_agents, gamma, n_steps, seed):
    """
    Run simulation with a custom graph topology.
    We build the graph, then inject it into the simulation.
    """
    # Build config with WS defaults (graph will be replaced)
    k_ws = max(6, min(int(n_agents * 0.12), 20))
    if k_ws % 2 == 1:
        k_ws -= 1

    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=k_ws,
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=gamma,
        expulsion_threshold=8.0,
        n_steps=n_steps,
        record_history=True,
        seed=seed,
    )

    sim = GirardSimulation(cfg, source="object", spread="attention")

    # Replace graph if not watts_strogatz
    if graph_type != "watts_strogatz":
        G = build_custom_graph(graph_type, n_agents, seed)
        sim.graph = G
        # Recompute distances
        sim.distances = dict(nx.all_pairs_shortest_path_length(G))
        # Reinitialize prestige weights for new edges
        sim.prestige_base = {}
        for i, j in G.edges():
            sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
            sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
        sim.prestige = dict(sim.prestige_base)

    sim.run()

    # Extract metrics
    exp_events = sim.history["expulsion_events"]
    exp_times = [e[0] for e in exp_events]
    n_exp = len(exp_events)
    n_alive = sum(1 for v in sim.alive.values() if v)
    pct_consumed = (n_agents - n_alive) / n_agents * 100.0
    silence = (n_steps - exp_times[-1]) if exp_times else n_steps

    # Convergence
    converged = False
    if sim.history["modal_agreement"]:
        modal = sim.history["modal_agreement"]
        for t in range(len(modal) - 10):
            if all(modal[t + k] >= 0.95 for k in range(10)):
                converged = True
                break

    peak_modal = max(sim.history["modal_agreement"]) if sim.history["modal_agreement"] else 0.0
    peak_gini = max(sim.history["aggression_gini"]) if sim.history["aggression_gini"] else 0.0
    exhausted = silence >= 500 and n_exp > 0

    # Graph stats
    mean_degree = np.mean([d for _, d in sim.graph.degree()])
    clustering = nx.average_clustering(sim.graph)

    return {
        "n_exp": n_exp,
        "n_alive": n_alive,
        "pct_consumed": pct_consumed,
        "converged": converged,
        "peak_modal": peak_modal,
        "peak_gini": peak_gini,
        "exhausted": exhausted,
        "silence": silence,
        "mean_degree": mean_degree,
        "clustering": clustering,
    }


def main():
    N_AGENTS = 200
    N_STEPS = 5000
    N_SEEDS = 10
    GAMMA = 2.0
    SEED_BASE = 42
    SEED_STRIDE = 1000

    topologies = ["watts_strogatz", "barabasi_albert", "erdos_renyi", "complete"]

    out_lines = []
    def log(s=""):
        print(s, flush=True)
        out_lines.append(s)

    log("=" * 120)
    log(f"TOPOLOGY ROBUSTNESS AT N={N_AGENTS}")
    log(f"AC variant, gamma={GAMMA}, Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 120)

    # Summary table
    log(f"\n{'Topology':<18} {'MeanDeg':>8} {'Clust':>7} "
        f"{'MedExp':>7} {'Consumed':>9} {'Conv%':>6} "
        f"{'PeakModal':>10} {'Exhausted':>10}")
    log("-" * 95)

    all_results = {}

    for topo in topologies:
        results = []
        t0 = time.time()

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            res = run_with_topology(topo, N_AGENTS, GAMMA, N_STEPS, seed)
            results.append(res)

            conv_str = "CONV" if res["converged"] else "----"
            exh_str = "EXH" if res["exhausted"] else "cyc"
            print(f"    {topo} seed={seed}: {res['n_exp']} exp, "
                  f"{conv_str}, {exh_str}", flush=True)

        elapsed = time.time() - t0

        med_exp = np.median([r["n_exp"] for r in results])
        med_consumed = np.median([r["pct_consumed"] for r in results])
        conv_rate = sum(1 for r in results if r["converged"]) / N_SEEDS * 100
        med_peak_modal = np.median([r["peak_modal"] for r in results])
        n_exhausted = sum(1 for r in results if r["exhausted"])
        med_degree = np.median([r["mean_degree"] for r in results])
        med_cluster = np.median([r["clustering"] for r in results])

        log(f"{topo:<18} {med_degree:>8.1f} {med_cluster:>7.3f} "
            f"{med_exp:>7.0f} {med_consumed:>8.1f}% {conv_rate:>5.0f}% "
            f"{med_peak_modal:>10.3f} "
            f"{n_exhausted:>5}/{N_SEEDS}  ({elapsed:.0f}s)")

        all_results[topo] = results

    # Detailed per-topology
    for topo in topologies:
        results = all_results[topo]
        log(f"\n{'=' * 80}")
        log(f"DETAILED: {topo}")
        log(f"{'=' * 80}")

        for r in results:
            exh_str = "EXH" if r["exhausted"] else "cyc"
            conv_str = "CONV" if r["converged"] else "----"
            log(f"  exp={r['n_exp']:>3}, alive={r['n_alive']:>3}, "
                f"consumed={r['pct_consumed']:>5.1f}%, "
                f"peak_modal={r['peak_modal']:.3f}, "
                f"gini={r['peak_gini']:.3f}, "
                f"silence={r['silence']:>5}, {conv_str} {exh_str}")

    # Robustness verdict
    log(f"\n\n{'=' * 120}")
    log("ROBUSTNESS VERDICT")
    log(f"{'=' * 120}")

    for topo in topologies:
        results = all_results[topo]
        n_conv = sum(1 for r in results if r["converged"])
        n_exh = sum(1 for r in results if r["exhausted"])
        n_exp_med = np.median([r["n_exp"] for r in results])

        if n_conv >= N_SEEDS * 0.8 and n_exh >= N_SEEDS * 0.8:
            verdict = "FULL CONFIRMATION (convergence + exhaustion)"
        elif n_conv >= N_SEEDS * 0.5:
            verdict = f"PARTIAL (convergence {n_conv}/{N_SEEDS}, exhaustion {n_exh}/{N_SEEDS})"
        elif n_exp_med > 0:
            verdict = f"EXPULSION WITHOUT CONVERGENCE ({n_conv}/{N_SEEDS} converged)"
        else:
            verdict = "NO SCAPEGOATING"

        log(f"  {topo:<18}: {verdict}")

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("exp5_topology_n200_results_copy.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    log("Saved to exp5_topology_n200_results_copy.txt")


if __name__ == "__main__":
    main()
