# SPDX-License-Identifier: MIT
"""Shared helpers for the M4Plus-Linux tools: YAML loading, a small JSON Schema checker,
result front matter, heading anchors, and the repository model. Standard library + PyYAML."""

from __future__ import annotations

import datetime as _dt
import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

STATES = ["works-daily", "works-test", "attended", "prepared", "blocked", "not-realistic", "untested", "reported"]
WORKS = ("works-daily", "works-test")
STALE_DAYS = 30


# ---------------------------------------------------------------- YAML

class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps dates as strings, so the schema sees what the file says."""


_Loader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path_or_text):
    if isinstance(path_or_text, pathlib.Path):
        path_or_text = path_or_text.read_text(encoding="utf-8")
    return yaml.load(path_or_text, Loader=_Loader)


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- JSON Schema (subset)

_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
}


def _is_type(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def _resolve(root, ref):
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def schema_errors(value, schema, root=None, path="$"):
    """Validate value against the subset of JSON Schema used in schema/*.json.
    Returns a list of 'path: message' strings (empty when valid)."""
    root = schema if root is None else root
    errs = []
    if "$ref" in schema:
        return schema_errors(value, _resolve(root, schema["$ref"]), root, path)
    if "anyOf" in schema:
        branches = [schema_errors(value, s, root, path) for s in schema["anyOf"]]
        if all(branches):
            best = min(branches, key=len)
            errs.append(f"{path}: matches none of the allowed forms ({best[0]})")
        return errs
    t = schema.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_is_type(value, x) for x in ts):
            return [f"{path}: expected {'/'.join(ts)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: below {schema['minimum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems"):
            seen = [json.dumps(v, sort_keys=True) for v in value]
            if len(seen) != len(set(seen)):
                errs.append(f"{path}: items must be unique")
        if "items" in schema:
            for i, v in enumerate(value):
                errs += schema_errors(v, schema["items"], root, f"{path}[{i}]")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required key '{k}'")
        props = schema.get("properties", {})
        pprops = schema.get("patternProperties", {})
        addl = schema.get("additionalProperties", True)
        for k, v in value.items():
            sub = f"{path}.{k}"
            matched = False
            if k in props:
                errs += schema_errors(v, props[k], root, sub)
                matched = True
            for rx, s in pprops.items():
                if re.search(rx, str(k)):
                    errs += schema_errors(v, s, root, sub)
                    matched = True
            if not matched:
                if addl is False:
                    errs.append(f"{path}: unknown key '{k}'")
                elif isinstance(addl, dict):
                    errs += schema_errors(v, addl, root, sub)
    return errs


def load_schema(name):
    return load_json(ROOT / "schema" / name)


# ---------------------------------------------------------------- Markdown helpers

FRONT_RX = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def front_matter(text):
    """-> (dict or None, body). None when the file has no front matter."""
    m = FRONT_RX.match(text)
    if not m:
        return None, text
    return load_yaml(m.group(1)) or {}, text[m.end():]


def _plain(heading):
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)   # links -> text
    h = re.sub(r"<[^>]+>", "", h)                           # inline html
    return h.replace("`", "").replace("*", "").replace("~", "")


def slugify(heading):
    """GitHub's heading anchor: lower case, punctuation dropped, spaces to hyphens."""
    t = _plain(heading).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def anchors(markdown_text):
    """All heading anchors of a Markdown document, GitHub style (duplicates get -1, -2 ...)."""
    seen, out = {}, set()
    in_fence = False
    for line in markdown_text.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        s = slugify(m.group(2))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


# ---------------------------------------------------------------- dates

def parse_date(s):
    """'2026-11-07' or '2026-11-07T23:16Z' -> datetime.date (None if unparsable)."""
    if not isinstance(s, str):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    try:
        return _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def today():
    return _dt.datetime.now(_dt.timezone.utc).date()


# ---------------------------------------------------------------- repository model

def features():
    return load_yaml(ROOT / "schema" / "features.yaml")


def machine_files(root=ROOT):
    return sorted((root / "machines").glob("*/machine.yaml"))


def load_machines(root=ROOT):
    out = []
    for f in machine_files(root):
        out.append((f, load_yaml(f)))
    return out


def load_prs(root=ROOT):
    p = root / "upstream" / "prs.yaml"
    return load_yaml(p) if p.exists() else {"prs": []}


def load_status(root=ROOT):
    p = root / "upstream" / "status.json"
    return load_json(p) if p.exists() else {"prs": {}}


def pr_key(repo, number):
    return f"{repo}#{number}"


def owners_of(machine):
    o = machine.get("owner", [])
    return [o] if isinstance(o, str) else list(o)


def newest_cell(cells):
    """The cell that represents a feature in the matrix: the best state among the setups."""
    order = {s: i for i, s in enumerate(STATES)}
    return sorted(cells, key=lambda c: order.get(c.get("state"), 99))[0]


def reproduced(cells):
    """True when two setups have native evidence for a works-* state (computed, never written)."""
    setups = {c.get("setup") for c in cells if c.get("kind") == "native" and c.get("state") in WORKS}
    return len(setups) >= 2


def is_stale(cell, on=None, days=STALE_DAYS):
    if cell.get("state") not in WORKS:
        return False
    d = parse_date(cell.get("verified"))
    if d is None:
        return True
    return ((on or today()) - d).days > days
