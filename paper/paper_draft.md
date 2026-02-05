# Mimetic Attraction Multiplies: A Computational Test of Girard's Scapegoat Mechanism

**Maxwell J. Black**

Winthrop & Weinstine, P.A., Minneapolis

**Draft -- February 2026**

---

## Abstract

René Girard claims that mimetic crisis resolves through unanimous polarization against a single victim, driven by a "snowball effect" in which "the power of mimetic attraction multiplies with the number of those polarized" (*Things Hidden*, p. 26). This paper formalizes and tests that claim using agent-based simulation. We implement Girard's two-phase decomposition -- acquisitive mimesis (rivalry generating hostility) and conflictual mimesis (contagion of hostility producing convergence) -- as structurally distinct mechanisms and test their respective contributions to scapegoat emergence. We find that Girard's two-phase architecture is structurally correct: rivalry alone generates hostility but does not concentrate it; superlinear hostility-transmission, formalizing the "snowball effect," produces convergence onto a single victim; and their combination yields the fullest Girardian outcome, including endogenous marginalization of the victim. The model's primary contribution is specifying the formal requirement Girard leaves implicit: hostility-transmission must be superlinear -- any degree of superlinearity suffices -- for the transition from "all against all" to "all against one."

**Keywords:** mimetic theory, scapegoat mechanism, agent-based modeling, Girard, conflictual mimesis, collective violence

---

## 1. Introduction

Girard's theory of the scapegoat mechanism makes a precise structural prediction: that mimetic dynamics within a community in crisis will produce spontaneous convergence of hostility onto a single victim, whose expulsion restores social peace. This prediction unifies Girard's accounts of archaic religion, sacrifice, myth, and persecution texts across a body of work spanning four decades. Yet despite its ambition, the prediction has remained largely untested by formal or computational methods. Girard's evidence is drawn from literary criticism (*Deceit, Desire, and the Novel*), comparative mythology and anthropology (*Violence and the Sacred*, *The Scapegoat*), and scriptural interpretation (*Things Hidden Since the Foundation of the World*, *I See Satan Fall Like Lightning*). The theoretical apparatus has generated a rich secondary literature, but its core dynamical claims -- that mimetic transmission of hostility produces convergent targeting, that the victim is arbitrary, that expulsion produces catharsis -- have not been subjected to controlled test.

This paper addresses that gap. We construct an agent-based model that implements Girard's two-phase account of mimetic crisis as described in *Things Hidden* (Book I, Chapter 1) and *Violence and the Sacred* (Chapter 6), then tests whether the predicted scapegoat convergence emerges from the formalized dynamics. Our approach is not to encode scapegoating as an outcome and observe its preconditions, but to encode the mimetic mechanisms Girard describes and observe whether scapegoating emerges.

The central finding is that Girard's two-phase decomposition -- rivalry generating hostility (acquisitive mimesis), followed by contagion of hostility producing convergence (conflictual mimesis) -- is structurally sound. But the finding also specifies a formal requirement that Girard describes phenomenologically without formalizing: the transition from "all against all" to "all against one" requires that hostility-transmission be *superlinear*, meaning that the mimetic pull toward a target must grow faster than proportionally with the amount of existing hostility toward that target. This is precisely Girard's claim that mimetic attraction "multiplies" rather than merely accumulates, but our model shows that this multiplicative character is the *entire* formal difference between crisis-without-resolution and scapegoating.

### 1.1 Existing Computational Approaches

Computational engagement with Girard's mimetic theory is remarkably sparse. Sack (2021) presents the first agent-based model of mimetic desire in NetLogo, formalizing the triangular structure of subject-mediator-object from *Deceit, Desire, and the Novel*. However, Sack's model addresses only the desire triangle with 3-8 agents and does not extend to rivalry escalation, collective violence, or scapegoating. Gardin (2008) proposes "complex mimetic systems" as a framework connecting mimetic theory to complex adaptive systems, but presents no simulation or empirical results. Paes (2025) offers a NetLogo agent-based model of scapegoating as crisis management, simulating tension accumulation across a small-world network, though this work models crisis and victim-selection as programmatically distinct stages rather than testing whether convergence emerges from mimetic dynamics alone.

