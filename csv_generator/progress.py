from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from tqdm import tqdm


@dataclass(frozen=True)
class ProgressEvent:
    """親プロセスへ送るCSV進捗イベントを保持する。"""

    kind: str
    path: str
    total_rows: int = 0
    delta: int = 0


class NullProgressReporter:
    """進捗表示を行わないダミーレポーター。"""

    def start(self) -> None:
        """開始時の処理を何もしない。"""

    def advance(self, written_rows: int) -> None:
        """進捗更新を何もしない。"""

    def finish(self) -> None:
        """終了時の処理を何もしない。"""


class TqdmProgressReporter:
    """単一ファイル向けに `tqdm` バーを更新する。"""

    def __init__(self, path: Path, total_rows: int, position: int = 0, stream: TextIO | None = None) -> None:
        self.path = path
        self.total_rows = max(total_rows, 0)
        self.position = position
        self.stream = stream or sys.stdout
        self._bar: tqdm | None = None
        self._written_rows = 0

    def start(self) -> None:
        """対象ファイルのプログレスバーを開く。"""
        self._bar = tqdm(
            total=self.total_rows,
            desc=self.path.name,
            unit="rows",
            leave=True,
            dynamic_ncols=True,
            position=self.position,
            file=self.stream,
        )

    def advance(self, written_rows: int) -> None:
        """前回との差分ぶんだけバーを進める。"""
        delta = self._normalize_delta(written_rows)
        self._advance_delta(delta)

    def advance_delta(self, delta: int) -> None:
        """差分行数をそのまま受け取ってバーを進める。"""
        normalized = max(delta, 0)
        if normalized == 0:
            return
        actual_delta = min(normalized, self.total_rows - self._written_rows)
        self._written_rows += actual_delta
        self._advance_delta(actual_delta)

    def _advance_delta(self, delta: int) -> None:
        """実際のバー更新だけを行う。"""
        if delta == 0 or self._bar is None:
            return
        self._bar.update(delta)

    def finish(self) -> None:
        """残件数があれば進めきってバーを閉じる。"""
        if self._bar is None:
            return
        remaining = self.total_rows - self._written_rows
        if remaining > 0:
            self._written_rows += remaining
            self._bar.update(remaining)
        self._bar.close()
        self._bar = None

    def _normalize_delta(self, written_rows: int) -> int:
        """累計行数を差分更新量へ変換する。"""
        bounded_rows = min(max(written_rows, 0), self.total_rows)
        delta = bounded_rows - self._written_rows
        if delta <= 0:
            return 0
        self._written_rows = bounded_rows
        return delta


class QueueProgressReporter:
    """ワーカー側で進捗を間引きつつ親プロセスへ送る。"""

    def __init__(self, path: Path, total_rows: int, progress_queue: object) -> None:
        self.path = path
        self.total_rows = max(total_rows, 0)
        self.progress_queue = progress_queue
        self._written_rows = 0
        self._pending_delta = 0
        self._flush_threshold = max(self.total_rows // 100, 1)

    def start(self) -> None:
        """開始イベントを親プロセスへ送る。"""
        self.progress_queue.put(ProgressEvent("start", str(self.path), total_rows=self.total_rows))

    def advance(self, written_rows: int) -> None:
        """進捗差分を一定量ごとに親プロセスへ送る。"""
        delta = self._normalize_delta(written_rows)
        if delta == 0:
            return
        self._pending_delta += delta
        if self._pending_delta >= self._flush_threshold or self._written_rows == self.total_rows:
            self._flush_pending()

    def finish(self) -> None:
        """残り差分を送って終了イベントを送る。"""
        self._flush_pending()
        self.progress_queue.put(ProgressEvent("finish", str(self.path), total_rows=self.total_rows))

    def _normalize_delta(self, written_rows: int) -> int:
        """累計行数を差分更新量へ変換する。"""
        bounded_rows = min(max(written_rows, 0), self.total_rows)
        delta = bounded_rows - self._written_rows
        if delta <= 0:
            return 0
        self._written_rows = bounded_rows
        return delta

    def _flush_pending(self) -> None:
        """溜めた更新量を親プロセスへ送る。"""
        if self._pending_delta == 0:
            return
        self.progress_queue.put(ProgressEvent("advance", str(self.path), total_rows=self.total_rows, delta=self._pending_delta))
        self._pending_delta = 0


class ProgressDisplayManager:
    """親プロセス側で複数 `tqdm` バーを管理する。"""

    def __init__(self, paths: list[Path], stream: TextIO | None = None) -> None:
        self.stream = stream or sys.stdout
        self.positions = {str(path): index for index, path in enumerate(paths)}
        self._bars: dict[str, TqdmProgressReporter] = {}

    def handle(self, event: ProgressEvent) -> None:
        """受け取ったイベントに応じて対象バーを更新する。"""
        if event.kind == "start":
            self._bars[event.path] = TqdmProgressReporter(
                Path(event.path),
                total_rows=event.total_rows,
                position=self.positions.get(event.path, 0),
                stream=self.stream,
            )
            self._bars[event.path].start()
            return
        reporter = self._bars.get(event.path)
        if reporter is None:
            return
        if event.kind == "advance":
            reporter.advance_delta(event.delta)
            return
        if event.kind == "finish":
            reporter.finish()
            self._bars.pop(event.path, None)

    def close(self) -> None:
        """未終了バーがあれば閉じる。"""
        for reporter in list(self._bars.values()):
            reporter.finish()
        self._bars.clear()


def is_tty_stream(stream: TextIO | None = None) -> bool:
    """指定ストリームがTTYかどうかを返す。"""
    target = stream or sys.stdout
    return hasattr(target, "isatty") and target.isatty()
