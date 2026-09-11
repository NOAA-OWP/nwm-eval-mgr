"""Generate documentation for configuration schemas and sample config file used in nwm-eval-mgr.

This script generates markdown documentation for the configuration schemas used in the NWM Evaluation Manager
    (nwm-eval-mgr) tool. It creates example YAML configuration files and detailed markdown tables describing each
    field in the configuration schemas, including their types, descriptions, default values, and examples.

The generated markdown file is saved to `docs/source/config.md`.
"""

import inspect
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

import nwm_eval.configuration as configuration
from nwm_eval.configuration import Config

INDENT_LEVEL = 2
YAML_COMMENT_BUFFER = 5
NO_DESCRIPTION_STR = "No description provided"


def get_all_schema_models(module):
    """Retrieve all Pydantic schema models from a module."""
    schemas = {}

    for name, obj in inspect.getmembers(module):
        # keep only classes
        if not inspect.isclass(obj):
            continue

        # keep only BaseModel subclasses
        if not issubclass(obj, BaseModel):
            continue

        # skip BaseModel itself
        if obj is BaseModel:
            continue

        # optional: skip top-level Config model
        if obj is Config:
            continue

        schemas[name] = obj

    return schemas


DOCS_TO_CREATE = {
    "config.yaml": {
        "example_file_class": (Config,),
        "schemas": get_all_schema_models(configuration),
        "sample_files": [
            "configs/config_template.yaml",
            "configs/config_ngencerf.yaml",
            "configs/config_hindcast.yaml",
            "configs/config_nwm.yaml",
            "configs/config_ngensim.yaml",
        ],
        "sample_file_desc": {
            "configs/config_template.yaml": "Config template generated from the pydantic model, with default or example values defined for each field. This can be used as a starting point for creating your own configuration files.",
            "configs/config_ngencerf.yaml": "Sample config for verifying a single ngenCERF forecast at one location.",
            "configs/config_hindcast.yaml": "Sample config for verifying multiple ngenCERF hindcasts at one location.",
            "configs/config_nwm.yaml": "Sample config for verifying operational NWM v3 forecasts across multiple locations and domains using data retrieved from Google Cloud Storage (GCS).",
            "configs/config_ngensim.yaml": "Sample config for evaluating large-scale NGEN simulations (e.g., from regionalization) across multiple locations, VPUs, or NWM domains.",
        },
        "sample_file_anchor": {
            "configs/config_template.yaml": "config-template-yaml",
            "configs/config_ngencerf.yaml": "config-ngencerf-yaml",
            "configs/config_hindcast.yaml": "config-hindcast-yaml",
            "configs/config_nwm.yaml": "config-nwm-yaml",
            "configs/config_ngensim.yaml": "config-ngensim-yaml",
        },
    }
}


def type_to_str(tp):
    """Convert a type hint to a readable string for markdown."""
    origin = get_origin(tp)
    args = get_args(tp)

    if origin is None:  # Simple case e.g., str
        return getattr(tp, "__name__", str(tp))
    elif origin in (list, List):
        return f"List[{type_to_str(args[0])}]" if args else "List"
    elif origin in (dict, Dict):
        return (
            f"Dict[{type_to_str(args[0])}, {type_to_str(args[1])}]" if args else "Dict"
        )
    elif origin is Literal:
        return "str = " + " \\| ".join(map(str, args))
    elif len(args) > 1:
        return " \\| ".join(type_to_str(a) for a in args)
    else:  # Catch others
        return str(tp)


