"""
Figure G2: Softmax Convergence Band Width vs. Population Size (Appendix G)
===========================================================================
Scatter plot: x-axis = N, y-axis = band width.
Data from Table G3 in paper_draft_18.md.

Usage:  python gen_fig_softmax_band_width.py
Output: figures/fig_softmax_band_width.pdf/.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']


def main():
    # Data from Table G3 in paper_draft_18.md
    N_vals = [30, 50, 75, 100, 150, 200]
    band_widths = [0.682, 0.460, 0.183, 0.067, 0.0, 0.0]

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
    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Scatter points only, no connecting line
    ax.scatter(N_vals, band_widths, color=PALETTE[0], s=60, zorder=3,
              edgecolors='none')

    # Reference line at width=0
    ax.axhline(0, color='#888888', linestyle='--', linewidth=0.8, alpha=0.5)

    ax.set_xlabel('Population size $N$')
    ax.set_ylabel('Convergence band width ($T$ units)')
    ax.set_title('Softmax Convergence Band Width vs. Population Size', pad=10)
    ax.set_ylim(-0.05, 0.80)
    ax.set_xlim(15, 215)

    plt.tight_layout()
    fig.savefig('figures/fig_softmax_band_width.pdf', bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig_softmax_band_width.png', bbox_inches='tight', dpi=300)
    print("Saved: figures/fig_softmax_band_width.pdf/.png")


if __name__ == "__main__":
    main()
