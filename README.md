# Mimetic Desire Simulation

Agent-based model formalizing Girard's mimetic theory. Tests whether scapegoat convergence emerges from mimetic dynamics without hard-coded crisis mechanisms.

## Core Claims Under Test

- **Triangular desire**: agents desire what their models desire
- **Internal mediation**: rivalry intensifies with social proximity
- **Doubling**: mutual modeling creates positive feedback
- **Mimetic crisis**: system-level tension spike from escalating rivalries
- **Scapegoat resolution**: crisis resolves via mimetic convergence of accusation onto a single target

## Architecture

Agents live on a Watts-Strogatz small-world graph. Each agent maintains a desire vector over objects (some rivalrous) and an aggression vector over other agents. Prestige-weighted mimetic updating drives desire convergence; shared desire for rivalrous objects generates rivalry; rivalry sources aggression; aggression spreads mimetically through the network.

## Files

| File | Description |
|------|-------------|
| `mimetic_sim.py` | V1 simulation: hard-coded crisis/scapegoat mechanism |
| `mimetic_sim_v2.py` | V2 simulation: no hard-coded scapegoating; tests emergent convergence |
| `convergence_variants.py` | Four variant mechanisms for aggression spread (linear baseline, threshold contagion, attention/salience, signs-of-victim) |
| `gamma_sweep_lean.py` | Fine-grained sweep of the salience exponent around the phase transition |
| `run_simulation.py` | Runner + plots for v1 |
| `run_v2_validation.py` | Runner + plots for v2 validation |
| `run_variants.py` | Runner + comparative plots across all four convergence variants |

## Key Parameters

- **alpha**: autonomous desire retention (low = strong Girardian claim, high = rational-choice baseline)
- **salience_exponent** (gamma): sharpness of attentional concentration in the attention/salience variant. Phase transition near gamma ~1.0
- **expulsion_threshold**: received-aggression level triggering agent expulsion

## Running

```bash
# Single v1 run + alpha sweep
python run_simulation.py

# V2 emergent scapegoating validation
python run_v2_validation.py

# Convergence variant comparison
python run_variants.py

# Fine-grained gamma sweep
python gamma_sweep_lean.py
```

All runners produce PNG plots in the working directory and print summary tables to stdout.

## Dependencies

```
numpy
networkx
matplotlib
```
