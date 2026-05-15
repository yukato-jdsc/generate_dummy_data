# ストアドプロシージャとADF連携

## 概要

PostgreSQL にロードしたデータに対して加工と差分判定を行い、ADF を通じて ETL DB から App DB へ反映します。

アーキテクチャ全体は [docs/etl/architecture.md](../../docs/etl/architecture.md) を、時系列の流れは [docs/etl/sequence.md](../../docs/etl/sequence.md) を参照してください。

## パイプライン構成

- `summit_master`
  - `extract_daily` を実行
  - 毎月 1 日のみ `extract_monthly` を評価
  - 後続の `process_*` パイプラインを並列実行
- `extract_daily`
  - Kiwi SFTP から gzip CSV を取得
  - `sp_init_tmp_*` で `tmp_*` を初期化
  - `tmp_*` に Copy
- `process_*`
  - 差分系は `tmp_*` から業務変換して App DB に反映
  - 全件系は `sp_detect_diff` と `sp_merge_to_base` を経由して App DB に反映

## データフロー

差分ファイル:

```text
Kiwi gzip CSV
  -> extract_daily
  -> sp_init_tmp_*()
  -> tmp_*
  -> process_*
  -> sp_output_* または Data Flow
  -> App DB
```

全件ファイル:

```text
Kiwi gzip CSV
  -> extract_daily
  -> sp_init_tmp_*()
  -> tmp_*
  -> sp_detect_diff
  -> tmp_diff_*
  -> sp_merge_to_base
  -> Data Flow
  -> App DB
```

## 抽出定義

`extract_daily` の対象テーブルは `extract_daily_items.json` で管理します。各要素は以下の 3 項目です。

- `tableName`: 取込先 `tmp_*` のベース名
- `sftpPrefix`: Kiwi 上のファイル接頭辞
- `ddlSp`: `tmp_*` を作成 / 初期化するストアドプロシージャ

現在の対象は以下です。

| sftpPrefix | tableName | ddlSp |
|---|---|---|
| `b_hjn_bfs_mobile_entry` | `bfs_entry_informations` | `sp_init_tmp_bfs_entry_informations` |
| `b_hjn_bfs_mobile_service_summary_device` | `bfs_service_summary_devices` | `sp_init_tmp_bfs_service_summary_devices` |
| `b_hjn_bfs_mobile_service_summary_accessory` | `bfs_service_summary_accessories` | `sp_init_tmp_bfs_service_summary_accessories` |
| `m_hjn_smt_unified_company` | `corp_customer_info` | `sp_init_tmp_corp_customer_info` |
| `b_hjn_com_sales_approval` | `compass_sales_approval` | `sp_init_tmp_compass_sales_approval` |
| `m_agency_all` | `mars_agency_store` | `sp_init_tmp_mars_agency` |
| `m_campaign` | `mars_campaign` | `sp_init_tmp_mars_campaign` |
| `m_product_all` | `mars_product` | `sp_init_tmp_mars_product` |

`table_metadata.json` は過去の metadata-driven な取り込み方式の名残で、現行の `extract_daily` フローでは参照していません。

## ストアドプロシージャ

### sp_init_tmp_*

各 `tmp_*` テーブルの DDL を保持し、`CREATE TABLE IF NOT EXISTS` と `TRUNCATE` を行います。

### sp_detect_diff

全件ファイル向けの差分検知を行います。

- 入力: `tmp_*`, `tmp_base_*`, 主キー, 比較対象カラム
- 出力: `tmp_diff_*`
- 補足: 比較対象カラム未指定時は主キー以外の全カラムを比較します

### sp_process_trn_approval_mobile

モバイル決裁トランザクションデータを生成します。

- 入力: `tmp_diff_compass_sales_approval`
- 出力: `sp_output_trn_approval_mobile_upsert`, `sp_output_trn_approval_mobile_delete`

### sp_process_trn_bfs_entries

BFS エントリ・端末・アクセサリの 3 テーブルを結合し、トランザクションデータを生成します。

- 入力: `tmp_diff_bfs_entry_informations`, `tmp_diff_bfs_service_summary_devices`, `tmp_diff_bfs_service_summary_accessories`
- 出力: `sp_output_trn_bfs_entries_upsert`, `sp_output_trn_bfs_entries_delete`

### sp_process_mst_accessories

アクセサリーマスタを生成します。

- 入力: `tmp_diff_bfs_service_summary_accessories`
- 出力: `sp_output_mst_accessories`

### sp_process_mst_service_options

サービスオプションマスタを生成します。

- 入力: `tmp_diff_bfs_service_summary_devices`
- 出力: `sp_output_mst_service_options`

### sp_process_mst_corp_customer_info

法人顧客マスタを生成します。

- 入力: `tmp_diff_corp_customer_info`, `tmp_diff_bfs_entry_informations`, `tmp_target_companies`
- 出力: `sp_output_mst_corp_customer_info`

## テンプレートファイル

テンプレートは単一の `pl_bfs_compass_etl` ではなく、パイプラインごとに分割されています。

- `./azure_data_factory_template/summit_master.zip`
- `./azure_data_factory_template/extract_daily.zip`
- `./azure_data_factory_template/extract_monthly.zip`
- `./azure_data_factory_template/process_trn_bfs_entries.zip`
- `./azure_data_factory_template/process_mst_service_options.zip`
- `./azure_data_factory_template/process_mst_accessories.zip`
- `./azure_data_factory_template/process_mst_corp_customer_info.zip`
- `./azure_data_factory_template/process_trn_approval_mobile.zip`
- `./azure_data_factory_template/process_mst_agency.zip`
- `./azure_data_factory_template/process_mst_campaign.zip`
- `./azure_data_factory_template/process_mst_product.zip`

各 zip と同名ディレクトリ配下の JSON / `manifest.json` は、レビューしやすいように展開してコミットしたものです。
