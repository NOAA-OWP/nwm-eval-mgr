"""Module containing functions to calculate various metrics for evaluating hydrological model performance.

Functions:
    - treat_values: Preprocess time series data by removing negative values, NaN values, and replacing zero values.
    - pearson_corr: Calculate Pearson correlation coefficient and p-value between observed and simulated values.
    - mean_abs_error: Calculate mean absolute error between observed and simulated values.
    - root_mean_squared_error: Calculate root mean squared error or mean squared error between observed and simulated values.
    - rmse_std_ratio: Calculate the ratio of RMSE to the standard deviation of observed values.
    - percent_bias: Calculate percent bias between observed and simulated values.
    - nse: Calculate Nash-Sutcliffe efficiency, with options for logarithmic transformation and normalization.
    - weighted_nse: Calculate a weighted average of NSE and logarithmic NSE.
    - kge: Calculate Kling-Gupta efficiency between observed and simulated values.
    - pbias_fdc: Calculate percent bias of flow duration curve segments (high, medium, low flow) based on exceedance probabilities.
    - categorical_score: Calculate categorical scores (POD, FAR, CSI, FBIAS) based on a specified threshold.
    - calculate_metrics: A wrapper function to calculate multiple metrics at once based on user-specified metric names.

"""

import warnings
from typing import Dict, Optional, Union

warnings.simplefilter(action="ignore", category=FutureWarning)

import logging

import numpy as np
import pandas as pd
import scipy.stats as sp
from hydrotools.metrics import metrics as hm
from scipy.stats import pearsonr

from .event_metric_functions import event_based_metrics

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

__all__ = [
    "treat_values",
    "pearson_corr",
    "mean_abs_error",
    "root_mean_squared_error",
    "rmse_std_ratio",
    "percent_bias",
    "nse",
    "weighted_nse",
    "kge",
    "categorical_score",
    "pbias_fdc",
    "event_based_metrics",
]


def treat_values(
    df: pd.DataFrame,
    remove_neg: Optional[bool] = False,
    remove_na: Optional[bool] = False,
    replace_zero: Optional[bool] = False,
    replace_inf: Optional[bool] = False,
) -> pd.DataFrame:
    """Remove NaN, inf and negative values, and replace zero values of time series.

    Args:
        df (pd.DataFrame): Contains time series of observation and simulation.
        remove_neg (bool, optional): If True, when negative value occurs at the ith element of observation or simulation
            the ith element of both observation or simulation is removed.
        remove_na (bool, optional): If True, when NaN value occurs at the ith element of observation or simulation,
            the ith element of both observation or simulation is removed.
        replace_zero (bool, optional): If True, when the zero value occurs at the ith element of observation or simulation,
            all observation and simulation are added with 1/100 of mean of observation according to Pushpalatha et al (2012).
        replace_inf (bool, optional): If True, when the inf value occurs at the ith element of observation or simulation,
            the ith element of both observation or simulation is replaced with a large finite value.

    Returns:
        pd.DataFrame: New DataFrame with treated values

    References:
        Pushpalatha, R., C. Perrin, N. L. Moine, V. Andreassian, 2012: A review of efficiency criteria suitable
            for evaluating low-flow simulations. Journal of Hydrology, 420-421, 171-182.

    """
    df = df.copy()
    colnames = list(df.columns)

    # Remove rows with duplicated datetime
    df.drop_duplicates(subset=colnames[0], inplace=True)
    df.sort_values(by=colnames[0], na_position="last")

    # Remove rows with missing values
    if remove_na:
        na_index = df.isin([np.nan, np.inf, -np.inf])
        df = df[~na_index]
        df.dropna(inplace=True)

    # Remove rows with negative values
    if remove_neg:
        if (df[colnames[1:]] < 0).all(axis=1).any():
            df = df[~(df[colnames[1:]] < 0).all(axis=1)]

    # Replace zero values
    if replace_zero:
        if df[colnames[1:]].min().values.min() <= 0.0001:
            # df[colnames[1:]] = (
            #     df[colnames[1:]] + 1.0 / 100.0 * df[colnames[1]].mean()
            # )  # this treatment does not work when mean is zero
            df[colnames[1:]] = df[colnames[1:]] + 0.00001

    # Remove inf values
    if replace_inf:
        inf_index = df.isin([np.inf, -np.inf])
        df[inf_index] = np.nan

    return df


