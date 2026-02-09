"""
exp_small_n_scaling.py
=======================
Extend the T_exhaust ~ N^k scaling law down to small N.

Existing data covers N=50-750. This adds N=5-40 to see if the
power law holds across the full range, or if there's a regime
change at small N (where self-exhaustion is fast and reliable).

Uses adaptive unanimity trigger (consistent with viability experiment).

Run:
    python exp_small_n_scaling.py 2>&1 | Tee-Object -FilePath exp_small_n_scaling_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
"""

import sys, os, time
import numpy as np

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from small_n_utils import (adaptive_k, adaptive_unanimity_threshold,
                           run_unanimity_triggered)


SILENCE_THRESHOLD = 500


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

    # Full range: small N new + large N for continuity
    Ns = [10, 15, 20, 25, 30, 35, 40, 50, 75, 100]
    gammas = [1.5, 2.0]

    print("=" * 120)
    print("SMALL-N SCALING LAW: T_exhaust ~ N^k (extended downward)")
    print(f"Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    print(f"Ns: {Ns}")
    print(f"Trigger: adaptive unanimity threshold")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)

    for gamma in gammas:
        print(f"\n{'=' * 120}")
        print(f"  gamma = {gamma}")
        print(f"{'=' * 120}")
        print(f"\n{'N':<6} {'k':>3} {'Med Exp':>8} {'Consumed':>9} {'Exhausted':>10} "
              f"{'Med T_exh':>10} {'Med Gaps':>9} {'Med Slope':>10}")
        print("-" * 80)

        scaling_N = []
        scaling_T = []

        for N in Ns:
            results = []
            t0 = time.time()

            for r in range(N_SEEDS):
                seed = SEED_BASE + r * SEED_STRIDE
                res = run_unanimity_triggered(
                    N, gamma, "AC", n_steps=N_STEPS, seed=seed)

                # T_exhaust: step of last expulsion if genuinely exhausted
                t_exhaust = None
                if res["status"] == "genuine_exhaustion" and res["expulsion_steps"]:
                    t_exhaust = res["expulsion_steps"][-1]

                # OLS slope on gaps
                gap_slope = None
                if len(res["gaps"]) >= 6:
                    x = np.arange(len(res["gaps"]), dtype=float)
                    y = np.array(res["gaps"], dtype=float)
                    A_mat = np.vstack([x, np.ones(len(res["gaps"]))]).T
                    lstsq = np.linalg.lstsq(A_mat, y, rcond=None)
                    gap_slope = float(lstsq[0][0])

                results.append({
                    "seed": seed,
                    "n_exp": res["n_expulsions"],
                    "n_alive": res["n_alive"],
                    "pct_consumed": res["pct_consumed"],
                    "status": res["status"],
                    "gap_slope": gap_slope,
                    "n_gaps": len(res["gaps"]),
                    "t_exhaust": t_exhaust,
                })

                status_str = "EXH" if res["status"] == "genuine_exhaustion" else res["status"][:3]
                slope_str = f"slope={gap_slope:.3f}" if gap_slope else ""
                print(f"    N={N} seed={seed}: {res['n_expulsions']} exp, "
                      f"{status_str} {slope_str}", flush=True)

            elapsed = time.time() - t0

            med_exp = np.median([r["n_exp"] for r in results])
            med_consumed = np.median([r["pct_consumed"] for r in results]) * 100
            n_exhausted = sum(1 for r in results if r["status"] == "genuine_exhaustion")

            slopes = [r["gap_slope"] for r in results if r["gap_slope"] is not None]
            med_slope = f"{np.median(slopes):.4f}" if slopes else "--"
            med_gaps = np.median([r["n_gaps"] for r in results])
            k_ws = adaptive_k(N)

            # For scaling fit: use median T_exhaust (step of last expulsion)
            t_exhaust_vals = [r["t_exhaust"] for r in results if r["t_exhaust"] is not None]
            if n_exhausted >= N_SEEDS // 2 and t_exhaust_vals:
                med_t_exh = float(np.median(t_exhaust_vals))
                scaling_N.append(N)
                scaling_T.append(med_t_exh)
                t_exh_str = f"{med_t_exh:.0f}"
            else:
                t_exh_str = "--"

            print(f"{N:<6} {k_ws:>3} {med_exp:>8.0f} {med_consumed:>8.1f}% "
                  f"{n_exhausted:>10} {t_exh_str:>10} {med_gaps:>9.0f} "
                  f"{med_slope:>10}  ({elapsed:.0f}s)")

        # Fit scaling law on T_exhaust ~ N^k
        print(f"\n  --- Scaling fit for gamma={gamma} ---")
        if len(scaling_N) >= 3:
            k_exp, a_exp, r2 = fit_power_law(scaling_N, scaling_T)
            print(f"    T_exhaust ~ {a_exp:.2f} * N^{k_exp:.3f}  (R2={r2:.3f})")
            print(f"    Data points: {list(zip(scaling_N, [f'{t:.0f}' for t in scaling_T]))}")
        else:
            print(f"    Insufficient data for fit (need >= 3 N values with exhaustion)")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
