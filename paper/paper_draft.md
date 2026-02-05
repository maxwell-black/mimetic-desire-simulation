# A Computational Test of Girard's Scapegoat Mechanism

**Maxwell J. Black**

Winthrop & Weinstine, P.A., Minneapolis

**Draft -- February 2026**

---

## Abstract

Girard claims that mimetic crisis resolves through unanimous polarization against a single victim via a "snowball effect" in which mimetic attraction "multiplies with the number of those polarized." We formalize and test this claim using an agent-based model with four variants arranged in a 2x2 design, crossing two hostility-transmission modes (linear vs. convex redistributive) with two hostility sources (object-rivalry vs. status-rivalry). The central finding is that convex redistribution of hostility under L1 conservation -- formalized as salience-weighted reallocation of a conserved hostility budget -- is the necessary and sufficient condition for scapegoat convergence. The effective phase boundary lies in a narrow interval just above linearity ($\gamma \in [1.02, 1.05]$). Ablation confirms that convexity without conservation collapses the contagion channel entirely. The model specifies the formal requirement Girard describes phenomenologically but leaves implicit.

**Keywords:** mimetic theory, scapegoat mechanism, agent-based modeling, Girard, conflictual mimesis, collective violence

---

## 1. Introduction

Girard's theory of the scapegoat mechanism makes a precise structural prediction: that mimetic dynamics within a community in crisis will produce spontaneous convergence of hostility onto a single victim, whose expulsion restores social peace. This prediction unifies Girard's accounts of archaic religion, sacrifice, myth, and persecution texts across a body of work spanning four decades. Yet despite its ambition, the prediction has remained largely untested by formal or computational methods. Girard's evidence is drawn from literary criticism (*Deceit, Desire, and the Novel*), comparative mythology and anthropology (*Violence and the Sacred*, *The Scapegoat*), and scriptural interpretation (*Things Hidden Since the Foundation of the World*, *I See Satan Fall Like Lightning*). The theoretical apparatus has generated a rich secondary literature, but its core dynamical claims -- that mimetic transmission of hostility produces convergent targeting, that the victim is arbitrary, that expulsion produces catharsis -- have not been subjected to controlled test.

This paper addresses that gap. We construct an agent-based model that implements Girard's two-phase account of mimetic crisis as described in *Things Hidden* (Book I, Chapter 1) and *Violence and the Sacred* (Chapter 6), then tests whether the predicted scapegoat convergence emerges from the formalized dynamics. Our approach is not to encode scapegoating as an outcome and observe its preconditions, but to encode the mimetic mechanisms Girard describes and observe whether scapegoating emerges.

The central finding is that Girard's two-phase decomposition -- rivalry generating hostility (acquisitive mimesis), followed by contagion of hostility producing convergence (conflictual mimesis) -- is structurally sound. But the finding also specifies a formal requirement that Girard describes phenomenologically without formalizing: the transition from "all against all" to "all against one" requires that hostility-transmission operate as a *convex redistribution* rule, meaning that an agent's mimetic pull toward competing targets is reallocated by convex salience weights under conservation of total perceived hostility mass. This is precisely Girard's claim that mimetic attraction "multiplies" rather than merely accumulates: relative mimetic pull between targets is amplified by the salience exponent. Our model shows that this redistributive character is the *entire* formal difference between crisis-without-resolution and scapegoating. The effective phase boundary lies in a narrow interval just above linearity ($\gamma \in [1.02, 1.05]$), and applying a convex transform without the redistribution step does not produce convergence -- it collapses the contagion channel entirely (Section 3.3).

### 1.1 Existing Computational Approaches

Computational engagement with Girard's mimetic theory is remarkably sparse. Sack (2021) presents the first agent-based model of mimetic desire in NetLogo, formalizing the triangular structure of subject-mediator-object from *Deceit, Desire, and the Novel*. However, Sack's model addresses only the desire triangle with 3-8 agents and does not extend to rivalry escalation, collective violence, or scapegoating. Gardin (2008) proposes "complex mimetic systems" as a framework connecting mimetic theory to complex adaptive systems, but presents no simulation or empirical results. Paes (2025) offers a NetLogo agent-based model of scapegoating as crisis management, simulating tension accumulation across a small-world network, though this work models crisis and victim-selection as programmatically distinct stages rather than testing whether convergence emerges from mimetic dynamics alone.

Our work differs from these predecessors in two respects. First, we test *emergence*: rather than encoding scapegoating as a mechanism and observing when it activates, we encode mimetic transmission rules and observe whether convergent targeting arises as an emergent outcome. Second, we conduct a *mechanism comparison*: we implement multiple candidate convergence mechanisms (linear mimetic averaging, convex redistributive salience weighting, status-based rivalry, and their combinations) and test which are necessary and sufficient for the predicted outcome. This comparative approach allows us to identify what formal structure does the work in Girard's theory.

