-- ADFでUPSERTに使用するための処理済みデータを保存するステージングテーブル
CREATE TABLE IF NOT EXISTS sp_output_trn_bfs_entries_upsert (
    bfs_entry_id varchar(20) NOT NULL,
    approval_id varchar(10) NOT NULL,
    company_id varchar(10) NOT NULL,
    initial_rental_period smallint NOT NULL,
    billing_number varchar(12) NOT NULL,
    contractor_number varchar(12) NOT NULL,
    pic_name_contract varchar(100) NULL,
    pic_name_kana_contract varchar(100) NULL,
    dep_name_contract varchar(100) NULL,
    dep_name_delivery varchar(100) NULL,
    agency_code_1 varchar(54) NULL,
    agency_name varchar(2295) NULL,
    last_4_digit_display varchar(10) NULL,
    invoice_delivery_route varchar(10) NULL,
    accessory_fee_payment_method varchar(900) NULL,
    accessory_fee_billing_category varchar(900) NULL,
    accessory_fee_combined_type varchar(900) NULL,
    rental_used_start_date varchar(60) NULL,
    rental_used_period_months varchar(6) NULL,
    maximum_number_of_lines_applicable_to_the_special_agreement numeric(10,0) NULL,
    stakeholder_1 varchar(2295) NULL,
    stakeholder_2 varchar(2295) NULL,
    stakeholder_3 varchar(2295) NULL,
    stakeholder_4 varchar(2295) NULL,
    stakeholder_5 varchar(2295) NULL,
    stakeholder_6 varchar(2295) NULL,
    stakeholder_7 varchar(2295) NULL,
    stakeholder_8 varchar(2295) NULL,
    stakeholder_9 varchar(2295) NULL,
    stakeholder_10 varchar(2295) NULL,
    sales_representative varchar(2295) NULL,
    telephone_number varchar(39) NULL,
    department_name varchar(2133) NULL,
    identity_verification_implementer_code varchar(30) NULL,
    receptionist_code varchar(30) NULL,
    campaign json NOT NULL,
    options json NOT NULL,
    rental_options json NOT NULL,
    discount_devices json NOT NULL,
    discount_services json NOT NULL,
    accessories json NOT NULL,
    created_at timestamp(6) NOT NULL,
    updated_at timestamp(6) NOT NULL,
    CONSTRAINT pk_sp_output_trn_bfs_entries_upsert PRIMARY KEY (bfs_entry_id)
);

-- ADFでDELETEに使用するための処理済みデータを保存するステージングテーブル
-- 削除操作用の出力テーブル (ADFが読み取る)
CREATE TABLE IF NOT EXISTS sp_output_trn_bfs_entries_delete (
    bfs_entry_id varchar(20) NOT NULL,
    CONSTRAINT pk_sp_output_trn_bfs_entries_delete PRIMARY KEY (bfs_entry_id)
);

CREATE OR REPLACE PROCEDURE sp_process_trn_bfs_entries()
LANGUAGE plpgsql
AS $$
DECLARE
    v_now TIMESTAMP := NOW();