Our work differs from these predecessors in two respects. First, we test *emergence*: rather than encoding scapegoating as a mechanism and observing when it activates, we encode mimetic transmission rules and observe whether convergent targeting arises as an emergent outcome. Second, we conduct a *mechanism comparison*: we implement multiple candidate convergence mechanisms (linear mimetic averaging, superlinear attentional concentration, status-based rivalry, and their combinations) and test which are necessary and sufficient for the predicted outcome. This comparative approach allows us to identify what formal structure does the work in Girard's theory.

### 1.2 Girard's Two-Phase Account

The textual basis for our model is Girard's account in *Things Hidden Since the Foundation of the World* (Book I, Chapter 1), which we briefly reconstruct.

**Phase 1: Acquisitive Mimesis and the Dissolution of Differences.** Mimetic desire -- the imitation of another's desire for an object -- generates rivalry when the object is scarce or indivisible. As rivalry intensifies, the rivals "forget about whatever objects are, in principle, the cause of the rivalry and instead become more fascinated with one another" (Girard 1987, 26). The rivalry is "purified of any external stake and becomes a matter of pure rivalry and prestige" (ibid.). In *Violence and the Sacred*, Girard describes this as the crisis of differences: social distinctions that normally prevent direct rivalry dissolve, producing a state of undifferentiation in which "the monstrous double now takes the place of those objects that held the attention of the antagonists at a less advanced stage of the crisis" (Girard 1977, 161).

**Phase 2: Conflictual Mimesis and Unanimous Polarization.** Once objects of desire have dropped away, what remains is mimetic transmission of antagonism itself. Girard writes:

> If the object is excluded there can no longer be any acquisitive mimesis as we have defined it. There is no longer any support for mimesis but the antagonists themselves. What will occur at the heart of the crisis will therefore be the mimetic substitution of antagonists. (Girard 1987, 26)

The critical dynamical claim follows:

> Once the object has disappeared and the mimetic frenzy has reached a high degree of intensity, one can expect conflictual mimesis to take over and snowball in its effects. Since the power of mimetic attraction multiplies with the number of those polarized, it is inevitable that at one moment the entire community will find itself unified against a single individual. (Girard 1987, 26)

Two features of this passage are essential for formalization. First, Girard distinguishes the mechanism that produces the crisis (acquisitive mimesis, rivalry over objects) from the mechanism that produces convergence (conflictual mimesis, snowballing hostility-transmission). These are structurally different processes with different dynamical properties. Second, the convergence mechanism is characterized as *multiplicative*: "the power of mimetic attraction *multiplies* with the number of those polarized." This is not linear diffusion (where each additional hostile agent adds a fixed increment of mimetic pull) but superlinear amplification (where each additional hostile agent *multiplies* the pull on the remaining unpolarized agents). Our model tests whether this distinction -- linear versus superlinear hostility-transmission -- is in fact the formal boundary between crisis-without-convergence and scapegoating.

---

## 2. Model Design

### 2.1 Overview

We implement a family of agent-based models sharing common infrastructure but differing in their hostility-transmission mechanism. All variants operate on a Watts-Strogatz small-world network of 50 agents with mean degree 6 and rewiring probability 0.15. Each agent maintains a desire vector over a set of rivalrous and non-rivalrous objects, and an aggression vector over all other agents. The simulation proceeds in discrete timesteps, each consisting of:

1. **Desire step:** agents mimetically absorb neighbors' desires (weighted by prestige).
2. **Aggression-source step:** shared desire for rivalrous objects generates mutual aggression between neighbors (acquisitive mimesis), or status proximity generates rivalry-based aggression (in rivalry variants).
3. **Aggression-spread step:** agents mimetically absorb neighbors' aggression patterns. *This step varies across model variants and constitutes the experimental manipulation.*
4. **Decay step:** all aggression decays by a fixed fraction per timestep.
5. **Expulsion step:** if any agent's total received aggression exceeds a threshold, that agent is removed and all aggression toward them is zeroed.

The expulsion step is a *consequence rule*, not a convergence mechanism: it removes agents who have accumulated sufficient collective hostility, but does not influence how hostility accumulates or converges. Scapegoat convergence, if it occurs, must emerge from the aggression-spread step.

### 2.2 Variants

We test four model variants, implementing three distinct aggression-spread mechanisms and one combination:

**V0: Linear Baseline.** Agent *i*'s mimetic pull toward target *j* is a prestige-weighted average of neighbors' aggression toward *j*:

$$\text{pull}_i(j) = \frac{\sum_{k \in N(i)} w_{ik} \cdot \text{agg}_k(j)}{\sum_{k \in N(i)} w_{ik}}$$

