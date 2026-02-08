"""
unanimity_trigger_traces_full.py
=================================
Save full modal-agreement timeseries for figure generation.

Conditions:
  A) Unanimity-triggered, N=50:  gamma = 1.05, 1.50, 2.00
  B) Unanimity-triggered, N=200: gamma = 1.05, 2.00
     (confirms whether self-exhaustion disappears at large N)
  C) Accumulation-triggered, N=50: gamma=2.0, tau=500
     (for direct visual comparison with unanimity trigger)

Run from repo root:
    python unanimity_trigger_traces_full.py 2>&1 | tee traces_full_results.txt

Runtime: ~10-15 minutes.
Outputs: unanimity_trigger_traces_full.npz (for plotting)
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation


def get_modal_target(sim):
    alive = sim._alive_ids()
    if len(alive) < 2:
        return 0.0, None
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
        return 0.0, None
    counts = Counter(top_targets)
    modal_target, modal_count = counts.most_common(1)[0]
    return modal_count / len(top_targets), modal_target


def compute_modal_agreement_external(sim):
    """Modal agreement without target ID (for accumulation trigger)."""
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


def run_unanimity_triggered(n_agents, gamma, n_steps=800, seed=42,
                             unanimity_threshold=0.95, cooldown=5,
                             k_override=None):
    k = k_override or max(6, min(int(n_agents * 0.12), 20))
    if k % 2 == 1:
        k -= 1

    cfg = GirardConfig(
        n_agents=n_agents, n_neighbors=k, rewire_prob=0.15,
        alpha=0.15, salience_exponent=gamma,
        expulsion_threshold=None,
        n_steps=n_steps, record_history=False, seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_series = []
    expulsion_steps = []
    alive_counts = []
    steps_since_expulsion = cooldown + 1

    for step in range(n_steps):
        ma, mt = get_modal_target(sim)
        modal_series.append(ma)
        alive_counts.append(len(sim._alive_ids()))

        if (ma >= unanimity_threshold and
            steps_since_expulsion > cooldown and
            mt is not None and
            len(sim._alive_ids()) > 2):
            sim.alive[mt] = False
            sim.aggression[mt, :] = 0.0
            sim.aggression[:, mt] = 0.0
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
        if hasattr(sim, 'step_status_update'):
            sim.step_status_update()
        sim.step_num += 1

    return modal_series, expulsion_steps, alive_counts


def run_accumulation_triggered(n_agents, gamma, tau, n_steps=800, seed=42):
    """Run with the paper's original accumulation trigger for comparison."""
    k = max(6, min(int(n_agents * 0.12), 20))
    if k % 2 == 1:
        k -= 1

    cfg = GirardConfig(
        n_agents=n_agents, n_neighbors=k, rewire_prob=0.15,
        alpha=0.15, salience_exponent=gamma,
        expulsion_threshold=tau,
        n_steps=n_steps, record_history=False, seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_series = []
    expulsion_steps = []
    alive_counts = []

    for step in range(n_steps):
        ma = compute_modal_agreement_external(sim)
        modal_series.append(ma)
        alive_counts.append(len(sim._alive_ids()))

        alive_before = set(sim._alive_ids())

        sim._refresh_prestige()
        sim.step_desire()
        sim.step_aggression_source()
        sim._refresh_prestige()
        sim.step_aggression_spread()
        sim.step_decay()

        # Check accumulation trigger
        _, received = sim._received_aggression_vector()
        alive = sim._alive_ids()
        if len(alive) > 1 and len(received) > 0:
            max_r = float(np.max(received))
            if max_r >= tau:
                expulsion_steps.append(step)
                sim.step_expulsion()

        if hasattr(sim, 'step_status_update'):
            sim.step_status_update()
        sim.step_num += 1

    return modal_series, expulsion_steps, alive_counts


def main():
    traces = {}

    # --- A) Unanimity-triggered, N=50 ---
    for gamma in [1.05, 1.50, 2.00]:
        label = f"ut_n50_g{str(gamma).replace('.','')}"
        print(f"Running: unanimity trigger, N=50, gamma={gamma}...")
        m, e, a = run_unanimity_triggered(50, gamma, n_steps=800, seed=42)
        traces[f"{label}_modal"] = np.array(m, dtype=np.float32)
        traces[f"{label}_exps"] = np.array(e, dtype=np.int32)
        traces[f"{label}_alive"] = np.array(a, dtype=np.int32)
        print(f"  {len(e)} expulsions, final alive={a[-1]}")

    # --- B) Unanimity-triggered, N=200 ---
    for gamma in [1.05, 2.00]:
        label = f"ut_n200_g{str(gamma).replace('.','')}"
        print(f"Running: unanimity trigger, N=200, gamma={gamma}...")
        m, e, a = run_unanimity_triggered(200, gamma, n_steps=1500, seed=42)
        traces[f"{label}_modal"] = np.array(m, dtype=np.float32)
        traces[f"{label}_exps"] = np.array(e, dtype=np.int32)
        traces[f"{label}_alive"] = np.array(a, dtype=np.int32)
        print(f"  {len(e)} expulsions, final alive={a[-1]}")
        if e:
            print(f"  First exp: t={e[0]}, Last exp: t={e[-1]}")
            if len(m) > e[-1] + 100:
                # Check if it reconverged after last expulsion
                post = m[e[-1]+1:]
                reconverged = any(v >= 0.95 for v in post[:200])
                print(f"  Reconverged after last exp: {reconverged}")

    # --- C) Accumulation-triggered comparison, N=50 ---
    print(f"Running: accumulation trigger, N=50, gamma=2.0, tau=500...")
    m, e, a = run_accumulation_triggered(50, 2.0, 500.0, n_steps=800, seed=42)
    traces["accum_n50_g20_modal"] = np.array(m, dtype=np.float32)
    traces["accum_n50_g20_exps"] = np.array(e, dtype=np.int32)
    traces["accum_n50_g20_alive"] = np.array(a, dtype=np.int32)
    print(f"  {len(e)} expulsions, final alive={a[-1]}")

    # --- D) Bonus: unanimity trigger at N=200, gamma=2.0 with MORE seeds ---
    print(f"\nSelf-exhaustion test: N=200, gamma=2.0, 8 seeds...")
    for r in range(8):
        seed = 42 + r * 1000
        m, e, a = run_unanimity_triggered(200, 2.0, n_steps=1500, seed=seed)
        last_reconv = "N/A"
        if e:
            post = m[e[-1]+1:]
            if any(v >= 0.95 for v in post[:300]):
                last_reconv = "YES"
            else:
                last_reconv = "NO (self-exhausted)"
        print(f"  seed={seed}: {len(e)} exp, alive={a[-1]}, "
              f"reconverge after last: {last_reconv}")

    # Save
    np.savez_compressed('unanimity_trigger_traces_full.npz', **traces)
    print(f"\nSaved {len(traces)} arrays to unanimity_trigger_traces_full.npz")
    print("Keys:", sorted(traces.keys()))


if __name__ == "__main__":
    main()
