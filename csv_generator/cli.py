from __future__ import annotations

import argparse
from pathlib import Path

from .config import DEFAULT_COUNTS, DEFAULT_SEED, FULL_COUNTS, OUTPUT_FILES, VALID_TARGETS
from .format_spec import load_specs
from .generators import CsvGenerator
from .io import write_csv


def parse_args() -> argparse.Namespace:
    """CSV生成CLIの引数を解釈する。"""
    parser = argparse.ArgumentParser(description="Generate dummy CSV files from docs/format.md")
    parser.add_argument("--output-dir", default="generated_data")
    parser.add_argument("--targets", default="campaign,agency,product")
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


def main() -> None:
    """CLIの入口として、仕様読込からCSV出力までを統括する。"""
    args = parse_args()
    targets = parse_targets(args.targets)
    counts = FULL_COUNTS if args.full else DEFAULT_COUNTS
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    specs = load_specs(Path("docs/format.md"))
    generator = CsvGenerator(specs=specs, seed=args.seed, counts=counts)

    if "campaign" in targets:
        write_csv(
            output_dir / OUTPUT_FILES["campaign"],
            [column.header_label for column in specs["campaign"]],
            generator.campaign_rows(),
        )

    if "agency" in targets:
        generator.write_agency_files(output_dir)

    if "product" in targets:
        write_csv(
            output_dir / OUTPUT_FILES["product"],
            [column.header_label for column in specs["product"]],
            generator.product_rows(),
        )