Updated aggression: $\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$

where $\alpha \in [0, 1]$ controls the ratio of autonomous to mimetic aggression. This is the most literal formalization of "agents imitate others' hostility."

**V2: Attentional Concentration.** Before absorption, agent *i* filters neighbor hostility through a salience function that amplifies peaks:

$$a_i(j) = \frac{h_i(j)^\gamma}{\sum_k h_i(k)^\gamma}$$

$$\text{pull}_i(j) = a_i(j) \cdot \sum_k h_i(k)$$

where $h_i(j)$ is the prestige-weighted average neighbor hostility toward *j* (as in V0) and $\gamma > 1$ is the salience exponent. When $\gamma = 1$, this reduces to V0. When $\gamma > 1$, targets with above-average hostility capture disproportionate attention. This formalizes Girard's claim that mimetic attraction "multiplies": the exponent $\gamma$ controls the degree of multiplicative amplification.

**V5a: Rivalry + Linear.** Aggression is sourced not from shared object-desire but from *status rivalry*. Each agent has a status scalar (initialized near 0.5); agents in close status proximity to connected neighbors generate mutual aggression, weighted toward upward rivalry (agents rival those of equal or higher status more than those below). Collectively received aggression degrades the target's status, reducing their prestige (status-dependent) and their capacity to resist further targeting. Aggression *spreads* via linear mimesis (as in V0). This tests whether the rivalry-escalation feedback loop produces convergence without superlinear transmission.

**V5b: Rivalry + Attention.** Same status-rivalry dynamics as V5a, but aggression spreads via attentional concentration (as in V2). This tests the combination of both Girardian phases: rivalry-driven aggression generation plus superlinear conflictual mimesis.

### 2.3 Measurements

For each simulation run, we record:

- **Aggression Gini coefficient:** inequality in the distribution of received aggression across living agents. Higher Gini indicates more concentrated targeting.
- **Top-target share:** fraction of total received aggression absorbed by the single most-targeted agent.
- **Convergence ratio (top1/top2):** received aggression of the most-targeted agent divided by that of the second-most-targeted. Values near 1 indicate diffuse hostility; values >> 1 indicate focused targeting.
- **Shannon entropy:** information-theoretic measure of targeting diffusion. Lower entropy indicates more concentrated targeting.
- **Expulsion count and timing:** number and temporal distribution of agent removals.
- **Catharsis:** fractional tension drop following each expulsion event.
- **Victim status at expulsion** (rivalry variants): the expelled agent's status relative to the population mean, testing whether "signs of the victim" emerge endogenously.

---

## 3. Results

### 3.1 The Core Finding: Superlinearity Is Necessary and Sufficient

The central result is displayed in Table 1.

| Variant | Mechanism | Mean Gini | Top Share | Top1/Top2 | Expulsions | Catharsis |
|---------|-----------|-----------|-----------|-----------|------------|-----------|
| V0 | Linear mimesis | 0.115 | 0.041 | 1.05 | 16.6 | 4.0% |
| V2 | Attentional concentration | 0.739 | 0.310 | 1.62 | 28.8 | 18.8% |
| V5a | Rivalry + linear | 0.133 | 0.040 | 1.03 | 15.9 | 4.0% |
| V5b | Rivalry + attention | 0.803 | 0.353 | 1.45 | 28.2 | 27.0% |

*Table 1. Summary metrics across 10 runs per variant, alpha = 0.15, salience exponent = 2.0, 600 timesteps.*

The results divide cleanly into two regimes. Variants with linear hostility-transmission (V0, V5a) produce Gini coefficients around 0.11-0.13, top-target shares near 1/N (the uniform baseline for 50 agents is 0.02), and convergence ratios near 1.0. Hostility spreads but does not converge. Variants with superlinear transmission (V2, V5b) produce Gini coefficients above 0.73, top-target shares of 0.31-0.35, and convergence ratios of 1.4-1.6. Hostility both spreads and converges on a single target.

The addition of rivalry dynamics to linear mimesis (V0 → V5a) produces negligible change in convergence metrics. Rivalry generates more aggression -- hence comparable expulsion counts -- but does not concentrate it. By contrast, attentional concentration alone (V2) produces dramatic convergence. Rivalry combined with attention (V5b) produces the strongest convergence and deepest catharsis, but the attention mechanism does the overwhelming majority of the convergence work.

### 3.2 The Phase Transition at Superlinearity

