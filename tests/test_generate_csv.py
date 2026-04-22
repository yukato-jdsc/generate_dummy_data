from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "generate_csv.py"
TARGET_SIZES = {
    "m_campaign_all.csv": 400 * 1024,
    "m_agency_all.csv": 300 * 1024 * 1024,
    "m_agency_diff.csv": 80 * 1024,
    "m_product_all.csv": 219.76 * 1024 * 1024,
    "compass_sales_approval.csv": 200 * 1024 * 1024,
}
DEFAULT_ROW_COUNTS = {
    "m_campaign_all.csv": 50,
    "m_agency_all.csv": 1000,
    "m_agency_diff.csv": 53,
    "m_product_all.csv": 1000,
    "compass_sales_approval.csv": 100,
}
FULL_ROW_COUNTS = {
    "m_campaign_all.csv": 1612,
    "m_agency_all.csv": 1_200_000,
    "m_agency_diff.csv": 53,
    "m_product_all.csv": 122_802,
    "compass_sales_approval.csv": 160_000,
}


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
    with (directory / name).open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    return rows[0], rows[1:]


def generated_files(directory: Path) -> list[str]:
    """生成された CSV ファイル名をソートして返す。"""
    return sorted(path.name for path in directory.glob("*.csv"))


def assert_size_within_tolerance(path: Path, expected_size: float, tolerance: float = 0.10) -> None:
    """生成CSVの実サイズが許容幅内に収まることを検証する。"""
    actual_size = path.stat().st_size
    lower = int(expected_size * (1 - tolerance))
    upper = int(expected_size * (1 + tolerance))
    assert actual_size >= lower, f"{path.name}: actual={actual_size}, lower={lower}"
    assert actual_size <= upper, f"{path.name}: actual={actual_size}, upper={upper}"


