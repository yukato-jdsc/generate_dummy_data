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
LANGUAGE plpgsql
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
    SELECT 'オプション', option_category_1, option_service_1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_2, option_service_2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_3, option_service_3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_4, option_service_4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_5, option_service_5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_6, option_service_6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_7, option_service_7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_8, option_service_8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_9, option_service_9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'オプション', option_category_10, option_service_10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ2: rntopt_categoryおよびrntopt_planカラムをアンピボットする (レンタルオプション)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT 'レンタルオプション', rntopt_category_1, rntopt_plan_1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_2, rntopt_plan_2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_3, rntopt_plan_3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_4, rntopt_plan_4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_5, rntopt_plan_5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_6, rntopt_plan_6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_7, rntopt_plan_7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_8, rntopt_plan_8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_9, rntopt_plan_9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT 'レンタルオプション', rntopt_category_10, rntopt_plan_10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ3: relative_pd_categoryおよびrelative_pd_nameカラムをアンピボットする (相対プロダクト)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT '相対プロダクト', relative_pd_category_1, relative_pd_name_1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_2, relative_pd_name_2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_3, relative_pd_name_3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_4, relative_pd_name_4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_5, relative_pd_name_5 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_6, relative_pd_name_6 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_7, relative_pd_name_7 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_8, relative_pd_name_8 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_9, relative_pd_name_9 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対プロダクト', relative_pd_category_10, relative_pd_name_10 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ4: relative_other_pd_categoryおよびrelative_other_pd_nameカラムをアンピボットする (相対その他プロダクト)
    INSERT INTO tmp_all_service_options (service_type, category, option)
    SELECT '相対その他プロダクト', relative_other_pd_category_1, relative_other_pd_name_1 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', relative_other_pd_category_2, relative_other_pd_name_2 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', relative_other_pd_category_3, relative_other_pd_name_3 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', relative_other_pd_category_4, relative_other_pd_name_4 FROM tmp_diff_bfs_service_summary_devices
    UNION ALL
    SELECT '相対その他プロダクト', relative_other_pd_category_5, relative_other_pd_name_5 FROM tmp_diff_bfs_service_summary_devices;

    -- ステップ5: アンピボットしたデータを重複排除し、categoryとoptionの両方がNULLである行を除去する
    CREATE TEMP TABLE tmp_distinct_service_options AS
    SELECT DISTINCT service_type, category, option
    FROM tmp_all_service_options
    WHERE category IS NOT NULL OR option IS NOT NULL;

    -- ステップ6: 単一カラムの個別値を処理する
    -- 既に収集済みのサービス種別データ内に(category, option)の組み合わせとして存在するかを確認する。
    -- 該当する場合、そのservice_typeで新しい行を追加する。
    INSERT INTO tmp_distinct_service_options (service_type, category, option)
    SELECT DISTINCT t.service_type, s.column_name, s.value
    FROM (
        SELECT 'campaign_1' AS column_name, campaign_1 AS value FROM tmp_diff_bfs_service_summary_devices WHERE campaign_1 IS NOT NULL
        UNION ALL
        SELECT 'campaign_2', campaign_2 FROM tmp_diff_bfs_service_summary_devices WHERE campaign_2 IS NOT NULL
        UNION ALL
        SELECT 'campaign_3', campaign_3 FROM tmp_diff_bfs_service_summary_devices WHERE campaign_3 IS NOT NULL
        UNION ALL
        SELECT 'campaign_4', campaign_4 FROM tmp_diff_bfs_service_summary_devices WHERE campaign_4 IS NOT NULL
        UNION ALL
        SELECT 'campaign_5', campaign_5 FROM tmp_diff_bfs_service_summary_devices WHERE campaign_5 IS NOT NULL
        UNION ALL
        SELECT 'plan', plan FROM tmp_diff_bfs_service_summary_devices WHERE plan IS NOT NULL
        UNION ALL
        SELECT 'call_discount_w_white', call_discount_w_white FROM tmp_diff_bfs_service_summary_devices WHERE call_discount_w_white IS NOT NULL
        UNION ALL
        SELECT 'breaking_contract_gold_annual_contract', breaking_contract_gold_annual_contract FROM tmp_diff_bfs_service_summary_devices WHERE breaking_contract_gold_annual_contract IS NOT NULL
        UNION ALL
        SELECT 's_basic_pack', s_basic_pack FROM tmp_diff_bfs_service_summary_devices WHERE s_basic_pack IS NOT NULL
        UNION ALL
        SELECT 'data_communication_basic_fee_4g', data_communication_basic_fee_4g FROM tmp_diff_bfs_service_summary_devices WHERE data_communication_basic_fee_4g IS NOT NULL
        UNION ALL
        SELECT 'basic_fee_5g', basic_fee_5g FROM tmp_diff_bfs_service_summary_devices WHERE basic_fee_5g IS NOT NULL
        UNION ALL
        SELECT 'packet_discount', packet_discount FROM tmp_diff_bfs_service_summary_devices WHERE packet_discount IS NOT NULL
        UNION ALL
        SELECT 'option_pack', option_pack FROM tmp_diff_bfs_service_summary_devices WHERE option_pack IS NOT NULL
        UNION ALL
        SELECT 'anshin_guarantee_pack', anshin_guarantee_pack FROM tmp_diff_bfs_service_summary_devices WHERE anshin_guarantee_pack IS NOT NULL
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
                        TRIM(normalize(COALESCE(category, ''), NFKC)),
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
                        TRIM(normalize(COALESCE(option, ''), NFKC)),
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