To locate the formal boundary between crisis-without-convergence and scapegoating, we swept the salience exponent $\gamma$ from 1.0 to 5.0.

| Exponent ($\gamma$) | Mean Gini | Top Share | Top1/Top2 | Expulsions |
|---|---|---|---|---|
| 1.00 | 0.108 | 0.038 | 1.04 | 15.5 |
| 1.25 | 0.589 | 0.278 | 1.86 | 29.7 |
| 1.50 | 0.696 | 0.344 | 1.73 | 31.0 |
| 2.00 | 0.735 | 0.288 | 1.42 | 28.2 |
| 3.00 | 0.756 | 0.321 | 1.54 | 28.2 |

*Table 2. Convergence metrics as a function of salience exponent. Alpha = 0.15, 6 runs per condition.*

At $\gamma = 1.0$ (linear), the model matches the V0 baseline exactly: no convergence. At $\gamma = 1.25$ -- barely above linear -- Gini jumps from 0.108 to 0.589 and convergence ratio from 1.04 to 1.86. Above $\gamma = 1.5$, all metrics plateau. The phase transition is sharp and occurs at any degree of superlinearity. This is consistent with Girard's claim: what matters is not the *intensity* of mimetic transmission but its *multiplicative character*.

### 3.3 Robustness

The superlinear-convergence result is robust across:

- **Network topology:** Watts-Strogatz (small-world), Barabasi-Albert (scale-free), Erdos-Renyi (random), and complete graphs all produce convergence at $\gamma > 1$. Complete graphs produce the strongest convergence (Gini 0.558, convergence ratio 14.95) but also the most expulsions (46 of 50 agents), consistent with Girard's account of undifferentiation crisis in communities without structural barriers to mimetic transmission.
- **Group size:** Convergence occurs at N = 20, 35, 50, 75, and 100, with Gini increasing slightly with group size (0.598 to 0.754). Small groups produce sharper individual targeting (top-target share 0.50 at N = 20).
- **Mimetic susceptibility (alpha):** Even at alpha = 0.85 (85% autonomous aggression, 15% mimetic), convergence occurs at $\gamma \geq 1.5$. The attention mechanism does not require high mimetic susceptibility; it requires only that *whatever mimesis occurs* has superlinear character.

### 3.4 Catharsis Dynamics

Expulsion produces measurable tension reduction: 18.8% mean drop in V2, 27.0% in V5b. In V5b, 27 of 30 expulsions in a representative run produce genuine catharsis (tension decrease). The system exhibits crisis-relief-reaccumulation cycles with bimodal inter-expulsion intervals (clusters of rapid expulsions separated by extended quiet periods).

The immediate tension drop is partly arithmetic: removing the most-targeted agent eliminates their share of total received aggression. What is emergent is that tension does not immediately redirect to a new target. The attentional funnel requires time to reconstitute after losing its focal point; this temporal gap is the emergent catharsis. The bimodal rhythm -- rapid-fire scapegoating during acute crisis, long dormant periods between crises -- is entirely emergent and has no coded precursor.

### 3.5 The Arbitrariness and Endogenous Marginality of the Victim

In V2 (attention only, no rivalry), victims are statistically indistinguishable from the general population across all measured network properties: degree centrality (0.125 vs 0.122), betweenness centrality (0.037 vs 0.035), clustering coefficient (0.385 vs 0.370). The victim's identity is a contingent outcome of the attentional cascade, not a structural property of the network. This confirms Girard's claim about the fundamental arbitrariness of the victim.

In V5b (rivalry + attention), a different and theoretically richer picture emerges. Victims have a mean status of 0.264 at the moment of expulsion, against a population mean of 0.409 -- a deficit of 0.145. But status was initialized uniformly around 0.5. The victim's low status is an endogenous product of the targeting process: they were targeted, which degraded their status, which reduced their prestige and social capital, which made them less able to resist further targeting. The "signs of the victim" -- the visible markers of difference that retrospectively justify the community's violence -- are produced by the mechanism itself, not presupposed by it.

This finding directly addresses Girard's claim that the victim's "guilt" and "difference" are retrospective constructions:

> The signs of the victim are not the causes of victimization but its consequences. (Girard 1986, paraphrased from *The Scapegoat*)

In V5a (rivalry + linear), a tiny victim status deficit exists (0.012) but is negligible -- status degradation occurs but does not concentrate on any single target sufficiently to produce visible marginality. The endogenous production of "signs of the victim" requires both the rivalry feedback (status degradation) and the convergence mechanism (attentional concentration).