def field_to_dict(
    field: FieldInfo, value: Any = None, include_inherited_fields: bool = True
) -> dict:
    """Convert a Pydantic field to a dict for YAML/schema generation."""
    type_ = getattr(field, "annotation", Any)
    description = (
        getattr(field, "description", None)
        or getattr(field, "description_short", None)
        or NO_DESCRIPTION_STR
    )

    # Handle default or default_factory
    if value is not None:
        default_value = value
    elif getattr(field, "default_factory", None) is not None:
        try:
            default_value = field.default_factory()
        except Exception:
            default_value = "<factory>"
    elif field.default is not PydanticUndefined:
        default_value = field.default
    else:
        default_value = None

    # Prefer explicit field examples if present
    example = getattr(field, "examples", None)
    if isinstance(example, list):
        example = example[0] if example else None
    if example is None:
        example = default_value if default_value is not None else ""

    sub_dict = None

    # Handle nested BaseModel
    if isinstance(default_value, BaseModel):
        sub_dict = pydantic_to_dict(
            type(default_value),
            instance=default_value,
            outer_examples=example,
            include_inherited_fields=include_inherited_fields,
        )
    elif isinstance(type_, type) and issubclass(type_, BaseModel):
        sub_dict = pydantic_to_dict(
            type_,
            outer_examples=example,
            include_inherited_fields=include_inherited_fields,
        )
    else:
        # Dict[str, BaseModel]
        origin = get_origin(type_)
        args = get_args(type_)
        if (
            origin in (dict, Dict)
            and len(args) == 2
            and isinstance(args[1], type)
            and issubclass(args[1], BaseModel)
        ):
            value_type = args[1]
            if isinstance(default_value, dict):
                # Map examples if provided
                if isinstance(example, dict):
                    sub_dict = {
                        k: pydantic_to_dict(
                            value_type,
                            outer_examples=example.get(k),
                            include_inherited_fields=include_inherited_fields,
                        )
                        for k in default_value.keys()
                    }
                else:
                    sub_dict = {
                        k: pydantic_to_dict(
                            value_type,
                            include_inherited_fields=include_inherited_fields,
                        )
                        for k in default_value.keys()
                    }
            else:
                sub_dict = pydantic_to_dict(
                    value_type, include_inherited_fields=include_inherited_fields
                )

    json_schema_extra = getattr(field, "json_schema_extra", None)
    return {
        "type": type_,
        "description": description,
        "default": default_value,
        "example": example,
        "sub_dict": sub_dict,
        "json_schema_extra": json_schema_extra,
    }


def pydantic_to_dict(
    model_cls: type[BaseModel],
    instance: BaseModel | None = None,
    outer_examples: Any = None,
    start_fields: list[str] = ["general"],
    end_fields: list[str] = ["metrics", "plots"],
    include_inherited_fields: bool = False,
) -> dict[str, dict]:
    """Convert a Pydantic model to dict, optionally using an instance.

    Only child-only fields are included in the 'general' section.
    Always starts with start_fields and ends with end_fields.

    """
    dict_rep = {}

    # Collect inherited fields from ALL parent BaseModels
    inherited_fields = set()
    for parent in model_cls.__mro__[1:]:
        if issubclass(parent, BaseModel) and parent is not BaseModel:
            inherited_fields.update(parent.model_fields.keys())

    # Ordered field names
    all_fields = list(model_cls.model_fields.keys())

    # optionally remove inherited fields
    if not include_inherited_fields:
        all_fields = [f for f in all_fields if f not in inherited_fields]

    # preserve ordering
    middle_fields = [f for f in all_fields if f not in start_fields + end_fields]

    ordered_fields = (
        [f for f in start_fields if f in all_fields]
        + middle_fields
        + [f for f in end_fields if f in all_fields]
    )

    for name in ordered_fields:
        if name not in model_cls.model_fields:
            continue
        field = model_cls.model_fields[name]

        # Other sections: all fields
        value = getattr(instance, name, None) if instance else None
        dict_rep[name] = field_to_dict(
            field, value=value, include_inherited_fields=include_inherited_fields
        )

        # Override example with outer_examples if provided
        if isinstance(outer_examples, dict) and name in outer_examples:
            dict_rep[name]["example"] = outer_examples[name]

    return dict_rep


def dict_to_yaml(dict_rep: dict, indent: int = 0) -> list[str]:
    """Convert a python dictionary to YAML with added indent customization."""
    lines = []
    tmp_ind = " " * indent
    for i in dict_rep:
        if isinstance(dict_rep[i], dict):
            lines.append(f"{tmp_ind}{i}:")
            lines.extend(dict_to_yaml(dict_rep[i], indent + INDENT_LEVEL))
        else:
            lines.append(f"{tmp_ind}{i}: {str(dict_rep[i])}")
    return lines


