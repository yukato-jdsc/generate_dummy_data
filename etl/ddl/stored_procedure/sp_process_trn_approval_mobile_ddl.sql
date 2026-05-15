-- ADFでUPSERTに使用するための処理済みデータを保存するステージングテーブル
CREATE TABLE IF NOT EXISTS sp_output_trn_approval_mobile_upsert (
    approval_id varchar(10) NOT NULL,
    company_id varchar(10) NOT NULL,
    company_name varchar(100) NOT NULL,
    operation_type varchar(18) NOT NULL,
    approval_title text NOT NULL,
    name_pic varchar(100) NULL,
    phone_number_pic varchar(11) NULL,
    case_title text NOT NULL,
    case_description text NOT NULL,
    expected_contract_start_date date NULL,
    contract_period smallint NULL,
    auto_extension_flg varchar(2) NOT NULL,
    related_approval_ids varchar[] NULL,
    created_at timestamp(6) NOT NULL,
    updated_at timestamp(6) NOT NULL,
    CONSTRAINT pk_sp_output_trn_approval_mobile PRIMARY KEY (approval_id)
);

CREATE OR REPLACE PROCEDURE sp_process_trn_approval_mobile()
LANGUAGE plpgsql
AS $$
DECLARE
    v_now TIMESTAMP := NOW();
BEGIN
    -- 処理開始前に出力テーブルをクリア
    TRUNCATE TABLE sp_output_trn_approval_mobile_upsert;

    -- UPSERTデータを処理する
    INSERT INTO sp_output_trn_approval_mobile_upsert (
        approval_id,
        company_id,
        company_name,
        operation_type,
        approval_title,
        name_pic,
        phone_number_pic,
        case_title,
        case_description,
        expected_contract_start_date,
        contract_period,
        auto_extension_flg,
        related_approval_ids,
        created_at,
        updated_at
    )
    SELECT DISTINCT ON (approval_id)
        LEFT(COALESCE(approval_id::text, ''), 10) AS approval_id,
        LEFT(COALESCE(company_id::text, ''), 10) AS company_id,
        LEFT(COALESCE(company_name::text, ''), 100) AS company_name,
        LEFT(COALESCE(proposal_type::text, ''), 18) AS operation_type,
        COALESCE(approval_title::text, '') AS approval_title,
        LEFT(COALESCE(contact_name::text, ''), 100) AS name_pic,
        LEFT(REPLACE(COALESCE(contact_person_phone_number::text, ''), '-', ''), 11) AS phone_number_pic,
        COALESCE(project_name::text, '') AS case_title,
        COALESCE(project_summary_1::text, '') || COALESCE(project_summary_2::text, '') AS case_description,
        NULLIF(TRIM(contract_start_date::text), '')::date AS expected_contract_start_date,
        NULLIF(TRIM(contract_period_months::text), '')::smallint AS contract_period,
        LEFT(COALESCE(automatic_renewal::text, ''), 2) AS auto_extension_flg,
        CASE
            WHEN compass_related_approval IS NOT NULL AND compass_related_approval::text != ''
            THEN string_to_array(compass_related_approval::text, ',')
            ELSE NULL
        END AS related_approval_ids,
        v_now AS created_at,
        v_now AS updated_at
    FROM tmp_diff_compass_sales_approval
    ORDER BY approval_id;

END;
$$;
