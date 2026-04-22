from __future__ import annotations

import re
from pathlib import Path

from .config import ColumnSpec, SECTION_KEYS


def load_specs(path: Path) -> dict[str, list[ColumnSpec]]:
    """`docs/format.md` または `docs/format/` を読み込み、CSVごとの列定義へ変換する。"""
    if path.is_dir():
        return _load_specs_from_directory(path)

    text = path.read_text(encoding="utf-8")
    specs: dict[str, list[ColumnSpec]] = {}
    for section in re.split(r"^# ", text, flags=re.MULTILINE):
        if not section.strip():
            continue
        lines = section.splitlines()
        title = lines[0].strip()
        key = SECTION_KEYS.get(title)
        if key is None:
            continue
        specs[key] = parse_section_columns(lines)
    return specs


def _load_specs_from_directory(path: Path) -> dict[str, list[ColumnSpec]]:
    """Markdown ディレクトリ内の全仕様を読み込む。"""
    specs: dict[str, list[ColumnSpec]] = {}
    for markdown_path in sorted(path.glob("*.md")):
        specs.update(load_specs(markdown_path))
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
    column_name_index = _find_column_name_index(parts)
    if column_name_index is None or column_name_index == 0 or column_name_index + 2 >= len(parts):
        return None
    return (
        parts[column_name_index - 1],
        parts[column_name_index].strip("`"),
        parts[column_name_index + 1],
        parts[column_name_index + 2],
    )


def _find_column_name_index(parts: list[str]) -> int | None:
    """backtick 付きのカラム名セル位置を返す。"""
    for index, part in enumerate(parts):
        if part.startswith("`") and part.endswith("`"):
            return index
    return None


def parse_max_length(length_text: str) -> int | None:
    """桁数定義の先頭数値を取り出し、最大長として返す。"""
    match = re.match(r"(\d+)", length_text)
    return int(match.group(1)) if match else None
