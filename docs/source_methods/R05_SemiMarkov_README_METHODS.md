# R05 — 30-minute duration-conditioned state transitions (semi-Markov-inspired extension)

Source: Intraday_Cleaned_Datasets_v1(1).zip. SPY and QQQ minute bars, regular trading hours. Observations include 2008–2026-09-30; SPY years before 2008 omitted for matched-era comparability. Discover/train 2008–2019, evaluate 2020–2023 and 2024–Sep 2026. 2024–2026 is a temporal holdout for this fitted model, not completely untouched across the larger research program.

1. Group each trading session into consecutive 30-minute intervals from the 9:30 am ET open. Use first 1-minute bar's open and last 1-minute bar's close; calculate return = close/open - 1. Ignore leftover partial intervals. UP if return > 0.0005, DOWN if return < -0.0005, otherwise FLAT. Strict inequalities; values at boundaries are FLAT. No transition crosses a session boundary.
2. Consecutive run length is count of identical state windows through the current window in the same session, resetting whenever the current state changes (FLAT is itself a state). Duration bucket k is 1, 2, 3, or 4+ (all streaks of four or more pooled).
3. First-order Markov probabilities from discovery: p(j|i) = (N_ij + 1)/(N_i + 3). The simple unconditional probability: p(j) = (N_j + 1)/(N + 3).
4. Duration model: p(j|i,k) = (N_ikj + 100*p(j|i))/(N_ik+100). This prespecified 100-pseudo-observation hierarchical smoothing prevents tiny long-streak groups from producing extreme predictions. This is a duration-conditioned categorical transition estimator (semi-Markov-inspired), not a continuously timed survival hazard or fully estimated classical semi-Markov process.
5. Train once in 2008–2019; freeze state limits, buckets and smoothing before later evaluation. Compare fixed probabilities on 2020–2023 validation and 2024–2026 holdout. Primary scoring Brier (sum over three categories of squared deviations, lower is better); also log loss and three-state accuracy. Metrics evaluated across all eligible transitions. Day-cluster bootstrap (1,200 resamples, fixed seed) yields 95% percentile intervals for model forecast-score difference; positive delta indicates duration model wins.

## Caveats

- These are in-sample/descriptive duration distributions for 2008–2019 and out-of-sample *model forecasts* for later years, not actual realized trading P&L.
- Classifications are based on fixed 0.05% unscaled returns; class distributions shift with volatility regimes. This is a sensitivity limitation.
- Run length counts repeated *state classifications*, not cumulative trending distance or uninterrupted rising minute bars. A session boundary truncates streaks, and no overnight link is used.
- More complex sample-level dependencies, vendor adjustments and data-quality issues remain possible. Source cleaning report says corporate-action adjustment and price outliers are not independently certified.
- Re-run with alternative pre-registered 30-minute state thresholds, time-of-day conditioning and a true event-time survival / semi-Markov hazard as future research, while accounting for multiplicity.
- Bootstrap confidence intervals are exploratory, conditional on trained probabilities. They do not quantify uncertainty from refitting the model on alternative training samples. Repeated model/feature choices can undermine nominal confidence levels.
