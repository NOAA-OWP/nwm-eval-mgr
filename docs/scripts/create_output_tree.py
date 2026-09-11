"""Create text files representing the directory tree structure.

This supports the output data for different datasets (e.g., ngenCERF, hindcast, ngensim, gcs).
These text files are used in the documentation to provide an overview of the output data structure for each dataset.
"""

from pathlib import Path

MAX_FILES = 5


def write_tree(path: Path, out_file, prefix=""):
    """Recursively write the directory tree structure of 'path' to 'out_file' with a given 'prefix'."""
    items = sorted(path.iterdir())

    dirs = [p for p in items if p.is_dir()]
    files = [p for p in items if p.is_file()]

    for d in dirs:
        out_file.write(f"{prefix}├── {d.name}/\n")
        write_tree(d, out_file, prefix + "│   ")

    for f in files[:MAX_FILES]:
        out_file.write(f"{prefix}├── {f.name}\n")

    if len(files) > MAX_FILES:
        out_file.write(f"{prefix}└── ... ({len(files) - MAX_FILES} more files)\n")


dir_output = Path("data/outputs")
dir_tree = Path("docs/source/tech_reference")

output_tree_map = {
    "ngencerf": "usgs_01123000",
    "hindcast": "usgs_01123000_hindcast",
    "ngensim": "vpu_03S",
    "gcs": "calib_basin_group1",
}

for data_source, subdir in output_tree_map.items():
    dir_to_write = dir_output / subdir
    output_tree_file = dir_tree / f"{data_source}_output_tree.txt"
    with open(output_tree_file, "w") as f:
        f.write(f"{subdir}/\n")
        write_tree(dir_to_write, f)
