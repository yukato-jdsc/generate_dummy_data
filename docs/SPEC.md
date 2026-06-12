# CSVダミーデータ生成 仕様書

## 1. 目的

本プロジェクトは、`docs/format/` 配下のMarkdown定義をもとに、ETLやアプリ取り込み確認で利用するダミーCSVを生成する。

この文書は、2026-04-27 時点の実装とテストに基づく現行仕様をまとめたものである。  
`docs/PLAN.md` は初期設計メモとして残し、本書を最新の仕様書とする。

## 2. 対象範囲

### 2.1 対応ターゲット

CLI は次の6ターゲットをサポートする。

- `campaign`
- `agency`
- `compass`
- `product`
- `corp`
- `bfs`

### 2.2 生成ファイル

通常実行時は次の16ファイルを生成する。

| ターゲット | 出力ファイル |
| --- | --- |
| `campaign` | `DLV_OAI_MRS_CMPGN.csv`、`DLV_OAI_MRS_CMPGN_diff.csv` |
| `agency` | `DLV_OAI_CST_ORDCSTM.csv`、`DLV_OAI_CST_ORDCSTM_diff.csv` |
| `compass` | `DLV_OAI_COM_EIG_KESSAI.csv`、`DLV_OAI_COM_EIG_KESSAI_diff.csv` |
| `product` | `DLV_OAI_MRS_ITEM.csv`、`DLV_OAI_MRS_ITEM_diff.csv` |
| `corp` | `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv`、`DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv` |
| `bfs` | `DLV_OAI_BFS_BFS_ENTRY_INFO.csv`、`DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv`、`DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv`、`DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv`、`DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv`、`DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` |

`--gzip` 指定時は各ファイルを gzip 圧縮し、拡張子は `*.csv.gz` になる。

## 3. CLI仕様

基本実行例:

```bash
uv run python generate_csv.py
```

### 3.1 オプション

| オプション | 仕様 |
| --- | --- |
| `--output-dir <dir>` | 出力先ディレクトリ。既定値は `generated_data` |
| `--targets <csv>` | 生成対象。カンマ区切りで指定する。既定値は `campaign,agency,compass,product,corp,bfs` |
| `--output-date <YYYYMMDD>` | 出力ファイル名の日付プレフィックスに使う基準日。未指定時は実行日のローカル日付 |
| `--full` | 本番想定件数で生成する |
| `--gzip` | gzip 圧縮された `*.csv.gz` を生成する |
| `--headers-only` | ヘッダー行のみのCSVを生成する |
| `--duplicate-primary-keys` | テスト用に各CSVへ主キーが重複する行を1件追加する |
| `--null-optional-columns` | `docs/format/` で必須でない列を全データ行で空文字にする |
| `--seed <int>` | 乱数シード。既定値は `42` |
| `--jobs <auto\|N>` | 並列実行数。`auto` は通常実行時に1、`--full` 時は `min(CPU数, タスク数)` を採用する |

### 3.2 ターゲット指定ルール

- `--targets` の空白は無視する
- 空文字相当の場合は全ターゲット扱いに戻す
- 未定義ターゲットを含む場合はエラー終了する
- `--duplicate-primary-keys` と `--null-optional-columns` の同時指定はエラー終了する

## 4. 出力形式

### 4.1 CSV共通仕様

- 文字コードは `UTF-8 with BOM`
- 区切り文字は `,`
- ヘッダ行あり
- すべてのセルをダブルクォート付きで出力する
- 通常実行時は `.csv`、`--gzip` 時は `.csv.gz`
- 出力ファイル名は `YYYYMMDD_<CSV名>` とし、`*_diff.csv` は基準日の翌日を `YYYYMMDD` に使う

### 4.2 ヘッダ定義

- 列定義は `docs/format/` 配下のMarkdownから読み込む
- ヘッダはカラム名ではなく、日本語の表示名をそのまま使う
- 旧 `PLAN.md` にある `id` 列追加案は現行実装では採用していない

## 5. 件数仕様

### 5.1 通常実行時

