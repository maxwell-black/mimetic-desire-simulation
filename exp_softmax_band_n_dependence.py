"""
exp_softmax_band_n_dependence.py
=================================
Tests how the softmax convergence band depends on population size N.

QUESTION:
  The softmax operator produces a convergence band T in [T_lower, T_upper]
  rather than the power-law's open half-line gamma in [gamma*, inf).
  Does this band narrow, widen, or stay constant with N?

PREDICTIONS:
  - Band NARROWS with N: stochastic fluctuations driving argmax flipping
    become relatively smaller (law-of-large-numbers on salience vector),
    pushing T_lower upward. This means softmax becomes MORE fragile at
    scale and the power-law choice is increasingly justified.
  - Band WIDENS with N: more targets create a richer gradient landscape,
    giving softmax more room to work. Would weaken the power-law argument.
  - Band CONSTANT: the band is a property of the operator, not the
    population. Worth reporting as an invariant.

DESIGN:
  N in {10, 20, 30, 50, 75, 100, 150, 200}
  For each N, sweep temperatures across a range that covers both boundaries.
  10 seeds per (N, T) combination.
  Steps scaled: max(400, 10*N) to allow convergence at larger N.
  No expulsion (expulsion_threshold=None).

  Temperature grid: adaptive per-N based on the N=50 baseline
  (band ~ [0.20, 0.65]). Use a fixed coarse grid plus fine grids
  near estimated boundaries.

  We use the NORMALIZED softmax from exp_softmax_operator_sweep.py
  (identical operator).

Run:
    python exp_softmax_band_n_dependence.py 2>&1 | tee exp_softmax_band_n_dependence_results.txt

Estimated runtime: 4-8 hours (dominated by N=150, 200 runs).
"""

import sys, os, time, types
import numpy as np
from collections import Counter
from dataclasses import replace

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation


# =====================================================================
# Softmax spread operator (identical to exp_softmax_operator_sweep.py)
# =====================================================================

