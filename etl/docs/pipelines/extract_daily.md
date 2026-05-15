# `extract_daily`

日次ファイル取込をオーケストレーションするパイプライン。

## 役割

- `testTargetDate` または `pipeline().TriggerTime` から `targetDate` を決定する
- 決定した `targetDate` を 8 本の `copy_*` 子パイプラインに渡し、対応する `{targetDate}_*.csv.gz` を取得してロードする
- 差分ファイルは `tmp_diff_*`、全件ファイルは全件用一時テーブルにロードする
- 全件用一時テーブルの実装名は、現状の対象では `tmp_mars_*` になっている

## パラメータ

- `testTargetDate`
  - 指定あり: その値を `targetDate` として使う
  - 指定なし: `pipeline().TriggerTime` を `yyyyMMdd` に整形して使う

## 子パイプライン一覧

| 子パイプライン | 取得ファイル | 初期化SP | ロード先 | 備考 |
|---|---|---|---|---|
| `copy_bfs_entry_informations` | `{targetDate}_b_hjn_bfs_モバイル_エントリ情報.csv.gz` | `sp_init_tmp_bfs_entry_informations` | `tmp_diff_bfs_entry_informations` | 差分ファイル。`diff_type` を含む |
| `copy_bfs_service_summary_devices` | `{targetDate}_b_hjn_bfs_モバイル_サービスサマリ_端末.csv.gz` | `sp_init_tmp_bfs_service_summary_devices` | `tmp_diff_bfs_service_summary_devices` | 差分ファイル。`diff_type` を含む |
| `copy_bfs_service_summary_accessories` | `{targetDate}_b_hjn_bfs_モバイル_サービスサマリ_付属品.csv.gz` | `sp_init_tmp_bfs_service_summary_accessories` | `tmp_diff_bfs_service_summary_accessories` | 差分ファイル。`diff_type` を含む |
| `copy_corp_customer_info` | `{targetDate}_m_hjn_smt_統一企業情報.csv.gz` | `sp_init_tmp_corp_customer_info` | `tmp_diff_corp_customer_info` | 差分ファイル。`diff_type` を含む |
| `copy_compass_sale_approval` | `{targetDate}_b_hjn_com_営業決裁.csv.gz` | `sp_init_tmp_compass_sales_approval` | `tmp_diff_compass_sales_approval` | 差分ファイル。`diff_type` を含む |
| `copy_mars_agency_all` | `{targetDate}_m_取次店_all.csv.gz` | `sp_init_tmp_mars_agency` | `tmp_diff_mars_agency` | 差分ファイル。`diff_type` を含む |
| `copy_mars_campaign` | `{targetDate}_m_キャンペーン.csv.gz` | `sp_init_tmp_mars_campaign` | `tmp_mars_campaign` | 全件ファイル |
| `copy_mars_product_all` | `{targetDate}_m_商品_all.csv.gz` | `sp_init_tmp_mars_product` | `tmp_mars_product` | 全件ファイル |
