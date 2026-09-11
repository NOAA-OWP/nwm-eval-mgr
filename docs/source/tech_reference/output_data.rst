Schemas
=======

.. _forecast_data:

forecast_data
-------------

Raw forecast data for a given NWM dataset (here defined by forecast time period, NWM version and configuration, e.g., v3_oct.nwm30.short_range), which includes the forecasted values for all locations and time steps.

Sample file path: ``calib_basin_group1/v3_oct/short_range/20241001T00.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "value", "reference_time", "location_id", "value_time", "configuration", "variable_name", "measurement_unit"
   "1.8399999141693115", "2024-10-01 00:00:00", "nwm30-8134650", "2024-10-01 01:00:00", "short_range", "streamflow", "m3/s"
   "0.4099999964237213", "2024-10-01 00:00:00", "nwm30-23963741", "2024-10-01 01:00:00", "short_range", "streamflow", "m3/s"
   "0.3799999952316284", "2024-10-01 00:00:00", "nwm30-15576309", "2024-10-01 01:00:00", "short_range", "streamflow", "m3/s"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - value
     - Forecasted value for a specific location and time step.
     - float32

   * - reference_time
     - Reference time of the forecast.
     - datetime64[ms]

   * - location_id
     - Location identifier (e.g., NextGen hydrofabric feature ID).
     - object

   * - value_time
     - Time of the forecasted value.
     - datetime64[ms]

   * - configuration
     - NWM configuration of the forecast.
     - object

   * - variable_name
     - Name of the forecasted variable.
     - object

   * - measurement_unit
     - Unit of the forecasted value.
     - object




.. _metrics:

metrics
-------

Metrics computed for a given NWM dataset (here defined by forecast time period, NWM version and configuration, e.g., v3_oct.nwm30.short_range)

Sample file path: ``calib_basin_group1/metrics/v3_oct.nwm30.short_range.metrics.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "CORR", "NSE", "NNSE", "NSElog", "NSEwt", "KGE", "MAE", "RMSE", "PBIAS", "RSR", "HSEG_FDC", "MSEG_FDC", "LSEG_FDC", "POD", "FAR", "CSI", "lead_group", "primary_location_id"
   "0.900238037109375", "0.5106164900337751", "0.6714187402428521", "0.38159789582989834", "0.4461071929318367", "0.8427430901779777", "0.02477925270795822", "0.030133018270134926", "11.738386005163193", "0.6995594501495361", "6.77579939365387", "-18.028101325035095", "-11.541274189949036", "1.0", "0.7238095238095238", "0.2761904761904762", "1", "usgs-01362370"
   "0.6030905246734619", "-0.123655873992226", "0.4708860848156704", "-3.394126575737676", "-1.758891224864951", "0.504481708747024", "0.12183412909507751", "0.1523588001728058", "-3.8535218685865402", "1.0600262880325317", "7.445662468671799", "49.104440212249756", "-13125.10986328125", "0.7647058823529411", "0.7094972067039106", "0.26666666666666666", "1", "usgs-01365000"
   "0.724666953086853", "-7.859279237533739", "0.10142729259488406", "-6.2346414989182435", "-7.046960368225991", "0.3260914924230085", "0.018314972519874573", "0.019198978319764137", "54.1209876537323", "2.976454257965088", "42.32468605041504", "3.482237085700035", "100.0", "1.0", "0.9052969502407705", "0.09470304975922954", "1", "usgs-01390450"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - CORR
     - Correlation coefficient between forecasted and observed values.
     - float32

   * - NSE
     - Nash-Sutcliffe Efficiency coefficient between forecasted and observed values.
     - float64

   * - NNSE
     - NNSE
     - float64

   * - NSElog
     - Nash-Sutcliffe Efficiency coefficient computed on the logarithm of forecasted and observed values.
     - float64

   * - NSEwt
     - Weighted score of NSE and NSElog.
     - float64

   * - KGE
     - Kling-Gupta Efficiency coefficient between forecasted and observed values.
     - float64

   * - MAE
     - Mean Absolute Error between forecasted and observed values.
     - float32

   * - RMSE
     - Root Mean Square Error between forecasted and observed values.
     - float32

   * - PBIAS
     - Percent Bias between forecasted and observed values.
     - float64

   * - RSR
     - Ratio of the RMSE to the standard deviation of observed values.
     - float32

   * - HSEG_FDC
     - Flow Duration Curve error metric for the highflow segment.
     - float64

   * - MSEG_FDC
     - Flow Duration Curve error metric for the middle segment.
     - float64

   * - LSEG_FDC
     - Flow Duration Curve error metric for the lowflow segment.
     - float64

   * - POD
     - Probability of Detection.
     - float64

   * - FAR
     - False Alarm Ratio.
     - float64

   * - CSI
     - Critical Success Index.
     - float64

   * - lead_group
     - Lead time group.
     - object

   * - primary_location_id
     - Primary location identifier (e.g., USGS gage ID).
     - object




