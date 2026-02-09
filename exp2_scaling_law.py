"""
exp2_scaling_law.py
===================
Measure the relationship between population size and exhaustion timescale.

For each (N, gamma), runs 10 seeds at 10,000 steps and records:
  - T_exhaust: step of last expulsion (if silence >= 500 after it)
  - OLS gap slope (from gap_trend_analysis methodology)
  - Projected T_exhaust from gap slope extrapolation

Then fits T_exhaust ~ N^k to find the scaling exponent.

Run from repo root:
    python exp2_scaling_law.py 2>&1 | tee exp2_scaling_law_results.txt

Estimated runtime: 8-12 hours.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation


SILENCE_THRESHOLD = 500


def run_one(n_agents, gamma, n_steps, seed):
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

    # OLS slope on gaps
    gap_slope = None
    if len(gaps) >= 6:
        x = np.arange(len(gaps), dtype=float)
        y = np.array(gaps, dtype=float)
        A = np.vstack([x, np.ones(len(gaps))]).T
        result = np.linalg.lstsq(A, y, rcond=None)
        gap_slope = float(result[0][0])

    exhausted = silence >= SILENCE_THRESHOLD and len(exp_times) > 0
    t_exhaust = exp_times[-1] if (exhausted and exp_times) else None

    return {
        "seed": seed,
        "n_exp": n_exp,
        "n_alive": n_alive,
        "pct_consumed": pct_consumed,
        "silence": silence,
        "exhausted": exhausted,
        "t_exhaust": t_exhaust,
        "gap_slope": gap_slope,
        "n_gaps": len(gaps),
    }


def fit_power_law(Ns, Ts):
    """Fit T = a * N^k via log-log OLS. Returns (k, a, r2)."""
    if len(Ns) < 2:
        return None, None, None
    log_N = np.log(np.array(Ns, dtype=float))
    log_T = np.log(np.array(Ts, dtype=float))
    A = np.vstack([log_N, np.ones(len(log_N))]).T
    result = np.linalg.lstsq(A, log_T, rcond=None)
    k = float(result[0][0])
    a = float(np.exp(result[0][1]))
    ss_res = float(np.sum((log_T - (k * log_N + result[0][1])) ** 2))
    ss_tot = float(np.sum((log_T - np.mean(log_T)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return k, a, r2


def main():
    N_STEPS = 10_000
    N_SEEDS = 10
    SEED_BASE = 42
    SEED_STRIDE = 1000

    Ns = [50, 100, 150, 200, 300, 400, 500, 750]
    gammas = [1.5, 2.0]

    out_lines = []
    def log(s=""):
        print(s, flush=True)
        out_lines.append(s)

    log("=" * 120)
    log("EXHAUSTION SCALING LAW: T_exhaust ~ N^k")
    log(f"Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 120)

    for gamma in gammas:
        log(f"\n{'=' * 120}")
        log(f"  gamma = {gamma}")
        log(f"{'=' * 120}")
        log(f"\n{'N':<6} {'Med Exp':>8} {'Consumed':>9} {'Exhausted':>10} "
            f"{'Med T_exh':>10} {'Med Slope':>10} {'Med Gaps':>9}")
        log("-" * 75)

        scaling_N = []
        scaling_T = []

        for N in Ns:
            results = []
            t0 = time.time()

            for r in range(N_SEEDS):
                seed = SEED_BASE + r * SEED_STRIDE
                res = run_one(N, gamma, N_STEPS, seed)
                results.append(res)
                # Per-seed progress
                status_str = "EXH" if res["exhausted"] else "cyc"
                print(f"    N={N} seed={seed}: {res['n_exp']} exp, "
                      f"{status_str}, slope={res['gap_slope']:.3f}" if res['gap_slope'] else
                      f"    N={N} seed={seed}: {res['n_exp']} exp, {status_str}",
                      flush=True)

            elapsed = time.time() - t0

            med_exp = np.median([r["n_exp"] for r in results])
            med_consumed = np.median([r["pct_consumed"] for r in results])
            n_exhausted = sum(1 for r in results if r["exhausted"])

            exh_times = [r["t_exhaust"] for r in results if r["t_exhaust"] is not None]
            med_t_exh = f"{np.median(exh_times):.0f}" if exh_times else "--"

            slopes = [r["gap_slope"] for r in results if r["gap_slope"] is not None]
            med_slope = f"{np.median(slopes):.4f}" if slopes else "--"

            med_gaps = np.median([r["n_gaps"] for r in results])

            log(f"{N:<6} {med_exp:>8.0f} {med_consumed:>8.1f}% {n_exhausted:>10} "
                f"{med_t_exh:>10} {med_slope:>10} {med_gaps:>9.0f}  ({elapsed:.0f}s)")

            # For scaling fit: use median T_exhaust if majority exhausted,
            # else estimate from gap slope
            if exh_times and n_exhausted >= N_SEEDS // 2:
                scaling_N.append(N)
                scaling_T.append(np.median(exh_times))
            elif slopes:
                # Use last expulsion time from the longest-running exhausted seed,
                # or the final expulsion time from the longest-running non-exhausted seed
                last_times = []
                for r in results:
                    if r["t_exhaust"] is not None:
                        last_times.append(r["t_exhaust"])
                    elif r["n_exp"] > 0:
                        # last expulsion time = n_steps - silence
                        last_times.append(N_STEPS - r["silence"])
                if last_times:
                    scaling_N.append(N)
                    scaling_T.append(max(last_times))

        # Fit scaling law
        log(f"\n  --- Scaling fit for gamma={gamma} ---")
        if len(scaling_N) >= 3:
            k, a, r2 = fit_power_law(scaling_N, scaling_T)
            log(f"    T_exhaust ~ {a:.2f} * N^{k:.3f}  (R2={r2:.3f})")
            log(f"    Data points: {list(zip(scaling_N, [f'{t:.0f}' for t in scaling_T]))}")

            # Predictions
            for N_pred in [1000, 2000, 5000]:
                t_pred = a * N_pred ** k
                log(f"    Predicted T_exhaust at N={N_pred}: {t_pred:.0f} steps")
        else:
            log(f"    Insufficient data for fit (need >= 3 N values with exhaustion)")

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("exp2_scaling_law_results_copy.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    log("Saved to exp2_scaling_law_results_copy.txt")


if __name__ == "__main__":
    main()