### 1.2 Girard's Two-Phase Account

The textual basis for our model is Girard's account in *Things Hidden Since the Foundation of the World* (Book I, Chapter 1), which we briefly reconstruct.

**Phase 1: Acquisitive Mimesis and the Dissolution of Differences.** Mimetic desire -- the imitation of another's desire for an object -- generates rivalry when the object is scarce or indivisible. As rivalry intensifies: "the rivals 'forget about whatever objects are, in principle, the cause of the rivalry and instead become more fascinated with one another'" (Girard 1987, 26). The rivalry is "purified of any external stake and becomes a matter of pure rivalry and prestige" (ibid.). In *Violence and the Sacred*, Girard describes this as the crisis of differences: social distinctions that normally prevent direct rivalry dissolve, producing a state of undifferentiation in which "the monstrous double now takes the place of those objects that held the attention of the antagonists at a less advanced stage of the crisis" (Girard 1977, 161).

**Phase 2: Conflictual Mimesis and Unanimous Polarization.** Once objects of desire have dropped away, what remains is mimetic transmission of antagonism itself. Girard writes:

> If the object is excluded there can no longer be any acquisitive mimesis as we have defined it. There is no longer any support for mimesis but the antagonists themselves. What will occur at the heart of the crisis will therefore be the mimetic substitution of antagonists. (Girard 1987, 26)

The critical dynamical claim follows:

> Once the object has disappeared and the mimetic frenzy has reached a high degree of intensity, one can expect conflictual mimesis to take over and snowball in its effects. Since the power of mimetic attraction multiplies with the number of those polarized, it is inevitable that at one moment the entire community will find itself unified against a single individual. (Girard 1987, 26)

Two features of this passage are essential for formalization. First, Girard distinguishes the mechanism that produces the crisis (acquisitive mimesis, rivalry over objects) from the mechanism that produces convergence (conflictual mimesis, snowballing hostility-transmission). These are structurally different processes with different dynamical properties. Second, the convergence mechanism is characterized as *multiplicative*: "the power of mimetic attraction *multiplies* with the number of those polarized." This is not linear diffusion (where each additional hostile agent adds a fixed increment of mimetic pull) but a process in which relative differences in salience are amplified, so that mimetic attraction toward a leading target grows disproportionately as polarization increases. Our model tests whether this distinction -- linear versus convex redistributive hostility-transmission -- is in fact the formal boundary between crisis-without-convergence and scapegoating.

---

## 2. Model Design

### 2.1 Overview

We implement a family of agent-based models sharing common infrastructure but differing in their hostility-transmission mechanism. All variants operate on a Watts-Strogatz small-world network of $N = 50$ agents with mean degree 6 and rewiring probability 0.15. We chose $N = 50$ as the default because it is large enough that $1/N$ effects do not dominate the convergence metrics, small enough for tractable visualization of individual agent trajectories, and situated in the middle of the range ($N = 20$--$100$) across which we verify robustness in Section 3.4. Each agent maintains a desire vector over a set of rivalrous and non-rivalrous objects, and an aggression vector over all other agents. The simulation proceeds in discrete timesteps, each consisting of:

1. **Desire step:** agents mimetically absorb neighbors' desires (weighted by prestige).
2. **Aggression-source step:** shared desire for rivalrous objects generates mutual aggression between neighbors (acquisitive mimesis), or status proximity generates rivalry-based aggression (in rivalry variants).
3. **Aggression-spread step:** agents mimetically absorb neighbors' aggression patterns. *This step varies across model variants and constitutes the experimental manipulation.*
4. **Decay step:** all aggression decays by a fixed fraction per timestep.
5. **Expulsion step:** if any agent's total received aggression exceeds a threshold, that agent is removed and all aggression toward them is zeroed.

The expulsion step is a *consequence rule*, not a convergence mechanism: it removes agents who have accumulated sufficient collective hostility, but does not influence how hostility accumulates or converges. Scapegoat convergence, if it occurs, must emerge from the aggression-spread step.

### 2.2 Variants

We test four model variants designed to isolate the independent contributions of two candidate convergence mechanisms: (i) the character of hostility transmission (linear averaging vs. convex redistributive weighting), and (ii) the source of hostility (shared-object rivalry vs. status-proximity rivalry). The four variants are the cells of a 2x2 design:

|  | Linear spread | Attentional concentration spread |
|---|---|---|
| **Object-rivalry source** | LM (baseline) | AC |
| **Status-rivalry source** | RL | RA |

This design allows us to attribute convergence effects to transmission character, hostility source, or their interaction. If convergence requires only convex redistribution, the AC column should converge regardless of source. If rivalry alone suffices, the bottom row should converge regardless of transmission. If both are needed, only RA should converge.

**LM: Linear Mimesis (baseline).** Agent *i*'s mimetic pull toward target *j* is a prestige-weighted average of neighbors' aggression toward *j*:

