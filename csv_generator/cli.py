from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from multiprocessing import Manager
from pathlib import Path
from queue import Empty

from .config import (
    DEFAULT_COUNTS,
    DEFAULT_SEED,
    FULL_COUNTS,
    OUTPUT_FILES,
    VALID_TARGETS,
)
from .format_spec import load_specs
from .generators import (
    BFS_FAMILY_FILES,
    CORP_FAMILY_FILES,
    CsvGenerator,
    CsvWriteJob,
    ProgressFactory,
    run_csv_write_job,
)
from .io import build_dated_output_path, build_output_path, write_csv
from .progress import (
    NullProgressReporter,
    ProgressDisplayManager,
    ProgressEvent,
    TqdmProgressReporter,
    is_tty_stream,
)

CORP_OUTPUT_KEYS = tuple(output_key for output_key, _ in CORP_FAMILY_FILES)
CAMPAIGN_OUTPUT_KEYS = ("campaign", "campaign_diff")
COMPASS_OUTPUT_KEYS = ("compass_all", "compass_diff")
PRODUCT_OUTPUT_KEYS = ("product", "product_diff")


def announce_output(path: Path) -> None:
    """これから生成するCSVファイルの出力先をコンソールへ表示する。"""
    if is_tty_stream():
        return
    print(f"Generating {path}", flush=True)


def build_progress_factory(position_lookup: dict[str, int] | None = None) -> ProgressFactory:
    """TTY有無に応じた進捗レポーター生成関数を返す。"""
    if not is_tty_stream():
        return lambda path, total_rows: NullProgressReporter()

    def factory(path: Path, total_rows: int) -> TqdmProgressReporter:
        position = 0
        if position_lookup is not None:
            position = position_lookup.get(str(path), 0)
        return TqdmProgressReporter(path, total_rows, position=position)

    return factory


def parse_args() -> argparse.Namespace:
    """CSV生成CLIの引数を解釈する。"""
    parser = argparse.ArgumentParser(description="Generate dummy CSV files from docs/format/")
    parser.add_argument("--output-dir", default="generated_data")
    parser.add_argument("--targets", default="campaign,agency,compass,product,corp,bfs")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--gzip", action="store_true")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--jobs", default="auto")
    return parser.parse_args()


def parse_targets(raw_targets: str) -> list[str]:
    """カンマ区切りの target 指定を検証し、内部表現へ変換する。"""
    targets = [target.strip() for target in raw_targets.split(",") if target.strip()]
    unknown = sorted(set(targets) - VALID_TARGETS)
    if unknown:
        raise SystemExit(f"Unknown targets: {', '.join(unknown)}")
    return targets or sorted(VALID_TARGETS)


def parse_jobs(raw_jobs: str) -> int | None:
    """jobs 指定を解釈し、auto は None、数値は正の整数へ変換する。"""
    normalized = raw_jobs.strip().lower()
    if normalized == "auto":
        return None
    try:
        jobs = int(normalized)
    except ValueError as exc:
        raise SystemExit("--jobs must be 'auto' or a positive integer") from exc
    if jobs < 1:
        raise SystemExit("--jobs must be 'auto' or a positive integer")
    return jobs


def resolve_job_count(requested_jobs: int | None, task_count: int, full: bool) -> int:
    """実行条件から最終的なワーカー数を決定する。"""
    if task_count <= 1:
        return 1
    if requested_jobs is None:
        if not full:
            return 1
        return min(os.cpu_count() or 1, task_count)
    return min(requested_jobs, task_count)


def announce_outputs(paths: list[Path]) -> None:
    """複数の出力先を順に表示する。"""
    for path in paths:
        announce_output(path)


def build_output_path_for_key(
    output_dir: Path,
    output_key: str,
    compress: bool,
    output_date: date,
) -> Path:
    """出力キーから日付プレフィックス付き実ファイルパスを返す。"""
    return build_dated_output_path(output_dir, OUTPUT_FILES[output_key], compress, output_date)


