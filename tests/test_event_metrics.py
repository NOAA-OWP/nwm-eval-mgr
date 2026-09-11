from unittest.mock import patch

import numpy as np
import pandas as pd

from nwm_eval.metric_functions import event_based_metrics


@patch("nwm_metrics.event_metric_functions.preprocess_series")
@patch("nwm_metrics.event_metric_functions.split_into_valid_chunks")
@patch("nwm_metrics.event_metric_functions.identify_events")
@patch("nwm_metrics.event_metric_functions.merge_short_events")
@patch("nwm_metrics.event_metric_functions.separate_compound_events")
@patch("nwm_metrics.event_metric_functions.pair_events")
@patch("nwm_metrics.event_metric_functions.validate_events")
@patch("nwm_metrics.event_metric_functions.get_event_peaks")
@patch("nwm_metrics.event_metric_functions.plot_event_timeseries")
@patch("nwm_metrics.event_metric_functions.compute_event_metrics")
def test_event_based_metrics_happy_path(
    mock_compute,
    mock_plot,
    mock_get_peaks,
    mock_validate,
    mock_pair,
    mock_separate,
    mock_merge,
    mock_identify,
    mock_split,
    mock_preprocess,
):
    """Test event_based_metrics happy path."""
    # synthetic hourly series
    index = pd.date_range("2020-01-01", periods=24, freq="h")

    y_true = pd.Series(np.arange(24), index=index)
    y_pred = pd.Series(np.arange(24) + 1, index=index)

    # detected events
    detected_events = pd.DataFrame(
        {
            "start": [index[2]],
            "end": [index[10]],
        }
    )

    # paired events now require obs/mod start/end columns
    paired_events = pd.DataFrame(
        {
            "obs_start": [index[2]],
            "obs_end": [index[10]],
            "mod_start": [index[3]],
            "mod_end": [index[11]],
        }
    )

    # get_event_peaks output must contain peak info
    peaks_all = pd.DataFrame(
        {
            "obs_peak": [20.0],
            "mod_peak": [21.0],
            "obs_peak_time": [index[5]],
            "mod_peak_time": [index[6]],
        }
    )

    metrics = {
        "peak_bias": 1.0,
        "ptime_err": 2.0,
        "event_bias": 3.0,
    }

    # configure mocks
    mock_preprocess.side_effect = [y_true, y_pred]
    mock_split.return_value = [y_true]

    mock_identify.return_value = detected_events
    mock_merge.return_value = detected_events
    mock_separate.return_value = detected_events

    mock_pair.return_value = paired_events

    mock_validate.return_value = True

    mock_get_peaks.return_value = peaks_all

    mock_compute.return_value = metrics

    mock_plot.return_value = None

    # run
    result = event_based_metrics(
        y_true,
        y_pred,
        plot=False,
    )

    # verify output
    assert result == {
        "PKBIAS": 1.0,
        "PKTE": 2.0,
        "EVBIAS": 3.0,
    }

    # verify helper calls
    assert mock_identify.call_count == 2
    assert mock_merge.call_count == 2
    assert mock_separate.call_count == 2

    mock_pair.assert_called_once()
    mock_get_peaks.assert_called_once()
    mock_compute.assert_called_once()


def test_event_based_metrics_all_nan():
    """Test the event_based_metrics function with all NaN values in the input series, which should result in NaN metrics."""
    index = pd.date_range("2020-01-01", periods=24, freq="h")

    y_true = pd.Series(np.nan, index=index)
    y_pred = pd.Series(np.nan, index=index)

    result = event_based_metrics(y_true, y_pred)

    assert np.isnan(result["PKBIAS"])
    assert np.isnan(result["PKTE"])
    assert np.isnan(result["EVBIAS"])


@patch("nwm_metrics.event_metric_functions.identify_events")
def test_event_based_metrics_no_observed_events(mock_identify):
    """Test the event_based_metrics function when there are no observed events, which should result in NaN metrics."""
    index = pd.date_range("2020-01-01", periods=24, freq="h")

    y_true = pd.Series(np.arange(24), index=index)
    y_pred = pd.Series(np.arange(24), index=index)

    # observations: no events
    mock_identify.side_effect = [
        pd.DataFrame(),  # obs
        pd.DataFrame(),  # mod
    ]

    result = event_based_metrics(y_true, y_pred)

    assert np.isnan(result["PKBIAS"])
    assert np.isnan(result["PKTE"])
    assert np.isnan(result["EVBIAS"])


@patch("nwm_metrics.event_metric_functions.compute_event_metrics")
@patch("nwm_metrics.event_metric_functions.pair_events")
@patch("nwm_metrics.event_metric_functions.separate_compound_events")
@patch("nwm_metrics.event_metric_functions.identify_events")
def test_event_based_metrics_no_paired_events(
    mock_identify,
    mock_separate,
    mock_pair,
    mock_compute,
):
    """Test the event_based_metrics function when there are identified events but no paired events, which should result in NaN PKBIAS and PKTE, and EVBIAS should not be computed."""
    index = pd.date_range("2020-01-01", periods=24, freq="h")

    y_true = pd.Series(np.arange(24), index=index)
    y_pred = pd.Series(np.arange(24), index=index)

    detected = pd.DataFrame(
        {
            "start": [index[2]],
            "end": [index[10]],
        }
    )

    separated = pd.DataFrame(
        {
            "start": [index[2]],
            "end": [index[10]],
            "peak": [index[5]],
            "peak_value": [20.0],
        }
    )

    mock_identify.return_value = detected
    mock_separate.return_value = separated

    # No paired events
    mock_pair.return_value = pd.DataFrame()

    result = event_based_metrics(y_true, y_pred)

    assert np.isnan(result["PKBIAS"])

    mock_compute.assert_not_called()
