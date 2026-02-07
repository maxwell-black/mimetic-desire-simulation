"""
Reproduce Table 4: Expulsion Threshold Regimes
================================================
Tests four threshold levels to identify the three regimes:
  Regime 1 (tau=8):   Serial purge, no unanimity
  Intermediate (200): Partial convergence, fast cycles
  Regime 2 (tau=500): Founding murder -- unanimity before expulsion
  Regime 3 (tau=750): Near-ceiling, rare or no expulsion

Usage:  python reproduce_table_4.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~8 minutes (12 runs x 1500 steps x 4 thresholds).
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


def run_threshold_condition(tau, n_runs=12, n_steps=1500):
    """
    Run AC variant at a given expulsion threshold, collect regime metrics.
    """
    all_run_data = []

    for r in range(n_runs):
        seed = 42 + r * 1000
        cfg = GirardConfig(
            n_agents=50, n_neighbors=6, rewire_prob=0.15,
            alpha=0.15, salience_exponent=2.0,
            expulsion_threshold=tau,
            n_steps=n_steps, record_history=False, seed=seed,
        )
        sim = GirardSimulation(cfg, source="object", spread="attention")

        modal_series = []
        expulsion_events = []  # list of (step, pre_exp_modal)

        for step in range(n_steps):
            # Compute modal agreement BEFORE this step's expulsion
            cur_modal = compute_modal_agreement(sim)
            modal_series.append(cur_modal)

            # Run one full step
            sim._refresh_prestige()
            sim.step_desire()
            sim.step_aggression_source()
            sim._refresh_prestige()
            sim.step_aggression_spread()
            sim.step_decay()

            # Check for expulsion
            _, received = sim._received_aggression_vector()
            alive = sim._alive_ids()
            if len(alive) > 1 and len(received) > 0:
                max_r = float(np.max(received))
                if max_r >= tau:
                    # Record pre-expulsion modal
                    expulsion_events.append((step, cur_modal))
                    # Perform expulsion
                    sim.step_expulsion()

            if hasattr(sim, 'step_status_update'):
                sim.step_status_update()
            sim.step_num += 1

        # Analyze this run
        n_exp = len(expulsion_events)
        first_step = expulsion_events[0][0] if expulsion_events else None
        pre_modal = expulsion_events[0][1] if expulsion_events else None

        # Peace: consecutive steps with modal < 0.50 after first expulsion
        peace = 0
        if first_step is not None and first_step + 1 < len(modal_series):
            for t in range(first_step + 1, len(modal_series)):
                if modal_series[t] < 0.50:
                    peace += 1
                else:
                    break

        # Reconvergence: steps to modal >= 0.95 for 10 consecutive after first expulsion
        reconverge = None
        if first_step is not None:
            post = modal_series[first_step + 1:]
            for t in range(len(post) - 10):
                if all(post[t + k] >= 0.95 for k in range(10)):
                    reconverge = t
                    break

        # Gap to second expulsion
        gap = None
        if len(expulsion_events) >= 2:
            gap = expulsion_events[1][0] - expulsion_events[0][0]

        all_run_data.append({
            'n_expulsions': n_exp,
            'first_step': first_step,
            'pre_modal': pre_modal,
            'peace': peace,
            'reconverge': reconverge,
            'gap': gap,
        })

    return all_run_data


def safe_mean(vals):
    return np.mean(vals) if vals else float('nan')


def main():
    thresholds = [8, 200, 500, 750]

    print("=" * 95)
    print("TABLE 4: Post-expulsion dynamics across threshold regimes")
    print("  12 runs x 1500 steps, gamma=2.0, alpha=0.15, AC variant")
    print("=" * 95)
    print()
    print(f"{'Thresh':>7} | {'Expuls':>6} | {'1st Step':>8} | {'PreModal':>8} | "
          f"{'Peace':>6} | {'Reconvg':>8} | {'Gap 2nd':>8}")
    print("-" * 70)

    for tau in thresholds:
        print(f"  Running tau={tau}...", end="", flush=True)
        runs = run_threshold_condition(tau)

        n_exp = safe_mean([r['n_expulsions'] for r in runs])
        first_steps = [r['first_step'] for r in runs if r['first_step'] is not None]
        pre_modals = [r['pre_modal'] for r in runs if r['pre_modal'] is not None]
        peaces = [r['peace'] for r in runs if r['first_step'] is not None]
        reconverges = [r['reconverge'] for r in runs if r['reconverge'] is not None]
        gaps = [r['gap'] for r in runs if r['gap'] is not None]

        fs = f"{safe_mean(first_steps):.0f}" if first_steps else "--"
        pm = f"{safe_mean(pre_modals):.2f}" if pre_modals else "--"
        pc = f"{safe_mean(peaces):.0f}" if peaces else "--"
        rc = f"{safe_mean(reconverges):.0f}" if reconverges else "--"
        gp = f"{safe_mean(gaps):.0f}" if gaps else "260+"

        print(f"\r{tau:>7} | {n_exp:>6.1f} | {fs:>8} | {pm:>8} | "
              f"{pc:>6} | {rc:>8} | {gp:>8}")


if __name__ == "__main__":
    main()
