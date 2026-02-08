"""
unanimity_trigger_experiment.py
================================
Unanimity-triggered expulsion: fire when modal agreement >= threshold,
directly formalizing Girard's claim that unanimous focus IS the discharge.

Contrast with the paper's accumulation trigger (tau), which decouples
consensus from action and produces long plateaus of unanimous targeting
without discharge -- closer to ritualized sacrifice with "sacrificial delay"
than to the spontaneous founding murder.

Run from repo root (same directory as girard_2x2_v3.py):
    python unanimity_trigger_experiment.py

Output: summary table + detailed traces for boundary gammas.
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


def run_unanimity_triggered(gamma, n_steps=1500, seed=42,
                             unanimity_threshold=0.95,
                             cooldown=5):
    """
    Run AC variant with unanimity-triggered expulsion.

    When modal agreement >= unanimity_threshold, immediately expel
    the modal target. Cooldown prevents re-firing for N steps after
    an expulsion (models brief post-expulsion disorientation --
    without this, the system can re-fire on residual agreement
    before the cascade has time to dissolve).
    """
    cfg = GirardConfig(
        n_agents=50, n_neighbors=6, rewire_prob=0.15,
        alpha=0.15, salience_exponent=gamma,
        expulsion_threshold=None,  # disable accumulation trigger
        n_steps=n_steps, record_history=False, seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_series = []
    expulsion_steps = []
    steps_since_expulsion = cooldown + 1  # allow immediate first fire

    for step in range(n_steps):
        ma, mt = get_modal_target(sim)
        modal_series.append(ma)

        # Check unanimity trigger
        if (ma >= unanimity_threshold and
            steps_since_expulsion > cooldown and
            mt is not None and
            len(sim._alive_ids()) > 2):

            # Expel the modal target
            sim.alive[mt] = False
            sim.aggression[mt, :] = 0.0
            sim.aggression[:, mt] = 0.0
            expulsion_steps.append(step)
            steps_since_expulsion = 0
        else:
            steps_since_expulsion += 1

        # Run one simulation step
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
        # Peace: consecutive steps after expulsion where modal < peace_threshold
        peace_dur = 0
        for t in range(es + 1, len(modal_series)):
            if modal_series[t] < peace_threshold:
                peace_dur += 1
            else:
                break

        # Reconvergence: steps to reach 0.95 again
        reconverge = None
        for t in range(es + 1, len(modal_series)):
            if modal_series[t] >= 0.95:
                reconverge = t - es
                break

        # Time to next expulsion
        if i + 1 < len(expulsion_steps):
            gap = expulsion_steps[i + 1] - es
        else:
            gap = None

        results.append({
            'exp_step': es,
            'peace_dur': peace_dur,
            'reconverge': reconverge,
            'gap_to_next': gap,
        })
    return results


def main():
    gammas = [1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.15, 1.25, 1.50, 2.00]
    N_RUNS = 8
    N_STEPS = 1500

    print("=" * 85)
    print("UNANIMITY-TRIGGERED EXPULSION: SUMMARY")
    print("=" * 85)
    print(f"{'gamma':<8} {'Med Exp':>8} {'Med Peace':>10} {'Med Reconverge':>15} "
          f"{'Med Cycle':>10} {'Med Alive':>10}")
    print("-" * 85)

    all_results = {}

    for gamma in gammas:
        run_peace = []
        run_reconverge = []
        run_cycle = []
        run_expulsions = []
        run_alive = []

        for r in range(N_RUNS):
            seed = 42 + r * 1000
            modal, exps = run_unanimity_triggered(
                gamma, n_steps=N_STEPS, seed=seed,
                unanimity_threshold=0.95, cooldown=5
            )

            run_expulsions.append(len(exps))
            run_alive.append(50 - len(exps))

            cycles = measure_cycles(modal, exps)
            for c in cycles:
                run_peace.append(c['peace_dur'])
                if c['reconverge'] is not None:
                    run_reconverge.append(c['reconverge'])
                if c['gap_to_next'] is not None:
                    run_cycle.append(c['gap_to_next'])

        med_peace = f"{np.median(run_peace):.0f}" if run_peace else "--"
        med_reconv = f"{np.median(run_reconverge):.0f}" if run_reconverge else "--"
        med_cycle = f"{np.median(run_cycle):.0f}" if run_cycle else "--"
        med_exp = f"{np.median(run_expulsions):.1f}"
        med_alive = f"{np.median(run_alive):.0f}"

        print(f"{gamma:<8} {med_exp:>8} {med_peace:>10} {med_reconv:>15} "
              f"{med_cycle:>10} {med_alive:>10}")

        all_results[gamma] = {
            'peace': run_peace,
            'reconverge': run_reconverge,
            'cycle': run_cycle,
            'expulsions': run_expulsions,
        }

    # --- Detailed traces for selected gammas ---
    for gamma in [1.02, 1.05, 1.10, 2.00]:
        print(f"\n\nDetailed trace: gamma={gamma}, seed=42")
        print("-" * 65)
        modal, exps = run_unanimity_triggered(gamma, n_steps=N_STEPS, seed=42)
        cycles = measure_cycles(modal, exps)
        print(f"Expulsions: {len(exps)} in {N_STEPS} steps")
        print(f"Expulsion steps: {exps[:20]}{'...' if len(exps) > 20 else ''}")
        for i, c in enumerate(cycles[:15]):
            print(f"  Exp {i+1:>2} at t={c['exp_step']:>5}: "
                  f"peace={c['peace_dur']:>3} steps, "
                  f"reconverge={str(c['reconverge']):>4}, "
                  f"gap_to_next={str(c['gap_to_next']):>5}")
        if len(cycles) > 15:
            print(f"  ... ({len(cycles) - 15} more)")

    # --- Compare with accumulation trigger for gamma=2.0 ---
    print("\n\n" + "=" * 85)
    print("COMPARISON: UNANIMITY vs ACCUMULATION TRIGGER (gamma=2.0, seed=42)")
    print("=" * 85)

    # Unanimity trigger
    modal_u, exps_u = run_unanimity_triggered(2.0, n_steps=800, seed=42)
    cycles_u = measure_cycles(modal_u, exps_u)

    print(f"\nUnanimity trigger (fire at modal >= 0.95):")
    print(f"  Expulsions: {len(exps_u)} in 800 steps")
    if cycles_u:
        peace_vals = [c['peace_dur'] for c in cycles_u]
        reconv_vals = [c['reconverge'] for c in cycles_u if c['reconverge']]
        print(f"  Median peace duration: {np.median(peace_vals):.0f} steps")
        print(f"  Median reconvergence: {np.median(reconv_vals):.0f} steps")
        print(f"  Median cycle length: {np.median([c['gap_to_next'] for c in cycles_u if c['gap_to_next']]):.0f} steps")
    for i, c in enumerate(cycles_u[:8]):
        print(f"    Exp {i+1} at t={c['exp_step']:>4}: peace={c['peace_dur']:>3}, "
              f"reconverge={c['reconverge']}, gap={c['gap_to_next']}")

    # Save modal series for plotting
    np.savez('unanimity_trigger_traces.npz',
             # gamma=2.0 unanimity trigger
             modal_u_2_0=modal_u,
             exps_u_2_0=exps_u,
             # gamma=1.05 unanimity trigger
             **{f'modal_u_1_05': run_unanimity_triggered(1.05, 800, 42)[0],
                f'exps_u_1_05': run_unanimity_triggered(1.05, 800, 42)[1]},
    )
    print("\nSaved traces to unanimity_trigger_traces.npz")


if __name__ == "__main__":
    main()
