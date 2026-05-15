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

    par copy_* child pipelines
        ADF->>ETL: CALL sp_init_tmp_*()
        ADF->>SRC: 対象 CSV.gz を取得
        SRC-->>ADF: 対象ファイル
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
    and copy_* child pipelines
        ADF->>ETL: CALL sp_init_tmp_*()
        ADF->>SRC: 対象 CSV.gz を取得
        SRC-->>ADF: 対象ファイル
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
    end

    ADF->>ADF: 月初判定

    par diff系 process_*
        ADF->>ETL: SP 実行
        ETL-->>ADF: sp_output_* を生成
        ADF->>APP: Data Flow で反映
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

`extract_daily` は `testTargetDate` か `TriggerTime` から `targetDate` を決め、8 本の `copy_*` 子パイプラインを並列に実行。

```mermaid
sequenceDiagram
    autonumber
    participant SRC as Kiwi (SFTP)
    participant ADF as Azure Data Factory
    participant ETL as ETL DB

    ADF->>ADF: targetDate を yyyyMMdd で設定

    par 各 copy_*
        ADF->>ETL: CALL sp_init_tmp_*()
        ETL-->>ADF: 対象テーブル作成 / TRUNCATE 完了
        ADF->>SRC: {targetDate}_*.csv.gz を取得
        SRC-->>ADF: gzip CSV
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
    and 各 copy_*
        ADF->>ETL: CALL sp_init_tmp_*()
        ETL-->>ADF: 対象テーブル作成 / TRUNCATE 完了
        ADF->>SRC: {targetDate}_*.csv.gz を取得
        SRC-->>ADF: gzip CSV
        ADF->>ETL: tmp_diff_* / tmp_mars_* に Copy
        ETL-->>ADF: ロード完了
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

    ADF->>ETL: process_* の Script / Data Flow を実行
    ETL-->>ADF: sp_output_* または tmp_diff_* を返す
    ADF->>APP: Upsert / Delete
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
