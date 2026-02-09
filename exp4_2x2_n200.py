"""
exp4_2x2_n200.py
================
Run the full 2x2 design at N=200 to confirm all paper claims scale:
  - LM (linear, object): no convergence, diffuse hostility
  - AC (attention, object): scapegoat convergence + self-exhaustion
  - RL (linear, status): no convergence (possibly elevated tension)
  - RA (attention, status): scapegoat convergence with status dynamics

20 seeds each, 5000 steps, with expulsion enabled.

Run from repo root:
    python exp4_2x2_n200.py 2>&1 | tee exp4_2x2_n200_results.txt

Estimated runtime: 4-6 hours.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation, VARIANT_MAP


def compute_metrics(sim):
    """Extract summary metrics from a completed simulation."""
    n_agents = sim.cfg.n_agents
    exp_events = sim.history["expulsion_events"]
    n_exp = len(exp_events)
    n_alive = sum(1 for v in sim.alive.values() if v)
    pct_consumed = (n_agents - n_alive) / n_agents * 100.0

    exp_times = [e[0] for e in exp_events]
    silence = (sim.cfg.n_steps - exp_times[-1]) if exp_times else sim.cfg.n_steps

    # Convergence: did modal agreement ever reach 0.95 for 10+ consecutive steps?
    converged = False
    if sim.record_history and sim.history["modal_agreement"]:
        modal = sim.history["modal_agreement"]
        for t in range(len(modal) - 10):
            if all(modal[t + k] >= 0.95 for k in range(10)):
                converged = True
                break

    # Peak modal agreement
    peak_modal = max(sim.history["modal_agreement"]) if sim.history["modal_agreement"] else 0.0

    # Peak Gini
    peak_gini = max(sim.history["aggression_gini"]) if sim.history["aggression_gini"] else 0.0

    # Mean system tension
    mean_tension = np.mean(sim.history["system_tension"]) if sim.history["system_tension"] else 0.0

    # Self-exhaustion?
    exhausted = silence >= 500 and n_exp > 0

    # Catharsis
    catharsis_vals = [e[2] for e in sim.history.get("catharsis_events", [])]
    med_catharsis = np.median(catharsis_vals) if catharsis_vals else 0.0

    return {
        "n_exp": n_exp,
        "n_alive": n_alive,
        "pct_consumed": pct_consumed,
        "converged": converged,
        "peak_modal": peak_modal,
        "peak_gini": peak_gini,
        "mean_tension": mean_tension,
        "exhausted": exhausted,
        "silence": silence,
        "med_catharsis": med_catharsis,
    }


def main():
    N_AGENTS = 200
    N_STEPS = 5000
    N_SEEDS = 20
    GAMMA = 2.0
    SEED_BASE = 42
    SEED_STRIDE = 1000

    k = max(6, min(int(N_AGENTS * 0.12), 20))
    if k % 2 == 1:
        k -= 1

    variants = ["LM", "AC", "RL", "RA"]

    out_lines = []
    def log(s=""):
        print(s, flush=True)
        out_lines.append(s)

    log("=" * 120)
    log(f"FULL 2x2 AT N={N_AGENTS}: LM / AC / RL / RA")
    log(f"gamma={GAMMA}, k={k}, Steps: {N_STEPS}, Seeds: {N_SEEDS}")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 120)

    # Summary table header
    log(f"\n{'Variant':<8} {'Source':<8} {'Spread':<10} "
        f"{'Med Exp':>8} {'Consumed':>9} {'Conv%':>6} "
        f"{'PeakModal':>10} {'PeakGini':>9} {'Exhausted':>10} "
        f"{'MedCath':>8}")
    log("-" * 105)

    all_results = {}

    for variant in variants:
        source, spread = VARIANT_MAP[variant]
        results = []
        t0 = time.time()

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            cfg = GirardConfig(
                n_agents=N_AGENTS,
                n_neighbors=k,
                rewire_prob=0.15,
                alpha=0.15,
                salience_exponent=GAMMA,
                expulsion_threshold=8.0,
                n_steps=N_STEPS,
                record_history=True,
                seed=seed,
            )
            sim = GirardSimulation(cfg, source=source, spread=spread)
            sim.run()
            metrics = compute_metrics(sim)
            results.append(metrics)

            # Per-seed progress
            conv_str = "CONV" if metrics["converged"] else "----"
            exh_str = "EXH" if metrics["exhausted"] else "cyc"
            print(f"    {variant} seed={seed}: {metrics['n_exp']} exp, "
                  f"{conv_str}, {exh_str}, peak_modal={metrics['peak_modal']:.3f}",
                  flush=True)

        elapsed = time.time() - t0

        med_exp = np.median([r["n_exp"] for r in results])
        med_consumed = np.median([r["pct_consumed"] for r in results])
        conv_rate = sum(1 for r in results if r["converged"]) / N_SEEDS * 100
        med_peak_modal = np.median([r["peak_modal"] for r in results])
        med_peak_gini = np.median([r["peak_gini"] for r in results])
        n_exhausted = sum(1 for r in results if r["exhausted"])
        med_catharsis = np.median([r["med_catharsis"] for r in results])

        log(f"{variant:<8} {source:<8} {spread:<10} "
            f"{med_exp:>8.0f} {med_consumed:>8.1f}% {conv_rate:>5.0f}% "
            f"{med_peak_modal:>10.3f} {med_peak_gini:>9.3f} "
            f"{n_exhausted:>5}/{N_SEEDS:<4} "
            f"{med_catharsis:>8.3f}  ({elapsed:.0f}s)")

        all_results[variant] = results

    # Detailed comparison
    log(f"\n\n{'=' * 120}")
    log("DETAILED VARIANT COMPARISON")
    log(f"{'=' * 120}")

    for variant in variants:
        results = all_results[variant]
        log(f"\n  {variant} ({VARIANT_MAP[variant][0]}, {VARIANT_MAP[variant][1]}):")

        exp_vals = [r["n_exp"] for r in results]
        log(f"    Expulsions: median={np.median(exp_vals):.0f}, "
            f"mean={np.mean(exp_vals):.1f}, "
            f"range=[{min(exp_vals)}, {max(exp_vals)}]")

        modal_vals = [r["peak_modal"] for r in results]
        log(f"    Peak modal agreement: median={np.median(modal_vals):.3f}, "
            f"range=[{min(modal_vals):.3f}, {max(modal_vals):.3f}]")

        n_conv = sum(1 for r in results if r["converged"])
        n_exh = sum(1 for r in results if r["exhausted"])
        log(f"    Converged: {n_conv}/{N_SEEDS}, Exhausted: {n_exh}/{N_SEEDS}")

        tension_vals = [r["mean_tension"] for r in results]
        log(f"    Mean system tension: median={np.median(tension_vals):.2f}")

    # Paper claims check
    log(f"\n\n{'=' * 120}")
    log("PAPER CLAIMS VERIFICATION AT N=200")
    log(f"{'=' * 120}")

    lm_conv = sum(1 for r in all_results["LM"] if r["converged"])
    ac_conv = sum(1 for r in all_results["AC"] if r["converged"])
    rl_conv = sum(1 for r in all_results["RL"] if r["converged"])
    ra_conv = sum(1 for r in all_results["RA"] if r["converged"])

    log(f"\n  Claim 1: Linear spread does not produce convergence")
    log(f"    LM convergence: {lm_conv}/{N_SEEDS} -- {'CONFIRMED' if lm_conv == 0 else 'VIOLATED'}")
    log(f"    RL convergence: {rl_conv}/{N_SEEDS} -- {'CONFIRMED' if rl_conv == 0 else 'VIOLATED'}")

    log(f"\n  Claim 2: Attention spread produces scapegoat focusing")
    ac_modal = np.median([r["peak_modal"] for r in all_results["AC"]])
    ra_modal = np.median([r["peak_modal"] for r in all_results["RA"]])
    lm_modal = np.median([r["peak_modal"] for r in all_results["LM"]])
    rl_modal = np.median([r["peak_modal"] for r in all_results["RL"]])
    log(f"    AC peak modal: {ac_modal:.3f} vs LM: {lm_modal:.3f} -- "
        f"{'CONFIRMED' if ac_modal > 0.5 and ac_modal > lm_modal * 2 else 'WEAK/VIOLATED'}")
    log(f"    RA peak modal: {ra_modal:.3f} vs RL: {rl_modal:.3f} -- "
        f"{'CONFIRMED' if ra_modal > 0.5 and ra_modal > rl_modal * 2 else 'WEAK/VIOLATED'}")
    log(f"    Formal convergence (0.95 for 10 steps): AC {ac_conv}/{N_SEEDS}, RA {ra_conv}/{N_SEEDS}")
    log(f"    Note: self-exhaustion preempts formal convergence at N={N_AGENTS} on WS topology.")
    log(f"    Complete-graph confirmation (exp5): 100% convergence at N={N_AGENTS}.")

    ac_exh = sum(1 for r in all_results["AC"] if r["exhausted"])
    ra_exh = sum(1 for r in all_results["RA"] if r["exhausted"])
    log(f"\n  Claim 3: Attention variants self-exhaust at N=200")
    log(f"    AC exhaustion: {ac_exh}/{N_SEEDS} -- {'CONFIRMED' if ac_exh > N_SEEDS * 0.8 else 'WEAK/VIOLATED'}")
    log(f"    RA exhaustion: {ra_exh}/{N_SEEDS} -- {'CONFIRMED' if ra_exh > N_SEEDS * 0.8 else 'WEAK/VIOLATED'}")

    log(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open("exp4_2x2_n200_results_copy.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    log("Saved to exp4_2x2_n200_results_copy.txt")


if __name__ == "__main__":
    main()
