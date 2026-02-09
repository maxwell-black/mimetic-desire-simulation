"""
small_n_utils.py
================
Shared utilities for the small-N experiment battery.

Contains:
  - adaptive_unanimity_threshold(): principled discrete threshold
  - adaptive_k(): WS neighbor count safe for very small N
  - get_modal_target(): modal agreement computation
  - run_unanimity_triggered(): core simulation runner with adaptive trigger
  - count_fragments(): network fragmentation analysis
  - classify_exhaustion(): self-exhaustion classification

All small-N experiment scripts import from this module.
Place in the same directory as girard_2x2_v3.py.
"""

import numpy as np
import networkx as nx
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation, VARIANT_MAP


# =========================================================================
# Adaptive threshold
# =========================================================================

def adaptive_unanimity_threshold(n_eligible):
    """Adaptive threshold: 'all but at most one holdout', capped at 0.95.

    Operationalizes near-unanimity consistently across group sizes:
      N=5  -> 0.80 (4/5)
      N=10 -> 0.90 (9/10)
      N=15 -> 0.933 (14/15)
      N>=20 -> 0.95 (identical to all prior experiments)
    """
    if n_eligible <= 1:
        return 1.0
    return min(0.95, (n_eligible - 1) / n_eligible)


def adaptive_k(n_agents):
    """WS neighbor count: 12% of N, clamped [6, 20], forced even.
    At very small N, clamp to N-1 (complete graph) and force even."""
    k = max(6, min(int(n_agents * 0.12), 20))
    k = min(k, n_agents - 1)  # WS requires k < N
    if k % 2 == 1:
        k -= 1
    k = max(2, k)  # WS requires k >= 2
    return k


# =========================================================================
# Modal agreement
# =========================================================================

def get_modal_target(sim):
    """Return (modal_agreement, modal_target_id)."""
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


# =========================================================================
# Fragment analysis
# =========================================================================

def count_fragments(sim):
    """Count connected components and largest fragment among alive agents."""
    alive = set(sim._alive_ids())
    if len(alive) == 0:
        return 0, 0
    subgraph = sim.graph.subgraph(alive)
    components = list(nx.connected_components(subgraph))
    sizes = [len(c) for c in components]
    return len(components), max(sizes)


# =========================================================================
# Core runner: unanimity-triggered expulsion, any variant
# =========================================================================

