-- ADFでUPSERTに使用するための処理済みデータを保存するステージングテーブル
CREATE TABLE IF NOT EXISTS sp_output_mst_corp_customer_info (
    company_id varchar(10) NOT NULL,
    billing_number_main varchar(12) NOT NULL,
    contractor_number_main varchar(12) NOT NULL,
    company_name varchar(100) NOT NULL,
    company_name_kana varchar(200) NOT NULL,
    company_url text NOT NULL,
    corporate_structure_code varchar(2) NOT NULL,
    postal_code_contract varchar(7) NOT NULL,
    address_prefecture_contract varchar(100) NULL,
    address_city_contract varchar(100) NULL,
    address_line1_contract varchar(100) NULL,
    address_line2_contract varchar(100) NULL,
    address_building_contract varchar(100) NULL,
    ceo_name varchar(100) NOT NULL,
    ceo_name_kana varchar(200) NOT NULL,
    phone_number_main varchar(11) NULL,
    domain_name varchar(100) NOT NULL,
    created_at timestamp(6) NOT NULL,
    updated_at timestamp(6) NOT NULL,
    CONSTRAINT pk_sp_output_mst_corp_customer_info PRIMARY KEY (company_id)
);

CREATE OR REPLACE PROCEDURE sp_process_corp_customer_info()
LANGUAGE PLPGSQL
AS $$
DECLARE
    v_now TIMESTAMP := NOW();
