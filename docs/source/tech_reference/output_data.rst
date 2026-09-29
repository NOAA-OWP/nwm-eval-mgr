Schemas
=======

.. _forecast_data:

forecast_data
-------------

Simulation data for a given NWM dataset (e.g., test_kmeans), including the simulated values for all locations and time steps.

Sample file path: ``outputs/eval/vpu_03S/test_kmeans/ngen_simulation/20121001T03-20121001T10.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "value_time", "location_id", "value", "reference_time", "configuration", "variable_name", "measurement_unit"
   "2012-10-01 03:00:00", "ngen-1271704100114434", "0.5120489597320557", "2012-10-01 03:00:00", "ngen_simulation", "streamflow", "m3/s"
   "2012-10-01 04:00:00", "ngen-1271704100114434", "0.765230655670166", "2012-10-01 04:00:00", "ngen_simulation", "streamflow", "m3/s"
   "2012-10-01 05:00:00", "ngen-1271704100114434", "0.7610368728637695", "2012-10-01 05:00:00", "ngen_simulation", "streamflow", "m3/s"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - value_time
     - Time of the simulated value.
     - datetime64[ns]

   * - location_id
     - Location identifier for the simulated value.
     - object

   * - value
     - Simulated value for a specific location, time and reference time.
     - float32

   * - reference_time
     - Reference time for the simulation (same as value_time for simulations).
     - datetime64[ns]

   * - configuration
     - Configuration for the simulation or forecast (e.g., ngen_simulation, short_range, medium_range_blend).
     - object

   * - variable_name
     - Name of the simulated variable (e.g., streamflow).
     - object

   * - measurement_unit
     - Measurement unit of the simulated variable.
     - object



.. _metrics:

metrics
-------

Metrics computed for a given dataset (e.g., test_kmeans)

Sample file path: ``outputs/eval/vpu_03S/metrics/test_kmeans.ngen.ngen_simulation.metrics.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "KGE", "NSE", "CORR", "NNSE", "lead_group", "primary_location_id"
   "nan", "-3.80213291706771", "nan", "0.1723504122179575", "0", "usgs-251253080320100"
   "nan", "-3.8475265855849052", "nan", "0.17101247602108574", "0", "usgs-251341080291200"
   "nan", "-15.882174429973855", "nan", "0.055921610870980756", "0", "usgs-251355080312800"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - KGE
     - Kling-Gupta Efficiency (KGE) metric.
     - float64

   * - NSE
     - Nash-Sutcliffe Efficiency (NSE) metric.
     - float64

   * - CORR
     - Correlation coefficient between observed and simulated values.
     - float32

   * - NNSE
     - Normalized Nash-Sutcliffe Efficiency (NNSE) metric.
     - float64

   * - lead_group
     - Lead time group for the metric (e.g., 0-6 hours, 6-12 hours; 0 for simulations).
     - object

   * - primary_location_id
     - Primary location identifier (e.g., USGS gage ID).
     - object



.. _obs_data:

obs_data
--------

Observation data including the observed values for all locations and time steps.

Sample file path: ``outputs/eval/vpu_03S/usgs/2012-10-01_2012-10-03.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "location_id", "reference_time", "value_time", "value", "variable_name", "measurement_unit", "configuration"
   "usgs-02203655", "2012-10-01 00:00:00", "2012-10-01 00:00:00", "0.12034659832715988", "streamflow", "m3/s", "usgs_gage_data"
   "usgs-02203655", "2012-10-01 01:00:00", "2012-10-01 01:00:00", "2.3078229427337646", "streamflow", "m3/s", "usgs_gage_data"
   "usgs-02203655", "2012-10-01 02:00:00", "2012-10-01 02:00:00", "3.5962395668029785", "streamflow", "m3/s", "usgs_gage_data"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - location_id
     - Location identifier for the observed value.
     - object

   * - reference_time
     - Reference time for the observation (same as value_time for observations).
     - datetime64[ns]

   * - value_time
     - Time of the observed value.
     - datetime64[ns]

   * - value
     - Observed value for a specific location and time.
     - float32

   * - variable_name
     - Name of the observed variable (e.g., streamflow).
     - category

   * - measurement_unit
     - Measurement unit of the observed variable (e.g., cubic meters per second).
     - object

   * - configuration
     - Configuration for the observation (e.g., usgs_gage_data).
     - object



.. _pairs:

pairs
-----

Paired data including the simulated and observed values for all locations and time steps.

Sample file path: ``outputs/eval/vpu_03S/joined/test_kmeans.ngen.ngen_simulation.joined.group0.parquet``

**Example rows:**

.. csv-table::
   :header-rows: 1

   "primary_location_id", "primary_value", "secondary_location_id", "secondary_value", "value_time", "configuration", "measurement_unit", "variable_name", "reference_time", "lead_time"
   "usgs-02203655", "4.502378463745117", "ngen-1271697451481705", "5.666410446166992", "2012-10-01 03:00:00", "ngen_simulation", "m3/s", "streamflow", "2012-10-01 03:00:00", "0.0"
   "usgs-02203655", "3.7661404609680176", "ngen-1271697451481705", "6.261104583740234", "2012-10-01 04:00:00", "ngen_simulation", "m3/s", "streamflow", "2012-10-01 04:00:00", "0.0"
   "usgs-02203655", "3.086536169052124", "ngen-1271697451481705", "12.011900901794434", "2012-10-01 05:00:00", "ngen_simulation", "m3/s", "streamflow", "2012-10-01 05:00:00", "0.0"

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
     - Observed value for the primary location.
     - float32

   * - secondary_location_id
     - Secondary location identifier (e.g., NextGen catchment ID).
     - object

   * - secondary_value
     - Simulated value for the secondary location.
     - float32

   * - value_time
     - Time of the paired value.
     - datetime64[us]

   * - configuration
     - Configuration for the paired data (e.g., ngen_simulation, short_range, medium_range_blend).
     - object

   * - measurement_unit
     - Measurement unit of the paired variable (e.g., cubic meters per second).
     - object

   * - variable_name
     - Name of the paired variable (e.g., streamflow).
     - object

   * - reference_time
     - Reference time for the paired value (same as value_time for simulations).
     - datetime64[us]

   * - lead_time
     - Lead time for the paired value (e.g., 0 for simulations).
     - float64



.. toctree::
   :maxdepth: 2