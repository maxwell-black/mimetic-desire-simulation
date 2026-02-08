"""
self_exhaustion_extended.py
===========================
Resolves the self-exhaustion measurement artifact at N=200-500.

The 1500-step runs can't distinguish genuine self-exhaustion from
censored inter-burst intervals (which run 300-450 steps at high gamma).
This script runs 5000 steps with 20 seeds to get a clean answer.

Key question: At what N does high-gamma violence cease to self-exhaust?

Run:
    python self_exhaustion_extended.py 2>&1 | tee self_exhaustion_extended_results.txt

Runtime estimate: ~2-4 hours depending on hardware. Safe to leave overnight.
"""

import sys, os, time
import numpy as np
from collections import Counter
from datetime import datetime

# --- Adjust this path if girard_2x2_v3.py is in a different directory ---
# If running from the same directory as girard_2x2_v3.py, this is fine.
# If running from elsewhere, change to the absolute path of the repo.
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation


def get_modal_target(sim):
    """Compute modal agreement: fraction of agents whose top-aggression
    target is the same person."""
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


def run_unanimity_triggered(n_agents, gamma, n_steps=5000, seed=42,
                             unanimity_threshold=0.95, cooldown=5):
    """Run simulation with unanimity-triggered expulsion."""
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

    n_alive = sum(sim.alive.values())
    return modal_series, expulsion_steps, n_alive


def classify_exhaustion(modal_series, expulsion_steps, n_steps,
                         min_silence=500):
    """Classify whether the run genuinely self-exhausted.

    Genuine self-exhaustion: last expulsion occurred, and then
    at least `min_silence` steps passed with no reconvergence
    (modal agreement never returned to >= 0.95).

    Censored: last expulsion too close to end of sim to tell.
    Still cycling: reconvergence occurred after last expulsion.
    """
    if not expulsion_steps:
        return "no_expulsions", None, None

    last_exp = expulsion_steps[-1]
    remaining = n_steps - last_exp - 1

    # Check if modal agreement ever hit 0.95 again after last expulsion
    reconverged = False
    reconverge_step = None
    for t in range(last_exp + 1, n_steps):
        if modal_series[t] >= 0.95:
            reconverged = True
            reconverge_step = t - last_exp
            break

    if reconverged:
        return "still_cycling", reconverge_step, remaining
    elif remaining >= min_silence:
        return "genuine_exhaustion", None, remaining
    else:
        return "censored", None, remaining


def measure_inter_burst_gaps(expulsion_steps):
    """Compute gaps between expulsions for cycle analysis."""
    if len(expulsion_steps) < 2:
        return []
    return [expulsion_steps[i+1] - expulsion_steps[i]
            for i in range(len(expulsion_steps) - 1)]


