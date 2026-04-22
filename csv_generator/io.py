from __future__ import annotations

import csv
import gzip
from pathlib import Path
from typing import TextIO


def _create_csv_writer(handle: TextIO) -> csv.writer:
    """全文字列を常にダブルクォートするCSV writerを生成する。"""
    return csv.writer(handle, quoting=csv.QUOTE_ALL)


def _open_text_writer(path: Path) -> TextIO:
    """CSVを書き込むためのテキストストリームを開く。"""
    if path.suffix == ".gz":
        return gzip.open(path, "wt", encoding="utf-8-sig", newline="")
    return path.open("w", encoding="utf-8-sig", newline="")


def build_output_path(output_dir: Path, output_name: str, compress: bool) -> Path:
    """出力先ディレクトリと圧縮設定から実ファイルパスを組み立てる。"""
    path = output_dir / output_name
    if compress:
        return path.with_name(f"{path.name}.gz")
    return path


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    """BOM付きUTF-8でCSVを一括書き出しする。"""
    with _open_text_writer(path) as fh:
        writer = _create_csv_writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)


def open_csv_writer(path: Path) -> tuple[TextIO, csv.writer]:
    """逐次書き込み用のCSV writerを返す。"""
    handle = _open_text_writer(path)
    return handle, _create_csv_writer(handle)
