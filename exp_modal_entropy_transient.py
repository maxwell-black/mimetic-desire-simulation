"""
exp_modal_entropy_transient.py
===============================
Tests whether power-law convergence exhibits a two-phase dynamical
structure: an early oscillation phase (high target volatility) followed
by a smooth convergence phase (low volatility, compounding advantage).

METHOD:
  For each agent at each timestep, record which target receives the most
  aggression from that agent. The "modal target" is the plurality winner
  across all agents. We track:

  1. Modal target IDENTITY at each step (does it change between steps?)
  2. Sliding-window entropy of the modal-target indicator over a window
     of W steps. High entropy = target is flipping; low entropy = stable.
  3. "Target switch rate": fraction of consecutive step-pairs where the
     modal target changes identity, computed in a sliding window.

  The two-phase hypothesis predicts:
    - Near the phase boundary (gamma ~ 1.03-1.10): a transient volatility
      spike (high entropy / high switch rate) that decays into smooth
      convergence. The "monstrous doubles" regime.
    - Far above the boundary (gamma ~ 2.0): immediate low volatility,
      monotonic convergence. The "funnel" regime.

  The reviewer's prediction: the crossover between these regimes is
  continuous and gamma-dependent, not a binary phase.

DESIGN:
  gamma in {1.03, 1.05, 1.08, 1.10, 1.15, 1.25, 1.50, 2.00}
  N=50, alpha=0.15, decay=0.03, no expulsion, 400 steps, 20 seeds
  Sliding window width W=15 steps

  We report per-gamma:
    - Mean entropy trajectory (averaged over seeds)
    - Mean switch-rate trajectory
    - "Transient score": ratio of mean entropy in steps [5,30] vs [100,200]
      (>1 means volatility spike then decay; ~1 means no transient)

Run:
    python exp_modal_entropy_transient.py 2>&1 | tee exp_modal_entropy_transient_results.txt

Estimated runtime: 20-40 minutes.
"""

import sys, os, time
import numpy as np
from collections import Counter
from dataclasses import replace

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import GirardConfig, GirardSimulation


# =====================================================================
# Per-step modal target extraction
# =====================================================================

def extract_modal_targets(sim):
    """
    Re-extract the modal target at each recorded step from a completed
    simulation's aggression history.

    Since the sim only records aggregate modal_agreement (not which target),
    we need to record targets during the run. This function instead runs
    a fresh simulation step-by-step and records the modal target identity.

    Returns: list of (modal_target_id, modal_agreement) per step.
    """
    # This is handled by run_with_target_tracking below.
    raise NotImplementedError("Use run_with_target_tracking instead")


def run_with_target_tracking(cfg, n_steps=400):
    """
    Run a simulation step-by-step, recording the modal target identity
    at each timestep.

    Returns dict with:
      modal_targets: list[int|None] -- modal target ID at each step
      modal_agreements: list[float] -- modal agreement fraction at each step
      aggression_gini: list[float]
    """
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_targets = []
    modal_agreements = []
    aggression_gini = []

    for step in range(n_steps):
        sim.step()

        # Extract modal target identity (mirrors record_metrics logic)
        alive = sim._alive_ids()
        top_targets = []
        thresh = 1e-8
        for i in alive:
            targets = [j for j in alive if j != i]
            if not targets:
                continue
            vec = sim.aggression[i][targets]
            if float(np.sum(vec)) < thresh:
                continue
            top_j = targets[int(np.argmax(vec))]
            top_targets.append(top_j)

        if top_targets:
            counts = Counter(top_targets)
            modal_target = counts.most_common(1)[0][0]
            modal_agreement = counts[modal_target] / len(top_targets)
        else:
            modal_target = None
            modal_agreement = 0.0

        modal_targets.append(modal_target)
        modal_agreements.append(modal_agreement)

        # Gini
        _, received = sim._received_aggression_vector()
        aggression_gini.append(sim._gini(received))

    return {
        "modal_targets": modal_targets,
        "modal_agreements": modal_agreements,
        "aggression_gini": aggression_gini,
    }


# =====================================================================
# Sliding-window entropy and switch rate
# =====================================================================

def sliding_window_entropy(targets, window=15):
    """
    Compute sliding-window Shannon entropy (base 2) of the modal target
    identity sequence.

    targets: list of target IDs (ints or None)
    window: window width

    Returns: list of entropy values, length = len(targets) - window + 1
    """
    n = len(targets)
    if n < window:
        return []

    entropies = []
    for start in range(n - window + 1):
        chunk = targets[start:start + window]
        # Filter None
        valid = [t for t in chunk if t is not None]
        if not valid:
            entropies.append(0.0)
            continue
        counts = Counter(valid)
        total = len(valid)
        h = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                h -= p * np.log2(p)
        entropies.append(h)

    return entropies


