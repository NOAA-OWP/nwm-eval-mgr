"""Generate an RST file documenting metrics supported by nwm-eval-mgr."""

import sys
from pathlib import Path


def generate_metrics_rst() -> None:
    """Generate the supported-metrics table in metrics.rst."""
    # Add the package directory to sys.path when running the script directly
    # from the repository.
    repo_root = Path(__file__).resolve().parents[2]
    package_root = repo_root / "nwm_eval"

    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    from nwm_eval.settings import (
        dict_nwm_eval_metrics,
        dict_teehr_metrics,
    )

    output_file = repo_root / "docs" / "source" / "tech_reference" / "metrics.rst"

    # Combine metrics supported by either running mode.
    metric_names = sorted(
        set(dict_teehr_metrics) | set(dict_nwm_eval_metrics),
        key=str.lower,
    )

    lines = [
        "Supported Metrics",
        "=================",
        "",
        "`nwm-eval-mgr` currently supports metric calculation using either "
        "the `teehr` or `nwm_eval` library. The metrics supported by each "
        "library are listed below.",
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "",
        "   * - Metric Short Name",
        "     - Metric Long Name",
        "     - Supported by TEEHR",
        "     - Supported by ``nwm_eval``",
    ]

    for name in metric_names:
        if name in dict_nwm_eval_metrics:
            long_name = dict_nwm_eval_metrics[name].replace(" ", "_").lower()
        else:
            long_name = dict_teehr_metrics[name].replace(" ", "_").lower()

        teehr_supported = "Yes" if name in dict_teehr_metrics else "No"
        nwm_eval_supported = "Yes" if name in dict_nwm_eval_metrics else "No"

        lines.extend(
            [
                f"   * - {name}",
                f"     - {long_name}",
                f"     - {teehr_supported}",
                f"     - {nwm_eval_supported}",
            ]
        )

    lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")

    print(f"Generated supported metrics documentation: {output_file}")


if __name__ == "__main__":
    generate_metrics_rst()
