# R06 Survival Analysis — Version 2 (±0.50%)

## Purpose and version policy
This analysis **supersedes R06 v1 for the chosen 0.50% threshold**, but retains v1 unchanged as an archived sensitivity study. It does **not** replace any R05 Markov datasets or change their classification rules.

## Inputs and methodology
- `Intraday_Cleaned_Datasets_v1(1).zip` with SPY and QQQ 1-minute RTH prices, 2008 through September 2026; excluded sessions remain excluded as in cleaned source.
- At six original bar-start checkpoints (10:00, 10:30, 11:30, 13:00, 14:30, 15:30 ET), use the **close of the checkpoint's 1-minute candle** compared with the close 30 candles earlier.
- Include only events whose absolute preceding 30-minute return is at least **0.50%**. UP or DOWN defines the prior movement direction.
- Look strictly at subsequent 1-minute candles until the RTH closing bar: first **0.50% further in the same direction** is continuation; first **0.50% in the opposite direction** is reversal. Use high/low to detect touching a barrier. Whichever first touch occurs wins.
- If both barriers first hit in the same 1-minute candle, OHLC cannot determine order; treat as ambiguous censored immediately before the candle (observed twice in SPY discovery). If neither is reached before market close, censor at close. No overnight followup.
- Elapsed time is approximate minute-candle count after the anchor (the timestamp is the start of the 1-minute bar). No slippage/execution simulation.
- An event may overlap another checkpoint on the same day: **not statistically independent**. Analysis is descriptive, does not include cluster-robust confidence intervals. The periods have been explored previously; do not call the holdout pristine.

## Four outcome horizons
- **30, 60, 90 minutes:** first-touch rate by each horizon, using **only events with at least that many future one-minute bars**. Counts vary between horizons; do not compare percentages as though identical samples.
- **EOD:** first-touch type over entire remaining trading session. Different checkpoints have different remaining observation lengths, so interpretation must be stratified by checkpoint when comparing time-dependent outcomes.
- **Separate end-of-day close:** where the actual session closes compared with the checkpoint anchor price, regardless of which first-touch occurred earlier. `eod_signed_return_pct` is positive if close moves **in the prior-move direction**; negative if opposite. `eod_close_threshold_state` = CONTINUATION for signed >=+0.50%, REVERSAL for signed <=−0.50%, otherwise WITHIN_BARRIERS; `eod_close_sign_state` = CONTINUATION for signed >0, REVERSAL for signed <0, UNCHANGED for 0. This is a *different measure* from first touch, and the two should never be added.
- Competing-risks cumulative-incidence curves use an Aalen–Johansen estimator; at-risk counts account for right censoring (which can depend on checkpoint time).

## Tableau/SQL layout
Use each file **as a separate logical data source** (or SQL table), because each has a different grain. Do not join group summaries to event-level records without explicit aggregate keys.

- `r06_v2_checkpoint_events.csv`: 1 record per qualifying checkpoint event. Fields for first-touch outcome, elapsed minutes, full RTH EOD close and signed return.
- `r06_v2_first_touch_horizons.csv`: 1 row per `(symbol, period, previous_move_direction, horizon)`. Rate columns are decimal [0,1]; format as percentage in Tableau.
- `r06_v2_competing_risks_curves.csv`: 1 row per `(symbol, period, previous_move_direction, elapsed_minutes)`; render CIF line charts.
- `r06_v2_eod_close_summary.csv`: 1 row per `(symbol, period, previous_move_direction)`; real EOD closing direction and mean/median return, ±0.5% close-state breakdown.
- `r06_v2_group_summary.csv`: 1 row per `(symbol, period, previous_move_direction)`; raw first-touch and censor counts until EOD.
- `r06_v2_dashboard_ready.sqlite`: equivalent five relational tables, same names as CSV stems.
- `run_r06_v2.py`: independently reproducible script; default expected source is `/mnt/data/Intraday_Cleaned_Datasets_v1(1).zip` (or use `--source PATH`). Requires numpy and pandas.

## Limits and next validation
This study measures **first touch of price barriers and price at the close**; it does not measure the demise of continuous directional trends, 0.50% strategy profitability, bid-ask execution, or an optimized trading model. Before publishing strong differences, complete day-clustered bootstrap confidence intervals and time-of-day standardized analysis. Small samples, especially SPY holdout after UP moves (51), limit inference.