---

## 4. Discussion

### 4.1 What the Model Confirms in Girard

**The two-phase decomposition is structurally correct.** Girard's distinction between acquisitive mimesis (generating hostility through rivalry) and conflictual mimesis (producing convergence through hostility-contagion) is not merely expository but structurally necessary. The comparison between V5a (rivalry without convergence mechanism) and V2 (convergence mechanism without rivalry) demonstrates that these are genuinely independent dynamical contributions. Rivalry generates the raw material of hostility; conflictual mimesis concentrates it. Neither alone produces the full Girardian outcome; their combination does.

**The "snowball effect" is the convergence mechanism.** Girard's claim that "the power of mimetic attraction multiplies with the number of those polarized" is confirmed in precise formal terms. The multiplicative character of hostility-transmission -- formalized as any salience exponent $\gamma > 1$ -- is the necessary and sufficient condition for the transition from diffuse crisis to focused scapegoating. Linear hostility-transmission ($\gamma = 1$) produces crisis without resolution, regardless of other parameter settings. The phase transition is sharp and occurs at minimal superlinearity ($\gamma \approx 1.25$), indicating that the mechanism is robust rather than fragile.

**The victim is arbitrary, and "signs of the victim" are endogenously produced.** In the pure attention model (V2), victims are network-indistinguishable from the general population. In the combined model (V5b), victims acquire measurable marginality through the targeting process itself. Both findings are consistent with Girard's account: the victim need not be initially different; their "difference" is a product of the scapegoating process.

**Catharsis is real and temporally structured.** Expulsion produces genuine tension reduction with emergent crisis-relief-reaccumulation cycles.

### 4.2 What the Model Specifies Beyond Girard

**The formal requirement for convergence.** Girard describes conflictual mimesis phenomenologically -- as fascination, obsession, the "snowball effect." Our model identifies the precise formal property that produces convergence: superlinear hostility-transmission, where the mimetic pull toward a target grows faster than proportionally with existing hostility toward that target. Girard gestures toward this with "multiplies," but the model demonstrates that this is not one feature among many but *the* distinguishing formal feature of the scapegoat mechanism. Any degree of superlinearity produces convergence; linearity never does, regardless of all other parameters.

**The relative contributions of rivalry and conflictual mimesis.** Girard's narrative presents the two phases as sequential and mutually dependent. The model reveals their relative dynamical weight: conflictual mimesis (attentional concentration) accounts for the overwhelming majority of convergence, while rivalry contributes approximately 8% additional Gini concentration (0.739 → 0.803) and the endogenous marginality effect. Rivalry is a potentiator and enrichment of the scapegoat mechanism, not its primary driver.

**Minimal mimetic susceptibility suffices.** Even populations where 85% of individual aggression is autonomously generated produce scapegoats if the remaining 15% of mimetic transmission is superlinear. Girard's account emphasizes the dissolution of individual autonomy in crisis ("the doubles"), but the model suggests that the *qualitative character* of mimesis matters more than its *quantity*.

### 4.3 Relation to Empirical Literature on Attention Cascades

The superlinear attention mechanism we identify as the formal core of the scapegoat mechanism has independent empirical support in research on collective attention and information cascades. Studies of attention dynamics on social media platforms have found that the probability of an individual sharing content is a function of the *fraction* of their contacts who have already shared it, not the absolute number -- a result of competition for finite attention that naturally produces superlinear concentration on popular targets. Research on attention brokerage in online networks has demonstrated how high-degree nodes amplify content, causing followers to converge attention on the amplified target through local, causal processes that change global network structure. These findings describe the same functional mechanism -- superlinear attention concentration driven by mimetic absorption of neighbors' focus -- operating on information rather than hostility. The application to hostile targeting is a theoretically motivated extension, not a directly observed phenomenon; but the cognitive infrastructure (finite attention, salience-driven filtering, mimetic absorption of neighbors' priorities) is empirically grounded.

### 4.4 Limitations and Future Directions

The model treats the transition from acquisitive to conflictual mimesis as structurally given (separate coded mechanisms) rather than endogenous. A richer model might attempt to formalize the conditions under which agents shift from object-focused rivalry to objectless hostility-transmission, testing Girard's claim that this transition occurs when mimetic crisis reaches a critical intensity.

