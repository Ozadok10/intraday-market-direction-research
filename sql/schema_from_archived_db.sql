-- Extracted verbatim from the archived Intraday_Direction_Research_v1.db
-- Describes existing schema; does not populate data.

CREATE TABLE "discovery_observations" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "session_group" TEXT, "sample_period" TEXT, "lookback_return_pct" REAL, "forward_return_pct" REAL, "signed_forward_return_pct" REAL, "signal" INTEGER, "continuation" INTEGER, "reversal" INTEGER, "entry_open" REAL, "exit_close" REAL, "volume_eligible" INTEGER);

CREATE TABLE "earnings_month_overall" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "sample_period" TEXT, "month_group" TEXT, "qualifying_signals" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "avg_signed_move_pct" REAL, "binomial_p_unadjusted" REAL);

CREATE TABLE "holdout_observations" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "session_group" TEXT, "lookback_return_pct" REAL, "forward_return_pct" REAL, "signed_forward_return_pct" REAL, "signal" INTEGER, "continuation" INTEGER, "reversal" INTEGER, "volume_eligible" INTEGER);

CREATE TABLE "monthly_by_checkpoint" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "sample_period" TEXT, "month" INTEGER, "checkpoint_et" TEXT, "checkpoint_observations" INTEGER, "qualifying_signals" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "reversion_pct" REAL, "mean_signed_forward_pct" REAL, "median_signed_forward_pct" REAL, "continuation_mean_pct" REAL, "reversion_mean_pct" REAL, "binomial_p_unadjusted" REAL, "mean_p_unadjusted" REAL);

CREATE TABLE "monthly_overall" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "sample_period" TEXT, "month" INTEGER, "checkpoint_observations" INTEGER, "qualifying_signals" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "reversion_pct" REAL, "mean_signed_forward_pct" REAL, "median_signed_forward_pct" REAL, "continuation_mean_pct" REAL, "reversion_mean_pct" REAL, "binomial_p_unadjusted" REAL, "mean_p_unadjusted" REAL);

CREATE TABLE "move_size_overall" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "move_size_band" TEXT, "observations" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "mean_signed_forward_pct" REAL, "median_signed_forward_pct" REAL, "binomial_p_value" REAL);

CREATE TABLE "multivariable_predictions" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "signed_forward_return_pct" REAL, "year" INTEGER, "y" INTEGER, "pred_continuation_probability" REAL, "pred_label" INTEGER, "pred_correct" INTEGER);

CREATE TABLE "multivariable_summary" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "train_start" TEXT, "train_end" TEXT, "test_start" TEXT, "test_end" TEXT, "train_n" INTEGER, "test_n" INTEGER, "train_continuation_pct" REAL, "test_continuation_pct" REAL, "model_correct" INTEGER, "model_accuracy_pct" REAL, "majority_baseline_correct" INTEGER, "majority_baseline_accuracy_pct" REAL, "model_minus_baseline_pp" REAL, "model_auc" REAL, "model_brier" REAL, "model_log_loss" REAL, "confident_60_n" INTEGER, "confident_60_correct" INTEGER, "confident_60_accuracy_pct" REAL, "model_binomial_p_vs_50_unadjusted" REAL);

CREATE TABLE "quarterly_by_checkpoint" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "sample_period" TEXT, "quarter" INTEGER, "checkpoint_et" TEXT, "checkpoint_observations" INTEGER, "qualifying_signals" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "reversion_pct" REAL, "mean_signed_forward_pct" REAL, "median_signed_forward_pct" REAL, "continuation_mean_pct" REAL, "reversion_mean_pct" REAL, "binomial_p_unadjusted" REAL, "mean_p_unadjusted" REAL);

CREATE TABLE "quarterly_overall" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "sample_period" TEXT, "quarter" INTEGER, "checkpoint_observations" INTEGER, "qualifying_signals" INTEGER, "continuations" INTEGER, "reversions" INTEGER, "flat" INTEGER, "continuation_pct" REAL, "reversion_pct" REAL, "mean_signed_forward_pct" REAL, "median_signed_forward_pct" REAL, "continuation_mean_pct" REAL, "reversion_mean_pct" REAL, "binomial_p_unadjusted" REAL, "mean_p_unadjusted" REAL);

