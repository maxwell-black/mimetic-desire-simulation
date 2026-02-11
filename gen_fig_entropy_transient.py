"""
Figure H1: Modal-Target Entropy Decay by Superlinearity (Appendix H)
=====================================================================
Line plot (time series -- lines ARE appropriate): x-axis = time step,
y-axis = mean sliding-window entropy.
One line per gamma value, from Table H2 in paper_draft_18.md.

Usage:  python gen_fig_entropy_transient.py
Output: figures/fig_entropy_transient.pdf/.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']


def main():
    # Data from Table H2 in paper_draft_18.md
    t_steps = [0, 25, 50, 75, 100, 150, 200]

    # gamma -> entropy values at each time step
    data = {
        0.95: [1.212, 0.558, 0.397, 0.419, 0.381, 0.445, 0.418],
        1.00: [1.272, 0.473, 0.354, 0.304, 0.222, 0.241, 0.210],
        1.03: [1.308, 0.366, 0.131, 0.155, 0.036, 0.050, 0.000],
        1.05: [1.323, 0.402, 0.109, 0.000, 0.000, 0.000, 0.000],
        1.10: [1.315, 0.296, 0.042, 0.000, 0.000, 0.000, 0.000],
        1.25: [1.263, 0.112, 0.000, 0.000, 0.000, 0.000, 0.000],
        1.50: [1.090, 0.077, 0.000, 0.000, 0.000, 0.000, 0.000],
        2.00: [0.988, 0.092, 0.000, 0.000, 0.000, 0.000, 0.000],
    }

    # Color scheme: sub-threshold grey, near-boundary steel blue, deep supercritical dark/red
    colors = {
        0.95: '#adb5bd',   # grey (sub-threshold)
        1.00: '#868e96',   # grey (sub-threshold)
        1.03: '#74c0fc',   # light steel blue (near-boundary)
        1.05: PALETTE[2],  # steel blue (near-boundary)
        1.10: '#2b6cb0',   # darker steel blue (near-boundary)
        1.25: PALETTE[0],  # dark navy (supercritical)
        1.50: '#6d1a36',   # dark red (deep supercritical)
        2.00: PALETTE[1],  # red (deep supercritical)
    }

    linestyles = {
        0.95: '--',
        1.00: '--',
        1.03: '-',
        1.05: '-',
        1.10: '-',
        1.25: '-',
        1.50: '-',
        2.00: '-',
    }

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
    fig, ax = plt.subplots(figsize=(8, 5))

    for gamma in data:
        lw = 1.2 if gamma <= 1.00 else 1.8
        ax.plot(t_steps, data[gamma], color=colors[gamma],
                linewidth=lw, linestyle=linestyles[gamma],
                marker='o', markersize=4, markeredgewidth=0,
                label=f'$\\gamma = {gamma}$', zorder=3 if gamma >= 1.03 else 2)

    ax.set_xlabel('Timestep')
    ax.set_ylabel('Mean sliding-window entropy (bits)')
    ax.set_title('Modal-Target Entropy Decay by Superlinearity', pad=10)
    ax.set_ylim(-0.05, 1.5)
    ax.set_xlim(-5, 210)

    ax.legend(loc='upper right', ncol=2, framealpha=0.9)

    plt.tight_layout()
    fig.savefig('figures/fig_entropy_transient.pdf', bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig_entropy_transient.png', bbox_inches='tight', dpi=300)
    print("Saved: figures/fig_entropy_transient.pdf/.png")


if __name__ == "__main__":
    main()
