# generate_dummy_data

`docs/format/` 配下の定義をもとに、アプリ取り込み用のテストCSVを生成します。

対象は次の14ファイルです。

- `m_campaign_all.csv`
- `m_agency_all.csv`
- `m_agency_diff.csv`
- `compass_sales_approval.csv`
- `m_product_all.csv`
- `corp_customer_info_all_1.csv`
- `corp_customer_info_all_2.csv`
- `corp_customer_info_diff.csv`
- `bfs_entry_informations_all.csv`
- `bfs_entry_informations_diff.csv`
- `bfs_service_summary_devices_all.csv`
- `bfs_service_summary_devices_diff.csv`
- `bfs_service_summary_accessories_all.csv`
- `bfs_service_summary_accessories_diff.csv`

`docs/format.md` は索引で、実体の定義は `docs/format/` 配下にあります。

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
uv run python generate_csv.py --full --output-dir generated_data/full
uv run python generate_csv.py --seed 7
```

## オプション

| オプション | 説明 |
| --- | --- |
| `--output-dir` | 出力先ディレクトリ。既定値は `generated_data` |
| `--targets` | 生成対象。`campaign,agency,compass,product,corp,bfs` をカンマ区切りで指定 |
| `--full` | 本番想定件数で生成し、出力は gzip 圧縮された `*.csv.gz` になる |
| `--seed` | 乱数シード。既定値は `42` |

## 件数

通常実行時はローカル確認しやすい軽量件数で生成します。

| CSV | 既定件数 | `--full` 時 |
| --- | ---: | ---: |
| `m_campaign_all.csv` | 50 | 1,612 |
| `m_agency_all.csv` | 1,000 | 1,200,000 |
| `m_agency_diff.csv` | 53 | 53 |
| `compass_sales_approval.csv` | 100 | 160,000 |
| `m_product_all.csv` | 1,000 | 122,802 |
| `corp_customer_info_all_1.csv` | 500 | 1,500,000 |
| `corp_customer_info_all_2.csv` | 500 | 1,500,000 |
| `corp_customer_info_diff.csv` | 100 | 46,021 |
| `bfs_entry_informations_all.csv` | 1,000 | 2,000,000 |
| `bfs_entry_informations_diff.csv` | 100 | 5,921 |
| `bfs_service_summary_devices_all.csv` | 1,000 | 1,200,000 |
| `bfs_service_summary_devices_diff.csv` | 100 | 1,210 |
| `bfs_service_summary_accessories_all.csv` | 1,000 | 300,000 |
| `bfs_service_summary_accessories_diff.csv` | 100 | 3,907 |

## Output

- `campaign` を含む場合は `m_campaign_all.csv` を生成します
- `agency` を含む場合は `m_agency_all.csv` と `m_agency_diff.csv` を同時に生成します
- `compass` を含む場合は `compass_sales_approval.csv` を生成します
- `product` を含む場合は `m_product_all.csv` を生成します
- `corp` を含む場合は次の3ファイルを生成します
  - `corp_customer_info_all_1.csv`
  - `corp_customer_info_all_2.csv`
  - `corp_customer_info_diff.csv`
- `bfs` を含む場合は次の6ファイルを生成します
  - `bfs_entry_informations_all.csv`
  - `bfs_entry_informations_diff.csv`
  - `bfs_service_summary_devices_all.csv`
  - `bfs_service_summary_devices_diff.csv`
  - `bfs_service_summary_accessories_all.csv`
  - `bfs_service_summary_accessories_diff.csv`
- 各CSVは `docs/format/` の列定義どおりに出力します

## 取次店差分CSVについて

`m_agency_diff.csv` は独立生成ではなく、同じ実行で作られた `m_agency_all.csv` の母集団から 53 件を抽出して生成します。  
そのため、`m_agency_diff.csv` は `m_agency_all.csv` の部分集合になります。

## 生成ルール

- 同じ `--seed` を指定すると同じ内容のCSVを再生成できます
- 日本語名、住所風データ、電話番号、コード値を組み合わせて業務データらしい見た目に寄せています
- 厳密な本番マスタ整合ではなく、型・桁数・日付整合・最低限の業務らしさを重視しています
- 出力する全CSVは、ヘッダーを除く全カラムに必ず値を入れます
- ファイルサイズの目標値には合わせません
- 文字コードは `UTF-8 with BOM` です

## 開発者向け

テストは `pytest` で実装しています。

```bash
uv run pytest
```

実装の責務は次のように分かれています。

- `generate_csv.py`: CLI の薄い入口
- `csv_generator/cli.py`: 引数解釈と高レベル制御
- `csv_generator/format_spec.py`: `docs/format/` の列定義読込
- `csv_generator/generators.py`: 各CSVの行生成
- `csv_generator/values.py`: 共通の値生成
- `csv_generator/io.py`: CSV書き出し
