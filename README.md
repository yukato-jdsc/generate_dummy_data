# generate_dummy_data

`docs/format/` 配下の定義をもとに、アプリ取り込み用のテストCSVを生成します。

対象は次の15ファイルです。

- `m_キャンペーン.csv`
- `m_取次店_all.csv`
- `m_取次店_all_diff.csv`
- `b_hjn_com_営業決裁.csv`
- `b_hjn_com_営業決裁_diff.csv`
- `m_商品_all.csv`
- `m_hjn_smt_統一企業情報_1.csv`
- `m_hjn_smt_統一企業情報_2.csv`
- `m_hjn_smt_統一企業情報_diff.csv`
- `b_hjn_bfs_モバイル_エントリ情報.csv`
- `b_hjn_bfs_モバイル_エントリ情報_diff.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_端末.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_付属品.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv`

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
| `m_キャンペーン.csv` | 50 | 1,612 |
| `m_取次店_all.csv` | 1,000 | 1,200,000 |
| `m_取次店_all_diff.csv` | 53 | 53 |
| `b_hjn_com_営業決裁.csv` | 100 | 160,000 |
| `b_hjn_com_営業決裁_diff.csv` | 20 | 2,000 |
| `m_商品_all.csv` | 1,000 | 122,802 |
| `m_hjn_smt_統一企業情報_1.csv` | 500 | 1,500,000 |
| `m_hjn_smt_統一企業情報_2.csv` | 500 | 1,500,000 |
| `m_hjn_smt_統一企業情報_diff.csv` | 100 | 46,021 |
| `b_hjn_bfs_モバイル_エントリ情報.csv` | 1,000 | 2,000,000 |
| `b_hjn_bfs_モバイル_エントリ情報_diff.csv` | 100 | 5,921 |
| `b_hjn_bfs_モバイル_サービスサマリ_端末.csv` | 1,000 | 1,200,000 |
| `b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv` | 100 | 1,210 |
| `b_hjn_bfs_モバイル_サービスサマリ_付属品.csv` | 1,000 | 300,000 |
| `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv` | 100 | 3,907 |

## Output

- `campaign` を含む場合は `m_キャンペーン.csv` を生成します
- `agency` を含む場合は `m_取次店_all.csv` と `m_取次店_all_diff.csv` を同時に生成します
- `compass` を含む場合は次の2ファイルを生成します
  - `b_hjn_com_営業決裁.csv`
  - `b_hjn_com_営業決裁_diff.csv`
- `product` を含む場合は `m_商品_all.csv` を生成します
- `corp` を含む場合は次の3ファイルを生成します
  - `m_hjn_smt_統一企業情報_1.csv`
  - `m_hjn_smt_統一企業情報_2.csv`
  - `m_hjn_smt_統一企業情報_diff.csv`
- `bfs` を含む場合は次の6ファイルを生成します
  - `b_hjn_bfs_モバイル_エントリ情報.csv`
  - `b_hjn_bfs_モバイル_エントリ情報_diff.csv`
  - `b_hjn_bfs_モバイル_サービスサマリ_端末.csv`
  - `b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv`
  - `b_hjn_bfs_モバイル_サービスサマリ_付属品.csv`
  - `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv`
- 各CSVは `docs/format/` の列定義どおりに出力します

## 取次店差分CSVについて

`m_取次店_all_diff.csv` は独立生成ではなく、同じ実行で作られた `m_取次店_all.csv` の母集団から 53 件を抽出して生成します。  
そのため、`m_取次店_all_diff.csv` は `m_取次店_all.csv` の部分集合になります。

## COMPASS差分CSVについて

`b_hjn_com_営業決裁_diff.csv` は独立生成ではなく、同じ実行で作られた `b_hjn_com_営業決裁.csv` の母集団から件数ぶん抽出し、主要業務列を更新した差分データとして生成します。  
そのため、`b_hjn_com_営業決裁_diff.csv` は `approval_number` をはじめとする主要識別子を `b_hjn_com_営業決裁.csv` と共有しつつ、件名、日時、売上・利益系、備考などの内容が更新されます。

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
uv run ruff check .
```

実装の責務は次のように分かれています。

- `generate_csv.py`: CLI の薄い入口
- `csv_generator/cli.py`: 引数解釈と高レベル制御
- `csv_generator/format_spec.py`: `docs/format/` の列定義読込
- `csv_generator/generators.py`: 各CSVの行生成
- `csv_generator/values.py`: 共通の値生成
- `csv_generator/io.py`: CSV書き出し
