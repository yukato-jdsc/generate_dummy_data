# ETLアーキテクチャ

シークエンス図は [sequence.md](./sequence.md) を参照。

## 対象スコープ

- `b_hjn_bfs_mobile_entry` -> `tmp_diff_bfs_entry_informations`
- `b_hjn_bfs_mobile_service_summary_device` -> `tmp_diff_bfs_service_summary_devices`
- `b_hjn_bfs_mobile_service_summary_accessory` -> `tmp_diff_bfs_service_summary_accessories`
- `m_hjn_smt_unified_company` -> `tmp_diff_corp_customer_info`
- `b_hjn_com_sales_approval` -> `tmp_diff_compass_sales_approval`
- `m_agency_all` -> `tmp_diff_mars_agency`
- `m_campaign` -> `tmp_mars_campaign`
- `m_product_all` -> `tmp_mars_product`

## システム全体

```mermaid
flowchart LR
    subgraph EXT["外部連携"]
        SRC["Kiwi (SFTP)"]
    end

    subgraph ETL["ETLシステム"]
        ADF["Azure Data Factory"]
        ETLDB[("ETL DB")]
    end

    subgraph APPGRP["アプリケーション"]
        APP[("App DB")]
    end

    ADF --> SRC
    ADF --> ETLDB
    ETLDB --> ADF
    ADF --> APP
```

## パイプライン構成

```mermaid
flowchart TD
    MASTER["summit_master"]
    DAILY["extract_daily"]
    MONTHLY["extract_monthly<br/>(placeholder)"]
    DIFF["diff系 process_*"]
    FULL["full系 process_*"]

    MASTER --> DAILY
    MASTER --> MONTHLY
    MASTER --> DIFF
    MASTER --> FULL
```

## process パイプライン詳細

```mermaid
flowchart TB
    MASTER["summit_master"]

    subgraph DAILY["extract_daily"]
        SETDATE["set target date"]
        WRAPPER["copy_exec_wrapper<br/>Until で最大 3 回試行"]
        COPYDIFF["copy_* pipelines<br/>tmp_diff_* へロード"]
        COPYFULL["copy_* pipelines<br/>tmp_mars_* へロード"]
        SETDATE --> WRAPPER
        WRAPPER --> COPYDIFF
        WRAPPER --> COPYFULL
    end

    GATE{"is_first_day_of_the_month"}
    MONTHLY["extract_monthly<br/>(inactive placeholder)"]

    subgraph DIFF["差分ファイル系 process_*"]
        ENTRY["process_bfs_entry_informations<br/>-> upsert_trn_bfs_entry_informations"]
        DEV["process_bfs_service_summary_devices<br/>-> upsert_trn_bfs_service_summary_devices"]
        ACCSUM["process_bfs_service_summary_accessories<br/>-> upsert_trn_bfs_service_summary_accessories"]
        SVC["process_mst_service_options<br/>sp_process_mst_service_options<br/>-> filter_by_existing_three_columns"]
        ACC["process_mst_accessories<br/>sp_process_mst_accessories<br/>-> upsert_mst_accessories"]
        CORP["process_mst_corp_customer_info<br/>sp_process_corp_customer_info<br/>-> upsert_mst_corp_customer_info"]
        APPR["process_trn_approval_mobile<br/>sp_process_trn_approval_mobile<br/>-> upsert_delete_trn_approval_mobile"]
        AGY["process_mst_agency<br/>-> upsert_mst_agency"]
    end

    subgraph FULL["全件ファイル系 process_*"]
        MARS["process_mst_campaign / process_mst_product<br/>Create Diff Table<br/>-> Detect diff<br/>-> Merge diff<br/>-> ExecuteDataFlow"]
    end

    MASTER --> SETDATE
    COPYDIFF --> GATE
    COPYFULL --> GATE
    GATE -. 月初のみ評価 .-> MONTHLY
    GATE --> ENTRY
    GATE --> DEV
    GATE --> ACCSUM
    GATE --> SVC
    GATE --> ACC
    GATE --> CORP
    GATE --> APPR
    GATE --> AGY
    GATE --> MARS
```

- `process_mst_campaign` と `process_mst_product` は ADF 上の手順がほぼ同型のため、1 ノードにまとめている
- `process_mst_agency` と BFS 3 系統は、Data Flow で App DB に反映する

## 基本方針

- 目的ごとにパイプラインを分割する
- `summit_master` が抽出と後続処理をオーケストレーションする
- `extract_daily` は `targetDate` を決めて 8 対象分の `copy_exec_wrapper` を並列起動する
- `extract_monthly` は将来用の placeholder として残す
- `copy_exec_wrapper` は `targetCSV` に応じて `copy_*` 系を呼び出し、Until Activity で初期化から Copy までをまとめて最大 3 回試行し、間隔は 30 秒とする
- `process_*` 系の各Activityの再試行数は 2 回とし、再試行の間隔は 30 秒とする
- 差分ファイルは `tmp_diff_*` に、全件ファイルは `tmp_*` に取り込む
- 取込先テーブルの作成・初期化は `sp_init_tmp_*` で行い、DDL を git 管理する
- 差分ファイルは `tmp_diff_*` を直接後続処理に渡す
- 全件ファイルは `tmp_base_*` / `tmp_diff_*` を使って差分判定してから App DB に反映する
- `sp_detect_diff` は比較対象カラム未指定時、主キー以外の全カラムを差分判定対象にできる

## マート別の受信方式

| 区分 | マート |
|---|---|
| 全件 | `m_campaign`, `m_product_all` |
| 差分 | `b_hjn_bfs_mobile_entry`, `b_hjn_bfs_mobile_service_summary_device`, `b_hjn_bfs_mobile_service_summary_accessory`, `m_hjn_smt_unified_company`, `b_hjn_com_sales_approval`, `m_agency_all` |

## ETL DB 上の役割

| 役割 | テーブル |
|---|---|
| 差分ファイル取込先 | `tmp_diff_*` |
| 全件ファイル取込先 | `tmp_*` |
| 全件比較用ベース | `tmp_base_*` |
| 全件比較結果 | `tmp_diff_*` |
| App DB 反映用中間出力 | `sp_output_*` |

## App DB反映先

現在の process パイプラインで使用する反映先は以下。

| 取り込み元 | App DB反映先 |
|---|---|
| `b_hjn_bfs_mobile_entry` | `trn_bfs_entry_informations`, `mst_corp_customer_info` |
| `b_hjn_bfs_mobile_service_summary_device` | `trn_bfs_service_summary_devices`, `mst_service_options` |
| `b_hjn_bfs_mobile_service_summary_accessory` | `trn_bfs_service_summary_accessories`, `mst_accessories` |
| `m_hjn_smt_unified_company` | `mst_corp_customer_info` |
| `b_hjn_com_sales_approval` | `trn_approval_mobile` |
| `m_agency_all` | `mst_agency` |

## 実行順序

1. `summit_master` が `extract_daily` を実行する
2. 毎月 1 日のみ `extract_monthly` を評価する
3. `process_bfs_entry_informations`
4. `process_bfs_service_summary_devices`
5. `process_bfs_service_summary_accessories`
6. `process_mst_service_options`
7. `process_mst_accessories`
8. `process_mst_corp_customer_info`
9. `process_trn_approval_mobile`
10. `process_mst_agency`
11. `process_mst_campaign`
12. `process_mst_product`

`process_*` は monthly 判定完了後に並列で実行。
