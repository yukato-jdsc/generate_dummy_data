from __future__ import annotations

import re
from pathlib import Path

from .config import ColumnSpec, SECTION_KEYS


def load_specs(path: Path) -> dict[str, list[ColumnSpec]]:
    """`docs/format.md` または `docs/format/` を読み込み、CSVごとの列定義へ変換する。"""
    if path.is_dir():
        specs: dict[str, list[ColumnSpec]] = {}
        for markdown_path in sorted(path.glob("*.md")):
            specs.update(load_specs(markdown_path))
        return specs

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
    """Markdownの1セクションから、列定義を抽出する。"""
    columns: list[ColumnSpec] = []
    for line in lines:
        parsed = _parse_column_row(line)
        if parsed is None:
            continue
        item_label, name, data_type, max_length_text = parsed
        columns.append(
            ColumnSpec(
                name=name,
                header_label=item_label,
                data_type=data_type,
                max_length=parse_max_length(max_length_text),
            )
        )
    return columns


def _parse_column_row(line: str) -> tuple[str, str, str, str] | None:
    """列定義のMarkdown行を、表示名・列名・型・桁に分解する。"""
    if not line.startswith("|") or "`" not in line:
        return None
    parts = [part.strip() for part in line.strip().strip("|").split("|")]
    if len(parts) < 7:
        return None
    if len(parts) == 7:
        return parts[1], parts[2].strip("`"), parts[3], parts[4]
    return parts[2], parts[3].strip("`"), parts[4], parts[5]


def parse_max_length(length_text: str) -> int | None:
    """桁数定義の先頭数値を取り出し、最大長として返す。"""
    match = re.match(r"(\d+)", length_text)
    return int(match.group(1)) if match else None
