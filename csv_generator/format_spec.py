from __future__ import annotations

import re
from pathlib import Path

from .config import ColumnSpec, SECTION_KEYS


def load_specs(path: Path) -> dict[str, list[ColumnSpec]]:
    """`docs/format.md` を読み込み、CSVごとの列定義へ変換する。"""
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^# ", text, flags=re.MULTILINE)
    specs: dict[str, list[ColumnSpec]] = {}
    for section in sections:
        if not section.strip():
            continue
        lines = section.splitlines()
        title = lines[0].strip()
        key = SECTION_KEYS.get(title)
        if key is None:
            continue
        specs[key] = parse_section_columns(lines)
    return specs


def parse_section_columns(lines: list[str]) -> list[ColumnSpec]:
    """Markdownの1セクションから、`id` を除いた列定義だけを抽出する。"""
    columns: list[ColumnSpec] = []
    for line in lines:
        if not line.startswith("|") or "`" not in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 8 or not parts[3].startswith("`"):
            continue
        name = parts[3].strip("`")
        if name == "id":
            continue
        columns.append(
            ColumnSpec(
                name=name,
                data_type=parts[4],
                max_length=parse_max_length(parts[5]),
            )
        )
    return columns


def parse_max_length(length_text: str) -> int | None:
    """桁数定義の先頭数値を取り出し、最大長として返す。"""
    match = re.match(r"(\d+)", length_text)
    return int(match.group(1)) if match else None