def make_softmax_spread(temperature, normalize=True):
    """
    Softmax spread operator with throughput conservation and optional
    normalization for scale invariance. See exp_softmax_operator_sweep.py
    for full documentation.
    """
    T = float(temperature)

    def softmax_spread(self):
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            neighbor_hostility = np.zeros(cfg.n_agents, dtype=float)
            total_w = 0.0
            for k in neighbors:
                w = self._prestige_weight(i, k)
                neighbor_hostility += w * self.aggression[k]
                total_w += w
            if total_w > 0:
                neighbor_hostility /= total_w

            neighbor_hostility[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    neighbor_hostility[dead] = 0.0

            total_h = float(np.sum(neighbor_hostility))
            if total_h > 0.0:
                support_mask = neighbor_hostility > 1e-12
                if np.any(support_mask):
                    h_support = neighbor_hostility[support_mask]

                    if normalize:
                        h_max = float(np.max(h_support))
                        if h_max > 0:
                            h_normed = h_support / h_max
                        else:
                            h_normed = h_support
                    else:
                        h_normed = h_support

                    scaled = h_normed / T
                    scaled -= np.max(scaled)
                    exp_h = np.exp(scaled)
                    total_exp = float(np.sum(exp_h))
                    if total_exp > 0.0:
                        weights = np.zeros(cfg.n_agents, dtype=float)
                        weights[support_mask] = exp_h / total_exp
                    else:
                        weights = np.zeros(cfg.n_agents, dtype=float)
                else:
                    weights = np.zeros(cfg.n_agents, dtype=float)
                mimetic_pull = weights * total_h
                result = cfg.alpha * self.aggression[i] + (1.0 - cfg.alpha) * mimetic_pull
            else:
                result = cfg.alpha * self.aggression[i]

            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg

    return softmax_spread


# =====================================================================
# Convergence detection
# =====================================================================

def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


# =====================================================================
# Run one simulation
# =====================================================================

def run_softmax_sim(temperature, n_agents, n_steps, seed):
    """Run one simulation with softmax operator. Returns metrics dict."""
    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=min(6, n_agents - 1),  # handle small N
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=1.0,  # unused
        aggression_decay=0.03,
        expulsion_threshold=None,
        n_steps=n_steps,
        record_history=True,
        seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")
    sim.step_aggression_spread = types.MethodType(make_softmax_spread(temperature), sim)
    sim.run()

    modal = sim.history["modal_agreement"]
    t95 = time_to_95(modal)

    return {
        "peak_modal": float(np.max(modal)),
        "final_modal": float(np.mean(modal[-50:])) if len(modal) >= 50 else float(np.mean(modal)),
        "t95": t95,
    }


# =====================================================================
# Main
# =====================================================================

def main():
    N_SEEDS = 10

    # Population sizes to test
    pop_sizes = [10, 20, 30, 50, 75, 100, 150, 200]

    # Temperature grid: use a unified grid that covers the expected range
    # for all N values. Fine near boundaries, coarser in interior.
    temperatures = [
        0.05, 0.08, 0.10, 0.12, 0.15, 0.18,   # below/near lower boundary
        0.20, 0.22, 0.25, 0.28, 0.30,           # lower boundary zone
        0.35, 0.40, 0.45, 0.50, 0.55, 0.60,     # band interior
        0.63, 0.65, 0.68, 0.70, 0.75, 0.80,     # upper boundary zone
        0.90, 1.00,                               # above upper boundary
    ]

    print("=" * 120)
    print("SOFTMAX BAND N-DEPENDENCE EXPERIMENT")
    print(f"Question: Does the convergence band [T_lower, T_upper] narrow with N?")
    print(f"Population sizes: {pop_sizes}")
    print(f"Temperatures: {len(temperatures)} values from {temperatures[0]} to {temperatures[-1]}")
    print(f"Seeds per (N,T): {N_SEEDS}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)

    # Storage
    all_results = {}  # (N, T) -> list of result dicts

    for N in pop_sizes:
        n_steps = max(400, 10 * N)
        print(f"\n--- N={N}, steps={n_steps} ---")
        t0_n = time.time()

        for T in temperatures:
            t0 = time.time()
            results = []
            for seed_idx in range(N_SEEDS):
                seed = 42 + seed_idx * 1000
                res = run_softmax_sim(T, N, n_steps, seed)
                results.append(res)
            elapsed = time.time() - t0

            cr = sum(1 for r in results if r["t95"] is not None) / len(results)
            pm = np.mean([r["peak_modal"] for r in results])
            all_results[(N, T)] = results

            print(f"  N={N:>3d}  T={T:<6.3f}  conv={cr:>5.0%}  peak_modal={pm:.3f}  ({elapsed:.0f}s)")

        elapsed_n = time.time() - t0_n
        print(f"  N={N} total: {elapsed_n:.0f}s")

    # ================================================================
    # Phase boundary detection per N
    # ================================================================
    print(f"\n{'=' * 120}")
    print("PHASE BOUNDARIES BY N")
    print(f"{'=' * 120}")

    boundaries = {}  # N -> (T_lower, T_upper, band_width)

    for N in pop_sizes:
        conv_rates = []
        for T in temperatures:
            results = all_results[(N, T)]
            cr = sum(1 for r in results if r["t95"] is not None) / len(results)
            conv_rates.append((T, cr))

        # Find lower boundary (first T where conv >= 50%)
        lower = None
        for i in range(len(conv_rates) - 1):
            T_lo, cr_lo = conv_rates[i]
            T_hi, cr_hi = conv_rates[i + 1]
            if cr_lo < 0.5 and cr_hi >= 0.5:
                # Linear interpolation
                lower = T_lo + (T_hi - T_lo) * (0.5 - cr_lo) / (cr_hi - cr_lo)
                break

        # Find upper boundary (last T where conv drops below 50%)
        upper = None
        for i in range(len(conv_rates) - 1):
            T_lo, cr_lo = conv_rates[i]
            T_hi, cr_hi = conv_rates[i + 1]
            if cr_lo >= 0.5 and cr_hi < 0.5:
                upper = T_lo + (T_hi - T_lo) * (0.5 - cr_lo) / (cr_hi - cr_lo)

        if lower is not None and upper is not None:
            width = upper - lower
            boundaries[N] = (lower, upper, width)
            print(f"  N={N:>3d}:  T_lower={lower:.3f}  T_upper={upper:.3f}  "
                  f"band_width={width:.3f}")
        elif lower is not None:
            print(f"  N={N:>3d}:  T_lower={lower:.3f}  T_upper=???  (no upper boundary found)")
            boundaries[N] = (lower, None, None)
        elif upper is not None:
            print(f"  N={N:>3d}:  T_lower=???   T_upper={upper:.3f}  (no lower boundary found)")
            boundaries[N] = (None, upper, None)
        else:
            # Check if all converge or none converge
            all_cr = [cr for _, cr in conv_rates]
            if all(c >= 0.5 for c in all_cr):
                print(f"  N={N:>3d}:  ALL temperatures converge (boundaries outside range)")
            elif all(c < 0.5 for c in all_cr):
                print(f"  N={N:>3d}:  NO temperatures converge")
            else:
                print(f"  N={N:>3d}:  Non-monotonic pattern, boundary detection failed")
            boundaries[N] = (None, None, None)

    # ================================================================
    # Full convergence rate heatmap
    # ================================================================
    print(f"\n{'=' * 120}")
    print("CONVERGENCE RATE TABLE: N (rows) x T (columns)")
    print(f"{'=' * 120}")

    # Header
    col_temps = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.65, 0.70, 0.80, 1.00]
    hdr = f"{'N':>5} |" + "".join(f" {T:>5.2f}" for T in col_temps)
    print(hdr)
    print("-" * 120)

    for N in pop_sizes:
        vals = []
        for T in col_temps:
            if (N, T) in all_results:
                results = all_results[(N, T)]
                cr = sum(1 for r in results if r["t95"] is not None) / len(results)
                vals.append(f" {cr:>5.0%}")
            else:
                vals.append("    --")
        print(f"{N:>5d} |" + "".join(vals))

    # ================================================================
    # Band width trend
    # ================================================================
    print(f"\n{'=' * 120}")
    print("BAND WIDTH TREND")
    print(f"{'=' * 120}")

    ns_with_bands = [(N, b) for N, b in boundaries.items()
                     if b[2] is not None]
    if len(ns_with_bands) >= 2:
        ns = [x[0] for x in ns_with_bands]
        widths = [x[1][2] for x in ns_with_bands]
        lowers = [x[1][0] for x in ns_with_bands]
        uppers = [x[1][1] for x in ns_with_bands]

        print(f"{'N':>5} | {'T_lower':>8} {'T_upper':>8} {'Width':>8}")
        print("-" * 40)
        for N, (lo, up, w) in ns_with_bands:
            print(f"{N:>5d} | {lo:>8.3f} {up:>8.3f} {w:>8.3f}")

        # Trend analysis
        if len(widths) >= 3:
            # Simple monotonicity check
            narrowing = all(widths[i] >= widths[i + 1] for i in range(len(widths) - 1))
            widening = all(widths[i] <= widths[i + 1] for i in range(len(widths) - 1))

            if narrowing:
                print("\n  Band width is MONOTONICALLY DECREASING with N.")
                print("  The softmax operator becomes MORE fragile at larger populations.")
                print("  This strongly supports the power-law operator choice.")
            elif widening:
                print("\n  Band width is MONOTONICALLY INCREASING with N.")
                print("  The softmax operator becomes more robust at larger populations.")
            else:
                print("\n  Band width trend is NON-MONOTONIC.")

            # Which boundary moves?
            lo_increasing = all(lowers[i] <= lowers[i + 1] for i in range(len(lowers) - 1))
            up_decreasing = all(uppers[i] >= uppers[i + 1] for i in range(len(uppers) - 1))

            if lo_increasing:
                print("  T_lower is INCREASING with N (argmax oscillation gets worse).")
            if up_decreasing:
                print("  T_upper is DECREASING with N (upper boundary also shifts).")
            if lo_increasing and not up_decreasing:
                print("  Narrowing is driven by the LOWER boundary moving up.")
                print("  Interpretation: the argmax-oscillation failure mode worsens with N,")
                print("  likely because more targets = more ways to flip the argmax.")
    else:
        print("  Insufficient data to determine band width trend.")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