def pearson_corr(
    y_true: pd.Series,
    y_pred: pd.Series,
) -> float:
    """Compute mean squared error, or optionally root mean squared error.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations

    Returns:
        corr (float): Pearson correlation coefficient
        p_value (float): Two-tailed p-value


    """
    # Compute
    corr, p_value = pearsonr(y_pred, y_true)

    return corr, p_value


def mean_abs_error(
    y_true: pd.Series,
    y_pred: pd.Series,
) -> float:
    """Compute mean absolute error between simulation and observation.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations

    Returns:
        float: Mean absolute error

    """
    return np.nanmean(np.abs(y_pred - y_true))  # this handles NaN values appropriately


def root_mean_squared_error(
    y_true: pd.Series,
    y_pred: pd.Series,
    root: Optional[bool] = True,
) -> float:
    """Compute root mean squared error, or optionally mean squared error.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        root (bool, optional): When False, return the mean squared error.

    Returns:
        float: Root mean squared error or mean squared error

    """
    # Compute mean squared error
    mse = np.nanmean((y_true - y_pred) ** 2.0)  # this handles NaN values appropriately

    # Return RMSE, optionally return mean squared error
    if not root:
        return mse
    return np.sqrt(mse)


def rmse_std_ratio(
    y_true: pd.Series,
    y_pred: pd.Series,
    root: Optional[bool] = False,
    warning_msg: Optional[bool] = False,
) -> float:
    """Compute ratio of RMSE between simulation and observation to standard deviation of observation.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        root (bool, optional): When True, compute RMSE for the numerator; when False, compute MSE for the numerator.
        warning_msg (bool, optional): When True, display a warning message if the denominator is zero.

    Returns:
        float: Ratio of RMSE and standard deviation of observation

    """
    rmse = root_mean_squared_error(y_true, y_pred, root=root)
    denominator = np.std(y_true)

    if denominator != 0:
        rsr = rmse / denominator
    else:
        rsr = np.nan
        if warning_msg:
            logger.warning("'np.std(y_true) = 0', can't compute RSR")

    return rsr


def percent_bias(
    y_true: pd.Series,
    y_pred: pd.Series,
    warning_msg: Optional[bool] = False,
) -> float:
    """Compute mean squared error, or optionally root mean squared error.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        warning_msg (bool, optional): When True, display a warning message if the denominator is zero.

    Returns:
        float: Percent bias

    """
    denominator = np.sum(y_true)
    pbias = np.sum(np.subtract(y_pred, y_true)) / denominator * 100

    if denominator != 0:
        return pbias
    else:
        if warning_msg:
            logger.warning("'np.sum(y_true) = 0', can't compute PBIAS")
        return np.nan


def nse(
    y_true: pd.Series,
    y_pred: pd.Series,
    fun: Optional[str] = None,
    epsilon: Union[None, str] = [None, "Pushpalatha2012"],
    normalized: Optional[bool] = False,
    warning_msg: Optional[bool] = False,
) -> float:
    """Compute Nash-Sutcliffe efficiency.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        fun (str, optional): Transformation function applied to y_true and y_pred
        epsilon (Union[None, str], optional): Value added to both y_true and y_pred if fun is logarithm or other functions
            that are mathematically impossible to compute transformation of zero flows:
            1) 0: zero value
            2) "Pushpalatha2012": 1/100 of mean of y_true
            3) other numeric value
        normalized (bool, optional): If True, convert Nash-Sutcliffe efficiency to the normalized value.

    Returns:
        float: Nash-Sutcliffe Efficiency value

    """
    # Transform values
    if fun == "log":
        if epsilon == "Pushpalatha2012":
            y_true = y_true + np.mean(y_true) / 100
            y_pred = y_pred + np.mean(y_true) / 100
            if y_true.min() == 0.0:  # if not np.all(y_true)
                y_true = y_true + 0.01
            if y_pred.min() == 0.0:
                y_pred = y_pred + 0.01
        y_true = np.log(y_true)
        y_pred = np.log(y_pred)

    # Compute components
    numerator = np.sum(np.subtract(y_pred, y_true) ** 2.0) / len(y_true)
    denominator = np.sum(np.subtract(y_true, np.mean(y_true)) ** 2.0) / len(y_true)

    # Compute score, optionally normalize
    if denominator != 0:
        if normalized:
            return 1.0 / (1.0 + numerator / denominator)
        return 1.0 - numerator / denominator
    else:
        if warning_msg:
            logger.warning("'denominator = 0', can't compute NSE")
        return np.nan


