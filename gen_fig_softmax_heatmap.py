"""
Figure G1: Softmax Convergence Rate Heatmap (Appendix G)
=========================================================
Heatmap: x-axis = T (temperature), y-axis = N, cell color = convergence rate (%).
Data from Table G2 in paper_draft_18.md.

Usage:  python gen_fig_softmax_heatmap.py
Output: figures/fig_softmax_heatmap.pdf/.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']


def main():
    # Data from Table G2 in paper_draft_18.md
    N_vals = [10, 20, 30, 50, 75, 100, 150, 200]
    T_vals = [0.05, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.65, 0.70, 0.80]

    # Convergence rates (%) -- rows = N, cols = T
    data = np.array([
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0],  # N=10
        [ 70,  60,  60,  80, 100, 100, 100, 100, 100,  50],  # N=20
        [ 50,  80,  70, 100, 100, 100, 100,  90,  80,  10],  # N=30
        [ 10,  20,  50, 100, 100,  80, 100,  60,  10,   0],  # N=50
        [  0,  30,  30,  20,  70,  80,  30,  10,   0,   0],  # N=75
        [  0,   0,  10,  40,  30,  60,  10,   0,   0,   0],  # N=100
        [  0,   0,   0,   0,  20,   0,   0,   0,   0,   0],  # N=150
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0],  # N=200
    ], dtype=float)

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
    fig, ax = plt.subplots(figsize=(10, 5.5))

    im = ax.imshow(data, cmap='Blues', aspect='auto', vmin=0, vmax=100,
                   interpolation='nearest')

    # Axis labels
    ax.set_xticks(range(len(T_vals)))
    ax.set_xticklabels([f'{t:.2f}' for t in T_vals])
    ax.set_yticks(range(len(N_vals)))
    ax.set_yticklabels([str(n) for n in N_vals])

    ax.set_xlabel('Temperature $T$')
    ax.set_ylabel('Population size $N$')
    ax.set_title('Softmax Convergence Rate by Population Size and Temperature',
                 pad=10)

    # Annotate each cell with the convergence percentage
    for i in range(len(N_vals)):
        for j in range(len(T_vals)):
            val = int(data[i, j])
            text_color = 'white' if val >= 60 else '#333333'
            ax.text(j, i, f'{val}%', ha='center', va='center',
                    fontsize=8.5, color=text_color, fontweight='bold')

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('Convergence rate (%)', fontsize=10)

    plt.tight_layout()
    fig.savefig('figures/fig_softmax_heatmap.pdf', bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig_softmax_heatmap.png', bbox_inches='tight', dpi=300)
    print("Saved: figures/fig_softmax_heatmap.pdf/.png")


if __name__ == "__main__":
    main()
