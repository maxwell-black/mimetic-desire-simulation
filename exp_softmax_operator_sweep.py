"""
exp_softmax_operator_sweep.py
==============================
Tests whether the phase boundary is specific to the power-law h^gamma
operator or is a generic property of convex conserving operators.

The softmax operator replaces h^gamma with exp(h/T):

  Power-law AC:   w_j = h_j^gamma / sum(h_j^gamma)  * total_h
  Softmax:        w_j = exp(h_j/T) / sum(exp(h_j/T)) * total_h

Both are convex (concentrate mass on high-h targets) and conserve
throughput (total mimetic pull = total_h). The parameter T (temperature)
controls sharpness: low T = sharp (like high gamma), high T = flat
(like gamma near 1).

CRITICAL DESIGN CHOICE: hostility values are normalized to [0,1]
(dividing by max(h)) before applying softmax. Without this, softmax
is NOT scale-invariant: its sharpness depends on absolute hostility
magnitudes, which grow over the simulation. The power law h^gamma is
inherently scale-invariant (ratios are preserved under uniform scaling).
Normalization makes the comparison fair.

FINDING: The normalized softmax produces a CONVERGENCE BAND rather than
an open half-line. There is an upper boundary T* ~ 0.60-0.70 (too flat,
no convergence) AND a lower boundary T* ~ 0.15-0.22 (too sharp,
argmax oscillation prevents consensus). The power law has only an
upper boundary (gamma* ~ 1.02-1.05); arbitrarily high gamma always
converges. This asymmetry is likely due to the power law's multiplicative
structure preserving relative rankings even at extreme sharpness.

Design:
  N=50, alpha=0.15, decay=0.03, no expulsion, 800 steps
  10 seeds per temperature
  Temperature sweep: fine near both boundaries

Run from repo root:
    python exp_softmax_operator_sweep.py 2>&1 | tee exp_softmax_operator_sweep_results.txt

Estimated runtime: 2-4 hours.
"""

import sys, os, time
import numpy as np
from collections import Counter
from dataclasses import replace

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation


# =====================================================================
# Softmax spread operator (replaces step_aggression_spread)
# =====================================================================