def weighted_nse(
    y_true: pd.Series,
    y_pred: pd.Series,
    weight: Optional[float] = 0.5,
    normalized: Optional[bool] = False,
) -> float:
    """Compute weighted average of NSE of raw time series and NSE of logrithmic time series.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        weight (float, optional): Weight value for Nash-Sutcliffe efficiency component
        normalized (bool, optional): Whether to convert the weighted Nash-Sutcliffe efficiency to the normalized value

    Returns:
        float: Weighted Nash-Sutcliffe Efficiency value

    """
    nse1 = nse(y_true, y_pred)

    # Compute NSELog
    nselog = nse(y_true, y_pred, fun="log", epsilon="Pushpalatha2012")

    # Compute weighted NSE
    nsewt = nse1 * weight + nselog * (1 - weight)

    if normalized:
        return 1.0 / (2.0 - nsewt)
    return nsewt


def kge(
    y_true: pd.Series,
    y_pred: pd.Series,
    r_scale: Optional[float] = 1.0,
    a_scale: Optional[float] = 1.0,
    b_scale: Optional[float] = 1.0,
) -> float:
    """Compute Kling-Gupta efficiency between simulation and observation.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        r_scale (float, optional): correlation scaling factor (default is 1.0)
        a_scale (float, optional): relative variability scaling factor (default is 1.0)
        b_scale (float, optional): relative mean scaling factor (default is 1.0)

    Returns:
        float: Kling-Gupta efficiency value

    References:
        Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009). Decomposition of the mean
        squared error and NSE performance criteria: Implications for improving hydrological modelling.
        Journal of hydrology, 377(1-2), 80-91.

    """
    mean_obs = np.mean(y_true)
    mean_sim = np.mean(y_pred)
    std_obs = np.std(y_true)
    std_sim = np.std(y_pred)

    # Correlation
    if std_obs == 0 or std_sim == 0:
        r = np.nan
    else:
        r = np.corrcoef(y_true, y_pred)[0, 1]

    # Variability ratio
    alpha = np.nan if std_obs == 0 else std_sim / std_obs

    # Bias ratio
    beta = np.nan if mean_obs == 0 else mean_sim / mean_obs

    # Kling-Gupta Efficiency
    kge = 1 - np.sqrt(
        r_scale * (r - 1) ** 2 + a_scale * (alpha - 1) ** 2 + b_scale * (beta - 1) ** 2
    )

    return kge

    # avoid using hydrotools implementation due to potential ZeroDivisionError issues
    # return hm.kling_gupta_efficiency(y_true, y_pred, r_scale, a_scale, b_scale)


