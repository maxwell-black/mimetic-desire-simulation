# Mimetic Desire Simulation

Companion code for "A Computational Test of Girard's Scapegoat Mechanism" (Black, 2026).

## Overview

Agent-based model testing Girard's claim that mimetic crisis resolves through unanimous polarization against a single victim. Four variants in a 2x2 design cross two hostility-transmission modes (linear vs. convex redistributive) with two hostility sources (object-rivalry vs. status-rivalry).

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

These scripts ran the exploratory analyses that informed the v15 paper additions. Results are saved in `*_results.txt` files.

| Script | Analysis |
|--------|----------|
| `unanimity_trigger_experiment.py` | Initial unanimity-triggered expulsion (N=50) |
| `unanimity_trigger_N_gamma.py` | N x gamma sweep under unanimity trigger |
| `phase_boundary_large_N.py` | Phase boundary invariance across N |
| `self_exhaustion_extended.py` | Extended 5000-step self-exhaustion test |
| `unanimity_trigger_traces_full.py` | Detailed trace generation |

## Figure Generation

| Script | Figure |
|--------|--------|
| `gen_fig_trajectories.py` | Figure 1: LM vs AC convergence trajectories |
| `gen_fig_phase_transition.py` | Figure 2: Phase transition at superlinearity boundary |
| `gen_fig_founding_murder.py` | Figure 3: Founding murder cycle structure |
| `gen_fig_phase_boundary_N.py` | Figure 4: Phase boundary N-invariance |
| `gen_fig_violence_topologies.py` | Figure 5: Violence topology comparison |

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
paper/                     # manuscript drafts
figures/                   # generated figures
legacy/                    # old framework (pre-2x2 design)
```

## Changes in v15

- Added unanimity-triggered expulsion analysis (Sections 3.8-3.9)
- Phase boundary N-invariance (Table 2b)
- Violence topology classification: boundary grinding vs supercritical bursts (Tables 6, 7)
- Self-exhaustion at high gamma (Table 8)
- Figures 4-5

## Legacy Code

The `legacy/` directory contains earlier framework iterations (`convergence_variants.py`, `mimetic_sim.py`, etc.) that use different class hierarchies and variant naming. These files are retained for provenance but **do not reproduce the paper's reported numbers**. Use only the `reproduce_*.py` scripts in the repo root for replication.

## License

MIT