def main():
    # ---- Configuration ----
    Ns = [200, 500]
    gammas = [1.5, 2.0]
    N_SEEDS = 20
    N_STEPS = 5000
    MIN_SILENCE = 500  # steps of silence to confirm genuine exhaustion

    print("=" * 100)
    print(f"SELF-EXHAUSTION RESOLUTION: {N_STEPS} steps, {N_SEEDS} seeds")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    # Also run N=50 and N=100 as controls (should confirm genuine exhaustion)
    all_Ns = [50, 100] + Ns

    # ---- Summary table ----
    print(f"\n{'N':<6} {'gamma':<8} {'Med Exp':>8} {'Pct Consumed':>13} "
          f"{'Genuine Exh':>12} {'Still Cycling':>14} {'Censored':>9} "
          f"{'Med Silence':>12} {'Med Last Gap':>13}")
    print("-" * 100)

    all_results = {}

    for N in all_Ns:
        for gamma in gammas:
            t0 = time.time()
            run_data = []

            for r in range(N_SEEDS):
                seed = 42 + r * 1000
                try:
                    modal, exps, n_alive = run_unanimity_triggered(
                        N, gamma, n_steps=N_STEPS, seed=seed
                    )
                except Exception as e:
                    print(f"  ERROR: N={N}, gamma={gamma}, seed={seed}: {e}")
                    continue

                status, reconv_step, remaining = classify_exhaustion(
                    modal, exps, N_STEPS, min_silence=MIN_SILENCE
                )
                gaps = measure_inter_burst_gaps(exps)

                # Silence after last expulsion
                silence = (N_STEPS - exps[-1] - 1) if exps else N_STEPS

                run_data.append({
                    'seed': seed,
                    'n_exp': len(exps),
                    'n_alive': n_alive,
                    'status': status,
                    'reconv_step': reconv_step,
                    'remaining': remaining,
                    'silence': silence,
                    'gaps': gaps,
                    'last_exp': exps[-1] if exps else None,
                })

            elapsed = time.time() - t0
            all_results[(N, gamma)] = run_data

            # Compute summary stats
            n_genuine = sum(1 for d in run_data if d['status'] == 'genuine_exhaustion')
            n_cycling = sum(1 for d in run_data if d['status'] == 'still_cycling')
            n_censored = sum(1 for d in run_data if d['status'] == 'censored')
            med_exp = np.median([d['n_exp'] for d in run_data])
            pct_consumed = med_exp / N * 100
            silences = [d['silence'] for d in run_data if d['n_exp'] > 0]
            med_silence = np.median(silences) if silences else 0

            # Median of last inter-burst gap (proxy for cycle period)
            last_gaps = []
            for d in run_data:
                if d['gaps']:
                    last_gaps.append(d['gaps'][-1])
            med_last_gap = np.median(last_gaps) if last_gaps else 0

            print(f"{N:<6} {gamma:<8} {med_exp:>8.0f} {pct_consumed:>12.1f}% "
                  f"{n_genuine:>12} {n_cycling:>14} {n_censored:>9} "
                  f"{med_silence:>12.0f} {med_last_gap:>13.0f}"
                  f"  ({elapsed:.0f}s)")

        print()  # blank line between N groups

    # ---- Detailed traces for key conditions ----
    for N in Ns:
        for gamma in gammas:
            print("\n" + "=" * 100)
            print(f"DETAILED: N={N}, gamma={gamma}")
            print("=" * 100)

            data = all_results.get((N, gamma), [])
            for d in data[:5]:  # first 5 seeds
                print(f"\n  seed={d['seed']}: {d['n_exp']} expulsions, "
                      f"{d['n_alive']} alive ({d['n_exp']/N*100:.1f}% consumed)")
                print(f"    Status: {d['status']}")
                if d['last_exp'] is not None:
                    print(f"    Last exp: t={d['last_exp']}, "
                          f"silence after: {d['silence']} steps")
                if d['reconv_step'] is not None:
                    print(f"    Reconverged {d['reconv_step']} steps after last exp")
                if d['gaps']:
                    # Show gap distribution
                    gaps = d['gaps']
                    short = [g for g in gaps if g <= 14]  # paired (cooldown + few steps)
                    long = [g for g in gaps if g > 14]
                    print(f"    Gaps: {len(short)} short (<=14), {len(long)} long")
                    if long:
                        print(f"    Long gap range: {min(long)}-{max(long)}, "
                              f"median: {np.median(long):.0f}")

    # ---- Final verdict ----
    print("\n" + "=" * 100)
    print("VERDICT")
    print("=" * 100)

    for N in all_Ns:
        for gamma in gammas:
            data = all_results.get((N, gamma), [])
            if not data:
                continue
            n_genuine = sum(1 for d in data if d['status'] == 'genuine_exhaustion')
            n_cycling = sum(1 for d in data if d['status'] == 'still_cycling')
            n_censored = sum(1 for d in data if d['status'] == 'censored')

            if n_genuine > 0.8 * len(data):
                verdict = "GENUINE SELF-EXHAUSTION"
            elif n_cycling > 0.8 * len(data):
                verdict = "PERPETUAL CYCLING (no self-exhaustion)"
            elif n_censored > 0.5 * len(data):
                verdict = "STILL AMBIGUOUS (need longer runs)"
            else:
                verdict = f"MIXED ({n_genuine}G/{n_cycling}C/{n_censored}?)"

            print(f"  N={N:<4} gamma={gamma}: {verdict}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
