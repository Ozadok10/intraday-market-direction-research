# R05 — 30-minute Markov state-transition sensitivity test (v1)

## Scope
Direct timeframe comparison with R05's 5-minute Markov analysis. SPY and QQQ cleaned regular-session one-minute OHLCV, 2008-01-01 through 2026-09-30, sourced from `Intraday_Cleaned_Datasets_v1(1).zip`. Data cleaning remains unchanged.

## Predefined construction
- Consecutive, non-overlapping clock-aligned 30-minute blocks, 09:30–10:00 through 15:30–16:00 Eastern.
- Each completed 30-minute block must contain 30 rows. Block state based on close-to-close return relative to previous completed block, 100*(close_t/close_t-1 − 1).
- DOWN if return < -0.05 percentage points; UP if return > +0.05; FLAT otherwise. **Threshold intentionally unchanged from the preceding 5-minute experiment**, so only the window length changes. This is not the prior R01 ±0.30% signal filter.
- Within-session transitions only; no cross-day transitions. Since the first interval has no previous 30-minute block close, and final interval has no following block, a normal full session yields 11 transitions.
- Periods: discovery 2008–2019, validation 2020–2023, holdout 2024–2026-09-30. Later periods were previously explored in this broader project and should not be called untouched.
- Discovery state-frequency baseline vs first-order Markov row probabilities; both use additive Laplace smoothing (+1 count per class). Predictions are frozen after training on discovery.
- Outcomes: three-class accuracy, multiclass Brier = mean sum over three classes (p - one_hot)^2, and log loss. Positive score improvements reflect relative *loss reduction*, not predictive win rate or profitability.

## Results
| ticker | evaluation | transitions | Markov accuracy | baseline accuracy | relative Brier reduction |
|---|---|---:|---:|---:|---:|
| SPY | 2020–2023 | 10,997 | 38.67% | 39.07% | +0.56% |
| SPY | 2024–2026 | 7,532 | 37.37% | 34.86% | +0.52% |
| QQQ | 2020–2023 | 11,019 | 43.20% | 43.20% | +0.18% |
| QQQ | 2024–2026 | 7,510 | 39.47% | 39.47% | +0.25% |

On the discovery sample, conditional next-UP probabilities after DOWN were 39.36% SPY and 41.50% QQQ. Compare the full three-state distribution, rather than interpreting that as probability of a profitable reversal trade.

## Limitations
- These state bands do not equal the ±0.30% qualifying-move definition used in R01–R04. At a longer horizon, ±0.05% makes the classes more balanced; comparing raw accuracy directly against the five-minute experiment without accounting for changed class prevalence is misleading.
- No day-block bootstrap confidence intervals, formal clustered hypothesis test, fee/slippage analysis, or strategy backtest conducted. Small Brier reductions should not be called statistically significant.
- Only one fixed binning scheme and first-order model; no parameter optimization. Do not read result as universal evidence against other horizons/state definitions.
- R05 clean data covers eligible sessions, not all calendar trading days, and cross-session transitions are excluded.

## Files
`R05_30min_State_Transitions_v1.csv` individual transitions; `R05_30min_Transition_Matrices_v1.csv` state counts and matrix probabilities; `R05_30min_Model_Performance_v1.csv` period summaries; `R05_30min_Annual_Performance_v1.csv` annual summaries; `run_markov_30min.py` reproducible script.

## Suggested destination
`03_Research/R05_Markov/`. New independent sensitivity study; does not replace `R05_Markov_Analysis_v1.zip`.
