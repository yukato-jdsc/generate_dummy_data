CREATE OR REPLACE PROCEDURE sp_init_tmp_compass_sales_approval()
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS tmp_diff_compass_sales_approval (
      approval_id TEXT,
      approval_title TEXT,
      contact_name TEXT,
      contact_person_phone_number TEXT,
      project_name TEXT,
      company_name TEXT,
      company_id TEXT,
      contract_period_months TEXT,
      contract_start_date TEXT,
      proposal_type TEXT,
      project_summary_1 TEXT,
      project_summary_2 TEXT,
      automatic_renewal TEXT,
      compass_related_approval TEXT
    );
    TRUNCATE TABLE tmp_diff_compass_sales_approval;
END;
$$;
