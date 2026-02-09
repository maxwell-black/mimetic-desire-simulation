"""
exp3_param_sensitivity.py
=========================
Preemptive robustness check: does the sharp phase transition at
gamma* ~ 1.02-1.05 survive across different parameter settings?

Sweeps:
  - alpha in {0.05, 0.10, 0.15, 0.20, 0.30}
  - aggression_decay in {0.01, 0.03, 0.05, 0.10}
  - expulsion_threshold in {4.0, 8.0, 16.0}

For each parameter combo, finds the gamma at which >=50% of seeds
converge (modal agreement >= 0.95 for 10 consecutive steps).

This is 5 * 4 * 3 = 60 parameter combos, each swept over ~8 gammas
with 10 seeds. Total: ~4800 sims at N=50, 600 steps.

Reviewer objection addressed: "your results depend on fine-tuned parameters."

Run from repo root:
    python exp3_param_sensitivity.py 2>&1 | tee exp3_param_sensitivity_results.txt

Estimated runtime: 6-8 hours.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from itertools import product
from girard_2x2_v3 import GirardConfig, GirardSimulation


def time_to_95(sim, threshold=0.95, consecutive=10):
    """Check if modal agreement reaches threshold for consecutive steps."""
    modal = sim.history["modal_agreement"]
    n = len(modal)
    for t in range(n - consecutive + 1):
        if all(modal[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def find_boundary(alpha, decay, exp_thresh, gammas, n_seeds, n_steps, n_agents=50):
    """
    For a given parameter combo, sweep gammas and find boundary.
    Returns dict mapping gamma -> convergence_rate.
    """
    results = {}

    for gamma in gammas:
        converged = 0
        for r in range(n_seeds):
            seed = 42 + r * 1000
            cfg = GirardConfig(
                n_agents=n_agents,
                n_neighbors=6,
                rewire_prob=0.15,
                alpha=alpha,
                salience_exponent=gamma,
                aggression_decay=decay,
                expulsion_threshold=None,  # no expulsion for convergence test
                n_steps=n_steps,
                record_history=True,
                seed=seed,
            )
            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()

            t95 = time_to_95(sim)
            if t95 is not None:
                converged += 1

        results[gamma] = converged / n_seeds
    return results


def find_gamma_star(gamma_rates, threshold=0.5):
    """Find lowest gamma where convergence rate >= threshold."""
    for gamma in sorted(gamma_rates.keys()):
        if gamma_rates[gamma] >= threshold:
            return gamma
    return None


def main():
    alphas = [0.05, 0.10, 0.15, 0.20, 0.30]
    decays = [0.01, 0.03, 0.05, 0.10]
    thresholds = [4.0, 8.0, 16.0]  # expulsion thresholds (for later; convergence test is threshold-free)

    # Gamma sweep: fine around the known boundary, coarser elsewhere
    gammas = [0.90, 0.95, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.25, 2.00]

    N_SEEDS = 10
    N_STEPS = 800
    N_AGENTS = 50

    out_lines = []
    def log(s=""):
        print(s, flush=True)
        out_lines.append(s)

    log("=" * 100)
    log("PARAMETER SENSITIVITY: PHASE BOUNDARY ROBUSTNESS")
    log(f"Agents: {N_AGENTS}, Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    log(f"Gammas: {gammas}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 100)

    # Part 1: alpha x decay sweep (convergence test, no expulsion)
    log(f"\n{'=' * 100}")
    log("PART 1: CONVERGENCE BOUNDARY (alpha x decay)")
    log(f"{'=' * 100}")

    boundary_map = {}  # (alpha, decay) -> gamma*
    combo_count = 0
    total_combos = len(alphas) * len(decays)

    log(f"\n{'alpha':<8} {'decay':<8} {'gamma*':>8}  convergence rates by gamma...")
    log("-" * 100)

    for alpha, decay in product(alphas, decays):
        combo_count += 1
        t0 = time.time()

        rates = find_boundary(alpha, decay, None, gammas, N_SEEDS, N_STEPS, N_AGENTS)
        gamma_star = find_gamma_star(rates)
        boundary_map[(alpha, decay)] = gamma_star
        elapsed = time.time() - t0

        rates_str = "  ".join(f"{g}:{rates[g]:.0%}" for g in sorted(rates.keys()))
        gs_str = f"{gamma_star}" if gamma_star is not None else ">2.0"
        log(f"{alpha:<8.2f} {decay:<8.2f} {gs_str:>8}  {rates_str}  ({elapsed:.0f}s) "
            f"[{combo_count}/{total_combos}]")

    # Summary: boundary map
    log(f"\n\n{'=' * 100}")
    log("BOUNDARY MAP: gamma* by (alpha, decay)")
    log(f"{'=' * 100}")
    log(f"\n{'':>8}" + "".join(f"{'d=' + str(d):>10}" for d in decays))
    for alpha in alphas:
        row = f"a={alpha:<5.2f}"
        for decay in decays:
            gs = boundary_map.get((alpha, decay))
            row += f"{str(gs) if gs else '>2.0':>10}"
        log(row)

    # Part 2: expulsion threshold sweep at default alpha/decay
    log(f"\n\n{'=' * 100}")
    log("PART 2: EXPULSION DYNAMICS (threshold sweep)")
    log("alpha=0.15, decay=0.03, with expulsion enabled")
    log(f"{'=' * 100}")

    for exp_thresh in thresholds:
        log(f"\n  --- expulsion_threshold = {exp_thresh} ---")
        log(f"  {'gamma':<8} {'Med Exp':>8} {'Med Alive':>10} {'Med Consumed':>13}")
        log(f"  " + "-" * 45)

        for gamma in [1.05, 1.25, 1.50, 2.00]:
            exp_counts = []
            alive_counts = []

            for r in range(N_SEEDS):
                seed = 42 + r * 1000
                cfg = GirardConfig(
                    n_agents=N_AGENTS,
                    n_neighbors=6,
                    rewire_prob=0.15,
                    alpha=0.15,
                    salience_exponent=gamma,
                    aggression_decay=0.03,
                    expulsion_threshold=exp_thresh,
                    n_steps=1500,
                    record_history=False,
                    seed=seed,
                )
                sim = GirardSimulation(cfg, source="object", spread="attention")
                sim.run()

                n_exp = len(sim.history["expulsion_events"])
                n_alive = sum(1 for v in sim.alive.values() if v)
                exp_counts.append(n_exp)
                alive_counts.append(n_alive)

            med_exp = np.median(exp_counts)
            med_alive = np.median(alive_counts)
            med_consumed = (N_AGENTS - med_alive) / N_AGENTS * 100

            log(f"  {gamma:<8} {med_exp:>8.0f} {med_alive:>10.0f} {med_consumed:>12.1f}%")

        print(f"  threshold={exp_thresh} done", flush=True)

    # Part 3: Check boundary at N=200
    log(f"\n\n{'=' * 100}")
    log("PART 3: BOUNDARY CHECK AT N=200")
    log("Default params (alpha=0.15, decay=0.03), no expulsion")
    log(f"{'=' * 100}")

    k_200 = max(6, min(int(200 * 0.12), 20))
    if k_200 % 2 == 1:
        k_200 -= 1

    log(f"\n  {'gamma':<8} {'Conv Rate':>10}")
    log(f"  " + "-" * 20)

    for gamma in gammas:
        converged = 0
        for r in range(N_SEEDS):
            seed = 42 + r * 1000
            cfg = GirardConfig(
                n_agents=200,
                n_neighbors=k_200,
                rewire_prob=0.15,
                alpha=0.15,
                salience_exponent=gamma,
                expulsion_threshold=None,
                n_steps=N_STEPS,
                record_history=True,
                seed=seed,
            )
            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()
            t95 = time_to_95(sim)
            if t95 is not None:
                converged += 1

        rate = converged / N_SEEDS
        log(f"  {gamma:<8} {rate:>9.0%}")
        print(f"  N=200 gamma={gamma} done: {rate:.0%}", flush=True)

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("exp3_param_sensitivity_results_copy.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    log("Saved to exp3_param_sensitivity_results_copy.txt")


if __name__ == "__main__":
    main()
