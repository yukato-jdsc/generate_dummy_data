# ETLシーケンス図

## 概要

ETL 内での Kiwi (SFTP) / ADF / ETL DB / App DB 間の主要なやり取りを示す。

関連する全体構成図は [architecture.md](./architecture.md) を参照。

## 全体シーケンス

```mermaid
sequenceDiagram
    autonumber
    participant SRC as Kiwi (SFTP)
    participant ADF as Azure Data Factory
    participant ETL as ETL DB
    participant APP as App DB

    ADF->>ADF: summit_master 開始
    ADF->>ADF: extract_daily 実行
    ADF->>ADF: targetDate を決定

    par copy_exec_wrapper
        ADF->>ADF: targetCSV を指定して wrapper 実行
        ADF->>ADF: Until Activity で成功または最大 3 回まで試行
        ADF->>ADF: targetCSV に応じて copy_* を実行
        ADF->>ETL: CALL sp_init_tmp_*()
        ADF->>SRC: 対象 CSV.gz を取得
        SRC-->>ADF: 対象ファイル
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
    and copy_exec_wrapper
        ADF->>ADF: targetCSV を指定して wrapper 実行
        ADF->>ADF: Until Activity で成功または最大 3 回まで試行
        ADF->>ADF: targetCSV に応じて copy_* を実行
        ADF->>ETL: CALL sp_init_tmp_*()
        ADF->>SRC: 対象 CSV.gz を取得
        SRC-->>ADF: 対象ファイル
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
    end

    ADF->>ADF: 月初判定

    par diff系 process_*
        ADF->>ETL: 必要な変換を実行
        ADF->>APP: Data Flow で直接 upsert または業務変換して反映
    and full系 process_*
        ADF->>ETL: tmp_diff_* を初期化
        ADF->>ETL: sp_detect_diff 実行
        ADF->>ETL: sp_merge_to_base 実行
        ETL-->>ADF: 差分済みデータを用意
        ADF->>APP: Data Flow で反映
    end

    APP-->>ADF: 更新完了
    ADF->>ADF: summit_master 完了
```

## 日次抽出

`extract_daily` は `testTargetDate` か `TriggerTime` から `targetDate` を決め、8 対象分の `copy_exec_wrapper` を並列に実行する。`copy_exec_wrapper` は `targetCSV` に応じて対象の `copy_*` パイプラインを呼び出し、Activity 単位のリトライではなく Until Activity 内で初期化から Copy までをまとめて最大 3 回試行する。

```mermaid
sequenceDiagram
    autonumber
    participant SRC as Kiwi (SFTP)
    participant ADF as Azure Data Factory
    participant ETL as ETL DB

    ADF->>ADF: targetDate を yyyyMMdd で設定

    par 各 copy_exec_wrapper
        loop Until isSuccess == true or retryCount >= 3
            ADF->>ADF: targetCSV に応じて Switch Target
            ADF->>ADF: 対象の copy_* を ExecutePipeline で実行
            ADF->>ETL: CALL sp_init_tmp_*()
            ETL-->>ADF: 対象テーブル作成 / TRUNCATE 完了
            ADF->>SRC: {targetDate}_*.csv.gz を取得
            SRC-->>ADF: gzip CSV
            ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
            alt Copy 成功
                ETL-->>ADF: ロード完了
                ADF->>ADF: isSuccess = true
            else Copy 失敗
                ADF->>ADF: 30 秒待機
                ADF->>ADF: tmpRetryCount = retryCount + 1
                ADF->>ADF: retryCount = tmpRetryCount
            end
        end
    and 各 copy_exec_wrapper
        loop Until isSuccess == true or retryCount >= 3
            ADF->>ADF: targetCSV に応じて Switch Target
            ADF->>ADF: 対象の copy_* を ExecutePipeline で実行
            ADF->>ETL: CALL sp_init_tmp_*()
            ETL-->>ADF: 対象テーブル作成 / TRUNCATE 完了
            ADF->>SRC: {targetDate}_*.csv.gz を取得
            SRC-->>ADF: gzip CSV
            ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
            alt Copy 成功
                ETL-->>ADF: ロード完了
                ADF->>ADF: isSuccess = true
            else Copy 失敗
                ADF->>ADF: 30 秒待機
                ADF->>ADF: tmpRetryCount = retryCount + 1
                ADF->>ADF: retryCount = tmpRetryCount
            end
        end
    end
```

## 差分ファイルの後続処理

差分ファイルは ETL 側で追加の差分検知を行わず、そのまま業務変換と App DB 反映に進む。  
対象:

- `b_hjn_bfs_mobile_entry`
- `b_hjn_bfs_mobile_service_summary_device`
- `b_hjn_bfs_mobile_service_summary_accessory`
- `m_hjn_smt_unified_company`
- `b_hjn_com_sales_approval`
- `m_agency_all`

```mermaid
sequenceDiagram
    autonumber
    participant ADF as Azure Data Factory
    participant ETL as ETL DB
    participant APP as App DB

    ADF->>ETL: process_* を実行
    ADF->>APP: Data Flow で直接 upsert または業務変換して反映
    APP-->>ADF: 更新完了
```

## 全件ファイルの後続処理

全件ファイルは ETL DB 内で比較して差分化してから App DB に反映。  
対象:

- `m_campaign`
- `m_product_all`

```mermaid
sequenceDiagram
    autonumber
    participant ADF as Azure Data Factory
    participant ETL as ETL DB
    participant APP as App DB

    ADF->>ETL: tmp_diff_* を作成 / 初期化
    ADF->>ETL: CALL sp_detect_diff(tmp_*, tmp_base_*, pk, diffColumns)
    ETL-->>ADF: tmp_diff_* を生成
    ADF->>ETL: CALL sp_merge_to_base(...)
    ETL-->>ADF: tmp_base_* 更新完了
    ADF->>APP: Data Flow で反映
    APP-->>ADF: 更新完了
```

## 補足

- `sp_detect_diff` は `diffColumns` を空文字で渡した場合、主キー以外の全カラムを比較対象にできる
- `extract_monthly` は現状 placeholder のため、`summit_master` では月初のみ評価される
