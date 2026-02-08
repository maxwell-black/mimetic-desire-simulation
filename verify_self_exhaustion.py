"""
verify_self_exhaustion.py

Verify whether mimetic violence self-exhausts at small N / high gamma.
Unanimity-triggered expulsion (modal agreement >= 0.95, 5-step cooldown).
Runs 20 seeds at N=50, gamma=2.0 for 10,000 steps each.

Usage:
    python verify_self_exhaustion.py

Expects girard_2x2_v3.py in the same directory (or on PYTHONPATH).
"""

import sys
import time
import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation

# ── Configuration ──────────────────────────────────────────────────────
N_AGENTS = 50
GAMMA = 2.0
N_STEPS = 10_000
N_SEEDS = 20
UNANIMITY_THRESH = 0.95
COOLDOWN = 5
# ──────────────────────────────────────────────────────────────────────


def modal_agreement(sim):
    """Return (agreement_fraction, modal_target_id)."""
    living = sim._alive_ids()
    if len(living) < 3:
        return 0.0, -1
    targets = []
    for i in living:
        agg = sim.aggression[i]
        if np.sum(agg) < 1e-8:
            continue
        targets.append(int(np.argmax(agg)))
    if not targets:
        return 0.0, -1
    ctr = Counter(targets)
    mode_target, mode_count = ctr.most_common(1)[0]
    return mode_count / len(targets), mode_target


def run_one(seed):
    cfg = GirardConfig(
        n_agents=N_AGENTS,
        salience_exponent=GAMMA,
        expulsion_threshold=None,   # manual expulsion via unanimity trigger
        n_steps=1,                  # we call step() manually
        seed=seed,
        record_history=False,
    )
    sim = GirardSimulation(cfg, source='object', spread='attention')

    expulsion_times = []
    cooldown_remaining = 0

    for t in range(N_STEPS):
        sim.step()

        if cooldown_remaining > 0:
            cooldown_remaining -= 1
            continue

        ma, modal_target = modal_agreement(sim)
        if ma >= UNANIMITY_THRESH and modal_target >= 0:
            victim = modal_target
            sim.alive[victim] = False
            for i in sim._alive_ids():
                sim.aggression[i][victim] = 0.0
            sim.aggression[victim][:] = 0.0
            expulsion_times.append(t)
            cooldown_remaining = COOLDOWN

    n_alive = sum(1 for v in sim.alive.values() if v)
    last_exp = expulsion_times[-1] if expulsion_times else None
    silence = (N_STEPS - 1 - last_exp) if last_exp is not None else N_STEPS

    return expulsion_times, n_alive, silence


def main():
    print(f"Self-exhaustion verification: N={N_AGENTS}, gamma={GAMMA}, "
          f"T={N_STEPS:,}, seeds={N_SEEDS}")
    print(f"Unanimity threshold={UNANIMITY_THRESH}, cooldown={COOLDOWN}")
    print("=" * 80)
    print()

    t0 = time.time()
    all_results = []

    for i, seed in enumerate(range(42, 42 + N_SEEDS)):
        exp_times, n_alive, silence = run_one(seed)
        pct_consumed = (N_AGENTS - n_alive) / N_AGENTS * 100
        last_t = exp_times[-1] if exp_times else None

        # Classify
        if not exp_times:
            verdict = "NO EXPULSIONS"
        elif silence >= 2000:
            verdict = "EXHAUSTED"
        elif silence >= 500:
            verdict = "PROBABLY EXHAUSTED"
        else:
            verdict = "STILL CYCLING"

        all_results.append({
            'seed': seed,
            'n_exp': len(exp_times),
            'n_alive': n_alive,
            'pct_consumed': pct_consumed,
            'last_t': last_t,
            'silence': silence,
            'verdict': verdict,
            'exp_times': exp_times,
        })

        # Print summary line
        last_str = str(last_t) if last_t is not None else '--'
        print(f"Seed {seed:>3}: {len(exp_times):>3} expulsions, "
              f"{n_alive:>3} alive ({pct_consumed:4.1f}% consumed), "
              f"last t={last_str:>6}, silence={silence:>5}  [{verdict}]")

        # Print individual expulsion timestamps for first 5 seeds
        if i < 5 and exp_times:
            gaps = [exp_times[j+1] - exp_times[j] for j in range(len(exp_times)-1)]
            print(f"         timestamps: {exp_times}")
            if gaps:
                print(f"         gaps:       {gaps}")
            print()

        sys.stdout.flush()

    elapsed = time.time() - t0
    print()
    print("=" * 80)
    print("SUMMARY")
    print(f"  Seeds run:        {N_SEEDS}")
    print(f"  Steps per seed:   {N_STEPS:,}")
    print(f"  Elapsed:          {elapsed:.0f}s")
    print()

    exp_counts = [r['n_exp'] for r in all_results]
    silences = [r['silence'] for r in all_results if r['n_exp'] > 0]
    exhausted = sum(1 for r in all_results if 'EXHAUST' in r['verdict'])
    cycling = sum(1 for r in all_results if r['verdict'] == 'STILL CYCLING')
    no_exp = sum(1 for r in all_results if r['verdict'] == 'NO EXPULSIONS')

    print(f"  Expulsions:       median={np.median(exp_counts):.0f}, "
          f"mean={np.mean(exp_counts):.1f}, range=[{min(exp_counts)}, {max(exp_counts)}]")
    if silences:
        print(f"  Silence after:    median={np.median(silences):.0f}, "
              f"min={min(silences)}, max={max(silences)}")
    print(f"  Exhausted:        {exhausted}/{N_SEEDS}")
    print(f"  Still cycling:    {cycling}/{N_SEEDS}")
    print(f"  No expulsions:    {no_exp}/{N_SEEDS}")


if __name__ == '__main__':
    main()