$$\text{pull}_i(j) = \frac{\sum_{k \in N(i)} w_{ik} \cdot \text{agg}_k(j)}{\sum_{k \in N(i)} w_{ik}}$$

Updated aggression: $\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$

where $\alpha \in [0, 1]$ controls the ratio of autonomous to mimetic aggression. This is the most literal formalization of "agents imitate others' hostility."

**AC: Attentional Concentration (Convex Redistribution).** Let $h_i(j)$ denote the prestige-weighted mean hostility toward target $j$ among $i$'s neighbors (computed identically to LM). Agent $i$ then constructs salience weights and mimetic pull as follows.

Define salience weights:

$$w_i(j) = \frac{h_i(j)^\gamma}{\sum_k h_i(k)^\gamma}$$

That is: each target's share of agent $i$'s mimetic attention is the target's perceived hostility raised to the power $\gamma$, normalized across all targets. For each target $j$, agent $i$'s mimetic pull is then:

$$\text{pull}_i(j) = w_i(j) \cdot \sum_k h_i(k)$$

That is: agent $i$ adopts total mimetic pull equal to the total hostility it perceives in its neighborhood, but distributes that pull across targets according to the convex salience weights.

Two identities characterize this operator and connect it to Girard's phenomenology.

*L1 conservation.* Summing over targets:

$$\sum_j \text{pull}_i(j) = \sum_k h_i(k)$$

The total mimetic pull agent $i$ receives equals the total hostility mass it perceives among its neighbors. The spread step does not create hostility mass; it redistributes it. Agent $i$ adopts the same total hostility mass it perceives in its neighborhood, but reallocates that mass across targets by convex salience weights.

*Ratio identity.* For any two targets $a, b$ with $h_i(b) > 0$:

$$\frac{\text{pull}_i(a)}{\text{pull}_i(b)} = \left(\frac{h_i(a)}{h_i(b)}\right)^\gamma$$

Relative mimetic pull between any two targets is the ratio of their perceived hostilities raised to the power $\gamma$. This is the mathematically exact sense in which mimetic attraction "multiplies": a difference in salience becomes an amplified difference in imitative focus.

The salience exponent $\gamma$ controls the qualitative character of redistribution. When $\gamma = 1$, the operator reduces to LM (linear averaging): salience weights are proportional to perceived hostility, and no redistribution occurs. When $\gamma > 1$, relative salience differences are amplified (convex redistribution): targets with above-average hostility capture disproportionate mimetic pull. When $\gamma < 1$, relative salience differences are compressed (concave redistribution): the operator actively disperses hostility, working against convergence.

Normalizing salience weights and rescaling by $\sum_k h_i(k)$ ensures that varying $\gamma$ changes only the *distribution* of mimetic pull across targets, not the overall magnitude. Without this conservation, a power transform would implicitly change the effective strength of mimesis by shrinking subunit signals (since for $0 < x < 1$ and $\gamma > 1$, $x^\gamma < x$). The ablation study in Section 3.3 confirms that this conservation property is constitutive: removing it collapses the contagion channel entirely.

Updated aggression: $\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$

**RL: Rivalry + Linear.** Aggression is sourced not from shared object-desire but from *status rivalry*. Each agent has a status scalar (initialized near 0.5); agents in close status proximity to connected neighbors generate mutual aggression, weighted toward upward rivalry (agents rival those of equal or higher status more than those below). Collectively received aggression degrades the target's status, reducing their prestige (status-dependent) and their capacity to resist further targeting. Aggression *spreads* via linear mimesis (as in LM). This tests whether the rivalry-escalation feedback loop produces convergence without the redistributive operator.

**RA: Rivalry + Attention.** Same status-rivalry dynamics as RL, but aggression spreads via attentional concentration (as in AC). This tests the combination of both Girardian phases: rivalry-driven aggression generation plus convex redistributive conflictual mimesis.

### 2.3 Measurements

For each simulation run, we record:

- **Aggression Gini coefficient:** inequality in the distribution of received aggression across living agents. Higher Gini indicates more concentrated targeting.
- **Top-target share:** fraction of total received aggression absorbed by the single most-targeted agent.
- **Convergence ratio (top1/top2):** received aggression of the most-targeted agent divided by that of the second-most-targeted. Values near 1 indicate diffuse hostility; values >> 1 indicate focused targeting.
- **Shannon entropy:** information-theoretic measure of targeting diffusion. Lower entropy indicates more concentrated targeting.
- **Expulsion count and timing:** number and temporal distribution of agent removals.
- **Catharsis:** fractional tension drop following each expulsion event.
- **Victim status at expulsion** (rivalry variants): the expelled agent's status relative to the population mean, testing whether "signs of the victim" emerge endogenously.
- **Modal-target agreement:** fraction of living agents whose top aggression target is the modal target, excluding agents whose aggression vector sums to less than $10^{-8}$ (to prevent argmax-on-zero artifacts).