CREATE TABLE "relative_volume_events" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "lookback_return_pct" REAL, "prior_30m_volume" REAL, "prior_20_session_avg_volume" REAL, "relative_volume_30m" REAL, "volume_band" TEXT, "signed_forward_return_pct" REAL, "continuation" INTEGER, "reversal" INTEGER);

CREATE TABLE source_manifest(table_name TEXT PRIMARY KEY, source_csv TEXT NOT NULL, row_count INTEGER NOT NULL);

CREATE TABLE "validation_observations" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "session_group" TEXT, "lookback_return_pct" REAL, "forward_return_pct" REAL, "signed_forward_return_pct" REAL, "signal" INTEGER, "continuation" INTEGER, "reversal" INTEGER, "volume_eligible" INTEGER);

CREATE TABLE "volatility_audit" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "volatility_band" TEXT, "all_observations" INTEGER, "all_observations_pct" REAL, "qualifying_signals" INTEGER, "qualifying_signals_pct" REAL, "signal_rate_in_band_pct" REAL);

CREATE TABLE "volatility_events" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "lookback_return_pct" REAL, "realized_volatility_30m_pct" REAL, "volatility_band" TEXT, "band_low_upper_pct" REAL, "band_medium_upper_pct" REAL, "signed_forward_return_pct" REAL, "continuation" INTEGER, "reversal" INTEGER);

CREATE TABLE "volume_profile_events" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "lookback_return_pct" REAL, "checkpoint_previous_close" REAL, "developing_poc" REAL, "developing_val" REAL, "developing_vah" REAL, "value_area_volume_pct" REAL, "signed_poc_distance_pct" REAL, "poc_side" TEXT, "profile_position_band" TEXT, "signed_forward_return_pct" REAL, "continuation" INTEGER, "reversal" INTEGER);

CREATE TABLE "volume_profile_validation_events" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "lookback_return_pct" REAL, "checkpoint_previous_close" REAL, "developing_poc" REAL, "developing_val" REAL, "developing_vah" REAL, "value_area_volume_pct" REAL, "signed_poc_distance_pct" REAL, "poc_side" TEXT, "profile_position_band" TEXT, "signed_forward_return_pct" REAL, "continuation" INTEGER, "reversal" INTEGER);

CREATE TABLE "vwap_events" ("row_id" INTEGER PRIMARY KEY, "ticker" TEXT, "session_date" TEXT, "checkpoint_et" TEXT, "signal" INTEGER, "lookback_return_pct" REAL, "vwap_at_checkpoint" REAL, "checkpoint_previous_close" REAL, "signed_vwap_distance_pct" REAL, "vwap_position_band" TEXT, "signed_forward_return_pct" REAL, "continuation" INTEGER, "reversal" INTEGER);

CREATE VIEW all_observations AS SELECT ticker,session_date,checkpoint_et,session_group,lookback_return_pct,forward_return_pct,signed_forward_return_pct,signal,continuation,reversal,volume_eligible,'discovery_2008_2019' AS research_period FROM discovery_observations UNION ALL SELECT ticker,session_date,checkpoint_et,session_group,lookback_return_pct,forward_return_pct,signed_forward_return_pct,signal,continuation,reversal,volume_eligible,'validation_2020_2023' FROM validation_observations UNION ALL SELECT ticker,session_date,checkpoint_et,session_group,lookback_return_pct,forward_return_pct,signed_forward_return_pct,signal,continuation,reversal,volume_eligible,'holdout_2024_2026' FROM holdout_observations;

CREATE INDEX "idx_discovery_observations_event" ON "discovery_observations"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_holdout_observations_event" ON "holdout_observations"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_multivariable_predictions_event" ON "multivariable_predictions"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_relative_volume_events_event" ON "relative_volume_events"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_validation_observations_event" ON "validation_observations"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_volatility_events_event" ON "volatility_events"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_volume_profile_events_event" ON "volume_profile_events"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_volume_profile_validation_events_event" ON "volume_profile_validation_events"(ticker,session_date,checkpoint_et);

CREATE INDEX "idx_vwap_events_event" ON "vwap_events"(ticker,session_date,checkpoint_et);
