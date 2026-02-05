"""
Mimetic Desire Simulation -- Visualization & Analysis
======================================================
Produces:
  1. Single-run time series (tension, desire, rivalry, concentration)
  2. Alpha sweep: phase transition detection
  3. Comparison: Girardian (low alpha) vs rational-choice baseline (high alpha)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mimetic_sim import SimConfig, MimeticSimulation, run_alpha_sweep


def plot_single_run(history: dict, config: SimConfig, ax_grid=None, title_prefix=""):
    """Plot time series for a single simulation run."""
    steps = range(len(history['system_tension']))

    if ax_grid is None:
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
        axes = [fig.add_subplot(gs[i, j]) for i in range(3) for j in range(2)]
        standalone = True
    else:
        fig, axes = ax_grid
        standalone = False

    # 1. System tension
    ax = axes[0]
    ax.plot(steps, history['system_tension'], color='#8B0000', linewidth=1.2)
    # Mark scapegoat events
    for (s, vid) in history['scapegoat_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.6, linestyle='--', linewidth=0.8)
    # Mark crisis periods
    crisis_starts = []
    crisis_ends = []
    in_c = False
    for t, c in enumerate(history['crisis_active']):
        if c == 1 and not in_c:
            crisis_starts.append(t)
            in_c = True
        elif c == 0 and in_c:
            crisis_ends.append(t)
            in_c = False
    if in_c:
        crisis_ends.append(len(history['crisis_active']) - 1)
    for cs, ce in zip(crisis_starts, crisis_ends):
        ax.axvspan(cs, ce, alpha=0.12, color='red')
    ax.set_ylabel('System Tension')
    ax.set_title(f'{title_prefix}System Tension Over Time')
    ax.set_xlabel('Step')

    # 2. Mean desire intensity
    ax = axes[1]
    ax.plot(steps, history['mean_desire'], color='#2E4057', linewidth=1.2)
    ax.set_ylabel('Mean Desire')
    ax.set_title(f'{title_prefix}Mean Desire Intensity')
    ax.set_xlabel('Step')

    # 3. Max rivalry
    ax = axes[2]
    ax.plot(steps, history['max_rivalry'], color='#6B2D5B', linewidth=1.2)
    for (s, vid) in history['scapegoat_events']:
        ax.axvline(x=s, color='#CC5500', alpha=0.6, linestyle='--', linewidth=0.8)
    ax.set_ylabel('Max Rivalry')
    ax.set_title(f'{title_prefix}Peak Individual Rivalry')
    ax.set_xlabel('Step')

    # 4. Desire concentration (Herfindahl)
    ax = axes[3]
    ax.plot(steps, history['desire_concentration'], color='#1B4332', linewidth=1.2)
    ax.set_ylabel('Herfindahl Index')
    ax.set_title(f'{title_prefix}Desire Concentration')
    ax.set_xlabel('Step')
    ax.axhline(y=1.0/config.n_objects, color='gray', linestyle=':', alpha=0.5,
               label=f'Uniform ({1.0/config.n_objects:.2f})')
    ax.legend(fontsize=8)

    # 5. Active agents
    ax = axes[4]
    ax.plot(steps, history['n_active_agents'], color='#2C3E50', linewidth=1.5)
    ax.set_ylabel('Active Agents')
    ax.set_title(f'{title_prefix}Agents Remaining')
    ax.set_xlabel('Step')
    ax.set_ylim(0, config.n_agents + 2)

    # 6. Crisis indicator
    ax = axes[5]
    ax.fill_between(steps, history['crisis_active'], color='#8B0000', alpha=0.4)
    for (s, vid) in history['scapegoat_events']:
        ax.annotate(f'#{vid}', xy=(s, 0.8), fontsize=7, ha='center', color='#CC5500')
    ax.set_ylabel('Crisis Active')
    ax.set_title(f'{title_prefix}Crisis Periods & Scapegoat Events')
    ax.set_xlabel('Step')
    ax.set_ylim(-0.1, 1.3)

    if standalone:
        fig.suptitle(f'Mimetic Desire Simulation (alpha={config.alpha}, N={config.n_agents})',
                     fontsize=14, fontweight='bold', y=0.98)
        return fig
    return None


def plot_alpha_sweep(sweep_results: dict, base_config: SimConfig):
    """Plot phase transition across alpha values."""
    alphas = sorted(sweep_results.keys())

    # Aggregate across runs
    mean_peak_tension = []
    std_peak_tension = []
    mean_n_crises = []
    mean_n_scapegoats = []
    mean_concentration = []
    mean_agents_remaining = []

    for a in alphas:
        runs = sweep_results[a]
        mean_peak_tension.append(np.mean([r['peak_tension'] for r in runs]))
        std_peak_tension.append(np.std([r['peak_tension'] for r in runs]))
        mean_n_crises.append(np.mean([r['n_crises'] for r in runs]))
        mean_n_scapegoats.append(np.mean([r['n_scapegoats'] for r in runs]))
        mean_concentration.append(np.mean([r['final_concentration'] for r in runs]))
        mean_agents_remaining.append(np.mean([r['agents_remaining'] for r in runs]))

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle('Alpha Sweep: Phase Transition in Mimetic Dynamics',
                 fontsize=14, fontweight='bold')

    # Peak tension
    ax = axes[0, 0]
    ax.errorbar(alphas, mean_peak_tension, yerr=std_peak_tension,
                color='#8B0000', capsize=3, marker='o', markersize=4)
    ax.set_xlabel('alpha (autonomous desire)')
    ax.set_ylabel('Peak System Tension')
    ax.set_title('Peak Tension vs Alpha')

    # Number of crises
    ax = axes[0, 1]
    ax.bar(alphas, mean_n_crises, width=0.03, color='#CC5500', alpha=0.8)
    ax.set_xlabel('alpha')
    ax.set_ylabel('# Crisis Events')
    ax.set_title('Crisis Frequency vs Alpha')

    # Number of scapegoats
    ax = axes[0, 2]
    ax.bar(alphas, mean_n_scapegoats, width=0.03, color='#6B2D5B', alpha=0.8)
    ax.set_xlabel('alpha')
    ax.set_ylabel('# Scapegoat Expulsions')
    ax.set_title('Scapegoating vs Alpha')

    # Final desire concentration
    ax = axes[1, 0]
    ax.plot(alphas, mean_concentration, color='#1B4332', marker='s', markersize=5)
    ax.axhline(y=1.0/base_config.n_objects, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('alpha')
    ax.set_ylabel('Herfindahl Index')
    ax.set_title('Desire Concentration vs Alpha')

    # Agents remaining
    ax = axes[1, 1]
    ax.plot(alphas, mean_agents_remaining, color='#2C3E50', marker='D', markersize=5)
    ax.set_xlabel('alpha')
    ax.set_ylabel('Agents Remaining')
    ax.set_title('Population After Scapegoating')
    ax.set_ylim(0, base_config.n_agents + 2)

    # Mean tension (time-averaged)
    mean_avg_tension = [np.mean([r['mean_tension'] for r in sweep_results[a]]) for a in alphas]
    ax = axes[1, 2]
    ax.plot(alphas, mean_avg_tension, color='#8B0000', marker='^', markersize=5)
    ax.set_xlabel('alpha')
    ax.set_ylabel('Time-Averaged Tension')
    ax.set_title('Mean Tension vs Alpha')

    plt.tight_layout()
    return fig


def plot_comparison(history_low: dict, cfg_low: SimConfig,
                    history_high: dict, cfg_high: SimConfig):
    """Side-by-side: Girardian (low alpha) vs rational baseline (high alpha)."""
    fig = plt.figure(figsize=(16, 14))
    fig.suptitle('Girardian Dynamics (alpha=0.1) vs Rational Baseline (alpha=0.85)',
                 fontsize=14, fontweight='bold', y=0.99)

    gs = GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.35)

    # Left column: low alpha
    axes_low = [fig.add_subplot(gs[i, j]) for i in range(3) for j in range(2)]
    plot_single_run(history_low, cfg_low, ax_grid=(fig, axes_low), title_prefix="Girardian: ")

    # Right column: high alpha
    axes_high = [fig.add_subplot(gs[i, j]) for i in range(3) for j in range(2, 4)]
    plot_single_run(history_high, cfg_high, ax_grid=(fig, axes_high), title_prefix="Rational: ")

    return fig


def main():
    print("=" * 60)
    print("MIMETIC DESIRE SIMULATION")
    print("=" * 60)

    # -------------------------------------------------------
    # 1. Single run with default (Girardian) parameters
    # -------------------------------------------------------
    print("\n[1/4] Running single Girardian simulation (alpha=0.15)...")
    cfg = SimConfig(alpha=0.15, n_steps=500, seed=42)
    sim = MimeticSimulation(cfg)
    history = sim.run()

    print(f"  Peak system tension: {max(history['system_tension']):.2f}")
    print(f"  Scapegoat events: {len(history['scapegoat_events'])}")
    for s, vid in history['scapegoat_events']:
        print(f"    Step {s}: Agent #{vid} expelled")
    print(f"  Agents remaining: {history['n_active_agents'][-1]}/{cfg.n_agents}")
    print(f"  Final desire concentration: {history['desire_concentration'][-1]:.4f}")
    print(f"  Uniform baseline: {1.0/cfg.n_objects:.4f}")

    fig1 = plot_single_run(history, cfg)
    fig1.savefig('/home/claude/girardian_single_run.png', dpi=150, bbox_inches='tight')
    print("  Saved: girardian_single_run.png")

    # -------------------------------------------------------
    # 2. Rational baseline (high alpha)
    # -------------------------------------------------------
    print("\n[2/4] Running rational baseline (alpha=0.85)...")
    cfg_high = SimConfig(alpha=0.85, n_steps=500, seed=42)
    sim_high = MimeticSimulation(cfg_high)
    history_high = sim_high.run()

    print(f"  Peak system tension: {max(history_high['system_tension']):.2f}")
    print(f"  Scapegoat events: {len(history_high['scapegoat_events'])}")
    print(f"  Agents remaining: {history_high['n_active_agents'][-1]}/{cfg_high.n_agents}")
    print(f"  Final desire concentration: {history_high['desire_concentration'][-1]:.4f}")

    # -------------------------------------------------------
    # 3. Side-by-side comparison
    # -------------------------------------------------------
    print("\n[3/4] Generating comparison plot...")
    cfg_low = SimConfig(alpha=0.10, n_steps=500, seed=42)
    sim_low = MimeticSimulation(cfg_low)
    history_low = sim_low.run()

    fig2 = plot_comparison(history_low, cfg_low, history_high, cfg_high)
    fig2.savefig('/home/claude/comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved: comparison.png")

    # -------------------------------------------------------
    # 4. Alpha sweep: find the phase transition
    # -------------------------------------------------------
    print("\n[4/4] Running alpha sweep (0.05 to 0.95, 5 runs each)...")
    alphas = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
              0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
    base = SimConfig(n_steps=500)
    sweep = run_alpha_sweep(alphas, base, n_runs=5)

    for a in alphas:
        runs = sweep[a]
        avg_crises = np.mean([r['n_crises'] for r in runs])
        avg_scapegoats = np.mean([r['n_scapegoats'] for r in runs])
        avg_peak = np.mean([r['peak_tension'] for r in runs])
        print(f"  alpha={a:.2f}: crises={avg_crises:.1f}, "
              f"scapegoats={avg_scapegoats:.1f}, peak_tension={avg_peak:.1f}")

    fig3 = plot_alpha_sweep(sweep, base)
    fig3.savefig('/home/claude/alpha_sweep.png', dpi=150, bbox_inches='tight')
    print("  Saved: alpha_sweep.png")

    print("\n" + "=" * 60)
    print("DONE. Files saved to /home/claude/")
    print("=" * 60)


if __name__ == '__main__':
    main()
