"""
Generate Figure 4: Phase boundary N-invariance
================================================
Panel (a): Convergence rate vs gamma, scatter per N (no connecting lines).
Panel (b): Median t95 vs gamma per N (scatter, no connecting lines).

Uses pre-computed results from phase_boundary_large_N_results.txt if available.

Usage:  python gen_fig_phase_boundary_N.py
Output: figures/fig4_phase_boundary_N.pdf/.png
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from girard_2x2_v3 import GirardConfig, GirardSimulation

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def run_sweep():
    """Run the phase boundary sweep for all N values."""
    gammas = [0.95, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.08, 1.10, 1.25, 2.00]
    Ns = [50, 100, 200]
    N_RUNS = 20
    N_STEPS = 800

    results = {}
    for N in Ns:
        k = max(6, min(int(N * 0.12), 20))
        if k % 2 == 1:
            k -= 1

        results[N] = {'gammas': gammas, 'conv_rate': [], 'med_t95': []}

        for gamma in gammas:
            t95_vals = []
            for r in range(N_RUNS):
                seed = 42 + r * 1000
                cfg = GirardConfig(
                    n_agents=N, n_neighbors=k, rewire_prob=0.15,
                    alpha=0.15, salience_exponent=gamma,
                    expulsion_threshold=None,
                    n_steps=N_STEPS, record_history=True, seed=seed,
                )
                sim = GirardSimulation(cfg, source="object", spread="attention")
                sim.run()
                modal = sim.history["modal_agreement"]
                t95_vals.append(time_to_95(modal))

            converged = [t for t in t95_vals if t is not None]
            conv_rate = len(converged) / N_RUNS
            med_t95 = np.median(converged) if converged else None

            results[N]['conv_rate'].append(conv_rate)
            results[N]['med_t95'].append(med_t95)

            print(f"  N={N}, gamma={gamma}: conv={conv_rate*100:.0f}%")

    return results


def parse_results_file(path):
    """Parse pre-computed results from phase_boundary_large_N_results.txt."""
    results = {}
    current_N = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('--- N='):
                current_N = int(line.split('N=')[1].split(',')[0])
                results[current_N] = {'gammas': [], 'conv_rate': [], 'med_t95': []}
            elif current_N and line and line[0].isdigit():
                parts = line.split()
                gamma = float(parts[0])
                conv_str = parts[1].rstrip('%')
                conv_rate = float(conv_str) / 100.0
                med_t95_str = parts[2]
                med_t95 = float(med_t95_str) if med_t95_str != '--' else None

                results[current_N]['gammas'].append(gamma)
                results[current_N]['conv_rate'].append(conv_rate)
                results[current_N]['med_t95'].append(med_t95)

    return results


def main():
    results_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'phase_boundary_large_N_results.txt'
    )

    if os.path.exists(results_file):
        print("Loading pre-computed results...")
        results = parse_results_file(results_file)
    else:
        print("No pre-computed results found. Running sweep (this will take ~30 min)...")
        results = run_sweep()

    # --- Plot ---
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
    })

    os.makedirs('figures', exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    colors = {50: PALETTE[0], 100: PALETTE[2], 200: PALETTE[3]}
    markers = {50: 'o', 100: 's', 200: '^'}

    # Panel (a): Convergence rate vs gamma -- scatter only, no connecting lines
    for N in sorted(results.keys()):
        d = results[N]
        ax1.scatter(d['gammas'], [r * 100 for r in d['conv_rate']],
                    marker=markers.get(N, 'o'), color=colors.get(N, '#333'),
                    s=45, label=f'N={N}', zorder=3, edgecolors='none')

    ax1.axvspan(1.02, 1.05, alpha=0.12, color=PALETTE[1],
                label=r'$\gamma^* \in [1.02, 1.05]$')
    ax1.set_xlabel(r'Salience exponent $\gamma$')
    ax1.set_ylabel('Convergence rate (%)')
    ax1.set_title('(a) Phase boundary is N-invariant', pad=8)
    ax1.legend(fontsize=9)
    ax1.set_ylim(-5, 105)

    # Panel (b): Median t95 vs gamma -- scatter only, no connecting lines
    for N in sorted(results.keys()):
        d = results[N]
        valid_gammas = [g for g, t in zip(d['gammas'], d['med_t95']) if t is not None]
        valid_t95 = [t for t in d['med_t95'] if t is not None]
        if valid_t95:
            ax2.scatter(valid_gammas, valid_t95,
                        marker=markers.get(N, 'o'), color=colors.get(N, '#333'),
                        s=45, label=f'N={N}', zorder=3, edgecolors='none')

    ax2.set_xlabel(r'Salience exponent $\gamma$')
    ax2.set_ylabel(r'Median $t_{95}$ (steps)')
    ax2.set_title('(b) Convergence speed', pad=8)
    ax2.legend(fontsize=9)

    plt.tight_layout(w_pad=3)
    fig.savefig('figures/fig4_phase_boundary_N.pdf', bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig4_phase_boundary_N.png', bbox_inches='tight', dpi=300)
    print("Saved: figures/fig4_phase_boundary_N.pdf/.png")


if __name__ == "__main__":
    main()