def pbias_fdc(
    y_true: pd.Series,
    y_pred: pd.Series,
    bqthr: Optional[float] = 0.9,
    lqthr: Optional[float] = 0.7,
    hqthr: Optional[float] = 0.2,
    pqthr: Optional[float] = 0.1,
    warning_msg: Optional[bool] = False,
) -> Dict[str, float]:
    """Compute percent bias of flow duration curve (FDC) high-segment volume, midsegment slope and low-segment volume according to Yilmaz et al (2008).

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        bqthr (float, optional): baseflow exceedance probability (default is 0.9)
        lqthr (float, optional): low flow exceedance probability (default is 0.7)
        hqthr (float, optional): high flow exceedance probability (default is 0.2)
        pqthr (float, optional): peak flow exceedance probability (default is 0.1)
        warning_msg (bool, optional): If True, print warining messages.

    Returns:
        Dict[str, float]: Dictionary of pbias of peak flow, slope and low flow of FDC

    References:
        Yilmaz, K. K., H. V. Gupta, and T. Wagener (2008), A process-based diagnostic approach to
        modelevaluation: Application to the NWS distributed hydrologic model,
        Water Resource Research, 44, W09417,doi:10.1029/2007WR006716.

    """
    # Sort and rank
    y_true_sort = np.sort(y_true, axis=0)[::-1]
    y_pred_sort = np.sort(y_pred, axis=0)[::-1]

    # Compute exceedence probabilities
    y_true_prob = np.arange(1, len(y_true) + 1) / len(y_true)
    y_pred_prob = np.arange(1, len(y_pred) + 1) / len(y_pred)

    # Compute pbias of peak flow segment of FDC (require same number of elements)
    numerator = np.sum(
        np.subtract(y_pred_sort[y_pred_prob < pqthr], y_true_sort[y_true_prob < pqthr])
    )
    denominator = np.sum(y_true_sort[y_true_prob < pqthr])
    if denominator != 0:
        pbias_hseg_fdc = numerator / denominator * 100
    else:
        pbias_hseg_fdc = np.nan
        if warning_msg:
            logger.warning(
                "'denominator = 0', can't compute PBIAS for peak flow of FDC"
            )

    # Compute pbias of midsegment slope of FDC
    term1 = y_pred_sort[np.abs(y_pred_prob - hqthr).argmin()]
    term2 = y_pred_sort[np.abs(y_pred_prob - lqthr).argmin()]
    if term1 != 0 and term2 != 0:
        pred_term = np.log(term1) - np.log(term2)
        denominator = np.log(
            y_true_sort[np.abs(y_true_prob - hqthr).argmin()]
        ) - np.log(y_true_sort[np.abs(y_true_prob - lqthr).argmin()])
        numerator = pred_term - denominator
        if denominator > 0:
            pbias_mseg_fdc = numerator / denominator * 100
        else:
            pbias_mseg_fdc = np.nan
            if warning_msg:
                logger.warning(
                    "'denominator = 0', can't compute PBIAS for slope of FDC"
                )
    else:
        pbias_mseg_fdc = np.nan
        if warning_msg:
            logger.warning(
                "'0 as argument for np.log', can't compute PBIAS for slope of FDC"
            )

    # Compute pbias of low flow segment of FDC
    term1 = (y_pred_sort[y_pred_prob > bqthr]).min()
    term2 = y_pred_sort.min()
    term3 = (y_true_sort[y_true_prob > bqthr]).min()
    term4 = y_true_sort.min()
    if all([term1 != 0, term2 != 0, term3 != 0, term4 != 0]):
        denominator = np.sum(
            np.log(y_true_sort[y_true_prob > bqthr]) - np.log(y_true_sort.min())
        )
        numerator = (
            np.sum(np.log(y_pred_sort[y_pred_prob > bqthr]) - np.log(y_pred_sort.min()))
            - denominator
        )
        if denominator != 0:
            pbias_lseg_fdc = numerator / denominator * (-100)
        else:
            pbias_lseg_fdc = np.nan
            if warning_msg:
                logger.warning(
                    "'denominator = 0', can't compute PBIAS for low flow of FDC"
                )
    else:
        pbias_lseg_fdc = np.nan
        if warning_msg:
            logger.warning(
                "'0 as argument for np.log', can't compute PBIAS for low flow of FDC"
            )

    return {
        "HSEG_FDC": pbias_hseg_fdc,
        "MSEG_FDC": pbias_mseg_fdc,
        "LSEG_FDC": pbias_lseg_fdc,
    }


def categorical_score(
    y_true: pd.Series,
    y_pred: pd.Series,
    threshold: float,
) -> Dict[str, float]:
    """Compute probability of detection (POD), probability of false_alarm (FAR), cirtical success index (CSI) and frequency bias (FBIAS).

    Args:
        y_true (pd.Series) : Ground truth or observations
        y_pred (pd.Series) : Modeled values or simulations
        threshold (float): threshold value for categorizing observations and simulations.


    Returns:
        Dictionary of categorical score values

    """
    if threshold is None or pd.isna(threshold):
        return {"POD": np.nan, "FAR": np.nan, "CSI": np.nan, "FBIAS": np.nan}

    observed = y_true > threshold
    simulated = y_pred > threshold
    contingency_table = hm.compute_contingency_table(observed, simulated)
    pod = hm.probability_of_detection(contingency_table)
    far = hm.probability_of_false_alarm(contingency_table)
    csi = hm.threat_score(contingency_table)
    fbias = hm.frequency_bias(contingency_table)

    return {"POD": pod, "FAR": far, "CSI": csi, "FBIAS": fbias}


def get_threshold_value(data: pd.Series, threshold: dict) -> float:
    """Get threshold value based on the specified threshold type and value.

    Args:
        data (pd.Series): time series data (e.g., observed values) used to calculate threshold value when threshold type is "quantile"
        threshold (dict): Dictionary containing threshold value and type. Example: {"value": 0.9, "type": "quantile"} or {"value": 10, "type": "absolute"}

    Returns:
        float: threshold value

    """
    if threshold["type"] == "quantile":
        thresh_val = data.quantile(threshold["value"])
    elif threshold["type"] == "absolute":
        thresh_val = threshold["value"]
    else:
        msg = f"Unsupported threshold type: {threshold['type']}. Please use 'quantile' or 'absolute'."
        logger.error(msg)
        raise Exception(msg)

    return thresh_val


