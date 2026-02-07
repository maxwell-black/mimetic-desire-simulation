"""
Validation: Does Scapegoating Emerge?
======================================
Runs the v2 simulation (no hard-coded scapegoat mechanism) and measures
whether mimetic dynamics naturally produce convergence of aggression
onto single targets.

Key metrics:
  - Aggression Gini: high = concentrated (scapegoating), low = diffuse
  - Max share: what fraction of total aggression hits the top target?
  - Entropy: low = concentrated, high = uniform
  - Number of expulsions: does the threshold get crossed at all?
  - Mimetic vs local aggression ratio: is aggression spreading beyond
    direct rivals?
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from mimetic_sim_v2 import SimConfig, MimeticSimulationV2, run_alpha_sweep


def plot_single_run(history: dict, config: SimConfig, title_suffix=""):
    """Diagnostic plots for a single run."""
    steps = range(len(history['system_tension']))

    fig = plt.figure(figsize=(18, 14))
    fig.suptitle(f'Emergent Scapegoating Simulation (alpha={config.alpha}){title_suffix}',
                 fontsize=14, fontweight='bold', y=0.98)
    gs = GridSpec(3, 3, figure=fig, hspace=0.38, wspace=0.32)

    # 1. System tension (total received aggression)
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(steps, history['system_tension'], color='#8B0000', linewidth=1.0)
    for (s, vid, agg) in history['expulsion_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.7, linestyle='--', linewidth=0.8)
    ax.set_ylabel('Total Aggression')
    ax.set_title('System Tension')
    ax.set_xlabel('Step')

    # 2. Aggression Gini coefficient
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(steps, history['aggression_gini'], color='#4A0E4E', linewidth=1.0)
    for (s, vid, agg) in history['expulsion_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.5, linestyle='--', linewidth=0.8)
    ax.set_ylabel('Gini Coefficient')
    ax.set_title('Aggression Concentration (Gini)')
    ax.set_xlabel('Step')
    ax.set_ylim(-0.05, 1.0)
    ax.axhline(y=0.0, color='gray', linestyle=':', alpha=0.4, label='Perfect equality')
    ax.legend(fontsize=7)

    # 3. Max agent's share of total aggression
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(steps, history['aggression_max_share'], color='#1B4332', linewidth=1.0)
    uniform_share = 1.0 / config.n_agents if config.n_agents > 0 else 0
    ax.axhline(y=uniform_share, color='gray', linestyle=':', alpha=0.5,
               label=f'Uniform ({uniform_share:.3f})')
    for (s, vid, agg) in history['expulsion_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.5, linestyle='--', linewidth=0.8)
    ax.set_ylabel('Max Share')
    ax.set_title('Top Target\'s Share of Aggression')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7)

    # 4. Entropy of aggression distribution
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(steps, history['aggression_entropy'], color='#2E4057', linewidth=1.0)
    max_entropy = np.log2(config.n_agents) if config.n_agents > 1 else 0
    ax.axhline(y=max_entropy, color='gray', linestyle=':', alpha=0.5,
               label=f'Max entropy ({max_entropy:.2f})')
    ax.set_ylabel('Shannon Entropy')
    ax.set_title('Aggression Distribution Entropy')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7)

    # 5. Desire concentration
    ax = fig.add_subplot(gs[1, 1])
    ax.plot(steps, history['desire_concentration'], color='#1B4332', linewidth=1.0)
    ax.axhline(y=1.0/config.n_objects, color='gray', linestyle=':', alpha=0.5)
    ax.set_ylabel('Herfindahl')
    ax.set_title('Desire Concentration')
    ax.set_xlabel('Step')

    # 6. Active agents
    ax = fig.add_subplot(gs[1, 2])
    ax.plot(steps, history['n_active_agents'], color='#2C3E50', linewidth=1.5)
    ax.set_ylabel('Agents')
    ax.set_title('Agents Remaining')
    ax.set_xlabel('Step')
    ax.set_ylim(0, config.n_agents + 2)

    # 7. Rivalry-sourced vs mimetically-spread aggression
    ax = fig.add_subplot(gs[2, 0])
    ax.plot(steps, history['rivalry_generated_aggression'],
            color='#B8860B', linewidth=1.0, label='Rivalry-sourced', alpha=0.8)
    ax.plot(steps, history['mimetic_spread_aggression'],
            color='#8B0000', linewidth=1.0, label='Mimetic spread', alpha=0.8)
    ax.set_ylabel('Aggression')
    ax.set_title('Aggression Sources')
    ax.set_xlabel('Step')
    ax.legend(fontsize=8)

    # 8. Mimetic amplification ratio
    ax = fig.add_subplot(gs[2, 1])
    ratios = []
    for r, m in zip(history['rivalry_generated_aggression'],
                    history['mimetic_spread_aggression']):
        if r > 0:
            ratios.append(m / r)
        else:
            ratios.append(0.0)
    ax.plot(steps, ratios, color='#6B2D5B', linewidth=1.0)
    ax.set_ylabel('Ratio')
    ax.set_title('Mimetic Amplification (spread / sourced)')
    ax.set_xlabel('Step')
    ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5, label='1:1')
    ax.legend(fontsize=7)

    # 9. Top target aggression (absolute)
    ax = fig.add_subplot(gs[2, 2])
    ax.plot(steps, history['top_target_aggression'], color='#8B0000', linewidth=1.0)
    ax.axhline(y=config.expulsion_threshold, color='red', linestyle='--',
               alpha=0.6, label=f'Expulsion threshold ({config.expulsion_threshold})')
    for (s, vid, agg) in history['expulsion_events']:
        ax.plot(s, agg, 'rv', markersize=6)
    ax.set_ylabel('Aggression')
    ax.set_title('Most-Targeted Agent\'s Received Aggression')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7)

    return fig


def plot_alpha_sweep(sweep_results: dict, base: SimConfig):
    """Phase transition plots across alpha."""
    alphas = sorted(sweep_results.keys())

    metrics = {
        'mean_gini': ('Mean Aggression Gini', '#4A0E4E'),
        'peak_gini': ('Peak Aggression Gini', '#6B2D5B'),
        'mean_max_share': ('Mean Top-Target Share', '#1B4332'),
        'n_expulsions': ('Expulsions (emergent scapegoating)', '#CC5500'),
        'mean_entropy': ('Mean Aggression Entropy', '#2E4057'),
        'agents_remaining': ('Agents Remaining', '#2C3E50'),
    }

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    fig.suptitle('Phase Transition: Emergent Scapegoating vs Alpha\n'
                 '(No hard-coded crisis mechanism)',
                 fontsize=14, fontweight='bold')

    for idx, (key, (label, color)) in enumerate(metrics.items()):
        ax = axes[idx // 3, idx % 3]
        means = [np.mean([r[key] for r in sweep_results[a]]) for a in alphas]
        stds = [np.std([r[key] for r in sweep_results[a]]) for a in alphas]

        ax.errorbar(alphas, means, yerr=stds, color=color, capsize=3,
                    marker='o', markersize=5, linewidth=1.5)
        ax.set_xlabel('alpha (autonomous desire fraction)')
        ax.set_ylabel(label)
        ax.set_title(label)

        # Reference lines
        if key == 'mean_gini':
            ax.axhline(y=0.0, color='gray', linestyle=':', alpha=0.4)
        elif key == 'mean_max_share':
            ax.axhline(y=1.0/base.n_agents, color='gray', linestyle=':',
                        alpha=0.4, label='Uniform')
            ax.legend(fontsize=7)
        elif key == 'mean_entropy':
            ax.axhline(y=np.log2(base.n_agents), color='gray', linestyle=':',
                        alpha=0.4, label='Max entropy')
            ax.legend(fontsize=7)
        elif key == 'agents_remaining':
            ax.set_ylim(0, base.n_agents + 2)

    plt.tight_layout()
    return fig


def plot_comparison_low_high(h_low: dict, cfg_low: SimConfig,
                             h_high: dict, cfg_high: SimConfig):
    """Side-by-side: aggression distribution snapshots at select timesteps."""
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    fig.suptitle('Aggression Distribution: Girardian (alpha=0.10) vs Rational (alpha=0.90)',
                 fontsize=13, fontweight='bold')

    # We'll show Gini and max-share over time for both
    steps = range(len(h_low['aggression_gini']))

    ax = axes[0, 0]
    ax.plot(steps, h_low['aggression_gini'], color='#8B0000', linewidth=1.0)
    ax.set_title('Gini (alpha=0.10)')
    ax.set_ylabel('Gini')
    ax.set_ylim(-0.05, 1.0)

    ax = axes[0, 1]
    ax.plot(steps, h_low['aggression_max_share'], color='#1B4332', linewidth=1.0)
    ax.set_title('Top-Target Share (alpha=0.10)')
    ax.set_ylabel('Share')

    ax = axes[0, 2]
    ax.plot(steps, h_low['system_tension'], color='#8B0000', linewidth=1.0)
    for (s, v, a) in h_low['expulsion_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.6, linestyle='--')
    ax.set_title('Tension (alpha=0.10)')

    ax = axes[0, 3]
    ax.plot(steps, h_low['n_active_agents'], color='#2C3E50', linewidth=1.5)
    ax.set_title('Agents (alpha=0.10)')
    ax.set_ylim(0, cfg_low.n_agents + 2)

    steps_h = range(len(h_high['aggression_gini']))

    ax = axes[1, 0]
    ax.plot(steps_h, h_high['aggression_gini'], color='#2E4057', linewidth=1.0)
    ax.set_title('Gini (alpha=0.90)')
    ax.set_ylabel('Gini')
    ax.set_ylim(-0.05, 1.0)

    ax = axes[1, 1]
    ax.plot(steps_h, h_high['aggression_max_share'], color='#1B4332', linewidth=1.0)
    ax.set_title('Top-Target Share (alpha=0.90)')
    ax.set_ylabel('Share')

    ax = axes[1, 2]
    ax.plot(steps_h, h_high['system_tension'], color='#2E4057', linewidth=1.0)
    for (s, v, a) in h_high['expulsion_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.6, linestyle='--')
    ax.set_title('Tension (alpha=0.90)')

    ax = axes[1, 3]
    ax.plot(steps_h, h_high['n_active_agents'], color='#2C3E50', linewidth=1.5)
    ax.set_title('Agents (alpha=0.90)')
    ax.set_ylim(0, cfg_high.n_agents + 2)

    for ax in axes.flat:
        ax.set_xlabel('Step')

    plt.tight_layout()
    return fig


def main():
    print("=" * 65)
    print("EMERGENT SCAPEGOATING VALIDATION")
    print("(No hard-coded crisis mechanism)")
    print("=" * 65)

    # ------------------------------------------------------------------
    # 1. Single Girardian run (low alpha)
    # ------------------------------------------------------------------
    print("\n[1/4] Girardian run (alpha=0.10)...")
    cfg_low = SimConfig(alpha=0.10, n_steps=500, seed=42)
    sim_low = MimeticSimulationV2(cfg_low)
    h_low = sim_low.run()

    print(f"  Expulsion events: {len(h_low['expulsion_events'])}")
    for s, vid, agg in h_low['expulsion_events']:
        print(f"    Step {s}: Agent #{vid} (received aggression: {agg:.2f})")
    print(f"  Mean Gini: {np.mean(h_low['aggression_gini']):.4f}")
    print(f"  Peak Gini: {max(h_low['aggression_gini']):.4f}")
    print(f"  Mean top-target share: {np.mean(h_low['aggression_max_share']):.4f}")
    print(f"  Uniform baseline share: {1.0/cfg_low.n_agents:.4f}")

    fig1 = plot_single_run(h_low, cfg_low)
    fig1.savefig('/home/claude/v2_girardian_run.png', dpi=150, bbox_inches='tight')
    print("  Saved: v2_girardian_run.png")

    # ------------------------------------------------------------------
    # 2. Rational baseline (high alpha)
    # ------------------------------------------------------------------
    print("\n[2/4] Rational baseline (alpha=0.90)...")
    cfg_high = SimConfig(alpha=0.90, n_steps=500, seed=42)
    sim_high = MimeticSimulationV2(cfg_high)
    h_high = sim_high.run()

    print(f"  Expulsion events: {len(h_high['expulsion_events'])}")
    print(f"  Mean Gini: {np.mean(h_high['aggression_gini']):.4f}")
    print(f"  Peak Gini: {max(h_high['aggression_gini']):.4f}")
    print(f"  Mean top-target share: {np.mean(h_high['aggression_max_share']):.4f}")

    fig1b = plot_single_run(h_high, cfg_high)
    fig1b.savefig('/home/claude/v2_rational_run.png', dpi=150, bbox_inches='tight')
    print("  Saved: v2_rational_run.png")

    # ------------------------------------------------------------------
    # 3. Side-by-side comparison
    # ------------------------------------------------------------------
    print("\n[3/4] Comparison plot...")
    fig2 = plot_comparison_low_high(h_low, cfg_low, h_high, cfg_high)
    fig2.savefig('/home/claude/v2_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved: v2_comparison.png")

    # ------------------------------------------------------------------
    # 4. Alpha sweep
    # ------------------------------------------------------------------
    print("\n[4/4] Alpha sweep (0.05 to 0.95)...")
    alphas = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50,
              0.60, 0.70, 0.80, 0.90, 0.95]
    base = SimConfig(n_steps=500)
    sweep = run_alpha_sweep(alphas, base, n_runs=5)

    print(f"\n  {'Alpha':>6} | {'Expulsions':>10} | {'Mean Gini':>10} | "
          f"{'Peak Gini':>10} | {'Max Share':>10} | {'Remaining':>10}")
    print("  " + "-" * 72)
    for a in alphas:
        runs = sweep[a]
        print(f"  {a:6.2f} | "
              f"{np.mean([r['n_expulsions'] for r in runs]):10.1f} | "
              f"{np.mean([r['mean_gini'] for r in runs]):10.4f} | "
              f"{np.mean([r['peak_gini'] for r in runs]):10.4f} | "
              f"{np.mean([r['mean_max_share'] for r in runs]):10.4f} | "
              f"{np.mean([r['agents_remaining'] for r in runs]):10.1f}")

    fig3 = plot_alpha_sweep(sweep, base)
    fig3.savefig('/home/claude/v2_alpha_sweep.png', dpi=150, bbox_inches='tight')
    print("\n  Saved: v2_alpha_sweep.png")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    low_runs = sweep[0.10]
    high_runs = sweep[0.90]
    print(f"\n  At alpha=0.10 (Girardian):")
    print(f"    Mean expulsions:  {np.mean([r['n_expulsions'] for r in low_runs]):.1f}")
    print(f"    Mean Gini:        {np.mean([r['mean_gini'] for r in low_runs]):.4f}")
    print(f"    Mean top share:   {np.mean([r['mean_max_share'] for r in low_runs]):.4f}")
    print(f"\n  At alpha=0.90 (Rational):")
    print(f"    Mean expulsions:  {np.mean([r['n_expulsions'] for r in high_runs]):.1f}")
    print(f"    Mean Gini:        {np.mean([r['mean_gini'] for r in high_runs]):.4f}")
    print(f"    Mean top share:   {np.mean([r['mean_max_share'] for r in high_runs]):.4f}")

    gini_ratio = (np.mean([r['mean_gini'] for r in low_runs]) /
                  max(np.mean([r['mean_gini'] for r in high_runs]), 0.001))
    print(f"\n  Gini concentration ratio (low/high alpha): {gini_ratio:.2f}x")

    if gini_ratio > 1.5:
        print("  >> Mimetic dynamics produce significantly more concentrated aggression.")
        print("  >> Consistent with emergent scapegoating.")
    else:
        print("  >> Aggression concentration does not differ significantly by alpha.")
        print("  >> Scapegoating may not be emergent from mimetic dynamics alone.")

    print("\n" + "=" * 65)


if __name__ == '__main__':
    main()
