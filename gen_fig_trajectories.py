"""
Figure 2: Convergence Trajectories -- Linear vs Attentional Concentration
==========================================================================
Modal-target agreement over time for one representative run each of
LM (linear mimesis) and AC (attentional concentration), no expulsion.

Shows what "mimetic attraction multiplies" looks like as a dynamical
process: LM stays flat, AC snowballs to unanimity.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from girard_2x2_v3 import GirardConfig, GirardSimulation


def main():
    cfg = GirardConfig(
        n_agents=50, n_neighbors=6, rewire_prob=0.15,
        alpha=0.15, salience_exponent=2.0,
        expulsion_threshold=None,  # no expulsion
        n_steps=300,  # 300 is enough to show the full trajectory
        record_history=True, seed=42,
    )

    # Run LM
    sim_lm = GirardSimulation(cfg, source="object", spread="linear")
    sim_lm.run()
    modal_lm = sim_lm.history["modal_agreement"]

    # Run AC
    sim_ac = GirardSimulation(cfg, source="object", spread="attention")
    sim_ac.run()
    modal_ac = sim_ac.history["modal_agreement"]

    # Also run one RA for reference
    sim_ra = GirardSimulation(cfg, source="status", spread="attention")
    sim_ra.run()
    modal_ra = sim_ra.history["modal_agreement"]

    # Find convergence step for AC
    t95_ac = None
    for t in range(len(modal_ac) - 10):
        if all(modal_ac[t + k] >= 0.95 for k in range(10)):
            t95_ac = t
            break

    # ---- Plot ----
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.linewidth': 0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
    })

    fig, ax = plt.subplots(figsize=(8, 4.2))

    steps = np.arange(len(modal_lm))

    ax.plot(steps, modal_lm, color='#adb5bd', linewidth=1.8,
            label='LM (linear mimesis)', zorder=2)
    ax.plot(steps, modal_ac, color='#1a1a2e', linewidth=2.0,
            label='AC (attentional concentration)', zorder=3)
    ax.plot(steps, modal_ra, color='#e63946', linewidth=1.4,
            label='RA (rivalry + attention)', alpha=0.7,
            linestyle='--', zorder=2)

    # Convergence threshold
    ax.axhline(0.95, color='#888888', linestyle=':', linewidth=0.8,
               alpha=0.5, zorder=1)
    ax.text(302, 0.955, r'$m = 0.95$', fontsize=9, color='#888888',
            va='bottom')

    # Mark t_95
    if t95_ac is not None:
        ax.axvline(t95_ac, color='#1a1a2e', linestyle='--',
                   linewidth=0.7, alpha=0.4)
        ax.annotate(f'$t_{{95}} = {t95_ac}$',
                    xy=(t95_ac, 0.95), xytext=(t95_ac + 25, 0.78),
                    fontsize=9, color='#1a1a2e',
                    arrowprops=dict(arrowstyle='->', color='#1a1a2e',
                                    lw=0.8))

    # Ceiling annotation
    ax.text(250, 0.99, r'ceiling $(N{-}1)/N = 0.98$', fontsize=8.5,
            color='#666666', ha='center', va='bottom')

    # "Snowball" annotation near the inflection
    ac_arr = np.array(modal_ac)
    # Find steepest ascent region
    diffs = np.diff(ac_arr)
    steep_start = np.argmax(diffs > 0.02)
    if steep_start > 5:
        ax.annotate('mimetic snowball',
                    xy=(steep_start + 3, modal_ac[steep_start + 3]),
                    xytext=(steep_start + 40, 0.35),
                    fontsize=9, fontstyle='italic', color='#1a1a2e',
                    arrowprops=dict(arrowstyle='->', color='#1a1a2e',
                                    lw=0.8, connectionstyle='arc3,rad=0.2'))

    ax.set_xlabel('Timestep')
    ax.set_ylabel('Modal-target agreement')
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlim(-5, 310)
    ax.legend(loc='center right', framealpha=0.9, fontsize=10)

    plt.tight_layout()
    fig.savefig('fig2_trajectories.pdf',
                bbox_inches='tight', dpi=300)
    fig.savefig('fig2_trajectories.png',
                bbox_inches='tight', dpi=200)
    print("Saved: fig2_trajectories.pdf/.png")

    print(f"\nLM final modal: {modal_lm[-1]:.3f}")
    print(f"AC final modal: {modal_ac[-1]:.3f}")
    print(f"RA final modal: {modal_ra[-1]:.3f}")
    print(f"AC t_95: {t95_ac}")


if __name__ == "__main__":
    main()
