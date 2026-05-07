from __future__ import annotations

import csv
import gzip
from datetime import date, timedelta
from pathlib import Path
from typing import TextIO

from .progress import NullProgressReporter, QueueProgressReporter, TqdmProgressReporter

ProgressReporter = NullProgressReporter | QueueProgressReporter | TqdmProgressReporter


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


def dated_output_name(output_name: str, base_date: date) -> str:
    """出力CSV名に基準日または差分用の翌日をYYYYMMDD形式で付与する。"""
    output_date = base_date
    if Path(output_name).stem.endswith("_diff"):
        output_date = base_date + timedelta(days=1)
    return f"{output_date:%Y%m%d}_{output_name}"


def build_dated_output_path(
    output_dir: Path,
    output_name: str,
    compress: bool,
    base_date: date,
) -> Path:
    """日付プレフィックス付きの出力ファイルパスを組み立てる。"""
    return build_output_path(output_dir, dated_output_name(output_name, base_date), compress)


def write_csv(
    path: Path,
    headers: list[str],
    rows: list[list[str]],
    progress_reporter: ProgressReporter | None = None,
) -> None:
    """BOM付きUTF-8でCSVを書き出し、必要に応じて進捗を通知する。"""
    with _open_text_writer(path) as fh:
        writer = _create_csv_writer(fh)
        if progress_reporter is not None:
            progress_reporter.start()
        writer.writerow(headers)
        for index, row in enumerate(rows, start=1):
            writer.writerow(row)
            if progress_reporter is not None:
                progress_reporter.advance(index)
        if progress_reporter is not None:
            progress_reporter.finish()


def open_csv_writer(path: Path) -> tuple[TextIO, csv.writer]:
    """逐次書き込み用のCSV writerを返す。"""
    handle = _open_text_writer(path)
    return handle, _create_csv_writer(handle)