We define *convergence* as modal-target agreement >= 0.95 sustained for 10 consecutive steps. The theoretical ceiling for modal agreement is $(N-1)/N = 0.98$, because self-targeting is excluded.

---

## 3. Results

### 3.1 The Convergence Engine: Convex Redistribution

The central result is displayed in Table 1.

| Variant | Mechanism | Mean Gini | Top-Target Share | Convergence Ratio | Expulsions | Catharsis |
|---------|-----------|-----------|------------------|-------------------|------------|-----------|
| LM | Linear mimesis | 0.115 | 0.041 | 1.05 | 16.6 | 4.0% |
| AC | Attentional concentration | 0.739 | 0.310 | 1.62 | 28.8 | 18.8% |
| RL | Rivalry + linear | 0.133 | 0.040 | 1.03 | 15.9 | 4.0% |
| RA | Rivalry + attention | 0.803 | 0.353 | 1.45 | 28.2 | 27.0% |

*Table 1. Summary metrics across 10 runs per variant, alpha = 0.15, salience exponent = 2.0, 600 timesteps.*

The results divide cleanly along the transmission-character axis of the 2x2 design. Variants with linear hostility-transmission (LM, RL) produce Gini coefficients around 0.11--0.13, top-target shares near $1/N$ (the uniform baseline for 50 agents is 0.02), and convergence ratios near 1.0. Hostility spreads but does not converge. Variants with convex redistributive transmission (AC, RA) produce Gini coefficients above 0.73, top-target shares of 0.31--0.35, and convergence ratios of 1.4--1.6. Hostility both spreads and converges on a single target.

The addition of rivalry dynamics to linear mimesis (LM to RL) produces negligible change in convergence metrics. Rivalry generates more aggression -- hence comparable expulsion counts -- but does not concentrate it. By contrast, the AC mechanism alone produces dramatic convergence. Rivalry combined with attentional concentration (RA) produces the strongest convergence and deepest catharsis, but the redistributive mechanism does the overwhelming majority of the convergence work.

Applying a convex transform without conservation (pull $= h^\gamma$) does not produce convergence and in fact collapses the contagion channel by attenuating subunit signals (Section 3.3). Convergence requires the full redistributive operator: convex salience weights *plus* L1 conservation of perceived hostility mass.

### 3.2 The Effective Phase Boundary Near Linearity

To locate the boundary between diffuse crisis and scapegoat convergence, we performed a fine-grained sweep of the salience exponent $\gamma$ under the no-expulsion condition, isolating the convergence mechanism from the expulsion consequence rule.

| $\gamma$ | Peak Modal (sd) | Final Modal (sd) | Peak Gini | Med $t_{95}$ | Convergence Rate |
|-----------|-----------------|------------------|-----------|---------------|------------------|
| 0.75 | 0.125 (0.017) | 0.098 (0.017) | 0.100 | -- | 0% |
| 0.90 | 0.150 (0.020) | 0.122 (0.027) | 0.103 | -- | 0% |
| 0.95 | 0.172 (0.032) | 0.136 (0.029) | 0.104 | -- | 0% |
| 1.00 | 0.240 (0.074) | 0.194 (0.057) | 0.115 | -- | 0% |
| 1.01 | 0.305 (0.118) | 0.218 (0.071) | 0.132 | -- | 0% |
| 1.02 | 0.463 (0.260) | 0.356 (0.221) | 0.166 | 421 | 12% |
| 1.05 | 0.980 (0.000) | 0.980 (0.000) | 0.810 | 116 | 100% |
| 1.08 | 0.980 (0.000) | 0.980 (0.000) | 0.881 | 74 | 100% |
| 1.10 | 0.980 (0.000) | 0.980 (0.000) | 0.906 | 62 | 100% |
| 1.15 | 0.980 (0.000) | 0.980 (0.000) | 0.937 | 43 | 100% |
| 1.25 | 0.980 (0.000) | 0.980 (0.000) | 0.959 | 30 | 100% |
| 1.50 | 0.980 (0.000) | 0.980 (0.000) | 0.970 | 29 | 100% |
| 2.00 | 0.980 (0.000) | 0.980 (0.000) | 0.972 | 30 | 100% |

*Table 2. Fine-grained gamma-sweep results. N=50 agents, Watts-Strogatz k=6, p=0.15, alpha=0.15, no expulsion, 8 runs x 600 steps per condition.*

The effective phase boundary is sharp and narrowly localized. For $\gamma \leq 1.01$, no runs converged within 600 steps. At $\gamma = 1.02$, convergence is rare and slow (1 of 8 runs; $t_{95} = 421$). By $\gamma = 1.05$, convergence is universal (8/8; median $t_{95} = 116$). Convergence then accelerates with increasing $\gamma$: median $t_{95} = 74$ at 1.08, 62 at 1.10, 43 at 1.15. The effective phase boundary lies in the narrow interval [1.02, 1.05]: a ~3% departure from purely proportional imitation separates crisis-without-convergence from robust scapegoat convergence.

