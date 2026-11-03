# Intraday Market Direction Research

**Can historical market patterns and technical indicators predict intraday direction in SPY and QQQ?**

This research examines whether short-term price behavior and widely used market indicators offer reliable evidence of momentum continuation or mean reversion. Rather than assuming a profitable signal exists, the project measures outcomes against simple benchmarks and evaluates how findings vary across market conditions.

**Tools:** Python · SQL/SQLite · pandas · Statistical analysis · Tableau

## Research approach

- Analyze SPY and QQQ intraday prices at predefined checkpoints, including out-of-sample and final-holdout evaluations.
- Examine technical conditions including VWAP and relative volume.
- Explore directional state transitions with Markov and semi-Markov methods.
- Study time to price-threshold events using survival-style first-touch analysis.
- Compare prediction quality with baseline expectations, with attention to sample size and limitations.

## Key finding

Across the tested conditions, historical patterns and common technical indicators showed **limited reliable predictive advantage** for short-term continuation versus mean reversion. This is a result about the *specific tests performed*, not a claim that all technical indicators are ineffective.

## Explore the work

| Material | Location |
|---|---|
| Python analysis | [`src/`](src/) |
| SQLite schema | [`sql/`](sql/) |
| Selected result tables | [`data/processed/`](data/processed/) |
| Method details | [`docs/methodology.md`](docs/methodology.md) |
| Data and reproduction notes | [`docs/reproducibility.md`](docs/reproducibility.md) |
| Interactive Tableau dashboard | Link to be added when published |

## Research scope and limitations

These are historical analyses, not a production trading system. Findings depend on the defined checkpoints, market regimes, input data, and evaluation choices. Markov and semi-Markov implementations are **not** a controlled head-to-head test because their state definitions differ. Raw licensed minute bars and the populated SQLite database are not redistributed; selected scripts may require separate authorized input data. The exploratory multivariable model is omitted here because its full original input set was unavailable for reproducibility testing.

## Data

Historical SPY and QQQ intraday prices from the original private research archive. Refer to the methodology notes for study-specific date coverage and definitions. The included CSVs are selected summaries, not a complete reproduction dataset.
