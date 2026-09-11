Frequently Asked Questions
--------------------------

.. dropdown:: What is nwm-eval-mgr?

    nwm-eval-mgr is a repository of tools for conducting evaluation and verification of NWM/NextGen
    simulations, forecasts, and hindcasts. It includes two main Python packages: nwm_eval for orchestrating data 
    processing and evaluation workflows, and nwm_metrics for computing performance metrics.

.. dropdown:: How do I start using this tool?

    Check out the `User Guide <user_guide.html>`_ to get started.

.. dropdown:: Which variables can be evaluated with nwm-eval-mgr?

    Currently nwm-eval-mgr only supports evaluation of streamflow at gage locations. Evaluation of other variables 
    (e.g., soil moisture, snow water equivalent) and gridded evaluation will be added in the future.

.. dropdown:: How to use nwm-eval-mgr for conus-wide evaluation/verification?

    There are two approaches for conducting CONUS-wide evaluation or verification with nwm-eval-mgr:

    1) Single-run approach: run nwm-eval-mgr once using a configuration file that includes all gage locations across 
    the CONUS and forecast data covering the entire CONUS domain (e.g., operational NWM v3 forecasts). This approach 
    can be memory intensive and may require a high-performance computing environment, particularly for large-scale 
    or multi-year hindcast verification.

    2) Regional approach (recommended for large analyses): run nwm-eval-mgr separately for individual regions 
    (e.g., by Virtual Processing Unit (VPU)) across the CONUS. After all regional evaluations are complete, perform a 
    final run with `general.assemble_domain` set to `True` to aggregate the results into a single CONUS-wide evaluation. 
    This approach is generally more computationally efficient and scalable.

.. dropdown:: Can nwm-eval-mgr be used for comparative analyses?

    Yes, nwm-eval-mgr can be used for comparative analyses specifying multiple datasets in the configuration file. 
    For example, you can compare different versions of NWM forecasts (e.g., v3 vs v2) or compare ngen simulations using 
    different formulations or different regionalization algorithms.

    Example configuration to run simulations using two different regionalization algorithms (e.g., Gower vs KMeans):

    .. code-block:: yaml

        general:
        
            dataset_name: [gower, kmeans] 
            nwm_version: [ngen, ngen] 
            forecast_start_date: ['2012-10-01 00:00:00', '2012-10-01 00:00:00'] 
            forecast_end_date: ['2015-10-01 00:00:00', '2015-10-01 00:00:00'] 
            eval_start_date: ['2013-10-01 00:00:00', '2013-10-01 00:00:00']
            eval_end_date: ['2015-10-01 00:00:00', '2015-10-01 00:00:00'] 