Near the boundary, convergence exhibits pronounced critical slowing: as $\gamma \to 1^+$, time-to-convergence increases sharply.[^crit] Above the boundary, coordination rapidly saturates: peak modal agreement reaches its ceiling of $(N-1)/N = 0.98$ for all $\gamma \geq 1.05$. But the inequality of hostility mass (peak Gini) continues to increase with $\gamma$ -- from 0.810 at $\gamma = 1.05$ to 0.972 at $\gamma = 2.0$. $\gamma$ governs not only convergence speed but also the depth of hostility concentration: at low superlinear values, the community converges on a target but the disparity between target and non-target hostility is modest; at high $\gamma$, essentially all hostility mass is concentrated on a single agent.

[^crit]: The critical-slowing pattern is consistent with a phase-transition-like boundary, though we do not claim a continuous (second-order) phase transition on the basis of these finite-horizon data alone. We use "effective phase boundary" throughout to denote the empirically observed transition interval in this model, without claiming universality-class membership.

Decreasing $\gamma$ below 1 reduces both peak modal agreement and peak Gini monotonically. Under the normalized salience weighting $w(j) \propto h(j)^\gamma$, values $\gamma < 1$ compress relative salience differences, dispersing hostility rather than focusing it. The sublinear regime is actively anti-convergent: hostility spreads but is pushed toward uniformity rather than concentration. Only a minimal departure from linearity is required for convergence to occur on simulation timescales.

### 3.3 Operator Ablation

The AC convergence mechanism has two components: the convex power transform ($h^\gamma$ with $\gamma > 1$) and the redistributive normalization step (dividing by $\sum_k h_i(k)^\gamma$ and rescaling by $\sum_k h_i(k)$). This ablation study isolates their respective contributions by testing the transform with and without the redistribution, building from the simplest case to the full operator.

We define total aggression mass at time $t$ as $M_t = \sum_{i \neq j} \text{agg}_i(t)(j)$, summing over all ordered pairs of living agents. "Final Mass" is $M$ at $t = n\_steps$.

**Condition 1: Linear baseline ($\gamma = 1$).** Hostility spreads but does not converge: peak Gini = 0.115, peak modal = 0.240. Total aggression mass stabilizes at approximately 644, reflecting an equilibrium between the rivalry-sourcing step and decay. This is the LM variant and establishes the baseline against which the other conditions are measured.

**Condition 2: Raw convex transform ($h^\gamma$, no normalization).** One might expect that applying a superlinear transform ($h^\gamma$ with $\gamma = 2$) without the redistribution step would still produce convergence, since the exponent amplifies differences. It does not. Peak Gini = 0.115 and peak modal agreement = 0.113 -- *worse* than linear. Total aggression mass collapses to approximately 9.1, a 98.6% reduction relative to Condition 1. The explanation is arithmetic: for $0 < x < 1$ and $\gamma > 1$, $x^\gamma < x$. Since hostility signals are typically subunit (fractional values between 0 and 1 after prestige-weighted averaging), the power transform systematically attenuates the contagion channel. With decay and mixing, this attrition bleeds the system dry.[^clip]

**Condition 3: Full AC operator (convex redistribution, L1 conserved).** The normalization step rescales the sharpened weights so total mimetic pull equals total perceived hostility, preventing the attrition that destroys Condition 2. Peak Gini = 0.972, peak modal = 0.980, and total mass = 786. This is the standard AC variant and demonstrates that convergence requires the full redistributive operator.

| Condition | Description | Peak Gini | Peak Modal | Final Mass | Max Aggression |
|-----------|-------------|-----------|------------|------------|----------------|
| 1 | Linear baseline ($\gamma = 1$) | 0.115 | 0.240 | 644 | 0.646 |
| 2 | Raw $h^\gamma$ (no normalization) | 0.115 | 0.113 | 9.1 | 0.053 |
| 3 | Full AC (convex redistribution, L1 conserved) | 0.972 | 0.980 | 786 | 19.1 |

*Table 3. Ablation results. All conditions: N=50, alpha=0.15, no expulsion, 600 steps, 8 runs. Conditions 2 and 3 use gamma=2.0.*

The convergence boundary is not "convexity alone"; it is convexity used as a redistribution rule under mass conservation.

[^clip]: Clamping $h^\gamma$ to $[0, \text{max\_val}]$ produces results identical to Condition 2 (peak Gini 0.115, peak modal 0.113), confirming the collapse is due to signal attrition, not numerical overflow.

### 3.4 Robustness

The convergence result under convex redistribution is robust across:

