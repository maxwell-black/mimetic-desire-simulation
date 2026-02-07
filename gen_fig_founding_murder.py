"""
Figure 3: The Founding Murder and Its Aftermath
=================================================
Two-panel plot comparing tau=8 (serial purge) vs tau=500 (founding murder).
Modal agreement over time with vertical lines at expulsion events.

Directly illustrates the "missing sacred" argument: the cycle structure
is visible, the transient peace is visible, and the reconvergence is visible.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from girard_2x2_v3 import GirardConfig, GirardSimulation


def compute_modal_agreement(sim):
    alive = sim._alive_ids()
    if len(alive) < 2:
        return 0.0
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
        return 0.0
    counts = Counter(top_targets)
    _, modal_count = counts.most_common(1)[0]
    return modal_count / len(top_targets)


def run_with_threshold(tau, n_steps=800, seed=42):
    """Run AC variant, recording modal agreement and expulsion events."""
    cfg = GirardConfig(
        n_agents=50, n_neighbors=6, rewire_prob=0.15,
        alpha=0.15, salience_exponent=2.0,
        expulsion_threshold=tau,
        n_steps=n_steps, record_history=False, seed=seed,
    )
    sim = GirardSimulation(cfg, source="object", spread="attention")

    modal_series = []
    expulsion_steps = []

    for step in range(n_steps):
        cur_modal = compute_modal_agreement(sim)
        modal_series.append(cur_modal)

        # Count alive before step
        alive_before = len(sim._alive_ids())

        # Full step
        sim._refresh_prestige()
        sim.step_desire()
        sim.step_aggression_source()
        sim._refresh_prestige()
        sim.step_aggression_spread()
        sim.step_decay()

        # Check for expulsion
        _, received = sim._received_aggression_vector()
        alive = sim._alive_ids()
        if len(alive) > 1 and len(received) > 0:
            max_r = float(np.max(received))
            if max_r >= tau:
                expulsion_steps.append(step)
                sim.step_expulsion()

        if hasattr(sim, 'step_status_update'):
            sim.step_status_update()
        sim.step_num += 1

    return modal_series, expulsion_steps


def main():
    # Run both conditions
    print("Running tau=8 (serial purge)...")
    modal_8, exp_8 = run_with_threshold(8.0, n_steps=800, seed=42)
    print(f"  {len(exp_8)} expulsions")

    print("Running tau=500 (founding murder)...")
    modal_500, exp_500 = run_with_threshold(500.0, n_steps=800, seed=42)
    print(f"  {len(exp_500)} expulsions at steps: {exp_500}")

    # ---- Plot ----
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.linewidth': 0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    steps = np.arange(len(modal_8))

    # --- Panel (a): tau = 8 ---
    ax1.plot(steps, modal_8, color='#1a1a2e', linewidth=0.9, zorder=2)
    for es in exp_8[:60]:  # cap display to avoid visual overload
        ax1.axvline(es, color='#e63946', linewidth=0.4, alpha=0.35, zorder=1)
    ax1.axhline(0.95, color='#888888', linestyle=':', linewidth=0.7, alpha=0.4)

    ax1.set_ylabel('Modal-target agreement')
    ax1.set_ylim(-0.02, 1.05)
    ax1.set_title(r'(a) Regime 1: Serial purge ($\tau = 8$)', fontsize=12,
                  pad=8, loc='left')

    # Annotations for panel a
    ax1.text(500, 0.85, f'{len(exp_8)} expulsions in 800 steps',
             fontsize=9.5, color='#e63946', fontstyle='italic')
    ax1.text(500, 0.72, 'No sustained unanimity',
             fontsize=9.5, color='#666666')

    # --- Panel (b): tau = 500 ---
    ax2.plot(steps, modal_500, color='#1a1a2e', linewidth=1.2, zorder=2)
    for i, es in enumerate(exp_500):
        label = 'expulsion' if i == 0 else None
        ax2.axvline(es, color='#e63946', linewidth=1.2, alpha=0.7,
                    linestyle='-', zorder=1, label=label)
    ax2.axhline(0.95, color='#888888', linestyle=':', linewidth=0.7, alpha=0.4)

    ax2.set_xlabel('Timestep')
    ax2.set_ylabel('Modal-target agreement')
    ax2.set_ylim(-0.02, 1.05)
    ax2.set_xlim(-10, 810)
    ax2.set_title(r'(b) Regime 2: Founding murder ($\tau = 500$)',
                  fontsize=12, pad=8, loc='left')

    # Annotate the cycle structure in panel b
    if len(exp_500) >= 1:
        first_exp = exp_500[0]
        # Peace phase
        # Find where modal drops below 0.50 and where it rises back above 0.95
        post = modal_500[first_exp + 1:]
        peace_end = None
        for t, m in enumerate(post):
            if m >= 0.50:
                peace_end = t
                break

        if peace_end is not None and peace_end > 3:
            mid_peace = first_exp + 1 + peace_end // 2
            ax2.annotate('transient\npeace',
                         xy=(mid_peace, modal_500[mid_peace]),
                         xytext=(mid_peace - 20, 0.45),
                         fontsize=9, fontstyle='italic', color='#2a6f4e',
                         arrowprops=dict(arrowstyle='->',
                                         color='#2a6f4e', lw=0.8))

        # Reconvergence
        reconverge = None
        for t, m in enumerate(post):
            if m >= 0.95:
                reconverge = first_exp + 1 + t
                break
        if reconverge is not None:
            ax2.annotate('reconvergence\n(the sacred is absent)',
                         xy=(reconverge, 0.95),
                         xytext=(reconverge + 80, 0.55),
                         fontsize=9, fontstyle='italic', color='#444444',
                         arrowprops=dict(arrowstyle='->',
                                         color='#444444', lw=0.8))

    if exp_500:
        ax2.text(420, 0.42,
                 f'{len(exp_500)} expulsions in 800 steps',
                 fontsize=9.5, color='#e63946', fontstyle='italic',
                 ha='center')

    plt.tight_layout(h_pad=1.5)
    fig.savefig('fig3_founding_murder.pdf',
                bbox_inches='tight', dpi=300)
    fig.savefig('fig3_founding_murder.png',
                bbox_inches='tight', dpi=200)
    print("\nSaved: fig3_founding_murder.pdf/.png")


if __name__ == "__main__":
    main()
