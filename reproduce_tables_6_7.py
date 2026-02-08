"""
Reproduce Tables 6 and 7: Violence topologies under unanimity-triggered expulsion
==================================================================================
Table 6: N x gamma sweep with unanimity trigger.
Table 7: Detailed cycle structure for selected conditions.

Usage:  python reproduce_tables_6_7.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~30-45 minutes (N=500 is slow).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation


def get_modal_target(sim):
    """Return (modal_agreement, modal_target_id)."""
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


def run_unanimity_triggered(n_agents, gamma, n_steps=1500, seed=42,
                             unanimity_threshold=0.95, cooldown=5):
    """Run AC variant with unanimity-triggered expulsion."""
    k = max(6, min(int(n_agents * 0.12), 20))
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
    steps_since_expulsion = cooldown + 1

    for step in range(n_steps):
        ma, mt = get_modal_target(sim)
        modal_series.append(ma)

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

    return modal_series, expulsion_steps


def measure_cycles(modal_series, expulsion_steps, peace_threshold=0.50):
    """Measure peace durations and reconvergence times after each expulsion."""
    results = []
    for i, es in enumerate(expulsion_steps):
        peace_dur = 0
        for t in range(es + 1, len(modal_series)):
            if modal_series[t] < peace_threshold:
                peace_dur += 1
            else:
                break

        reconverge = None
        for t in range(es + 1, len(modal_series)):
            if modal_series[t] >= 0.95:
                reconverge = t - es
                break

        gap = None
        if i + 1 < len(expulsion_steps):
            gap = expulsion_steps[i + 1] - es

        results.append({
            'exp_step': es,
            'peace_dur': peace_dur,
            'reconverge': reconverge,
            'gap_to_next': gap,
        })
    return results


def main():
    Ns = [50, 100, 200, 500]
    gammas = [1.05, 1.10, 1.50, 2.00]
    N_RUNS = 8
    N_STEPS = 1500

    # --- Table 6: Summary ---
    print("=" * 95)
    print("TABLE 6: Violence topologies under unanimity-triggered expulsion")
    print(f"  AC variant, unanimity trigger (modal >= 0.95), cooldown=5, "
          f"{N_RUNS} seeds x {N_STEPS} steps")
    print("=" * 95)
    print()
    print(f"{'N':<6} {'gamma':<8} {'Med Exp':>8} {'Med Reconverge':>15} "
          f"{'Med Cycle':>10} {'Pct Consumed':>13}")
    print("-" * 70)

    all_data = {}

    for N in Ns:
        for gamma in gammas:
            run_reconverge = []
            run_cycle = []
            run_expulsions = []

            for r in range(N_RUNS):
                seed = 42 + r * 1000
                modal, exps = run_unanimity_triggered(
                    N, gamma, n_steps=N_STEPS, seed=seed)
                run_expulsions.append(len(exps))
                cycles = measure_cycles(modal, exps)
                for c in cycles:
                    if c['reconverge'] is not None:
                        run_reconverge.append(c['reconverge'])
                    if c['gap_to_next'] is not None:
                        run_cycle.append(c['gap_to_next'])

            med_exp = np.median(run_expulsions)
            med_reconv = f"{np.median(run_reconverge):.0f}" if run_reconverge else "--"
            med_cycle = f"{np.median(run_cycle):.0f}" if run_cycle else "--"
            pct_consumed = f"{med_exp / N * 100:.1f}%"

            print(f"{N:<6} {gamma:<8} {med_exp:>8.1f} {med_reconv:>15} "
                  f"{med_cycle:>10} {pct_consumed:>13}")

            all_data[(N, gamma)] = {
                'expulsions': run_expulsions,
                'reconverge': run_reconverge,
                'cycle': run_cycle,
            }

        print()

    # --- Table 7: Detailed traces ---
    print("\n" + "=" * 95)
    print("TABLE 7: Detailed cycle traces (seed=42)")
    print("=" * 95)

    detail_conditions = [
        (200, 1.05),   # boundary grinding
        (500, 2.00),   # supercritical bursts
    ]

    for N, gamma in detail_conditions:
        modal, exps = run_unanimity_triggered(N, gamma, n_steps=N_STEPS, seed=42)
        cycles = measure_cycles(modal, exps)
        print(f"\nN={N}, gamma={gamma}: {len(exps)} expulsions "
              f"({len(exps)/N*100:.1f}% consumed)")
        for i, c in enumerate(cycles[:15]):
            print(f"  Exp {i+1:>2} t={c['exp_step']:>5}: "
                  f"peace={c['peace_dur']:>3}, "
                  f"reconv={str(c['reconverge']):>4}, "
                  f"gap={str(c['gap_to_next']):>5}")
        if len(cycles) > 15:
            print(f"  ... ({len(cycles) - 15} more)")


if __name__ == "__main__":
    main()
