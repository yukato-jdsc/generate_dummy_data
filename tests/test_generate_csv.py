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
from csv_generator.values import ValueFactory

SCRIPT = ROOT / "generate_csv.py"
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
BASE_OUTPUT_FILES = [
    "DLV_OAI_BFS_BFS_ENTRY_INFO.csv",
    "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv",
    "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv",
    "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv",
    "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv",
    "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv",
    "DLV_OAI_COM_EIG_KESSAI.csv",
    "DLV_OAI_COM_EIG_KESSAI_diff.csv",
    "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv",
    "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv",
    "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv",
    "DLV_OAI_MRS_CMPGN.csv",
    "DLV_OAI_MRS_CMPGN_diff.csv",
    "DLV_OAI_CST_ORDCSTM.csv",
    "DLV_OAI_CST_ORDCSTM_diff.csv",
    "DLV_OAI_MRS_ITEM.csv",
    "DLV_OAI_MRS_ITEM_diff.csv",
]
DEFAULT_OUTPUT_FILES = sorted(dated_output_name(name, TODAY) for name in BASE_OUTPUT_FILES)


def test_unit_tests_do_not_use_full_option() -> None:
    """単体テスト内で `--full` 実行を使わない方針を守る。"""
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = "--" + "full"
    assert f'"{forbidden}"' not in source


def test_company_code_uses_unified_ten_character_format() -> None:
    """統一企業コード系の共通生成は `UC` + 8桁の10文字形式に揃える。"""
    values = ValueFactory(seed=1)

    codes = [values.company_code(number) for number in (1, 999, 10_000_000, 100_000_000)]

    assert codes == ["UC00000001", "UC00000999", "UC10000000", "UC00000000"]
    assert all(len(code) == 10 for code in codes)


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
    return header.index(column_name)


def spec_column_name(spec_key: str, item_label: str) -> str:
    """仕様の項目名からCSVヘッダーに出力するカラム名を返す。"""
    specs = load_specs(ROOT / "docs/format")
    for column in specs[spec_key]:
        if column.header_label == item_label:
            return column.name
    raise AssertionError(f"{spec_key}: item label not found: {item_label}")


def header_index(header: list[str], spec_key: str, item_label: str) -> int:
    """項目名を使って、カラム名ヘッダーの列位置を返す。"""
    return header.index(spec_column_name(spec_key, item_label))


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

    _, campaign_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN.csv")
    _, agency_rows = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM.csv")
    _, agency_diff_rows = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM_diff.csv")
    _, compass_all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, compass_diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    _, product_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")
    _, product_diff_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM_diff.csv")
    _, bfs_all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, bfs_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    _, bfs_device_all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, bfs_device_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    _, bfs_accessories_all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, bfs_accessories_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")
    _, corp_all_1_rows = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    _, corp_all_2_rows = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    _, corp_diff_rows = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")
    _, campaign_diff_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN_diff.csv")

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
    output_path = generated_default_dir / dated_output_name("DLV_OAI_BFS_BFS_ENTRY_INFO.csv", TODAY)

    assert output_path.stat().st_size <= 2_900_000