def test_default_run_generates_all_expected_files(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    files = generated_files(tmp_path)
    assert files == [
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

    assert len(campaign_rows) == 50
    assert len(agency_rows) == 1000
    assert len(agency_diff_rows) == 53
    assert len(compass_rows) == 100
    assert len(product_rows) == 1000


def test_targets_campaign_only_generates_single_file(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "campaign")
    assert generated_files(tmp_path) == ["m_campaign_all.csv"]


def test_targets_compass_only_generates_single_file(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--targets", "compass")
    assert generated_files(tmp_path) == ["compass_sales_approval.csv"]


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
        "m_campaign_all.csv",
        "m_agency_all.csv",
        "m_agency_diff.csv",
        "compass_sales_approval.csv",
        "m_product_all.csv",
    ]:
        assert (first_tmp / name).read_text(encoding="utf-8-sig") == (second_tmp / name).read_text(
            encoding="utf-8-sig"
        )


def test_csv_headers_include_id_column(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    campaign_header, _ = read_csv(tmp_path, "m_campaign_all.csv")
    agency_header, _ = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, _ = read_csv(tmp_path, "m_agency_diff.csv")
    compass_header, _ = read_csv(tmp_path, "compass_sales_approval.csv")
    product_header, _ = read_csv(tmp_path, "m_product_all.csv")

    assert campaign_header[0] == "id"
    assert agency_header[0] == "id"
    assert diff_header[0] == "id"
    assert compass_header[0] == "ID"
    assert product_header[0] == "id"


def test_csv_headers_use_japanese_labels_from_format_spec(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    campaign_header, _ = read_csv(tmp_path, "m_campaign_all.csv")
    agency_header, _ = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, _ = read_csv(tmp_path, "m_agency_diff.csv")
    compass_header, _ = read_csv(tmp_path, "compass_sales_approval.csv")
    product_header, _ = read_csv(tmp_path, "m_product_all.csv")

    assert campaign_header[:4] == ["id", "キャンペーンid", "キャンペーン名称", "説明"]
    assert agency_header[:4] == ["id", "取次店コード", "有効開始日", "有効終了日"]
    assert compass_header[:4] == ["ID", "決裁番号", "決裁件名", "ステータス"]
    assert product_header[:4] == ["id", "商品コード", "有効開始日", "有効開始時間"]
    assert agency_header == diff_header


def test_csv_rows_include_stable_generated_id_values(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--seed", "7")

    _, campaign_rows = read_csv(tmp_path, "m_campaign_all.csv")
    _, agency_rows = read_csv(tmp_path, "m_agency_all.csv")
    _, compass_rows = read_csv(tmp_path, "compass_sales_approval.csv")
    _, product_rows = read_csv(tmp_path, "m_product_all.csv")

    assert campaign_rows[0][0] == "1"
    assert campaign_rows[1][0] == "2"
    assert agency_rows[0][0] == "1"
    assert agency_rows[1][0] == "2"
    assert product_rows[0][0] == "1"
    assert product_rows[1][0] == "2"
    assert compass_rows[0][0] == "CM0000000001"
    assert compass_rows[1][0] == "CM0000000002"


def test_agency_diff_is_subset_of_agency_all(tmp_path: Path) -> None:
    run_script(str(tmp_path), "--seed", "11")

    agency_header, agency_rows = read_csv(tmp_path, "m_agency_all.csv")
    diff_header, diff_rows = read_csv(tmp_path, "m_agency_diff.csv")
    assert agency_header == diff_header

    id_index = agency_header.index("id")
    code_index = agency_header.index("取次店コード")
    agency_pairs = {(row[id_index], row[code_index]) for row in agency_rows}
    diff_pairs = [(row[id_index], row[code_index]) for row in diff_rows]
    diff_codes = [row[code_index] for row in diff_rows]
    assert len(diff_codes) == 53
    assert len(diff_codes) == len(set(diff_codes))
    assert set(diff_pairs).issubset(agency_pairs)


def test_default_output_sizes_follow_document_ratio_targets(tmp_path: Path) -> None:
    run_script(str(tmp_path))

    for name, target_size in TARGET_SIZES.items():
        scaled_target = target_size * (DEFAULT_ROW_COUNTS[name] / FULL_ROW_COUNTS[name])
        assert_size_within_tolerance(tmp_path / name, scaled_target)


def test_compass_rows_keep_major_business_columns_filled(tmp_path: Path) -> None:
    """営業決裁の主要業務列が空欄化されないことを確認する。"""
    run_script(str(tmp_path), "--targets", "compass", "--seed", "7")

    header, rows = read_csv(tmp_path, "compass_sales_approval.csv")
    target_columns = [
        "ステータス",
        "申請日時",
        "決裁種別",
        "起案者名",
        "起案者電話番号",
        "起案者の所属組織情報一覧",
        "販路",
        "案件名",
        "企業名",
        "売上（円）",
        "営業利益（円）",
        "閲覧範囲",
        "追加・変更内容",
        "承認日時",
        "集約番号",
        "請求形態",
        "開通工事費無料",
        "負担内容1",
        "見込回線数（上限）",
        "追加情報欄",
        "要旨補足（申請者専用）",
        "試算シート番号",
        "起案者部署",
        "申請者（ユーザー名）",
    ]
    indexes = [header.index(name) for name in target_columns]

    for row in rows[:5]:
        for index in indexes:
            assert row[index] != ""


def test_compass_status_is_fixed_to_approved_and_history_is_empty(tmp_path: Path) -> None:
    """営業決裁のステータス固定と承認履歴空欄を確認する。"""
    run_script(str(tmp_path), "--targets", "compass", "--seed", "7")

    header, rows = read_csv(tmp_path, "compass_sales_approval.csv")
    status_index = header.index("ステータス")
    history_index = header.index("承認履歴")

    assert {row[status_index] for row in rows} == {"承認"}
    assert {row[history_index] for row in rows} == {""}