def build_output_paths_for_keys(
    output_dir: Path,
    output_keys: tuple[str, ...],
    compress: bool,
    output_date: date,
) -> list[Path]:
    """複数の出力キーを日付プレフィックス付き実ファイルパスへ変換する。"""
    return [build_output_path_for_key(output_dir, output_key, compress, output_date) for output_key in output_keys]


def build_jobs(
    targets: list[str],
    output_dir: Path,
    format_dir: Path,
    seed: int,
    counts: dict[str, int],
    compress: bool,
    output_date: date,
) -> list[CsvWriteJob]:
    """target 指定をファイル単位の実行ジョブへ展開する。"""
    jobs: list[CsvWriteJob] = []
    common = {
        "output_dir": str(output_dir),
        "format_dir": str(format_dir),
        "seed": seed,
        "counts": counts,
        "compress": compress,
        "output_date": output_date,
    }
    for target in targets:
        if target == "campaign":
            jobs.append(CsvWriteJob(job_type="campaign", **common))
        elif target == "agency":
            jobs.append(CsvWriteJob(job_type="agency", **common))
        elif target == "product":
            jobs.append(CsvWriteJob(job_type="product", **common))
        elif target == "compass":
            jobs.append(CsvWriteJob(job_type="compass", **common))
        elif target == "corp":
            for output_key, variant in CORP_FAMILY_FILES:
                jobs.append(CsvWriteJob(job_type="corp", output_key=output_key, variant=variant, **common))
        elif target == "bfs":
            for spec_key, output_key, variant in BFS_FAMILY_FILES:
                jobs.append(
                    CsvWriteJob(
                        job_type="bfs",
                        spec_key=spec_key,
                        output_key=output_key,
                        variant=variant,
                        **common,
                    )
                )
    return jobs


def job_output_paths(jobs: list[CsvWriteJob], output_dir: Path) -> list[Path]:
    """ジョブ一覧に対応する実ファイルパス一覧を表示順のまま返す。"""
    paths: list[Path] = []
    for job in jobs:
        if job.job_type == "campaign":
            paths.extend(build_output_paths_for_keys(output_dir, CAMPAIGN_OUTPUT_KEYS, job.compress, job.output_date))
            continue
        if job.job_type == "agency":
            paths.extend(
                build_output_paths_for_keys(output_dir, ("agency_all", "agency_diff"), job.compress, job.output_date)
            )
            continue
        if job.job_type == "compass":
            paths.extend(build_output_paths_for_keys(output_dir, COMPASS_OUTPUT_KEYS, job.compress, job.output_date))
            continue
        if job.job_type == "product":
            paths.extend(build_output_paths_for_keys(output_dir, PRODUCT_OUTPUT_KEYS, job.compress, job.output_date))
            continue
        assert job.output_key is not None
        paths.append(build_output_path_for_key(output_dir, job.output_key, job.compress, job.output_date))
    return paths


def execute_jobs(jobs: list[CsvWriteJob], max_workers: int) -> None:
    """ジョブ一覧を直列またはプロセス並列で実行する。"""
    output_paths = job_output_paths(jobs, Path(jobs[0].output_dir))
    position_lookup = {str(path): index for index, path in enumerate(output_paths)}
    progress_factory = build_progress_factory(position_lookup)
    if max_workers == 1:
        for job in jobs:
            run_csv_write_job(job, progress_factory=progress_factory)
        return
    if not is_tty_stream():
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_csv_write_job, job) for job in jobs]
            for future in futures:
                future.result()
        return
    with Manager() as manager:
        progress_queue = manager.Queue()
        display_manager = ProgressDisplayManager(output_paths)
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(run_csv_write_job, job, progress_queue=progress_queue)
                for job in jobs
            ]
            while True:
                try:
                    event = progress_queue.get(timeout=0.1)
                    if isinstance(event, ProgressEvent):
                        display_manager.handle(event)
                except Empty:
                    if all(future.done() for future in futures):
                        break
            while True:
                try:
                    event = progress_queue.get_nowait()
                    if isinstance(event, ProgressEvent):
                        display_manager.handle(event)
                except Empty:
                    break
            for future in futures:
                future.result()
        display_manager.close()


