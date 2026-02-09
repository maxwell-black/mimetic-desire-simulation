"""
ER Target Diagnostic
====================
Determine whether the Erdos-Renyi 0% convergence / 0.995 peak modal result
is driven by:
  (1) Target rotation: modal target identity changes rapidly, or
  (2) Agreement oscillation: modal target is stable but agreement fluctuates.

Runs a few ER seeds and complete-graph seeds at N=200, AC variant, gamma=2.0,
recording the modal target identity at each step.

Also runs WS for comparison.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import networkx as nx
from girard_2x2_v3 import GirardConfig, GirardSimulation
from collections import Counter


def build_graph(graph_type, n, seed):
    rng = np.random.default_rng(seed)
    k = max(6, min(int(n * 0.12), 20))
    if graph_type == "erdos_renyi":
        p = k / (n - 1)
        G = nx.erdos_renyi_graph(n, p, seed=seed)
        if not nx.is_connected(G):
            comps = list(nx.connected_components(G))
            for i in range(1, len(comps)):
                u = rng.choice(list(comps[i-1]))
                v = rng.choice(list(comps[i]))
                G.add_edge(u, v)
        return G
    elif graph_type == "complete":
        return nx.complete_graph(n)
    elif graph_type == "watts_strogatz":
        if k % 2 == 1:
            k -= 1
        return nx.watts_strogatz_graph(n, k, 0.15, seed=seed)
    else:
        raise ValueError(graph_type)


def inject_graph(sim, G):
    """Replace the sim's graph with a custom one."""
    sim.graph = G
    sim.distances = dict(nx.all_pairs_shortest_path_length(G))
    sim.prestige_base = {}
    for i, j in G.edges():
        sim.prestige_base[(i, j)] = float(sim.rng.uniform(0.1, 1.0))
        sim.prestige_base[(j, i)] = float(sim.rng.uniform(0.1, 1.0))
    sim.prestige = dict(sim.prestige_base)


def get_modal_target(sim):
    """Extract modal target identity and agreement from current state."""
    alive = sim._alive_ids()
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
        return None, 0.0, 0

    counts = Counter(top_targets)
    modal_target = counts.most_common(1)[0][0]
    agreement = counts[modal_target] / len(top_targets)
    return modal_target, agreement, len(top_targets)


def run_diagnostic(graph_type, n_agents, seed, n_steps=5000, gamma=2.0):
    """Run one seed, return step-by-step modal target trace."""
    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=max(6, min(int(n_agents * 0.12), 20)),
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=gamma,
        expulsion_threshold=8.0,
        n_steps=n_steps,
        record_history=True,
        seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    if graph_type != "watts_strogatz":
        G = build_graph(graph_type, n_agents, seed)
        inject_graph(sim, G)

    targets = []
    agreements = []

    for t in range(n_steps):
        sim.step()
        mt, ag, elig = get_modal_target(sim)
        targets.append(mt)
        agreements.append(ag)

        # Early stop if exhausted (silence > 500)
        alive_count = sum(1 for v in sim.alive.values() if v)
        if alive_count < 3:
            break

    return targets, agreements, sim


def analyze_trace(targets, agreements, label):
    """Compute rotation vs oscillation metrics."""
    # Filter out None entries (early steps before any aggression)
    valid = [(t, a) for t, a in zip(targets, agreements) if t is not None and a > 0.1]
    if not valid:
        print(f"  {label}: No valid data")
        return

    vt = [x[0] for x in valid]
    va = [x[1] for x in valid]

    # Target changes: how often does the modal target change identity?
    changes = sum(1 for i in range(1, len(vt)) if vt[i] != vt[i-1])
    change_rate = changes / max(1, len(vt) - 1)

    # High-agreement steps (>= 0.90)
    high_ag = [a for a in va if a >= 0.90]
    pct_high = len(high_ag) / len(va) * 100

    # Consecutive runs at >= 0.95 (the convergence criterion)
    max_consec_95 = 0
    cur = 0
    for a in va:
        if a >= 0.95:
            cur += 1
            max_consec_95 = max(max_consec_95, cur)
        else:
            cur = 0

    # Target tenure: how long does each modal target stay as modal?
    tenures = []
    cur_target = vt[0]
    cur_len = 1
    for i in range(1, len(vt)):
        if vt[i] == cur_target:
            cur_len += 1
        else:
            tenures.append(cur_len)
            cur_target = vt[i]
            cur_len = 1
    tenures.append(cur_len)

    # Agreement stats during high-agreement windows
    peak_ag = max(va)
    med_ag = np.median(va)

    # Find stretches where agreement > 0.90 and check if target is stable
    # within those stretches
    in_high = False
    high_stretch_targets = []
    cur_stretch = []
    for t_id, a in zip(vt, va):
        if a >= 0.90:
            cur_stretch.append(t_id)
        else:
            if cur_stretch:
                high_stretch_targets.append(cur_stretch)
                cur_stretch = []
    if cur_stretch:
        high_stretch_targets.append(cur_stretch)

    # In high-agreement stretches, how often does target change?
    high_changes = 0
    high_total = 0
    for stretch in high_stretch_targets:
        for i in range(1, len(stretch)):
            high_total += 1
            if stretch[i] != stretch[i-1]:
                high_changes += 1

    print(f"  {label}:")
    print(f"    Valid steps: {len(vt)}")
    print(f"    Target changes: {changes} ({change_rate:.4f}/step)")
    print(f"    Median tenure: {np.median(tenures):.0f} steps, "
          f"mean: {np.mean(tenures):.1f}, max: {max(tenures)}")
    print(f"    Peak agreement: {peak_ag:.4f}, median: {med_ag:.4f}")
    print(f"    Steps with agreement >= 0.90: {pct_high:.1f}%")
    print(f"    Max consecutive steps >= 0.95: {max_consec_95}")
    print(f"    High-agreement stretches (>=0.90): {len(high_stretch_targets)}")
    if high_total > 0:
        print(f"    Target changes WITHIN high-agreement stretches: "
              f"{high_changes}/{high_total} ({high_changes/high_total:.4f}/step)")
    else:
        print(f"    (No high-agreement stretches to analyze)")
    print(f"    Unique targets in trace: {len(set(vt))}")

    # Verdict
    if change_rate > 0.05 and max_consec_95 < 10:
        verdict = "ROTATION (target identity unstable)"
    elif change_rate < 0.01 and max_consec_95 < 10:
        verdict = "OSCILLATION (target stable, agreement fluctuates)"
    elif max_consec_95 >= 10:
        verdict = "CONVERGED"
    else:
        verdict = "MIXED (moderate rotation + moderate oscillation)"
    print(f"    >> VERDICT: {verdict}")
    return change_rate, max_consec_95, tenures


def main():
    N = 200
    SEEDS = [42, 1042, 2042, 3042]
    N_STEPS = 5000
    GAMMA = 2.0

    for topo in ["erdos_renyi", "complete", "watts_strogatz"]:
        print(f"\n{'='*80}")
        print(f"TOPOLOGY: {topo}, N={N}, gamma={GAMMA}")
        print(f"{'='*80}")

        for seed in SEEDS:
            print(f"\n  --- seed={seed} ---")
            targets, agreements, sim = run_diagnostic(topo, N, seed, N_STEPS, GAMMA)
            analyze_trace(targets, agreements, f"{topo}/seed={seed}")

            # Also report final state
            n_alive = sum(1 for v in sim.alive.values() if v)
            n_exp = len(sim.history["expulsion_events"])
            print(f"    Expulsions: {n_exp}, Alive: {n_alive}")


if __name__ == "__main__":
    main()
