-- ADFでUPSERTに使用するための処理済みデータを保存するステージングテーブル
CREATE TABLE IF NOT EXISTS sp_output_mst_accessories (
    product_code varchar(255) NOT NULL,
    manufacturer varchar(255) NULL,
    product_name varchar(255) NULL,
    product_name_normalized varchar(255) NULL,
    created_at timestamp(6) NOT NULL,
    updated_at timestamp(6) NOT NULL,
    CONSTRAINT pk_sp_output_mst_accessories PRIMARY KEY (product_code)
);

CREATE OR REPLACE PROCEDURE sp_process_mst_accessories()
LANGUAGE plpgsql
AS $$
DECLARE
    v_now TIMESTAMP := NOW();
BEGIN
    -- 処理開始前に出力テーブルをクリア
    TRUNCATE TABLE sp_output_mst_accessories;

    -- データを加工し出力テーブルへINSERT
    -- 処理手順:
    -- 1. product_codeでDISTINCT SELECTし、重複キーエラーを回避
    -- 2. varchar上限に合わせて値を切り詰める
    -- 3. product_nameを正規化してproduct_name_normalizedを生成
    INSERT INTO sp_output_mst_accessories (
        product_code,
        manufacturer,
        product_name,
        product_name_normalized,
        created_at,
        updated_at
    )
    SELECT DISTINCT ON (product_code)
        -- varchar(255)上限に合わせて切り詰める
        LEFT(COALESCE(product_code::text, ''), 255) AS product_code,
        LEFT(COALESCE(manufacturer::text, ''), 255) AS manufacturer,
        LEFT(COALESCE(product_name::text, ''), 255) AS product_name,
        -- product_nameを正規化
        -- 1. NFKC正規化 (全角から半角への変換等)
        -- 2. 前後の空白を除去
        -- 3. 連続する空白を単一の空白に圧縮
        -- 4. 「ー」(カタカナ長音記号)を「-」に置換
        -- 5. 小文字に変換
        LEFT(
            LOWER(
                REPLACE(
                    REGEXP_REPLACE(
                        TRIM(normalize(COALESCE(product_name::text, ''), NFKC)),
                        '\s+',
                        ' ',
                        'g'
                    ),
                    'ー',
                    '-'
                )
            ),
            255
        ) AS product_name_normalized,
        v_now AS created_at,
        v_now AS updated_at
    FROM tmp_diff_bfs_service_summary_accessories
    WHERE product_code IS NOT NULL
      AND product_code != ''
    ORDER BY product_code;

END;
$$;