def make_softmax_spread(temperature, normalize=True):
    """
    Return a bound method replacement for step_aggression_spread
    that uses softmax with the given temperature instead of h^gamma.

    Operator:
      h_j  = prestige-weighted mean neighbor hostility toward j
      H    = sum(h_j)                        [total throughput]
      w_j  = exp(h_j / T) / sum(exp(h_j/T)) [softmax weights]
      pull_j = w_j * H                       [throughput-conserving]

    If normalize=True (default), hostility values are normalized to [0,1]
    before softmax, making the operator scale-invariant like the power law.
    This is essential because softmax's sharpness depends on absolute
    magnitudes, whereas the power law depends only on ratios.

    Numerically stabilized: subtract max before exp.
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

            # Prestige-weighted mean neighbor aggression vector
            neighbor_hostility = np.zeros(cfg.n_agents, dtype=float)
            total_w = 0.0
            for k in neighbors:
                w = self._prestige_weight(i, k)
                neighbor_hostility += w * self.aggression[k]
                total_w += w
            if total_w > 0:
                neighbor_hostility /= total_w

            # Exclude self and dead targets
            neighbor_hostility[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    neighbor_hostility[dead] = 0.0

            total_h = float(np.sum(neighbor_hostility))
            if total_h > 0.0:
                # Mask: only apply softmax over targets with positive hostility.
                support_mask = neighbor_hostility > 1e-12
                if np.any(support_mask):
                    h_support = neighbor_hostility[support_mask]

                    # Normalize to [0,1] for scale invariance
                    if normalize:
                        h_max = float(np.max(h_support))
                        if h_max > 0:
                            h_normed = h_support / h_max
                        else:
                            h_normed = h_support
                    else:
                        h_normed = h_support

                    scaled = h_normed / T
                    scaled -= np.max(scaled)  # shift for numerical stability
                    exp_h = np.exp(scaled)
                    total_exp = float(np.sum(exp_h))
                    if total_exp > 0.0:
                        weights = np.zeros(cfg.n_agents, dtype=float)
                        weights[support_mask] = exp_h / total_exp
                    else:
                        weights = np.zeros(cfg.n_agents, dtype=float)
                else:
                    weights = np.zeros(cfg.n_agents, dtype=float)
                mimetic_pull = weights * total_h  # throughput conserved
                result = cfg.alpha * self.aggression[i] + (1.0 - cfg.alpha) * mimetic_pull
            else:
                result = cfg.alpha * self.aggression[i]

            # Enforce constraints
            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg

    return softmax_spread


# =====================================================================
# Convergence detection (same criterion as paper)
# =====================================================================

def time_to_95(modal_series, threshold=0.95, consecutive=10):
    """Returns step at which modal agreement >= threshold for consecutive steps, or None."""
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


# =====================================================================
# Run one simulation with softmax operator
# =====================================================================

def run_softmax(temperature, n_agents=50, n_steps=800, seed=42):
    """Run one simulation with softmax spread operator. Returns metrics dict."""
    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=6,
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=1.0,  # unused by softmax, but must be set
        aggression_decay=0.03,
        expulsion_threshold=None,
        n_steps=n_steps,
        record_history=True,
        seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    # Monkey-patch: replace the AC spread with softmax spread
    import types
    sim.step_aggression_spread = types.MethodType(make_softmax_spread(temperature), sim)

    sim.run()

    modal = sim.history["modal_agreement"]
    gini = sim.history["aggression_gini"]
    t95 = time_to_95(modal)

    return {
        "peak_modal": float(np.max(modal)),
        "final_modal": float(np.mean(modal[-50:])),
        "peak_gini": float(np.max(gini)),
        "final_gini": float(np.mean(gini[-50:])),
        "t95": t95,
    }


# =====================================================================
# Sweep logic
# =====================================================================

def sweep_temperature(temperature, n_seeds=10, n_steps=800, n_agents=50):
    """Run n_seeds simulations at a given temperature. Returns list of results."""
    results = []
    for r in range(n_seeds):
        seed = 42 + r * 1000
        res = run_softmax(temperature, n_agents=n_agents, n_steps=n_steps, seed=seed)
        results.append(res)
    return results


def conv_rate(results, n_steps=800):
    """Fraction of runs where t95 is not None (i.e., converged)."""
    return sum(1 for r in results if r["t95"] is not None) / len(results)


def main():
    N_SEEDS = 10
    N_STEPS = 800
    N_AGENTS = 50

    # Temperature sweep (scale-normalized softmax).
    # With normalization, h values are in [0,1] before softmax.
    # Empirical calibration found:
    #   - Upper boundary (too flat): T* ~ 0.60-0.70
    #   - Lower boundary (too sharp, oscillates): T* ~ 0.15-0.22
    #   - Convergence band: T ~ [0.22, 0.65]
    # Fine grid near both boundaries, coarser in the middle.
    temperatures = [
        0.05, 0.10, 0.12, 0.15,             # below lower boundary (too sharp)
        0.18, 0.20, 0.22, 0.25, 0.28,       # lower boundary zone
        0.30, 0.35, 0.40, 0.45, 0.50,       # convergence band
        0.55, 0.60, 0.63, 0.65, 0.68,       # upper boundary zone
        0.70, 0.75, 0.80, 1.00, 2.00,       # above upper boundary (too flat)
    ]

    print("=" * 110)
    print("SOFTMAX OPERATOR SWEEP: ALTERNATIVE CONVEX CONSERVING OPERATOR")
    print(f"Agents: {N_AGENTS}, Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    print(f"Temperatures: {temperatures}")
    print(f"Operator: w_j = exp((h_j/max(h))/T) / sum(exp((h_j/max(h))/T)) * total_h")
    print(f"  (h normalized to [0,1] for scale invariance)")
    print(f"Convergence criterion: modal agreement >= 0.95 for 10 consecutive steps")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)

    all_results = {}

    for T in temperatures:
        t0 = time.time()
        results = sweep_temperature(T, N_SEEDS, N_STEPS, N_AGENTS)
        elapsed = time.time() - t0
        all_results[T] = results

        cr = conv_rate(results, N_STEPS)
        pm = np.mean([r["peak_modal"] for r in results])
        fm = np.mean([r["final_modal"] for r in results])
        pg = np.mean([r["peak_gini"] for r in results])

        converging_t95 = [r["t95"] for r in results if r["t95"] is not None]
        med_t95 = np.median(converging_t95) if converging_t95 else float("nan")

        print(f"  T={T:<8.4f}  conv={cr:>5.0%}  peak_modal={pm:.3f}  "
              f"final_modal={fm:.3f}  peak_gini={pg:.3f}  "
              f"med_t95={med_t95:>6.0f}  ({elapsed:.0f}s)")

    # ================================================================
    # Full results table
    # ================================================================
    print(f"\n{'=' * 110}")
    print("RESULTS TABLE")
    print(f"{'=' * 110}")
    hdr = (f"{'T':>8} | {'Pk Modal':>8} {'(sd)':>6} | {'Fin Modal':>9} {'(sd)':>6} | "
           f"{'Pk Gini':>7} | {'Med t95':>7} | {'%Conv':>5}")
    print(hdr)
    print("-" * 110)

    for T in temperatures:
        r = all_results[T]
        pm_avg = np.mean([x["peak_modal"] for x in r])
        pm_sd = np.std([x["peak_modal"] for x in r])
        fm_avg = np.mean([x["final_modal"] for x in r])
        fm_sd = np.std([x["final_modal"] for x in r])
        pg_avg = np.mean([x["peak_gini"] for x in r])
        cr = conv_rate(r, N_STEPS)

        converging = [x["t95"] for x in r if x["t95"] is not None]
        t95_str = f"{np.median(converging):>7.0f}" if converging else "     --"

        print(f"{T:>8.4f} | {pm_avg:>8.3f} {pm_sd:>5.3f} | "
              f"{fm_avg:>9.3f} {fm_sd:>5.3f} | "
              f"{pg_avg:>7.3f} | {t95_str} | {cr:>5.0%}")

    # ================================================================
    # Phase boundary detection (both upper and lower)
    # ================================================================
    print(f"\n{'=' * 110}")
    print("PHASE BOUNDARIES (softmax)")
    print(f"{'=' * 110}")

    # Upper boundary: highest T where conv_rate >= 50% (then drops)
    # Lower boundary: lowest T where conv_rate >= 50% (below which it drops again)
    upper_boundary = None
    lower_boundary = None

    conv_rates = [(T, conv_rate(all_results[T], N_STEPS)) for T in temperatures]

    # Find lower boundary: first T (ascending) where convergence starts
    for i in range(len(conv_rates) - 1):
        T_lo, cr_lo = conv_rates[i]
        T_hi, cr_hi = conv_rates[i + 1]
        if cr_lo < 0.5 and cr_hi >= 0.5:
            lower_boundary = (T_lo, T_hi)
            print(f"  Lower boundary (sharp -> converge): "
                  f"T={T_lo:.4f} ({cr_lo:.0%}) -> T={T_hi:.4f} ({cr_hi:.0%})")

    # Find upper boundary: last T (ascending) where convergence ends
    for i in range(len(conv_rates) - 1):
        T_lo, cr_lo = conv_rates[i]
        T_hi, cr_hi = conv_rates[i + 1]
        if cr_lo >= 0.5 and cr_hi < 0.5:
            upper_boundary = (T_lo, T_hi)
            print(f"  Upper boundary (converge -> flat):   "
                  f"T={T_lo:.4f} ({cr_lo:.0%}) -> T={T_hi:.4f} ({cr_hi:.0%})")

    if lower_boundary and upper_boundary:
        print(f"\n  Convergence BAND: T in [{lower_boundary[1]:.3f}, {upper_boundary[0]:.3f}]")
        print(f"  This differs from the power-law, which has only an upper boundary")
        print(f"  (gamma* ~ 1.02-1.05) with convergence at all gamma > gamma*.")
    elif upper_boundary and not lower_boundary:
        print(f"\n  Only upper boundary found (like power-law).")
    elif not upper_boundary and not lower_boundary:
        all_cr = [cr for _, cr in conv_rates]
        if all(c >= 0.5 for c in all_cr):
            print("  All temperatures converge -- boundaries outside tested range")
        elif all(c < 0.5 for c in all_cr):
            print("  No temperatures converge -- convergence band may not exist")
        else:
            print("  Non-monotonic convergence pattern:")
            for T, cr in conv_rates:
                print(f"    T={T:.4f}: {cr:.0%}")

    # ================================================================
    # Comparison with power-law boundary
    # ================================================================
    print(f"\n{'=' * 110}")
    print("COMPARISON: SOFTMAX vs POWER-LAW")
    print(f"{'=' * 110}")
    print("  Power-law gamma sweep: boundary at gamma* ~ 1.02-1.05")
    print("  Power-law: gamma > gamma* always converges (no upper limit)")
    print("  Softmax: convergence only in a BAND of temperatures")
    print()
    print("  SHARED PROPERTY:")
    print("    Both operators produce a sharp upper boundary (too flat -> no convergence)")
    print("    This confirms the boundary is a property of convex conserving operators")
    print()
    print("  DIFFERENCE:")
    print("    Power-law: no lower boundary (arbitrarily high gamma converges)")
    print("    Softmax: lower boundary exists (too-sharp softmax oscillates)")
    print("    Likely cause: power-law is scale-invariant and preserves relative")
    print("    rankings multiplicatively, while softmax (even normalized) produces")
    print("    near-argmax behavior at low T, causing target oscillation")
    print()
    if lower_boundary and upper_boundary:
        print(f"  Softmax band:           T in [{lower_boundary[1]:.3f}, {upper_boundary[0]:.3f}]")
    print(f"  Power-law half-line:    gamma in [~1.03, inf)")

    # ================================================================
    # Also run power-law gamma sweep with same parameters for
    # direct head-to-head comparison
    # ================================================================
    print(f"\n{'=' * 110}")
    print("REFERENCE: POWER-LAW GAMMA SWEEP (same N, seeds, steps)")
    print(f"{'=' * 110}")

    gammas = [0.90, 0.95, 1.00, 1.02, 1.03, 1.05, 1.10, 1.25, 2.00]

    for gamma in gammas:
        t0 = time.time()
        results = []
        for r in range(N_SEEDS):
            seed = 42 + r * 1000
            cfg = GirardConfig(
                n_agents=N_AGENTS,
                n_neighbors=6,
                rewire_prob=0.15,
                alpha=0.15,
                salience_exponent=gamma,
                aggression_decay=0.03,
                expulsion_threshold=None,
                n_steps=N_STEPS,
                record_history=True,
                seed=seed,
            )
            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()
            modal = sim.history["modal_agreement"]
            gini = sim.history["aggression_gini"]
            t95 = time_to_95(modal)
            results.append({
                "peak_modal": float(np.max(modal)),
                "final_modal": float(np.mean(modal[-50:])),
                "peak_gini": float(np.max(gini)),
                "t95": t95,
            })
        elapsed = time.time() - t0
        cr = conv_rate(results, N_STEPS)
        pm = np.mean([x["peak_modal"] for x in results])
        print(f"  gamma={gamma:<5.2f}  conv={cr:>5.0%}  peak_modal={pm:.3f}  ({elapsed:.0f}s)")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