- **Network topology:** Watts-Strogatz (small-world), Barabasi-Albert (scale-free), Erdos-Renyi (random), and complete graphs all produce convergence at $\gamma > 1$. Complete graphs produce the strongest convergence (Gini 0.558, convergence ratio 14.95) but also the most expulsions (46 of 50 agents), consistent with Girard's account of undifferentiation crisis in communities without structural barriers to mimetic transmission.
- **Group size:** Convergence occurs at N = 20, 35, 50, 75, and 100, with Gini increasing slightly with group size (0.598 to 0.754). Small groups produce sharper individual targeting (top-target share 0.50 at N = 20).
- **Mimetic susceptibility (alpha):** Even at alpha = 0.85 (85% autonomous aggression, 15% mimetic), convergence occurs at $\gamma \geq 1.5$. The redistributive mechanism does not require high mimetic susceptibility; it requires only that *whatever mimesis occurs* has convex redistributive character.

### 3.5 Catharsis Dynamics

Expulsion produces measurable tension reduction: 18.8% mean drop in AC, 27.0% in RA. In RA, 27 of 30 expulsions in a representative run produce genuine catharsis (tension decrease). The system exhibits crisis-relief-reaccumulation cycles with bimodal inter-expulsion intervals (clusters of rapid expulsions separated by extended quiet periods).

The immediate tension drop is partly arithmetic: removing the most-targeted agent eliminates their share of total received aggression. What is emergent is that tension does not immediately redirect to a new target. The attentional funnel requires time to reconstitute after losing its focal point; this temporal gap is the emergent catharsis. The bimodal rhythm -- rapid-fire scapegoating during acute crisis, long dormant periods between crises -- is entirely emergent and has no coded precursor.

### 3.6 The Arbitrariness and Endogenous Marginality of the Victim

In AC (attentional concentration only, no rivalry), victims are statistically indistinguishable from the general population across all measured network properties: degree centrality (0.125 vs 0.122), betweenness centrality (0.037 vs 0.035), clustering coefficient (0.385 vs 0.370). The victim's identity is a contingent outcome of the attentional cascade, not a structural property of the network. This confirms Girard's claim about the fundamental arbitrariness of the victim.

In RA (rivalry + attention), a different and theoretically richer picture emerges. Victims have a mean status of 0.264 at the moment of expulsion, against a population mean of 0.409 -- a deficit of 0.145. But status was initialized uniformly around 0.5. The victim's low status is an endogenous product of the targeting process: they were targeted, which degraded their status, which reduced their prestige and social capital, which made them less able to resist further targeting. The "signs of the victim" -- the visible markers of difference that retrospectively justify the community's violence -- are produced by the mechanism itself, not presupposed by it.

This finding directly addresses Girard's claim that the victim's "guilt" and "difference" are retrospective constructions. As Girard argues in *The Scapegoat*, the signs of the victim are not the causes of victimization but its consequences (Girard 1986, ch. 2).

In RL (rivalry + linear), a tiny victim status deficit exists (0.012) but is negligible -- status degradation occurs but does not concentrate on any single target sufficiently to produce visible marginality. The endogenous production of "signs of the victim" requires both the rivalry feedback (status degradation) and the convergence mechanism (convex redistribution).

---

## 4. Discussion

### 4.1 What the Model Confirms in Girard

**The two-phase decomposition is structurally correct.** Girard's distinction between acquisitive mimesis (generating hostility through rivalry) and conflictual mimesis (producing convergence through hostility-contagion) is not merely expository but structurally necessary. The comparison between RL (rivalry without convergence mechanism) and AC (convergence mechanism without rivalry) demonstrates that these are genuinely independent dynamical contributions. Rivalry generates the raw material of hostility; conflictual mimesis concentrates it. Neither alone produces the full Girardian outcome; their combination does.

**The "snowball effect" is the convergence mechanism.** Girard's claim that "the power of mimetic attraction multiplies with the number of those polarized" is confirmed in precise formal terms. The redistributive character of hostility-transmission -- formalized as convex salience weighting with any exponent $\gamma > 1$ -- is the necessary and sufficient condition for the transition from diffuse crisis to focused scapegoating. Linear hostility-transmission ($\gamma = 1$) produces crisis without resolution, regardless of other parameter settings. The effective phase boundary is sharp and occurs at minimal superlinearity ($\gamma$ approximately 1.02--1.05), indicating that the mechanism is robust rather than fragile.

**The victim is arbitrary, and "signs of the victim" are endogenously produced.** In the pure attention model (AC), victims are network-indistinguishable from the general population. In the combined model (RA), victims acquire measurable marginality through the targeting process itself. Both findings are consistent with Girard's account: the victim need not be initially different; their "difference" is a product of the scapegoating process.

**Catharsis is real and temporally structured.** Expulsion produces genuine tension reduction with emergent crisis-relief-reaccumulation cycles.

### 4.2 What the Model Specifies Beyond Girard