_all_metric_funcs = {
    "CORR": pearson_corr,
    "NSE": nse,
    "NNSE": nse,
    "NSElog": nse,
    "NSEwt": weighted_nse,
    "KGE": kge,
    "MAE": mean_abs_error,
    "RMSE": root_mean_squared_error,
    "RSR": rmse_std_ratio,
    "PBIAS": percent_bias,
    "HSEG_FDC": pbias_fdc,
    "MSEG_FDC": pbias_fdc,
    "LSEG_FDC": pbias_fdc,
    "POD": categorical_score,
    "FAR": categorical_score,
    "CSI": categorical_score,
    "FBIAS": categorical_score,
    "PKBIAS": event_based_metrics,
    "PKTE": event_based_metrics,
    "EVBIAS": event_based_metrics,
}

_all_metrics = {
    "CORR": "pearson_correlation",
    "NSE": "nash_sutcliffe_efficiency",
    "NNSE": "nash_sutcliffe_efficiency_normalized",
    "NSElog": "logrithmic nash_sutcliffe_efficiency",
    "NSEwt": "weighted NSE and NSElog",
    "KGE": "kling_gupta_efficiency",
    "MAE": "mean_absolute_error",
    "RMSE": "root_mean_squared_error",
    "PBIAS": "percent_bias",
    "RSR": "RMSE_observation_std_ratio",
    "HSEG_FDC": "pbias_high_flow_FDC",
    "MSEG_FDC": "pbias_medium_flow_FDC",
    "LSEG_FDC": "pbias_low_flow_FDC",
    "POD": "probability_of_detection",
    "FAR": "false_alarm_ratio",
    "CSI": "critical_success_index",
    "FBIAS": "frequency_bias",
    "PKBIAS": "percent_peak_flow_bias",
    "PKTE": "peak_timing_error",
    "EVBIAS": "event_volume_bias",
}


def calculate_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    metrics: Optional[list] = [],
    threshold_categorical: Optional[dict] = {"value": 0.9, "type": "quantile"},
    threshold_event: Optional[dict] = {"value": 0.9, "type": "quantile"},
) -> Dict[str, float]:
    """Compute all statistical metrics between simulation and observation.

    Args:
        y_true (pd.Series): Ground truth or observations
        y_pred (pd.Series): Modeled values or simulations
        metrics (list, optional): list of metrics to be calculated; if undefined, calculate all metrics
        threshold_categorical (dict, optional): threshold value for calculating categorical scores. Default is {"value": 0.9, "type": "quantile"}.
        threshold_event (dict, optional): threshold value for defining events. Default is {"value": 0.9, "type": "quantile"}.

    Returns:
        Dict[str, float]: dictionary of metric values

    """
    metrics_all = _all_metrics.keys()
    if not metrics:
        metrics1 = metrics_all
    else:
        metrics1 = [m1 for m1 in metrics if m1 in metrics_all]
        metrics2 = [m1 for m1 in metrics if m1 not in metrics1]
        if len(metrics2) > 0:
            raise Exception(f"These metrics are not supported: {metrics2}")

    # loop through metrics to calculate them
    result = {}
    for m1 in metrics1:
        # some metrics (e.g., categorical, event-based, FDC-based) are calculated together so only need to call function once
        if m1 in result.keys():
            next

        # get metric function
        f1 = _all_metric_funcs.get(m1)

        # calculate metric and add to result dictionary
        if m1 in ["NSE", "KGE", "RSR", "RMSE", "MAE", "PBIAS", "NSEwt"]:
            result.update({m1: f1(y_true, y_pred)})
        elif m1 == "CORR":
            result.update({m1: f1(y_true, y_pred)[0]})
        elif m1 == "NSElog":
            result.update(
                {m1: f1(y_true, y_pred, fun="log", epsilon="Pushpalatha2012")}
            )
        elif m1 == "NNSE":
            result.update({m1: f1(y_true, y_pred, normalized=True)})
        elif m1 in ["POD", "FAR", "CSI", "FBIAS"]:
            result.update(
                f1(y_true, y_pred, get_threshold_value(y_true, threshold_categorical))
            )
        elif m1 in ["HSEG_FDC", "MSEG_FDC", "LSEG_FDC"]:
            result.update(f1(y_true, y_pred))
        elif m1 in ["PKBIAS", "PKTE", "EVBIAS"]:
            result.update(
                f1(y_true, y_pred, get_threshold_value(y_true, threshold_event))
            )
        else:
            raise Exception(f"Unsupported metric: {m1}")

    # only return metrics that are requested
    result1 = {k: v for k, v in result.items() if k in metrics1}

    return result1
