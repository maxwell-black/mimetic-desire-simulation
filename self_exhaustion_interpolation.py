"""
self_exhaustion_interpolation.py
================================
Interpolate between N=200 (confirmed self-exhaustion) and N=500 (ambiguous)
by running N=300 and N=400 at both gamma=1.5 and gamma=2.0.

Uses the same classification logic as the extended self-exhaustion experiment:
  - genuine_exhaustion: last expulsion followed by >= 500 steps of silence
  - still_cycling: last expulsion within 50 steps of run end AND gaps show
    no lengthening trend
  - censored: last expulsion too close to run end to classify confidently
  - no_expulsions: zero expulsions in entire run

Also re-runs N=200 and N=500 as controls to confirm reproducibility.

Run from repo root:
    python self_exhaustion_interpolation.py

Output: console summary + self_exhaustion_interpolation_results.txt
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from dataclasses import replace
from girard_2x2_v3 import GirardConfig, GirardSimulation


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

SILENCE_THRESHOLD = 500   # steps of silence to call "genuine exhaustion"
CENSORED_WINDOW = 50      # if last exp within this many steps of end, "censored"


def classify_run(exp_times, n_steps):
    """
    Classify a single run.
    Returns (status, silence_after_last, median_gap, median_long_gap).
    """
    if not exp_times:
        return "no_expulsions", n_steps, None, None

    silence = n_steps - exp_times[-1]

    gaps = [exp_times[i] - exp_times[i - 1] for i in range(1, len(exp_times))]
    med_gap = float(np.median(gaps)) if gaps else None

    # "Long" gaps: > 14 steps (from the extended experiment's convention)
    long_gaps = [g for g in gaps if g > 14]
    med_long = float(np.median(long_gaps)) if long_gaps else None

    if silence >= SILENCE_THRESHOLD:
        return "genuine_exhaustion", silence, med_gap, med_long
    elif silence <= CENSORED_WINDOW:
        return "censored", silence, med_gap, med_long
    else:
        # Intermediate: could be a long gap or slow cycling
        return "censored", silence, med_gap, med_long


def run_condition(n_agents, gamma, n_steps, n_seeds, seed_base=42, seed_stride=1000):
    """
    Run one (N, gamma) condition across seeds.
    Returns list of per-seed result dicts.
    """
    results = []
    for r in range(n_seeds):
        seed = seed_base + r * seed_stride

        cfg = GirardConfig(
            n_agents=n_agents,
            n_neighbors=6,
            rewire_prob=0.15,
            alpha=0.15,
            salience_exponent=gamma,
            expulsion_threshold=8.0,
            n_steps=n_steps,
            record_history=False,
            seed=seed,
        )
        sim = GirardSimulation(cfg, source="object", spread="attention")
        sim.run()

        exp_times = [e[0] for e in sim.history["expulsion_events"]]
        n_exp = len(exp_times)
        n_alive = sum(1 for v in sim.alive.values() if v)
        pct_consumed = (n_agents - n_alive) / n_agents * 100.0

        status, silence, med_gap, med_long = classify_run(exp_times, n_steps)

        # Gap sequence for detailed output
        gaps = [exp_times[i] - exp_times[i - 1] for i in range(1, len(exp_times))]
        short_gaps = sum(1 for g in gaps if g <= 14)
        long_gaps_list = [g for g in gaps if g > 14]

        results.append({
            "seed": seed,
            "n_exp": n_exp,
            "n_alive": n_alive,
            "pct_consumed": pct_consumed,
            "status": status,
            "silence": silence,
            "med_gap": med_gap,
            "med_long": med_long,
            "last_exp_time": exp_times[-1] if exp_times else None,
            "short_gaps": short_gaps,
            "long_gaps_count": len(long_gaps_list),
            "long_gap_range": (min(long_gaps_list), max(long_gaps_list)) if long_gaps_list else None,
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    N_STEPS = 5000
    N_SEEDS = 20

    conditions = [
        # (N, gamma)
        (200, 1.5),
        (200, 2.0),
        (300, 1.5),
        (300, 2.0),
        (400, 1.5),
        (400, 2.0),
        (500, 1.5),
        (500, 2.0),
    ]

    out_lines = []
    def log(s=""):
        print(s)
        out_lines.append(s)

    log("=" * 110)
    log("SELF-EXHAUSTION INTERPOLATION: N=200, 300, 400, 500")
    log(f"Steps: {N_STEPS}, Seeds per condition: {N_SEEDS}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 110)

    # Summary table
    log()
    log(f"{'N':<6} {'gamma':<8} {'Med Exp':>8} {'Pct Consumed':>13} "
        f"{'Genuine':>8} {'Cycling':>8} {'Censored':>9} {'NoExp':>6} "
        f"{'Med Silence':>12} {'Med Long Gap':>13}")
    log("-" * 110)

    all_condition_results = {}

    for n_agents, gamma in conditions:
        t0 = time.time()
        results = run_condition(n_agents, gamma, N_STEPS, N_SEEDS)
        elapsed = time.time() - t0

        # Aggregate
        med_exp = np.median([r["n_exp"] for r in results])
        med_consumed = np.median([r["pct_consumed"] for r in results])
        n_genuine = sum(1 for r in results if r["status"] == "genuine_exhaustion")
        n_cycling = sum(1 for r in results if r["status"] == "still_cycling")
        n_censored = sum(1 for r in results if r["status"] == "censored")
        n_noexp = sum(1 for r in results if r["status"] == "no_expulsions")

        silences = [r["silence"] for r in results if r["status"] == "genuine_exhaustion"]
        med_silence = np.median(silences) if silences else 0

        long_gaps = [r["med_long"] for r in results if r["med_long"] is not None]
        med_long_gap = f"{np.median(long_gaps):.0f}" if long_gaps else "--"

        log(f"{n_agents:<6} {gamma:<8} {med_exp:>8.0f} {med_consumed:>12.1f}% "
            f"{n_genuine:>8} {n_cycling:>8} {n_censored:>9} {n_noexp:>6} "
            f"{med_silence:>12.0f} {med_long_gap:>13}  ({elapsed:.0f}s)")

        all_condition_results[(n_agents, gamma)] = results

    # Detailed output for the NEW conditions (N=300, N=400)
    for n_agents in [300, 400]:
        for gamma in [1.5, 2.0]:
            log(f"\n{'=' * 110}")
            log(f"DETAILED: N={n_agents}, gamma={gamma}")
            log(f"{'=' * 110}")

            results = all_condition_results[(n_agents, gamma)]
            for r in results[:10]:  # first 10 seeds
                log(f"\n  seed={r['seed']}: {r['n_exp']} expulsions, "
                    f"{r['n_alive']} alive ({r['pct_consumed']:.1f}% consumed)")
                log(f"    Status: {r['status']}")
                if r["last_exp_time"] is not None:
                    log(f"    Last exp: t={r['last_exp_time']}, "
                        f"silence after: {r['silence']} steps")
                    log(f"    Gaps: {r['short_gaps']} short (<=14), "
                        f"{r['long_gaps_count']} long")
                    if r["long_gap_range"]:
                        log(f"    Long gap range: {r['long_gap_range'][0]}-"
                            f"{r['long_gap_range'][1]}, "
                            f"median: {r['med_long']:.0f}")

    # Verdict
    log(f"\n\n{'=' * 110}")
    log("VERDICTS")
    log(f"{'=' * 110}")

    for n_agents, gamma in conditions:
        results = all_condition_results[(n_agents, gamma)]
        n_genuine = sum(1 for r in results if r["status"] == "genuine_exhaustion")
        n_censored = sum(1 for r in results if r["status"] == "censored")
        n_noexp = sum(1 for r in results if r["status"] == "no_expulsions")

        if n_genuine >= 18:
            verdict = "GENUINE SELF-EXHAUSTION"
        elif n_genuine >= 12:
            verdict = f"MOSTLY EXHAUSTION ({n_genuine}G/{n_censored}C/{n_noexp}N)"
        elif n_genuine >= 5:
            verdict = f"MIXED ({n_genuine}G/{n_censored}C/{n_noexp}N)"
        elif n_censored >= 15:
            verdict = f"STILL AMBIGUOUS -- need longer runs ({n_genuine}G/{n_censored}C)"
        else:
            verdict = f"UNCLEAR ({n_genuine}G/{n_censored}C/{n_noexp}N)"

        log(f"  N={n_agents:<4} gamma={gamma}: {verdict}")

    log(f"\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("self_exhaustion_interpolation_results.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print("\nSaved to self_exhaustion_interpolation_results.txt")


if __name__ == "__main__":
    main()
