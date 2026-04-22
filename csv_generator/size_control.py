from __future__ import annotations

from dataclasses import dataclass

from .config import (
    COMPASS_COMPACT_COLUMNS,
    COMPASS_KEEP_COLUMNS,
    COMPASS_SHRINK_PRIORITY_COLUMNS,
    DOCUMENT_TARGET_SIZES,
    FULL_COUNTS,
    SIZE_FILLER_TEXT,
    SIZE_GROW_COLUMNS,
    ColumnSpec,
)


UTF8_BOM_SIZE = 3


@dataclass(frozen=True)
class RowSizeProfile:
    """CSV種別ごとの行サイズ調整方針を表す。"""

    grow_columns: tuple[str, ...]
    shrink_columns: tuple[str, ...]
    compact_columns: tuple[str, ...]
    filler_text: str


def row_size_bytes(values: list[str]) -> int:
    """CSV 1行ぶんのUTF-8バイト数を概算する。"""
    return sum(len(value.encode("utf-8")) for value in values) + max(len(values) - 1, 0) + 2


def target_file_size_bytes(output_key: str, row_count: int) -> int:
    """出力件数に応じた目標ファイルサイズを返す。"""
    full_count = FULL_COUNTS[output_key]
    target_bytes = DOCUMENT_TARGET_SIZES[output_key]
    return max(UTF8_BOM_SIZE, round(target_bytes * (row_count / full_count)))


def target_row_size_bytes(columns: list[ColumnSpec], output_key: str, row_count: int) -> int:
    """ヘッダーを差し引いた目標の平均1行バイト数を返す。"""
    headers = [column.header_label for column in columns]
    target_file_size = target_file_size_bytes(output_key, row_count)
    available = max(row_count, target_file_size - UTF8_BOM_SIZE - row_size_bytes(headers))
    return max(1, available // max(row_count, 1))


def build_row_size_profile(columns: list[ColumnSpec], output_key: str, keep_columns: set[str] | None = None) -> RowSizeProfile:
    """列定義からCSV種別ごとのサイズ調整プロファイルを構築する。"""
    keep_columns = set(keep_columns or set())
    compact_columns: tuple[str, ...] = ()
    preferred_shrink_columns: tuple[str, ...] = ()
    if output_key == "compass":
        keep_columns.update(COMPASS_KEEP_COLUMNS)
        compact_columns = COMPASS_COMPACT_COLUMNS
        preferred_shrink_columns = COMPASS_SHRINK_PRIORITY_COLUMNS
    remaining_columns = [column.name for column in columns if column.name not in keep_columns]
    shrink_columns = _ordered_shrink_columns(remaining_columns, preferred_shrink_columns)
    return RowSizeProfile(
        grow_columns=SIZE_GROW_COLUMNS.get(output_key, ()),
        shrink_columns=shrink_columns,
        compact_columns=compact_columns,
        filler_text=SIZE_FILLER_TEXT.get(output_key, "補足情報"),
    )


def _ordered_shrink_columns(columns: list[str], preferred_columns: tuple[str, ...]) -> tuple[str, ...]:
    """優先指定列を先頭にした縮小順を返す。"""
    ordered: list[str] = []
    seen: set[str] = set()
    for name in preferred_columns:
        if name in columns and name not in seen:
            ordered.append(name)
            seen.add(name)
    for name in columns:
        if name not in seen:
            ordered.append(name)
    return tuple(ordered)


class RowSizeAdjuster:
    """行の値を目標バイト数へ近づける調整器。"""

    def __init__(self, columns: list[ColumnSpec], target_bytes: int, profile: RowSizeProfile) -> None:
        self.columns = columns
        self.target_bytes = target_bytes
        self.profile = profile
        self.name_to_index = {column.name: index for index, column in enumerate(columns)}
        self.max_lengths = [column.max_length for column in columns]

    def fit(self, row: list[str]) -> list[str]:
        """行を目標バイト数へ近づくように短文化または補足語で調整する。"""
        current = row_size_bytes(row)
        if current > self.target_bytes:
            current = self._compact(row, current)
        if current > self.target_bytes:
            current = self._shrink(row, current)
        if current < self.target_bytes:
            self._grow(row, current)
        return row

    def _compact(self, row: list[str], current: int) -> int:
        """長文列を短文化して、重要列を残したまま行サイズを下げる。"""
        for name in self.profile.compact_columns:
            if current <= self.target_bytes:
                break
            index = self.name_to_index.get(name)
            if index is None or not row[index]:
                continue
            current = self._compact_column(row, index, current)
        return current

    def _shrink(self, row: list[str], current: int) -> int:
        """優先列を空欄化して行サイズを縮小する。"""
        for name in self.profile.shrink_columns:
            index = self.name_to_index.get(name)
            if index is None or not row[index]:
                continue
            current -= len(row[index].encode("utf-8"))
            row[index] = ""
            if current <= self.target_bytes:
                break
        return current

    def _grow(self, row: list[str], current: int) -> None:
        """優先列へ説明文を加えて行サイズを拡張する。"""
        for name in self.profile.grow_columns:
            index = self.name_to_index.get(name)
            if index is None:
                continue
            max_length = self.max_lengths[index]
            current = self._grow_column(row, index, current, max_length)
            if current >= self.target_bytes:
                break

    def _grow_column(self, row: list[str], index: int, current: int, max_length: int | None) -> int:
        """単一列を伸ばして目標サイズへ寄せる。"""
        value = row[index]
        if max_length is not None and len(value) >= max_length:
            return current
        base = self.profile.filler_text
        while current < self.target_bytes:
            remaining = None if max_length is None else max_length - len(value)
            if remaining is not None and remaining <= 0:
                break
            addition = base if remaining is None else base[:remaining]
            if not addition:
                break
            value += addition
            current += len(addition.encode("utf-8"))
            if current >= self.target_bytes:
                while current > self.target_bytes and value:
                    char = value[-1]
                    value = value[:-1]
                    current -= len(char.encode("utf-8"))
                break
        row[index] = value
        return current

    def _compact_column(self, row: list[str], index: int, current: int) -> int:
        """単一列を読みやすさを保つ最小限まで短文化する。"""
        value = row[index]
        max_length = self.max_lengths[index]
        compact_value = self._truncate_text(value, 48, max_length)
        if compact_value == value:
            return current
        current -= len(value.encode("utf-8"))
        row[index] = compact_value
        current += len(compact_value.encode("utf-8"))
        return current

    def _truncate_text(self, value: str, minimum_length: int, max_length: int | None) -> str:
        """値の先頭情報を残したまま、短い要約長へ切り詰める。"""
        if len(value) <= minimum_length:
            return value
        truncated = value[:minimum_length].rstrip()
        if max_length is not None:
            truncated = truncated[:max_length]
        return truncated
