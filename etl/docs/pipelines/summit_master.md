# `summit_master`

## 役割

`summit_master` は ETL 全体の親パイプライン。  
`extract_daily` 実行後に月初判定を行い、後続の `process_*` パイプラインを起動。

## 起動する子パイプライン

| パイプライン | 役割 | 参照先 |
|---|---|---|
| `extract_daily` | SFTP から日次ファイルを取得し、`tmp_diff_*` / `tmp_mars_*` にロード。 | [extract_daily.md](./extract_daily.md) |
| `extract_monthly` | 月初だけ評価する placeholder。 |  |
| `process_bfs_entry_informations` | BFS エントリ情報を App DB へ反映。 | [architecture.md](../architecture.md) |
| `process_bfs_service_summary_devices` | BFS 端末サマリを App DB へ反映。 | [architecture.md](../architecture.md) |
| `process_bfs_service_summary_accessories` | BFS 付属品サマリを App DB へ反映。 | [architecture.md](../architecture.md) |
| `process_mst_service_options` | 端末サマリから `mst_service_options` を作成。 | [sp_process_mst_service_options.md](../stored_procedures/sp_process_mst_service_options.md) |
| `process_mst_accessories` | 付属品サマリから `mst_accessories` を作成。 | [sp_process_mst_accessories.md](../stored_procedures/sp_process_mst_accessories.md) |
| `process_mst_corp_customer_info` | 顧客 CSV と BFS エントリから `mst_corp_customer_info` を作成。 | [sp_process_corp_customer_info.md](../stored_procedures/sp_process_corp_customer_info.md) |
| `process_trn_approval_mobile` | COMPASS 決裁差分から `trn_approval_mobile` を作成。 | [sp_process_trn_approval_mobile.md](../stored_procedures/sp_process_trn_approval_mobile.md) |
| `process_mst_agency` | Mars 取次店データを App DB に反映。 | 専用の stored procedure ドキュメントなし |
| `process_mst_campaign` | Campaign 全件を比較し、差分のみ App DB に反映。 | 共通処理として `sp_detect_diff()` / `sp_merge_to_base()` を使用 |
| `process_mst_product` | Product 全件を比較し、差分のみ App DB に反映。 | 共通処理として `sp_detect_diff()` / `sp_merge_to_base()` を使用 |

## 処理フローチャート

```mermaid
flowchart TB
    START["summit_master 開始"]
    DAILY["extract_daily"]
    GATE{"is_first_day_of_the_month"}
    MONTHLY["extract_monthly<br/>(inactive placeholder)"]

    ENTRY["process_bfs_entry_informations"]
    DEV["process_bfs_service_summary_devices"]
    ACCSUM["process_bfs_service_summary_accessories"]
    SVC["process_mst_service_options"]
    ACC["process_mst_accessories"]
    CORP["process_mst_corp_customer_info"]
    APPR["process_trn_approval_mobile"]
    AGY["process_mst_agency"]
    CAM["process_mst_campaign"]
    PROD["process_mst_product"]

    START --> DAILY
    DAILY --> GATE
    GATE -. 月初のみ評価 .-> MONTHLY
    GATE --> ENTRY
    GATE --> DEV
    GATE --> ACCSUM
    GATE --> SVC
    GATE --> ACC
    GATE --> CORP
    GATE --> APPR
    GATE --> AGY
    GATE --> CAM
    GATE --> PROD
```

## 補足

- `extract_monthly` は ADF テンプレート上では `Inactive`。現状は placeholder 扱い。
- 各 `process_*` は `is_first_day_of_the_month` の `Completed` 後に起動。月初判定の真偽にかかわらず後続処理へ進む。
- `process_*` 系のリトライ回数と間隔は [architecture.md](../architecture.md) の基本方針に従う。
- 実行順の起点は `extract_daily`。

## 参照実装

- [`summit_master.json`](../../../etl/adf/azure_data_factory_template/summit_master/summit_master.json)
