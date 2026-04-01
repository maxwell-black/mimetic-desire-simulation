# Mimetic Desire Simulation

Companion code for "A Computational Test of Girard's Scapegoat Mechanism" (Black, 2026).

## Overview

Agent-based model testing Girard's claim that mimetic crisis resolves through unanimous polarization against a single victim via a "snowball effect" in which mimetic attraction "multiplies with the number of those polarized." Four variants in a 2x2 design cross two hostility-transmission modes (linear vs. convex redistributive) with two hostility sources (object-rivalry vs. status-rivalry).

## Core Module

- **`girard_2x2_v3.py`** -- Authoritative simulation module implementing all four variants (LM, AC, RL, RA).

## Reproduction Scripts

Each script reproduces one table or analysis section from the paper. All import from `girard_2x2_v3.py` and should be run from the repo root.

| Script | Reproduces | Runtime |
|--------|-----------|---------|
| `reproduce_tables_1_1b.py` | Tables 1, 1b | ~3 min |
| `reproduce_table_2.py` | Table 2 (gamma sweep) | ~5 min |
| `reproduce_table_2b.py` | Table 2b (phase boundary N-invariance) | ~20-30 min |
| `reproduce_table_3.py` | Table 3 (operator ablation) | ~2 min |
| `reproduce_table_4.py` | Table 4 (threshold regimes) | ~8 min |
| `reproduce_tables_6_7.py` | Tables 6, 7 (unanimity-triggered violence topologies) | ~30-45 min |
| `reproduce_table_8.py` | Table 8 (self-exhaustion) | ~10-20 min |
| `reproduce_table_d1.py` | Table D1 (fixed-scale ablation) | ~5 min |
| `reproduce_table_e1.py` | Table E1 (robustness grid) | ~8 min |
| `reproduce_section_3_7.py` | Section 3.7 statistics | ~4 min |

## Experiment Scripts

These scripts ran the exploratory analyses that informed the paper. Results are saved in `*_results.txt` files.

| Script | Analysis |
|--------|----------|
| `unanimity_trigger_experiment.py` | Initial unanimity-triggered expulsion (N=50) |
| `unanimity_trigger_N_gamma.py` | N x gamma sweep under unanimity trigger |
| `phase_boundary_large_N.py` | Phase boundary invariance across N |
| `self_exhaustion_extended.py` | Extended 5000-step self-exhaustion test |
| `unanimity_trigger_traces_full.py` | Detailed trace generation |
| `exp_small_n_*.py` | Small-N scaling, topology, viability analyses |
| `exp_softmax_*.py` | Softmax operator comparison (Appendix G) |
| `exp_modal_entropy_transient.py` | Entropy trajectory analysis (Appendix H) |

## Figure Generation

| Script | Figure |
|--------|--------|
| `gen_fig_trajectories.py` | Figure 1: LM vs AC convergence trajectories |
| `gen_fig_phase_transition.py` | Figure 2: Phase transition at superlinearity boundary |
| `gen_fig_founding_murder.py` | Figure 3: Founding murder cycle structure |
| `gen_fig_phase_boundary_N.py` | Figure 4: Phase boundary N-invariance |
| `gen_fig_violence_topologies.py` | Figure 5: Violence topology comparison |
| `gen_fig_entropy_transient.py` | Appendix H: Modal-target entropy transient |
| `gen_fig_softmax_heatmap.py` | Appendix G: Softmax convergence rate heatmap |
| `gen_fig_softmax_band_width.py` | Appendix G: Softmax convergence band vs N |

### Requirements

```
numpy
networkx
scipy       # for reproduce_section_3_7.py only
matplotlib  # for figure generation only
```

### Quick Start

```bash
python reproduce_tables_1_1b.py
```

## Directory Structure

```
girard_2x2_v3.py          # core simulation
reproduce_*.py             # reproduction scripts
gen_fig_*.py               # figure generation
unanimity_trigger_*.py     # experiment scripts
phase_boundary_*.py        # experiment scripts
self_exhaustion_*.py       # experiment scripts
exp_*.py                   # additional experiments (softmax, small-N, etc.)
paper/                     # manuscript drafts
figures/                   # generated figures
legacy/                    # old framework (pre-2x2 design)
```

## Key Findings (v18)

- **Phase boundary**: The effective phase boundary lies just above linearity (γ ∈ [1.02, 1.03]), is invariant across community sizes from 5 to 500 agents, and sharpens with increasing N.
- **Operator comparison**: The phase boundary is a generic property of the convex conserving operator class, but power-law's scale invariance is uniquely robust to population scaling. Softmax convergence band narrows monotonically with N and vanishes at N ≥ 150.
- **Violence topologies**: Three distinct regimes emerge above the phase boundary: (1) boundary-grinding (relentless serial purges), (2) supercritical bursts (paired expulsions with peace intervals), and (3) self-exhaustion through topology destruction (small communities only).
- **Viability window**: The founding murder is generative—self-exhausting with majority survival—only within a window at approximately N = 15–50, corresponding to primate and early hominid community sizes. This identifies the boundary above which Girard's "sacred" becomes structurally indispensable.

## Changes in v18

- **Appendix G**: Softmax/Boltzmann operator comparison; confirms phase boundary is generic to convex conserving operators but power-law's scale invariance is uniquely robust (Tables G1, G2, G3)
- **Appendix H**: Modal-target entropy transient analysis showing early entropy dip before convergence (Tables H1, H2)
- **Small-N analyses**: Extended parameter sensitivity, topology robustness, and viability window analysis (Appendices E-F)
- Additional figures for appendix material

## Legacy Code

The `legacy/` directory contains earlier framework iterations (`convergence_variants.py`, `mimetic_sim.py`, etc.) that use different class hierarchies and variant naming. These files are retained for provenance but **do not reproduce the paper's reported numbers**. Use only the `reproduce_*.py` scripts in the repo root for replication.

## License

MIT
