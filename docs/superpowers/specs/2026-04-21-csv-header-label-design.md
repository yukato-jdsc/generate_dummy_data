# CSV Header Label Design

## 背景

現状の CSV 生成では、`docs/format.md` の「カラム名」をヘッダーとして出力している。
要件は、CSV の 1 行目に「カラム名」ではなく「項目名」を出力すること。

## 目的

- CSV のヘッダーを日本語の項目名へ変更する
- 行データ生成で使っている内部キーは既存の英字カラム名のまま維持する
- `id` 列も `docs/format.md` の定義どおり出力する

## 採用方針

`ColumnSpec` に次の 2 種類の名前を保持する。

- `name`: 既存どおりの英字カラム名。行データ生成や内部参照で利用する
- `header_label`: `docs/format.md` の項目名。CSV ヘッダー出力で利用する

この分離により、既存の生成ロジックを壊さずに、出力ヘッダーだけを要件どおり変更する。

## 変更対象

### `csv_generator/config.py`

- `ColumnSpec` に `header_label` フィールドを追加する

### `csv_generator/format_spec.py`

- `docs/format.md` の表から「項目名」と「カラム名」をそれぞれ読み取る
- `id` 行も他列と同様に読み込む
- 生成する `ColumnSpec` に `name` と `header_label` を両方設定する

### `csv_generator/cli.py`

- `campaign` と `product` の CSV ヘッダー生成を `column.name` から `column.header_label` に切り替える

### `csv_generator/generators.py`

- `agency` 系 CSV のヘッダー生成を `column.name` から `column.header_label` に切り替える
- 行データ生成は引き続き `column.name` を使用する

### `tests/test_generate_csv.py`

- `id` 列が出力されることを確認する
- 代表的なヘッダーが日本語項目名になることを追加確認する
- 英字ヘッダー名で列位置を探している箇所は、日本語ヘッダー前提に更新する

## データフロー

1. `docs/format.md` を読み込む
2. 各列について英字カラム名と日本語項目名を `ColumnSpec` に保持する
3. 行データ生成時は英字カラム名で値を解決する
4. CSV 書き出し時は日本語項目名をヘッダーへ出力する

## エラーハンドリング

- 既存の仕様読込方式を維持し、対象セクションが見つからない場合の挙動は変更しない
- 今回は `docs/format.md` の表構造変更までは扱わない

## テスト方針

- CLI 実行で生成した CSV のヘッダーが日本語項目名になっていることを確認する
- `m_agency_all.csv` と `m_agency_diff.csv` で同一ヘッダーが出力されることを確認する
- 差分 CSV が全量 CSV の部分集合である既存検証は維持する

## 非対象

- データ本体の生成ルール変更
- CSV の文字コードや出力ファイル名の変更
- `docs/format.md` 自体の記述変更
