"""
Figure 1: Phase Transition at the Superlinearity Boundary
==========================================================
Two-panel plot:
  Left:  Convergence rate (%) vs gamma
  Right: Median t_95 vs gamma (converging runs only)

Uses girard_2x2_v3.py for verified data.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from girard_2x2_v3 import GirardConfig, GirardSimulation


def time_to_95(modal_series, threshold=0.95, consecutive=10):
    n = len(modal_series)
    for t in range(n - consecutive + 1):
        if all(modal_series[t + k] >= threshold for k in range(consecutive)):
            return t
    return None


def main():
    gammas = [0.75, 0.90, 0.95, 1.00, 1.01, 1.02, 1.05, 1.08,
              1.10, 1.15, 1.25, 1.50, 2.00]
    N_RUNS = 8
    N_STEPS = 600

    conv_rates = []
    med_t95s = []
    t95_lows = []
    t95_highs = []

    for gamma in gammas:
        t95_values = []
        for r in range(N_RUNS):
            seed = 42 + r * 1000
            cfg = GirardConfig(
                n_agents=50, n_neighbors=6, rewire_prob=0.15,
                alpha=0.15, salience_exponent=gamma,
                expulsion_threshold=None, n_steps=N_STEPS,
                record_history=True, seed=seed,
            )
            sim = GirardSimulation(cfg, source="object", spread="attention")
            sim.run()
            modal = sim.history["modal_agreement"]
            t95_values.append(time_to_95(modal))

        converged = [t for t in t95_values if t is not None]
        conv_rates.append(len(converged) / N_RUNS * 100)

        if converged:
            med_t95s.append(float(np.median(converged)))
            t95_lows.append(float(np.min(converged)))
            t95_highs.append(float(np.max(converged)))
        else:
            med_t95s.append(None)
            t95_lows.append(None)
            t95_highs.append(None)

        print(f"  gamma={gamma:.2f}: conv={conv_rates[-1]:.0f}%, "
              f"med_t95={med_t95s[-1]}")

    # ---- Plot ----
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.linewidth': 0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))

    # Left panel: Convergence rate
    ax1.plot(gammas, conv_rates, 'o-', color='#1a1a2e', markersize=6,
             linewidth=1.5, markerfacecolor='#1a1a2e', markeredgewidth=0)
    ax1.axvspan(1.02, 1.05, alpha=0.12, color='#e63946', zorder=0)
    ax1.axvline(1.0, color='#888888', linestyle=':', linewidth=0.8, alpha=0.6)

    ax1.set_xlabel(r'Salience exponent $\gamma$')
    ax1.set_ylabel('Convergence rate (%)')
    ax1.set_ylim(-5, 108)
    ax1.set_xlim(0.65, 2.1)
    ax1.text(1.035, 55, r'$\gamma^*$', fontsize=13, ha='center',
             color='#e63946', fontstyle='italic')
    ax1.text(0.78, 92, 'No convergence', fontsize=9, color='#666666')
    ax1.text(1.35, 92, 'Universal\nconvergence', fontsize=9,
             color='#666666', ha='center')
    ax1.set_title('(a) Phase boundary', fontsize=12, pad=8)

    # Right panel: Median t_95 (only converging gammas)
    conv_gammas = [g for g, t in zip(gammas, med_t95s) if t is not None]
    conv_t95 = [t for t in med_t95s if t is not None]
    conv_lo = [lo for lo in t95_lows if lo is not None]
    conv_hi = [hi for hi in t95_highs if hi is not None]

    yerr_lo = [m - lo for m, lo in zip(conv_t95, conv_lo)]
    yerr_hi = [hi - m for m, hi in zip(conv_t95, conv_hi)]

    ax2.errorbar(conv_gammas, conv_t95, yerr=[yerr_lo, yerr_hi],
                 fmt='s-', color='#1a1a2e', markersize=5, linewidth=1.5,
                 markerfacecolor='#1a1a2e', markeredgewidth=0,
                 capsize=3, capthick=0.8, elinewidth=0.8, ecolor='#666666')
    ax2.axvline(1.0, color='#888888', linestyle=':', linewidth=0.8, alpha=0.6)

    ax2.set_xlabel(r'Salience exponent $\gamma$')
    ax2.set_ylabel(r'Median $t_{95}$ (steps to convergence)')
    ax2.set_xlim(0.95, 2.1)
    ax2.set_title('(b) Critical slowing down', fontsize=12, pad=8)

    # Annotate the critical slowing
    ax2.annotate(r'$t_{95} = 421$' + '\n(1 of 8 runs)',
                 xy=(1.02, 421), xytext=(1.22, 380),
                 fontsize=8.5, ha='left',
                 arrowprops=dict(arrowstyle='->', color='#444444',
                                 lw=0.8),
                 color='#444444')

    plt.tight_layout(w_pad=3)
    fig.savefig('fig1_phase_transition.pdf',
                bbox_inches='tight', dpi=300)
    fig.savefig('fig1_phase_transition.png',
                bbox_inches='tight', dpi=200)
    print("\nSaved: fig1_phase_transition.pdf/.png")


if __name__ == "__main__":
    main()