| 出力ファイル | 件数 |
| --- | ---: |
| `DLV_OAI_MRS_CMPGN.csv` | 50 |
| `DLV_OAI_MRS_CMPGN_diff.csv` | 50 |
| `DLV_OAI_CST_ORDCSTM.csv` | 1,000 |
| `DLV_OAI_CST_ORDCSTM_diff.csv` | 53 |
| `DLV_OAI_COM_EIG_KESSAI.csv` | 100 |
| `DLV_OAI_COM_EIG_KESSAI_diff.csv` | 20 |
| `DLV_OAI_MRS_ITEM.csv` | 1,000 |
| `DLV_OAI_MRS_ITEM_diff.csv` | 1,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv` | 1,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv` | 100 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO.csv` | 1,000 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv` | 100 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv` | 1,000 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` | 100 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv` | 1,000 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` | 100 |

### 5.2 `--full` 実行時

| 出力ファイル | 件数 |
| --- | ---: |
| `DLV_OAI_MRS_CMPGN.csv` | 1,612 |
| `DLV_OAI_MRS_CMPGN_diff.csv` | 1,612 |
| `DLV_OAI_CST_ORDCSTM.csv` | 1,110,000 |
| `DLV_OAI_CST_ORDCSTM_diff.csv` | 53 |
| `DLV_OAI_COM_EIG_KESSAI.csv` | 188,000 |
| `DLV_OAI_COM_EIG_KESSAI_diff.csv` | 2,000 |
| `DLV_OAI_MRS_ITEM.csv` | 350,000 |
| `DLV_OAI_MRS_ITEM_diff.csv` | 350,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv` | 5,600,000 |
| `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv` | 46,021 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO.csv` | 2,530,000 |
| `DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv` | 5,921 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv` | 1,310,000 |
| `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` | 1,210 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv` | 384,000 |
| `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` | 3,907 |

補足:

- `corp` の全量件数は内部的に `corp_all` として管理し、1ファイルへ出力する
- `--full --gzip` は `.csv.gz` のサイズをフォーマット資料のデータ量に近づける。非圧縮CSVサイズは調整対象外とする
- `--null-optional-columns` 指定時は、NULL許容列をCSV上のNULL表現である空文字セルとして出力する

## 6. データ生成仕様

### 6.1 共通

- 同じ `--seed` では同じ内容を再生成できる
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁以外はすべてのセルを非空欄で出力する
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁は必須セルを非空欄にし、任意セルには一定割合の空欄を含める
- 業務データらしい見た目を優先し、日本語の会社名・担当者名・住所・電話番号・日付を生成する
- 日付や時刻は項目ごとに整合する範囲で生成する

### 6.2 `campaign`

- 主キー相当の先頭列は `キャンペーンid`
- 先頭値は `CP` プレフィックスのコードを使う
- `DLV_OAI_MRS_CMPGN.csv` と `DLV_OAI_MRS_CMPGN_diff.csv` を必ず同時生成する
- 2ファイルとも全量更新データのため `diff_type` は付与しない
- `DLV_OAI_MRS_CMPGN_diff.csv` は `DLV_OAI_MRS_CMPGN.csv` と同じヘッダ、同じ件数で出力する
- `DLV_OAI_MRS_CMPGN_diff.csv` は、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `キャンペーンid` で値が変わる更新行を含む
- `旧フラグ` は常に `"0"` または `"1"`

### 6.3 `agency`

- `DLV_OAI_CST_ORDCSTM.csv` と `DLV_OAI_CST_ORDCSTM_diff.csv` を必ず同時生成する
- 差分は全量から固定件数をリザーバサンプリングして抽出する
- 差分CSVのヘッダは全量CSVと同一
- `diff_type` 列は出力しない
- 差分CSVは削除行を出力しない
- 新規追加行は全量CSVに未存在の `取次店コード` を使う
- 既存更新行は全量CSVに存在する `取次店コード` を使う
- 差分件数は常に 53 件

### 6.4 `compass`

- `DLV_OAI_COM_EIG_KESSAI.csv` と `DLV_OAI_COM_EIG_KESSAI_diff.csv` を同時生成する
- `diff_type` 列は出力しない
- 差分CSVは削除行を出力しない
- `ID` 列を先頭に出力する
- 新規追加行は全量CSVに未存在の `決裁番号` を使う
- 既存更新行は全量CSVに存在する `決裁番号` を使う
- 少なくとも次の列は全量と差分で異なる値になる
  - `決裁件名`
  - `申請日時`
  - `承認日時`
  - `売上（円）`
  - `備考`
  - `追加・変更内容`
