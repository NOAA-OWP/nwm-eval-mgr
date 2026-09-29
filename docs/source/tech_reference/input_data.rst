Schemas
=======

.. _gage_crosswalk:

gage_crosswalk
--------------

Crosswalk between USGS gages and NextGen catchments for a given domain (e.g., conus).

Sample file path: ``inputs/eval/usgs_ngen_crosswalk_conus.parquet``

.. note:: Geometry column omitted from preview table for brevity.

**Example rows:**

.. csv-table::
   :header-rows: 1

   "domain", "vpu_id", "primary_location_id", "secondary_location_id", "basin_area_km2", "status"
   "CONUS", "01", "usgs-01118300", "ngen-1285848541835259", "13.74", "USGS-active"
   "CONUS", "01", "usgs-01118400", "ngen-1285847199882424", "43.77", "USGS-discontinued"
   "CONUS", "01", "usgs-01118668", "ngen-1285847048692311", "36.65", "USGS-discontinued"

**Schema:**

.. list-table::
   :header-rows: 1

   * - Column
     - Description
     - Type
   * - domain
     - NWM domain (e.g., CONUS).
     - object

   * - vpu_id
     - Unique identifier for Virtual Processing Unit (VPU).
     - object

   * - primary_location_id
     - Primary location identifier (e.g., USGS gage ID).
     - object

   * - secondary_location_id
     - Secondary location identifier (e.g., NextGen catchment ID).
     - object

   * - basin_area_km2
     - Basin area in square kilometers.
     - float64

   * - status
     - Status of the gage (e.g., "USGS-active" or "USGS-discontinued").
     - object

   * - geometry
     - Geometry of the catchment.
     - object



.. _troute_output:

troute_output
-------------

Troute output for the given configuration.

Sample file path: ``outputs/ngen/regionalization/test_kmeans/vpu_03S/Output/troute_output_201210010000.nc``

**Schema:**

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Type
     - Dimensions
     - Example values
   * - type
     - Type
     - <U2
     - feature_id
     - wb, wb, wb

   * - flow
     - Flow (m3 s-1)
     - float32
     - feature_id, time
     - 0.0, 0.0, 0.0

   * - velocity
     - Velocity (m/s)
     - float32
     - feature_id, time
     - 0.0, 0.0, 0.0

   * - depth
     - Depth (m)
     - float32
     - feature_id, time
     - 0.0, 0.0, 0.0

   * - nudge
     - Streamflow Nudge Value (m3 s-1)
     - float32
     - feature_id, time
     - nan, nan, nan

   * - time
     - valid output time (seconds since 2012-10-01)
     - float64
     - time
     - 1349053200000000000, 1349056800000000000, 1349060400000000000

   * - feature_id
     - Segment ID
     - int64
     - feature_id
     - 1072639236903480, 1072639243699931, 1072639267016356



.. toctree::
   :maxdepth: 2