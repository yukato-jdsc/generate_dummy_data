# `copy_exec_wrapper`

`copy_*` 系パイプラインの共通リトライ制御を担うラッパーパイプライン。

## 役割

- `extract_daily` から `targetDate` と `targetCSV` を受け取る
- `targetCSV` に応じて対象の `copy_*` パイプラインを呼び分ける
- Until Activity で `copy_*` の初期化 SP 実行から Copy までをまとめてリトライする
- Activity 単位のリトライではなく、`copy_*` パイプライン実行単位で最大 3 回試行する

## パラメータ

| パラメータ | 型 | 役割 |
|---|---|---|
| `targetDate` | `string` | 取得対象日の `yyyyMMdd` |
| `targetCSV` | `string` | 呼び出す `copy_*` 系パイプラインの識別子 |

## 変数

| 変数 | 初期値 | 役割 |
|---|---:|---|
| `retryCount` | `0` | 試行回数を保持する |
| `tmpRetryCount` | `0` | `retryCount` 更新用の一時変数 |
| `isSuccess` | `false` | `copy_*` 成功時に `true` へ更新する |

## リトライ制御

Until Activity の終了条件は以下。

```text
@or(
  equals(variables('isSuccess'), true),
  greaterOrEquals(variables('retryCount'), 3)
)
```

Until Activity 内では `Switch Target` で `targetCSV` を評価し、対応する `copy_*` パイプラインを `ExecutePipeline` で実行する。`copy_*` が成功した場合は `isSuccess = true` に更新する。失敗した場合は 30 秒待機し、`tmpRetryCount = @add(variables('retryCount'), 1)`、`retryCount = @variables('tmpRetryCount')` の順に更新してから次の試行に進む。

## `targetCSV` と呼び出し先

| `targetCSV` | 呼び出し先パイプライン |
|---|---|
| `bfs_entry_informations` | `copy_bfs_entry_informations` |
| `bfs_service_summary_devices` | `copy_bfs_service_summary_devices` |
| `bfs_service_summary_accessories` | `copy_bfs_service_summary_accessories` |
| `corp_customer_info` | `copy_corp_customer_info` |
| `compass_sale_approval` | `copy_compass_sale_approval` |
| `mars_agency_all` | `copy_mars_agency_all` |
| `mars_campaign` | `copy_mars_campaign` |
| `mars_product_all` | `copy_mars_product_all` |

## `copy_*` 系パイプラインとの責務分担

`copy_*` 系パイプラインは `targetDate` を受け取り、対象テーブルの初期化 SP 実行と SFTP から ETL DB への Copy 本体だけを行う。共通の Until Activity、リトライ回数、待機時間、成功判定は `copy_exec_wrapper` に集約する。
