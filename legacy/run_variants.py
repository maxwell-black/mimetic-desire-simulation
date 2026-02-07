"""
Run all four convergence variants and compare.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from convergence_variants import (
    VariantConfig, LinearBaseline, ThresholdContagion,
    AttentionSalience, SignsOfVictim, run_variant
)

VARIANTS = [
    ('0: Linear Baseline', LinearBaseline),
    ('1: Threshold Contagion', ThresholdContagion),
    ('2: Attention/Salience', AttentionSalience),
    ('3: Signs of Victim', SignsOfVictim),
]
COLORS = ['#7F8C8D', '#8B0000', '#1B4332', '#4A0E4E']
N_RUNS = 8


def main():
    cfg = VariantConfig(alpha=0.15, n_steps=500)
    all_results = {}

    for name, cls in VARIANTS:
        print(f"\nRunning {name} ({N_RUNS} runs)...")
        results = run_variant(cls, cfg, n_runs=N_RUNS)
        all_results[name] = results

        exp = np.mean([r['n_expulsions'] for r in results])
        gini = np.mean([r['mean_gini'] for r in results])
        pgini = np.mean([r['peak_gini'] for r in results])
        ms = np.mean([r['mean_max_share'] for r in results])
        pms = np.mean([r['peak_max_share'] for r in results])
        cr = np.mean([r['mean_convergence_ratio'] for r in results])
        pcr = np.mean([r['peak_convergence_ratio'] for r in results])
        t3 = np.mean([r['mean_top3_share'] for r in results])
        ent = np.mean([r['mean_entropy'] for r in results])
        rem = np.mean([r['agents_remaining'] for r in results])
        print(f"  Expulsions: {exp:.1f}  |  Mean Gini: {gini:.4f}  |  Peak Gini: {pgini:.4f}")
        print(f"  Mean TopShare: {ms:.4f}  |  Peak TopShare: {pms:.4f}")
        print(f"  Mean Top1/Top2: {cr:.3f}  |  Peak Top1/Top2: {pcr:.3f}")
        print(f"  Mean Top3Share: {t3:.4f}  |  Entropy: {ent:.3f}  |  Remaining: {rem:.1f}")

    # ---- Summary table ----
    print("\n" + "=" * 100)
    print("COMPARATIVE TABLE")
    print("=" * 100)
    metrics = [
        ('n_expulsions', 'Expulsions'),
        ('mean_gini', 'Mean Gini'),
        ('peak_gini', 'Peak Gini'),
        ('mean_max_share', 'Mean Top Share'),
        ('peak_max_share', 'Peak Top Share'),
        ('mean_convergence_ratio', 'Top1/Top2 Ratio'),
        ('peak_convergence_ratio', 'Peak Top1/Top2'),
        ('mean_top3_share', 'Top3 Share'),
        ('mean_entropy', 'Entropy'),
        ('agents_remaining', 'Agents Left'),
    ]

    header = f"{'Metric':<18}"
    for name, _ in VARIANTS:
        header += f" | {name:>22}"
    print(header)
    print("-" * len(header))
    for key, label in metrics:
        row = f"{label:<18}"
        for name, _ in VARIANTS:
            runs = all_results[name]
            m = np.mean([r[key] for r in runs])
            s = np.std([r[key] for r in runs])
            row += f" | {m:>14.3f} ±{s:>5.3f}"
        print(row)

    # ---- Bar charts ----
    names = [n for n, _ in VARIANTS]
    bar_metrics = [
        ('mean_gini', 'Mean Aggression Gini\n(higher = concentrated)'),
        ('peak_gini', 'Peak Aggression Gini'),
        ('mean_max_share', 'Mean Top-Target Share'),
        ('mean_convergence_ratio', 'Convergence Ratio (Top1/Top2)'),
        ('n_expulsions', 'Expulsions'),
        ('mean_entropy', 'Aggression Entropy\n(lower = concentrated)'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Scapegoat Convergence: Which Mechanism Produces Girardian Targeting?',
                 fontsize=14, fontweight='bold')
    for idx, (key, label) in enumerate(bar_metrics):
        ax = axes[idx // 3, idx % 3]
        means = [np.mean([r[key] for r in all_results[n]]) for n in names]
        stds = [np.std([r[key] for r in all_results[n]]) for n in names]
        ax.bar(range(len(names)), means, yerr=stds, capsize=4,
               color=COLORS, alpha=0.85, edgecolor='black', linewidth=0.5)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([n.replace(': ', ':\n') for n in names], fontsize=7.5)
        ax.set_title(label, fontsize=10)
        if 'share' in key:
            ax.axhline(y=1.0/50, color='gray', linestyle=':', alpha=0.5)
    plt.tight_layout()
    fig.savefig('/home/claude/variant_bars.png', dpi=150, bbox_inches='tight')
    print("\nSaved: variant_bars.png")

    # ---- Time series for best run of each variant ----
    fig2, axes2 = plt.subplots(4, 4, figsize=(20, 16))
    fig2.suptitle('Time Series by Variant (single representative run)',
                  fontsize=14, fontweight='bold', y=0.98)
    col_keys = [
        ('aggression_gini', 'Gini'),
        ('aggression_max_share', 'Top-Target Share'),
        ('convergence_ratio', 'Top1/Top2'),
        ('system_tension', 'Total Aggression'),
    ]

    for row, ((name, _), color) in enumerate(zip(VARIANTS, COLORS)):
        h = all_results[name][0]['history']
        steps = range(len(h['aggression_gini']))
        for col, (hkey, clabel) in enumerate(col_keys):
            ax = axes2[row, col]
            ax.plot(steps, h[hkey], color=color, linewidth=0.8)
            for (s, vid, agg) in h['expulsion_events']:
                ax.axvline(x=s, color='#CC5500', alpha=0.4, linestyle='--', linewidth=0.6)
            if row == 0:
                ax.set_title(clabel, fontsize=10)
            if col == 0:
                ax.set_ylabel(name, fontsize=9)
            ax.set_xlabel('Step' if row == 3 else '')
            if hkey == 'aggression_gini':
                ax.set_ylim(-0.05, 1.0)
            if hkey == 'aggression_max_share':
                ax.axhline(y=1.0/50, color='gray', linestyle=':', alpha=0.4)

    plt.tight_layout()
    fig2.savefig('/home/claude/variant_timeseries.png', dpi=150, bbox_inches='tight')
    print("Saved: variant_timeseries.png")

    # ---- Expulsion timeline comparison ----
    fig3, axes3 = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    fig3.suptitle('Expulsion Timelines by Variant', fontsize=14, fontweight='bold')
    for row, ((name, _), color) in enumerate(zip(VARIANTS, COLORS)):
        ax = axes3[row]
        h = all_results[name][0]['history']
        events = h['expulsion_events']
        if events:
            times = [e[0] for e in events]
            ax.eventplot([times], lineoffsets=0.5, linelengths=0.8, colors=[color])
        ax.set_ylabel(name, fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlim(0, cfg.n_steps)
    axes3[-1].set_xlabel('Step')
    plt.tight_layout()
    fig3.savefig('/home/claude/variant_expulsions.png', dpi=150, bbox_inches='tight')
    print("Saved: variant_expulsions.png")

    # ---- Alpha sweep for each variant ----
    print("\nRunning alpha sweeps...")
    alphas = [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 0.95]
    sweep_results = {}

    for name, cls in VARIANTS:
        print(f"  Sweeping {name}...")
        sweep_results[name] = {}
        for alpha in alphas:
            acfg = VariantConfig(alpha=alpha, n_steps=500, seed=cfg.seed)
            runs = run_variant(cls, acfg, n_runs=4)
            sweep_results[name][alpha] = runs

    fig4, axes4 = plt.subplots(2, 2, figsize=(14, 10))
    fig4.suptitle('Alpha Sweep by Variant: Phase Transitions',
                  fontsize=14, fontweight='bold')
    sweep_metrics = [
        ('mean_gini', 'Mean Gini'),
        ('n_expulsions', 'Expulsions'),
        ('mean_max_share', 'Top-Target Share'),
        ('mean_convergence_ratio', 'Top1/Top2 Ratio'),
    ]
    for idx, (key, label) in enumerate(sweep_metrics):
        ax = axes4[idx // 2, idx % 2]
        for (name, _), color in zip(VARIANTS, COLORS):
            means = [np.mean([r[key] for r in sweep_results[name][a]]) for a in alphas]
            ax.plot(alphas, means, color=color, marker='o', markersize=4,
                    linewidth=1.5, label=name)
        ax.set_xlabel('alpha')
        ax.set_ylabel(label)
        ax.set_title(f'{label} vs Alpha')
        ax.legend(fontsize=7)
    plt.tight_layout()
    fig4.savefig('/home/claude/variant_alpha_sweep.png', dpi=150, bbox_inches='tight')
    print("Saved: variant_alpha_sweep.png")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == '__main__':
    main()