def is_dict_of_basemodel(field_dict: dict) -> bool:
    """Check if a field dict represents a Dict[str, BaseModel]-like field."""
    type_ = field_dict.get("type")
    if type_ is None:
        return False
    origin = get_origin(type_)
    args = get_args(type_)
    return (
        origin in (dict, Dict)
        and len(args) == 2
        and isinstance(args[1], type)
        and issubclass(args[1], BaseModel)
    )


def pydantic_dict_to_lines(dict_rep: dict, indent: int = 0) -> list[str]:
    """Convert a pydantic model to lines in the YAML format."""
    lines = []
    tmp_ind = " " * indent
    com_buffer = " " * YAML_COMMENT_BUFFER

    for k, v in dict_rep.items():
        description = (v.get("json_schema_extra") or {}).get(
            "description_short"
        ) or v.get("description")

        comment = (
            f"{com_buffer}# {description}"
            if description and description != NO_DESCRIPTION_STR
            else ""
        )

        # If sub_dict exists, recurse except for fields of type dict{str, BaseModel}, so that examples defined in
        # format of dict{str: BaseModel} are preserved.
        if v.get("sub_dict") is not None and not is_dict_of_basemodel(v):
            lines.append(f"{tmp_ind}{k}:{comment}")
            lines.extend(pydantic_dict_to_lines(v["sub_dict"], indent + INDENT_LEVEL))
            continue

        # Skip fields without examples
        if v.get("example") is None and v.get("default") is None:
            continue

        # Convert value to string; if more than one example is provided, use the first one
        # val = v["example"] if v.get("example") is not None else v["default"]
        val = v.get("default") if v.get("default") is not None else v.get("example")
        if isinstance(val, str):
            val = f"'{val}'"
        elif isinstance(val, dict):
            lines.append(f"{tmp_ind}{k}:{comment}")
            lines.extend(dict_to_yaml(val, indent + INDENT_LEVEL))
            continue

        lines.append(f"{tmp_ind}{k}: {val}{comment}")

    return lines


def justify_yaml_comments(lines: list[str]):
    """Update a YAML file so that comments all start at same column."""
    max_len = 0
    for i in lines:
        cur_len = len(i.split(" #")[0])
        max_len = max([cur_len, max_len])
    for ind, i in enumerate(lines):
        cur_len = len(i.split(" #")[0])
        lines[ind] = i.replace(
            " #", " #" + ("-" * ((max_len + YAML_COMMENT_BUFFER) - cur_len))
        )

    return lines


def generate_yaml_template(model_cls: type[BaseModel], top_key: str = None) -> str:
    """Generate YAML file using examples and descriptions."""
    # Convert BaseModel to dict for easier manipulation
    dict_rep = pydantic_to_dict(model_cls, include_inherited_fields=True)

    # Build initial yaml lines
    if top_key is not None:
        lines = [f"{top_key}:"]
        indent = INDENT_LEVEL
    else:
        lines = []
        indent = 0
    lines.extend(pydantic_dict_to_lines(dict_rep, indent))

    # comment out comments justification for now, as it can create very long lines and
    # hence make comments in the sample yaml files not readily viewable
    # lines = justify_yaml_comments(lines)
    return "\n".join(lines)


def generate_markdown_table(
    model_cls: type[BaseModel],
    include_inherited_fields: bool = False,
) -> str:
    """Convert a Pydantic model to markdown table."""
    dict_rep = pydantic_to_dict(
        model_cls,
        include_inherited_fields=include_inherited_fields,
    )

    headers = [
        "Field",
        "Type(s)",
        "Description",
        "Default",
        "Example(s)",
    ]

    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for name, field_dict in dict_rep.items():
        table.append(
            f"| {name} | "
            f"{type_to_str(field_dict['type'])} | "
            f"{field_dict['description']} | "
            f"{field_dict['default']} | "
            f"{field_dict['example']} |"
        )

    return "\n".join(table)


def myst_anchor(title: str) -> str:
    """Convert a heading to MyST-style anchor ID."""
    title = title.strip().lower()

    # Replace any character that is NOT a-z, 0-9 with dash
    title = re.sub(r"[^a-z0-9]+", "-", title)

    # Collapse multiple consecutive dashes
    title = re.sub(r"-+", "-", title)

    # Strip leading/trailing dashes
    title = title.strip("-")

    return title


