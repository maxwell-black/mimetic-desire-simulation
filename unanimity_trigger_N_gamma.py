"""
unanimity_trigger_N_gamma.py
================================
Cross N x gamma under unanimity-triggered expulsion.

Tests whether the self-exhaustion result (high gamma stops cycling)
and the depletion-peace result (boundary gamma decelerates as population
shrinks) survive at larger N.

Hypothesis: both are small-N artifacts. At large N, all superlinear
gammas cycle indefinitely, and the sacred is necessary everywhere
above the phase boundary.

Run from repo root:
    python unanimity_trigger_N_gamma.py 2>&1 | tee unanimity_N_gamma_results.txt

Runtime estimate: ~30-45 minutes (N=500 is slow).
"""

import sys, os
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


def run_unanimity_triggered(n_agents, gamma, n_steps=1500, seed=42,
                             unanimity_threshold=0.95, cooldown=5):
    # Scale k with N to keep mean degree ~ 12% of N, min 6
    k = max(6, min(int(n_agents * 0.12), 20))
    if k % 2 == 1:
        k -= 1  # Watts-Strogatz needs even k

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
    gammas = [1.03, 1.05, 1.10, 1.50, 2.00]
    N_RUNS = 8
    N_STEPS = 1500

    print("=" * 100)
    print("N x GAMMA UNANIMITY-TRIGGERED EXPULSION")
    print("=" * 100)

    # Header
    print(f"\n{'N':<6} {'gamma':<8} {'Med Exp':>8} {'Med Peace':>10} "
          f"{'Med Reconverge':>15} {'Med Cycle':>10} "
          f"{'Pct Consumed':>13} {'Self-Exhaust':>12}")
    print("-" * 100)

    for N in Ns:
        for gamma in gammas:
            run_peace = []
            run_reconverge = []
            run_cycle = []
            run_expulsions = []
            run_self_exhaust = []  # True if last expulsion has no reconvergence

            for r in range(N_RUNS):
                seed = 42 + r * 1000
                try:
                    modal, exps = run_unanimity_triggered(
                        N, gamma, n_steps=N_STEPS, seed=seed,
                        unanimity_threshold=0.95, cooldown=5
                    )
                except Exception as e:
                    print(f"  ERROR: N={N}, gamma={gamma}, seed={seed}: {e}")
                    continue

                run_expulsions.append(len(exps))

                cycles = measure_cycles(modal, exps)
                for c in cycles:
                    run_peace.append(c['peace_dur'])
                    if c['reconverge'] is not None:
                        run_reconverge.append(c['reconverge'])
                    if c['gap_to_next'] is not None:
                        run_cycle.append(c['gap_to_next'])

                # Self-exhaustion: did the last expulsion fail to reconverge?
                if cycles and cycles[-1]['reconverge'] is None:
                    run_self_exhaust.append(True)
                elif not exps:
                    run_self_exhaust.append(False)  # never started
                else:
                    run_self_exhaust.append(False)

            med_peace = f"{np.median(run_peace):.0f}" if run_peace else "--"
            med_reconv = f"{np.median(run_reconverge):.0f}" if run_reconverge else "--"
            med_cycle = f"{np.median(run_cycle):.0f}" if run_cycle else "--"
            med_exp = np.median(run_expulsions) if run_expulsions else 0
            pct_consumed = f"{med_exp / N * 100:.1f}%"
            exhaust_rate = f"{sum(run_self_exhaust)}/{len(run_self_exhaust)}"

            print(f"{N:<6} {gamma:<8} {med_exp:>8.1f} {med_peace:>10} "
                  f"{med_reconv:>15} {med_cycle:>10} "
                  f"{pct_consumed:>13} {exhaust_rate:>12}")

        print()  # blank line between N groups

    # --- Key comparison: gamma=2.0 across N ---
    print("\n" + "=" * 100)
    print("DETAILED: gamma=2.0 across N (seed=42)")
    print("=" * 100)

    for N in Ns:
        modal, exps = run_unanimity_triggered(N, 2.0, n_steps=N_STEPS, seed=42)
        cycles = measure_cycles(modal, exps)
        print(f"\nN={N}: {len(exps)} expulsions, "
              f"{N - len(exps)} alive ({len(exps)/N*100:.1f}% consumed)")
        if exps:
            print(f"  First exp: t={exps[0]}, Last exp: t={exps[-1]}")
            if cycles[-1]['reconverge'] is None:
                print(f"  SELF-EXHAUSTED after exp {len(exps)}")
            else:
                print(f"  Still cycling at t={N_STEPS}")
        for i, c in enumerate(cycles[:10]):
            print(f"    Exp {i+1:>2} t={c['exp_step']:>5}: "
                  f"peace={c['peace_dur']:>3}, reconv={str(c['reconverge']):>4}, "
                  f"gap={str(c['gap_to_next']):>5}")
        if len(cycles) > 10:
            print(f"    ... ({len(cycles) - 10} more)")

    # --- Key comparison: gamma=1.05 across N ---
    print("\n" + "=" * 100)
    print("DETAILED: gamma=1.05 across N (seed=42)")
    print("=" * 100)

    for N in Ns:
        modal, exps = run_unanimity_triggered(N, 1.05, n_steps=N_STEPS, seed=42)
        cycles = measure_cycles(modal, exps)
        print(f"\nN={N}: {len(exps)} expulsions, "
              f"{N - len(exps)} alive ({len(exps)/N*100:.1f}% consumed)")
        if exps:
            print(f"  First exp: t={exps[0]}, Last exp: t={exps[-1]}")
            # Report late-cycle gaps
            late_gaps = [c['gap_to_next'] for c in cycles[-5:] if c['gap_to_next'] is not None]
            if late_gaps:
                print(f"  Last 5 cycle gaps: {late_gaps}")
        for i, c in enumerate(cycles[:10]):
            print(f"    Exp {i+1:>2} t={c['exp_step']:>5}: "
                  f"peace={c['peace_dur']:>3}, reconv={str(c['reconverge']):>4}, "
                  f"gap={str(c['gap_to_next']):>5}")
        if len(cycles) > 10:
            print(f"    ... ({len(cycles) - 10} more)")


if __name__ == "__main__":
    main()
