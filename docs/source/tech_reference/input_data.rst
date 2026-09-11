Schemas
=======

.. _gage_crosswalk:

gage_crosswalk
--------------

Crosswalk between USGS gages and NextGen catchments for the CONUS domain.

Sample file path: ``nhf/usgs_ngen_crosswalk_conus.parquet``

.. note:: Geometry column omitted from preview table for brevity.

**Example rows:**

.. csv-table::
   :header-rows: 1

   "domain", "vpu_id", "primary_location_id", "secondary_location_id", "basin_area_km2", "status"
   "CONUS", "01", "usgs-01118300", "ngen-3308860", "13.74", "USGS-active"
   "CONUS", "01", "usgs-01118400", "ngen-3308834", "43.77", "USGS-discontinued"
   "CONUS", "01", "usgs-01118668", "ngen-3309403", "36.65", "USGS-discontinued"

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
     - Gage ID.
     - object

   * - secondary_location_id
     - Catchment ID.
     - object

   * - basin_area_km2
     - Basin area in square kilometers.
     - float64

   * - status
     - Status of the gage (e.g., "active" or "inactive").
     - object

   * - geometry
     - Geometry of the gage location.
     - object




.. toctree::
   :maxdepth: 2