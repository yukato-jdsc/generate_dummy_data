from __future__ import annotations

import re
from pathlib import Path

from .config import SECTION_KEYS, ColumnSpec


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
    header_parts: list[str] = []
    for line in lines:
        if _is_table_header(line):
            header_parts = _split_markdown_row(line)
            continue
        parsed = _parse_column_row(line, header_parts)
        if parsed is None:
            continue
        item_label, name, data_type, max_length_text, primary_key_text, required_text = parsed
        columns.append(
            ColumnSpec(
                name=name,
                header_label=item_label,
                data_type=data_type,
                max_length=parse_max_length(max_length_text),
                primary_key=is_marker_text(primary_key_text),
                required=is_marker_text(required_text),
            )
        )
    return columns


def _parse_column_row(
    line: str,
    header_parts: list[str] | None = None,
) -> tuple[str, str, str, str, str, str] | None:
    """列定義のMarkdown行を、表示名・列名・型・桁に分解する。"""
    if not line.startswith("|") or "`" not in line:
        return None
    parts = _split_markdown_row(line)
    column_name_index = _find_column_name_index(parts)
    if column_name_index is None or column_name_index == 0 or column_name_index + 2 >= len(parts):
        return None
    primary_key_index = _find_named_index(header_parts or [], "PK")
    required_index = _find_required_index(header_parts or [], column_name_index)
    return (
        parts[column_name_index - 1],
        parts[column_name_index].strip("`"),
        parts[column_name_index + 1],
        parts[column_name_index + 2],
        parts[primary_key_index] if primary_key_index is not None and primary_key_index < len(parts) else "",
        parts[required_index] if required_index is not None and required_index < len(parts) else "",
    )


def _split_markdown_row(line: str) -> list[str]:
    """Markdown表の1行をセルの配列へ変換する。"""
    return [part.strip() for part in line.strip().strip("|").split("|")]


def _is_table_header(line: str) -> bool:
    """列定義テーブルのヘッダー行かどうかを返す。"""
    return line.startswith("|") and "カラム名" in line and "`" not in line


def _find_required_index(header_parts: list[str], column_name_index: int) -> int | None:
    """ヘッダー行から必須セルの位置を特定する。"""
    required_index = _find_named_index(header_parts, "必須")
    if required_index is not None:
        return required_index
    fallback_index = column_name_index + 3
    return fallback_index


def _find_named_index(header_parts: list[str], header_name: str) -> int | None:
    """ヘッダー行から指定名のセル位置を返す。"""
    if header_name in header_parts:
        return header_parts.index(header_name)
    return None


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


def is_marker_text(text: str) -> bool:
    """列定義セルが統一済みの丸印マークを含むかどうかを返す。"""
    return "○" in text