BEGIN
    -- 処理済みデータ用のテーブルをクリア
    TRUNCATE TABLE sp_output_mst_corp_customer_info;

    -- customer infoを処理する
    -- company_idを元にDISTINCT SELECTして重複を避ける
    CREATE TEMP TABLE tmp_organized_customer_info AS
    SELECT DISTINCT ON (company_id)
        company_id,
        company_name,
        company_name_kana,
        company_url,
        corporate_structure_code,
        postal_code AS postal_code_contract,
        addresses_prefecture AS address_prefecture_contract,
        addresses_city AS address_city_contract,
        addresses_line1 AS address_line1_contract,
        addresses_line2 AS address_line2_contract,
        addresses_building AS address_building_contract,
        ceo_name,
        ceo_name_kana,
        phone_number AS phone_number_main,
        -- URLからドメインを抽出する: プロトコル部分およびwwwプレフィックスを除去する
        CASE
            WHEN company_url IS NOT NULL AND company_url != '' THEN
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        company_url,
                        '^https?://([^/]+)/?.*$',
                        '\1'
                    ),
                    '^www\.',
                    ''
                )
            ELSE NULL
        END AS domain_name
    FROM tmp_diff_corp_customer_info
    ORDER BY company_id;

    -- 対象企業情報を処理する
    -- unified_company_codeでグループ化し、billing_numberおよびcontractor_numberの最頻値取得
    CREATE TEMP TABLE tmp_bfs_target_companies AS
    WITH ranked_billing AS (
        SELECT
            corp_cd,
            bill_no,
            count(*) AS cnt,
            ROW_NUMBER() OVER (
                PARTITION BY corp_cd
                ORDER BY count(*) desc, bill_no desc
            ) AS rn
        FROM tmp_diff_bfs_entry_informations
        WHERE corp_cd IS NOT NULL
          AND corp_cd != ''
        GROUP BY corp_cd, bill_no
    ),
    ranked_contractor AS (
        SELECT
            corp_cd,
            contract_no,
            count(*) AS cnt,
            ROW_NUMBER() OVER (
                PARTITION BY corp_cd
                ORDER BY count(*) desc, contract_no desc
            ) AS rn
        FROM tmp_diff_bfs_entry_informations
        WHERE corp_cd IS NOT NULL
          AND corp_cd != ''
        GROUP BY corp_cd, contract_no
    )
    SELECT
        rb.corp_cd AS company_id,
        rb.bill_no AS billing_number_main,
        rc.contract_no AS contractor_number_main
    FROM ranked_billing rb
    LEFT JOIN ranked_contractor rc
        ON rb.corp_cd = rc.corp_cd AND rc.rn = 1
    WHERE rb.rn = 1;

    -- 新しい値が存在する場合、billing_number_mainおよびcontractor_number_mainを更新する
    CREATE TEMP TABLE tmp_updated_target_companies AS
    SELECT
        b.company_id,
        COALESCE(
            -- 文字列の整形: 数値末尾の「.0」を除去する
            CASE
                WHEN b.billing_number_main ~ '^\d+\.0$'
                THEN REGEXP_REPLACE(b.billing_number_main, '\.0$', '')
                ELSE b.billing_number_main
            END,
            ''
        ) AS billing_number_main,
        COALESCE(
            CASE
                WHEN b.contractor_number_main ~ '^\d+\.0$'
                THEN REGEXP_REPLACE(b.contractor_number_main, '\.0$', '')
                ELSE b.contractor_number_main
            END,
            ''
        ) AS contractor_number_main
    FROM tmp_bfs_target_companies b;

    -- 整理済み顧客情報と結合し、出力テーブルへINSERT
    INSERT INTO sp_output_mst_corp_customer_info (
        company_id,
        billing_number_main,
        contractor_number_main,
        company_name,
        company_name_kana,
        company_url,
        corporate_structure_code,
        postal_code_contract,
        address_prefecture_contract,
        address_city_contract,
        address_line1_contract,
        address_line2_contract,
        address_building_contract,
        ceo_name,
        ceo_name_kana,
        phone_number_main,
        domain_name,
        created_at,
        updated_at
    )
    SELECT
        -- varchar上限に合わせて切り詰め、各種変換処理を適用
        LEFT(COALESCE(t.company_id, ''), 10) AS company_id,
        LEFT(COALESCE(t.billing_number_main, ''), 12) AS billing_number_main,
        LEFT(COALESCE(t.contractor_number_main, ''), 12) AS contractor_number_main,
        LEFT(COALESCE(c.company_name, ''), 100) AS company_name,
        LEFT(COALESCE(c.company_name_kana, ''), 200) AS company_name_kana,
        COALESCE(c.company_url, '') AS company_url,
        -- corporate_structure_codeの整形: 末尾に「.0」が付与されている場合は除去
        LEFT(
            CASE
                WHEN c.corporate_structure_code ~ '^\d+\.0$'
                THEN REGEXP_REPLACE(c.corporate_structure_code, '\.0$', '')
                WHEN c.corporate_structure_code IS NULL THEN ''
                ELSE c.corporate_structure_code
            END,
            2
        ) AS corporate_structure_code,
        -- 郵便番号からハイフンを除去し、桁数上限に合わせて切り詰める
        LEFT(REPLACE(COALESCE(c.postal_code_contract, ''), '-', ''), 7) AS postal_code_contract,
        LEFT(COALESCE(c.address_prefecture_contract, ''), 100) AS address_prefecture_contract,
        LEFT(COALESCE(c.address_city_contract, ''), 100) AS address_city_contract,
        LEFT(COALESCE(c.address_line1_contract, ''), 100) AS address_line1_contract,
        LEFT(COALESCE(c.address_line2_contract, ''), 100) AS address_line2_contract,
        LEFT(COALESCE(c.address_building_contract, ''), 100) AS address_building_contract,
        LEFT(COALESCE(c.ceo_name, ''), 100) AS ceo_name,
        LEFT(COALESCE(c.ceo_name_kana, ''), 200) AS ceo_name_kana,
        -- 電話番号からハイフンを除去し、桁数上限に合わせて切り詰める
        LEFT(REPLACE(COALESCE(c.phone_number_main, ''), '-', ''), 11) AS phone_number_main,
        LEFT(COALESCE(c.domain_name, ''), 100) AS domain_name,
        v_now AS created_at,
        v_now AS updated_at
    FROM tmp_updated_target_companies t
    LEFT JOIN tmp_organized_customer_info c ON t.company_id = c.company_id
    ON CONFLICT (company_id) DO UPDATE SET
        billing_number_main = EXCLUDED.billing_number_main,
        contractor_number_main = EXCLUDED.contractor_number_main,
        company_name = EXCLUDED.company_name,
        company_name_kana = EXCLUDED.company_name_kana,
        company_url = EXCLUDED.company_url,
        corporate_structure_code = EXCLUDED.corporate_structure_code,
        postal_code_contract = EXCLUDED.postal_code_contract,
        address_prefecture_contract = EXCLUDED.address_prefecture_contract,
        address_city_contract = EXCLUDED.address_city_contract,
        address_line1_contract = EXCLUDED.address_line1_contract,
        address_line2_contract = EXCLUDED.address_line2_contract,
        address_building_contract = EXCLUDED.address_building_contract,
        ceo_name = EXCLUDED.ceo_name,
        ceo_name_kana = EXCLUDED.ceo_name_kana,
        phone_number_main = EXCLUDED.phone_number_main,
        domain_name = EXCLUDED.domain_name,
        updated_at = EXCLUDED.updated_at;

    -- 一時テーブルを削除
    DROP TABLE IF EXISTS tmp_organized_customer_info;
    DROP TABLE IF EXISTS tmp_bfs_target_companies;
    DROP TABLE IF EXISTS tmp_updated_target_companies;

END;
$$;