def write_target_csv(
    output_dir: Path,
    output_name: str,
    headers: list[str],
    rows: list[list[str]],
    compress: bool = False,
) -> None:
    """生成対象CSVの出力先表示と書き出しをまとめて行う。"""
    path = build_output_path(output_dir, output_name, compress)
    announce_output(path)
    progress_factory = build_progress_factory()
    progress_reporter = progress_factory(path, len(rows))
    write_csv(path, headers, rows, progress_reporter=progress_reporter)


def _write_campaign_csvs(
    output_dir: Path,
    generator: CsvGenerator,
    compress: bool,
) -> None:
    """campaign 対象の全量・全量更新diff CSVを書き出す。"""
    announce_outputs(build_output_paths_for_keys(output_dir, CAMPAIGN_OUTPUT_KEYS, compress, generator.output_date))
    generator.write_campaign_files(output_dir, compress=compress, progress_factory=build_progress_factory())


def _write_product_csvs(
    output_dir: Path,
    generator: CsvGenerator,
    compress: bool,
) -> None:
    """product 対象の全量・全量更新diff CSVを書き出す。"""
    announce_outputs(build_output_paths_for_keys(output_dir, PRODUCT_OUTPUT_KEYS, compress, generator.output_date))
    generator.write_product_files(output_dir, compress=compress, progress_factory=build_progress_factory())


def _write_agency_csvs(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """agency 対象の全量・差分CSVを書き出す。"""
    announce_outputs(build_output_paths_for_keys(output_dir, ("agency_all", "agency_diff"), compress, generator.output_date))
    generator.write_agency_files(output_dir, compress=compress, progress_factory=build_progress_factory())


def _write_compass_csv(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """compass 対象の全量・差分CSVを書き出す。"""
    announce_outputs(build_output_paths_for_keys(output_dir, COMPASS_OUTPUT_KEYS, compress, generator.output_date))
    generator.write_compass_files(
        output_dir,
        compress=compress,
        progress_factory=build_progress_factory(),
    )


def _write_bfs_csvs(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """bfs 対象の全量・差分CSVを書き出す。"""
    announce_outputs(
        build_output_paths_for_keys(
            output_dir,
            (
                "bfs_all",
                "bfs_diff",
                "bfs_device_all",
                "bfs_device_diff",
                "bfs_accessories_all",
                "bfs_accessories_diff",
            ),
            compress,
            generator.output_date,
        )
    )
    generator.write_bfs_files(output_dir, compress=compress, progress_factory=build_progress_factory())


def _write_corp_csvs(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """corp 対象の全量・差分CSVを書き出す。"""
    announce_outputs(build_output_paths_for_keys(output_dir, CORP_OUTPUT_KEYS, compress, generator.output_date))
    generator.write_corp_files(output_dir, compress=compress, progress_factory=build_progress_factory())


def main() -> None:
    """CLIの入口として、仕様読込からCSV出力までを統括する。"""
    args = parse_args()
    targets = parse_targets(args.targets)
    requested_jobs = parse_jobs(args.jobs)
    counts = FULL_COUNTS if args.full else DEFAULT_COUNTS
    compress = args.gzip
    output_dir = Path(args.output_dir)
    output_date = date.today()
    format_dir = Path("docs/format")
    output_dir.mkdir(parents=True, exist_ok=True)

    specs = load_specs(format_dir)
    generator = CsvGenerator(specs=specs, seed=args.seed, counts=counts, output_date=output_date)
    if requested_jobs == 1:
        for target in targets:
            if target == "campaign":
                _write_campaign_csvs(output_dir, generator, compress)
            elif target == "agency":
                _write_agency_csvs(output_dir, generator, compress)
            elif target == "product":
                _write_product_csvs(output_dir, generator, compress)
            elif target == "compass":
                _write_compass_csv(output_dir, generator, compress)
            elif target == "corp":
                _write_corp_csvs(output_dir, generator, compress)
            elif target == "bfs":
                _write_bfs_csvs(output_dir, generator, compress)
        return

    jobs = build_jobs(targets, output_dir, format_dir, args.seed, counts, compress, output_date)
    announce_outputs(job_output_paths(jobs, output_dir))
    execute_jobs(jobs, resolve_job_count(requested_jobs, len(jobs), args.full))
