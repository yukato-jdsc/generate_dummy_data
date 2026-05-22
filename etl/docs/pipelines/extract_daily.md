# `extract_daily`

日次ファイル取込をオーケストレーションするパイプライン。

## 役割

- `testTargetDate` または `pipeline().TriggerTime` から `targetDate` を決定する
- 決定した `targetDate` と対象を表す `targetCSV` を `copy_exec_wrapper` に渡し、8 対象を並列にロードする
- `copy_exec_wrapper` は `targetCSV` に応じて `copy_*` 系パイプラインを呼び出す
- `copy_*` 系は初期化 SP 実行と Copy 本体を担い、共通リトライ制御は `copy_exec_wrapper` に集約する
- 差分ファイルは `tmp_diff_*`、全件ファイルは全件用一時テーブルにロードする
- 全件用一時テーブルの実装名は、現状の対象では `tmp_mars_*` になっている

## パラメータ

- `testTargetDate`
  - 指定あり: その値を `targetDate` として使う
  - 指定なし: `pipeline().TriggerTime` を `yyyyMMdd` に整形して使う

## `copy_exec_wrapper` によるリトライ制御

`extract_daily` は `copy_*` 系を直接リトライせず、対象ごとに `copy_exec_wrapper` を実行する。`copy_exec_wrapper` は `targetCSV` に応じて対象の `copy_*` を呼び出し、Until Activity で初期化 SP 実行から Copy までをまとめて最大 3 回試行する。

リトライ条件と対象の呼び分けは [`copy_exec_wrapper`](./copy_exec_wrapper.md) を参照。

## 子パイプライン一覧

| `targetCSV` | 子パイプライン | 取得ファイル | 初期化SP | ロード先 | 備考 |
|---|---|---|---|---|---|
| `bfs_entry_informations` | `copy_bfs_entry_informations` | `kw-if-f20966/{targetDate}_DLV_OAI_BFS_BFS_ENTRY_INFO.csv.gz` | `sp_init_tmp_bfs_entry_informations` | `tmp_diff_bfs_entry_informations` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `bfs_service_summary_devices` | `copy_bfs_service_summary_devices` | `kw-if-f20966/{targetDate}_DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv.gz` | `sp_init_tmp_bfs_service_summary_devices` | `tmp_diff_bfs_service_summary_devices` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `bfs_service_summary_accessories` | `copy_bfs_service_summary_accessories` | `kw-if-f20966/{targetDate}_DLV_OAI_BFS_BFS_ATTACHMENT_SUMMALLY.csv.gz` | `sp_init_tmp_bfs_service_summary_accessories` | `tmp_diff_bfs_service_summary_accessories` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `corp_customer_info` | `copy_corp_customer_info` | `kw-if-f20966/{targetDate}_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE.csv.gz` | `sp_init_tmp_corp_customer_info` | `tmp_diff_corp_customer_info` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `compass_sale_approval` | `copy_compass_sale_approval` | `kw-if-f20966/{targetDate}_DLV_OAI_COM_EIG_KESSAI.csv.gz` | `sp_init_tmp_compass_sales_approval` | `tmp_diff_compass_sales_approval` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `mars_agency_all` | `copy_mars_agency_all` | `kw-if-f20966/{targetDate}_DLV_OAI_CST_ORDCSTM.csv.gz` | `sp_init_tmp_mars_agency` | `tmp_diff_mars_agency` | INSERTとUPDATEのみ連携。`diff_type` は持たない |
| `mars_campaign` | `copy_mars_campaign` | `kw-if-f20966/{targetDate}_DLV_OAI_MRS_CMPGN.csv.gz` | `sp_init_tmp_mars_campaign` | `tmp_mars_campaign` | 全件ファイル |
| `mars_product_all` | `copy_mars_product_all` | `kw-if-f20966/{targetDate}_DLV_OAI_MRS_ITEM.csv.gz` | `sp_init_tmp_mars_product` | `tmp_mars_product` | 全件ファイル |