def test_bfs_device_summary_uncompressed_size_is_reduced(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末CSVの圧縮前サイズを現行の1/2程度に抑える。"""
    output_path = generated_default_dir / dated_output_name("DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv", TODAY)

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
    assert generated_files(tmp_path) == expected_output_files("DLV_OAI_MRS_CMPGN.csv", "DLV_OAI_MRS_CMPGN_diff.csv")


def test_targets_product_only_generates_product_files(tmp_path: Path) -> None:
    """product 指定では商品全量と全量更新diffだけを生成する。"""
    run_script(str(tmp_path), "--targets", "product")
    assert generated_files(tmp_path) == expected_output_files("DLV_OAI_MRS_ITEM.csv", "DLV_OAI_MRS_ITEM_diff.csv")


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
    assert generated_files(tmp_path) == expected_output_files("DLV_OAI_COM_EIG_KESSAI.csv", "DLV_OAI_COM_EIG_KESSAI_diff.csv")


def test_targets_bfs_only_generates_two_files(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "bfs")
    assert generated_files(tmp_path) == expected_output_files(
        "DLV_OAI_BFS_BFS_ENTRY_INFO.csv",
        "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv",
        "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv",
        "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv",
        "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv",
        "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv",
    )


def test_targets_corp_only_generates_three_files(tmp_path: Path) -> None:
    """corp 指定では統一企業情報の3ファイルだけを生成する。"""
    run_script(str(tmp_path), "--targets", "corp")
    assert generated_files(tmp_path) == expected_output_files(
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv",
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

    assert "DLV_OAI_MRS_CMPGN.csv" in completed.stdout
    assert "DLV_OAI_MRS_CMPGN_diff.csv" in completed.stdout
    assert "DLV_OAI_CST_ORDCSTM.csv" in completed.stdout
    assert "DLV_OAI_CST_ORDCSTM_diff.csv" in completed.stdout
    assert "DLV_OAI_COM_EIG_KESSAI.csv" in completed.stdout
    assert "DLV_OAI_COM_EIG_KESSAI_diff.csv" in completed.stdout
    assert "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv" in completed.stdout
    assert "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv" in completed.stdout
    assert "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv" in completed.stdout
    assert "DLV_OAI_MRS_ITEM.csv" not in completed.stdout


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
        "DLV_OAI_MRS_CMPGN.csv",
        "DLV_OAI_MRS_CMPGN_diff.csv",
        compress=True,
    )
    assert f"{TODAY:%Y%m%d}_DLV_OAI_MRS_CMPGN.csv.gz" in completed.stdout
    assert f"{TOMORROW:%Y%m%d}_DLV_OAI_MRS_CMPGN_diff.csv.gz" in completed.stdout
    _, rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN.csv.gz")
    _, diff_rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN_diff.csv.gz")
    assert len(rows) == 50
    assert len(diff_rows) == 50


def test_headers_only_campaign_outputs_headers_without_rows(
    tmp_path: Path,
    generated_default_dir: Path,
) -> None:
    """headers-only指定時は対象CSVをヘッダー行だけで生成する。"""
    completed = run_script(str(tmp_path), "--targets", "campaign", "--headers-only")

    assert generated_files(tmp_path) == expected_output_files("DLV_OAI_MRS_CMPGN.csv", "DLV_OAI_MRS_CMPGN_diff.csv")
    assert "DLV_OAI_MRS_CMPGN.csv" in completed.stdout
    assert "DLV_OAI_MRS_CMPGN_diff.csv" in completed.stdout

    normal_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN.csv")
    normal_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN_diff.csv")
    header, rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN.csv")
    diff_header, diff_rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN_diff.csv")

    assert header == normal_header
    assert diff_header == normal_diff_header
    assert rows == []
    assert diff_rows == []


def test_headers_only_omits_diff_type_headers(tmp_path: Path) -> None:
    """headers-only指定でも差分更新CSVに diff_type ヘッダーを出力しない。"""
    run_script(str(tmp_path), "--targets", "agency", "--headers-only")

    header, rows = read_csv(tmp_path, "DLV_OAI_CST_ORDCSTM.csv")
    diff_header, diff_rows = read_csv(tmp_path, "DLV_OAI_CST_ORDCSTM_diff.csv")

    assert header[0] == "ordcstm_cd"
    assert diff_header[0] == "ordcstm_cd"
    assert "diff_type" not in header
    assert "diff_type" not in diff_header
    assert rows == []
    assert diff_rows == []


def test_headers_only_can_write_gzip_csv(tmp_path: Path) -> None:
    """headers-only指定はgzip出力でもヘッダー行だけを書き出す。"""
    completed = run_script(str(tmp_path), "--targets", "campaign", "--headers-only", "--gzip")

    assert generated_files(tmp_path) == expected_output_files(
        "DLV_OAI_MRS_CMPGN.csv",
        "DLV_OAI_MRS_CMPGN_diff.csv",
        compress=True,
    )
    assert f"{TODAY:%Y%m%d}_DLV_OAI_MRS_CMPGN.csv.gz" in completed.stdout
    assert f"{TOMORROW:%Y%m%d}_DLV_OAI_MRS_CMPGN_diff.csv.gz" in completed.stdout

    _, rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN.csv.gz")
    _, diff_rows = read_csv(tmp_path, "DLV_OAI_MRS_CMPGN_diff.csv.gz")

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
        "DLV_OAI_COM_EIG_KESSAI.csv",
        "DLV_OAI_COM_EIG_KESSAI_diff.csv",
        "DLV_OAI_MRS_CMPGN.csv",
        "DLV_OAI_MRS_CMPGN_diff.csv",
        "DLV_OAI_CST_ORDCSTM.csv",
        "DLV_OAI_CST_ORDCSTM_diff.csv",
        "DLV_OAI_MRS_ITEM.csv",
        "DLV_OAI_MRS_ITEM_diff.csv",
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

    assert dated_output_name("DLV_OAI_MRS_CMPGN.csv", base_date) == "20260501_DLV_OAI_MRS_CMPGN.csv"
    assert dated_output_name("DLV_OAI_MRS_CMPGN_diff.csv", base_date) == "20260502_DLV_OAI_MRS_CMPGN_diff.csv"
    assert dated_output_name("DLV_OAI_MRS_ITEM_diff.csv", base_date) == "20260502_DLV_OAI_MRS_ITEM_diff.csv"


def test_dated_output_path_keeps_csv_gzip_suffix(tmp_path: Path) -> None:
    """日付付き出力パスでもgzip時は `.csv.gz` を末尾に付ける。"""
    actual = build_dated_output_path(tmp_path, "DLV_OAI_MRS_CMPGN_diff.csv", True, date(2026, 5, 1))

    assert actual.name == "20260502_DLV_OAI_MRS_CMPGN_diff.csv.gz"


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
    campaign_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN.csv")
    campaign_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN_diff.csv")
    agency_header, _ = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM.csv")
    diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM_diff.csv")
    compass_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    compass_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    product_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")
    product_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM_diff.csv")
    bfs_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    bfs_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    bfs_device_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    bfs_device_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    bfs_accessories_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    bfs_accessories_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")
    corp_all_1_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    corp_all_2_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    corp_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")

    assert campaign_header[0] == "campaign_id"
    assert campaign_diff_header[0] == "campaign_id"
    assert agency_header[0] == "ordcstm_cd"
    assert diff_header[0] == "ordcstm_cd"
    assert compass_all_header[0] == "id"
    assert compass_diff_header[0] == "id"
    assert product_header[0] == "itm_cd"
    assert product_diff_header[0] == "itm_cd"
    assert bfs_all_header[0] == "entry_no"
    assert bfs_diff_header[0] == "entry_no"
    assert bfs_device_all_header[0] == "entry_no"
    assert bfs_device_diff_header[0] == "entry_no"
    assert bfs_accessories_all_header[0] == "entry_no"
    assert bfs_accessories_diff_header[0] == "entry_no"
    assert corp_all_1_header[0] == "uniq_corp_cd"
    assert corp_all_2_header[0] == "uniq_corp_cd"
    assert corp_diff_header[0] == "uniq_corp_cd"


def test_diff_type_header_is_not_output_to_any_csv(generated_default_dir: Path) -> None:
    """すべてのCSVに diff_type ヘッダーを出力しない。"""
    output_files = (
        "DLV_OAI_CST_ORDCSTM.csv",
        "DLV_OAI_CST_ORDCSTM_diff.csv",
        "DLV_OAI_COM_EIG_KESSAI.csv",
        "DLV_OAI_COM_EIG_KESSAI_diff.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv",
        "DLV_OAI_BFS_BFS_ENTRY_INFO.csv",
        "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv",
        "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv",
        "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv",
        "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv",
        "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv",
        "DLV_OAI_MRS_CMPGN.csv",
        "DLV_OAI_MRS_CMPGN_diff.csv",
        "DLV_OAI_MRS_ITEM.csv",
        "DLV_OAI_MRS_ITEM_diff.csv",
    )

    for file_name in output_files:
        header, _ = read_csv(generated_default_dir, file_name)
        assert "diff_type" not in header


def test_csv_headers_use_column_names_from_format_spec(generated_default_dir: Path) -> None:
    """CSVヘッダーは項目名ではなく仕様のカラム名を使う。"""
    campaign_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN.csv")
    campaign_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN_diff.csv")
    agency_header, _ = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM.csv")
    diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM_diff.csv")
    compass_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    compass_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    product_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")
    product_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM_diff.csv")
    bfs_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    bfs_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    bfs_device_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    bfs_device_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    bfs_accessories_all_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    bfs_accessories_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")
    corp_all_1_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    corp_all_2_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    corp_diff_header, _ = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")

    expected_headers = {
        "campaign": ["campaign_id", "campaign_nm", "description", "effective_dt_from"],
        "agency": ["ordcstm_cd", "effective_dt_from", "effective_dt_to", "common_store_cd"],
        "compass": ["id", "name", "salesapprovaltitle", "status"],
        "product": ["itm_cd", "effective_dt_from", "effective_tm_from", "effective_dt_to"],
        "bfs": ["entry_no", "entry_nm", "entry_status_nm", "entry_type_nm"],
        "bfs_device": ["entry_no", "svcsm_id", "linenum", "rental_set_terminal_flg_nm"],
        "bfs_accessories": ["entry_no", "attach_sm_id", "serial_attach_flg_nm", "itm_cd"],
        "corp": ["uniq_corp_cd", "h_no", "teikoku_db_kigyo_bng", "hojinkaku_flg"],
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


def test_product_headers_reflect_updated_format_columns(generated_default_dir: Path) -> None:
    """商品CSVヘッダーは更新後フォーマットのカラム名を反映する。"""
    header, _ = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")

    assert "itm_lvl4_id" in header
    assert "itm_lvl3_id" in header
    assert "itm_lvl2_id" in header
    assert "itm_lvl1_id" in header
    assert "maker_id" in header
    assert "brand_id" in header
    assert "carrier_id" in header
    assert "size_d" in header
    assert "pack_mtr_paper_wgt" in header
    assert "mrpplanner_cd" in header
    assert "model_id" in header
    assert "imsi_typ_nm" in header
    assert "pickup_flg" in header


def test_product_decimal_values_fit_updated_format_lengths(generated_default_dir: Path) -> None:
    """商品CSVの更新対象DECIMAL列は数値で新しい整数桁数に収まる。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM_diff.csv")
    decimal_columns = {
        "carrier_id": 3,
        "charge_amt": 6,
        "universal_amt": 4,
        "effective_dt_use": 5,
        "standard_qty": 10,
        "ship_qty": 6,
        "size_d": 4,
        "size_w": 4,
        "size_h": 4,
        "pack_mtr_paper_wgt": 7,
        "pack_mtr_plstc_wgt": 7,
        "itm_wgt": 7,
        "palette_stack_num": 8,
        "pack_spcf": 4,
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
            "| 項目名 | カラム名 | 型 | 桁 | PK | 必須 | 説明 |",
            "| エントリ番号 | `entry_number` | VARCHAR | 18 | ○ | ⚪︎ | - |",
            "| 契約期間 | `contract_period` | DECIMAL | 18,0 | － | ◯ | - |",
            "| 回線数 | `number_of_lines` | DECIMAL | 10 | ○ | － | - |",
        ]
    )

    assert [column.required for column in columns] == [True, True, False]


