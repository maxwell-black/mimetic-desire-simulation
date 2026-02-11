"""
Generate Figure 5: Violence topologies
========================================
Two representative traces showing qualitatively distinct regimes:
  (a) Boundary grinding: N=200, gamma=1.05 -- relentless 7-step cycles
  (b) Supercritical bursts: N=500, gamma=2.0 -- paired expulsions with long peace

Usage:  python gen_fig_violence_topologies.py
Output: figures/fig5_violence_topologies.pdf/.png
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation

PALETTE = ['#1a1a2e', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a']


def get_modal_target(sim):
    """Return (modal_agreement, modal_target_id)."""
    alive = sim._alive_ids()
    if len(alive) < 2:
        return 0.0, None
    thresh = 1e-8
    top_targets = []
    for i in alive:
        targets = [j for j in alive if j != i]
        if not targets:
            continue
        vec = sim.aggression[i][targets]
        if float(np.sum(vec)) < thresh:
            continue
        top_j = targets[int(np.argmax(vec))]
        top_targets.append(top_j)
    if not top_targets:
        return 0.0, None
    counts = Counter(top_targets)
    modal_target, modal_count = counts.most_common(1)[0]
    return modal_count / len(top_targets), modal_target


def run_unanimity_triggered(n_agents, gamma, n_steps=1500, seed=42,
                             unanimity_threshold=0.95, cooldown=5):
    """Run AC variant with unanimity-triggered expulsion."""
    k = max(6, min(int(n_agents * 0.12), 20))
    if k % 2 == 1:
        k -= 1

    cfg = GirardConfig(
        n_agents=n_agents, n_neighbors=k, rewire_prob=0.15,
        alpha=0.15, salience_exponent=gamma,
        expulsion_threshold=None,
        n_steps=n_steps, record_history=False, seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_series = []
    expulsion_steps = []
    steps_since_expulsion = cooldown + 1

    for step in range(n_steps):
        ma, mt = get_modal_target(sim)
        modal_series.append(ma)

        if (ma >= unanimity_threshold and
            steps_since_expulsion > cooldown and
            mt is not None and
            len(sim._alive_ids()) > 2):

            sim.alive[mt] = False
            sim.aggression[mt, :] = 0.0
            sim.aggression[:, mt] = 0.0
            expulsion_steps.append(step)
            steps_since_expulsion = 0
        else:
            steps_since_expulsion += 1

        sim._refresh_prestige()
        sim.step_desire()
        sim.step_aggression_source()
        sim._refresh_prestige()
        sim.step_aggression_spread()
        sim.step_decay()

        if hasattr(sim, 'step_status_update'):
            sim.step_status_update()
        sim.step_num += 1

    return modal_series, expulsion_steps


def main():
    print("Running N=200, gamma=1.05 (boundary grinding)...")
    modal_grind, exps_grind = run_unanimity_triggered(200, 1.05, n_steps=800, seed=42)

    print("Running N=500, gamma=2.0 (supercritical bursts)...")
    modal_burst, exps_burst = run_unanimity_triggered(500, 2.0, n_steps=1500, seed=42)

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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Panel (a): Boundary grinding
    steps_a = range(len(modal_grind))
    ax1.plot(steps_a, modal_grind, color=PALETTE[2], linewidth=0.8, alpha=0.8)
    for es in exps_grind:
        if es < len(modal_grind):
            ax1.axvline(x=es, color=PALETTE[1], alpha=0.4, linewidth=0.5)
    ax1.axhline(y=0.95, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    ax1.set_ylabel('Modal agreement')
    ax1.set_title(f'(a) Boundary grinding: N=200, $\\gamma$=1.05 '
                  f'({len(exps_grind)} expulsions in 800 steps)', pad=8)
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xlim(0, 800)

    # Panel (b): Supercritical bursts
    steps_b = range(len(modal_burst))
    ax2.plot(steps_b, modal_burst, color=PALETTE[3], linewidth=0.8, alpha=0.8)
    for es in exps_burst:
        if es < len(modal_burst):
            ax2.axvline(x=es, color=PALETTE[1], alpha=0.6, linewidth=1.0)
    ax2.axhline(y=0.95, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    ax2.set_xlabel('Timestep')
    ax2.set_ylabel('Modal agreement')
    ax2.set_title(f'(b) Supercritical bursts: N=500, $\\gamma$=2.0 '
                  f'({len(exps_burst)} expulsions in 1500 steps)', pad=8)
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_xlim(0, 1500)

    plt.tight_layout(h_pad=2)
    fig.savefig('figures/fig5_violence_topologies.pdf', bbox_inches='tight', dpi=300)
    fig.savefig('figures/fig5_violence_topologies.png', bbox_inches='tight', dpi=300)
    print("\nSaved: figures/fig5_violence_topologies.pdf/.png")

    print(f"\nPanel (a): {len(exps_grind)} expulsions, "
          f"{200 - len(exps_grind)} alive")
    print(f"Panel (b): {len(exps_burst)} expulsions, "
          f"{500 - len(exps_burst)} alive")


if __name__ == "__main__":
    main()
