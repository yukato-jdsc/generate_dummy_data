# CSV Header Label Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CSV の 1 行目を英字カラム名ではなく `docs/format.md` の日本語項目名で出力し、内部の値生成キーは現状のまま維持する。

**Architecture:** `ColumnSpec` に内部参照用の英字カラム名と出力用の日本語ヘッダー名を分離して保持する。仕様読込で両方を設定し、行生成は英字カラム名、CSV 書き出しは日本語ヘッダー名を使う。テストは CLI 実行ベースの既存方針を維持しつつ、ヘッダー期待値だけ更新する。

**Tech Stack:** Python 3.12, unittest, uv

---

### Task 1: ヘッダー仕様の失敗テストを追加する

**Files:**
- Modify: `tests/test_generate_csv.py`
- Test: `tests/test_generate_csv.py`

- [ ] **Step 1: Write the failing test**

```python
    def test_csv_headers_use_japanese_labels_from_format_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            self.run_script(tmp_dir)

            campaign_header, _ = self.read_csv(output_dir, "m_campaign_all.csv")
            agency_header, _ = self.read_csv(output_dir, "m_agency_all.csv")
            diff_header, _ = self.read_csv(output_dir, "m_agency_diff.csv")
            product_header, _ = self.read_csv(output_dir, "m_product_all.csv")

            self.assertEqual(campaign_header[:3], ["キャンペーンid", "キャンペーン名称", "説明"])
            self.assertEqual(agency_header[:3], ["取次店コード", "有効開始日", "有効終了日"])
            self.assertEqual(product_header[:3], ["商品コード", "有効開始日", "有効開始時間"])
            self.assertEqual(agency_header, diff_header)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_generate_csv.GenerateCsvCliTests.test_csv_headers_use_japanese_labels_from_format_spec`
Expected: FAIL because current header output is English column names such as `campaign_id`

- [ ] **Step 3: Adjust the subset test to the new header**

```python
            index = agency_header.index("取次店コード")
```

- [ ] **Step 4: Run the targeted tests and confirm the current code still fails only on the new header expectation**

Run: `uv run python -m unittest tests.test_generate_csv.GenerateCsvCliTests.test_csv_headers_use_japanese_labels_from_format_spec tests.test_generate_csv.GenerateCsvCliTests.test_agency_diff_is_subset_of_agency_all`
Expected: first test FAIL, second test PASS after the header lookup string is updated

- [ ] **Step 5: Commit**

```bash
git add tests/test_generate_csv.py
git commit -m "test: verify csv headers use japanese labels"
```

### Task 2: 仕様読込と CSV 出力で表示名を使う

**Files:**
- Modify: `csv_generator/config.py`
- Modify: `csv_generator/format_spec.py`
- Modify: `csv_generator/cli.py`
- Modify: `csv_generator/generators.py`
- Test: `tests/test_generate_csv.py`

- [ ] **Step 1: Add header label to `ColumnSpec`**

```python
@dataclass(frozen=True)
class ColumnSpec:
    name: str
    header_label: str
    data_type: str
    max_length: int | None
```

- [ ] **Step 2: Parse both item labels and column names from `docs/format.md`**

```python
        item_label = parts[2]
        name = parts[3].strip("`")
        if name == "id":
            continue
        columns.append(
            ColumnSpec(
                name=name,
                header_label=item_label,
                data_type=parts[4],
                max_length=parse_max_length(parts[5]),
            )
        )
```

- [ ] **Step 3: Switch campaign and product CSV headers to `header_label`**

```python
            [column.header_label for column in specs["campaign"]],
```

```python
            [column.header_label for column in specs["product"]],
```

- [ ] **Step 4: Switch agency CSV headers to `header_label` while keeping row resolution on `name`**

```python
        headers = [column.header_label for column in self.specs["agency"]]
```

- [ ] **Step 5: Run the focused test suite**

Run: `uv run python -m unittest tests.test_generate_csv`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add csv_generator/config.py csv_generator/format_spec.py csv_generator/cli.py csv_generator/generators.py tests/test_generate_csv.py
git commit -m "fix: use japanese labels for csv headers"
```
