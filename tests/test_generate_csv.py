from __future__ import annotations

import csv
import gzip
import os
import re
import subprocess
import sys
import tomllib
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from csv_generator import progress as progress_module
from csv_generator.cli import (
    parse_jobs,
    parse_targets,
    resolve_job_count,
    write_target_csv,
)
from csv_generator.config import DEFAULT_COUNTS
from csv_generator.format_spec import load_specs, parse_section_columns
from csv_generator.generators import CsvGenerator
from csv_generator.io import (
    build_dated_output_path,
    build_output_path,
    dated_output_name,
)
from csv_generator.progress import NullProgressReporter, TqdmProgressReporter

SCRIPT = ROOT / "generate_csv.py"
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
BASE_OUTPUT_FILES = [
    "b_hjn_bfs_モバイル_エントリ情報.csv",
    "b_hjn_bfs_モバイル_エントリ情報_diff.csv",
    "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv",
    "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv",
    "b_hjn_bfs_モバイル_サービスサマリ_端末.csv",
    "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv",
    "b_hjn_com_営業決裁.csv",
    "b_hjn_com_営業決裁_diff.csv",
    "m_hjn_smt_統一企業情報_1.csv",
    "m_hjn_smt_統一企業情報_2.csv",
    "m_hjn_smt_統一企業情報_diff.csv",
    "m_キャンペーン.csv",
    "m_キャンペーン_diff.csv",
    "m_取次店_all.csv",
    "m_取次店_all_diff.csv",
    "m_商品_all.csv",
    "m_商品_all_diff.csv",
]
DEFAULT_OUTPUT_FILES = sorted(dated_output_name(name, TODAY) for name in BASE_OUTPUT_FILES)


def test_unit_tests_do_not_use_full_option() -> None:
    """単体テスト内で `--full` 実行を使わない方針を守る。"""
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = "--" + "full"
    assert f'"{forbidden}"' not in source