def sliding_window_switch_rate(targets, window=15):
    """
    Fraction of consecutive step-pairs in each window where the modal
    target changes identity.

    Returns: list of switch rates, length = len(targets) - window + 1
    """
    n = len(targets)
    if n < window:
        return []

    rates = []
    for start in range(n - window + 1):
        chunk = targets[start:start + window]
        switches = 0
        pairs = 0
        for k in range(len(chunk) - 1):
            if chunk[k] is not None and chunk[k + 1] is not None:
                pairs += 1
                if chunk[k] != chunk[k + 1]:
                    switches += 1
        rates.append(switches / pairs if pairs > 0 else 0.0)

    return rates


# =====================================================================
# Main experiment
# =====================================================================

def main():
    N_AGENTS = 50
    N_STEPS = 400
    N_SEEDS = 20
    WINDOW = 15

    gammas = [1.03, 1.05, 1.08, 1.10, 1.15, 1.25, 1.50, 2.00]

    # Also run two sub-threshold values as controls
    control_gammas = [0.95, 1.00]
    all_gammas = control_gammas + gammas

    print("=" * 110)
    print("MODAL TARGET ENTROPY TRANSIENT EXPERIMENT")
    print(f"Tests two-phase hypothesis: oscillation-then-convergence at near-boundary gamma")
    print(f"Agents: {N_AGENTS}, Steps: {N_STEPS}, Seeds: {N_SEEDS}, Window: {WINDOW}")
    print(f"Gammas: {all_gammas}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)

    # Storage: per-gamma, averaged over seeds
    results = {}

    for gamma in all_gammas:
        t0 = time.time()

        all_entropies = []
        all_switch_rates = []
        all_modal_agreements = []
        n_converged = 0

        for seed_idx in range(N_SEEDS):
            seed = 42 + seed_idx * 1000

            cfg = GirardConfig(
                n_agents=N_AGENTS,
                n_neighbors=6,
                rewire_prob=0.15,
                alpha=0.15,
                salience_exponent=gamma,
                aggression_decay=0.03,
                expulsion_threshold=None,
                n_steps=N_STEPS,
                record_history=False,  # we track manually
                seed=seed,
            )

            res = run_with_target_tracking(cfg, N_STEPS)

            ent = sliding_window_entropy(res["modal_targets"], WINDOW)
            sw = sliding_window_switch_rate(res["modal_targets"], WINDOW)

            all_entropies.append(ent)
            all_switch_rates.append(sw)
            all_modal_agreements.append(res["modal_agreements"])

            # Check convergence (95% modal for 10 consecutive steps)
            ma = res["modal_agreements"]
            converged = False
            for t in range(len(ma) - 10):
                if all(ma[t + k] >= 0.95 for k in range(10)):
                    converged = True
                    break
            if converged:
                n_converged += 1

        elapsed = time.time() - t0

        # Align and average trajectories
        min_ent_len = min(len(e) for e in all_entropies)
        ent_array = np.array([e[:min_ent_len] for e in all_entropies])
        sw_array = np.array([s[:min_ent_len] for s in all_switch_rates])
        ma_array = np.array([m[:N_STEPS] for m in all_modal_agreements])

        mean_ent = np.mean(ent_array, axis=0)
        mean_sw = np.mean(sw_array, axis=0)
        mean_ma = np.mean(ma_array, axis=0)

        # Transient score: mean entropy in early window vs late window
        # Early: steps 5-30 (indices 5-30 of the entropy series,
        #         which correspond to ~steps 5+W/2 to 30+W/2 center points)
        # Late:  steps 100-200
        early_start, early_end = 5, 30
        late_start, late_end = 100, 200

        early_ent = float(np.mean(mean_ent[early_start:early_end])) if early_end <= len(mean_ent) else float("nan")
        late_ent = float(np.mean(mean_ent[late_start:late_end])) if late_end <= len(mean_ent) else float("nan")
        transient_score = early_ent / late_ent if late_ent > 1e-10 else float("inf")

        early_sw = float(np.mean(mean_sw[early_start:early_end])) if early_end <= len(mean_sw) else float("nan")
        late_sw = float(np.mean(mean_sw[late_start:late_end])) if late_end <= len(mean_sw) else float("nan")
        sw_transient = early_sw / late_sw if late_sw > 1e-10 else float("inf")

        # Peak entropy and its location
        peak_ent_idx = int(np.argmax(mean_ent))
        peak_ent_val = float(mean_ent[peak_ent_idx])

        # Time to "settle": first step where entropy drops below 0.5 and stays below
        settle_step = None
        for t in range(len(mean_ent)):
            if mean_ent[t] < 0.5:
                if all(mean_ent[t + k] < 0.5 for k in range(min(10, len(mean_ent) - t))):
                    settle_step = t
                    break

        results[gamma] = {
            "mean_entropy": mean_ent,
            "mean_switch_rate": mean_sw,
            "mean_modal_agreement": mean_ma,
            "early_ent": early_ent,
            "late_ent": late_ent,
            "transient_score": transient_score,
            "early_sw": early_sw,
            "late_sw": late_sw,
            "sw_transient": sw_transient,
            "peak_ent_val": peak_ent_val,
            "peak_ent_step": peak_ent_idx,
            "settle_step": settle_step,
            "conv_rate": n_converged / N_SEEDS,
        }

        settle_str = f"{settle_step:>4d}" if settle_step is not None else "  --"
        print(f"  gamma={gamma:<5.2f}  conv={n_converged / N_SEEDS:>5.0%}  "
              f"peak_ent={peak_ent_val:.3f}@step{peak_ent_idx:<4d}  "
              f"early_ent={early_ent:.3f}  late_ent={late_ent:.3f}  "
              f"transient={transient_score:>6.2f}x  "
              f"settle={settle_str}  ({elapsed:.0f}s)")

    # ================================================================
    # Summary table
    # ================================================================
    print(f"\n{'=' * 110}")
    print("SUMMARY TABLE")
    print(f"{'=' * 110}")
    hdr = (f"{'gamma':>6} | {'%Conv':>5} | {'Peak Ent':>8} {'@Step':>6} | "
           f"{'Early H':>7} {'Late H':>7} {'Ratio':>6} | "
           f"{'Early SW':>8} {'Late SW':>8} {'Ratio':>6} | {'Settle':>6}")
    print(hdr)
    print("-" * 110)

    for gamma in all_gammas:
        r = results[gamma]
        settle_str = f"{r['settle_step']:>6d}" if r['settle_step'] is not None else "    --"
        print(f"{gamma:>6.2f} | {r['conv_rate']:>5.0%} | "
              f"{r['peak_ent_val']:>8.3f} {r['peak_ent_step']:>6d} | "
              f"{r['early_ent']:>7.3f} {r['late_ent']:>7.3f} {r['transient_score']:>6.2f} | "
              f"{r['early_sw']:>8.3f} {r['late_sw']:>8.3f} {r['sw_transient']:>6.2f} | "
              f"{settle_str}")

    # ================================================================
    # Entropy trajectory snapshots (every 25 steps)
    # ================================================================
    print(f"\n{'=' * 110}")
    print("ENTROPY TRAJECTORIES (mean over seeds, sampled every 25 steps)")
    print(f"{'=' * 110}")

    sample_steps = list(range(0, 350, 25))
    header = f"{'gamma':>6} |" + "".join(f" t={s:>3d}" for s in sample_steps)
    print(header)
    print("-" * 110)
    for gamma in all_gammas:
        r = results[gamma]
        vals = []
        for s in sample_steps:
            if s < len(r["mean_entropy"]):
                vals.append(f" {r['mean_entropy'][s]:>5.3f}")
            else:
                vals.append("    --")
        print(f"{gamma:>6.2f} |" + "".join(vals))

    # ================================================================
    # Switch rate trajectory snapshots
    # ================================================================
    print(f"\n{'=' * 110}")
    print("SWITCH RATE TRAJECTORIES (mean over seeds, sampled every 25 steps)")
    print(f"{'=' * 110}")

    print(header)
    print("-" * 110)
    for gamma in all_gammas:
        r = results[gamma]
        vals = []
        for s in sample_steps:
            if s < len(r["mean_switch_rate"]):
                vals.append(f" {r['mean_switch_rate'][s]:>5.3f}")
            else:
                vals.append("    --")
        print(f"{gamma:>6.2f} |" + "".join(vals))

    # ================================================================
    # Interpretation
    # ================================================================
    print(f"\n{'=' * 110}")
    print("INTERPRETATION")
    print(f"{'=' * 110}")
    print()
    print("Two-phase hypothesis predictions:")
    print("  - Transient score >> 1 at near-boundary gamma (1.03-1.10): oscillation then convergence")
    print("  - Transient score ~ 1 at high gamma (1.50-2.00): immediate convergence, no transient")
    print("  - Settle step decreasing with gamma: stronger funnel = faster stabilization")
    print()

    # Classify each gamma
    for gamma in gammas:
        r = results[gamma]
        ts = r["transient_score"]
        if ts > 3.0:
            regime = "STRONG TRANSIENT (oscillation-then-convergence)"
        elif ts > 1.5:
            regime = "MODERATE TRANSIENT"
        elif ts > 1.1:
            regime = "WEAK TRANSIENT"
        else:
            regime = "NO TRANSIENT (immediate funnel)"
        print(f"  gamma={gamma:.2f}: transient={ts:.2f}x -> {regime}")

    print()
    # Check for continuous crossover
    transient_scores = [(g, results[g]["transient_score"]) for g in gammas]
    is_monotone = all(
        transient_scores[i][1] >= transient_scores[i + 1][1]
        for i in range(len(transient_scores) - 1)
    )
    if is_monotone:
        print("  Transient score is MONOTONICALLY DECREASING with gamma.")
        print("  This supports a continuous crossover from oscillation-dominated")
        print("  to funnel-dominated dynamics, as the reviewer predicted.")
    else:
        print("  Transient score is NOT monotonically decreasing with gamma.")
        print("  The crossover may not be as clean as predicted, or noise")
        print("  in the transient estimate may obscure the trend.")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