Girard describes conflictual mimesis phenomenologically -- as fascination, obsession, the "snowball effect." The model identifies the precise formal property that produces convergence: convex redistribution of hostility under L1 conservation, where mimetic pull toward competing targets is reallocated by salience weights that amplify relative differences. Girard gestures toward this with "multiplies," but this redistributive character is not one feature among many: it is *the* distinguishing formal feature of the scapegoat mechanism.

The ablation (Section 3.3) reveals a further structural requirement: convexity without conservation destroys convergence rather than producing it. The conserved-budget structure is constitutive, not optional. The mechanism is not amplification but *organization* -- the AC operator does not create hostility mass; it gives existing mass a direction. This aligns more precisely with Girard's phenomenology than a naive "amplification" reading. In Girard, mimetic crisis is already a high-energy field of undifferentiated violence; the scapegoat mechanism organizes that field into unanimity, not intensifying it. Rivalry dynamics load the system with hostility mass (acquisitive mimesis as fuel), while convex redistribution focuses that mass onto a single target (conflictual mimesis as organizing engine).

The 2x2 design also clarifies the relative dynamical weight of the two phases: the AC mechanism accounts for the overwhelming majority of convergence, while rivalry contributes an additional ~8% Gini concentration and the endogenous marginality effect. Rivalry is a potentiator and enrichment of the scapegoat mechanism, not its primary driver.

Finally, the model reveals that minimal mimetic susceptibility suffices. Even populations where 85% of individual aggression is autonomously generated produce scapegoats if the remaining 15% of mimetic transmission operates under convex redistribution. Girard's account emphasizes the dissolution of individual autonomy in crisis ("the doubles"), but the *qualitative character* of mimesis matters more than its *quantity*.

### 4.3 Relation to Empirical Literature on Attention Cascades

The convex redistributive salience mechanism we identify as the formal core of the scapegoat mechanism has independent empirical support in research on collective attention and information cascades. The AC operator is formally a budget allocation rule -- fixed total perceived mass, convex reallocation among competing targets -- which is the mathematical backbone of finite-attention and salience-competition models in the empirical literature.

Hodas and Lerman (2014) provide the most directly relevant finding: in their study of content diffusion on social media platforms, the probability of an individual sharing content scales with the *fraction* of their contacts who have already shared it, not the absolute count. This is a consequence of competition for finite attention: each user's feed is a fixed-capacity channel, and items compete for slots in proportion to their prevalence among contacts. The result is a naturally superlinear concentration effect on popular items -- precisely the finite-attention redistribution that the AC operator formalizes.

Weng et al. (2012) demonstrate the mechanism at the system level, showing that competition for limited user attention, combined with the network structure of social media, is sufficient to produce the heavy-tailed distribution of content popularity ("going viral"). Their agent-based model produces power-law popularity distributions from finite-attention agents on a network -- structurally analogous to our finding that finite-attention redistribution produces power-law-like concentration of hostility.

Lorenz-Spreen et al. (2019) document the macro-level consequence: collective attention spans are accelerating across multiple domains (Twitter, Google, Reddit, cinema, academic citations), with topics cycling more rapidly through public consciousness. The acceleration is consistent with increasing competition for finite collective attention producing sharper winner-take-all dynamics over time.

The application of these findings to hostile targeting is a theoretically motivated extension, not a directly observed phenomenon. But the cognitive infrastructure -- finite attention, salience-driven filtering, mimetic absorption of neighbors' priorities -- is empirically grounded, and our model identifies the formal conditions under which these same dynamics produce convergent scapegoating.

### 4.4 Limitations and Falsifiability

The model treats the transition from acquisitive to conflictual mimesis as structurally given (separate coded mechanisms) rather than endogenous. A richer model might attempt to formalize the conditions under which agents shift from object-focused rivalry to objectless hostility-transmission, testing Girard's claim that this transition occurs when mimetic crisis reaches a critical intensity.

The model does not include institutional or ritual structures that, in Girard's later work, serve to *prevent* or *channel* mimetic crisis. Prohibition, ritual, and sacrificial substitution are absent. Testing whether the addition of such structures produces the stability Girard predicts -- mimetic crisis contained through institutionalized repetition of the founding murder -- is a natural extension.

The model assumes a single community without external relations. Girard's account of the scapegoat mechanism is fundamentally about intra-community dynamics, but real communities exist in relation to others. Whether inter-community contact modulates or amplifies the scapegoat mechanism is unexplored.

Our model of "attentional concentration" is one possible formalization of convex redistributive hostility-transmission. Other formalizations -- threshold models, information-cascade models, or explicit Girardian "fascination" dynamics -- might produce convergence with different properties. Our finding that any degree of superlinearity suffices (in the sense of convex redistribution) suggests that the specific functional form matters less than the qualitative property of budget-conserving convex reallocation, but systematic comparison of alternative formalizations is warranted.

