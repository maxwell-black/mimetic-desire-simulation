"""
Reproduce Table 8: Self-exhaustion under unanimity trigger
===========================================================
Does the scapegoat cycle self-exhaust at high gamma?

Usage:  python reproduce_table_8.py
Requires girard_2x2_v3.py in the same directory or on sys.path.

Expected runtime: ~10-20 minutes.
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


def main():
    Ns = [50, 100, 200, 500]
    N_STEPS = 1500

    print("=" * 90)
    print("TABLE 8: Self-exhaustion under unanimity trigger")
    print(f"  AC variant, gamma=2.0, unanimity trigger, seed=42, {N_STEPS} steps")
    print("=" * 90)
    print()
    print(f"{'N':<6} {'Expulsions':>10} {'Pct Consumed':>13} "
          f"{'Last Exp Step':>14} {'Silence After':>14}")
    print("-" * 65)

    for N in Ns:
        modal, exps = run_unanimity_triggered(
            N, gamma=2.0, n_steps=N_STEPS, seed=42)

        n_exp = len(exps)
        pct = f"{n_exp / N * 100:.1f}%"
        last_step = exps[-1] if exps else "--"
        silence = N_STEPS - exps[-1] - 1 if exps else N_STEPS

        # Check if reconvergence happened after last expulsion
        reconverged = False
        if exps:
            for t in range(exps[-1] + 1, len(modal)):
                if modal[t] >= 0.95:
                    reconverged = True
                    break

        status = "self-exhausted" if not reconverged and exps else "still cycling"
        if not exps:
            status = "no expulsions"

        print(f"{N:<6} {n_exp:>10} {pct:>13} "
              f"{str(last_step):>14} {silence:>14}  ({status})")

    # Detailed traces
    print("\n" + "-" * 90)
    print("Detailed expulsion traces (gamma=2.0, seed=42)")
    print("-" * 90)

    for N in Ns:
        modal, exps = run_unanimity_triggered(
            N, gamma=2.0, n_steps=N_STEPS, seed=42)
        print(f"\nN={N}: {len(exps)} expulsions")
        if exps:
            print(f"  Steps: {exps}")
            # Compute inter-expulsion gaps
            if len(exps) > 1:
                gaps = [exps[i+1] - exps[i] for i in range(len(exps)-1)]
                print(f"  Gaps:  {gaps}")


if __name__ == "__main__":
    main()
