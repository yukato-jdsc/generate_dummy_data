from __future__ import annotations

INITIAL_DIFF_TYPE = "I"
UPDATE_DIFF_TYPE = "U"
DIFF_TYPE_ORDER = (INITIAL_DIFF_TYPE, UPDATE_DIFF_TYPE)
DIFF_TYPE_ORDERS_BY_OUTPUT_KEY = {
    "corp_diff": (INITIAL_DIFF_TYPE, UPDATE_DIFF_TYPE),
    "bfs_device_diff": (INITIAL_DIFF_TYPE,),
    "bfs_accessories_diff": (INITIAL_DIFF_TYPE, UPDATE_DIFF_TYPE),
}


def build_output_headers(base_headers: list[str], _output_key: str) -> list[str]:
    """出力キーに関わらず仕様定義どおりのヘッダーを返す。"""
    return list(base_headers)


def build_initial_diff_types(_output_key: str, row_count: int) -> list[str | None]:
    """初期データCSV向けに、出力しない内部差分種別の一覧を返す。"""
    return [None] * row_count


def build_mixed_diff_types(output_key: str, row_count: int) -> list[str]:
    """差分CSV向けに出力キーごとの `diff_type` 並びを返す。"""
    diff_type_order = DIFF_TYPE_ORDERS_BY_OUTPUT_KEY.get(output_key, DIFF_TYPE_ORDER)
    return [diff_type_order[index % len(diff_type_order)] for index in range(row_count)]


def prepend_diff_type(row: list[str], _diff_type: str | None) -> list[str]:
    """内部用の差分種別をCSV行へ出力せず、元の行を返す。"""
    return row
