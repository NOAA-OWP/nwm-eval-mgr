"""Functions to compute event-based metrics.

Functions:
    - identify_events: Conduct first-round event detection using hydrotools.events.event_detection.
    - separate_compound_events: Separate compound/multi-peak events into single-peak events.
    - pair_events: One-to-one pairing of observed and model events with optional virtual events.
    - compute_event_metrics: Compute event-based metrics given paired observed and model events.
    - preprocess_series: Resample to hourly and interpolate short gaps.
    - split_into_valid_chunks: Split time series into continuous NaN-free chunks.
    - plot_event_timeseries: Plot observed and simulated streamflow time series with event peak markers.
    - validate_events: Validate event chronology and non-overlap.
    - event_based_metrics: Compute event-based metrics: PKBIAS, PKTE, EVBIAS. Optionally, plot time series with event markers.
    - get_event_peaks: Get observed and modeled event peaks.

"""

import datetime as dt
import logging
import warnings
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hydrotools.events.event_detection import decomposition as ev

warnings.simplefilter(action="ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

__all__ = [
    "identify_events",
    "separate_compound_events",
    "pair_events",
    "compute_event_metrics",
    "preprocess_series",
    "split_into_valid_chunks",
    "plot_event_timeseries",
    "validate_events",
    "event_based_metrics",
    "get_event_peaks",
]


def identify_events(
    data: pd.Series,
    halflife: str = "6h",
    window: str = "7d",
    minimum_event_duration: str = "6h",
    start_radius: str = "6h",
) -> pd.DataFrame:
    """Conduct first-round event detection using hydrotools.events.event_detection.

    Args:
        data: Streamflow time series.
        halflife: Smoothing parameter for event detection.
        window: Rolling search window for event detection.
        minimum_event_duration: Minimum allowed event duration.
        start_radius: Search radius used to identify event starts.

    Returns:
        DataFrame containing:
            - start
            - end
            - peak
            - peak_value

    """
    events = ev.list_events(
        data,
        halflife=halflife,
        window=window,
        minimum_event_duration=minimum_event_duration,
        start_radius=start_radius,
    )

    if events.empty:
        return events

    event_slices = [
        data.loc[event.start : event.end] for event in events.itertuples(index=False)
    ]

    events = events.copy()
    events["peak"] = [s.idxmax() for s in event_slices]
    events["peak_value"] = [s.max() for s in event_slices]

    return events


def merge_short_events(
    events: pd.DataFrame,
    data: pd.Series,
    minimum_event_duration: str = "6h",
) -> pd.DataFrame:
    """Merge events shorter than the minimum duration with the nearest neighboring event.

    Args:
        events (pd.DataFrame): Event dataframe containing: start, end

        data (pd.Series): Original streamflow series.

        minimum_event_duration (str): Minimum allowed duration.

    Returns:
        pd.DataFrame: updated event dataframe.

    """
    if events.empty:
        return events.copy()

    min_duration = pd.Timedelta(minimum_event_duration)
    events = events.copy().sort_values("start").reset_index(drop=True)

    # Iteratively merge short events
    changed = True

    while changed:
        changed = False

        durations = events["end"] - events["start"]
        short_idx = durations[durations < min_duration].index

        if len(short_idx) == 0:
            break

        i = short_idx[0]

        # Case 1: only one event
        if len(events) == 1:
            break

        # Determine merge target
        if i == 0:
            # merge with next
            merge_into = 1

        elif i == len(events) - 1:
            # merge with previous
            merge_into = i - 1

        else:
            # compare temporal gaps
            prev_gap = events.loc[i, "start"] - events.loc[i - 1, "end"]
            next_gap = events.loc[i + 1, "start"] - events.loc[i, "end"]
            merge_into = i - 1 if prev_gap <= next_gap else i + 1

        # Merge events
        target = min(i, merge_into)
        source = max(i, merge_into)

        new_start = min(
            events.loc[target, "start"],
            events.loc[source, "start"],
        )

        new_end = max(
            events.loc[target, "end"],
            events.loc[source, "end"],
        )

        # recompute peak using original data
        segment = data.loc[new_start:new_end]

        events.loc[target, "start"] = new_start
        events.loc[target, "end"] = new_end
        events.loc[target, "peak"] = segment.idxmax()
        events.loc[target, "peak_value"] = segment.max()

        # remove merged row
        events = events.drop(index=source).reset_index(drop=True)

        changed = True

    return events


def separate_compound_events(
    events: pd.DataFrame,
    data: pd.Series,
) -> pd.DataFrame:
    """Separate compound/multi-peak events into single-peak events.

    Args:
        events: Events detected by ``event_detection()``.
            Must contain columns:
                - start
                - end

        data: Original streamflow time series.

    Returns:
        DataFrame containing decomposed single-peak events with columns:
            - start
            - end
            - peak
            - peak_value

    """
    # Build working dataframe
    df_data = pd.DataFrame(index=data.index)
    df_data["value"] = data
    df_data["smooth"] = df_data["value"].ewm(halflife="6h", times=df_data.index).mean()

    decomposed_events = []

    pad = dt.timedelta(hours=6)
    peak_shift = dt.timedelta(hours=12)
    event_gap = dt.timedelta(hours=1)

    for event in events.itertuples(index=False):
        # Extract event window with padding
        window = df_data.loc[event.start - pad : event.end + pad].copy()

        smooth = window["smooth"]

        # Detect turning points (local maxima)
        turning_points = (
            (smooth.shift(-2) < smooth.shift(-1))
            & (smooth.shift(-1) < smooth)
            & (smooth.shift(1) < smooth)
            & (smooth.shift(2) < smooth.shift(1))
        )

        tp_times = window.index[turning_points]

        # Map turning points back to original series peaks
        peak_times = []
        for tp_time in tp_times:
            peak_time = df_data["value"].loc[tp_time - peak_shift : tp_time].idxmax()

            if event.start < peak_time < event.end:
                peak_times.append(peak_time)

        # Remove duplicates while preserving order
        peak_times = list(dict.fromkeys(peak_times))

        # Determine event boundaries
        start_times = [event.start]

        for left_peak, right_peak in zip(peak_times[:-1], peak_times[1:]):
            split_time = df_data["value"].loc[left_peak:right_peak].idxmin()
            start_times.append(split_time)

        end_times = [t - event_gap for t in start_times[1:]] + [event.end]

        # Keep only valid events
        valid_events = [
            (start, end) for start, end in zip(start_times, end_times) if start < end
        ]

        # Recompute peaks for each sub-event
        for start, end in valid_events:
            event_slice = df_data["value"].loc[start:end]

            decomposed_events.append(
                {
                    "start": start,
                    "end": end,
                    "peak": event_slice.idxmax(),
                    "peak_value": event_slice.max(),
                }
            )

    return pd.DataFrame(decomposed_events)


def pair_events(
    events_obs: pd.DataFrame,
    events_mod: pd.DataFrame,
    threshold: float,
    virtual_strategy: str = "obs",
) -> pd.DataFrame:
    """One-to-one pairing of observed and model events with optional virtual events.

    For unmatched observed events, can optionally create virtual model events with same start/end as observed to avoid
    penalizing model events below threshold. Similarly for unmatched model events. The virtual_strategy parameter
    controls which virtual events to create.

    Args:
        events_obs : pd.DataFrame
            Observed events with columns: start, end, peak_value

        events_mod : pd.DataFrame
            Model events with columns: start, end, peak_value

        threshold : float
            Only events with peak_value >= threshold are paired.

        virtual_strategy : str
            Controls handling of unmatched events:
            - "none": no virtual events
            - "obs": virtual model window for unmatched observed events
            - "mod": virtual observed window for unmatched model events
            - "both": apply both

    Returns:
        pd.DataFrame with columns:
            obs_start, obs_end, mod_start, mod_end, status

    """
    if virtual_strategy not in {"none", "obs", "mod", "both"}:
        raise ValueError(f"Invalid virtual_strategy: {virtual_strategy}")

    # Filter observed events by threshold
    obs = events_obs.loc[events_obs["peak_value"] >= threshold].copy()
    mod = events_mod.copy()

    obs_start = obs["start"].to_numpy()
    obs_end = obs["end"].to_numpy()

    mod_start = mod["start"].to_numpy()
    mod_end = mod["end"].to_numpy()

    paired_mod = np.zeros(len(mod), dtype=bool)

    rows = []

    # OBSERVED → MODEL matching (one-to-one)
    for i in range(len(obs)):
        available = ~paired_mod

        overlap = np.maximum(obs_start[i], mod_start[available]) < np.minimum(
            obs_end[i], mod_end[available]
        )

        matched_idx = np.where(available)[0][overlap]

        if matched_idx.size > 0:
            # choose best overlap match
            overlap_duration = np.minimum(
                obs_end[i], mod_end[matched_idx]
            ) - np.maximum(obs_start[i], mod_start[matched_idx])

            best = matched_idx[np.argmax(overlap_duration)]
            paired_mod[best] = True

            rows.append(
                {
                    "obs_start": obs_start[i],
                    "obs_end": obs_end[i],
                    "mod_start": mod_start[best],
                    "mod_end": mod_end[best],
                    "status": "paired",
                }
            )

        else:
            if virtual_strategy in {"obs", "both"}:
                rows.append(
                    {
                        "obs_start": obs_start[i],
                        "obs_end": obs_end[i],
                        "mod_start": obs_start[i],
                        "mod_end": obs_end[i],
                        "status": "virtual_obs",
                    }
                )
            else:
                rows.append(
                    {
                        "obs_start": obs_start[i],
                        "obs_end": obs_end[i],
                        "mod_start": pd.NaT,
                        "mod_end": pd.NaT,
                        "status": "missed",
                    }
                )

    # UNMATCHED MODEL EVENTS (false alarms / virtual_mod)
    remaining_mod = mod.loc[~paired_mod]

    # keep only events above threshold (if any)
    remaining_mod = remaining_mod.loc[remaining_mod["peak_value"] >= threshold]

    for e in remaining_mod.itertuples(index=False):
        if virtual_strategy in {"mod", "both"}:
            rows.append(
                {
                    "obs_start": e.start,
                    "obs_end": e.end,
                    "mod_start": e.start,
                    "mod_end": e.end,
                    "status": "virtual_mod",
                }
            )
        else:
            rows.append(
                {
                    "obs_start": pd.NaT,
                    "obs_end": pd.NaT,
                    "mod_start": e.start,
                    "mod_end": e.end,
                    "status": "false_alarm",
                }
            )

    events = pd.DataFrame(rows)

    if events.empty:
        return events

    # sort events by observed start time, then model start time (with NaT sorted at the end)
    sort_key = events["obs_start"].fillna(events["mod_start"])

    events = (
        events.assign(_sort=sort_key)
        .sort_values("_sort")
        .drop(columns="_sort")
        .reset_index(drop=True)
    )

    # Ensure no overlap between paired events by shifting start times if needed
    for i in range(1, len(events)):
        prev = events.iloc[i - 1]
        curr = events.iloc[i]

        # fix obs overlap
        if pd.notna(curr.obs_start) and pd.notna(prev.obs_end):
            if curr.obs_start <= prev.obs_end:
                shift = prev.obs_end - curr.obs_start + pd.Timedelta("1h")
                events.at[curr.name, "obs_start"] += shift
                events.at[curr.name, "obs_end"] += shift

        # fix mod overlap similarly if needed
        if pd.notna(curr.mod_start) and pd.notna(prev.mod_end):
            if curr.mod_start <= prev.mod_end:
                shift = prev.mod_end - curr.mod_start + pd.Timedelta("1h")
                events.at[curr.name, "mod_start"] += shift
                events.at[curr.name, "mod_end"] += shift

    return events.reset_index(drop=True)


def get_event_peaks(
    event_pairs: pd.DataFrame,
    data_obs: pd.Series,
    data_mod: pd.Series,
) -> pd.DataFrame:
    """Get observed and modeled event peaks.

    Args:
        event_pairs: DataFrame containing paired observed and modeled events
        data_obs: Series containing observed data
        data_mod: Series containing modeled data

    Returns:
        DataFrame with columns: obs_peak_time, obs_peak, mod_peak_time, mod_peak, obs_event_volume, mod_event_volume

    """
    peaks = []

    for e in event_pairs.itertuples(index=False):
        # Observed event
        if pd.notna(e.obs_start) and pd.notna(e.obs_end):
            obs = data_obs.loc[e.obs_start : e.obs_end]

            if len(obs) > 0:
                obs_peak_time = obs.idxmax()
                obs_peak = obs.max()
                obs_volume = obs.sum()
            else:
                obs_peak_time = pd.NaT
                obs_peak = np.nan
                obs_volume = np.nan

        else:
            obs_peak_time = pd.NaT
            obs_peak = np.nan
            obs_volume = np.nan

        # Modeled event
        if pd.notna(e.mod_start) and pd.notna(e.mod_end):
            mod = data_mod.loc[e.mod_start : e.mod_end]

            if len(mod) > 0:
                mod_peak_time = mod.idxmax()
                mod_peak = mod.max()
                mod_volume = mod.sum()
            else:
                mod_peak_time = pd.NaT
                mod_peak = np.nan
                mod_volume = np.nan

        else:
            mod_peak_time = pd.NaT
            mod_peak = np.nan
            mod_volume = np.nan

        peaks.append(
            {
                "obs_peak_time": obs_peak_time,
                "obs_peak": obs_peak,
                "mod_peak_time": mod_peak_time,
                "mod_peak": mod_peak,
                "obs_event_volume": obs_volume,
                "mod_event_volume": mod_volume,
            }
        )

    return pd.DataFrame(peaks)


def compute_event_metrics(
    peaks: pd.DataFrame,
    aggregation: str = "mean",
) -> Dict[str, float]:
    """Compute event-based metrics given paired observed and model events.

    Given the event peaks identified, compute the three event-based metrics (peak bias, peak timing error,
    event volume bias). Return either the mean or median of metrics calculated for all events.

    Args:
        peaks: DataFrame containing event peaks and volumes from get_event_peaks()
        aggregation: aggregation method (mean or median) for metrics calculated for all events

    Returns:
        Dictionary with keys "peak_bias", "ptime_err", and "event_bias" containing the corresponding metric values.

    """
    if peaks.empty:
        return {
            "peak_bias": np.nan,
            "ptime_err": np.nan,
            "event_bias": np.nan,
        }

    # Peak magnitude error
    peak_error = np.where(
        peaks["obs_peak"] == 0,
        np.nan,
        np.abs(peaks["mod_peak"] - peaks["obs_peak"]) / peaks["obs_peak"] * 100,
    )

    # Peak timing error
    timing_error = np.abs(
        (peaks["mod_peak_time"] - peaks["obs_peak_time"]) / np.timedelta64(1, "h")
    )

    # Event volume bias
    event_bias = np.where(
        peaks["obs_event_volume"] == 0,
        np.nan,
        np.abs(peaks["mod_event_volume"] - peaks["obs_event_volume"])
        / peaks["obs_event_volume"]
        * 100,
    )

    if aggregation == "mean":
        peak_bias = np.nanmean(peak_error)
        ptime_err = np.nanmean(timing_error)
        event_bias = np.nanmean(event_bias)

    elif aggregation == "median":
        peak_bias = np.nanmedian(peak_error)
        ptime_err = np.nanmedian(timing_error)
        event_bias = np.nanmedian(event_bias)

    else:
        raise ValueError(f"Unknown aggregation for event-based metrics: {aggregation}")

    return {
        "peak_bias": peak_bias,
        "ptime_err": ptime_err,
        "event_bias": event_bias,
    }


def preprocess_series(y: pd.Series) -> pd.Series:
    """Resample to hourly and interpolate short gaps.

    Resample the input series to hourly frequency using forward fill, then linearly interpolate gaps of up to 5 hours in length. This ensures a continuous hourly time series for event detection while avoiding excessive interpolation over long gaps.

    Args:
        y: Input time series with arbitrary frequency and potential missing values.

    Returns:
        A time series resampled to hourly frequency with short gaps interpolated.

    """
    return (
        y.copy()
        .resample("h")
        .first()
        .interpolate(method="linear", limit=5, limit_direction="both")
    )


def split_into_valid_chunks(y: pd.Series, min_len: int = 10):
    """Split time series into continuous NaN-free chunks.

    Args:
        y: Input time series with potential missing values.
        min_len: Minimum length of chunks to retain.

    Returns:
        A list of continuous NaN-free chunks with length >= min_len.

    """
    chunks = np.split(y, np.where(np.isnan(y))[0])
    chunks = [c[~np.isnan(c)] for c in chunks if not isinstance(c, np.ndarray)]

    return [c for c in chunks if len(c) >= min_len]


def plot_event_timeseries(
    y_true: pd.Series,
    y_pred: pd.Series,
    events_obs: pd.DataFrame,
    events_sim: pd.DataFrame,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    threshold: Optional[float] = None,
    threshold_unit: Optional[str] = "m3/s",
    plot_filename: Optional[str] = None,
):
    """Plot observed and simulated streamflow time series with event peak markers.

    Args:
        y_true: observed streamflow series
        y_pred: simulated streamflow series
        events_obs: observed events with columns "start", "end", "peak", "peak_value"
        events_sim: simulated events with columns "start", "end", "peak", "peak_value"
        start_time: optional start time to subset the series for plotting
        end_time: optional end time to subset the series for plotting
        threshold: optional event threshold to plot as a horizontal line
        plot_filename: optional filename to save the plot

    Returns:
        None (saves plot to file if plot_filename is provided)

    """
    # Subset time range
    if start_time is not None:
        y_true = y_true.loc[start_time:]
        y_pred = y_pred.loc[start_time:]

    if end_time is not None:
        y_true = y_true.loc[:end_time]
        y_pred = y_pred.loc[:end_time]

    fig, ax = plt.subplots(figsize=(16, 6))

    # Plot hydrographs
    ax.plot(
        y_true.index,
        y_true.values,
        label="Observed",
        linewidth=2,
    )

    ax.plot(
        y_pred.index,
        y_pred.values,
        label="Simulated",
        linewidth=2,
        alpha=0.8,
    )

    # Plot observed event peaks
    for _, event in events_obs.iterrows():
        if event["peak"] not in y_true.index:
            continue

        ax.scatter(
            event["peak"],
            y_true.loc[event["peak"]],
            s=80,
            marker="o",
            facecolors="none",
            edgecolors="black",
            linewidths=2,
            label="Obs peak",
        )

    # Plot simulated event peaks
    for _, event in events_sim.iterrows():
        if event["peak"] not in y_pred.index:
            continue

        ax.scatter(
            event["peak"],
            event["peak_value"],
            s=120,
            marker="x",
            linewidths=2,
            label="Sim peak",
        )

    # Plot threshold line if provided
    if threshold is not None:
        ax.axhline(
            y=threshold,
            color="gray",
            linestyle="--",
            label=f"Event threshold: {threshold} {threshold_unit}",
        )

    # Clean duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()

    unique = dict(zip(labels, handles))

    ax.legend(
        unique.values(),
        unique.keys(),
        loc="upper left",
    )

    # Formatting
    ax.set_title("Observed and Simulated Streamflow Events")
    ax.set_xlabel("Time")
    ax.set_ylabel("Streamflow")

    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if plot_filename is not None:
        plt.savefig(plot_filename, dpi=300)


def validate_events(events: pd.DataFrame) -> bool:
    """Validate event chronology and non-overlap.

    Args:
        events: DataFrame containing event start and end times with columns "start" and "end".

    Returns:
        bool: True if events are valid, False otherwise.

    """
    if events.empty:
        return True

    events = events.sort_values("start").reset_index(drop=True)

    # Individual event validity
    valid = events["start"].notna() & events["end"].notna()
    invalid = valid & (events["start"] >= events["end"])
    if invalid.any():
        logger.debug("Invalid events with start time after end time detected.")
        return False

    # Inter-event validity
    start = events["start"].iloc[1:].reset_index(drop=True)
    end = events["end"].iloc[:-1].reset_index(drop=True)
    valid = start.notna() & end.notna()
    if not (start[valid] > end[valid]).all():
        logger.debug("Overlapping events detected")
        return False

    return True


def event_based_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    threshold: float,
    aggregation: str = "mean",
    separate_compound: bool = True,
    virtual_strategy: str = "both",
    plot: bool = False,
    plot_filename: Optional[str] = None,
) -> Dict[str, float]:
    """Compute event-based metrics: PKBIAS, PKTE, EVBIAS. Optionally, plot time series with event markers.

    Args:
        y_true: observed streamflow series
        y_pred: simulated streamflow series
        threshold: flow threshold for event detection
        aggregation: method to aggregate metrics across events ("mean" or "median")
        separate_compound: whether to separate compound events into single-peak events
        virtual_strategy: strategy for handling unmatched events by creating virtual events ("none", "obs", "mod", "both")
        plot: whether to plot time series with event markers
        plot_filename: filename for saving the plot (if plot=True)

    Returns:
        Dictionary with keys "PKBIAS", "PKTE", and "EVBIAS" containing the corresponding metric values.

    """
    if threshold is None or np.isnan(threshold):
        return {"PKBIAS": np.nan, "PKTE": np.nan, "EVBIAS": np.nan}

    # Step 1: preprocessing (resample + interpolate)
    y_true0 = preprocess_series(y_true)
    y_pred0 = preprocess_series(y_pred)

    # Step 2: chunking
    y_true_chunks = split_into_valid_chunks(y_true0)

    if len(y_true_chunks) == 0:
        logger.debug("Events cannot be calculated due to missing data")
        return {"PKBIAS": np.nan, "PKTE": np.nan, "EVBIAS": np.nan}

    events_all = []

    # Step 3: per-chunk event processing
    for y_true_chunk in y_true_chunks:
        y_pred_chunk = y_pred0.loc[y_true_chunk.index]

        events_obs = identify_events(y_true_chunk)
        events_mod = identify_events(y_pred_chunk)

        if len(events_obs) == 0:
            continue

        # merge short events before pairing
        events_obs = merge_short_events(
            events_obs, y_true_chunk, minimum_event_duration="6h"
        )
        events_mod = merge_short_events(
            events_mod, y_pred_chunk, minimum_event_duration="6h"
        )

        if separate_compound:
            events_obs = separate_compound_events(events_obs, y_true_chunk)
            events_mod = separate_compound_events(events_mod, y_pred_chunk)

        if len(events_obs) == 0 or len(events_mod) == 0:
            continue

        # validate events before pairing
        validate_events(events_obs)
        validate_events(events_mod)

        events_paired = pair_events(
            events_obs,
            events_mod,
            threshold,
            virtual_strategy=virtual_strategy,
        )

        if events_paired.empty:
            continue

        # validate paired events
        events_paired_obs = events_paired[["obs_start", "obs_end"]].rename(
            columns={"obs_start": "start", "obs_end": "end"}
        )
        validate_events(events_paired_obs)

        events_paired_mod = events_paired[["mod_start", "mod_end"]].rename(
            columns={"mod_start": "start", "mod_end": "end"}
        )
        validate_events(events_paired_mod)

        events_all.append(events_paired)

    # Step 4: merge chunks, get event peaks/timings/volumes (and optionally plot time series with event markers)
    if len(events_all) == 0:
        logger.debug(
            "No paired events found and event-based metrics cannot be calculated"
        )
        return {"PKBIAS": np.nan, "PKTE": np.nan, "EVBIAS": np.nan}

    events_all = pd.concat(events_all, ignore_index=True)

    # Get event peaks/timings/volumes
    peaks_all = get_event_peaks(
        events_all,
        y_true0,
        y_pred0,
    )

    # plot timeseries with event markers if requested
    if plot:
        events_obs = events_all[["obs_start", "obs_end"]].rename(
            columns={"obs_start": "start", "obs_end": "end"}
        )
        events_obs["peak"] = peaks_all["obs_peak_time"]
        events_obs["peak_value"] = peaks_all["obs_peak"]

        events_sim = events_all[["mod_start", "mod_end"]].rename(
            columns={"mod_start": "start", "mod_end": "end"}
        )
        events_sim["peak"] = peaks_all["mod_peak_time"]
        events_sim["peak_value"] = peaks_all["mod_peak"]

        plot_event_timeseries(
            y_true0,
            y_pred0,
            events_obs,
            events_sim,
            threshold=threshold,
            plot_filename=plot_filename,
        )

    # Step 5: compute metrics (events with NaN peaks are dropped)
    peaks_all = peaks_all.dropna(subset=["obs_peak", "mod_peak"])
    metrics = compute_event_metrics(
        peaks_all,
        aggregation,
    )

    return {
        "PKBIAS": metrics["peak_bias"],
        "PKTE": metrics["ptime_err"],
        "EVBIAS": metrics["event_bias"],
    }