.. _obs_data:

obs_data
--------

Observation data, which includes the observed values for all locations and time steps.

Sample file path: ``calib_basin_group1/usgs/2024-10-01.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "location_id", "reference_time", "value_time", "value", "variable_name", "measurement_unit", "configuration"
   "usgs-01048000", "2024-10-01 00:00:00", "2024-10-01 00:00:00", "6.994260787963867", "streamflow", "m3/s", "usgs_gage_data"
   "usgs-01048000", "2024-10-01 01:00:00", "2024-10-01 01:00:00", "6.880993843078613", "streamflow", "m3/s", "usgs_gage_data"
   "usgs-01048000", "2024-10-01 02:00:00", "2024-10-01 02:00:00", "6.880993843078613", "streamflow", "m3/s", "usgs_gage_data"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - location_id
     - Location identifier (e.g., USGS gage ID).
     - object

   * - reference_time
     - Reference time of the observation.
     - datetime64[ns]

   * - value_time
     - Time of the observed value.
     - datetime64[ns]

   * - value
     - Observed value for a specific location and time step.
     - float32

   * - variable_name
     - Name of the observed variable.
     - category

   * - measurement_unit
     - Unit of the observed value.
     - object

   * - configuration
     - NWM configuration of the observation.
     - object




.. _pairs:

pairs
-----

Paired data for the short-range forecast (v3_oct.nwm30.short_range) in the calib_basin_group1 dataset, which includes the forecasted and observed values for each location and time step.

Sample file path: ``calib_basin_group1/joined/v3_oct.nwm30.short_range.joined.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "primary_location_id", "primary_value", "secondary_location_id", "secondary_value", "value_time", "configuration", "measurement_unit", "variable_name", "reference_time", "lead_time"
   "usgs-02408540", "1.9765158891677856", "nwm30-22274612", "2.240000009536743", "2024-10-12 03:00:00", "short_range", "m3/s", "streamflow", "2024-10-11 22:00:00", "5.0"
   "usgs-02408540", "1.9765158891677856", "nwm30-22274612", "2.190000057220459", "2024-10-12 03:00:00", "short_range", "m3/s", "streamflow", "2024-10-11 14:00:00", "13.0"
   "usgs-02408540", "1.9765158891677856", "nwm30-22274612", "2.190000057220459", "2024-10-12 03:00:00", "short_range", "m3/s", "streamflow", "2024-10-11 10:00:00", "17.0"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - primary_location_id
     - Primary location identifier (e.g., USGS gage ID).
     - object

   * - primary_value
     - Forecasted value for the primary location.
     - float32

   * - secondary_location_id
     - Secondary location identifier (e.g., USGS gage ID).
     - object

   * - secondary_value
     - Observed value for the secondary location.
     - float32

   * - value_time
     - Time of the forecasted and observed values.
     - datetime64[us]

   * - configuration
     - NWM configuration of the forecast.
     - object

   * - measurement_unit
     - Unit of the forecasted and observed values.
     - object

   * - variable_name
     - Name of the forecasted variable.
     - object

   * - reference_time
     - Reference time of the forecast.
     - datetime64[us]

   * - lead_time
     - Lead time of the forecast.
     - float64




.. toctree::
   :maxdepth: 2