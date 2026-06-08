# generate_dummy_data

`docs/format/` 配下の定義をもとに、アプリ取り込み用のテストCSVを生成します。

対象は次の16ファイルです。実際の出力ファイル名には日付プレフィックスが付きます。

- `DLV_OAI_MRS_CMPGN.csv`
- `DLV_OAI_MRS_CMPGN_diff.csv`
- `DLV_OAI_CST_ORDCSTM.csv`
- `DLV_OAI_CST_ORDCSTM_diff.csv`
- `DLV_OAI_COM_EIG_KESSAI.csv`
- `DLV_OAI_COM_EIG_KESSAI_diff.csv`
- `DLV_OAI_MRS_ITEM.csv`
- `DLV_OAI_MRS_ITEM_diff.csv`
- `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv`
- `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv`
- `DLV_OAI_BFS_BFS_ENTRY_INFO.csv`
- `DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv`
- `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv`
- `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv`
- `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv`
- `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv`

`docs/format.md` は索引で、実体の定義は `docs/format/` 配下にあります。

## 出力ファイル名

出力ファイル名は `YYYYMMDD_<CSV名>` です。`YYYYMMDD` は実行日のローカル日付です。
`--output-date YYYYMMDD` を指定した場合は、指定日を基準日にします。
`*_diff.csv` は差分データとして扱い、基準日の翌日を `YYYYMMDD` に使います。

例: 2026年5月1日に実行した場合

- `20260501_DLV_OAI_MRS_CMPGN.csv`
- `20260502_DLV_OAI_MRS_CMPGN_diff.csv`
- `20260501_DLV_OAI_CST_ORDCSTM.csv`
- `20260502_DLV_OAI_CST_ORDCSTM_diff.csv`

`--gzip` 指定時は日付プレフィックス付きの `.csv.gz` を生成します。

## 前提

- Python `3.12` 以上
- `uv` が利用できること
- 依存ライブラリは `faker`、開発時テスト実行には `pytest`

初回実行時は `uv` が仮想環境と依存関係を自動で準備します。

## Usage

```bash
uv run python generate_csv.py
uv run python generate_csv.py --targets campaign
uv run python generate_csv.py --targets compass
uv run python generate_csv.py --targets corp
uv run python generate_csv.py --targets bfs
uv run python generate_csv.py --full --gzip --output-dir generated_data/full
uv run python generate_csv.py --seed 7
uv run python generate_csv.py --output-date 20260501
uv run python generate_csv.py --headers-only
uv run python generate_csv.py --duplicate-primary-keys
```

## オプション

| オプション | 説明 |
| --- | --- |
| `--output-dir` | 出力先ディレクトリ。既定値は `generated_data` |
| `--targets` | 生成対象。`campaign,agency,compass,product,corp,bfs` をカンマ区切りで指定 |
| `--output-date` | 出力ファイル名の日付プレフィックスに使う基準日。`YYYYMMDD` 形式。未指定時は実行日 |
| `--full` | 本番想定件数で生成 |
| `--gzip` | gzip 圧縮された `YYYYMMDD_*.csv.gz` を生成 |
| `--headers-only` | ヘッダー行のみのCSVを生成 |
| `--duplicate-primary-keys` | テスト用に各CSVへ主キーが重複する行を1件追加 |
| `--seed` | 乱数シード。既定値は `42` |

## 件数

通常実行時はローカル確認しやすい軽量件数で生成します。

| CSV | 既定件数 | `--full` 時 |
| --- | ---: | ---: |
| `DLV_OAI_MRS_CMPGN.csv` | 5 | 1,612 |
| `DLV_OAI_MRS_CMPGN_diff.csv` | 5 | 1,612 |
| `DLV_OAI_CST_ORDCSTM.csv` | 100 | 1,110,000 |
| `DLV_OAI_CST_ORDCSTM_diff.csv` | 5 | 53 |
| `DLV_OAI_COM_EIG_KESSAI.csv` | 10 | 188,000 |
| `DLV_OAI_COM_EIG_KESSAI_diff.csv` | 2 | 2,000 |
| `DLV_OAI_MRS_ITEM.csv` | 100 | 350,000 |
| `DLV_OAI_MRS_ITEM_diff.csv` | 100 | 350,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv` | 100 | 5,600,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv` | 10 | 46,021 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO.csv` | 100 | 2,530,000 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv` | 10 | 5,921 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv` | 100 | 1,310,000 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` | 10 | 1,210 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv` | 100 | 384,000 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` | 10 | 3,907 |

`--full --gzip` では、更新後のフォーマット資料に記載されたデータ量に近づくよう、`.csv.gz` のサイズを目安として行データを調整します。非圧縮CSVのサイズは列数やクォートを維持するため調整対象外です。