def generate_toc_from_markdown(md_text: str) -> str:
    """Scan generated markdown, find headings, and return a TOC block (markdown)."""
    toc_lines = ["### Table of Contents", ""]

    for line in md_text.splitlines():
        m = re.match(r"^(#{2,6})\s+(.*)", line)
        if not m:
            continue

        level = len(m.group(1))
        title = m.group(2).strip()

        # Generate MyST-compatible anchor
        anchor = myst_anchor(title)

        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")

    return "\n".join(toc_lines) + "\n\n"


def main(docs_to_create: dict) -> None:
    """Create markdown file documentation for the specified pydantic models."""
    # Static intro paragraph
    intro_block = ["# Configuration for Evaluation/Verification\n"]

    # Introduction text for the config documentation page
    intro_block.append("### Introduction\n")
    intro_block.append(
        "This page provides detailed documentation for configuring the NWM Evaluation Manager (nwm-eval-mgr) tool for "
        "a variety of simulation evaluation or forecast verification applications.\n"
    )
    intro_block.append(
        "Template files, sample configuration files, and schemas for all configuration fields and subfields are included below. "
        "You can navigate to individual configuration files or schema sections using the tabs on the right or the Table of Contents below.\n"
    )

    for i in docs_to_create:
        sample_files = docs_to_create[i].get("sample_files", [])
        for sample_file in sample_files:
            sample_path = Path(sample_file)
            intro_block.append(
                "- `"
                + sample_path.name
                + "`: "
                + docs_to_create[i]["sample_file_desc"].get(sample_file, "")
            )
    intro_block.append("\n")
    intro_block = "\n".join(intro_block)

    # Generate sections for each config file
    lines = []
    for i in docs_to_create:
        lines.append("### Sample Files\n")

        # Insert sample config files for different use cases
        sample_files = docs_to_create[i].get("sample_files", [])

        for sample_file in sample_files:
            sample_path = Path(sample_file)

            lines.append("")
            # add MyST anchor for the sample file, so that it can be linked to from other pages
            lines.append(
                f"({docs_to_create[i]['sample_file_anchor'].get(sample_file, '')})="
            )
            lines.append(f"#### `{sample_path.name}`\n")
            lines.append(docs_to_create[i]["sample_file_desc"].get(sample_file, ""))
            lines.append("")

            lines.append("```yaml")

            if sample_path.name == "config_template.yaml":
                yaml = generate_yaml_template(*docs_to_create[i]["example_file_class"])
                lines.append(yaml)

                # save the generated template to the sample file path
                sample_path.write_text(yaml, encoding="utf-8")
            else:
                if sample_path.exists():
                    yaml_text = sample_path.read_text(encoding="utf-8")
                    lines.append(yaml_text.rstrip())
                else:
                    lines.append(f"> Warning: sample file not found: {sample_file}")

            lines.append("```")

        lines.append("### Schemas\n")
        for j, model_cls in docs_to_create[i]["schemas"].items():
            # Get direct parent class(es) dynamically
            parent_cls = [
                c
                for c in model_cls.__bases__
                if issubclass(c, BaseModel) and c not in (BaseModel, object)
            ]

            lines.append("")  # blank line before heading

            if parent_cls:
                lines.append(
                    f"#### `{j}` (inherits from `{', '.join(c.__name__ for c in parent_cls)}`)"
                )  # heading with inheritance info
            else:
                lines.append(f"#### `{j}`")

            lines.append("")  # blank line before heading

            lines.append(
                generate_markdown_table(
                    model_cls,
                    include_inherited_fields=False,
                )
            )

    # Convert to final markdown text
    md_text = "\n".join(lines)

    # Generate TOC
    toc_block = generate_toc_from_markdown(md_text)

    # Prepend intro and TOC
    md_text = intro_block + toc_block + md_text

    Path("docs/source/config.md").write_text(md_text, encoding="utf-8")


if __name__ == "__main__":
    main(DOCS_TO_CREATE)