- 上記の主要業務列更新は既存更新行に適用する
- `ステータス` は承認済み系で固定運用される
- 真偽値列は `TRUE` / `FALSE` で出力する

### 6.5 `product`

- 先頭列は `商品コード`
- 先頭値は `PRD` プレフィックスのコードを使う
- `DLV_OAI_MRS_ITEM.csv` と `DLV_OAI_MRS_ITEM_diff.csv` を必ず同時生成する
- 2ファイルとも全量更新データのため `diff_type` は付与しない
- `DLV_OAI_MRS_ITEM_diff.csv` は `DLV_OAI_MRS_ITEM.csv` と同じヘッダ、同じ件数で出力する
- `DLV_OAI_MRS_ITEM_diff.csv` は、基準CSVに存在しない追加行、基準CSVから除かれた削除行、同じ `商品コード` で値が変わる更新行を含む
- 商品カテゴリ、ブランド、メーカー、色、価格などをテンプレートベースで生成する
- 開始日と終了日、開始時間と終了時間の整合を持たせる

### 6.6 `corp`

- 全量は `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv` に出力する
- `diff_type` 列は出力しない
- `統一企業コード` は重複しない
- `DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv` は新規追加行と既存更新行を混在させる
- 新規追加行は全量に未存在の `統一企業コード` を使う
- 既存更新行は全量に存在する `統一企業コード` を使う
- 差分CSVは削除行を出力しない
- 親企業関連・無効理由関連・登録日時/更新日時には最低限の整合ルールを持たせる

### 6.7 `bfs`

- 3系統をまとめて扱う
  - エントリ情報
  - サービスサマリ_端末
  - サービスサマリ_付属品
- 各系統について全量と差分を生成する
- `diff_type` 列は出力しない
- `DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv` は新規追加行と既存更新行を混在させる
- `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` は新規追加行のみを出力する
- `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` は新規追加行と既存更新行を混在させる
- `エントリ番号` は `EN`、`サマリ番号` は `SM` プレフィックスで生成する
- `DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv` の新規追加行は初期データに未存在の `エントリ番号` / `サマリ番号` を使う
- `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` の新規追加行は初期データに未存在の `商品コード` を使う
- `DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY_diff.csv` の既存更新行は初期データに存在する `商品コード` を使う
- 差分CSVは削除行を出力しない
- サービスサマリ系は同一実行で生成したBFSエントリと参照整合する
- 付属品サマリの `紐付けサマリ番号` は `サマリ番号` と同値にする

## 7. 仕様定義ファイルの扱い

- `docs/format.md` は索引
- 実際の列定義は `docs/format/*.md` を読む
- 実装はMarkdown本文を一般的に解釈するのではなく、各セクションの表から表示名・カラム名・型・桁数を抽出して利用する

## 8. 非機能仕様

### 8.1 性能・実行方式

- 通常実行時の既定は直列実行
- `--full` かつ `--jobs auto` の場合はCPU数に応じて並列化する
- 進捗表示はTTY時のみ有効にする
- 非TTY環境ではファイル生成開始のメッセージのみ表示し、進捗バーは出さない

### 8.2 メモリ方針

- 大きいCSVは逐次書き出しで生成する
- `agency` と `compass` の差分抽出は、全量を丸ごと保持せず固定件数だけを保持する

## 9. テストで担保している事項

- デフォルト実行で17ファイルが生成されること
- 各ファイルの件数が期待値どおりであること
- 同一 `--seed` で完全再現できること
- `--targets`、`--jobs`、`--gzip` の解釈が正しいこと
- gzip出力が読み戻せること
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁以外の全セルが非空欄であること
- BFSエントリ情報、BFSサービスサマリ端末、BFSサービスサマリ付属品、COMPASS営業決裁の必須セルが非空欄で、任意セルに一定割合の空欄があること
- ヘッダが `docs/format/` の日本語表示名と一致すること
- `agency_diff` が `agency_all` の部分集合であること
- `campaign_diff` が全量更新として追加・削除・更新後の状態を表すこと
- `product_diff` が全量更新として追加・削除・更新後の状態を表すこと
- `compass_diff` が `compass_all` の一部を更新した内容であること
- `corp` 全量ファイルの順序と一意性が保たれること
- BFSサービスサマリがBFSエントリ番号を参照していること
