from __future__ import annotations

import csv
from pathlib import Path


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    """BOM付きUTF-8でCSVを一括書き出しする。"""
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)


def open_csv_writer(path: Path) -> tuple[object, csv.writer]:
    """逐次書き込み用のCSV writerを返す。"""
    handle = path.open("w", encoding="utf-8-sig", newline="")
    return handle, csv.writer(handle)