def test_load_specs_includes_bfs_entry_information() -> None:
    """実フォーマットのBFS定義が読み込める。"""
    specs = load_specs(ROOT / "docs/format")

    assert "bfs" in specs
    assert "bfs_device" in specs
    assert "bfs_accessories" in specs
    assert len(specs["bfs"]) == 217
    assert len(specs["bfs_device"]) == 509
    assert len(specs["bfs_accessories"]) == 26
    assert [column.name for column in specs["bfs"][:4]] == [
        "entry_no",
        "entry_nm",
        "entry_status_nm",
        "entry_type_nm",
    ]
    assert [column.header_label for column in specs["bfs"][:4]] == ["エントリ番号", "件名", "作成区分", "オーダ種別"]
    assert [column.name for column in specs["bfs_device"][:4]] == [
        "entry_no",
        "svcsm_id",
        "linenum",
        "rental_set_terminal_flg_nm",
    ]
    assert [column.header_label for column in specs["bfs_device"][:4]] == [
        "エントリ番号",
        "サマリ番号",
        "回線数",
        "レンタルセット端末",
    ]
    assert [column.name for column in specs["bfs_accessories"][:4]] == [
        "entry_no",
        "attach_sm_id",
        "serial_attach_flg_nm",
        "itm_cd",
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
        "uniq_corp_cd",
        "h_no",
        "teikoku_db_kigyo_bng",
        "hojinkaku_flg",
    ]
    assert [column.header_label for column in specs["corp"][:4]] == [
        "統一企業コード",
        "法人管理番号",
        "dunsnumber",
        "法人格コード",
    ]