## Output

- `campaign` を含む場合は `YYYYMMDD_DLV_OAI_MRS_CMPGN.csv` と `YYYYMMDD_DLV_OAI_MRS_CMPGN_diff.csv` を同時に生成します
- `agency` を含む場合は `YYYYMMDD_DLV_OAI_CST_ORDCSTM.csv` と `YYYYMMDD_DLV_OAI_CST_ORDCSTM_diff.csv` を同時に生成します
- `compass` を含む場合は次の2ファイルを生成します
  - `YYYYMMDD_DLV_OAI_COM_EIG_KESSAI.csv`
  - `YYYYMMDD_DLV_OAI_COM_EIG_KESSAI_diff.csv`
- `product` を含む場合は `YYYYMMDD_DLV_OAI_MRS_ITEM.csv` と `YYYYMMDD_DLV_OAI_MRS_ITEM_diff.csv` を同時に生成します
- `corp` を含む場合は次の2ファイルを生成します
  - `YYYYMMDD_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv`
  - `YYYYMMDD_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv`
- `bfs` を含む場合は次の6ファイルを生成します
  - `YYYYMMDD_DLV_OAI_BFS_BFS_ENTRY_INFO.csv`
  - `YYYYMMDD_DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv`
  - `YYYYMMDD_DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv`
  - `YYYYMMDD_DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv`
  - `YYYYMMDD_DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv`
  - `YYYYMMDD_DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv`
- 各CSVは `docs/format/` の列定義どおりに出力します

## 差分更新CSVについて

すべてのCSVは `docs/format/` の列定義どおりに出力し、`diff_type` 列は付与しません。
差分更新CSVは削除行を出力せず、新規追加行と既存更新行を含みます。
新規追加行は初期データに存在しない業務キー、既存更新行は初期データに存在する業務キーを使います。
`DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` は新規追加行のみを出力します。

## キャンペーンdiff CSVについて

`DLV_OAI_MRS_CMPGN_diff.csv` は同じ実行で作られた `DLV_OAI_MRS_CMPGN.csv` を変更した全量更新後データとして生成します。
`diff_type` は持たず、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `キャンペーンid` で値が変わる更新行を含みます。

## 商品diff CSVについて

`DLV_OAI_MRS_ITEM_diff.csv` は同じ実行で作られた `DLV_OAI_MRS_ITEM.csv` を変更した全量更新後データとして生成します。
`diff_type` は持たず、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `商品コード` で値が変わる更新行を含みます。

## 取次店差分CSVについて

`DLV_OAI_CST_ORDCSTM_diff.csv` は同じ実行で作られた `DLV_OAI_CST_ORDCSTM.csv` とキー整合を持つように生成します。
新規追加行の `取次店コード` は `DLV_OAI_CST_ORDCSTM.csv` に未存在、既存更新行の `取次店コード` は `DLV_OAI_CST_ORDCSTM.csv` に存在する値です。

## COMPASS差分CSVについて

`DLV_OAI_COM_EIG_KESSAI_diff.csv` は同じ実行で作られた `DLV_OAI_COM_EIG_KESSAI.csv` とキー整合を持つように生成します。
新規追加行の `決裁番号` は `DLV_OAI_COM_EIG_KESSAI.csv` に未存在、既存更新行の `決裁番号` は `DLV_OAI_COM_EIG_KESSAI.csv` に存在する値です。
既存更新行では件名、日時、売上・利益系、備考などの主要業務列も更新されます。

## 生成ルール

- 同じ `--seed` を指定すると同じ内容のCSVを再生成できます
- 日本語名、住所風データ、電話番号、コード値を組み合わせて業務データらしい見た目に寄せています
- 厳密な本番マスタ整合ではなく、型・桁数・日付整合・最低限の業務らしさを重視しています
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁以外のCSVは、ヘッダーを除く全カラムに必ず値を入れます
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁は必須項目を必ず入力し、任意項目には一定割合の空欄を含めます
- ファイルサイズの目標値には合わせません
- 文字コードは `UTF-8 with BOM` です

## 開発者向け

テストは `pytest` で実装しています。

```bash
uv run pytest
uv run ruff check .
```

実装の責務は次のように分かれています。

- `generate_csv.py`: CLI の薄い入口
- `csv_generator/cli.py`: 引数解釈と高レベル制御
- `csv_generator/format_spec.py`: `docs/format/` の列定義読込
- `csv_generator/generators.py`: 各CSVの行生成
- `csv_generator/values.py`: 共通の値生成
- `csv_generator/io.py`: CSV書き出し
