-- 対象データベースへの実際のINSERT/UPDATE/DELETEは、出力テーブルを読み取る
-- Azure Data Factory (ADF) が担当する
--
-- ソーステーブル: tmp_diff_bfs_service_summary_devices

-- ADFでUPSERTに使用するための処理済みデータを保存するステージングテーブル
-- UPSERT判定のユニークキーとして (service_type, category, option) を使用する
CREATE TABLE IF NOT EXISTS sp_output_mst_service_options (
    service_type varchar(255) NOT NULL,
    category varchar(255) NOT NULL,
    option varchar(255) NOT NULL,
    category_normalized varchar(255) NOT NULL,
    option_normalized varchar(255) NOT NULL,
    created_at timestamp(6) NOT NULL,
    updated_at timestamp(6) NOT NULL,
    CONSTRAINT pk_sp_output_mst_service_options PRIMARY KEY (
        service_type,
        category,
        option
    )
);

CREATE OR REPLACE PROCEDURE sp_process_mst_service_options()
LANGUAGE PLPGSQL
AS $$
DECLARE
    v_now TIMESTAMP := NOW();
BEGIN
    -- 処理開始前に出力テーブルをクリア
    TRUNCATE TABLE sp_output_mst_service_options;

    -- アンピボットしたデータを集約するための一時テーブルを作成
    CREATE TEMP TABLE tmp_all_service_options (
        service_type varchar(255),
        category varchar(255),
        option varchar(255)
    );

    -- ステップ1: option_categoryおよびoption_serviceカラムをアンピボットする
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT 'オプション', optcate1, optsvc1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate2, optsvc2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate3, optsvc3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate4, optsvc4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate5, optsvc5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate6, optsvc6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate7, optsvc7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate8, optsvc8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate9, optsvc9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', optcate10, optsvc10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ2: rntopt_categoryおよびrntopt_planカラムをアンピボットする (レンタルオプション)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT 'レンタルオプション', rntopt1, rntpln1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt2, rntpln2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt3, rntpln3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt4, rntpln4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt5, rntpln5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt6, rntpln6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt7, rntpln7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt8, rntpln8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt9, rntpln9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt10, rntpln10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ3: relative_pd_categoryおよびrelative_pd_nameカラムをアンピボットする (相対プロダクト)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT '相対プロダクト', pcn1, pdn1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn2, pdn2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn3, pdn3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn4, pdn4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn5, pdn5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn6, pdn6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn7, pdn7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn8, pdn8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn9, pdn9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', pcn10, pdn10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ4: relative_other_pd_categoryおよびrelative_other_pd_nameカラムをアンピボットする (相対その他プロダクト)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT '相対その他プロダクト', opcn1, opdn1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', opcn2, opdn2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', opcn3, opdn3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', opcn4, opdn4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', opcn5, opdn5 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ5: アンピボットしたデータを重複排除し、categoryとoptionの両方がNULLまたは空文字である行を除去する
    CREATE TEMP TABLE tmp_distinct_service_options AS
    SELECT DISTINCT service_type, category, option
    FROM tmp_all_service_options
    WHERE NULLIF(TRIM(category), '') IS NOT NULL
       OR NULLIF(TRIM(option), '') IS NOT NULL;

    -- ステップ6: 単一カラムの個別値を処理する
    -- 既に収集済みのサービス種別データ内に(category, option)の組み合わせとして存在するかを確認する。
    -- 該当する場合、そのservice_typeで新しい行を追加する。
    INSERT INTO tmp_distinct_service_options (service_type, category, option)
    SELECT DISTINCT t.service_type, s.column_name, s.value
    FROM (
        SELECT 'campnm1' AS column_name, campnm1 AS value FROM tmp_diff_bfs_service_summary_devices WHERE campnm1 IS NOT NULL
        UNION ALL
        SELECT 'campnm2', campnm2 FROM tmp_diff_bfs_service_summary_devices WHERE campnm2 IS NOT NULL
        UNION ALL
        SELECT 'campnm3', campnm3 FROM tmp_diff_bfs_service_summary_devices WHERE campnm3 IS NOT NULL
        UNION ALL
        SELECT 'campnm4', campnm4 FROM tmp_diff_bfs_service_summary_devices WHERE campnm4 IS NOT NULL
        UNION ALL
        SELECT 'campnm5', campnm5 FROM tmp_diff_bfs_service_summary_devices WHERE campnm5 IS NOT NULL
        UNION ALL
        SELECT 'cate01', cate01 FROM tmp_diff_bfs_service_summary_devices WHERE cate01 IS NOT NULL
        UNION ALL
        SELECT 'cate02', cate02 FROM tmp_diff_bfs_service_summary_devices WHERE cate02 IS NOT NULL
        UNION ALL
        SELECT 'cate03', cate03 FROM tmp_diff_bfs_service_summary_devices WHERE cate03 IS NOT NULL
        UNION ALL
        SELECT 'cate04', cate04 FROM tmp_diff_bfs_service_summary_devices WHERE cate04 IS NOT NULL
        UNION ALL
        SELECT 'cate05', cate05 FROM tmp_diff_bfs_service_summary_devices WHERE cate05 IS NOT NULL
        UNION ALL
        SELECT 'cate06', cate06 FROM tmp_diff_bfs_service_summary_devices WHERE cate06 IS NOT NULL
        UNION ALL
        SELECT 'cate07', cate07 FROM tmp_diff_bfs_service_summary_devices WHERE cate07 IS NOT NULL
        UNION ALL
        SELECT 'cate08', cate08 FROM tmp_diff_bfs_service_summary_devices WHERE cate08 IS NOT NULL
        UNION ALL
        SELECT 'cate09', cate09 FROM tmp_diff_bfs_service_summary_devices WHERE cate09 IS NOT NULL
    ) s
    JOIN tmp_distinct_service_options t ON t.category = s.column_name AND t.option = s.value;

    -- ステップ7: 重複排除済みの結果を正規化処理を施した上で出力テーブルへINSERTする
    INSERT INTO sp_output_mst_service_options (
        service_type,
        category,
        option,
        category_normalized,
        option_normalized,
        created_at,
        updated_at
    )
    SELECT DISTINCT
        LEFT(COALESCE(service_type, ''), 255) AS service_type,
        LEFT(COALESCE(category, ''), 255) AS category,
        LEFT(COALESCE(option, ''), 255) AS option,
        -- categoryを正規化する (NFKC変換、空白除去、連続空白の圧縮、「ー」を「-」に置換、小文字変換)
        LEFT(
            LOWER(
                REPLACE(
                    REGEXP_REPLACE(
                        TRIM(NORMALIZE(COALESCE(category, ''), NFKC)),
                        '\s+',
                        ' ',
                        'g'
                    ),
                    'ー',
                    '-'
                )
            ),
            255
        ) AS category_normalized,
        -- optionを正規化する
        LEFT(
            LOWER(
                REPLACE(
                    REGEXP_REPLACE(
                        TRIM(NORMALIZE(COALESCE(option, ''), NFKC)),
                        '\s+',
                        ' ',
                        'g'
                    ),
                    'ー',
                    '-'
                )
            ),
            255
        ) AS option_normalized,
        v_now AS created_at,
        v_now AS updated_at
    FROM tmp_distinct_service_options
    ON CONFLICT (service_type, category, option) DO UPDATE SET
        category_normalized = EXCLUDED.category_normalized,
        option_normalized = EXCLUDED.option_normalized,
        updated_at = EXCLUDED.updated_at;

    -- 一時テーブルを削除
    DROP TABLE IF EXISTS tmp_all_service_options;
    DROP TABLE IF EXISTS tmp_distinct_service_options;

END;
$$;