def test_csv_rows_start_with_primary_business_keys(generated_seed7_dir: Path) -> None:
    _, campaign_rows = read_csv(generated_seed7_dir, "DLV_OAI_MRS_CMPGN.csv")
    _, campaign_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_MRS_CMPGN_diff.csv")
    _, agency_rows = read_csv(generated_seed7_dir, "DLV_OAI_CST_ORDCSTM.csv")
    _, compass_all_rows = read_csv(generated_seed7_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, compass_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    _, product_rows = read_csv(generated_seed7_dir, "DLV_OAI_MRS_ITEM.csv")
    _, product_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_MRS_ITEM_diff.csv")
    _, bfs_all_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, bfs_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    _, bfs_device_all_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, bfs_device_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    _, bfs_accessories_all_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, bfs_accessories_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")
    _, corp_all_1_rows = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    _, corp_all_2_rows = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    _, corp_diff_rows = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")

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

    bfs_all_header, bfs_all_rows = read_csv(tmp_path, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    device_all_header, device_all_rows = read_csv(tmp_path, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    accessories_all_header, accessories_all_rows = read_csv(tmp_path, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")

    bfs_entry_numbers = {row[header_index(bfs_all_header, "bfs", "エントリ番号")] for row in bfs_all_rows}
    device_entry_index = header_index(device_all_header, "bfs_device", "エントリ番号")
    device_summary_index = header_index(device_all_header, "bfs_device", "サマリ番号")
    accessories_entry_index = header_index(accessories_all_header, "bfs_accessories", "エントリ番号")
    accessories_summary_index = header_index(accessories_all_header, "bfs_accessories", "サマリ番号")
    linked_summary_index = header_index(accessories_all_header, "bfs_accessories", "紐付けサマリ番号")

    for row in device_all_rows[:20]:
        assert row[device_entry_index] in bfs_entry_numbers
        assert row[device_summary_index].startswith("SM")

    for row in accessories_all_rows[:20]:
        assert row[accessories_entry_index] in bfs_entry_numbers
        assert row[accessories_summary_index].startswith("SM")
        assert row[linked_summary_index] == row[accessories_summary_index]


def test_bfs_device_headers_include_new_columns(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末ヘッダーに追加カラムを含める。"""
    header, _ = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")

    assert "offered_price_step1" in header
    assert "offered_price_step2" in header
    assert "offered_price_step3" in header
    assert header[-2:] == ["industrial_company_cd", "load_day"]


def test_bfs_device_optional_new_columns_use_valid_values_when_populated(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の任意新規2項目は入力時に仕様内の値にする。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")

    current_device_contract_period_index = header_index(header, "bfs_device", "現端末契約期間")
    reflected_in_summary_unit_index = header_index(header, "bfs_device", "サマリ単位反映")

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
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    current_device_contract_period_index = header_index(header, "bfs_device", "現端末契約期間")

    for row in all_rows[:20] + diff_rows[:20]:
        value = row[current_device_contract_period_index]
        if value == "":
            continue
        assert value.isdecimal()
        assert len(value) <= 2


def test_bfs_device_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_names = [column.name for column in specs["bfs_device"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")

    assert required_names == ["entry_no", "svcsm_id", "itm_cd", "brand_nm", "itm_middle_grp_nm", "itm_nm", "cate01"]
    required_indexes = [header.index(name) for name in required_names]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_device_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")

    optional_indexes = [header.index(column.name) for column in specs["bfs_device"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_device_repeating_pairs_are_contiguous_and_complete(generated_default_dir: Path) -> None:
    """BFSサービスサマリ端末の連番ペア列は途中飛びや片側入力を作らない。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    paired_groups = [
        [
            (spec_column_name("bfs_device", f"オプションカテゴリ{index}"), spec_column_name("bfs_device", f"オプションサービス{index}"))
            for index in range(1, 11)
        ],
        [
            (spec_column_name("bfs_device", f"rntoptカテゴリ{index}"), spec_column_name("bfs_device", f"rntoptプラン{index}"))
            for index in range(1, 11)
        ],
        [
            (
                spec_column_name("bfs_device", f"rntoptattカテゴリ{index}"),
                spec_column_name("bfs_device", f"rntoptattプラン{index}"),
            )
            for index in range(1, 11)
        ],
        [
            (spec_column_name("bfs_device", f"相対pdカテゴリ{index}"), spec_column_name("bfs_device", f"相対pd名称{index}"))
            for index in range(1, 11)
        ],
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
    header, rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    checks = {
        "rental_set_terminal_flg_nm": {"有", "無"},
        "mnp_flg_nm": {"有", "無"},
        "cate01": {"基本プラン（音声）", "基本プラン（データ）", "通話定額基本料（ケータイ）", "ホワイト特別相対S", "ホワイト特別相対L"},
        "cate04": {"通話料割引Wホワイト", "通話料割引Wホワイトライト"},
        "cate10": {"相対2年契約10000", "相対5年契約15000"},
        "cate11": {"ウェブ使用料（無料）", "ウェブ使用料（i）", "ウェブ使用料なし", "ウェブ使用料（スマ放題/通話基本プラン）"},
        "cate12": {"4Gデータ通信基本料(i)", "4Gデータ通信基本料(F)", "4Gデータ通信基本料(S)"},
        "cate13": {"5Gサービス利用料", "5G基本料（内包用）"},
        "cate14": {"データプラン7GB（法人）", "パケットし放題フラット"},
        "cate23": {"セレクトパック", "iPhone法人基本パック", "スマートフォン法人基本パック"},
        "cate24": {"(端末)安心保証パックB", "あんしん保証パックプラス"},
    }

    for column_name, expected_values in checks.items():
        index = bfs_device_column_index(header, column_name)
        values = {row[index] for row in rows if row[index] != ""}
        assert values
        assert values.issubset(expected_values)


def test_bfs_entry_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSエントリ情報の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_names = [column.name for column in specs["bfs"] if column.required]
    all_header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")

    assert required_names == [
        "entry_no",
        "entry_status_nm",
        "entry_type_nm",
        "application_make_type",
        "latest_appli_output_type",
        "corp_notification",
        "line_opened_status",
        "unit_agent_cd",
        "unit_agent_nm",
        "carrier_type_nm",
        "enterprise_type_nm",
        "application_no",
        "contract_type_nm",
        "entry_create_user_id",
        "entry_ins_tstamp",
        "entry_last_upd_user_id",
        "entry_last_upd_tstamp",
    ]
    required_indexes = [all_header.index(name) for name in required_names]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_entry_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSエントリ情報の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")

    optional_indexes = [header.index(column.name) for column in specs["bfs"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_entry_values_follow_updated_spec_examples(generated_default_dir: Path) -> None:
    """BFSエントリ情報の主要列は更新後の仕様例に沿う値を使う。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    rows = all_rows + diff_rows
    checks = {
        "entry_status_nm": {"エントリ作成", "試算作成", "申込書作成"},
        "entry_type_nm": {"追加新規"},
        "application_make_type": {"有", "無"},
        "latest_appli_output_type": {"有", "無"},
        "corp_notification": {"有", "無"},
        "line_opened_status": {"有", "無"},
        "contract_type_nm": {"相対", "約款"},
        "accessory_sale_flg_nm": {"有", "無"},
    }

    for name, expected_values in checks.items():
        index = header.index(name)
        values = {row[index] for row in rows if row[index] != ""}
        assert values
        assert values.issubset(expected_values)


def test_bfs_entry_dates_follow_updated_formats(generated_default_dir: Path) -> None:
    """BFSエントリ情報の日付・日時列は更新後の仕様形式で出力する。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    rows = all_rows[:20] + diff_rows[:20]

    activation_date_index = header.index("open_date")
    entry_creation_index = header.index("entry_ins_tstamp")
    entry_update_index = header.index("entry_last_upd_tstamp")
    activation_date_pattern = re.compile(r"^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$")
    date_time_pattern = re.compile(r"^\d{4}/\d{2}/\d{2} \d{1,2}:\d{2}:\d{2}$")

    for row in rows:
        if row[activation_date_index] != "":
            assert activation_date_pattern.match(row[activation_date_index])
        assert date_time_pattern.match(row[entry_creation_index])
        assert date_time_pattern.match(row[entry_update_index])


def test_bfs_entry_rental_periods_use_month_labels(generated_default_dir: Path) -> None:
    """BFSエントリ情報の期間列は仕様説明どおり月表記で出力する。"""
    all_header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")

    period_after_renewal_index = all_header.index("auto_renew_term_nm")
    initial_rental_period_index = all_header.index("initial_rental_term_nm")

    for row in all_rows[:20] + diff_rows[:20]:
        for index in (period_after_renewal_index, initial_rental_period_index):
            value = row[index]
            if value == "":
                continue
            assert re.match(r"^\d+ヶ月$", value)


def test_bfs_accessories_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_names = [column.name for column in specs["bfs_accessories"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")

    assert required_names == ["entry_no", "attach_sm_id", "serial_attach_flg_nm", "itm_cd", "brand_nm", "itm_nm", "num1", "base_price"]
    required_indexes = [header.index(name) for name in required_names]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_bfs_accessories_optional_columns_have_moderate_blanks(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品の任意列には20-35%程度の空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")

    optional_indexes = [header.index(column.name) for column in specs["bfs_accessories"] if not column.required]
    values = [row[index] for row in all_rows + diff_rows for index in optional_indexes]
    blank_rate = values.count("") / len(values)

    assert 0.20 <= blank_rate <= 0.35


def test_bfs_accessories_serial_number_accessories_is_fixed_text(generated_default_dir: Path) -> None:
    """BFSサービスサマリ付属品のシリアル付付属品は仕様説明どおり固定文言で出力する。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")
    serial_index = header.index("serial_attach_flg_nm")

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
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_CST_ORDCSTM_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        all_rows,
        diff_rows,
        header.index("ordcstm_cd"),
        expect_existing=True,
    )


def test_compass_diff_keys_include_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """COMPASS差分の業務キーは新規追加分と既存更新分を含む。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")

    assert_diff_keys_partition_initial_and_existing(all_rows, diff_rows, header.index("name"), expect_existing=True)


def test_compass_required_columns_are_populated_in_all_and_diff(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の必須列は全量・差分とも空欄にしない。"""
    specs = load_specs(ROOT / "docs/format")
    required_names = [column.name for column in specs["compass"] if column.required]
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")

    assert required_names[:6] == ["id", "name", "salesapprovaltitle", "status", "applicationdate", "paymenttype"]
    assert {"contractperiod", "plannedstartdate"} <= set(required_names)
    required_indexes = [header.index(name) for name in required_names]
    for row in all_rows + diff_rows:
        assert all(row[index] != "" for index in required_indexes)


def test_compass_optional_columns_include_blanks(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の任意列には空欄を含める。"""
    specs = load_specs(ROOT / "docs/format")
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")

    optional_indexes = [header.index(column.name) for column in specs["compass"] if not column.required]
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
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")

    for label in boolean_labels:
        index = header_index(header, "compass", label)
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
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")

    for label in yes_no_labels:
        index = header_index(header, "compass", label)
        values = {row[index] for row in all_rows + diff_rows}
        assert values <= {"", "有", "無"}


def test_compass_date_columns_follow_documented_formats(generated_default_dir: Path) -> None:
    """COMPASS営業決裁の仕様に形式がある日付列は、全量・差分とも指定形式で出力する。"""
    date_labels = ["実行予定日（提案/処理依頼予定日)", "契約開始予定日", "有効期限"]
    datetime_labels = ["作成日", "最終更新日", "最終参照日", "最終閲覧日"]
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    datetime_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$")
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    rows = all_rows + diff_rows

    for label in date_labels:
        index = header_index(header, "compass", label)
        values = [row[index] for row in rows if row[index] != ""]
        assert values
        assert all(date_pattern.match(value) for value in values)

    for label in datetime_labels:
        index = header_index(header, "compass", label)
        values = [row[index] for row in rows if row[index] != ""]
        assert values
        assert all(datetime_pattern.match(value) for value in values)


def test_corp_diff_keys_include_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """統一企業情報差分の業務キーは新規追加分と既存更新分を含む。"""
    header_1, all_rows_1 = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    _, all_rows_2 = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        all_rows_1 + all_rows_2,
        diff_rows,
        header_1.index("uniq_corp_cd"),
        expect_existing=True,
    )


def test_bfs_diff_keys_include_expected_insert_and_existing_updates(generated_default_dir: Path) -> None:
    """BFS差分3ファイルの業務キーは新規追加分と既存更新分に分かれる。"""
    bfs_header, bfs_all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO.csv")
    _, bfs_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv")
    device_header, device_all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv")
    _, device_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv")
    accessories_header, accessories_all_rows = read_csv(
        generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv"
    )
    _, accessories_diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")

    assert_diff_keys_partition_initial_and_existing(
        bfs_all_rows,
        bfs_diff_rows,
        bfs_header.index("entry_no"),
        expect_existing=True,
    )
    assert_diff_keys_partition_initial_and_existing(
        device_all_rows,
        device_diff_rows,
        device_header.index("entry_no"),
        expect_existing=False,
    )
    assert_diff_keys_partition_initial_and_existing(
        accessories_all_rows,
        accessories_diff_rows,
        accessories_header.index("itm_cd"),
        expect_existing=True,
    )


def test_bfs_accessories_diff_updates_existing_product_codes(generated_default_dir: Path) -> None:
    """BFS付属品差分の更新行は商品コードを維持しつつ主要列を変更する。"""
    header, all_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv")
    _, diff_rows = read_csv(generated_default_dir, "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv")

    product_code_index = header.index("itm_cd")
    manufacturer_index = header.index("brand_nm")
    product_name_index = header.index("itm_nm")
    quantity_1_index = header.index("num1")
    price_index = header.index("base_price")

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
    all_header, all_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN.csv")
    diff_header, diff_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_CMPGN_diff.csv")

    assert_full_refresh_diff_replaces_rows(all_header, all_rows, diff_header, diff_rows, "campaign_id")


def test_product_diff_replaces_deleted_added_and_updated_rows(generated_default_dir: Path) -> None:
    """商品diffは全量更新として削除・追加・更新後の状態を表す。"""
    all_header, all_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM.csv")
    diff_header, diff_rows = read_csv(generated_default_dir, "DLV_OAI_MRS_ITEM_diff.csv")

    assert_full_refresh_diff_replaces_rows(all_header, all_rows, diff_header, diff_rows, "itm_cd")


def test_agency_diff_existing_keys_are_subset_of_agency_all(generated_agency_seed11_dir: Path) -> None:
    """取次店差分は既存キー更新分と未存在キー追加分を生成する。"""
    agency_header, agency_rows = read_csv(generated_agency_seed11_dir, "DLV_OAI_CST_ORDCSTM.csv")
    diff_header, diff_rows = read_csv(generated_agency_seed11_dir, "DLV_OAI_CST_ORDCSTM_diff.csv")
    assert agency_header == diff_header

    assert len(diff_rows) == 53
    code_index = agency_header.index("ordcstm_cd")
    agency_codes = {row[code_index] for row in agency_rows}
    diff_codes = [row[code_index] for row in diff_rows]
    existing_diff_codes = {row[code_index] for row in diff_rows if row[code_index] in agency_codes}
    insert_codes = {row[code_index] for row in diff_rows if row[code_index] not in agency_codes}

    assert len(diff_codes) == len(set(diff_codes))
    assert existing_diff_codes.issubset(agency_codes)
    assert insert_codes.isdisjoint(agency_codes)


def test_compass_diff_updates_subset_of_compass_all(generated_compass_seed11_dir: Path) -> None:
    """営業決裁差分は既存キー更新分と未存在キー追加分を生成する。"""
    all_header, all_rows = read_csv(generated_compass_seed11_dir, "DLV_OAI_COM_EIG_KESSAI.csv")
    diff_header, diff_rows = read_csv(generated_compass_seed11_dir, "DLV_OAI_COM_EIG_KESSAI_diff.csv")
    assert all_header == diff_header

    approval_number_index = all_header.index("name")
    approval_subject_index = all_header.index("salesapprovaltitle")
    application_datetime_index = all_header.index("applicationdate")
    approval_datetime_index = header_index(all_header, "compass", "承認日時")
    sales_yen_index = header_index(all_header, "compass", "売上（円）")
    notes_index = header_index(all_header, "compass", "備考")
    changes_index = header_index(all_header, "compass", "追加・変更内容")

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
            "DLV_OAI_BFS_BFS_ENTRY_INFO" in name
            or "DLV_OAI_BFS_BFS_SERVICE_SUMMARY4" in name
            or "DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY" in name
            or "DLV_OAI_COM_EIG_KESSAI" in name
        ):
            continue
        header, rows = read_csv(generated_seed7_dir, name)
        assert_all_cells_filled(header, rows, name)


def test_corp_company_codes_are_unique_across_all_files(generated_seed7_dir: Path) -> None:
    """corp 全量CSVの統一企業コードは分割後も重複しない。"""
    header, rows_1 = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    _, rows_2 = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    code_index = header.index("uniq_corp_cd")

    codes = [row[code_index] for row in [*rows_1, *rows_2]]
    assert len(codes) == len(set(codes))


def test_corp_all_files_split_rows_in_order(generated_seed7_dir: Path) -> None:
    """corp 全量CSVは前半と後半に分割され、統一企業コードの順序が連続する。"""
    header, rows_1 = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv")
    _, rows_2 = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv")
    code_index = header.index("uniq_corp_cd")

    assert rows_1[-1][code_index] < rows_2[0][code_index]


def test_unified_company_codes_use_same_ten_character_format(generated_seed7_dir: Path) -> None:
    """各CSVの統一企業コード系項目は `UC` + 8桁の10文字形式に揃える。"""
    code_pattern = re.compile(r"^UC\d{8}$")
    targets = [
        ("DLV_OAI_COM_EIG_KESSAI.csv", "compass", ["統一企業コード"]),
        ("DLV_OAI_COM_EIG_KESSAI_diff.csv", "compass", ["統一企業コード"]),
        ("DLV_OAI_BFS_BFS_ENTRY_INFO.csv", "bfs", ["統一企業コード"]),
        ("DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv", "bfs", ["統一企業コード"]),
        ("DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv", "corp", ["統一企業コード", "親企業番号", "合併企業番号"]),
        ("DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv", "corp", ["統一企業コード", "親企業番号", "合併企業番号"]),
        ("DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv", "corp", ["統一企業コード", "親企業番号", "合併企業番号"]),
    ]

    for file_name, spec_key, labels in targets:
        header, rows = read_csv(generated_seed7_dir, file_name)
        assert rows
        for label in labels:
            index = header_index(header, spec_key, label)
            values = [row[index] for row in rows if row[index] not in {"", "0"}]
            assert values, f"{file_name}: {label}"
            assert all(len(value) <= 10 for value in values)
            assert all(code_pattern.match(value) for value in values)


def test_approval_numbers_use_same_format(generated_seed7_dir: Path) -> None:
    """各CSVの決裁番号系項目は `LS` + 7桁の9文字形式に揃える。"""
    approval_pattern = re.compile(r"^LS\d{7}$")
    targets = [
        ("DLV_OAI_COM_EIG_KESSAI.csv", "name"),
        ("DLV_OAI_COM_EIG_KESSAI_diff.csv", "name"),
        ("DLV_OAI_BFS_BFS_ENTRY_INFO.csv", "decide_no1"),
        ("DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv", "decide_no1"),
    ]

    for file_name, column_name in targets:
        header, rows = read_csv(generated_seed7_dir, file_name)
        values = [row[header.index(column_name)] for row in rows if row[header.index(column_name)] != ""]
        assert values, f"{file_name}: {column_name}"
        assert all(approval_pattern.match(value) for value in values)


def test_corp_split_counts_put_extra_row_in_first_file() -> None:
    """奇数件のcorp全量は先頭ファイルを1件多くして分割する。"""
    specs = load_specs(ROOT / "docs/format")
    counts = dict(DEFAULT_COUNTS)
    counts["corp_all"] = 5
    generator = CsvGenerator(specs=specs, seed=42, counts=counts)

    assert generator._corp_split_counts() == (3, 2)


def test_corp_parent_and_invalidity_fields_are_consistent(generated_seed7_dir: Path) -> None:
    """corp の親企業・無効理由関連の最低限の整合を確認する。"""
    header, rows = read_csv(generated_seed7_dir, "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv")
    company_code_index = header.index("uniq_corp_cd")
    parent_flag_index = header_index(header, "corp", "親企業フラグ")
    parent_company_index = header_index(header, "corp", "親企業番号")
    invalid_flag_index = header_index(header, "corp", "有効無効フラグ")
    invalid_reason_index = header_index(header, "corp", "無効理由")
    merged_company_index = header_index(header, "corp", "合併企業番号")
    registered_at_index = header_index(header, "corp", "登録日時")
    updated_at_index = header_index(header, "corp", "更新日時")

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
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv",
        "DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv",
    ):
        header, rows = read_csv(generated_seed7_dir, file_name)
        datetime_indexes = [header_index(header, "corp", label) for label in ("登録日", "更新日", "登録日時", "更新日時")]

        for row in rows[:20]:
            for index in datetime_indexes:
                assert timestamp_pattern.match(row[index])


def test_campaign_old_flag_is_always_filled(tmp_path: Path) -> None:
    """キャンペーンの旧フラグは全行で非空欄にする。"""
    run_script(str(tmp_path), "--targets", "campaign", "--seed", "7")

    for file_name in ("DLV_OAI_MRS_CMPGN.csv", "DLV_OAI_MRS_CMPGN_diff.csv"):
        header, rows = read_csv(tmp_path, file_name)
        old_flag_index = header.index("old_flg")

        assert {row[old_flag_index] for row in rows}.issubset({"0", "1"})


def test_compass_status_is_fixed_to_approved_and_history_is_filled(generated_seed7_dir: Path) -> None:
    """営業決裁のステータス固定と承認履歴非空欄を確認する。"""
    for file_name in ("DLV_OAI_COM_EIG_KESSAI.csv", "DLV_OAI_COM_EIG_KESSAI_diff.csv"):
        header, rows = read_csv(generated_seed7_dir, file_name)
        status_index = header.index("status")
        history_index = header_index(header, "compass", "承認履歴")

        assert {row[status_index] for row in rows} == {"承認"}
        assert all(row[history_index] != "" for row in rows)
