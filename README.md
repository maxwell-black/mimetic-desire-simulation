# Mimetic Desire Simulation

Companion code for "Mimetic Attraction Multiplies: A Computational Test of Girard's Scapegoat Mechanism" (Black, 2026).

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
| `reproduce_table_3.py` | Table 3 (operator ablation) | ~2 min |
| `reproduce_table_4.py` | Table 4 (threshold regimes) | ~8 min |
| `reproduce_table_d1.py` | Table D1 (fixed-scale ablation) | ~5 min |
| `reproduce_table_e1.py` | Table E1 (robustness grid) | ~8 min |
| `reproduce_section_3_7.py` | Section 3.7 statistics | ~4 min |

### Requirements

```
numpy
networkx
scipy  # for reproduce_section_3_7.py only
```

### Quick Start

```bash
python reproduce_tables_1_1b.py
```

## Directory Structure

```
girard_2x2_v3.py          # core simulation
reproduce_*.py             # reproduction scripts
paper/                     # manuscript drafts
figures/                   # generated figures
legacy/                    # old framework (pre-2x2 design)
```

## Legacy Code

The `legacy/` directory contains earlier framework iterations (`convergence_variants.py`, `mimetic_sim.py`, etc.) that use different class hierarchies and variant naming. These files are retained for provenance but **do not reproduce the paper's reported numbers**. Use only the `reproduce_*.py` scripts in the repo root for replication.

## License

MIT
