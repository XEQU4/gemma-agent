#!/usr/bin/env python3
"""Static v1 checks and deterministic ZIP packaging; not the official compiler."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: use the project's validation dependency group.")

PROJECT = Path(__file__).resolve().parents[1]
MAX_SIZE = 3_221_225_472
YAML_LIMIT = 50 * 1024 * 1024
EXTENSIONS = {".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}
ROOTS = {"agent.yaml", "agent.yml", "root_agent.yaml", "root_agent.yml"}
MODELS = {f"gemma-4-{n}-it-qat-w4a16-ct" for n in ("31b", "12b", "e4b", "e2b")}
TOOLS = {
    "run_command", "read_file", "edit_file", "write_file", "get_status",
    "submit_patch", "get_code_neighbors", "search_similar_code", "get_code_subgraph",
}
GEN_FIELDS = {
    "temperature", "top_p", "top_k", "max_output_tokens", "presence_penalty",
    "frequency_penalty", "stop_sequences", "response_mime_type", "seed", "thinking_config",
}
FORBIDDEN_GEN = {"tools", "system_instruction", "http_options", "safety_settings", "response_schema"}
TIMESTAMP = (1980, 1, 1, 0, 0, 0)
CHUNK = 1024 * 1024


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def safe_path(value):
    require(isinstance(value, str) and bool(value), "Path must be a nonempty string")
    require("\0" not in value and "\\" not in value and ":" not in value,
            f"Unsafe path: {value!r}")
    require(not PurePosixPath(value).is_absolute() and not PureWindowsPath(value).drive,
            f"Absolute path: {value!r}")
    require(all(part not in ("", ".", "..") for part in value.split("/")),
            f"Traversal or empty path component: {value!r}")
    return value


def is_link(path):
    return path.is_symlink() or path.is_junction()


def digest(stream):
    stream.seek(0)
    h = hashlib.sha256()
    while chunk := stream.read(CHUNK):
        h.update(chunk)
    return h.hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return digest(stream)


@dataclass(frozen=True)
class Include:
    path: str


class ConfigPath(str):
    """Keep the defining YAML location when includes are expanded."""
    def __new__(cls, value, owner):
        obj = super().__new__(cls, value)
        obj.owner = owner
        return obj


class StrictLoader(yaml.SafeLoader):
    # A conservative v1 subset: reject aliases/merge keys instead of expanding bombs.
    def compose_node(self, parent, index):
        require(not self.check_event(yaml.AliasEvent), "YAML aliases are not supported")
        return super().compose_node(parent, index)


def construct_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        require(key_node.tag != "tag:yaml.org,2002:merge", "YAML merge keys are not supported")
        key = loader.construct_object(key_node, deep=deep)
        require(isinstance(key, str), "YAML mapping keys must be strings")
        require(key not in result, f"Duplicate YAML key: {key}")
        value = loader.construct_object(value_node, deep=deep)
        if key == "config_path":
            require(isinstance(value, str), "config_path must be a string")
            value = ConfigPath(value, loader.owner)
        result[key] = value
    return result


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
StrictLoader.add_constructor(
    "!include", lambda loader, node: Include(loader.construct_scalar(node)))


def inventory(source):
    require(source.is_dir() and not is_link(source), "Submission must be a real directory")
    files = {}

    def visit(directory):
        for path in sorted(directory.iterdir()):
            require(not is_link(path), f"Symlink/junction is forbidden: {path}")
            name = safe_path(path.relative_to(source).as_posix())
            if path.is_dir():
                visit(path)
            else:
                require(stat.S_ISREG(path.stat().st_mode), f"Not a regular file: {name}")
                require(path.suffix in EXTENSIONS, f"Unsupported extension: {name}")
                files[name] = path.stat().st_size

    visit(source)
    roots = ROOTS.intersection(files)
    require(len(roots) == 1, f"Expected exactly one root config; found {sorted(roots)}")
    require(roots == {"agent.yaml"}, "This v1 packager requires agent.yaml at the ZIP root")
    require(len(files) <= 10_000, "File count exceeds README limit")
    require(sum(files.values()) < MAX_SIZE, "Unpacked size must be strictly below 3221225472")
    require(sum(name.endswith((".yaml", ".yml")) for name in files) <= 1_000,
            "YAML file count exceeds README limit")
    return dict(sorted(files.items()))


def model_alias(value):
    require(isinstance(value, str), "model must be a string")
    prefix, separator, suffix = value.partition("/")
    return suffix if separator and prefix in {"openai", "google", "hosted_vllm", "custom"} else value


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, f"Invalid {label}: {value!r}")


def generation(config):
    require(isinstance(config, dict), "generate_content_config must be a mapping")
    require(not (set(config) & FORBIDDEN_GEN), "Forbidden generate_content_config field")
    require(set(config) <= GEN_FIELDS, "Unknown generate_content_config field")
    integer(config.get("max_output_tokens", 16384), 1, 32768, "max_output_tokens")
    thinking = config.get("thinking_config", {})
    require(isinstance(thinking, dict), "thinking_config must be a mapping")
    require(set(thinking) <= {"thinking_budget", "thinking_level", "include_thoughts"},
            "Unknown thinking_config field")
    if "thinking_budget" in thinking:
        integer(thinking["thinking_budget"], 0, 32768, "thinking_budget")
    if "thinking_level" in thinking:
        level = thinking["thinking_level"]
        require(isinstance(level, str) and level.upper() in
                {"MINIMAL", "LOW", "MEDIUM", "HIGH", "NONE"}, "Invalid thinking_level")
    if "include_thoughts" in thinking:
        require(type(thinking["include_thoughts"]) is bool, "include_thoughts must be boolean")
    for field in ("temperature", "top_p", "presence_penalty", "frequency_penalty"):
        if field in config:
            value = config[field]
            require(type(value) in (int, float) and math.isfinite(value),
                    f"{field} must be finite numeric")
            if field == "temperature":
                require(value >= 0, "temperature must be >= 0")
            if field == "top_p":
                require(0 <= value <= 1, "top_p must be in [0, 1]")
    if "top_k" in config:
        require(type(config["top_k"]) is int and config["top_k"] >= 1, "Invalid top_k")
    if "seed" in config:
        require(type(config["seed"]) is int, "seed must be an integer")
    if "stop_sequences" in config:
        require(isinstance(config["stop_sequences"], list) and
                all(isinstance(s, str) for s in config["stop_sequences"]), "Invalid stop_sequences")
    if "response_mime_type" in config:
        require(isinstance(config["response_mime_type"], str), "Invalid response_mime_type")


class Validator:
    def __init__(self, source, files):
        self.source, self.files = source, files
        self.raw, self.expanded, self.edges = {}, {}, {}
        self.models, self.agents = set(), set()
        self.expansion_bytes = 0

    def target(self, owner, value):
        safe_path(value)
        name = (PurePosixPath(owner).parent / value).as_posix()
        safe_path(name)
        require(name in self.files, f"Missing reference from {owner}: {value}")
        require((self.source / name).resolve().is_relative_to(self.source.resolve()),
                f"Reference escapes submission: {value}")
        self.edges.setdefault(owner, set()).add(name)
        return name

    def scan_refs(self, node, owner):
        if isinstance(node, Include):
            target = self.target(owner, node.path)
            require(Path(target).suffix in {".md", ".txt", ".yaml", ".yml"},
                    f"Unsupported include type: {target}")
        elif isinstance(node, ConfigPath):
            target = self.target(node.owner, node)
            require(target.endswith((".yaml", ".yml")), "config_path must reference YAML")
        elif isinstance(node, dict):
            for value in node.values():
                self.scan_refs(value, owner)
        elif isinstance(node, list):
            for value in node:
                self.scan_refs(value, owner)

    def acyclic(self):
        active, done = set(), set()

        def visit(name):
            require(name not in active, f"Reference cycle involving {name}")
            if name in done:
                return
            active.add(name)
            for child in self.edges.get(name, ()):
                visit(child)
            active.remove(name)
            done.add(name)

        for name in self.edges:
            visit(name)

    def expand(self, node, owner, depth=0):
        if isinstance(node, Include):
            require(depth < 10, "Include depth exceeds 10")
            name = self.target(owner, node.path)
            self.expansion_bytes += self.files[name]
            require(self.expansion_bytes <= YAML_LIMIT, "Include expansion exceeds 50 MiB")
            if name.endswith((".yaml", ".yml")):
                return self.expand(self.raw[name], name, depth + 1)
            return (self.source / name).read_text(encoding="utf-8")
        if isinstance(node, dict):
            return {k: self.expand(v, owner, depth) for k, v in node.items()}
        if isinstance(node, list):
            return [self.expand(v, owner, depth) for v in node]
        return node

    def agent_reference(self, value):
        require(isinstance(value, dict) and "config_path" in value,
                "This v1 checker requires config_path for nested agent references")
        ref = value["config_path"]
        require(isinstance(ref, ConfigPath), "Invalid agent config_path")
        self.agent(self.expanded[self.target(ref.owner, ref)])

    def agent(self, node):
        require(isinstance(node, dict), "Agent config must be a mapping")
        if id(node) in self.agents:
            return
        self.agents.add(id(node))
        require(len(self.agents) <= 500, "Agent count exceeds 500")
        require(isinstance(node.get("name"), str) and bool(node["name"]), "Agent name is required")
        require(node.get("agent_class", "LlmAgent") == "LlmAgent",
                "This v1 checker supports LlmAgent only; use official compiler for other classes")
        model = model_alias(node.get("model"))
        require(model in MODELS, f"Model is not in the README competition allowlist: {model}")
        self.models.add(model)
        instruction = node.get("instruction", "")
        require(isinstance(instruction, str) and len(instruction) <= 1_000_000,
                "Invalid or oversized instruction")
        generation(node.get("generate_content_config", {}))
        tools = node.get("tools", [])
        require(isinstance(tools, list), "tools must be a list")
        for tool in tools:
            if isinstance(tool, str):
                require(tool in TOOLS, f"Unknown tool: {tool}")
            else:
                require(isinstance(tool, dict) and set(tool) == {"agent_tool"}, "Invalid tool entry")
                spec = tool["agent_tool"]
                require(isinstance(spec, dict), "agent_tool must be a mapping")
                if "skip_summarization" in spec:
                    require(type(spec["skip_summarization"]) is bool, "Invalid skip_summarization")
                self.agent_reference(spec)
        children = node.get("sub_agents", [])
        require(isinstance(children, list), "sub_agents must be a list")
        for child in children:
            self.agent_reference(child)
        # Skills are not used by v1; avoid silently implying official skill validation.
        require(not node.get("skills"), "Skills require official validation; unsupported by v1 checker")
        adapter = node.get("adapter")
        if adapter is not None:
            import re
            require(isinstance(adapter, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", adapter),
                    "Invalid adapter name")
            base = f"adapters/{adapter}/"
            require(base + "adapter_config.json" in self.files and
                    base + "adapter_model.safetensors" in self.files, f"Missing adapter files: {adapter}")
            config = json.loads((self.source / base / "adapter_config.json").read_text(encoding="utf-8"))
            require(isinstance(config, dict) and config.get("peft_type") == "LORA", "Expected LoRA config")
            integer(config.get("r"), 1, 128, "adapter rank")
            require(model_alias(config.get("base_model_name_or_path")) == model,
                    "Declared adapter base model differs from agent model")

    def run(self):
        for name, size in self.files.items():
            if name.endswith((".yaml", ".yml")):
                require(size <= YAML_LIMIT, f"YAML exceeds 50 MiB: {name}")
                loader = StrictLoader((self.source / name).read_text(encoding="utf-8"))
                loader.owner = name
                try:
                    self.raw[name] = loader.get_single_data()
                finally:
                    loader.dispose()
                require(isinstance(self.raw[name], dict), f"Expected YAML mapping: {name}")
                self.scan_refs(self.raw[name], name)
        self.acyclic()
        for name, node in self.raw.items():
            self.expansion_bytes = self.files[name]
            self.expanded[name] = self.expand(node, name)
        self.agent(self.expanded["agent.yaml"])
        # Also inspect standalone agent YAMLs and generation mappings.
        def scan(node):
            if isinstance(node, dict):
                if "model" in node or "agent_class" in node:
                    self.agent(node)
                if "generate_content_config" in node:
                    generation(node["generate_content_config"])
                for value in node.values():
                    scan(value)
            elif isinstance(node, list):
                for value in node:
                    scan(value)
        for node in self.expanded.values():
            scan(node)
        require(len(self.models) == 1, "Submission must declare exactly one unique model")
        analyzer = self.expanded.get("sub_agents/code_analyzer.yaml")
        require(isinstance(analyzer, dict), "v1 analyzer YAML is missing")
        require(self.expanded["agent.yaml"].get("generate_content_config") ==
                analyzer.get("generate_content_config"), "Root/analyzer sampling differs")
        return {
            "yaml_files": len(self.raw), "models": sorted(self.models),
            "references": [{"source": s, "target": t}
                           for s in sorted(self.edges) for t in sorted(self.edges[s])],
        }


def build_archive(stream, source, files):
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for name, size in files.items():
            info = zipfile.ZipInfo(name, date_time=TIMESTAMP)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            info.file_size = size
            with archive.open(info, "w", force_zip64=size >= zipfile.ZIP64_LIMIT) as dest:
                with (source / name).open("rb") as src:
                    shutil.copyfileobj(src, dest, CHUNK)


def verify_archive(stream, source, files, hashes):
    stream.seek(0)
    with zipfile.ZipFile(stream, "r") as archive:
        require(archive.testzip() is None, "ZIP CRC check failed")
        require(archive.namelist() == list(files), "ZIP entry list/order differs from source")
        for info in archive.infolist():
            safe_path(info.filename)
            require(info.date_time == TIMESTAMP and info.file_size == files[info.filename],
                    "ZIP timestamp/size mismatch")
            require(not info.is_dir() and stat.S_ISREG(info.external_attr >> 16),
                    "ZIP entry is not a regular file")
            h = hashlib.sha256()
            with archive.open(info) as packed, (source / info.filename).open("rb") as original:
                while True:
                    chunk = packed.read(CHUNK)
                    require(chunk == original.read(CHUNK), f"ZIP bytes differ: {info.filename}")
                    if not chunk:
                        break
                    h.update(chunk)
            require(h.hexdigest() == hashes[info.filename], "Source changed during build")


def build(source, output):
    source = source.absolute()
    output = output.absolute()
    files = inventory(source)
    require(not output.resolve().is_relative_to(source.resolve()), "Output must be outside submission")
    require(not output.exists() and not output.is_symlink(), "Output exists; choose a new --output")
    checks = Validator(source, files).run()
    hashes = {name: file_hash(source / name) for name in files}
    with tempfile.SpooledTemporaryFile(max_size=8 * CHUNK) as first, \
            tempfile.SpooledTemporaryFile(max_size=8 * CHUNK) as second:
        for stream in (first, second):
            build_archive(stream, source, files)
            verify_archive(stream, source, files, hashes)
        hash1, hash2 = digest(first), digest(second)
        require(hash1 == hash2, "Two builds have different SHA-256")
        require(inventory(source) == files, "Source file inventory changed during build")
        output.parent.mkdir(parents=True, exist_ok=True)
        first.seek(0)
        with output.open("xb") as dest:
            shutil.copyfileobj(first, dest, CHUNK)
    with output.open("rb") as final:
        verify_archive(final, source, files, hashes)
    require(file_hash(output) == hash1, "Written ZIP hash mismatch")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT, capture_output=True, text=True)
    return {
        "validation": "static checks only; not official compilation or runtime validation",
        "source_commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "output": str(output), "zip_bytes": output.stat().st_size,
        "sha256": hash1, "second_build_sha256": hash2,
        "unpacked_bytes": sum(files.values()), "checks": checks,
        "files": [{"path": name, "bytes": size, "sha256": hashes[name]}
                  for name, size in files.items()],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission-dir", type=Path, default=PROJECT / "submission")
    parser.add_argument("--output", type=Path, default=PROJECT / "dist/submission.zip")
    args = parser.parse_args()
    try:
        result = build(args.submission_dir, args.output)
    except (ValidationError, yaml.YAMLError, OSError, ValueError, RecursionError,
            zipfile.BadZipFile) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
