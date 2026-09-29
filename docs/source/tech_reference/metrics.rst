Supported Metrics
=================

`nwm-eval-mgr` currently supports metric calculation using either the `teehr` or `nwm_eval` library. The metrics supported by each library are listed below.

.. list-table::
   :header-rows: 1

   * - Metric Short Name
     - Metric Long Name
     - Supported by TEEHR
     - Supported by ``nwm_eval``
   * - aprBIAS
     - annual_peak_relative_bias
     - Yes
     - No
   * - CORR
     - pearson_correlation
     - Yes
     - Yes
   * - CSI
     - critical_success_index
     - No
     - Yes
   * - EVBIAS
     - event_volume_bias
     - No
     - Yes
   * - FAR
     - false_alarm_ratio
     - No
     - Yes
   * - FBIAS
     - frequency_bias
     - No
     - Yes
   * - HSEG_FDC
     - pbias_high_flow_fdc
     - No
     - Yes
   * - KGE
     - kling_gupta_efficiency
     - Yes
     - Yes
   * - KGE1
     - kling_gupta_efficiency_mod1
     - Yes
     - No
   * - KGE2
     - kling_gupta_efficiency_mod2
     - Yes
     - No
   * - LSEG_FDC
     - pbias_low_flow_fdc
     - No
     - Yes
   * - MAE
     - mean_absolute_error
     - Yes
     - Yes
   * - max_delta
     - max_value_delta
     - Yes
     - No
   * - max_mod
     - secondary_maximum
     - Yes
     - No
   * - max_obs
     - primary_maximum
     - Yes
     - No
   * - MBAIS
     - multiplicative_bias
     - Yes
     - No
   * - ME
     - mean_error
     - Yes
     - No
   * - mean_mod
     - secondary_average
     - Yes
     - No
   * - mean_obs
     - primary_average
     - Yes
     - No
   * - min_mod
     - secondary_minimum
     - Yes
     - No
   * - min_obs
     - primary_minimum
     - Yes
     - No
   * - MSE
     - mean_squared_error
     - Yes
     - No
   * - MSEG_FDC
     - pbias_medium_flow_fdc
     - No
     - Yes
   * - n_mod
     - secondary_count
     - Yes
     - No
   * - n_obs
     - primary_count
     - Yes
     - No
   * - NNSE
     - nash_sutcliffe_efficiency_normalized
     - Yes
     - Yes
   * - NSE
     - nash_sutcliffe_efficiency
     - Yes
     - Yes
   * - NSElog
     - logrithmic_nash_sutcliffe_efficiency
     - No
     - Yes
   * - NSEwt
     - weighted_nse_and_nselog
     - No
     - Yes
   * - PBIAS
     - percent_bias
     - No
     - Yes
   * - PKBIAS
     - percent_peak_flow_bias
     - No
     - Yes
   * - PKTE
     - peak_timing_error
     - No
     - Yes
   * - POD
     - probability_of_detection
     - No
     - Yes
   * - R2
     - r_squared
     - Yes
     - No
   * - RBIAS
     - relative_bias
     - Yes
     - No
   * - RMAE
     - mean_absolute_relative_error
     - Yes
     - No
   * - RMSE
     - root_mean_squared_error
     - Yes
     - Yes
   * - RSR
     - rmse_observation_std_ratio
     - No
     - Yes
   * - sCORR
     - spearman_correlation
     - Yes
     - No
   * - sum_mod
     - secondary_sum
     - Yes
     - No
   * - sum_obs
     - primary_sum
     - Yes
     - No
   * - var_mod
     - secondary_variance
     - Yes
     - No
   * - var_obs
     - primary_variance
     - Yes
     - No
