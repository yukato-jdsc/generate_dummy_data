# `sp_detect_diff()` / `sp_merge_to_base()`

## 目的

今回受信した全件データと比較用ベースデータを突き合わせ、差分検出とベース更新を行う共通ストアド。  

## `sp_detect_diff()`

### 入力 / 出力

| 種別 | テーブル | 役割 |
|---|---|---|
| 入力 | `tmp_*` | 今回受信した全件データ |
| 入力 | `tmp_base_*` | 前回取り込み時点の基準データ |
| 出力 | `tmp_diff_*` | 今回取り込み分に `I/U/D` を付けた差分結果 |

### 何をするか

- `I`: 新規。今回の `tmp_*` にあり、`tmp_base_*` にない
- `U`: 更新。主キーは同じで、比較対象列に差分がある
- `D`: 削除。`tmp_base_*` にあり、今回の `tmp_*` にない

### 補足

- 主キーは `p_primary_keys` で受け取る
- 比較対象列は `p_diff_columns` で受け取る
- `p_diff_columns` が空なら、主キー以外の全列を比較する
- 初回実行で `tmp_base_*` がなければ、全件を `I` として `tmp_diff_*` に出力する

## `sp_merge_to_base()`

### 入力 / 出力

| 種別 | テーブル | 役割 |
|---|---|---|
| 入力 | `tmp_*` | 初回作成時のベース元 |
| 入力 | `tmp_diff_*` | `I/U/D` 付き差分 |
| 出力 | `tmp_base_*` | 更新後の基準データ |

### 何をするか

- 初回実行: `tmp_*` から `tmp_base_*` を作成
- `I`: `tmp_base_*` に INSERT する
- `U`: `tmp_base_*` の同じ主キー行を UPDATE する
- `D`: `tmp_base_*` の同じ主キー行を DELETE する

### 補足

- `sp_detect_diff()` が差分ラベルを作成し、`sp_merge_to_base()` がその結果を次回比較用の `tmp_base_*` に反映する
- `tmp_base_*` は次回の全件比較で「前回までの基準データ」として使われる
- 現状の呼び出し元は `process_mst_campaign` と `process_mst_product`

## 関連実装

- [`sp_detect_diff.sql`](../../../etl/adf/stored_procedure/sp_detect_diff.sql)
- [`sp_merge_to_base.sql`](../../../etl/adf/stored_procedure/sp_merge_to_base.sql)
