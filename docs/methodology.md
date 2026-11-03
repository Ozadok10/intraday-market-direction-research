# Methodology at a glance

This repository brings together distinct experiments. Each has its own definitions and sample, as explained in the original methods files under [`source_methods/`](source_methods/).

1. **Checkpoint study (R01).** Tests predeclared intraday checkpoints using backward price changes and subsequent forward outcomes, then evaluates discovery, out-of-sample, and final-holdout periods. The original study uses ±0.30% backward-movement thresholds and a 30-bar forward window. See [R01 methods](source_methods/R01_Six_Checkpoint_README_v1.md).
2. **Indicator studies (R04).** Evaluates conditional outcomes for VWAP and relative volume; do not interpret descriptive differences as automatically tradable signals.
3. **Markov and semi-Markov (R05).** Examines transition probabilities and duration-related behavior. These studies use differing state definitions, so observed performance differences cannot be attributed solely to duration conditioning. See [Markov methods](source_methods/R05_30min_Methodology_and_Findings_v1.md) and [semi-Markov methods](source_methods/R05_SemiMarkov_README_METHODS.md).
4. **First-touch horizons (R06).** Examines the time to specified subsequent price thresholds. See [R06 methods](source_methods/R06_v2_README.md).

**Interpretation:** Outcomes are specific to the stated samples and procedures. The evidence does not establish a robust general-purpose directional trading edge.
