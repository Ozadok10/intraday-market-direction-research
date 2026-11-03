# Reproducibility and data availability

The selected original research scripts were tested previously against private, archived inputs: eight executed and 28 regenerated CSVs matched corresponding archived outputs byte-for-byte. This does **not** mean a fresh clone of this repository alone can rerun the full analysis.

- Install dependencies listed in `requirements.txt` in an appropriate Python environment (versions are not pinned).
- Scripts may expect private research archives or data paths. `INTRADAY_WORKDIR` is supported by the portability-edited scripts; review each script's inputs before running.
- Public files include representative summary CSVs and database *schema*, but not raw market minute bars or the populated SQLite database.
- An exploratory multivariable script is deliberately excluded because a required original event-level input was unavailable for verification.
- Checkpoint results are observational; overlapping observations and data reuse need care when interpreting uncertainty.

This repository emphasizes transparent research code and inspectable outputs rather than claiming a one-command, fully self-contained replication.
