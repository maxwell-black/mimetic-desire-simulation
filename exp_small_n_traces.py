"""
exp_small_n_traces.py
======================
Save full modal-agreement timeseries at small N for figure generation.

Conditions (all with adaptive unanimity trigger):
  A) N=5,  gamma={1.05, 2.0}   -- minimal group
  B) N=10, gamma={1.05, 2.0}   -- threshold crossover point
  C) N=20, gamma={1.05, 2.0}   -- backward-compatible threshold
  D) N=30, gamma={1.05, 2.0}   -- mid-range
  E) N=50, gamma={1.05, 2.0}   -- continuity with existing traces

Multiple seeds per condition for visual comparison.

Run:
    python exp_small_n_traces.py 2>&1 | Tee-Object -FilePath exp_small_n_traces_results.txt

Requires: girard_2x2_v3.py, small_n_utils.py
Outputs: small_n_traces.npz (for plotting)
"""

import sys, os, time
import numpy as np

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

from small_n_utils import (adaptive_k, adaptive_unanimity_threshold,
                           run_unanimity_triggered)


def main():
    conditions = [
        # (N, gamma, n_steps)
        (5,  1.05, 2000),
        (5,  2.00, 2000),
        (10, 1.05, 3000),
        (10, 2.00, 3000),
        (20, 1.05, 5000),
        (20, 2.00, 5000),
        (30, 1.05, 5000),
        (30, 2.00, 5000),
        (50, 1.05, 5000),
        (50, 2.00, 5000),
    ]
    N_SEEDS = 5
    SEED_BASE = 42
    SEED_STRIDE = 1000

    traces = {}

    print("=" * 100)
    print("SMALL-N FULL TRACES FOR FIGURES")
    print(f"Seeds: {N_SEEDS}")
    print(f"Trigger: adaptive unanimity threshold")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    for N, gamma, n_steps in conditions:
        k = adaptive_k(N)
        thresh = adaptive_unanimity_threshold(N)
        gamma_str = str(gamma).replace('.', '')

        print(f"\n--- N={N}, gamma={gamma}, k={k}, threshold={thresh:.3f}, "
              f"{n_steps} steps ---")

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            t0 = time.time()

            res = run_unanimity_triggered(
                N, gamma, "AC", n_steps=n_steps, seed=seed,
                record_history=True)

            elapsed = time.time() - t0

            label = f"n{N}_g{gamma_str}_s{seed}"
            traces[f"{label}_modal"] = np.array(res["modal_series"], dtype=np.float32)
            traces[f"{label}_exps"] = np.array(res["expulsion_steps"], dtype=np.int32)
            traces[f"{label}_alive"] = np.array(res["alive_counts"], dtype=np.int32)

            print(f"  seed={seed}: {res['n_expulsions']} exp, "
                  f"{res['n_alive']}/{N} alive, "
                  f"status={res['status']}, pk_modal={res['peak_modal']:.3f} "
                  f"({elapsed:.1f}s)")

            # Detailed cycle info for first few expulsions
            if res["expulsion_steps"]:
                exps = res["expulsion_steps"]
                modal = res["modal_series"]
                for i, es in enumerate(exps[:5]):
                    # Peace after expulsion
                    peace = 0
                    for t in range(es + 1, min(es + 200, n_steps)):
                        if modal[t] < 0.5:
                            peace += 1
                        else:
                            break
                    print(f"    Exp {i+1} at t={es}: peace_after={peace} steps")

    # Save traces
    outfile = "small_n_traces.npz"
    np.savez_compressed(outfile, **traces)
    print(f"\nSaved {len(traces)} arrays to {outfile}")
    print("Keys:", sorted(traces.keys()))

    # Summary table
    print(f"\n\n{'=' * 100}")
    print("SUMMARY: FOUNDING MURDER DYNAMICS BY N")
    print(f"{'=' * 100}")
    print(f"\n{'N':<6} {'gamma':>6} {'thresh':>7} {'k':>3} "
          f"{'Med Exp':>8} {'Med Alive':>10} {'Med Status':>15}")
    print("-" * 70)

    for N, gamma, n_steps in conditions:
        gamma_str = str(gamma).replace('.', '')
        exps_all = []
        alive_all = []
        status_all = []

        for r in range(N_SEEDS):
            seed = SEED_BASE + r * SEED_STRIDE
            res = run_unanimity_triggered(
                N, gamma, "AC", n_steps=n_steps, seed=seed)
            exps_all.append(res["n_expulsions"])
            alive_all.append(res["n_alive"])
            status_all.append(res["status"])

        from collections import Counter
        status_counts = Counter(status_all)
        modal_status = status_counts.most_common(1)[0][0]

        print(f"{N:<6} {gamma:>6} {adaptive_unanimity_threshold(N):>7.3f} "
              f"{adaptive_k(N):>3} {np.median(exps_all):>8.0f} "
              f"{np.median(alive_all):>10.0f} {modal_status:>15}")

    print(f"\n\nCompleted: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