BEGIN
    -- 処理開始前に出力テーブルをクリア
    TRUNCATE TABLE sp_output_trn_bfs_entries_upsert;
    TRUNCATE TABLE sp_output_trn_bfs_entries_delete;

    -- ステップ1: entry_numberごとに最初のデバイス行を取得する
    CREATE TEMP TABLE tmp_first_device AS
    SELECT DISTINCT ON (entry_number) *
    FROM tmp_diff_bfs_service_summary_devices
    ORDER BY entry_number, summary_number;

    -- ステップ2: entry_numberごとにアクセサリのJSONを構築する
    -- 各アクセサリ行をcolors配列を含むJSONオブジェクトに変換する
    CREATE TEMP TABLE tmp_accessories_json AS
    SELECT
        entry_number,
        COALESCE(
            json_agg(
                json_build_object(
                    'product_code', COALESCE(TRIM(product_code::text), ''),
                    'manufacturer', COALESCE(TRIM(manufacturer::text), ''),
                    'product_name', COALESCE(TRIM(product_name::text), ''),
                    'colors', (
                        SELECT COALESCE(json_agg(
                            json_build_object('color', c.color, 'quantity', c.quantity)
                        ), '[]'::json)
                        FROM (
                            VALUES
                                (TRIM(COALESCE(a.color_1::text, '')), TRIM(COALESCE(a.quantity_1::text, ''))),
                                (TRIM(COALESCE(a.color_2::text, '')), TRIM(COALESCE(a.quantity_2::text, ''))),
                                (TRIM(COALESCE(a.color_3::text, '')), TRIM(COALESCE(a.quantity_3::text, ''))),
                                (TRIM(COALESCE(a.color_4::text, '')), TRIM(COALESCE(a.quantity_4::text, ''))),
                                (TRIM(COALESCE(a.color_5::text, '')), TRIM(COALESCE(a.quantity_5::text, '')))
                        ) AS c(color, quantity)
                        WHERE c.color != '' OR c.quantity != ''
                    )
                )
            ),
            '[]'::json
        ) AS accessories_json
    FROM tmp_diff_bfs_service_summary_accessories a
    GROUP BY entry_number;

    -- ステップ3: UPSERTデータを処理する (diff_type = 'I' または 'U')
    INSERT INTO sp_output_trn_bfs_entries_upsert (
        bfs_entry_id,
        approval_id,
        company_id,
        initial_rental_period,
        billing_number,
        contractor_number,
        pic_name_contract,
        pic_name_kana_contract,
        dep_name_contract,
        dep_name_delivery,
        agency_code_1,
        agency_name,
        last_4_digit_display,
        invoice_delivery_route,
        accessory_fee_payment_method,
        accessory_fee_billing_category,
        accessory_fee_combined_type,
        rental_used_start_date,
        rental_used_period_months,
        maximum_number_of_lines_applicable_to_the_special_agreement,
        stakeholder_1,
        stakeholder_2,
        stakeholder_3,
        stakeholder_4,
        stakeholder_5,
        stakeholder_6,
        stakeholder_7,
        stakeholder_8,
        stakeholder_9,
        stakeholder_10,
        sales_representative,
        telephone_number,
        department_name,
        identity_verification_implementer_code,
        receptionist_code,
        campaign,
        options,
        rental_options,
        discount_devices,
        discount_services,
        accessories,
        created_at,
        updated_at
    )
    SELECT
        e.entry_number AS bfs_entry_id,
        COALESCE(e.approval_number_1::text, '') AS approval_id,
        COALESCE(e.unified_company_code::text, '') AS company_id,
        COALESCE(NULLIF(TRIM(e.initial_rental_period::text), '')::smallint, 0) AS initial_rental_period,
        COALESCE(e.billing_number::text, '') AS billing_number,
        COALESCE(e.contractor_number::text, '') AS contractor_number,
        e.contact_person_name::text AS pic_name_contract,
        e.contact_person_name_katakana::text AS pic_name_kana_contract,
        e.contact_person_department::text AS dep_name_contract,
        e.billing_department_name::text AS dep_name_delivery,
        LEFT(COALESCE(e.agency_code_1::text, ''), 54) AS agency_code_1,
        LEFT(COALESCE(e.agency_name::text, ''), 2295) AS agency_name,
        LEFT(COALESCE(e.last_4_digits::text, ''), 10) AS last_4_digit_display,
        LEFT(COALESCE(e.invoice_delivery::text, ''), 10) AS invoice_delivery_route,

        LEFT(COALESCE(e.accessory_fee_payment_method::text, ''), 900) AS accessory_fee_payment_method,
        LEFT(COALESCE(e.accessory_fee_billing_category::text, ''), 900) AS accessory_fee_billing_category,
        LEFT(COALESCE(e.accessory_fee_combined_type::text, ''), 900) AS accessory_fee_combined_type,
        LEFT(COALESCE(e.rental_used_start_date::text, ''), 60) AS rental_used_start_date,
        LEFT(COALESCE(e.rental_used_period_months::text, ''), 6) AS rental_used_period_months,
        NULLIF(TRIM(e.maximum_number_of_lines_applicable_to_the_special_agreement::text), '')::numeric(10,0) AS maximum_number_of_lines_applicable_to_the_special_agreement,
        LEFT(COALESCE(e.stakeholder_1::text, ''), 2295) AS stakeholder_1,
        LEFT(COALESCE(e.stakeholder_2::text, ''), 2295) AS stakeholder_2,
        LEFT(COALESCE(e.stakeholder_3::text, ''), 2295) AS stakeholder_3,
        LEFT(COALESCE(e.stakeholder_4::text, ''), 2295) AS stakeholder_4,
        LEFT(COALESCE(e.stakeholder_5::text, ''), 2295) AS stakeholder_5,
        LEFT(COALESCE(e.stakeholder_6::text, ''), 2295) AS stakeholder_6,
        LEFT(COALESCE(e.stakeholder_7::text, ''), 2295) AS stakeholder_7,
        LEFT(COALESCE(e.stakeholder_8::text, ''), 2295) AS stakeholder_8,
        LEFT(COALESCE(e.stakeholder_9::text, ''), 2295) AS stakeholder_9,
        LEFT(COALESCE(e.stakeholder_10::text, ''), 2295) AS stakeholder_10,
        LEFT(COALESCE(e.sales_representative_1::text, ''), 2295) AS sales_representative,
        LEFT(COALESCE(e.telephone_number::text, ''), 39) AS telephone_number,
        LEFT(COALESCE(e.department_name::text, ''), 2133) AS department_name,
        LEFT(COALESCE(e.identity_verification_implementer_code::text, ''), 30) AS identity_verification_implementer_code,
        LEFT(COALESCE(e.receptionist_code::text, ''), 30) AS receptionist_code,

        -- campaign: campaign_1-5の空でない値からJSON配列を構築する
        COALESCE(
            (SELECT json_agg(val)
             FROM (
                VALUES
                    (TRIM(COALESCE(d.campaign_1::text, ''))),
                    (TRIM(COALESCE(d.campaign_2::text, ''))),
                    (TRIM(COALESCE(d.campaign_3::text, ''))),
                    (TRIM(COALESCE(d.campaign_4::text, ''))),
                    (TRIM(COALESCE(d.campaign_5::text, '')))
             ) AS t(val)
             WHERE val != ''
            ),
            '[]'::json
        ) AS campaign,

        -- options: option_category/service 1-10から{category, service}のJSON配列を構築する
        COALESCE(
            (SELECT json_agg(json_build_object('category', cat, 'service', svc))
             FROM (
                VALUES
                    (TRIM(COALESCE(d.option_category_1::text, '')), TRIM(COALESCE(d.option_service_1::text, ''))),
                    (TRIM(COALESCE(d.option_category_2::text, '')), TRIM(COALESCE(d.option_service_2::text, ''))),
                    (TRIM(COALESCE(d.option_category_3::text, '')), TRIM(COALESCE(d.option_service_3::text, ''))),
                    (TRIM(COALESCE(d.option_category_4::text, '')), TRIM(COALESCE(d.option_service_4::text, ''))),
                    (TRIM(COALESCE(d.option_category_5::text, '')), TRIM(COALESCE(d.option_service_5::text, ''))),
                    (TRIM(COALESCE(d.option_category_6::text, '')), TRIM(COALESCE(d.option_service_6::text, ''))),
                    (TRIM(COALESCE(d.option_category_7::text, '')), TRIM(COALESCE(d.option_service_7::text, ''))),
                    (TRIM(COALESCE(d.option_category_8::text, '')), TRIM(COALESCE(d.option_service_8::text, ''))),
                    (TRIM(COALESCE(d.option_category_9::text, '')), TRIM(COALESCE(d.option_service_9::text, ''))),
                    (TRIM(COALESCE(d.option_category_10::text, '')), TRIM(COALESCE(d.option_service_10::text, '')))
             ) AS t(cat, svc)
             WHERE cat != '' OR svc != ''
            ),
            '[]'::json
        ) AS options,

        -- rental_options: rntopt_category/plan 1-10から{category, service}のJSON配列を構築する
        COALESCE(
            (SELECT json_agg(json_build_object('category', cat, 'service', svc))
             FROM (
                VALUES
                    (TRIM(COALESCE(d.rntopt_category_1::text, '')), TRIM(COALESCE(d.rntopt_plan_1::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_2::text, '')), TRIM(COALESCE(d.rntopt_plan_2::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_3::text, '')), TRIM(COALESCE(d.rntopt_plan_3::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_4::text, '')), TRIM(COALESCE(d.rntopt_plan_4::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_5::text, '')), TRIM(COALESCE(d.rntopt_plan_5::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_6::text, '')), TRIM(COALESCE(d.rntopt_plan_6::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_7::text, '')), TRIM(COALESCE(d.rntopt_plan_7::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_8::text, '')), TRIM(COALESCE(d.rntopt_plan_8::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_9::text, '')), TRIM(COALESCE(d.rntopt_plan_9::text, ''))),
                    (TRIM(COALESCE(d.rntopt_category_10::text, '')), TRIM(COALESCE(d.rntopt_plan_10::text, '')))
             ) AS t(cat, svc)
             WHERE cat != '' OR svc != ''
            ),
            '[]'::json
        ) AS rental_options,

        -- discount_devices: relative_pd_category/name 1-10から{category, name}のJSON配列を構築する
        COALESCE(
            (SELECT json_agg(json_build_object('category', cat, 'name', nm))
             FROM (
                VALUES
                    (TRIM(COALESCE(d.relative_pd_category_1::text, '')), TRIM(COALESCE(d.relative_pd_name_1::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_2::text, '')), TRIM(COALESCE(d.relative_pd_name_2::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_3::text, '')), TRIM(COALESCE(d.relative_pd_name_3::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_4::text, '')), TRIM(COALESCE(d.relative_pd_name_4::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_5::text, '')), TRIM(COALESCE(d.relative_pd_name_5::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_6::text, '')), TRIM(COALESCE(d.relative_pd_name_6::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_7::text, '')), TRIM(COALESCE(d.relative_pd_name_7::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_8::text, '')), TRIM(COALESCE(d.relative_pd_name_8::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_9::text, '')), TRIM(COALESCE(d.relative_pd_name_9::text, ''))),
                    (TRIM(COALESCE(d.relative_pd_category_10::text, '')), TRIM(COALESCE(d.relative_pd_name_10::text, '')))
             ) AS t(cat, nm)
             WHERE cat != '' OR nm != ''
            ),
            '[]'::json
        ) AS discount_devices,

        -- discount_services: relative_other_pd_category/name 1-5から{category, name}のJSON配列を構築する
        COALESCE(
            (SELECT json_agg(json_build_object('category', cat, 'name', nm))
             FROM (
                VALUES
                    (TRIM(COALESCE(d.relative_other_pd_category_1::text, '')), TRIM(COALESCE(d.relative_other_pd_name_1::text, ''))),
                    (TRIM(COALESCE(d.relative_other_pd_category_2::text, '')), TRIM(COALESCE(d.relative_other_pd_name_2::text, ''))),
                    (TRIM(COALESCE(d.relative_other_pd_category_3::text, '')), TRIM(COALESCE(d.relative_other_pd_name_3::text, ''))),
                    (TRIM(COALESCE(d.relative_other_pd_category_4::text, '')), TRIM(COALESCE(d.relative_other_pd_name_4::text, ''))),
                    (TRIM(COALESCE(d.relative_other_pd_category_5::text, '')), TRIM(COALESCE(d.relative_other_pd_name_5::text, '')))
             ) AS t(cat, nm)
             WHERE cat != '' OR nm != ''
            ),
            '[]'::json
        ) AS discount_services,

        -- accessories: 事前構築済みのJSONから取得する
        COALESCE(acc.accessories_json, '[]'::json) AS accessories,

        v_now AS created_at,
        v_now AS updated_at

    FROM tmp_diff_bfs_entry_informations e
    LEFT JOIN tmp_first_device d ON e.entry_number = d.entry_number
    LEFT JOIN tmp_accessories_json acc ON e.entry_number = acc.entry_number
    WHERE e.diff_type IN ('I', 'U')
    ON CONFLICT (bfs_entry_id) DO UPDATE SET
        approval_id = EXCLUDED.approval_id,
        company_id = EXCLUDED.company_id,
        initial_rental_period = EXCLUDED.initial_rental_period,
        billing_number = EXCLUDED.billing_number,
        contractor_number = EXCLUDED.contractor_number,
        pic_name_contract = EXCLUDED.pic_name_contract,
        pic_name_kana_contract = EXCLUDED.pic_name_kana_contract,
        dep_name_contract = EXCLUDED.dep_name_contract,
        dep_name_delivery = EXCLUDED.dep_name_delivery,
        last_4_digit_display = EXCLUDED.last_4_digit_display,
        invoice_delivery_route = EXCLUDED.invoice_delivery_route,
        accessory_fee_payment_method = EXCLUDED.accessory_fee_payment_method,
        accessory_fee_billing_category = EXCLUDED.accessory_fee_billing_category,
        accessory_fee_combined_type = EXCLUDED.accessory_fee_combined_type,
        rental_used_start_date = EXCLUDED.rental_used_start_date,
        rental_used_period_months = EXCLUDED.rental_used_period_months,
        maximum_number_of_lines_applicable_to_the_special_agreement = EXCLUDED.maximum_number_of_lines_applicable_to_the_special_agreement,
        stakeholder_1 = EXCLUDED.stakeholder_1,
        stakeholder_2 = EXCLUDED.stakeholder_2,
        stakeholder_3 = EXCLUDED.stakeholder_3,
        stakeholder_4 = EXCLUDED.stakeholder_4,
        stakeholder_5 = EXCLUDED.stakeholder_5,
        stakeholder_6 = EXCLUDED.stakeholder_6,
        stakeholder_7 = EXCLUDED.stakeholder_7,
        stakeholder_8 = EXCLUDED.stakeholder_8,
        stakeholder_9 = EXCLUDED.stakeholder_9,
        stakeholder_10 = EXCLUDED.stakeholder_10,
        sales_representative = EXCLUDED.sales_representative,
        telephone_number = EXCLUDED.telephone_number,
        department_name = EXCLUDED.department_name,
        identity_verification_implementer_code = EXCLUDED.identity_verification_implementer_code,
        receptionist_code = EXCLUDED.receptionist_code,
        campaign = EXCLUDED.campaign,
        options = EXCLUDED.options,
        rental_options = EXCLUDED.rental_options,
        discount_devices = EXCLUDED.discount_devices,
        discount_services = EXCLUDED.discount_services,
        accessories = EXCLUDED.accessories,
        updated_at = EXCLUDED.updated_at;

    -- ステップ4: 削除データを処理する (diff_type = 'D')
    INSERT INTO sp_output_trn_bfs_entries_delete (bfs_entry_id)
    SELECT DISTINCT entry_number::text
    FROM tmp_diff_bfs_entry_informations
    WHERE diff_type = 'D'
      AND entry_number IS NOT NULL;

    -- 一時テーブルを削除する
    DROP TABLE IF EXISTS tmp_first_device;
    DROP TABLE IF EXISTS tmp_accessories_json;

END;
$$;