def run_script(
    output_dir: str,
    *args: str,
    expect_success: bool = True,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    """CLI を実行し、必要に応じて正常終了を検証する。"""
    command = ["uv", "run", "python", str(SCRIPT), "--output-dir", output_dir, *args]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if expect_success:
        assert completed.returncode == 0, f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    return completed


def read_csv(directory: Path, name: str) -> tuple[list[str], list[list[str]]]:
    """CSV のヘッダーとデータ行を読み込む。"""
    path = directory / name
    if not path.exists():
        if name.endswith(".csv.gz"):
            path = directory / f"{dated_output_name(name.removesuffix('.gz'), TODAY)}.gz"
        else:
            path = directory / dated_output_name(name, TODAY)
    if path.suffix == ".gz":
        handle = gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    else:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    with handle as fh:
        rows = list(csv.reader(fh))
    return rows[0], rows[1:]


def generated_files(directory: Path) -> list[str]:
    """生成された CSV ファイル名をソートして返す。"""
    return sorted(path.name for path in directory.iterdir() if path.is_file())


def expected_output_files(*names: str, compress: bool = False) -> list[str]:
    """論理CSV名から日付付きの期待ファイル名一覧を返す。"""
    suffix = ".gz" if compress else ""
    return sorted(f"{dated_output_name(name, TODAY)}{suffix}" for name in names)


def load_pyproject() -> dict[str, object]:
    """pyproject.toml を辞書として読み込む。"""
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def generate_fixture_dir(tmp_path_factory: pytest.TempPathFactory, name: str, *args: str) -> Path:
    """テスト用のCSV生成結果ディレクトリを作り、指定条件で一度だけ生成する。"""
    directory = tmp_path_factory.mktemp(name)
    run_script(str(directory), *args)
    return directory


def assert_all_cells_filled(header: list[str], rows: list[list[str]], name: str) -> None:
    """CSV内の全セルが空欄でないことを検証する。"""
    assert header, f"{name}: header is empty"
    for row_index, row in enumerate(rows, start=1):
        assert len(row) == len(header), f"{name}: row={row_index}, columns={len(row)}, header={len(header)}"
        for column_index, value in enumerate(row):
            assert value != "", f"{name}: row={row_index}, column={header[column_index]}"


def bfs_device_column_index(header: list[str], column_name: str) -> int:
    """BFSサービスサマリ端末の英字カラム名からCSV列位置を返す。"""
    specs = load_specs(ROOT / "docs/format")
    labels = {column.name: column.header_label for column in specs["bfs_device"]}
    return header.index(labels[column_name])


@pytest.fixture(scope="module")
def generated_default_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """デフォルト実行結果をモジュール内で使い回す。"""
    return generate_fixture_dir(tmp_path_factory, "generated-default")


@pytest.fixture(scope="module")
def generated_seed7_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """seed=7 の全件実行結果をモジュール内で使い回す。"""
    return generate_fixture_dir(tmp_path_factory, "generated-seed7", "--seed", "7")


@pytest.fixture(scope="module")
def generated_agency_seed11_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """agency の seed=11 実行結果をモジュール内で使い回す。"""
    return generate_fixture_dir(tmp_path_factory, "generated-agency-seed11", "--targets", "agency", "--seed", "11")


@pytest.fixture(scope="module")
def generated_compass_seed11_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """compass の seed=11 実行結果をモジュール内で使い回す。"""
    return generate_fixture_dir(tmp_path_factory, "generated-compass-seed11", "--targets", "compass", "--seed", "11")


def test_default_run_generates_all_expected_files(generated_default_dir: Path) -> None:
    files = generated_files(generated_default_dir)
    assert files == DEFAULT_OUTPUT_FILES

    _, campaign_rows = read_csv(generated_default_dir, "m_キャンペーン.csv")
    _, agency_rows = read_csv(generated_default_dir, "m_取次店_all.csv")
    _, agency_diff_rows = read_csv(generated_default_dir, "m_取次店_all_diff.csv")
    _, compass_all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, compass_diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")
    _, product_rows = read_csv(generated_default_dir, "m_商品_all.csv")
    _, product_diff_rows = read_csv(generated_default_dir, "m_商品_all_diff.csv")
    _, bfs_all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, bfs_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    _, bfs_device_all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, bfs_device_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    _, bfs_accessories_all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, bfs_accessories_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")
    _, corp_all_1_rows = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_1.csv")
    _, corp_all_2_rows = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_2.csv")
    _, corp_diff_rows = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_diff.csv")
    _, campaign_diff_rows = read_csv(generated_default_dir, "m_キャンペーン_diff.csv")

    assert len(campaign_rows) == 50
    assert len(campaign_diff_rows) == 50
    assert len(agency_rows) == 1000
    assert len(agency_diff_rows) == 53
    assert len(compass_all_rows) == 100
    assert len(compass_diff_rows) == 20
    assert len(product_rows) == 1000
    assert len(product_diff_rows) == 1000
    assert len(bfs_all_rows) == 1000
    assert len(bfs_diff_rows) == 100
    assert len(bfs_device_all_rows) == 1000
    assert len(bfs_device_diff_rows) == 100
    assert len(bfs_accessories_all_rows) == 1000
    assert len(bfs_accessories_diff_rows) == 100
    assert len(corp_all_1_rows) == 500
    assert len(corp_all_2_rows) == 500
    assert len(corp_diff_rows) == 100


def test_bfs_entry_information_uncompressed_size_is_reduced(generated_default_dir: Path) -> None:
    """BFSエントリ情報CSVの圧縮前サイズを現行想定の3/4程度に抑える。"""
    output_path = generated_default_dir / dated_output_name("b_hjn_bfs_モバイル_エントリ情報.csv", TODAY)

    assert output_path.stat().st_size <= 2_900_000


def test_bfs_device_summary_uncompressed_size_is_reduced(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末CSVの圧縮前サイズを現行の1/2程度に抑える。"""
    output_path = generated_default_dir / dated_output_name("b_hjn_bfs_モバイル_サービスサマリ_端末.csv", TODAY)

    assert output_path.stat().st_size <= 3_000_000


def test_bfs_entry_numbers_do_not_wrap_after_six_digits() -> None:
    """BFSエントリ番号は桁数の境界を超えても連番が巻き戻らない。"""
    specs = load_specs(ROOT / "docs" / "format")
    counts = DEFAULT_COUNTS | {"bfs_all": 1_000_001}
    generator = CsvGenerator(specs=specs, seed=42, counts=counts)

    first_context = generator._bfs_service_context(0, "all")
    million_context = generator._bfs_service_context(1_000_000, "all")
    large_context = generator._bfs_service_context(100_000_000, "all")

    assert len({first_context["entry_number"], million_context["entry_number"], large_context["entry_number"]}) == 3


def test_targets_campaign_only_generates_campaign_files(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "campaign")
    assert generated_files(tmp_path) == expected_output_files("m_キャンペーン.csv", "m_キャンペーン_diff.csv")


def test_targets_product_only_generates_product_files(tmp_path: Path) -> None:
    """product 指定では商品全量と全量更新diffだけを生成する。"""
    run_script(str(tmp_path), "--targets", "product")
    assert generated_files(tmp_path) == expected_output_files("m_商品_all.csv", "m_商品_all_diff.csv")


def test_pyproject_includes_ruff_in_dev_dependencies() -> None:
    """開発依存関係に ruff を含める。"""
    pyproject = load_pyproject()
    dependency_groups = pyproject["dependency-groups"]
    assert "ruff>=0.12.0" in dependency_groups["dev"]


def test_pyproject_defines_ruff_configuration() -> None:
    """Ruff の lint 設定を pyproject.toml に持つ。"""
    pyproject = load_pyproject()
    tool = pyproject["tool"]
    ruff_config = tool["ruff"]
    lint_config = ruff_config["lint"]

    assert ruff_config["target-version"] == "py312"
    assert ruff_config["line-length"] == 88
    assert lint_config["select"] == ["E", "F", "I", "UP", "B"]
    assert lint_config["ignore"] == ["E501"]
    assert lint_config["per-file-ignores"] == {"tests/test_generate_csv.py": ["E402"]}


def test_readme_mentions_ruff_check_command() -> None:
    """README に Ruff 実行手順を載せる。"""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "uv run ruff check ." in readme


def test_readme_mentions_headers_only_option() -> None:
    """README に headers-only 実行手順を載せる。"""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "--headers-only" in readme


def test_targets_compass_only_generates_single_file(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "compass")
    assert generated_files(tmp_path) == expected_output_files("b_hjn_com_営業決裁.csv", "b_hjn_com_営業決裁_diff.csv")


def test_targets_bfs_only_generates_two_files(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "bfs")
    assert generated_files(tmp_path) == expected_output_files(
        "b_hjn_bfs_モバイル_エントリ情報.csv",
        "b_hjn_bfs_モバイル_エントリ情報_diff.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_端末.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv",
    )


def test_targets_corp_only_generates_three_files(tmp_path: Path) -> None:
    """corp 指定では統一企業情報の3ファイルだけを生成する。"""
    run_script(str(tmp_path), "--targets", "corp")
    assert generated_files(tmp_path) == expected_output_files(
        "m_hjn_smt_統一企業情報_1.csv",
        "m_hjn_smt_統一企業情報_2.csv",
        "m_hjn_smt_統一企業情報_diff.csv",
    )


def test_parse_targets_trims_values_and_defaults_when_empty() -> None:
    """target指定は前後空白を除去し、空なら全対象へ戻す。"""
    assert parse_targets(" campaign , bfs ") == ["campaign", "bfs"]
    assert parse_targets(" , ") == ["agency", "bfs", "campaign", "compass", "corp", "product"]


def test_parse_jobs_accepts_auto_and_positive_integer() -> None:
    """jobs指定は auto または正の整数だけを受け付ける。"""
    assert parse_jobs("auto") is None
    assert parse_jobs(" 3 ") == 3


def test_resolve_job_count_uses_serial_by_default_and_caps_requested_jobs() -> None:
    """jobs 解決は通常実行を直列にし、上限は実行タスク数で丸める。"""
    assert resolve_job_count(None, task_count=3, full=False) == 1
    assert resolve_job_count(None, task_count=3, full=True) == min(os.cpu_count() or 1, 3)
    assert resolve_job_count(8, task_count=3, full=False) == 3


def test_jobs_argument_rejects_zero(tmp_path: Path) -> None:
    """jobs には 1 以上の整数だけを許可する。"""
    completed = run_script(str(tmp_path), "--jobs", "0", expect_success=False)

    assert completed.returncode != 0
    assert "--jobs" in completed.stderr


def test_console_outputs_generated_file_names(tmp_path: Path) -> None:
    completed = run_script(str(tmp_path), "--targets", "campaign,agency,compass,corp")

    assert "m_キャンペーン.csv" in completed.stdout
    assert "m_キャンペーン_diff.csv" in completed.stdout
    assert "m_取次店_all.csv" in completed.stdout
    assert "m_取次店_all_diff.csv" in completed.stdout
    assert "b_hjn_com_営業決裁.csv" in completed.stdout
    assert "b_hjn_com_営業決裁_diff.csv" in completed.stdout
    assert "m_hjn_smt_統一企業情報_1.csv" in completed.stdout
    assert "m_hjn_smt_統一企業情報_2.csv" in completed.stdout
    assert "m_hjn_smt_統一企業情報_diff.csv" in completed.stdout
    assert "m_商品_all.csv" not in completed.stdout


def test_console_does_not_emit_progress_lines_when_not_tty(tmp_path: Path) -> None:
    """非TTY環境では進捗バー由来の行を出力しない。"""
    completed = run_script(str(tmp_path), "--targets", "campaign")

    assert "Generating" in completed.stdout
    assert "0%" not in completed.stdout
    assert "100%" not in completed.stdout


def test_gzip_option_outputs_gzip_csv(tmp_path: Path) -> None:
    """gzip指定時は通常件数でも `.csv.gz` を生成する。"""
    completed = run_script(str(tmp_path), "--targets", "campaign", "--gzip")

    assert generated_files(tmp_path) == expected_output_files(
        "m_キャンペーン.csv",
        "m_キャンペーン_diff.csv",
        compress=True,
    )
    assert f"{TODAY:%Y%m%d}_m_キャンペーン.csv.gz" in completed.stdout
    assert f"{TOMORROW:%Y%m%d}_m_キャンペーン_diff.csv.gz" in completed.stdout
    _, rows = read_csv(tmp_path, "m_キャンペーン.csv.gz")
    _, diff_rows = read_csv(tmp_path, "m_キャンペーン_diff.csv.gz")
    assert len(rows) == 50
    assert len(diff_rows) == 50


def test_headers_only_campaign_outputs_headers_without_rows(
    tmp_path: Path,
    generated_default_dir: Path,
) -> None:
    """headers-only指定時は対象CSVをヘッダー行だけで生成する。"""
    completed = run_script(str(tmp_path), "--targets", "campaign", "--headers-only")

    assert generated_files(tmp_path) == expected_output_files("m_キャンペーン.csv", "m_キャンペーン_diff.csv")
    assert "m_キャンペーン.csv" in completed.stdout
    assert "m_キャンペーン_diff.csv" in completed.stdout

    normal_header, _ = read_csv(generated_default_dir, "m_キャンペーン.csv")
    normal_diff_header, _ = read_csv(generated_default_dir, "m_キャンペーン_diff.csv")
    header, rows = read_csv(tmp_path, "m_キャンペーン.csv")
    diff_header, diff_rows = read_csv(tmp_path, "m_キャンペーン_diff.csv")

    assert header == normal_header
    assert diff_header == normal_diff_header
    assert rows == []
    assert diff_rows == []


def test_headers_only_omits_diff_type_headers(tmp_path: Path) -> None:
    """headers-only指定でも差分更新CSVに diff_type ヘッダーを出力しない。"""
    run_script(str(tmp_path), "--targets", "agency", "--headers-only")

    header, rows = read_csv(tmp_path, "m_取次店_all.csv")
    diff_header, diff_rows = read_csv(tmp_path, "m_取次店_all_diff.csv")

    assert header[0] == "取次店コード"
    assert diff_header[0] == "取次店コード"
    assert "diff_type" not in header
    assert "diff_type" not in diff_header
    assert rows == []
    assert diff_rows == []


def test_headers_only_can_write_gzip_csv(tmp_path: Path) -> None:
    """headers-only指定はgzip出力でもヘッダー行だけを書き出す。"""
    completed = run_script(str(tmp_path), "--targets", "campaign", "--headers-only", "--gzip")

    assert generated_files(tmp_path) == expected_output_files(
        "m_キャンペーン.csv",
        "m_キャンペーン_diff.csv",
        compress=True,
    )
    assert f"{TODAY:%Y%m%d}_m_キャンペーン.csv.gz" in completed.stdout
    assert f"{TOMORROW:%Y%m%d}_m_キャンペーン_diff.csv.gz" in completed.stdout

    _, rows = read_csv(tmp_path, "m_キャンペーン.csv.gz")
    _, diff_rows = read_csv(tmp_path, "m_キャンペーン_diff.csv.gz")

    assert rows == []
    assert diff_rows == []


def test_null_progress_reporter_emits_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    """非TTY用の無効化レポーターは標準出力へ何も出さない。"""
    reporter = NullProgressReporter()

    reporter.start()
    reporter.advance(1)
    reporter.finish()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_tqdm_progress_reporter_leaves_completed_bar(monkeypatch: pytest.MonkeyPatch) -> None:
    """TTY向けバーは完了後も100%のまま残す設定で初期化する。"""
    captured_kwargs: dict[str, object] = {}

    class DummyBar:
        def update(self, delta: int) -> None:
            return None

        def close(self) -> None:
            return None

    def fake_tqdm(*args: object, **kwargs: object) -> DummyBar:
        captured_kwargs.update(kwargs)
        return DummyBar()

    monkeypatch.setattr(progress_module, "tqdm", fake_tqdm)

    reporter = TqdmProgressReporter(Path("sample.csv"), total_rows=3)
    reporter.start()

    assert captured_kwargs["leave"] is True


def test_same_seed_is_deterministic(tmp_path: Path) -> None:
    first_tmp = tmp_path / "first"
    second_tmp = tmp_path / "second"
    first_tmp.mkdir()
    second_tmp.mkdir()

    run_script(str(first_tmp), "--seed", "7")
    run_script(str(second_tmp), "--seed", "7")

    for name in DEFAULT_OUTPUT_FILES:
        assert (first_tmp / name).read_text(encoding="utf-8-sig") == (second_tmp / name).read_text(
            encoding="utf-8-sig"
        )


def test_jobs_parallel_output_generates_expected_files(tmp_path: Path) -> None:
    """jobs を増やしても複数 target の並列生成が正常終了する。"""
    parallel_dir = tmp_path / "parallel"
    parallel_dir.mkdir()

    targets = "campaign,agency,compass,product"
    completed = run_script(str(parallel_dir), "--targets", targets, "--seed", "7", "--jobs", "2", timeout=120)

    assert generated_files(parallel_dir) == expected_output_files(
        "b_hjn_com_営業決裁.csv",
        "b_hjn_com_営業決裁_diff.csv",
        "m_キャンペーン.csv",
        "m_キャンペーン_diff.csv",
        "m_取次店_all.csv",
        "m_取次店_all_diff.csv",
        "m_商品_all.csv",
        "m_商品_all_diff.csv",
    )
    assert "0%" not in completed.stdout
    assert "100%" not in completed.stdout


def test_output_path_adds_gzip_suffix_when_compressing(tmp_path: Path) -> None:
    """圧縮時は実ファイル名が `.csv.gz` になる。"""
    actual = build_output_path(tmp_path, "sample.csv", True)
    assert actual.name == "sample.csv.gz"


def test_dated_output_name_uses_next_day_for_diff_files() -> None:
    """差分CSVだけ基準日の翌日をファイル名プレフィックスに使う。"""
    base_date = date(2026, 5, 1)

    assert dated_output_name("m_キャンペーン.csv", base_date) == "20260501_m_キャンペーン.csv"
    assert dated_output_name("m_キャンペーン_diff.csv", base_date) == "20260502_m_キャンペーン_diff.csv"
    assert dated_output_name("m_商品_all_diff.csv", base_date) == "20260502_m_商品_all_diff.csv"


def test_dated_output_path_keeps_csv_gzip_suffix(tmp_path: Path) -> None:
    """日付付き出力パスでもgzip時は `.csv.gz` を末尾に付ける。"""
    actual = build_dated_output_path(tmp_path, "m_キャンペーン_diff.csv", True, date(2026, 5, 1))

    assert actual.name == "20260502_m_キャンペーン_diff.csv.gz"


def test_write_target_csv_can_write_gzip(tmp_path: Path) -> None:
    """圧縮書き込みでもCSVとして読み戻せる。"""
    write_target_csv(tmp_path, "sample.csv", ["列1", "列2"], [["a", "b"]], compress=True)

    path = tmp_path / "sample.csv.gz"
    assert path.exists()

    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))

    assert rows == [["列1", "列2"], ["a", "b"]]


def test_write_target_csv_always_quotes_all_string_values(tmp_path: Path) -> None:
    """ヘッダーと空文字を含む全文字列が常にダブルクォートされる。"""
    write_target_csv(tmp_path, "sample.csv", ["列1", "列2"], [["", "値"]], compress=False)

    assert (tmp_path / "sample.csv").read_text(encoding="utf-8-sig").splitlines() == ['"列1","列2"', '"","値"']


def test_csv_headers_start_with_business_keys(generated_default_dir: Path) -> None:
    campaign_header, _ = read_csv(generated_default_dir, "m_キャンペーン.csv")
    campaign_diff_header, _ = read_csv(generated_default_dir, "m_キャンペーン_diff.csv")
    agency_header, _ = read_csv(generated_default_dir, "m_取次店_all.csv")
    diff_header, _ = read_csv(generated_default_dir, "m_取次店_all_diff.csv")
    compass_all_header, _ = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    compass_diff_header, _ = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")
    product_header, _ = read_csv(generated_default_dir, "m_商品_all.csv")
    product_diff_header, _ = read_csv(generated_default_dir, "m_商品_all_diff.csv")
    bfs_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    bfs_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    bfs_device_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    bfs_device_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    bfs_accessories_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    bfs_accessories_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")
    corp_all_1_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_1.csv")
    corp_all_2_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_2.csv")
    corp_diff_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_diff.csv")

    assert campaign_header[0] == "キャンペーンid"
    assert campaign_diff_header[0] == "キャンペーンid"
    assert agency_header[0] == "取次店コード"
    assert diff_header[0] == "取次店コード"
    assert compass_all_header[0] == "ID"
    assert compass_diff_header[0] == "ID"
    assert product_header[0] == "商品コード"
    assert product_diff_header[0] == "商品コード"
    assert bfs_all_header[0] == "エントリ番号"
    assert bfs_diff_header[0] == "エントリ番号"
    assert bfs_device_all_header[0] == "エントリ番号"
    assert bfs_device_diff_header[0] == "エントリ番号"
    assert bfs_accessories_all_header[0] == "エントリ番号"
    assert bfs_accessories_diff_header[0] == "エントリ番号"
    assert corp_all_1_header[0] == "統一企業コード"
    assert corp_all_2_header[0] == "統一企業コード"
    assert corp_diff_header[0] == "統一企業コード"
    for header in (
        campaign_header,
        campaign_diff_header,
        agency_header,
        compass_all_header,
        compass_diff_header,
        product_header,
        product_diff_header,
        bfs_all_header,
        bfs_diff_header,
        bfs_device_all_header,
        bfs_device_diff_header,
        bfs_accessories_all_header,
        bfs_accessories_diff_header,
        corp_all_1_header,
        corp_all_2_header,
        corp_diff_header,
    ):
        if header == compass_all_header or header == compass_diff_header:
            assert "ID" in header
        else:
            assert "id" not in header


def test_diff_type_header_is_not_output_to_any_csv(generated_default_dir: Path) -> None:
    """すべてのCSVに diff_type ヘッダーを出力しない。"""
    output_files = (
        "m_取次店_all.csv",
        "m_取次店_all_diff.csv",
        "b_hjn_com_営業決裁.csv",
        "b_hjn_com_営業決裁_diff.csv",
        "m_hjn_smt_統一企業情報_1.csv",
        "m_hjn_smt_統一企業情報_2.csv",
        "m_hjn_smt_統一企業情報_diff.csv",
        "b_hjn_bfs_モバイル_エントリ情報.csv",
        "b_hjn_bfs_モバイル_エントリ情報_diff.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_端末.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv",
        "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv",
        "m_キャンペーン.csv",
        "m_キャンペーン_diff.csv",
        "m_商品_all.csv",
        "m_商品_all_diff.csv",
    )

    for file_name in output_files:
        header, _ = read_csv(generated_default_dir, file_name)
        assert "diff_type" not in header


def test_csv_headers_use_japanese_labels_from_format_spec(generated_default_dir: Path) -> None:
    campaign_header, _ = read_csv(generated_default_dir, "m_キャンペーン.csv")
    campaign_diff_header, _ = read_csv(generated_default_dir, "m_キャンペーン_diff.csv")
    agency_header, _ = read_csv(generated_default_dir, "m_取次店_all.csv")
    diff_header, _ = read_csv(generated_default_dir, "m_取次店_all_diff.csv")
    compass_all_header, _ = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    compass_diff_header, _ = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")
    product_header, _ = read_csv(generated_default_dir, "m_商品_all.csv")
    product_diff_header, _ = read_csv(generated_default_dir, "m_商品_all_diff.csv")
    bfs_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    bfs_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    bfs_device_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    bfs_device_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    bfs_accessories_all_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    bfs_accessories_diff_header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")
    corp_all_1_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_1.csv")
    corp_all_2_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_2.csv")
    corp_diff_header, _ = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_diff.csv")

    expected_headers = {
        "campaign": ["キャンペーンid", "キャンペーン名称", "説明", "有効開始日"],
        "agency": ["取次店コード", "有効開始日", "有効終了日", "共通店舗コード"],
        "compass": ["ID", "決裁番号", "決裁件名", "ステータス"],
        "product": ["商品コード", "有効開始日", "有効開始時間", "有効終了日"],
        "bfs": ["エントリ番号", "件名", "作成区分", "オーダ種別"],
        "bfs_device": ["エントリ番号", "サマリ番号", "回線数", "レンタルセット端末"],
        "bfs_accessories": ["エントリ番号", "サマリ番号", "シリアル付付属品", "商品コード"],
        "corp": ["統一企業コード", "法人管理番号", "dunsnumber", "法人格コード"],
    }

    assert campaign_header[:4] == expected_headers["campaign"]
    assert campaign_diff_header[:4] == expected_headers["campaign"]
    assert campaign_header == campaign_diff_header
    assert agency_header[:4] == expected_headers["agency"]
    assert compass_all_header[:4] == expected_headers["compass"]
    assert compass_all_header == compass_diff_header
    assert product_header[:4] == expected_headers["product"]
    assert product_diff_header[:4] == expected_headers["product"]
    assert product_header == product_diff_header
    assert agency_header == diff_header
    assert bfs_all_header[:4] == expected_headers["bfs"]
    assert bfs_all_header == bfs_diff_header
    assert bfs_device_all_header[:4] == expected_headers["bfs_device"]
    assert bfs_device_all_header == bfs_device_diff_header
    assert bfs_accessories_all_header[:4] == expected_headers["bfs_accessories"]
    assert bfs_accessories_all_header == bfs_accessories_diff_header
    assert corp_all_1_header[:4] == expected_headers["corp"]
    assert corp_all_1_header == corp_all_2_header
    assert corp_all_1_header == corp_diff_header


def test_product_headers_reflect_updated_format_labels(generated_default_dir: Path) -> None:
    """商品CSVヘッダーは更新後フォーマットの表示名を反映する。"""
    header, _ = read_csv(generated_default_dir, "m_商品_all.csv")

    assert "商品細分類ID" in header
    assert "商品小分類ID" in header
    assert "商品中分類ID" in header
    assert "商品大分類ID" in header
    assert "メーカーID" in header
    assert "ブランドID" in header
    assert "MVNO識別ID" in header
    assert "個装箱サイズ_縦(mm)" in header
    assert "梱包財_紙重量(g)" in header
    assert "MRP管理者コード" in header
    assert "MODEL_ID" in header
    assert "ISMIタイプ名称" in header


def test_product_decimal_values_fit_updated_format_lengths(generated_default_dir: Path) -> None:
    """商品CSVの更新対象DECIMAL列は数値で新しい整数桁数に収まる。"""
    header, all_rows = read_csv(generated_default_dir, "m_商品_all.csv")
    _, diff_rows = read_csv(generated_default_dir, "m_商品_all_diff.csv")
    decimal_columns = {
        "MVNO識別ID": 3,
        "チャージ額": 6,
        "ユニバーサル使用料": 4,
        "利用有効期間": 5,
        "標準入数": 10,
        "出荷時入数": 6,
        "個装箱サイズ_縦(mm)": 4,
        "個装箱サイズ_横(mm)": 4,
        "個装箱サイズ_高さ(mm)": 4,
        "梱包財_紙重量(g)": 7,
        "梱包財_プラ重量(g)": 7,
        "商品重量(g)": 7,
        "パレット積み付け数": 8,
        "梱包仕様等": 4,
    }

    for row in all_rows[:20] + diff_rows[:20]:
        for label, max_integer_digits in decimal_columns.items():
            value = row[header.index(label)]
            integer_part = value.split(".", maxsplit=1)[0]
            assert integer_part.isdecimal()
            assert len(integer_part) <= max_integer_digits


def test_load_specs_can_read_a_directory_of_markdown_files(tmp_path: Path) -> None:
    """仕様読み込みは Markdown ディレクトリを直接受け取れる。"""
    format_dir = tmp_path / "format"
    format_dir.mkdir()
    (format_dir / "sample.md").write_text(
        "\n".join(
            [
                "# (Mars)キャンペーン",
                "",
                "## カラム定義",
                "",
                "| 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |",
                "| --- | --- | --- | --- | --- | --- |",
                "| キャンペーンid | `campaign_id` | VARCHAR | 40 | － | - |",
            ]
        ),
        encoding="utf-8",
    )

    specs = load_specs(format_dir)

    assert list(specs) == ["campaign"]
    assert [column.name for column in specs["campaign"]] == ["campaign_id"]
    assert [column.header_label for column in specs["campaign"]] == ["キャンペーンid"]


def test_parse_section_columns_supports_multiple_markdown_row_formats() -> None:
    """列定義の行形式差異を吸収して同じ ColumnSpec に変換する。"""
    columns = parse_section_columns(
        [
            "| 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |",
            "| キャンペーンid | `campaign_id` | VARCHAR | 40 | － | - |",
            "| No | 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 | 備考 |",
            "| 1 | 取次店コード | `agent_code` | VARCHAR | 10 | － | - | - |",
            "| No | 項目名 | カラム名 | 型 | 桁 | 説明 |",
            "| 1 | 決裁番号 | `approval_number` | VARCHAR | 20 | - |",
        ]
    )

    assert [column.header_label for column in columns] == ["キャンペーンid", "取次店コード", "決裁番号"]
    assert [column.name for column in columns] == ["campaign_id", "agent_code", "approval_number"]
    assert [column.max_length for column in columns] == [40, 10, 20]
    assert [column.required for column in columns] == [False, False, False]


def test_parse_section_columns_detects_required_marker() -> None:
    """列定義の必須マークを ColumnSpec に保持する。"""
    columns = parse_section_columns(
        [
            "| 項目名 | カラム名 | 型 | 桁 | 必須 | 説明 |",
            "| エントリ番号 | `entry_number` | VARCHAR | 18 | ⚪︎ | - |",
            "| 回線数 | `number_of_lines` | DECIMAL | 10 | － | - |",
        ]
    )

    assert [column.required for column in columns] == [True, False]


def test_load_specs_includes_bfs_entry_information() -> None:
    """実フォーマットのBFS定義が読み込める。"""
    specs = load_specs(ROOT / "docs/format")

    assert "bfs" in specs
    assert "bfs_device" in specs
    assert "bfs_accessories" in specs
    assert len(specs["bfs"]) == 216
    assert len(specs["bfs_device"]) == 504
    assert len(specs["bfs_accessories"]) == 22
    assert [column.name for column in specs["bfs"][:4]] == ["entry_number", "subject", "creation_category", "order_type"]
    assert [column.header_label for column in specs["bfs"][:4]] == ["エントリ番号", "件名", "作成区分", "オーダ種別"]
    assert [column.name for column in specs["bfs_device"][:4]] == [
        "entry_number",
        "summary_number",
        "number_of_lines",
        "rental_set_device",
    ]
    assert [column.header_label for column in specs["bfs_device"][:4]] == [
        "エントリ番号",
        "サマリ番号",
        "回線数",
        "レンタルセット端末",
    ]
    assert [column.name for column in specs["bfs_accessories"][:4]] == [
        "entry_number",
        "summary_number",
        "serial_number_accessories",
        "product_code",
    ]
    assert [column.header_label for column in specs["bfs_accessories"][:4]] == [
        "エントリ番号",
        "サマリ番号",
        "シリアル付付属品",
        "商品コード",
    ]


def test_load_specs_includes_corp_unified_company_information() -> None:
    """実フォーマットの統一企業情報定義が corp キーで読み込める。"""
    specs = load_specs(ROOT / "docs/format")

    assert "corp" in specs
    assert len(specs["corp"]) == 63
    assert [column.name for column in specs["corp"][:4]] == [
        "統一企業コード",
        "法人管理番号",
        "dunsnumber",
        "法人格コード",
    ]
    assert [column.header_label for column in specs["corp"][:4]] == [
        "統一企業コード",
        "法人管理番号",
        "dunsnumber",
        "法人格コード",
    ]


def test_csv_rows_start_with_primary_business_keys(generated_seed7_dir: Path) -> None:
    _, campaign_rows = read_csv(generated_seed7_dir, "m_キャンペーン.csv")
    _, campaign_diff_rows = read_csv(generated_seed7_dir, "m_キャンペーン_diff.csv")
    _, agency_rows = read_csv(generated_seed7_dir, "m_取次店_all.csv")
    _, compass_all_rows = read_csv(generated_seed7_dir, "b_hjn_com_営業決裁.csv")
    _, compass_diff_rows = read_csv(generated_seed7_dir, "b_hjn_com_営業決裁_diff.csv")
    _, product_rows = read_csv(generated_seed7_dir, "m_商品_all.csv")
    _, product_diff_rows = read_csv(generated_seed7_dir, "m_商品_all_diff.csv")
    _, bfs_all_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, bfs_diff_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    _, bfs_device_all_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, bfs_device_diff_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    _, bfs_accessories_all_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, bfs_accessories_diff_rows = read_csv(generated_seed7_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")
    _, corp_all_1_rows = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_1.csv")
    _, corp_all_2_rows = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_2.csv")
    _, corp_diff_rows = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_diff.csv")

    expected_prefixes = {
        "campaign": "CP",
        "agency": "AG",
        "product": "PRD",
        "compass_id": "CMP",
        "compass": "LS",
        "bfs_all": "EN",
        "bfs_diff": "EN",
        "bfs_device_all": "EN",
        "bfs_device_diff": "EN",
        "bfs_accessories_all": "EN",
        "bfs_accessories_diff": "EN",
        "corp_all_1": "",
        "corp_all_2": "",
        "corp_diff": "",
    }

    for row in campaign_rows[:2]:
        assert row[0].startswith(expected_prefixes["campaign"])
    for row in campaign_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["campaign"])
    for row in agency_rows[:2]:
        assert row[0].startswith(expected_prefixes["agency"])
    for row in product_rows[:2]:
        assert row[0].startswith(expected_prefixes["product"])
    for row in product_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["product"])
    for row in compass_all_rows[:2]:
        assert row[0].startswith(expected_prefixes["compass_id"])
        assert row[1].startswith(expected_prefixes["compass"])
    for row in compass_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["compass_id"])
        assert row[1].startswith(expected_prefixes["compass"])
    for row in bfs_all_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_all"])
    for row in bfs_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_diff"])
    for row in bfs_device_all_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_device_all"])
    for row in bfs_device_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_device_diff"])
    for row in bfs_accessories_all_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_accessories_all"])
    for row in bfs_accessories_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_accessories_diff"])
    for row in corp_all_1_rows[:2]:
        assert len(row[0]) > 0
    for row in corp_all_2_rows[:2]:
        assert len(row[0]) > 0
    for row in corp_diff_rows[:2]:
        assert len(row[0]) > 0


def test_bfs_summary_files_reference_generated_bfs_entries(tmp_path: Path) -> None:
    """BFSサービスサマリのキーが同一実行のBFSエントリと整合することを確認する。"""
    run_script(str(tmp_path), "--targets", "bfs", "--seed", "7")

    bfs_all_header, bfs_all_rows = read_csv(tmp_path, "b_hjn_bfs_モバイル_エントリ情報.csv")
    device_all_header, device_all_rows = read_csv(tmp_path, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    accessories_all_header, accessories_all_rows = read_csv(tmp_path, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")

    bfs_entry_numbers = {row[bfs_all_header.index("エントリ番号")] for row in bfs_all_rows}
    device_entry_index = device_all_header.index("エントリ番号")
    device_summary_index = device_all_header.index("サマリ番号")
    accessories_entry_index = accessories_all_header.index("エントリ番号")
    accessories_summary_index = accessories_all_header.index("サマリ番号")
    linked_summary_index = accessories_all_header.index("紐付けサマリ番号")

    for row in device_all_rows[:20]:
        assert row[device_entry_index] in bfs_entry_numbers
        assert row[device_summary_index].startswith("SM")

    for row in accessories_all_rows[:20]:
        assert row[accessories_entry_index] in bfs_entry_numbers
        assert row[accessories_summary_index].startswith("SM")
        assert row[linked_summary_index] == row[accessories_summary_index]


def test_bfs_device_headers_include_new_columns(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末ヘッダーの末尾に新規2項目を含める。"""
    header, _ = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")

    assert header[-2:] == ["現端末契約期間", "サマリ単位反映"]


def test_bfs_device_optional_new_columns_use_valid_values_when_populated(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の任意新規2項目は入力時に仕様内の値にする。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")

    current_device_contract_period_index = header.index("現端末契約期間")
    reflected_in_summary_unit_index = header.index("サマリ単位反映")

    current_device_contract_period_values = []
    reflected_in_summary_unit_values = []
    for row in all_rows[:20] + diff_rows[:20]:
        if row[current_device_contract_period_index] != "":
            current_device_contract_period_values.append(row[current_device_contract_period_index])
        if row[reflected_in_summary_unit_index] != "":
            reflected_in_summary_unit_values.append(row[reflected_in_summary_unit_index])

    assert current_device_contract_period_values
    assert reflected_in_summary_unit_values
    assert set(reflected_in_summary_unit_values).issubset({"0", "1"})


def test_bfs_device_contract_period_uses_two_digit_decimal_values(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の現端末契約期間は2桁以内の数値文字列で出力する。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    current_device_contract_period_index = header.index("現端末契約期間")

    for row in all_rows[:20] + diff_rows[:20]:
        value = row[current_device_contract_period_index]
        if value == "":
            continue
        assert value.isdecimal()
        assert len(value) <= 2


def test_bfs_device_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_labels = [column.header_label for column in specs["bfs_device"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")

    assert required_labels == ["エントリ番号", "サマリ番号", "商品コード", "メーカ", "移動機分類", "機種名", "プラン"]
    required_indexes = [header.index(label) for label in required_labels]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_device_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")

    optional_indexes = [header.index(column.header_label) for column in specs["bfs_device"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_device_repeating_pairs_are_contiguous_and_complete(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の連番ペア列は途中飛びや片側入力を作らない。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    paired_groups = [
        [(f"option_category_{index}", f"option_service_{index}") for index in range(1, 8)]
        + [("option_category_8", "optional_service_8")]
        + [(f"optional_category_{index}", f"optional_service_{index}") for index in range(9, 11)],
        [(f"rntopt_category_{index}", f"rntopt_plan_{index}") for index in range(1, 11)],
        [(f"rntoptatt_category_{index}", f"rntoptatt_plan_{index}") for index in range(1, 9)]
        + [("rntopta_tt_category_9", "rntoptatt_plan_9")]
        + [("rntoptatt_category_10", "rntoptatt_plan_10")],
        [(f"relative_pd_category_{index}", f"relative_pd_name_{index}") for index in range(1, 11)],
        [(f"relative_other_pd_category_{index}", f"relative_other_pd_name_{index}") for index in range(1, 6)],
    ]

    for row in all_rows[:50] + diff_rows[:50]:
        for group in paired_groups:
            seen_blank = False
            for left_name, right_name in group:
                left = row[bfs_device_column_index(header, left_name)]
                right = row[bfs_device_column_index(header, right_name)]
                assert (left == "") == (right == "")
                if left == "":
                    seen_blank = True
                else:
                    assert not seen_blank


def test_bfs_device_values_follow_updated_spec_examples(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の主要列は短縮コードではなく仕様例に沿う値を使う。"""
    header, rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    checks = {
        "rental_set_device": {"有", "無"},
        "mnp": {"有", "無"},
        "plan": {"基本プラン（音声）", "基本プラン（データ）", "通話定額基本料（ケータイ）", "ホワイト特別相対S", "ホワイト特別相対L"},
        "call_discount_w_white": {"通話料割引Wホワイト", "通話料割引Wホワイトライト"},
        "breaking_contract_gold_annual_contract": {"相対2年契約10000", "相対5年契約15000"},
        "s_basic_pack": {"ウェブ使用料（無料）", "ウェブ使用料（i）", "ウェブ使用料なし", "ウェブ使用料（スマ放題/通話基本プラン）"},
        "data_communication_basic_fee_4g": {"4Gデータ通信基本料(i)", "4Gデータ通信基本料(F)", "4Gデータ通信基本料(S)"},
        "basic_fee_5g": {"5Gサービス利用料", "5G基本料（内包用）"},
        "packet_discount": {"データプラン7GB（法人）", "パケットし放題フラット"},
        "option_pack": {"セレクトパック", "iPhone法人基本パック", "スマートフォン法人基本パック"},
        "anshin_guarantee_pack": {"(端末)安心保証パックB", "あんしん保証パックプラス"},
    }

    for column_name, expected_values in checks.items():
        index = bfs_device_column_index(header, column_name)
        values = {row[index] for row in rows if row[index] != ""}
        assert values
        assert values.issubset(expected_values)


def test_bfs_entry_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSエントリ情報の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_labels = [column.header_label for column in specs["bfs"] if column.required]
    all_header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")

    assert required_labels == [
        "エントリ番号",
        "作成区分",
        "オーダ種別",
        "申込書連携",
        "特約分離出力有無",
        "通知書対象",
        "開通済有無",
        "取次店コード",
        "所属代理店",
        "キャリア種別",
        "事業者区分",
        "申込書番号",
        "契約種別",
        "エントリ作成者id",
        "エントリ作成日時",
        "エントリ更新担当者id",
        "エントリ更新日時",
    ]
    required_indexes = [all_header.index(label) for label in required_labels]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_entry_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSエントリ情報の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")

    optional_indexes = [header.index(column.header_label) for column in specs["bfs"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_entry_values_follow_updated_spec_examples(generated_default_dir: Path) -> None:
    """BFSエントリ情報の主要列は更新後の仕様例に沿う値を使う。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    rows = all_rows + diff_rows
    checks = {
        "作成区分": {"エントリ作成", "試算作成", "申込書作成"},
        "オーダ種別": {"追加新規"},
        "申込書連携": {"有", "無"},
        "特約分離出力有無": {"有", "無"},
        "通知書対象": {"有", "無"},
        "開通済有無": {"有", "無"},
        "契約種別": {"相対", "約款"},
        "付属品購入": {"有", "無"},
    }

    for label, expected_values in checks.items():
        index = header.index(label)
        values = {row[index] for row in rows if row[index] != ""}
        assert values
        assert values.issubset(expected_values)


def test_bfs_entry_dates_follow_updated_formats(generated_default_dir: Path) -> None:
    """BFSエントリ情報の日付・日時列は更新後の仕様形式で出力する。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    rows = all_rows[:20] + diff_rows[:20]

    activation_date_index = header.index("開通日")
    entry_creation_index = header.index("エントリ作成日時")
    entry_update_index = header.index("エントリ更新日時")
    activation_date_pattern = re.compile(r"^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$")
    date_time_pattern = re.compile(r"^\d{4}/\d{2}/\d{2} \d{1,2}:\d{2}:\d{2}$")

    for row in rows:
        if row[activation_date_index] != "":
            assert activation_date_pattern.match(row[activation_date_index])
        assert date_time_pattern.match(row[entry_creation_index])
        assert date_time_pattern.match(row[entry_update_index])


def test_bfs_entry_rental_periods_use_month_labels(generated_default_dir: Path) -> None:
    """BFSエントリ情報の期間列は仕様説明どおり月表記で出力する。"""
    all_header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")

    period_after_renewal_index = all_header.index("自動更新後の期間")
    initial_rental_period_index = all_header.index("初期レンタル期間")

    for row in all_rows[:20] + diff_rows[:20]:
        for index in (period_after_renewal_index, initial_rental_period_index):
            value = row[index]
            if value == "":
                continue
            assert re.match(r"^\d+ヶ月$", value)


def test_bfs_accessories_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_labels = [column.header_label for column in specs["bfs_accessories"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")

    assert required_labels == [
        "エントリ番号",
        "サマリ番号",
        "シリアル付付属品",
        "商品コード",
        "メーカ",
        "商品名",
        "台数1",
        "付属品標準価格",
    ]
    required_indexes = [header.index(label) for label in required_labels]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_accessories_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")

    optional_indexes = [header.index(column.header_label) for column in specs["bfs_accessories"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_accessories_serial_number_accessories_is_fixed_text(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品のシリアル付付属品は仕様説明どおり固定文言で出力する。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")
    serial_index = header.index("シリアル付付属品")

    assert {row[serial_index] for row in all_rows + diff_rows} == {"シリアルなし"}


def assert_diff_keys_partition_initial_and_existing(
    all_rows: list[list[str]],
    diff_rows: list[list[str]],
    key_index: int,
    *,
    expect_existing: bool,
) -> None:
    """差分CSVの業務キーが新規追加分と既存更新分に分かれることを確認する。"""
    all_keys = {row[key_index] for row in all_rows}

    insert_keys = {row[key_index] for row in diff_rows if row[key_index] not in all_keys}
    existing_keys = {row[key_index] for row in diff_rows if row[key_index] in all_keys}

    assert insert_keys
    assert insert_keys.isdisjoint(all_keys)
    if expect_existing:
        assert existing_keys
        assert existing_keys.issubset(all_keys)
    else:
        assert not existing_keys


def assert_full_refresh_diff_replaces_rows(
    all_header: list[str],
    all_rows: list[list[str]],
    diff_header: list[str],
    diff_rows: list[list[str]],
    key_label: str,
) -> None:
    """全量更新diffが削除・追加・更新後の状態を表すことを検証する。"""
    key_index = all_header.index(key_label)
    all_by_key = {row[key_index]: row for row in all_rows}
    diff_by_key = {row[key_index]: row for row in diff_rows}
    deleted_keys = set(all_by_key) - set(diff_by_key)
    added_keys = set(diff_by_key) - set(all_by_key)
    updated_keys = {
        key
        for key in set(all_by_key) & set(diff_by_key)
        if all_by_key[key] != diff_by_key[key]
    }

    assert all_header == diff_header
    assert "diff_type" not in diff_header
    assert len(diff_rows) == len(all_rows)
    assert deleted_keys
    assert added_keys
    assert updated_keys


def test_agency_diff_keys_include_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """取次店差分の業務キーは新規追加分と既存更新分を含む。"""
    header, all_rows = read_csv(generated_default_dir, "m_取次店_all.csv")
    _, diff_rows = read_csv(generated_default_dir, "m_取次店_all_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        all_rows,
        diff_rows,
        header.index("取次店コード"),
        expect_existing=True,
    )


def test_compass_diff_keys_include_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """COMPASS差分の業務キーは新規追加分と既存更新分を含む。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")

    assert_diff_keys_partition_initial_and_existing(all_rows, diff_rows, header.index("決裁番号"), expect_existing=True)


def test_compass_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_labels = [column.header_label for column in specs["compass"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")

    assert required_labels[:6] == ["ID", "決裁番号", "決裁件名", "ステータス", "申請日時", "決裁種別"]
    required_indexes = [header.index(label) for label in required_labels]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_compass_optional_columns_include_blanks(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の任意列には空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")

    optional_indexes = [header.index(column.header_label) for column in specs["compass"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]

    assert "" in values


def test_compass_boolean_columns_use_true_false(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の真偽値列はTRUE/FALSEで出力する。"""
    boolean_labels = [
        "モバイル",
        "音声",
        "音声(おとく光電話)",
        "ID(データ)",
        "IS(NI・物販)",
        "PHS",
        "包括決裁",
        "グループ包括決裁",
        "他案件で利用",
        "代理店情報手入力フラグ",
        "フローから子決裁作成フラグ",
        "非公開フラグ",
        "有効",
        "削除",
        "SUMMITデータ移行フラグ",
        "与信審査依頼名（COMPASS）有無判定",
    ]
    header, all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")

    for label in boolean_labels:
        index = header.index(label)
        values = {row[index] for row in all_rows + diff_rows if row[index] != ""}
        assert values
        assert values.issubset({"TRUE", "FALSE"})


def test_compass_yes_no_columns_use_japanese_values(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の有無列は有/無または空欄で出力する。"""
    yes_no_labels = [
        "与信アラート",
        "与信審査実施有無",
        "法務事前審査実施有無",
        "再決裁・起案フラグ",
        "事前相談有無",
        "開通工事費無料",
        "減免有無",
        "自動更新有無",
        "試算シート有無",
    ]
    header, all_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_com_営業決裁_diff.csv")

    for label in yes_no_labels:
        index = header.index(label)
        values = {row[index] for row in all_rows + diff_rows}
        assert values <= {"", "有", "無"}


def test_corp_diff_keys_include_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """統一企業情報差分の業務キーは新規追加分と既存更新分を含む。"""
    header_1, all_rows_1 = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_1.csv")
    _, all_rows_2 = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_2.csv")
    _, diff_rows = read_csv(generated_default_dir, "m_hjn_smt_統一企業情報_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        all_rows_1 + all_rows_2,
        diff_rows,
        header_1.index("統一企業コード"),
        expect_existing=True,
    )


def test_bfs_diff_keys_include_expected_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """BFS差分3ファイルの業務キーは新規追加分と既存更新分に分かれる。"""
    bfs_header, bfs_all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報.csv")
    _, bfs_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_エントリ情報_diff.csv")
    device_header, device_all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末.csv")
    _, device_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv")
    accessories_header, accessories_all_rows = read_csv(
        generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv"
    )
    _, accessories_diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        bfs_all_rows,
        bfs_diff_rows,
        bfs_header.index("エントリ番号"),
        expect_existing=True,
    )
    assert_diff_keys_partition_initial_and_existing(
        device_all_rows,
        device_diff_rows,
        device_header.index("エントリ番号"),
        expect_existing=False,
    )
    assert_diff_keys_partition_initial_and_existing(
        accessories_all_rows,
        accessories_diff_rows,
        accessories_header.index("商品コード"),
        expect_existing=True,
    )


def test_bfs_accessories_diff_updates_existing_product_codes(generated_default_dir: Path) -> None:
    """BFS付属品差分の更新行は商品コードを維持しつつ主要列を変更する。"""
    header, all_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品.csv")
    _, diff_rows = read_csv(generated_default_dir, "b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv")

    product_code_index = header.index("商品コード")
    manufacturer_index = header.index("メーカ")
    product_name_index = header.index("商品名")
    quantity_1_index = header.index("台数1")
    price_index = header.index("付属品標準価格")

    all_by_product_code = {row[product_code_index]: row for row in all_rows}
    updated_rows = [row for row in diff_rows if row[product_code_index] in all_by_product_code]

    assert updated_rows
    for row in updated_rows:
        all_row = all_by_product_code[row[product_code_index]]
        changed_columns = (
            row[manufacturer_index] != all_row[manufacturer_index]
            or row[product_name_index] != all_row[product_name_index]
            or row[quantity_1_index] != all_row[quantity_1_index]
            or row[price_index] != all_row[price_index]
        )
        assert changed_columns


def test_campaign_diff_replaces_deleted_added_and_updated_rows(generated_default_dir: Path) -> None:
    """キャンペーンdiffは全量更新として削除・追加・更新後の状態を表す。"""
    all_header, all_rows = read_csv(generated_default_dir, "m_キャンペーン.csv")
    diff_header, diff_rows = read_csv(generated_default_dir, "m_キャンペーン_diff.csv")

    assert_full_refresh_diff_replaces_rows(all_header, all_rows, diff_header, diff_rows, "キャンペーンid")


def test_product_diff_replaces_deleted_added_and_updated_rows(generated_default_dir: Path) -> None:
    """商品diffは全量更新として削除・追加・更新後の状態を表す。"""
    all_header, all_rows = read_csv(generated_default_dir, "m_商品_all.csv")
    diff_header, diff_rows = read_csv(generated_default_dir, "m_商品_all_diff.csv")

    assert_full_refresh_diff_replaces_rows(all_header, all_rows, diff_header, diff_rows, "商品コード")


def test_agency_diff_existing_keys_are_subset_of_agency_all(generated_agency_seed11_dir: Path) -> None:
    """取次店差分は既存キー更新分と未存在キー追加分を生成する。"""
    agency_header, agency_rows = read_csv(generated_agency_seed11_dir, "m_取次店_all.csv")
    diff_header, diff_rows = read_csv(generated_agency_seed11_dir, "m_取次店_all_diff.csv")
    assert agency_header == diff_header

    assert len(diff_rows) == 53
    code_index = agency_header.index("取次店コード")
    agency_codes = {row[code_index] for row in agency_rows}
    diff_codes = [row[code_index] for row in diff_rows]
    existing_diff_codes = {row[code_index] for row in diff_rows if row[code_index] in agency_codes}
    insert_codes = {row[code_index] for row in diff_rows if row[code_index] not in agency_codes}

    assert len(diff_codes) == len(set(diff_codes))
    assert existing_diff_codes.issubset(agency_codes)
    assert insert_codes.isdisjoint(agency_codes)


def test_compass_diff_updates_subset_of_compass_all(generated_compass_seed11_dir: Path) -> None:
    """営業決裁差分は既存キー更新分と未存在キー追加分を生成する。"""
    all_header, all_rows = read_csv(generated_compass_seed11_dir, "b_hjn_com_営業決裁.csv")
    diff_header, diff_rows = read_csv(generated_compass_seed11_dir, "b_hjn_com_営業決裁_diff.csv")
    assert all_header == diff_header

    approval_number_index = all_header.index("決裁番号")
    approval_subject_index = all_header.index("決裁件名")
    application_datetime_index = all_header.index("申請日時")
    approval_datetime_index = all_header.index("承認日時")
    sales_yen_index = all_header.index("売上（円）")
    notes_index = all_header.index("備考")
    changes_index = all_header.index("追加・変更内容")

    all_by_approval_number = {row[approval_number_index]: row for row in all_rows}
    diff_approval_numbers = [row[approval_number_index] for row in diff_rows]
    existing_diff_rows = [row for row in diff_rows if row[approval_number_index] in all_by_approval_number]
    insert_approval_numbers = {
        row[approval_number_index] for row in diff_rows if row[approval_number_index] not in all_by_approval_number
    }
    existing_diff_numbers = [row[approval_number_index] for row in existing_diff_rows]

    assert len(diff_rows) == 20
    assert len(diff_approval_numbers) == len(set(diff_approval_numbers))
    assert set(existing_diff_numbers).issubset(all_by_approval_number)
    assert insert_approval_numbers.isdisjoint(all_by_approval_number)

    for diff_row in existing_diff_rows:
        all_row = all_by_approval_number[diff_row[approval_number_index]]
        assert diff_row[approval_subject_index] != all_row[approval_subject_index]
        assert diff_row[application_datetime_index] != all_row[application_datetime_index]
        assert diff_row[approval_datetime_index] != all_row[approval_datetime_index]
        assert diff_row[sales_yen_index] != all_row[sales_yen_index]
        assert diff_row[notes_index] != all_row[notes_index]
        assert diff_row[changes_index] != all_row[changes_index]


def test_default_run_fills_every_cell_in_all_csvs(generated_seed7_dir: Path) -> None:
    """デフォルト実行では任意空欄許容CSV以外の全セルが非空欄になる。"""
    for name in generated_files(generated_seed7_dir):
        if (
            "エントリ情報" in name
            or "サービスサマリ_端末" in name
            or "サービスサマリ_付属品" in name
            or "営業決裁" in name
        ):
            continue
        header, rows = read_csv(generated_seed7_dir, name)
        assert_all_cells_filled(header, rows, name)


def test_corp_company_codes_are_unique_across_all_files(generated_seed7_dir: Path) -> None:
    """corp 全量CSVの統一企業コードは分割後も重複しない。"""
    header, rows_1 = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_1.csv")
    _, rows_2 = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_2.csv")
    code_index = header.index("統一企業コード")

    codes = [row[code_index] for row in [*rows_1, *rows_2]]
    assert len(codes) == len(set(codes))


def test_corp_all_files_split_rows_in_order(generated_seed7_dir: Path) -> None:
    """corp 全量CSVは前半と後半に分割され、統一企業コードの順序が連続する。"""
    header, rows_1 = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_1.csv")
    _, rows_2 = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_2.csv")
    code_index = header.index("統一企業コード")

    assert rows_1[-1][code_index] < rows_2[0][code_index]


def test_corp_split_counts_put_extra_row_in_first_file() -> None:
    """奇数件のcorp全量は先頭ファイルを1件多くして分割する。"""
    specs = load_specs(ROOT / "docs/format")
    counts = dict(DEFAULT_COUNTS)
    counts["corp_all"] = 5
    generator = CsvGenerator(specs=specs, seed=42, counts=counts)

    assert generator._corp_split_counts() == (3, 2)


def test_corp_parent_and_invalidity_fields_are_consistent(generated_seed7_dir: Path) -> None:
    """corp の親企業・無効理由関連の最低限の整合を確認する。"""
    header, rows = read_csv(generated_seed7_dir, "m_hjn_smt_統一企業情報_diff.csv")
    company_code_index = header.index("統一企業コード")
    parent_flag_index = header.index("親企業フラグ")
    parent_company_index = header.index("親企業番号")
    invalid_flag_index = header.index("有効無効フラグ")
    invalid_reason_index = header.index("無効理由")
    merged_company_index = header.index("合併企業番号")
    registered_at_index = header.index("登録日時")
    updated_at_index = header.index("更新日時")

    assert rows
    for row in rows[:30]:
        company_code = row[company_code_index]
        parent_flag = row[parent_flag_index]
        parent_company = row[parent_company_index]
        invalid_flag = row[invalid_flag_index]
        invalid_reason = row[invalid_reason_index]
        merged_company = row[merged_company_index]

        if parent_flag == "1":
            assert parent_company == company_code
        else:
            assert parent_company != ""

        if invalid_flag == "1":
            assert invalid_reason in {"10", "20", "30", "40"}
        else:
            assert invalid_reason == "0"

        if invalid_reason == "10":
            assert merged_company != "0"
        else:
            assert merged_company != ""

        assert row[registered_at_index] <= row[updated_at_index]


def test_corp_datetime_columns_use_millisecond_timestamp_format(generated_seed7_dir: Path) -> None:
    """corp の日時4項目は YYYY-MM-DD HH:MI:SS.000 形式で出力する。"""
    timestamp_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.000$")

    for file_name in (
        "m_hjn_smt_統一企業情報_1.csv",
        "m_hjn_smt_統一企業情報_2.csv",
        "m_hjn_smt_統一企業情報_diff.csv",
    ):
        header, rows = read_csv(generated_seed7_dir, file_name)
        datetime_indexes = [header.index(label) for label in ("登録日", "更新日", "登録日時", "更新日時")]

        for row in rows[:20]:
            for index in datetime_indexes:
                assert timestamp_pattern.match(row[index])


def test_campaign_old_flag_is_always_filled(tmp_path: Path) -> None:
    """キャンペーンの旧フラグは全行で非空欄にする。"""
    run_script(str(tmp_path), "--targets", "campaign", "--seed", "7")

    for file_name in ("m_キャンペーン.csv", "m_キャンペーン_diff.csv"):
        header, rows = read_csv(tmp_path, file_name)
        old_flag_index = header.index("旧フラグ")

        assert {row[old_flag_index] for row in rows}.issubset({"0", "1"})


def test_compass_status_is_fixed_to_approved_and_history_is_filled(generated_seed7_dir: Path) -> None:
    """営業決裁のステータス固定と承認履歴非空欄を確認する。"""
    for file_name in ("b_hjn_com_営業決裁.csv", "b_hjn_com_営業決裁_diff.csv"):
        header, rows = read_csv(generated_seed7_dir, file_name)
        status_index = header.index("ステータス")
        history_index = header.index("承認履歴")

        assert {row[status_index] for row in rows} == {"承認"}
        assert all(row[history_index] != "" for row in rows)
