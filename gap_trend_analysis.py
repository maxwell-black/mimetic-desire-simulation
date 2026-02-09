"""
gap_trend_analysis.py
=====================
Analyze whether inter-expulsion gaps at N=500 are LENGTHENING (trending
toward exhaustion) or STATIONARY (self-sustaining cycling).

If gaps lengthen over time, the community is slowly depleting its capacity
for crisis and would eventually exhaust.  If stationary, cycling is
self-sustaining and N=500 marks a qualitative regime change -- the threshold
beyond which cultural management of violence ("the sacred") becomes necessary.

Method:
  1. Re-run the N=500 simulations (5000 steps, 20 seeds, both gammas).
  2. Extract the full gap sequence for each seed.
  3. For seeds with >= 10 gaps:
     a. Mann-Kendall trend test on gap sequence.
     b. Split into first-half / second-half, compare medians (Wilcoxon).
     c. Fit OLS slope (gap ~ ordinal index).
  4. Aggregate across seeds to draw a population-level conclusion.

Also runs N=200 as a positive control (known exhaustion -- gaps SHOULD
show a trend toward lengthening in the late phase).

Run from repo root:
    python gap_trend_analysis.py

Output: console summary + gap_trend_results.txt
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from dataclasses import replace
from girard_2x2_v3 import GirardConfig, GirardSimulation

# ---------------------------------------------------------------------------
# Simulation runner (matches self_exhaustion_extended conventions)
# ---------------------------------------------------------------------------

def run_and_extract_gaps(n_agents, gamma, n_steps, seed):
    """
    Run one AC simulation.  Return dict with:
      - expulsion_times: list of timesteps where expulsions occurred
      - gaps: list of inter-expulsion intervals
      - n_expulsions: int
      - n_alive: int
      - silence_after_last: steps from last expulsion to end of run
    """
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
    gaps = []
    for i in range(1, len(exp_times)):
        gaps.append(exp_times[i] - exp_times[i - 1])

    silence = (n_steps - exp_times[-1]) if exp_times else n_steps
    n_alive = sum(1 for v in sim.alive.values() if v)

    return {
        "expulsion_times": exp_times,
        "gaps": gaps,
        "n_expulsions": len(exp_times),
        "n_alive": n_alive,
        "silence_after_last": silence,
    }


# ---------------------------------------------------------------------------
# Trend tests
# ---------------------------------------------------------------------------

def mann_kendall(x):
    """
    Mann-Kendall trend test.  Returns (S, p_value, trend_direction).
    S > 0 => increasing trend (gaps lengthening).
    """
    from itertools import combinations
    n = len(x)
    if n < 4:
        return 0, 1.0, "insufficient_data"

    S = 0
    for i, j in combinations(range(n), 2):
        diff = x[j] - x[i]
        if diff > 0:
            S += 1
        elif diff < 0:
            S -= 1

    # Variance under null (no ties correction for simplicity)
    var_S = n * (n - 1) * (2 * n + 5) / 18.0

    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0.0

    # Two-sided p-value from standard normal
    from scipy.stats import norm
    p = 2.0 * norm.sf(abs(Z))

    if p < 0.05:
        direction = "increasing" if S > 0 else "decreasing"
    else:
        direction = "no_trend"

    return S, p, direction


def half_split_test(gaps):
    """
    Split gaps into first and second half, compare medians via Wilcoxon rank-sum.
    Returns (median_first, median_second, p_value, direction).
    """
    from scipy.stats import mannwhitneyu
    n = len(gaps)
    if n < 6:
        return None, None, 1.0, "insufficient_data"

    mid = n // 2
    first = gaps[:mid]
    second = gaps[mid:]

    med1 = np.median(first)
    med2 = np.median(second)

    try:
        _, p = mannwhitneyu(first, second, alternative='two-sided')
    except ValueError:
        p = 1.0

    if p < 0.05:
        direction = "lengthening" if med2 > med1 else "shortening"
    else:
        direction = "no_difference"

    return med1, med2, p, direction


def ols_slope(gaps):
    """
    Fit gap_i = a + b*i.  Return (slope, r_squared).
    """
    n = len(gaps)
    if n < 3:
        return 0.0, 0.0
    x = np.arange(n, dtype=float)
    y = np.array(gaps, dtype=float)
    A = np.vstack([x, np.ones(n)]).T
    result = np.linalg.lstsq(A, y, rcond=None)
    slope, intercept = result[0]
    y_hat = slope * x + intercept
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return slope, r2


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    N_STEPS = 5000
    N_SEEDS = 20
    SEED_BASE = 42
    SEED_STRIDE = 1000

    conditions = [
        # (N, gamma, label)
        (200, 1.5, "N=200 g=1.5 [positive control]"),
        (200, 2.0, "N=200 g=2.0 [positive control]"),
        (500, 1.5, "N=500 g=1.5 [ambiguous]"),
        (500, 2.0, "N=500 g=2.0 [mixed]"),
    ]

    out_lines = []
    def log(s=""):
        print(s)
        out_lines.append(s)

    log("=" * 100)
    log("GAP TREND ANALYSIS")
    log(f"Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 100)

    for n_agents, gamma, label in conditions:
        log(f"\n{'=' * 100}")
        log(f"  {label}")
        log(f"{'=' * 100}")

        mk_directions = []
        half_directions = []
        slopes = []
        all_gaps_first_half = []
        all_gaps_second_half = []

        t0 = time.time()

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            result = run_and_extract_gaps(n_agents, gamma, N_STEPS, seed)
            gaps = result["gaps"]

            if len(gaps) < 6:
                log(f"  seed={seed}: {result['n_expulsions']} expulsions, "
                    f"{len(gaps)} gaps -- too few for trend analysis")
                continue

            # Trend tests
            S, mk_p, mk_dir = mann_kendall(gaps)
            med1, med2, half_p, half_dir = half_split_test(gaps)
            slope, r2 = ols_slope(gaps)

            mk_directions.append(mk_dir)
            half_directions.append(half_dir)
            slopes.append(slope)

            mid = len(gaps) // 2
            all_gaps_first_half.extend(gaps[:mid])
            all_gaps_second_half.extend(gaps[mid:])

            log(f"  seed={seed}: {len(gaps)} gaps | "
                f"MK: S={S:+d} p={mk_p:.4f} ({mk_dir}) | "
                f"Half: {med1:.0f}->{med2:.0f} p={half_p:.4f} ({half_dir}) | "
                f"OLS slope={slope:+.2f} R2={r2:.3f}")

        elapsed = time.time() - t0

        # Aggregate
        log(f"\n  --- Aggregate for {label} ({elapsed:.0f}s) ---")

        if mk_directions:
            for d in ["increasing", "decreasing", "no_trend"]:
                ct = mk_directions.count(d)
                log(f"    Mann-Kendall {d}: {ct}/{len(mk_directions)} seeds")

        if half_directions:
            for d in ["lengthening", "shortening", "no_difference"]:
                ct = half_directions.count(d)
                log(f"    Half-split {d}: {ct}/{len(half_directions)} seeds")

        if slopes:
            log(f"    OLS slope: median={np.median(slopes):+.3f}, "
                f"mean={np.mean(slopes):+.3f}, "
                f"range=[{min(slopes):+.3f}, {max(slopes):+.3f}]")

        if all_gaps_first_half and all_gaps_second_half:
            log(f"    Pooled gap medians: first_half={np.median(all_gaps_first_half):.0f}, "
                f"second_half={np.median(all_gaps_second_half):.0f}")

        # Verdict
        if mk_directions:
            n_inc = mk_directions.count("increasing")
            n_dec = mk_directions.count("decreasing")
            n_seeds = len(mk_directions)
            if n_inc > n_seeds * 0.6:
                verdict = "GAPS LENGTHENING -> likely eventual exhaustion"
            elif n_dec > n_seeds * 0.4:
                verdict = "GAPS SHORTENING -> accelerating (unexpected)"
            else:
                verdict = "GAPS STATIONARY -> self-sustaining cycling"
            log(f"    VERDICT: {verdict}")

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("gap_trend_results.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print("\nSaved to gap_trend_results.txt")


if __name__ == "__main__":
    main()
