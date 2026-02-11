"""
Figure 1: Convergence Trajectories -- Linear vs Attentional Concentration
==========================================================================
Modal-target agreement over time for one representative run each of
LM (linear mimesis) and AC (attentional concentration), no expulsion.

Lines connecting timesteps ARE appropriate here (time series).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from girard_2x2_v3 import GirardConfig, GirardSimulation

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']

plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
})


def main():
    cfg = GirardConfig(
        n_agents=50, n_neighbors=6, rewire_prob=0.15,
        alpha=0.15, salience_exponent=2.0,
        expulsion_threshold=None,  # no expulsion
        n_steps=300,
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
    fig, ax = plt.subplots(figsize=(8, 4.2))

    steps = np.arange(len(modal_lm))

    ax.plot(steps, modal_lm, color='#adb5bd', linewidth=1.8,
            label='LM (linear mimesis)', zorder=2)
    ax.plot(steps, modal_ac, color=PALETTE[0], linewidth=2.0,
            label='AC (attentional concentration)', zorder=3)
    ax.plot(steps, modal_ra, color=PALETTE[1], linewidth=1.4,
            label='RA (rivalry + attention)', alpha=0.7,
            linestyle='--', zorder=2)

    # Convergence threshold
    ax.axhline(0.95, color='#888888', linestyle=':', linewidth=0.8,
               alpha=0.5, zorder=1)
    ax.text(302, 0.955, r'$m = 0.95$', fontsize=9, color='#888888',
            va='bottom')

    # Mark t_95 with a vertical dashed line (no arrow annotation)
    if t95_ac is not None:
        ax.axvline(t95_ac, color=PALETTE[0], linestyle='--',
                   linewidth=0.7, alpha=0.4)
        ax.text(t95_ac + 3, 0.75, f'$t_{{95}} = {t95_ac}$',
                fontsize=9, color=PALETTE[0])

    # Ceiling annotation
    ax.text(250, 0.99, r'ceiling $(N{-}1)/N = 0.98$', fontsize=8.5,
            color='#666666', ha='center', va='bottom')

    ax.set_xlabel('Timestep')
    ax.set_ylabel('Modal-target agreement')
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlim(-5, 310)
    ax.legend(loc='center right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    fig.savefig('figures/fig1_trajectories.pdf',
                bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig1_trajectories.png',
                bbox_inches='tight', dpi=300)
    print("Saved: figures/fig1_trajectories.pdf/.png")

    print(f"\nLM final modal: {modal_lm[-1]:.3f}")
    print(f"AC final modal: {modal_ac[-1]:.3f}")
    print(f"RA final modal: {modal_ra[-1]:.3f}")
    print(f"AC t_95: {t95_ac}")


if __name__ == "__main__":
    main()
