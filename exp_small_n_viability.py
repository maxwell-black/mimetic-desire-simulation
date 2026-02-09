"""
exp_small_n_viability.py
=========================
Core experiment: where does the founding murder transition from
GENERATIVE (lasting peace, community survives) to DESTRUCTIVE
(serial mass violence, community destroyed)?

Full 2x2 design x population sweep x gamma sweep,
all with adaptive unanimity-triggered expulsion.

Design:
  N:       {5, 10, 15, 20, 25, 30, 35, 40}
  Variant: {LM, AC, RL, RA}
  Gamma:   {1.05, 1.5, 2.0}
  Seeds:   20 per cell
  Steps:   5000
  Trigger: adaptive -- min(0.95, (N_alive-1)/N_alive)

Run:
    python exp_small_n_viability.py 2>&1 | Tee-Object -FilePath exp_small_n_viability_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
"""

import sys, os, time
import numpy as np
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from girard_2x2_v3 import VARIANT_MAP
from small_n_utils import (adaptive_k, adaptive_unanimity_threshold,
                           run_unanimity_triggered)


def main():
    Ns = [5, 10, 15, 20, 25, 30, 35, 40]
    gammas = [1.05, 1.5, 2.0]
    variants = ["LM", "AC", "RL", "RA"]
    N_SEEDS = 20
    N_STEPS = 5000

    total_cells = len(Ns) * len(gammas) * len(variants)
    total_runs = total_cells * N_SEEDS

    print("=" * 120)
    print(f"SMALL-N FOUNDING MURDER VIABILITY: Full 2x2 x N x gamma")
    print(f"  N values:  {Ns}")
    print(f"  Gammas:    {gammas}")
    print(f"  Variants:  {variants}")
    print(f"  Seeds:     {N_SEEDS}, Steps: {N_STEPS}")
    print(f"  Threshold: adaptive min(0.95, (N-1)/N)")
    print(f"  Total:     {total_cells} cells x {N_SEEDS} seeds = {total_runs} runs")
    print(f"  Started:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)

    print("\n  Adaptive threshold by N:")
    for N in Ns:
        print(f"    N={N:>3}: threshold={adaptive_unanimity_threshold(N):.3f}, k={adaptive_k(N)}")

    hdr = (f"{'Var':<4} {'Src':<7} {'Sprd':<10} {'N':>4} {'k':>3} {'gam':>5} "
           f"{'MedExp':>7} {'Consumed':>9} {'Alive':>6} "
           f"{'Exh':>5} {'Cyc':>5} {'Cen':>5} {'NoExp':>6} {'T/O':>4} "
           f"{'1stPeace':>9} {'1stReconv':>10} {'MedGap':>7} "
           f"{'Frags':>6} {'LrgFrag':>8} {'PkModal':>8}")
    print(f"\n{hdr}")
    print("-" * 120)

    all_results = []

    for variant in variants:
        source, spread = VARIANT_MAP[variant]
        for N in Ns:
            for gamma in gammas:
                t0 = time.time()
                cell_results = []

                for r in range(N_SEEDS):
                    seed = 42 + r * 1000
                    res = run_unanimity_triggered(
                        N, gamma, variant, n_steps=N_STEPS, seed=seed)
                    cell_results.append(res)
                    all_results.append(res)

                elapsed = time.time() - t0

                exps = [r["n_expulsions"] for r in cell_results]
                statuses = [r["status"] for r in cell_results]
                n_exh = sum(1 for s in statuses if s == "genuine_exhaustion")
                n_cyc = sum(1 for s in statuses if s == "still_cycling")
                n_cen = sum(1 for s in statuses if s == "censored")
                n_noexp = sum(1 for s in statuses if s == "no_expulsions")
                n_timeout = sum(1 for s in statuses if s == "timeout")

                peace_vals = [r["first_peace"] for r in cell_results if r["first_peace"] is not None]
                reconv_vals = [r["first_reconverge"] for r in cell_results if r["first_reconverge"] is not None]
                gap_vals = [r["med_gap"] for r in cell_results if r["med_gap"] is not None]

                med_exp = np.median(exps)
                med_consumed = np.median([r["pct_consumed"] for r in cell_results]) * 100
                med_alive = np.median([r["n_alive"] for r in cell_results])
                med_peace = np.median(peace_vals) if peace_vals else None
                med_reconv = np.median(reconv_vals) if reconv_vals else None
                med_gap = np.median(gap_vals) if gap_vals else None
                med_frags = np.median([r["n_fragments"] for r in cell_results])
                med_lrg = np.median([r["largest_fragment"] for r in cell_results])
                med_pk = np.median([r["peak_modal"] for r in cell_results])
                k = adaptive_k(N)

                row = (f"{variant:<4} {source:<7} {spread:<10} {N:>4} {k:>3} "
                       f"{gamma:>5.2f} {med_exp:>7.0f} {med_consumed:>8.1f}% "
                       f"{med_alive:>6.0f} "
                       f"{n_exh:>5} {n_cyc:>5} {n_cen:>5} {n_noexp:>6} {n_timeout:>4} "
                       f"{(f'{med_peace:.0f}' if med_peace is not None else '--'):>9} "
                       f"{(f'{med_reconv:.0f}' if med_reconv is not None else '--'):>10} "
                       f"{(f'{med_gap:.0f}' if med_gap is not None else '--'):>7} "
                       f"{med_frags:>6.0f} {med_lrg:>8.0f} {med_pk:>8.3f}"
                       f"  ({elapsed:.0f}s)")
                print(row)

    # ========================================================================
    print("\n\n" + "=" * 120)
    print("DETAILED: ATTENTION VARIANTS AT SMALL N")
    print("=" * 120)

    for variant in ["AC", "RA"]:
        for N in [5, 10, 15, 20, 25, 30]:
            for gamma in gammas:
                cell = [r for r in all_results if r["variant"] == variant and r["N"] == N and r["gamma"] == gamma]
                if not cell: continue
                print(f"\n--- {variant} N={N} gamma={gamma} ---")
                for r in cell[:5]:
                    fp = r['first_peace'] if r['first_peace'] is not None else '--'
                    fr = r['first_reconverge'] if r['first_reconverge'] is not None else '--'
                    print(f"  seed={r['seed']}: {r['n_expulsions']} exp, "
                          f"{r['n_alive']}/{N} alive ({r['pct_consumed']*100:.1f}%), "
                          f"status={r['status']}, 1st_peace={fp}, 1st_reconv={fr}, "
                          f"frags={r['n_fragments']}, largest={r['largest_fragment']}, "
                          f"pk_modal={r['peak_modal']:.3f}")

    # ========================================================================
    print("\n\n" + "=" * 120)
    print("FOUNDING MURDER VIABILITY INDEX")
    print("  Generative = genuine_exhaustion AND pct_consumed < 0.50 AND n_expulsions >= 1")
    print("=" * 120)

    print(f"\n{'Var':<4} {'gam':>5} ", end="")
    for N in Ns: print(f"{'N='+str(N):>8}", end="")
    print()
    print("-" * (12 + 8 * len(Ns)))

    for variant in ["AC", "RA"]:
        for gamma in gammas:
            print(f"{variant:<4} {gamma:>5.2f} ", end="")
            for N in Ns:
                cell = [r for r in all_results if r["variant"] == variant and r["N"] == N and r["gamma"] == gamma]
                gen = sum(1 for r in cell if r["status"] == "genuine_exhaustion" and r["pct_consumed"] < 0.50 and r["n_expulsions"] >= 1)
                pct = gen / len(cell) * 100 if cell else 0
                print(f"{pct:>7.0f}%", end="")
            print()

    # ========================================================================
    print("\n\n" + "=" * 120)
    print("COMMUNITY SURVIVAL: Median % alive at end (AC/RA only)")
    print("=" * 120)
    print(f"\n{'Var':<4} {'gam':>5} ", end="")
    for N in Ns: print(f"{'N='+str(N):>8}", end="")
    print()
    print("-" * (12 + 8 * len(Ns)))
    for variant in ["AC", "RA"]:
        for gamma in gammas:
            print(f"{variant:<4} {gamma:>5.2f} ", end="")
            for N in Ns:
                cell = [r for r in all_results if r["variant"] == variant and r["N"] == N and r["gamma"] == gamma]
                if cell:
                    surv = np.median([r["n_alive"] / r["N"] * 100 for r in cell])
                    print(f"{surv:>7.0f}%", end="")
                else: print(f"{'--':>8}", end="")
            print()

    # ========================================================================
    print("\n\n" + "=" * 120)
    print("LINEAR VARIANTS: Peak modal + expulsions (do they reach unanimity at small N?)")
    print("=" * 120)
    print(f"\n{'Var':<4} {'gam':>5} {'metric':<10}", end="")
    for N in Ns: print(f"{'N='+str(N):>8}", end="")
    print()
    print("-" * (22 + 8 * len(Ns)))
    for variant in ["LM", "RL"]:
        for gamma in gammas:
            print(f"{variant:<4} {gamma:>5.2f} {'pk_modal':<10}", end="")
            for N in Ns:
                cell = [r for r in all_results if r["variant"] == variant and r["N"] == N and r["gamma"] == gamma]
                if cell: print(f"{np.median([r['peak_modal'] for r in cell]):>8.3f}", end="")
                else: print(f"{'--':>8}", end="")
            print()
            print(f"{'':>4} {'':>5} {'med_exp':<10}", end="")
            for N in Ns:
                cell = [r for r in all_results if r["variant"] == variant and r["N"] == N and r["gamma"] == gamma]
                if cell: print(f"{np.median([r['n_expulsions'] for r in cell]):>8.0f}", end="")
                else: print(f"{'--':>8}", end="")
            print()

    print(f"\n\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
