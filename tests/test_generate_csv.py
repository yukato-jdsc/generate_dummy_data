from __future__ import annotations

import csv
import gzip
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from csv_generator.cli import write_target_csv
from csv_generator.format_spec import load_specs
from csv_generator.io import build_output_path

SCRIPT = ROOT / "generate_csv.py"


def test_unit_tests_do_not_use_full_option() -> None:
    """単体テスト内で `--full` 実行を使わない方針を守る。"""
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = "--" + "full"
    assert f'"{forbidden}"' not in source


def run_script(output_dir: str, *args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    """CLI を実行し、必要に応じて正常終了を検証する。"""
    command = ["uv", "run", "python", str(SCRIPT), "--output-dir", output_dir, *args]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_success:
        assert completed.returncode == 0, f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    return completed


def read_csv(directory: Path, name: str) -> tuple[list[str], list[list[str]]]:
    """CSV のヘッダーとデータ行を読み込む。"""
    path = directory / name
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


def assert_all_cells_filled(header: list[str], rows: list[list[str]], name: str) -> None:
    """CSV内の全セルが空欄でないことを検証する。"""
    assert header, f"{name}: header is empty"
    for row_index, row in enumerate(rows, start=1):
        assert len(row) == len(header), f"{name}: row={row_index}, columns={len(row)}, header={len(header)}"
        for column_index, value in enumerate(row):
            assert value != "", f"{name}: row={row_index}, column={header[column_index]}"


def test_default_run_generates_all_expected_files(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    files = generated_files(tmp_path)
    assert files == [
        "bfs_entry_informations_all.csv",
        "bfs_entry_informations_diff.csv",
        "compass_sales_approval.csv",
        "m_agency_all.csv",
        "m_agency_diff.csv",
        "m_campaign_all.csv",
        "m_product_all.csv",
    ]

    _, campaign_rows = read_csv(tmp_path, "m_campaign_all.csv")
    _, agency_rows = read_csv(tmp_path, "m_agency_all.csv")
    _, agency_diff_rows = read_csv(tmp_path, "m_agency_diff.csv")
    _, compass_rows = read_csv(tmp_path, "compass_sales_approval.csv")
    _, product_rows = read_csv(tmp_path, "m_product_all.csv")
    _, bfs_all_rows = read_csv(tmp_path, "bfs_entry_informations_all.csv")
    _, bfs_diff_rows = read_csv(tmp_path, "bfs_entry_informations_diff.csv")

    assert len(campaign_rows) == 50
    assert len(agency_rows) == 1000
    assert len(agency_diff_rows) == 53
    assert len(compass_rows) == 100
    assert len(product_rows) == 1000
    assert len(bfs_all_rows) == 1000
    assert len(bfs_diff_rows) == 100


def test_targets_campaign_only_generates_single_file(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "campaign")
    assert generated_files(tmp_path) == ["m_campaign_all.csv"]


def test_targets_compass_only_generates_single_file(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "compass")
    assert generated_files(tmp_path) == ["compass_sales_approval.csv"]


def test_targets_bfs_only_generates_two_files(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "bfs")
    assert generated_files(tmp_path) == [
        "bfs_entry_informations_all.csv",
        "bfs_entry_informations_diff.csv",
    ]


def test_console_outputs_generated_file_names(tmp_path: Path) -> None:
    completed = run_script(str(tmp_path), "--targets", "campaign,agency,compass")

    assert "m_campaign_all.csv" in completed.stdout
    assert "m_agency_all.csv" in completed.stdout
    assert "m_agency_diff.csv" in completed.stdout
    assert "compass_sales_approval.csv" in completed.stdout
    assert "m_product_all.csv" not in completed.stdout


def test_same_seed_is_deterministic(tmp_path: Path) -> None:
    first_tmp = tmp_path / "first"
    second_tmp = tmp_path / "second"
    first_tmp.mkdir()
    second_tmp.mkdir()

    run_script(str(first_tmp), "--seed", "7")
    run_script(str(second_tmp), "--seed", "7")

    for name in [
        "bfs_entry_informations_all.csv",
        "bfs_entry_informations_diff.csv",
        "m_campaign_all.csv",
        "m_agency_all.csv",
        "m_agency_diff.csv",
        "compass_sales_approval.csv",
        "m_product_all.csv",
    ]:
        assert (first_tmp / name).read_text(encoding="utf-8-sig") == (second_tmp / name).read_text(
            encoding="utf-8-sig"
        )


def test_output_path_adds_gzip_suffix_when_compressing(tmp_path: Path) -> None:
    """圧縮時は実ファイル名が `.csv.gz` になる。"""
    actual = build_output_path(tmp_path, "sample.csv", True)
    assert actual.name == "sample.csv.gz"


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


def test_csv_headers_start_with_business_keys(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    campaign_header, _ = read_csv(tmp_path, "m_campaign_all.csv")
    agency_header, _ = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, _ = read_csv(tmp_path, "m_agency_diff.csv")
    compass_header, _ = read_csv(tmp_path, "compass_sales_approval.csv")
    product_header, _ = read_csv(tmp_path, "m_product_all.csv")
    bfs_all_header, _ = read_csv(tmp_path, "bfs_entry_informations_all.csv")
    bfs_diff_header, _ = read_csv(tmp_path, "bfs_entry_informations_diff.csv")

    assert campaign_header[0] == "キャンペーンid"
    assert agency_header[0] == "取次店コード"
    assert diff_header[0] == "取次店コード"
    assert compass_header[0] == "決裁番号"
    assert product_header[0] == "商品コード"
    assert bfs_all_header[0] == "エントリ番号"
    assert bfs_diff_header[0] == "エントリ番号"
    for header in (
        campaign_header,
        agency_header,
        compass_header,
        product_header,
        bfs_all_header,
        bfs_diff_header,
    ):
        assert "id" not in header


def test_csv_headers_use_japanese_labels_from_format_spec(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    campaign_header, _ = read_csv(tmp_path, "m_campaign_all.csv")
    agency_header, _ = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, _ = read_csv(tmp_path, "m_agency_diff.csv")
    compass_header, _ = read_csv(tmp_path, "compass_sales_approval.csv")
    product_header, _ = read_csv(tmp_path, "m_product_all.csv")
    bfs_all_header, _ = read_csv(tmp_path, "bfs_entry_informations_all.csv")
    bfs_diff_header, _ = read_csv(tmp_path, "bfs_entry_informations_diff.csv")

    expected_headers = {
        "campaign": ["キャンペーンid", "キャンペーン名称", "説明", "有効開始日"],
        "agency": ["取次店コード", "有効開始日", "有効終了日", "共通店舗コード"],
        "compass": ["決裁番号", "決裁件名", "ステータス", "申請日時"],
        "product": ["商品コード", "有効開始日", "有効開始時間", "有効終了日"],
        "bfs": ["エントリ番号", "件名", "作成区分", "オーダ種別"],
    }

    assert campaign_header[:4] == expected_headers["campaign"]
    assert agency_header[:4] == expected_headers["agency"]
    assert compass_header[:4] == expected_headers["compass"]
    assert product_header[:4] == expected_headers["product"]
    assert agency_header == diff_header
    assert bfs_all_header[:4] == expected_headers["bfs"]
    assert bfs_all_header == bfs_diff_header


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


def test_load_specs_includes_bfs_entry_information() -> None:
    """実フォーマットのBFS定義が読み込める。"""
    specs = load_specs(ROOT / "docs/format")

    assert "bfs" in specs
    assert len(specs["bfs"]) == 216
    assert [column.name for column in specs["bfs"][:4]] == ["entry_number", "subject", "creation_category", "order_type"]
    assert [column.header_label for column in specs["bfs"][:4]] == ["エントリ番号", "件名", "作成区分", "オーダ種別"]


def test_csv_rows_start_with_primary_business_keys(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--seed", "7")

    _, campaign_rows = read_csv(tmp_path, "m_campaign_all.csv")
    _, agency_rows = read_csv(tmp_path, "m_agency_all.csv")
    _, compass_rows = read_csv(tmp_path, "compass_sales_approval.csv")
    _, product_rows = read_csv(tmp_path, "m_product_all.csv")
    _, bfs_all_rows = read_csv(tmp_path, "bfs_entry_informations_all.csv")
    _, bfs_diff_rows = read_csv(tmp_path, "bfs_entry_informations_diff.csv")

    expected_prefixes = {
        "campaign": "CP",
        "agency": "AG",
        "product": "PRD",
        "compass": "LS",
        "bfs_all": "EN",
        "bfs_diff": "EN",
    }

    for row in campaign_rows[:2]:
        assert row[0].startswith(expected_prefixes["campaign"])
    for row in agency_rows[:2]:
        assert row[0].startswith(expected_prefixes["agency"])
    for row in product_rows[:2]:
        assert row[0].startswith(expected_prefixes["product"])
    for row in compass_rows[:2]:
        assert row[0].startswith(expected_prefixes["compass"])
    for row in bfs_all_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_all"])
    for row in bfs_diff_rows[:2]:
        assert row[0].startswith(expected_prefixes["bfs_diff"])


def test_agency_diff_is_subset_of_agency_all(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--seed", "11")

    agency_header, agency_rows = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, diff_rows = read_csv(tmp_path, "m_agency_diff.csv")
    assert agency_header == diff_header

    assert len(diff_rows) == 53
    code_index = agency_header.index("取次店コード")
    agency_codes = {row[code_index] for row in agency_rows}
    diff_codes = [row[code_index] for row in diff_rows]
    assert len(diff_codes) == len(set(diff_codes))
    assert set(diff_codes).issubset(agency_codes)


def test_default_run_fills_every_cell_in_all_csvs(tmp_path: Path) -> None:
    """デフォルト実行では全CSVの全セルが非空欄になる。"""
    run_script(str(tmp_path), "--seed", "7")

    for name in generated_files(tmp_path):
        header, rows = read_csv(tmp_path, name)
        assert_all_cells_filled(header, rows, name)


def test_campaign_old_flag_is_always_filled(tmp_path: Path) -> None:
    """キャンペーンの旧フラグは全行で非空欄にする。"""
    run_script(str(tmp_path), "--targets", "campaign", "--seed", "7")

    header, rows = read_csv(tmp_path, "m_campaign_all.csv")
    old_flag_index = header.index("旧フラグ")

    assert {row[old_flag_index] for row in rows}.issubset({"0", "1"})


def test_compass_status_is_fixed_to_approved_and_history_is_filled(tmp_path: Path) -> None:
    """営業決裁のステータス固定と承認履歴非空欄を確認する。"""
    run_script(str(tmp_path), "--targets", "compass", "--seed", "7")

    header, rows = read_csv(tmp_path, "compass_sales_approval.csv")
    status_index = header.index("ステータス")
    history_index = header.index("承認履歴")

    assert {row[status_index] for row in rows} == {"承認"}
    assert all(row[history_index] != "" for row in rows)