def run_unanimity_triggered(n_agents, gamma, variant="AC", n_steps=5000,
                            seed=42, cooldown=5, record_history=False,
                            source_override=None, spread_override=None,
                            timeout_seconds=None):
    """
    Run one simulation with adaptive unanimity-triggered expulsion.

    timeout_seconds: wall-clock safety net. If None, defaults to
      max(60, n_agents * n_steps * 0.001) -- generous enough to never
      fire under normal conditions. Exists to catch pathological hangs,
      NOT as a theoretical outcome category.

    Returns dict with all metrics + optional modal_series.
    """
    import time as _time

    if timeout_seconds is None:
        timeout_seconds = max(60, n_agents * n_steps * 0.001)

    if source_override and spread_override:
        source, spread = source_override, spread_override
    else:
        source, spread = VARIANT_MAP[variant]
    k = adaptive_k(n_agents)

    cfg = GirardConfig(
        n_agents=n_agents,
        n_neighbors=k,
        rewire_prob=0.15,
        alpha=0.15,
        salience_exponent=gamma,
        expulsion_threshold=None,
        n_steps=n_steps,
        record_history=record_history,
        seed=seed,
    )
    sim = GirardSimulation(cfg, source=source, spread=spread)

    modal_series = []
    expulsion_steps = []
    alive_counts = []
    steps_since_expulsion = cooldown + 1
    peak_modal = 0.0
    timed_out = False
    wall_start = _time.monotonic()

    for step in range(n_steps):
        # Wall-clock safety net
        if _time.monotonic() - wall_start > timeout_seconds:
            timed_out = True
            break

        ma, mt = get_modal_target(sim)
        modal_series.append(ma)
        n_alive_now = len(sim._alive_ids())
        alive_counts.append(n_alive_now)
        if ma > peak_modal:
            peak_modal = ma

        # Adaptive unanimity trigger
        thresh = adaptive_unanimity_threshold(n_alive_now)
        if (ma >= thresh and
            steps_since_expulsion > cooldown and
            mt is not None and
            n_alive_now > 2):

            sim.alive[mt] = False
            for other in sim._alive_ids():
                sim.aggression[other][mt] = 0.0
            sim.aggression[mt][:] = 0.0
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
        sim.step_status_update()
        sim.step_num += 1

    # --- Compute metrics ---
    n_alive = sum(1 for v in sim.alive.values() if v)
    n_exp = len(expulsion_steps)
    pct_consumed = (n_agents - n_alive) / n_agents
    effective_steps = len(modal_series)  # may be < n_steps if timed out

    # Self-exhaustion classification
    if timed_out:
        status = "timeout"
        self_exhausted = None
    else:
        status, self_exhausted = classify_exhaustion(
            modal_series, expulsion_steps, effective_steps, n_alive
        )

    # Peace after first expulsion
    first_peace = None
    first_reconverge = None
    if n_exp >= 1:
        t0 = expulsion_steps[0]
        peace_count = 0
        for t in range(t0 + 1, effective_steps):
            if modal_series[t] < 0.5:
                peace_count += 1
            else:
                break
        first_peace = peace_count
        # Reconvergence uses adaptive threshold for current alive count
        for t in range(t0 + 1, effective_steps):
            n_exp_so_far = sum(1 for es in expulsion_steps if es <= t)
            n_alive_at_t = n_agents - n_exp_so_far
            thresh_at_t = adaptive_unanimity_threshold(n_alive_at_t)
            if modal_series[t] >= thresh_at_t:
                first_reconverge = t - t0
                break

    # Inter-expulsion gaps
    if n_exp >= 2:
        gaps = [expulsion_steps[i+1] - expulsion_steps[i]
                for i in range(n_exp - 1)]
        med_gap = float(np.median(gaps))
    else:
        gaps = []
        med_gap = None

    # Network fragmentation
    n_fragments, largest_fragment = count_fragments(sim)

    result = {
        "N": n_agents,
        "gamma": gamma,
        "variant": variant,
        "seed": seed,
        "k": k,
        "n_expulsions": n_exp,
        "pct_consumed": pct_consumed,
        "n_alive": n_alive,
        "status": status,
        "self_exhausted": self_exhausted,
        "timed_out": timed_out,
        "steps_completed": effective_steps,
        "first_peace": first_peace,
        "first_reconverge": first_reconverge,
        "med_gap": med_gap,
        "gaps": gaps,
        "expulsion_steps": expulsion_steps,
        "n_fragments": n_fragments,
        "largest_fragment": largest_fragment,
        "peak_modal": peak_modal,
    }
    if record_history:
        result["modal_series"] = modal_series
        result["alive_counts"] = alive_counts
        result["sim"] = sim
    return result


def classify_exhaustion(modal_series, expulsion_steps, n_steps, n_alive,
                        min_silence=500):
    """Classify whether the run genuinely self-exhausted.
    Uses adaptive threshold based on surviving population."""
    if not expulsion_steps:
        return "no_expulsions", None

    last_exp = expulsion_steps[-1]
    remaining = n_steps - last_exp - 1

    # Check if modal agreement ever hit adaptive threshold again
    final_thresh = adaptive_unanimity_threshold(n_alive)
    reconverged = False
    for t in range(last_exp + 1, n_steps):
        if modal_series[t] >= final_thresh:
            reconverged = True
            break

    if reconverged:
        return "still_cycling", False
    elif remaining >= min_silence:
        return "genuine_exhaustion", True
    else:
        return "censored", None
