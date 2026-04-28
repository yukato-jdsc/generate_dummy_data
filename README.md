# generate_dummy_data

`docs/format/` 配下の定義をもとに、アプリ取り込み用のテストCSVを生成します。

対象は次の17ファイルです。

- `m_キャンペーン.csv`
- `m_キャンペーン_diff.csv`
- `m_取次店_all.csv`
- `m_取次店_all_diff.csv`
- `b_hjn_com_営業決裁.csv`
- `b_hjn_com_営業決裁_diff.csv`
- `m_商品_all.csv`
- `m_商品_all_diff.csv`
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
uv run python generate_csv.py --full --gzip --output-dir generated_data/full
uv run python generate_csv.py --seed 7
```

## オプション

| オプション | 説明 |
| --- | --- |
| `--output-dir` | 出力先ディレクトリ。既定値は `generated_data` |
| `--targets` | 生成対象。`campaign,agency,compass,product,corp,bfs` をカンマ区切りで指定 |
| `--full` | 本番想定件数で生成 |
| `--gzip` | gzip 圧縮された `*.csv.gz` を生成 |
| `--seed` | 乱数シード。既定値は `42` |

## 件数

通常実行時はローカル確認しやすい軽量件数で生成します。

| CSV | 既定件数 | `--full` 時 |
| --- | ---: | ---: |
| `m_キャンペーン.csv` | 50 | 1,612 |
| `m_キャンペーン_diff.csv` | 50 | 1,612 |
| `m_取次店_all.csv` | 1,000 | 1,200,000 |
| `m_取次店_all_diff.csv` | 53 | 53 |
| `b_hjn_com_営業決裁.csv` | 100 | 160,000 |
| `b_hjn_com_営業決裁_diff.csv` | 20 | 2,000 |
| `m_商品_all.csv` | 1,000 | 122,802 |
| `m_商品_all_diff.csv` | 1,000 | 122,802 |
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

- `campaign` を含む場合は `m_キャンペーン.csv` と `m_キャンペーン_diff.csv` を同時に生成します
- `agency` を含む場合は `m_取次店_all.csv` と `m_取次店_all_diff.csv` を同時に生成します
- `compass` を含む場合は次の2ファイルを生成します
  - `b_hjn_com_営業決裁.csv`
  - `b_hjn_com_営業決裁_diff.csv`
- `product` を含む場合は `m_商品_all.csv` と `m_商品_all_diff.csv` を同時に生成します
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

## `diff_type` 列について

- `m_取次店_all.csv`
- `m_取次店_all_diff.csv`
- `b_hjn_com_営業決裁.csv`
- `b_hjn_com_営業決裁_diff.csv`
- `m_hjn_smt_統一企業情報_1.csv`
- `m_hjn_smt_統一企業情報_2.csv`
- `m_hjn_smt_統一企業情報_diff.csv`
- `b_hjn_bfs_モバイル_エントリ情報.csv`
- `b_hjn_bfs_モバイル_エントリ情報_diff.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_端末.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_付属品.csv`
- `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv`

上記のCSVでは、出力時に先頭列として `diff_type` を追加します。

- `I`: 新規
- `U`: 更新
- `D`: 削除

初期データ側のCSVは全行 `I` です。  
差分CSVは原則 `I` `U` `D` を混在させます。  
差分CSVでは `diff_type=I` の行は初期データに存在しない業務キー、`diff_type=U` と `diff_type=D` の行は初期データに存在する業務キーを使います。  
ただし `m_hjn_smt_統一企業情報_diff.csv`、`b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv`、`b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv` は `I` と `U` のみを出力し、`D` は出力しません。
`m_キャンペーン.csv`、`m_キャンペーン_diff.csv`、`m_商品_all.csv`、`m_商品_all_diff.csv` は全量更新データのため `diff_type` を付与しません。

## キャンペーンdiff CSVについて

`m_キャンペーン_diff.csv` は同じ実行で作られた `m_キャンペーン.csv` を変更した全量更新後データとして生成します。
`diff_type` は持たず、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `キャンペーンid` で値が変わる更新行を含みます。

## 商品diff CSVについて

`m_商品_all_diff.csv` は同じ実行で作られた `m_商品_all.csv` を変更した全量更新後データとして生成します。
`diff_type` は持たず、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `商品コード` で値が変わる更新行を含みます。

## 取次店差分CSVについて

`m_取次店_all_diff.csv` は同じ実行で作られた `m_取次店_all.csv` とキー整合を持つように生成します。
`diff_type=I` の `取次店コード` は `m_取次店_all.csv` に未存在、`diff_type=U` と `diff_type=D` の `取次店コード` は `m_取次店_all.csv` に存在する値です。

## COMPASS差分CSVについて

`b_hjn_com_営業決裁_diff.csv` は同じ実行で作られた `b_hjn_com_営業決裁.csv` とキー整合を持つように生成します。
`diff_type=I` の `決裁番号` は `b_hjn_com_営業決裁.csv` に未存在、`diff_type=U` と `diff_type=D` の `決裁番号` は `b_hjn_com_営業決裁.csv` に存在する値です。
`U` と `D` の行では件名、日時、売上・利益系、備考などの主要業務列も更新されます。

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
