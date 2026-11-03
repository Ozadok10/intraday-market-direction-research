# R01 — Six-Checkpoint Intraday Momentum vs Reversion (v1)

## Scope
Discovery ONLY (2008-01-01 through 2019-12-31). Input: previously cleaned SPY and QQQ research bars v3 in `Intraday_Research_Eligibility_v3.zip`. No validation or holdout years were tested. Only full 390-minute, price-eligible sessions are included. Results are price-only; zero-volume day flag is preserved but does not block price analysis.

## Predeclared checkpoints and bins
10:00 and 10:30 ET = opening; 11:30 and 13:00 ET = midday; 14:30 and 15:30 ET = closing.
Each uses 30 one-minute bars for a backward movement and 30 one-minute bars for forward performance. Because bar timestamps indicate bar start, backward return is (close of last lookback bar / close of first lookback bar - 1), as in the prior discovery engine. Forward return is (close of last forward bar / open of first forward bar - 1). These conventions are carried over for comparability. Note that the backward calculation is close-to-close across 29 elapsed minutes, not precisely a 30-minute open-to-close return; if we decide to revise, that becomes a *new methodology version* and must be applied consistently to all checkpoints.

Threshold is backward return >= +0.30% (up), <= -0.30% (down), else neutral. `signed_forward_return_pct` = forward return times signal direction (+1 up, -1 down). Positive signed return = continuation, negative = reversal, zero = flat. Pct columns are in percent units, e.g. 0.05 means five basis points. All event-level records (including neutrals) are kept in the event file. Summary and annual tables contain only qualified directional signals. Checkpoint analyses are not independent across an entire day, so simple standard errors are descriptive only, not valid independent-event inferential p-values.

## Session eligibility and exclusions
Full-session days in the discovery range: SPY 2,992; QQQ 2,991. SPY checkpoint rows: 17,952, directional signals 2,490; QQQ: 17,946, directional signals 3,553. Three-phase bins are labels, not uninterrupted full-session return measurements. Early-close days are not evaluated in this six-checkpoint discovery because six checks require all regular trading hours.

## Key descriptive results
Average signed 30-minute forward return (SPY / QQQ):
- 10:00: -0.013368% / +0.008127%
- 10:30: +0.000221% / +0.015537%
- 11:30: +0.020713% / +0.008876%
- 13:00: -0.043906% / -0.019662%
- 14:30: -0.001700% / -0.013862%
- 15:30: +0.088911% / +0.062262%

Interpretation: largest positive means in the 15:30 checkpoint but this is not evidence of statistical significance or tradable edge. Both tickers' 13:00 means negative, but other midday bins have positive means. No cost/slippage or trade feasibility included; broad trading conclusions are premature.

## Flat SQL-ready tables
- `R01_Six_Checkpoint_Events_v1.csv`: one row per ticker/date/checkpoint, including neutral periods. Composite unique key = (ticker, session_date, checkpoint_et).
- `R01_Six_Checkpoint_Summary_v1.csv`: qualifying signal aggregates by ticker and checkpoint, phase group, and ALL. Fields `checkpoint_or_group` and `signal_group` specify grouping.
- `R01_Six_Checkpoint_Annual_v1.csv`: qualifying results by ticker/year/session group.
- `R01_Run_Six_Checkpoints_v1.py`: reproducible Python script referencing the archived eligibility v3 package in /mnt/data. Adjust the source path on your computer if necessary.

All outputs are descriptive, not tested for clustered statistical significance yet. Next step is year-by-year consistency and dependence-aware uncertainty, using only discovery before moving to prespecified validation/holdout.

Save package and extracted outputs to: `03_Research`.
