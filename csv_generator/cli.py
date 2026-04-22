from __future__ import annotations

import argparse
from pathlib import Path

from .config import ColumnSpec, DEFAULT_COUNTS, DEFAULT_SEED, FULL_COUNTS, OUTPUT_FILES, VALID_TARGETS
from .format_spec import load_specs
from .generators import CsvGenerator
from .io import build_output_path, write_csv


def announce_output(path: Path) -> None:
    """これから生成するCSVファイルの出力先をコンソールへ表示する。"""
    print(f"Generating {path}")


def parse_args() -> argparse.Namespace:
    """CSV生成CLIの引数を解釈する。"""
    parser = argparse.ArgumentParser(description="Generate dummy CSV files from docs/format/")
    parser.add_argument("--output-dir", default="generated_data")
    parser.add_argument("--targets", default="campaign,agency,compass,product,bfs")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def parse_targets(raw_targets: str) -> list[str]:
    """カンマ区切りの target 指定を検証し、内部表現へ変換する。"""
    targets = [target.strip() for target in raw_targets.split(",") if target.strip()]
    unknown = sorted(set(targets) - VALID_TARGETS)
    if unknown:
        raise SystemExit(f"Unknown targets: {', '.join(unknown)}")
    return targets or sorted(VALID_TARGETS)


def header_labels(specs: dict[str, list[ColumnSpec]], spec_key: str) -> list[str]:
    """指定したCSV仕様からヘッダー表示名の一覧を取り出す。"""
    return [column.header_label for column in specs[spec_key]]


def announce_outputs(paths: list[Path]) -> None:
    """複数の出力先を順に表示する。"""
    for path in paths:
        announce_output(path)


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
    write_csv(path, headers, rows)


def _write_campaign_csv(
    output_dir: Path,
    specs: dict[str, list[ColumnSpec]],
    generator: CsvGenerator,
    compress: bool,
) -> None:
    """campaign 対象のCSVを書き出す。"""
    write_target_csv(
        output_dir,
        OUTPUT_FILES["campaign"],
        header_labels(specs, "campaign"),
        generator.campaign_rows(),
        compress=compress,
    )


def _write_product_csv(
    output_dir: Path,
    specs: dict[str, list[ColumnSpec]],
    generator: CsvGenerator,
    compress: bool,
) -> None:
    """product 対象のCSVを書き出す。"""
    write_target_csv(
        output_dir,
        OUTPUT_FILES["product"],
        header_labels(specs, "product"),
        generator.product_rows(),
        compress=compress,
    )


def _write_agency_csvs(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """agency 対象の全量・差分CSVを書き出す。"""
    announce_outputs(
        [
            build_output_path(output_dir, OUTPUT_FILES["agency_all"], compress),
            build_output_path(output_dir, OUTPUT_FILES["agency_diff"], compress),
        ]
    )
    generator.write_agency_files(output_dir, compress=compress)


def _write_compass_csv(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """compass 対象のCSVを書き出す。"""
    announce_output(build_output_path(output_dir, OUTPUT_FILES["compass"], compress))
    generator.write_compass_file(output_dir, compress=compress)


def _write_bfs_csvs(output_dir: Path, generator: CsvGenerator, compress: bool) -> None:
    """bfs 対象の全量・差分CSVを書き出す。"""
    announce_outputs(
        [
            build_output_path(output_dir, OUTPUT_FILES["bfs_all"], compress),
            build_output_path(output_dir, OUTPUT_FILES["bfs_diff"], compress),
        ]
    )
    generator.write_bfs_files(output_dir, compress=compress)


def main() -> None:
    """CLIの入口として、仕様読込からCSV出力までを統括する。"""
    args = parse_args()
    targets = parse_targets(args.targets)
    counts = FULL_COUNTS if args.full else DEFAULT_COUNTS
    compress = args.full
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    specs = load_specs(Path("docs/format"))
    generator = CsvGenerator(specs=specs, seed=args.seed, counts=counts)
    for target in targets:
        if target == "campaign":
            _write_campaign_csv(output_dir, specs, generator, compress)
        elif target == "agency":
            _write_agency_csvs(output_dir, generator, compress)
        elif target == "product":
            _write_product_csv(output_dir, specs, generator, compress)
        elif target == "compass":
            _write_compass_csv(output_dir, generator, compress)
        elif target == "bfs":
            _write_bfs_csvs(output_dir, generator, compress)
