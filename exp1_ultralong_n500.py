"""
exp1_ultralong_n500.py
======================
Definitive test: does N=500 eventually self-exhaust?

Gap trend analysis says YES (gaps lengthening 20/20 seeds, both gammas).
This runs 8 seeds at 50,000 steps to produce at least one clean exhaustion.
If it works, the ambiguity in the extended results is fully resolved.

Run from repo root:
    python exp1_ultralong_n500.py 2>&1 | Tee-Object -FilePath exp1_ultralong_n500_results.txt

Estimated runtime: 10-15 hours.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation


SILENCE_THRESHOLD = 2000  # generous: 2000 steps silence = exhausted


def run_one(n_agents, gamma, n_steps, seed):
    """Run one sim, return result dict."""
    k = max(6, min(int(n_agents * 0.12), 20))
    if k % 2 == 1:
        k -= 1

    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=k,
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
    silence = (n_steps - exp_times[-1]) if exp_times else n_steps

    gaps = [exp_times[i] - exp_times[i - 1] for i in range(1, len(exp_times))]

    if silence >= SILENCE_THRESHOLD:
        status = "genuine_exhaustion"
    elif not exp_times:
        status = "no_expulsions"
    elif silence < 100:
        status = "still_cycling"
    else:
        status = "censored"

    return {
        "seed": seed,
        "n_exp": n_exp,
        "n_alive": n_alive,
        "pct_consumed": pct_consumed,
        "status": status,
        "silence": silence,
        "last_exp": exp_times[-1] if exp_times else None,
        "gaps": gaps,
    }


def main():
    N_STEPS = 50_000
    N_SEEDS = 8
    SEED_BASE = 42
    SEED_STRIDE = 1000

    conditions = [
        (500, 1.5),
        (500, 2.0),
    ]

    out_lines = []
    def log(s=""):
        print(s, flush=True)
        out_lines.append(s)

    log("=" * 100)
    log("ULTRA-LONG SELF-EXHAUSTION TEST: N=500, 50,000 steps")
    log(f"Seeds: {N_SEEDS}, Silence threshold: {SILENCE_THRESHOLD}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 100)

    for n_agents, gamma in conditions:
        log(f"\n{'=' * 100}")
        log(f"  N={n_agents}, gamma={gamma}")
        log(f"{'=' * 100}")

        results = []
        t0_cond = time.time()

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            t0 = time.time()
            res = run_one(n_agents, gamma, N_STEPS, seed)
            elapsed = time.time() - t0
            results.append(res)

            # Interim output
            log(f"  seed={seed}: {res['n_exp']} exp, {res['n_alive']} alive "
                f"({res['pct_consumed']:.1f}% consumed), "
                f"silence={res['silence']}, status={res['status']}  "
                f"({elapsed:.0f}s)")

            if res['gaps']:
                n_gaps = len(res['gaps'])
                early = res['gaps'][:n_gaps // 3]
                late = res['gaps'][-n_gaps // 3:]
                if early and late:
                    log(f"    gap trend: early_med={np.median(early):.0f}, "
                        f"late_med={np.median(late):.0f}, "
                        f"total_gaps={n_gaps}")

        cond_elapsed = time.time() - t0_cond
        n_exhausted = sum(1 for r in results if r["status"] == "genuine_exhaustion")
        n_cycling = sum(1 for r in results if r["status"] == "still_cycling")
        n_censored = sum(1 for r in results if r["status"] == "censored")
        n_noexp = sum(1 for r in results if r["status"] == "no_expulsions")

        log(f"\n  SUMMARY N={n_agents} gamma={gamma} ({cond_elapsed:.0f}s):")
        log(f"    Exhausted: {n_exhausted}/{N_SEEDS}")
        log(f"    Still cycling: {n_cycling}/{N_SEEDS}")
        log(f"    Censored: {n_censored}/{N_SEEDS}")
        log(f"    No expulsions: {n_noexp}/{N_SEEDS}")

        if n_exhausted > 0:
            exh = [r for r in results if r["status"] == "genuine_exhaustion"]
            log(f"    Exhausted seeds consumed: "
                f"median {np.median([r['pct_consumed'] for r in exh]):.1f}%")
            log(f"    Exhausted seeds last exp: "
                f"median t={np.median([r['last_exp'] for r in exh]):.0f}")

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("exp1_ultralong_n500_results_copy.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    log("Saved to exp1_ultralong_n500_results_copy.txt")


if __name__ == "__main__":
    main()