**Falsifiability.** The model's core claim is that hostility convergence requires superlinear (convex redistributive) transmission. This claim would be disconfirmed by empirical observation of scapegoating convergence in a population where hostility transmission is demonstrably linear -- that is, where individuals' adoption of hostility toward a target is strictly proportional to the prevalence of that hostility among their contacts, with no superlinear concentration. If real-world mob targeting events can be shown to emerge from purely proportional contagion without any attentional or salience-based redistribution, the model's central thesis is falsified.

---

## 5. Conclusion

Girard writes that "the power of mimetic attraction multiplies with the number of those polarized." We have formalized that sentence and tested it. The formalization reveals that the multiplicative character of mimetic attraction in hostile contexts -- what Girard calls conflictual mimesis and describes as a "snowball effect" -- is the necessary and sufficient formal condition for the emergence of scapegoat convergence. Linear mimetic transmission, however intense, produces crisis without resolution: hostility spreads but does not converge. Convex redistributive transmission -- any degree of it, with the effective phase boundary lying between $\gamma = 1.02$ and $\gamma = 1.05$ -- produces the full Girardian pattern: convergence onto an arbitrary single victim, cathartic tension reduction upon expulsion, and -- when combined with status-rivalry dynamics -- endogenous production of the "signs of the victim."

The mechanism is not amplification but organization: the AC operator does not create hostility mass; it focuses existing mass onto a single target through convex salience weights under L1 conservation. Applying a convex transform without the redistribution step collapses the contagion channel entirely (Section 3.3). The convergence boundary is convexity used as a budget allocation rule, not convexity alone.

The model does not replace Girard's theory; it specifies it. Girard correctly identified the two-phase structure of mimetic crisis (rivalry-driven hostility generation, then hostility-contagion-driven convergence), correctly predicted the emergent properties (arbitrariness and retrospective marginalization of the victim, cathartic relief), and correctly characterized the convergence mechanism as multiplicative. What the model adds is the demonstration that this multiplicative character is not one feature among many but the *precise formal boundary* between crisis and scapegoating -- and that it is robust across network structures, group sizes, and levels of individual mimetic susceptibility.

---

## References

Bakshy, E., Hofman, J. M., Mason, W. A., & Watts, D. J. (2011). Everyone's an influencer: Quantifying influence on Twitter. *Proceedings of the Fourth ACM International Conference on Web Search and Data Mining*, 65-74.

Gardin, A. (2008). Complex mimetic systems. *Contagion: Journal of Violence, Mimesis, and Culture*, 15/16, 25-42.

Girard, R. (1965). *Deceit, Desire, and the Novel: Self and Other in Literary Structure*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1977). *Violence and the Sacred*. Trans. P. Gregory. Johns Hopkins University Press.

Girard, R. (1986). *The Scapegoat*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1987). *Things Hidden Since the Foundation of the World*. Trans. S. Bann and M. Metteer. Stanford University Press.

Girard, R. (2001). *I See Satan Fall Like Lightning*. Trans. J. G. Williams. Orbis Books.

Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*, 83(6), 1420-1443.

Hodas, N. O., & Lerman, K. (2014). The simple rules of social contagion. *Scientific Reports*, 4, 4343.

Lorenz-Spreen, P., Moensted, B. M., Hovel, P., & Lehmann, S. (2019). Accelerating dynamics of collective attention. *Nature Communications*, 10, 1759.

O'Higgins Norman, J., & Connolly, J. (2011). Mimetic theory and scapegoating in the age of cyberbullying. *Pastoral Care in Education*, 29(4), 287-300.

Paes, L. (2025). An agent-based model of scapegoating. Unpublished manuscript. [NetLogo model.]

Sack, G. A. (2021). Geometries of desire: A computational approach to Girardian mimetic theory. *Contagion: Journal of Violence, Mimesis, and Culture*, 28, 81-112.

Weng, L., Flammini, A., Vespignani, A., & Menczer, F. (2012). Competition among memes in a world with limited attention. *Scientific Reports*, 2, 335.

---

## Appendix A: Model Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| N | 50 | Number of agents |
| k | 6 | Mean degree (Watts-Strogatz) |
| p | 0.15 | Rewiring probability |
| alpha | 0.15 | Autonomous vs mimetic aggression ratio |
| gamma | 2.0 | Salience exponent (AC, RA) |
| Objects | 8 (5 rivalrous) | Number of desire objects |
| Rivalry-to-aggression | 0.2 | Aggression increment from shared desire |
| Aggression decay | 0.03 | Per-step decay fraction |
| Expulsion threshold | 8.0 | Received aggression triggering removal |
| Status loss rate | 0.005 | Aggression-to-status degradation (RL, RA) |
| Rivalry intensity | 0.15 | Rivalry-to-aggression conversion (RL, RA) |
| Timesteps | 600 | Simulation duration |
| Runs per condition | 10 | Replications for summary statistics |

## Appendix B: Code Availability

All simulations are implemented in Python using NumPy and NetworkX. Source code, runner scripts, and figure-generation code are available at: https://github.com/maxwell-black/mimetic-desire-simulation
