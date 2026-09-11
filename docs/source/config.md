# Configuration for Evaluation/Verification

### Introduction

This page provides detailed documentation for configuring the NWM Evaluation Manager (nwm-eval-mgr) tool for a variety of simulation evaluation or forecast verification applications.

Template files, sample configuration files, and schemas for all configuration fields and subfields are included below. You can navigate to individual configuration files or schema sections using the tabs on the right or the Table of Contents below.

- `config_template.yaml`: Config template generated from the pydantic model, with default or example values defined for each field. This can be used as a starting point for creating your own configuration files.
- `config_ngencerf.yaml`: Sample config for verifying a single ngenCERF forecast at one location.
- `config_hindcast.yaml`: Sample config for verifying multiple ngenCERF hindcasts at one location.
- `config_nwm.yaml`: Sample config for verifying operational NWM v3 forecasts across multiple locations and domains using data retrieved from Google Cloud Storage (GCS).
- `config_ngensim.yaml`: Sample config for evaluating large-scale NGEN simulations (e.g., from regionalization) across multiple locations, VPUs, or NWM domains.

### Table of Contents

  - [Sample Files](#sample-files)
    - [`config_template.yaml`](#config-template-yaml)
    - [`config_ngencerf.yaml`](#config-ngencerf-yaml)
    - [`config_hindcast.yaml`](#config-hindcast-yaml)
    - [`config_nwm.yaml`](#config-nwm-yaml)
    - [`config_ngensim.yaml`](#config-ngensim-yaml)
  - [Schemas](#schemas)
    - [`BarChartConfig` (inherits from `BasePlotConfig`)](#barchartconfig-inherits-from-baseplotconfig)
    - [`BasePlotConfig` (inherits from `LeadTimesMixin`)](#baseplotconfig-inherits-from-leadtimesmixin)
    - [`BoxPlotConfig` (inherits from `BasePlotConfig`)](#boxplotconfig-inherits-from-baseplotconfig)
    - [`FilePathsConfig`](#filepathsconfig)
    - [`FlowObservationConfig`](#flowobservationconfig)
    - [`GeneralConfig`](#generalconfig)
    - [`HistogramConfig` (inherits from `BasePlotConfig`)](#histogramconfig-inherits-from-baseplotconfig)
    - [`LeadTimesMixin`](#leadtimesmixin)
    - [`LocationFilter`](#locationfilter)
    - [`MetricsConfig` (inherits from `LeadTimesMixin`)](#metricsconfig-inherits-from-leadtimesmixin)
    - [`NWMForecastConfig`](#nwmforecastconfig)
    - [`PairDataConfig`](#pairdataconfig)
    - [`PlotsConfig`](#plotsconfig)
    - [`ReferenceTimesMixin`](#referencetimesmixin)
    - [`SpatialMapConfig` (inherits from `BasePlotConfig`)](#spatialmapconfig-inherits-from-baseplotconfig)
    - [`TablePlotConfig` (inherits from `BasePlotConfig`)](#tableplotconfig-inherits-from-baseplotconfig)
    - [`TimeSeriesConfig` (inherits from `BasePlotConfig, ReferenceTimesMixin`)](#timeseriesconfig-inherits-from-baseplotconfig-referencetimesmixin)
    - [`USGSConfig`](#usgsconfig)

### Sample Files


(config-template-yaml)=
#### `config_template.yaml`

Config template generated from the pydantic model, with default or example values defined for each field. This can be used as a starting point for creating your own configuration files.

```yaml
general:     # General configuration for the evaluation, including dataset information and evaluation settings.
  steps:     # Steps to run in the evaluation process.
    fetch_fcst_data: True
    fetch_obs_data: True
    pair_data: True
    compute_metrics: True
    plot_metrics: True
  domain: 'conus'     # Domain for the evaluation. Valid options are 'conus', 'hi', 'ak', 'prvi' (case insensitive).
  assemble_domain: False     # Whether to assemble results across VPUs for the CONUS domain.
  location_set_name: 'usgs_01123000'     # Name for the set of locations to evaluate.
  location_list: ['01123000', '01123500']     # List of specific locations to include in the evaluation. If None, all locations in the crosswalk file will be used.
  location_type: 'usgs_gage'     # Type of locations to evaluate, which determines how locations are identified and processed.
  location_filter:     # Configuration for filtering locations based on column values.
    columns: ['vpu_id', 'status']
    values: ['03S', 'USGS-active']
  location_group_size: 200     # Number of locations to process in each group when pairing forecast and observation data.
  variable_name: 'streamflow'     # Name of the variable to evaluate. Currently only 'streamflow' is supported, but this field is included for future extensibility.
  nwm_configuration: 'ngen'     # NWM configuration to evaluate.
  dataset_name: ['noah_cfes', 'noah_topmodel']     # User-specified name(s) for the dataset(s) to evaluate.
  nwm_version: ['ngen', 'nwm30']     # NWM version(s) to evaluate.
  forecast_start_date: ['2022-12-01 00:00:00', '2022-12-15 00:00:00']     # Start date(s) for the forecast data to evaluate.
  forecast_end_date: ['2022-12-31 00:00:00', '2023-01-15 00:00:00']     # End date(s) for the forecast data to evaluate.
  eval_start_date: ['2022-12-11 00:00:00', '2022-12-25 00:00:00']     # Start date(s) for the evaluation period.
  eval_end_date: ['2022-12-31 00:00:00', '2023-01-15 00:00:00']     # End date(s) for the evaluation period.
  separate_calibrated: False     # Whether to distinguish calibrated and regionalized locations in the evaluation
file_paths:     # Configuration for file paths used in the evaluation, including input data and output directories.
  base_dir: '~/ngen_evaluation/'     # Root directory for storing data and outputs.
  location_list_file: ~/location_list.csv     # Path to a file containing the list of locations to evaluate
  crosswalk_file: ~/crosswalk.csv     # Path to a crosswalk file or a dictionary of crosswalk files.
  fcst_config_file: 'data/inputs/nwm_forecast_configuration.yaml'     # Path to the forecast configuration file defining parameters for different NWM configurations.
  fcst_data_file: '01123000_output.csv'     # Path to the forecast data file or a dictionary of forecast data files.
  fcst_data_dir: 'data/inputs/hindcasts/'     # Path to the directory containing forecast data files or a dictionary of directories.
  obs_data_file: 'data/inputs/obs/01123000_hourly_discharge.csv'     # Path to the observation data file. Both obs_data_file and obs_data_dir can be specified. The run will read all .csv and .parquet files in obs_data_dir and obs_data_file and remove duplicates.If neither obs_data_file nor obs_data_dir is provided, an observation data source must be specified in the 'flow_observation.usgs' section.
  obs_data_dir: 'data/inputs/obs/'     # ("Path to the observation data directory where one or more observation data files are stored. The run will look for all .csv and .parquet files in this directory. Each file can contain observation data for a single location (with the filename starting with the location identifier), or multiple locations with a 'location_id' column specifying the location identifiers.",)
  calib_param_file: 'data/inputs/calib_params.csv'     # Path to the calibration parameter file.
  txdot_gage_file: 'data/inputs/gage_files/tx_gauges.csv'     # Path to the TxDOT gage file.
  output_dir: 'ngen_evaluation/outputs/usgs_01123000/'     # Directory to save outputs such as paired data, computed metrics, and plots. 
nwm_forecast:     # Configuration for NWM forecast data.
  data_source: 'ngenCERF'     # Data source for the NWM forecast. Valid options include 'ngenCERF', 'ngenSIM', 'hindcast', and 'GCS'.
  fetch_fcst: [True]     # Whether to fetch forecast data for each dataset, with local file existence check.
  output_type: 'channel_rt'     # Type of NWM output to retrieve. Currently only 'channel_rt' is supported. Only applicable when data_source='GCS'. 
  t_minus: [0, 1, 2]     # T-minus hours for which to retrieve NWM forecasts, only applicable for AnA runs on GCS.
  kerchunk_method: 'local'     # Preference for creating Kerchunk reference json files, only applicable for GCS data source.
  process_by_z_hour: True     # Whether to process NWM files by z-hour per day, only applicable for GCS data source.
  stepsize: 100     # Number of files to process in memory at once when processing GCS data without z-hour chunking.
  ignore_missing_file: True     # Whether to ignore missing NWM files and continue processing, only applicable for GCS data source.
  overwrite_output: False     # Whether to overwrite existing forecast data files.
  memory_per_worker_gb: 3     # Configurable memory (in GB) assigned to each worker or process.
flow_observation:     # Configuration for flow observation data.
  usgs: ''     # Configuration for USGS flow observations. If omitted, obs_data_file and/or obs_data_dir must be provided in file_paths section, 
pair_data:     # Configuration for paired data.
  overwrite: True     # Whether to overwrite existing paired data files.
  group_size: 200     # Number of locations to process in each group when pairing forecast and observation data.
metrics:     # Configuration for metrics.
  lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
  overwrite: True     # Whether to overwrite existing metric files. 
  library: 'nwm.eval'     # Library to use for metric computation. Valid options: nwm.eval, teehr. 
  metric_subset: 'all'     # Subset of metrics to compute, either 'all' or a list of metric names.
  metric_exclude: ['HSEG_FDC', 'MSEG_FDC', 'LSEG_FDC']     # List of metric names to exclude from metric_subset for computation. 
  threshold_categorical:     # Threshold for categorical metrics. Valid options for type are 'quantile' and 'absolute'. If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. If 'absolute', the threshold will be the specified absolute flow value.
    value: 0.9
    type: quantile
  threshold_event:     # Threshold for event-based metrics. Valid options for type are 'quantile' and 'absolute'. If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. If 'absolute', the threshold will be the specified absolute flow value.
    value: 0.9
    type: quantile
  file_format: 'parquet'     # File format for output files. Valid options are 'parquet' and 'csv'.
plots:     # Configuration for plots.
  histogram:     # Configuration for histogram plots.
    lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
    binning:     # Dictionary specifying the binning for histogram plots, with metric names as keys and lists of bin edges as values.
      NSE: [-1, -0.5, 0, 0.5, 1]
      KGE: [-1, -0.5, 0, 0.5, 1]
  boxplot:     # Configuration for box plot.
    lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
    show_outliers: False     # Whether to show outliers in box plots. If True, outliers will be shown as individual points. If False, outliers will be omitted.
  spatial_map:     # Configuration for spatial map plots.
    lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
    scaling:     # Dictionary specifying the scaling for spatial maps, with metric names as keys and lists of scaling ranges as values.
      NSE: [-0.5, 1.0]
      KGE: [-0.5, 1.0]
  time_series:     # Configuration for time series plots.
    reference_times: ['2022-12-01 00:00:00', '2022-12-15 00:00:00']     # Reference times (T0s) to include in the evaluation.
    lead_times: [1, 2, 3]     # List of lead times for time series plots. Each lead time should be a number representing the forecast lead time in hours.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
  metric_table:     # Configuration for metric table plots.
    lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
  barchart:     # Configuration for bar chart plots.
    lead_times: ['all', '1-5', '5-10', '10-15', 'all_aggregated']     # Lead times to include in the evaluation.
    plot: False     # Whether to generate this type of plot.
    metric_subset: ['NSE', 'KGE']     # List of metric names to include in the plots.
    tag: ''     # Optional tag to include in plot titles and filenames.
```

(config-ngencerf-yaml)=
#### `config_ngencerf.yaml`

Sample config for verifying a single ngenCERF forecast at one location.

```yaml
general:   
  steps: # define which of the 5 steps to run; each step can be run independently,
    fetch_fcst_data: true
    fetch_obs_data: true
    pair_data: true
    compute_metrics: true
    plot_metrics: true
  location_set_name: usgs_01123000  # user-specified name for the set of locations
  location_list: ['01123000'] # list of usgs gage IDs
  location_type: usgs_gage # location type
  variable_name: streamflow # currently only 'streamflow' is supported
  nwm_configuration: short_range # must match one of the configurations defined in fcst_config_file  
  dataset_name: [noah_cfes] # user-specified name of datasets (e.g., formualtion name
  nwm_version: [ngen] # list of NWM versions; must have the same length as 'dataset_name'
  forecast_start_date: ['2022-12-01 00:00:00'] # list of start dates for verification; must be same length as 'dataset_name'
  forecast_end_date: ['2022-12-01 00:00:00'] # list of end dates for verification; must be same length as 'dataset_name'

file_paths:
  base_dir: ~/repos/nwm-eval-mgr/data/ # root directory to store data/outputs for verification
  crosswalk_file: '{base_dir}/inputs/gage_files/usgs_{nwm_version}_crosswalk_all_domains.parquet' # crosswalk file mapping gage IDs to NWM/ngen link IDs
  fcst_config_file: '{base_dir}/inputs/nwm_forecast_configuration.yaml' # NWM forecast configuration file
  fcst_data_file: '{base_dir}/inputs/{location_set_name}/{dataset_name}/{nwm_configuration}.csv' # forecast data directory (must be specified when nwm_forecast.data_source is set to ngenCERF)
  output_dir: '{base_dir}/outputs/{location_set_name}' # output directory to store all datasets, metrics and plots

nwm_forecast:
  data_source: ngenCERF    # Specifies the source to retrieve the model forecast or simulation data. Currently supported options: GCS, ngenCERF, ngenSIM

flow_observation:
  usgs: # flow obs retrieved will be stored at [data_dir_root]/[location_set_name]/usgs
    chunk_by: month   # data are saved in parquet files by day/month/year
    overwrite_output: True  # If True, existing output files will be overwritten; if False, existing files are retained
    memory_per_worker_gb: 3  # configurable memory (in GB) assigned to each worker

pair_data:  
  overwrite: true # whether to overwrite existing joined parquet files
  group_size: 200 # break large location list into smaller groups (for pair_data and cacl_metrics steps) to avoid potential memory issues and to speed up processing

metrics:  
  overwrite: true # whether to overwrite existing metric files
  library: nwm.eval # currently supported options: teehr, nwm.eval
  metric_subset: 'all'
  threshold_categorical:
    value: 0.9 # threshold value to be used for categorical metrics in nwm.eval 
    type: quantile # type of threshold for categorical metrics in nwm.eval; options are 'quantile' or 'absolute'
  threshold_event:
    value: 0.9 # threshold value to be used for event-based metrics in nwm.eval
    type: quantile # type of threshold for event-based metrics in nwm.eval; options are 'quantile' or 'absolute'
  lead_times: ['all_aggregated'] # list of lead times (in hours) for which metrics should be calculated for  
  file_format: parquet # file format for metrics. Options are: parquet, csv. Default is parquet.

plots:
  time_series:
    plot: true  # whether to create time series plots
  metric_table:
    plot: true  # whether to create metric table plots
  barchart:
    plot: true  # whether to create barchart plots
```

(config-hindcast-yaml)=
#### `config_hindcast.yaml`

Sample config for verifying multiple ngenCERF hindcasts at one location.

```yaml
general:   
  steps: # define which of the 5 steps to run; each step can be run independently,
    fetch_fcst_data: true
    fetch_obs_data: true
    pair_data: true
    compute_metrics: true
    plot_metrics: true
  location_set_name: 'usgs_01123000'  # user-specified name for the set of locations
  location_list: ['01123000'] # list of usgs gage IDs
  location_type: usgs_gage # location type
  variable_name: streamflow # currently only 'streamflow' is supported
  nwm_configuration: short_range  # must match one of the configurations defined in fcst_config_file  
  dataset_name: [noah_cfes, noah_sac] # user-specified name of datasets (e.g., formualtion name)
  nwm_version: [ngen, ngen] # list of NWM versions; must have the same length as 'dataset_name'
  forecast_start_date: ['2025-08-20 00:00:00', '2025-08-20 00:00:00'] # list of start dates for verification; must be same length as 'dataset_name'
  forecast_end_date: ['2025-08-22 06:00:00', '2025-08-22 06:00:00'] # list of end dates for verification; must be same length as 'dataset_name'

file_paths:
  base_dir: ~/repos/nwm-eval-mgr/data/ # root directory to store data/outputs for verification
  crosswalk_file: '{base_dir}/inputs/gage_files/usgs_{nwm_version}_crosswalk_all_domains.parquet' # crosswalk file mapping gage IDs to NWM/ngen link IDs
  fcst_config_file: '{base_dir}/inputs/nwm_forecast_configuration.yaml' # NWM forecast configuration file
  fcst_data_dir: '{base_dir}/inputs/{location_set_name}/{dataset_name}/hind_run1' # forecast data directory or file (must be specified when nwm_forecast.data_source is set to ngenCERF or hinscast)
  fcst_data_file: '01123000_output.csv' # forecast data file path pattern (must be specified when nwm_forecast.data_source is set to ngenCERF or hinscast)
  output_dir: '{base_dir}/outputs/{location_set_name}_hindcast' # output directory to store all datasets, metrics and plots

nwm_forecast:
  data_source: hindcast    # Specifies the source to retrieve the model forecast or simulation data. Currently supported options: GCS, ngenCERF, ngenSIM, hindcast

flow_observation:
  usgs: # flow obs retrieved will be stored at [data_dir_root]/[location_set_name]/usgs
    chunk_by: month   # data are saved in parquet files by day/month/year
    overwrite_output: True  # If True, existing output files will be overwritten; if False, existing files are retained
    memory_per_worker_gb: 3  # configurable memory (in GB) assigned to each worker

pair_data:  
  overwrite: true # whether to overwrite existing joined parquet files
  group_size: 200 # break large location list into smaller groups (for pair_data and cacl_metrics steps) to avoid potential memory issues and to speed up processing

metrics:  
  overwrite: true # whether to overwrite existing metric files
  library: nwm.eval # currently supported options: teehr, nwm.eval
  metric_subset: 'all'
  threshold_categorical:
    value: 0.9 # threshold value to be used for categorical metrics in nwm.eval 
    type: quantile # type of threshold for categorical metrics in nwm.eval; options are 'quantile' or 'absolute'
  threshold_event:
    value: 0.9 # threshold value to be used for event-based metrics in nwm.eval
    type: quantile # type of threshold for event-based metrics in nwm.eval; options are 'quantile' or 'absolute'
  lead_times: [all, 1-5, 6-10, 11-18, all_aggregated] # list of lead times (in hours) for which metrics should be calculated for  
  file_format: parquet # file format for metrics. Options are: parquet, csv. Default is parquet.

plots:
  time_series:
    plot: true  # whether to create time series plots
    lead_times: [1, 6, 12, 18] # list of lead times (in hours) for which time series plots should be created
    reference_times: ['2025-08-20 00:00:00', '2025-08-21 00:00:00', '2025-08-22 00:00:00'] # list of forecast reference times for which time series plots should be created
  metric_table:
    plot: true  # whether to create metric table plots
    lead_times: [1, 10, 1-5, all_aggregated] # list of lead times (in hours) for which metric table plots should be created
  barchart:
    plot: true  # whether to create barchart plots
    metric_subset: [KGE, NSE, CORR, NNSE, PBIAS]
    lead_times: [1, 5, 10, 18, 1-5, 6-10, 11-18, "all_aggregated"] # list of lead times (in hours) for which barchart plots should be created
```

(config-nwm-yaml)=
#### `config_nwm.yaml`

Sample config for verifying operational NWM v3 forecasts across multiple locations and domains using data retrieved from Google Cloud Storage (GCS).

```yaml
general: # define which of the 5 steps to run; each step can be run independently, assuming data from previous steps (from previous runs) are available for use
  steps:
    fetch_fcst_data: true
    fetch_obs_data: true
    pair_data: true
    compute_metrics: true
    plot_metrics: true

  location_set_name: calib_basin_group1 # user-specified name for the set of locations
  variable_name: streamflow # currently only 'streamflow' is supported
  nwm_configuration: short_range   # Currently, only short_range, short_range_alaska, short_range_hawaii, and short_range_puertorico are supported
  dataset_name: [v3_sep, v3_oct] # user-specified name of datasets (used for creating sub-folders for datasets and plots) 
  nwm_version: [nwm30, nwm30] # list of NWM versions; must have the same length as 'dataset_name'.
  forecast_start_date: ['2024-09-01 00:00:00', '2024-10-01 00:00:00'] # list of start date for forecast verification period; list must have the same length as 'dataset_name'
  forecast_end_date: ['2024-09-30 23:00:00', '2024-10-30 23:00:00'] # list of end date for forecast verification period; list must have the same length as 'dataset_name'

file_paths:  
  base_dir: ~/repos/nwm-eval-mgr/data/  # root directory to store the downloaded NWM forecast and flow observation data
  location_list_file: "{base_dir}/inputs/gage_files/usgs_gages_link_CONUS_calib100.csv" # [optional] file path for the list of locations (e.g., gage IDs or NWM link IDs)
  crosswalk_file: '{base_dir}/inputs/gage_files/usgs_{nwm_version}_crosswalk_all_domains.parquet' # parquet files containing the crosswalk between NWM feature_id and usgs gage id  
  fcst_config_file: '{base_dir}/inputs/nwm_forecast_configuration.yaml' # NWM forecast configuration file  
  output_dir: '{base_dir}/outputs/{location_set_name}' # output directory to store all datasets and plots

nwm_forecast:
  data_source: GCS    # Specifies the source to retrieve the model forecast or simulation data. Currently supported options: GCS, ngenCERF, ngenSIM
  fetch_fcst: [true, true]  # whether to fetch the forecast data for each dataset listed in ['general']['dataset_name']  
  output_type: channel_rt
  t_minus: [0, 1, 2]  # Only used if an assimilation run is selected
  kerchunk_method: local  
  process_by_z_hour: true  
  stepsize: 100  # Only used if PROCESS_BY_Z_HOUR = False. Controls how many files are processed in memory at once
  ignore_missing_file: false  # If True, the missing file(s) will be skipped and the process will resume; if False, TEEHR will fail if a missing NWM file is encountered
  overwrite_output: false  # If True, existing output files will be overwritten; if False, existing files are retained
  memory_per_worker_gb: 3  # configurable memory (in GB) assigned to each worker

flow_observation:
  usgs: # flow obs retrieved will be stored at [data_dir_root]/[location_set_name]/usgs
    chunk_by: day   # data are saved in parquet files by day/month/year
    overwrite_output: false  # If True, existing output files will be overwritten; if False, existing files are retained
    memory_per_worker_gb: 3  # configurable memory (in GB) assigned to each worker

pair_data:  
  overwrite: true # whether to overwrite existing joined parquet files
  group_size: 200 # break large location list into smaller groups (for pair_data and cacl_metrics steps) to avoid potential memory issues and to speed up processing

metrics:  
  overwrite: true # whether to overwrite existing metric files
  library: nwm.eval # library to be used for metric calculation; currently supported options: teehr, nwm.eval
  metric_subset: 'all' # list of metrics to be calculated; if set to 'all', all available metrics will be calculated 
  metric_exclude: [PKBIAS, PKTE, EVBIAS, FBIAS] # list of metrics to be excluded from calculation (leave blank if no need to exclude any metrics)
  threshold_categorical:
    value: 0.9 # threshold value to be used for categorical metrics in nwm.eval 
    type: quantile # type of threshold for categorical metrics in nwm.eval; options are 'quantile' or 'absolute'
  threshold_event:
    value: 0.9 # threshold value to be used for event-based metrics in nwm.eval
    type: quantile # type of threshold for event-based metrics in nwm.eval; options are 'quantile' or 'absolute'
  lead_times: [all, 1-5, 6-10, 11-18] # list of lead times (in hours) for which metrics should be calculated for

# For each type of plots (histogram, boxplot, spatial map), 
#   1) 'metric_subset' must be a subset of metrics defined for calculation (i.e., 'metric_subset' defined in Section 'metrics')
#   2) 'lead_times' must be a subset of lead times defined for metrics calculation (i.e., 'lead_times' defined in Section 'metrics')
plots:
  histogram:
    plot: true # whether to create histogram plots    
    metric_subset: [KGE, NSE, CORR, NNSE] # list of metrics to create histogram plots for
    binning: # for each metric, define list of bin edges for generating the histogram plot
      KGE: [-inf, -1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
      NSE: [-inf, -1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
      NNSE: [0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
      CORR: [-1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]    
    lead_times: [1, 3, 5, 10, 15, 18, 1-5, 6-10, 11-18] # list of lead times (in hours) to create histograms for
    tag:  # optional string that gets added to the filename of histogram plots to differentiate between runs

  boxplot: 
    plot: true
    metric_subset: [KGE, NSE, CORR, NNSE]   
    scaling:  # Define an appropriate range (min/max) for each metric to scale the values for better visualization of boxplot
      KGE: [-0.5, 1]
      NSE: [-0.5, 1]
      CORR: [-0.5, 1]
      NNSE: [0, 1]
      RSR: [0, 20]
      MAE: [0, 5]
      RMSE: [0, 20]
      PBIAS: [-100, 300]
    lead_times: [1, 3, 5, 10, 15, 18, 1-5, 6-10, 11-18]
    show_outliers: false
    tag:

  spatial_map:
    plot: true    
    metric_subset: [KGE, NSE, CORR, NNSE]    
    scaling: # Define an appropriate range (min/max) for each metric to scale the values for the spatial map
      KGE: [-0.5, 1]
      NSE: [-0.5, 1]
      CORR: [-0.5, 1]
      NNSE: [0, 1]
      RSR: [0, 20]
      MAE: [0, 20]
      RMSE: [0, 20]
      PBIAS: [-100, 300]
    lead_times: [1, 3, 5, 10, 15, 18, 1-5, 6-10, 11-18]
    tag:
```

(config-ngensim-yaml)=
#### `config_ngensim.yaml`

Sample config for evaluating large-scale NGEN simulations (e.g., from regionalization) across multiple locations, VPUs, or NWM domains.

```yaml
general:   
  steps: # define which of the 5 steps to run; each step can be run independently,
    fetch_fcst_data: true
    fetch_obs_data: true
    pair_data: true
    compute_metrics: true
    plot_metrics: true
  domain: conus  # Define NWM domain. Supported options: conus, ak, hi, prvi
  assemble_domain: false # whether to assemble metrics from various VPUs for the entire domain and plot domain-level metrics
  location_set_name: vpu_03S  # user-specified name for the set of locations
  location_type: usgs_gage # location type
  location_filter: # filter locations based on column and value in the gage crosswalk file; if null, all locations in the crosswalk file will be used, unless location_list or location_list_file is specified
    columns: ["vpu_id", "status"]  
    values: ["03S", "USGS-active"]
  variable_name: streamflow # currently only 'streamflow' is supported
  nwm_configuration: ngen_simulation    
  dataset_name: [gower, kmeans] # user-specified name of datasets (e.g., formualtion or algorithm name)
  nwm_version: [ngen, ngen] # list of NWM versions; must have the same length as 'dataset_name'
  forecast_start_date: ['2012-10-01 00:00:00', '2012-10-01 00:00:00'] # list of start dates for simulation; must be same length as 'dataset_name'
  forecast_end_date: ['2012-10-01 10:00:00', '2012-10-01 10:00:00'] # list of end dates for simulation; must be same length as 'dataset_name'
  eval_start_date: ['2012-10-01 03:00:00', '2012-10-01 03:00:00'] # start date for evaluation period, only used for ngenSIM
  eval_end_date: ['2012-10-01 10:00:00', '2012-10-01 10:00:00'] # end date for evaluation period, only used for ngenSIM
  separate_calibrated: true # whether to distinguish calibrated and regionalized locations in the evaluation

file_paths:
  base_dir: ~/repos/nwm-eval-mgr/data/ # root directory to store data/outputs for verification
  crosswalk_file: '{base_dir}/inputs/nhf/usgs_{nwm_version}_crosswalk_{domain}.parquet' # crosswalk file mapping gage IDs to NWM/ngen link IDs
  fcst_data_file: '{base_dir}/inputs/troute_output_201210010000_{dataset_name}.nc' # forecast data directory (must be specified when nwm_forecast.data_source is set to ngenCERF)
  calib_param_file: '{base_dir}/../../nwm-region-mgr/data/inputs/region/pseudo_calib_params/sampled_params_{domain}.csv' # calibration parameters file (used when separate_calibrated is True); must have column 'gage_id'
  output_dir: '{base_dir}/outputs/{location_set_name}' # output directory to store all datasets, metrics and plots

nwm_forecast:
  data_source: ngenSIM   # Specifies the source to retrieve the model forecast or simulation data. Currently supported options: GCS, ngenCERF, ngenSIM

flow_observation:
  usgs: # flow obs retrieved will be stored at [data_dir_root]/[location_set_name]/usgs
    chunk_by: month   # data are saved in parquet files by day/month/year
    overwrite_output: True  # If True, existing output files will be overwritten; if False, existing files are retained
    memory_per_worker_gb: 3  # configurable memory (in GB) assigned to each worker

pair_data:  
  overwrite: true # whether to overwrite existing joined parquet files
  group_size: 200 # break large location list into smaller groups (for pair_data and cacl_metrics steps) to avoid potential memory issues and to speed up processing

metrics:  
  overwrite: true # whether to overwrite existing metric files
  library: nwm.eval # currently supported options: teehr, nwm.eval
  metric_subset: [KGE, NSE, CORR, NNSE, PKBIAS, PKTE, EVBIAS] # subset of metrics to calculate; if null, all available metrics will be calculated
  threshold_categorical:
    value: 0.9 # threshold value to be used for categorical metrics in nwm.eval 
    type: quantile # type of threshold for categorical metrics in nwm.eval; options are 'quantile' or 'absolute'
  threshold_event:
    value: 0.9 # threshold value to be used for event-based metrics in nwm.eval
    type: quantile # type of threshold for event-based metrics in nwm.eval; options are 'quantile' or 'absolute'
  lead_times: ['all'] # list of lead times (in hours) for which metrics should be calculated for  
  file_format: parquet # file format for metrics. Options are: parquet, csv. Default is parquet.

plots:
  histogram:
    plot: true
    metric_subset: [KGE, NSE, CORR, NNSE]
    binning:
      KGE: [-inf, -1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
      NSE: [-inf, -1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
      NNSE: [0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
      CORR: [-1, -0.5, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
    lead_times: ['all']

  boxplot: 
    plot: true
    metric_subset: [KGE, NSE, CORR, NNSE]
    scaling:
      KGE: [-0.5, 1]
      NSE: [-0.5, 1]
      CORR: [-0.5, 1]
      NNSE: [0, 1]
      RSR: [0, 20]
      MAE: [0, 5]
      RMSE: [0, 20]
      PBIAS: [-100, 300]

    lead_times: [1, 3, 5, 10, 15, 18, 1-5, 6-10, 11-18]
    show_outliers: false

  spatial_map:
    plot: true
    metric_subset: [KGE, NSE, CORR, NNSE]
    scaling:
      KGE: [-0.5, 1]
      NSE: [-0.5, 1]
      CORR: [-0.5, 1]
      NNSE: [0, 1]
      RSR: [0, 20]
      MAE: [0, 20]
      RMSE: [0, 20]
      PBIAS: [-100, 300]
    lead_times: [1, 3, 5, 10, 15, 18, 1-5, 6-10, 11-18]
```
### Schemas


#### `BarChartConfig` (inherits from `BasePlotConfig`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |

#### `BasePlotConfig` (inherits from `LeadTimesMixin`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| plot | bool \| NoneType | Whether to generate this type of plot. If False, the script will skip generating this type of plot. If True, the script will generate this type of plot for the specified lead times. | False | False |
| metric_subset | str \| List[str] \| NoneType | List of metric names to include in the plots. If not defined, all available metrics will be included in the plots.  | None | ['NSE', 'KGE'] |
| tag | str \| NoneType | Optional tag to include in the plot titles and filenames. This can be used to distinguish different configurations in the plot outputs. |  |  |

#### `BoxPlotConfig` (inherits from `BasePlotConfig`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| show_outliers | bool \| NoneType | Whether to show outliers in box plots. If True, outliers will be shown as individual points. If False, outliers will be omitted. | False | False |

#### `FilePathsConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| base_dir | Path | Root directory to store data and outputs for the evaluation. The script will create subdirectories under this base directory for different datasets and types of outputs (e.g., noah_cfes, usgs, joined, metrics, plots). | None | ~/ngen_evaluation/ |
| location_list_file | Path \| str \| NoneType | Path to a file containing the list of locations to evaluate, only used if 'general.location_list' is not provided. If neither is provided, locations from the crosswalk file will be used, filtered by 'general.location_filter'. | None | ~/location_list.csv |
| crosswalk_file | Path \| str \| Dict[str, Path] \| Dict[str, str] | Path to a crosswalk file or a dictionary of crosswalk files, corresponding to different nwm versions. The crosswalk file maps location identifiers to other relevant information. | None | ~/crosswalk.csv |
| fcst_config_file | str \| Path \| NoneType | Path to the forecast configuration file. This file defines the parameters for different NWM configurations. For each forecast configuration, a list that specify the following parameters (in order): cycle_start: start time of forecast cycles in Zulu time or UTC (e.g., 0Z);cycle_end: end time of forecast cycles in Zulu time or UTC (e.g., 23Z);cycle_freq: frequency of forecast cycles in hours (e.g., 1);fcst_win: forecast window in hours (e.g., 18);fcst_timestep: forecast timestep in hours (e.g., 1); | None | data/inputs/nwm_forecast_configuration.yaml |
| fcst_data_file | Path \| str \| Dict[str, Path] \| Dict[str, str] \| NoneType | Path to the forecast data file or a dictionary of forecast data files. | None | 01123000_output.csv |
| fcst_data_dir | Path \| str \| Dict[str, Path] \| Dict[str, str] \| NoneType | Path to the directory containing forecast data files or a dictionary of directories. | None | data/inputs/hindcasts/ |
| obs_data_file | Path \| str \| NoneType | Path to the observation data file. Both obs_data_file and obs_data_dir can be specified. The run will read all .csv and .parquet files in obs_data_dir and obs_data_file and remove duplicates.If neither obs_data_file nor obs_data_dir is provided, an observation data source must be specified in the 'flow_observation.usgs' section. | None | data/inputs/obs/01123000_hourly_discharge.csv |
| obs_data_dir | Path \| str \| NoneType | ("Path to the observation data directory where one or more observation data files are stored. The run will look for all .csv and .parquet files in this directory. Each file can contain observation data for a single location (with the filename starting with the location identifier), or multiple locations with a 'location_id' column specifying the location identifiers.",) | None | data/inputs/obs/ |
| calib_param_file | Path \| str \| NoneType | Path to the calibration parameter file. | None | data/inputs/calib_params.csv |
| txdot_gage_file | Path \| str \| NoneType | Path to the TxDOT gage file. This is only needed if evaluating TxDOT locations, for which streamflow observations are retrieved differently than USGS gages. If not provided, the default TxDOT list defined in settings.py will be used.  | None | data/inputs/gage_files/tx_gauges.csv |
| output_dir | str \| Path | Directory to save outputs such as paired data, computed metrics, and plots.  | None | ngen_evaluation/outputs/usgs_01123000/ |

#### `FlowObservationConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| usgs | USGSConfig \| NoneType | Configuration for USGS flow observations. If omitted, obs_data_file and/or obs_data_dir must be provided in file_paths section,  | None |  |

#### `GeneralConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| steps | Dict[str, bool] | Dictionary specifying which steps to run. Keys are step names (e.g., 'fetch_fcst_data', 'fetch_obs_data', 'pair_data', 'compute_metrics', 'plot_metrics'), and values are booleans indicating whether to run the step.Note that these steps need to run in order, since some steps depend on the output of previous steps (e.g., one cannot compute metrics without first fetching data and pairing it). | {'fetch_fcst_data': True, 'fetch_obs_data': True, 'pair_data': True, 'compute_metrics': True, 'plot_metrics': True} | {'fetch_fcst_data': True, 'fetch_obs_data': True, 'pair_data': True, 'compute_metrics': True, 'plot_metrics': True} |
| domain | str = conus \| hi \| ak \| prvi \| NoneType | Domain for the evaluation. Valid options are 'conus', 'hi', 'ak', 'prvi' (case insensitive). | None | conus |
| assemble_domain | bool \| NoneType | Whether to assemble results from different VPUs across domains. This is only applicable when domain is 'conus', since the CONUS domain is currently divided into VPUs while other domains are not. If True, the script will look for metric files from each VPU, concatenate them, and save the assembled metric file for the entire CONUS domain. | None | False |
| location_set_name | str | User-specified name for the set of locations (e.g., a specific VPU or a cluster from a regionalization). This will be used in naming output files and directories. | usgs_01123000 | vpu_03S |
| location_list | List[str] \| NoneType | List of specific locations to include in the evaluation. If None, all locations in the crosswalk file will be used. | None | ['01123000', '01123500'] |
| location_type | str = usgs_gage \| nwm30_link \| nwm22_link | Type of locations to evaluate. Valid options are 'usgs_gage', 'nwm30_link', and 'nwm22_link'. This will determine which columns in the crosswalk file to use for filtering locations and for merging forecast and observation data. | usgs_gage | usgs_gage |
| location_filter | LocationFilter \| NoneType | Optional configuration for filtering locations based on column values in the crosswalk file. If provided, only locations that match the specified column-value pairs will be included in the evaluation. | None | {'columns': ['vpu_id', 'status'], 'values': ['03S', 'USGS-active']} |
| location_group_size | int \| NoneType | Number of locations to process in each group when pairing forecast and observation data. This is used to manage memory usage during the pairing step. If None, all locations will be processed in a single group. | 200 | 100 |
| variable_name | str | Name of the variable to evaluate. Currently only 'streamflow' is supported, but this field is included for future extensibility. | streamflow | streamflow |
| nwm_configuration | str | Name of the NWM configuration to evaluate. This can be 'ngen' for ngen-based simulations or match one of the configurations defined in the forecast configuration file specified by 'file_paths.fcst_config_file'. | None | ngen |
| dataset_name | List[str] | User-specified name(s) for the dataset(s) to evaluate (e.g., formulation name or regionalization algorithm). This will be used in naming output files and directories. If evaluating multiple datasets, this should be a list of names with the same length as 'nwm_version', 'forecast_start_date', and 'forecast_end_date'. | None | ['noah_cfes', 'noah_topmodel'] |
| nwm_version | List[str] | List of NWM versions to evaluate. Valid options include 'ngen', 'nwm30', 'nwm22', etc. This should be a list of the same length as 'dataset_name', where each entry corresponds to the NWM version for the dataset with the same index in 'dataset_name'. | None | ['ngen', 'nwm30'] |
| forecast_start_date | List[str] | List of start dates for the forecast data to evaluate. This should be a list of the same length as 'dataset_name', where each entry corresponds to the start date for the dataset with the same index in 'dataset_name' | None | ['2022-12-01 00:00:00', '2022-12-15 00:00:00'] |
| forecast_end_date | List[str] | List of end dates for the forecast data to evaluate. This should be a list of the same length as 'dataset_name', where each entry corresponds to the end date for the dataset with the same index in 'dataset_name' | None | ['2022-12-31 00:00:00', '2023-01-15 00:00:00'] |
| eval_start_date | List[str] \| NoneType | List of start dates for the evaluation period. This should be a list of the same length as 'dataset_name', where each entry corresponds to the start date for the evaluation period of the dataset with the same index in 'dataset_name'. If not provided, the evaluation will start from the earliest available date in the paired forecast and observation data for each dataset. | None | ['2022-12-11 00:00:00', '2022-12-25 00:00:00'] |
| eval_end_date | List[str] \| NoneType | List of end dates for the evaluation period. This should be a list of the same length as 'dataset_name', where each entry corresponds to the end date for the evaluation period of the dataset with the same index in 'dataset_name'. If not provided, the evaluation will end at the latest available date in the paired forecast and observation data for each dataset. | None | ['2022-12-31 00:00:00', '2023-01-15 00:00:00'] |
| separate_calibrated | bool \| NoneType | Whether to distinguish calibrated and regionalized locations in the evaluation | None | False |

#### `HistogramConfig` (inherits from `BasePlotConfig`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| binning | Dict[str, List[int \| float]] \| NoneType | Dictionary specifying the binning for histogram plots. Keys are metric names, and values are lists of numbers defining the bin edges for the corresponding metric. If a metric is not included in this dictionary, binning is determined by dividing the range of metric values into 8 equal-width bins.  | {'NSE': [-1, -0.5, 0, 0.5, 1], 'KGE': [-1, -0.5, 0, 0.5, 1]} | {'NSE': [-1, -0.5, 0, 0.5, 1], 'KGE': [-1, -0.5, 0, 0.5, 1]} |

#### `LeadTimesMixin`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| lead_times | List[str] \| NoneType | List of lead times to compute metrics or make plots for. Each lead time can be specified as an integer (e.g., 6), a numeric string (e.g., '6'), or a range string (e.g., '1-6'). `all` represents all available individual lead times for a given nwm configuration. Range strings will be expanded to include all individual lead times within the range. `all_aggregated` represents a range that includes all lead times for a given nwm configuration, (e.g., 1-18 for short_range).Note lead times defined in `plots` must be a subset of those defined in `metrics`. | None | ['all', '1-5', '5-10', '10-15', 'all_aggregated'] |

#### `LocationFilter`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| columns | str \| List[str] \| NoneType | Column name(s) in the crosswalk file to filter on. Can be a single string or a list of strings. | None | vpu_id |
| values | str \| List[str] \| NoneType | Value(s) to filter on for the corresponding columns. Can be a single string or a list of strings. | None | 03S |

#### `MetricsConfig` (inherits from `LeadTimesMixin`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| overwrite | bool \| NoneType | Whether to overwrite existing metric files.  | True | False |
| library | str \| NoneType | Library to use for metric computation. Valid options: nwm.eval, teehr.  | nwm.eval | nwm.eval |
| metric_subset | str \| List[str] | Subset of metrics to compute. Can be 'all' or a list of metric names. If 'all', all available metrics in the specified library will be computed. If a list of metric names is provided, only those metrics will be computed. | None | all |
| metric_exclude | List[str] \| NoneType | List of metric names to exclude from metric_subset for computation.  | None | ['HSEG_FDC', 'MSEG_FDC', 'LSEG_FDC'] |
| threshold_categorical | Dict[str, float \| str] \| NoneType | Threshold for categorical metrics. Valid options for type are 'quantile' and 'absolute'. If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. If 'absolute', the threshold will be the specified absolute flow value. | {'value': 0.9, 'type': 'quantile'} | {'value': 0.9, 'type': 'quantile'} |
| threshold_event | Dict[str, float \| str] \| NoneType | Threshold for event-based metrics. Valid options for type are 'quantile' and 'absolute'. If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. If 'absolute', the threshold will be the specified absolute flow value. | {'value': 0.9, 'type': 'quantile'} | {'value': 0.9, 'type': 'quantile'} |
| file_format | str \| NoneType | File format for output files. Valid options are 'parquet' and 'csv'. | parquet | parquet |

#### `NWMForecastConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| data_source | str = ngenCERF \| ngenSIM \| hindcast \| GCS | Data source for the NWM forecast. This specifies the source from which forecast data will be retrieved.Valid options are: 'ngenCERF' for ngen-based single-location forecasts for a single reference time (T0), 'hindcast' for ngen-based single-location hindcast data for multiple reference times (T0), 'ngenSIM' for large-scale ngen-based simulations (e.g., across a VPU from regionalization), 'GCS' for large-scale operational NWM forecasts on Google Cloud Storage. | None | ngenCERF |
| fetch_fcst | List[bool] \| NoneType | List of booleans indicating whether to fetch forecast data for each dataset. If False, forecast data will be retrieved regardless of whether it already exists locally. Otherwise, skip fetching if forecast data file already exists locally.  | [True] | [True] |
| output_type | str \| NoneType | Type of NWM output to retrieve. Currently only 'channel_rt' is supported. Only applicable when data_source='GCS'.  | channel_rt | channel_rt |
| t_minus | List[int] \| NoneType | List of integers indicating the T-minus hours for which to retrieve NWM forecasts. Only applicable when data_source='GCS' and nwm_configuration is an AnA run (analysis & assimilation). | [0, 1, 2] | [0] |
| kerchunk_method | str \| NoneType | Specifies the preference in creating Kerchunk reference json files. Only needed for data_source = 'GCS'. 'local' - always create new json files from netcdf files in GCS and save locally, if they do not already exist; 'remote' - read the CIROH pre-generated jsons from s3, ignoring any that are unavailable; 'auto' - read the CIROH pre-generated jsons from s3, and create any that are unavailable, storing locally | local | zarr |
| process_by_z_hour | bool \| NoneType | Only applicable when data_source='GCS'. If True, NWM files will be processed by z-hour per day. If False, files will be processed in chunks (defined by STEPSIZE). This can help if you want to read many reaches at once (all ~2.7 million for medium range for example). | True | False |
| stepsize | int \| NoneType | Only applicable when data_source='GCS' and process_by_z_hour=False. Controls how many files are processed in memory at once. Higher values can increase performance at the expense on memory.  | 100 | 50 |
| ignore_missing_file | bool \| NoneType | Only applicable when data_source='GCS'. If True, the missing file(s) will be skipped and the process will resume. If False, TEEHR will fail if a missing NWM file is encountered. | True | False |
| overwrite_output | bool \| NoneType | Whether to overwrite existing forecast data files. If False, the script will check if the forecast data file already exists locally before attempting to fetch it. If True, the script will fetch the forecast data and overwrite any existing local file with the same name. | False | False |
| memory_per_worker_gb | int \| NoneType | Configurable memory (in GB) assigned to each worker or process. | 3 | 1 |

#### `PairDataConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| overwrite | bool \| NoneType | Whether to overwrite existing paired data files. If False, the script will check if the paired data file already exists locally before attempting to pair data. If True, the script will pair the data and overwrite any existing local file with the same name. | True | False |
| group_size | int \| NoneType | Number of locations to process in each group when pairing forecast and observation data. This is used to manage memory usage during the pairing step. If None, all locations will be processed in a single group. | 200 | 100 |

#### `PlotsConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| histogram | HistogramConfig | Configuration for histogram plots. | lead_times=None plot=False metric_subset=None tag='' binning={'NSE': [-1, -0.5, 0, 0.5, 1], 'KGE': [-1, -0.5, 0, 0.5, 1]} | lead_times=None plot=False metric_subset=None tag='' binning={'NSE': [-1, -0.5, 0, 0.5, 1], 'KGE': [-1, -0.5, 0, 0.5, 1]} |
| boxplot | BoxPlotConfig | Configuration for box plot. | lead_times=None plot=False metric_subset=None tag='' show_outliers=False | lead_times=None plot=False metric_subset=None tag='' show_outliers=False |
| spatial_map | SpatialMapConfig | Configuration for spatial map plots. | lead_times=None plot=False metric_subset=None tag='' scaling={'NSE': [-0.5, 1.0], 'KGE': [-0.5, 1.0]} | lead_times=None plot=False metric_subset=None tag='' scaling={'NSE': [-0.5, 1.0], 'KGE': [-0.5, 1.0]} |
| time_series | TimeSeriesConfig | Configuration for time series plots. | reference_times=None lead_times=None plot=False metric_subset=None tag='' | reference_times=None lead_times=None plot=False metric_subset=None tag='' |
| metric_table | TablePlotConfig | Configuration for metric table plots. | lead_times=None plot=False metric_subset=None tag='' | lead_times=None plot=False metric_subset=None tag='' |
| barchart | BarChartConfig | Configuration for bar chart plots. | lead_times=None plot=False metric_subset=None tag='' | lead_times=None plot=False metric_subset=None tag='' |

#### `ReferenceTimesMixin`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| reference_times | List[datetime] \| NoneType | List of reference times (T0s) to compute metrics or make plots for. Each reference time can be specified as a datetime object or a string in a format recognized by pandas.to_datetime. | None | ['2022-12-01 00:00:00', '2022-12-15 00:00:00'] |

#### `SpatialMapConfig` (inherits from `BasePlotConfig`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| scaling | Dict[str, List[int \| float]] \| NoneType | Dictionary specifying the scaling for spatial maps. Keys are metric names, and values are lists of numbers defining the scaling range for the corresponding metric. If a metric is not included in this dictionary, metric data will not be scaled and hence the resulting spatial map may be difficult to interpret if there are extreme outliers. | {'NSE': [-0.5, 1.0], 'KGE': [-0.5, 1.0]} | {'NSE': [-0.5, 1.0], 'KGE': [-0.5, 1.0]} |

#### `TablePlotConfig` (inherits from `BasePlotConfig`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |

#### `TimeSeriesConfig` (inherits from `BasePlotConfig, ReferenceTimesMixin`)

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |

#### `USGSConfig`

| Field | Type(s) | Description | Default | Example(s) |
| --- | --- | --- | --- | --- |
| chunk_by | str = day \| month \| year | How downloaded data are chunked into parquet files. | month | month |
| overwrite_output | bool \| NoneType | If True, existing output files are overwritten. If False, existing files are retained. | True | True |
| memory_per_worker_gb | int \| NoneType | Memory assigned to each worker in GB. | 3 | 3 |