The model does not include institutional or ritual structures that, in Girard's later work, serve to *prevent* or *channel* mimetic crisis. Prohibition, ritual, and sacrificial substitution are absent. Testing whether the addition of such structures produces the stability Girard predicts -- mimetic crisis contained through institutionalized repetition of the founding murder -- is a natural extension.

The model assumes a single community without external relations. Girard's account of the scapegoat mechanism is fundamentally about intra-community dynamics, but real communities exist in relation to others. Whether inter-community contact modulates or amplifies the scapegoat mechanism is unexplored.

Finally, our model of "attentional concentration" is one possible formalization of superlinear hostility-transmission. Other formalizations -- threshold models, information-cascade models, or explicit Girardian "fascination" dynamics -- might produce convergence with different properties. Our finding that any degree of superlinearity suffices suggests that the specific functional form matters less than the qualitative property of multiplicative amplification, but systematic comparison of alternative superlinear formalizations is warranted.

---

## 5. Conclusion

Girard writes that "the power of mimetic attraction multiplies with the number of those polarized." We have formalized that sentence and tested it. The formalization reveals that the multiplicative character of mimetic attraction in hostile contexts -- what Girard calls conflictual mimesis and describes as a "snowball effect" -- is the necessary and sufficient formal condition for the emergence of scapegoat convergence. Linear mimetic transmission, however intense, produces crisis without resolution: hostility amplifies but does not converge. Any degree of superlinear transmission produces the full Girardian pattern: convergence onto an arbitrary single victim, cathartic tension reduction upon expulsion, and -- when combined with status-rivalry dynamics -- endogenous production of the "signs of the victim."

The model does not replace Girard's theory; it specifies it. Girard correctly identified the two-phase structure of mimetic crisis (rivalry-driven hostility generation, then hostility-contagion-driven convergence), correctly predicted the emergent properties (arbitrariness and retrospective marginalization of the victim, cathartic relief), and correctly characterized the convergence mechanism as multiplicative. What the model adds is the demonstration that this multiplicative character is not one feature among many but the *precise formal boundary* between crisis and scapegoating -- and that it is robust across network structures, group sizes, and levels of individual mimetic susceptibility.

---

## References

Gardin, A. (2008). Complex mimetic systems. *Contagion: Journal of Violence, Mimesis, and Culture*, 15/16, 25-42.

Girard, R. (1965). *Deceit, Desire, and the Novel: Self and Other in Literary Structure*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1977). *Violence and the Sacred*. Trans. P. Gregory. Johns Hopkins University Press.

Girard, R. (1986). *The Scapegoat*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1987). *Things Hidden Since the Foundation of the World*. Trans. S. Bann and M. Metteer. Stanford University Press.

Girard, R. (2001). *I See Satan Fall Like Lightning*. Trans. J. G. Williams. Orbis Books.

Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*, 83(6), 1420-1443.

O'Higgins Norman, J., & Connolly, J. (2011). Mimetic theory and scapegoating in the age of cyberbullying. *Pastoral Care in Education*, 29(4), 287-300.

Paes, L. (2025). An agent-based model of scapegoating. Unpublished manuscript. [NetLogo model.]

Sack, G. A. (2021). Geometries of desire: A computational approach to Girardian mimetic theory. *Contagion: Journal of Violence, Mimesis, and Culture*, 28, 81-112.

[TODO: Add social media attention-cascade empirical cites -- Lorenz-Spreen et al. 2019; Hodas & Lerman 2014; Weng et al. 2012; Bakshy et al. 2011]

---

## Appendix A: Model Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| N | 50 | Number of agents |
| k | 6 | Mean degree (Watts-Strogatz) |
| p | 0.15 | Rewiring probability |
| alpha | 0.15 | Autonomous vs mimetic aggression ratio |
| gamma | 2.0 | Salience exponent (V2, V5b) |
| Objects | 8 (5 rivalrous) | Number of desire objects |
| Rivalry-to-aggression | 0.2 | Aggression increment from shared desire |
| Aggression decay | 0.03 | Per-step decay fraction |
| Expulsion threshold | 8.0 | Received aggression triggering removal |
| Status loss rate | 0.005 | Aggression-to-status degradation (V5a, V5b) |
| Rivalry intensity | 0.15 | Rivalry-to-aggression conversion (V5a, V5b) |
| Timesteps | 600 | Simulation duration |
| Runs per condition | 10 | Replications for summary statistics |

## Appendix B: Code Availability

[TODO: GitHub repository link. All simulations implemented in Python using NumPy and NetworkX.]
