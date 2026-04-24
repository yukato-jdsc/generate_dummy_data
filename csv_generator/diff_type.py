from __future__ import annotations

DIFF_TYPE_HEADER = "diff_type"
INITIAL_DIFF_TYPE = "I"
UPDATE_DIFF_TYPE = "U"
DELETE_DIFF_TYPE = "D"
DIFF_TYPE_ORDER = (INITIAL_DIFF_TYPE, UPDATE_DIFF_TYPE, DELETE_DIFF_TYPE)
INCREMENTAL_OUTPUT_KEYS = frozenset(
    {
        "agency_all",
        "agency_diff",
        "compass_all",
        "compass_diff",
        "corp_all_1",
        "corp_all_2",
        "corp_diff",
        "bfs_all",
        "bfs_diff",
        "bfs_device_all",
        "bfs_device_diff",
        "bfs_accessories_all",
        "bfs_accessories_diff",
    }
)
DIFF_OUTPUT_KEYS = frozenset(
    {
        "agency_diff",
        "compass_diff",
        "corp_diff",
        "bfs_diff",
        "bfs_device_diff",
        "bfs_accessories_diff",
    }
)


def output_uses_diff_type(output_key: str) -> bool:
    """指定した出力CSVが `diff_type` 列を持つ対象かどうかを返す。"""
    return output_key in INCREMENTAL_OUTPUT_KEYS


def output_is_diff_file(output_key: str) -> bool:
    """指定した出力CSVが差分データ用ファイルかどうかを返す。"""
    return output_key in DIFF_OUTPUT_KEYS


def build_output_headers(base_headers: list[str], output_key: str) -> list[str]:
    """出力キーに応じて `diff_type` を先頭付与したヘッダーを返す。"""
    if not output_uses_diff_type(output_key):
        return list(base_headers)
    return [DIFF_TYPE_HEADER, *base_headers]


def build_initial_diff_types(output_key: str, row_count: int) -> list[str | None]:
    """初期データCSV向けの `diff_type` 一覧を返す。"""
    if not output_uses_diff_type(output_key):
        return [None] * row_count
    return [INITIAL_DIFF_TYPE] * row_count


def build_mixed_diff_types(row_count: int) -> list[str]:
    """差分CSV向けに再現性のある `I/U/D` の並びを返す。"""
    return [DIFF_TYPE_ORDER[index % len(DIFF_TYPE_ORDER)] for index in range(row_count)]


def prepend_diff_type(row: list[str], diff_type: str | None) -> list[str]:
    """必要な場合だけ `diff_type` を先頭付与した行を返す。"""
    if diff_type is None:
        return row
    return [diff_type, *row]
