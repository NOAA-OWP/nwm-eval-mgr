from pathlib import Path

import pandas as pd

from nwm_eval_mgr.event_metric_functions import event_based_metrics


def run_event_analysis(
    obs_file: str | Path,
    sim_file: str | Path,
    obs_column: str,
    sim_column: str,
    time_column: str = "time",
    start_time: str | None = None,
    end_time: str | None = None,
    threshold: float = 0.9,
    aggregation: str = "mean",
    separate_compound: bool = True,
    virtual_strategy: str = "none",
    plot: bool = True,
    plot_filename: str | None = None,
):
    """End-to-end event analysis workflow."""
    # Load data
    obs_df = pd.read_csv(obs_file, parse_dates=[time_column]).set_index(time_column)
    sim_df = pd.read_csv(sim_file, parse_dates=[time_column]).set_index(time_column)

    y_true = obs_df[obs_column].sort_index()
    y_pred = sim_df[sim_column].sort_index()

    # Align
    idx = y_true.index.intersection(y_pred.index)
    y_true = y_true.loc[idx]
    y_pred = y_pred.loc[idx]

    # Subset time range
    if start_time is not None:
        y_true = y_true[y_true.index >= pd.to_datetime(start_time)]
        y_pred = y_pred[y_pred.index >= pd.to_datetime(start_time)]
    if end_time is not None:
        y_true = y_true[y_true.index <= pd.to_datetime(end_time)]
        y_pred = y_pred[y_pred.index <= pd.to_datetime(end_time)]

    # compute event-based metrics and plot time series with events highlighted
    metrics = event_based_metrics(
        y_true,
        y_pred,
        threshold=threshold,
        aggregation=aggregation,
        separate_compound=separate_compound,
        virtual_strategy=virtual_strategy,
        plot=plot,
        plot_filename=plot_filename,
    )

    print("\nEvent-based metrics")
    print("-------------------")
    for k, v in metrics.items():
        print(f"{k:10s}: {v:.3f}")


if __name__ == "__main__":
    gage = "13237920"
    start_time = "2020-03-01"
    end_time = "2020-09-01"

    # gage = "01123000"
    # start_time = "2014-03-01"
    # end_time = "2014-09-01"

    separate_compound = True
    suffix = "_single_peak" if separate_compound else "_multi_peak"
    filename = f"event_timeseries_{gage}{suffix}.png"

    results = run_event_analysis(
        obs_file=Path(f"{gage}_hourly_discharge.csv").expanduser(),
        sim_file=Path(f"{gage}_output_valid_best.csv").expanduser(),
        obs_column="q_cms",
        sim_column="sim_flow",
        time_column="time",
        start_time=start_time,
        end_time=end_time,
        threshold=0.90,
        aggregation="mean",  # valid options: "mean", "median"
        separate_compound=separate_compound,  # valid options: True, False
        virtual_strategy="both",  # valid options: "none", "obs", "sim", "both"
        plot=True,
        plot_filename=filename,
    )
