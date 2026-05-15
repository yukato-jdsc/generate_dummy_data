CREATE OR REPLACE PROCEDURE sp_init_tmp_bfs_service_summary_accessories()
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS tmp_diff_bfs_service_summary_accessories (
    entry_number TEXT,
    summary_number TEXT,
    serial_number_accessories TEXT,
    product_code TEXT,
    manufacturer TEXT,
    product_name TEXT,
    color_1 TEXT,
    quantity_1 TEXT,
    color_2 TEXT,
    quantity_2 TEXT,
    color_3 TEXT,
    quantity_3 TEXT,
    color_4 TEXT,
    quantity_4 TEXT,
    color_5 TEXT,
    quantity_5 TEXT,
    standard_price_of_accessories TEXT,
    provision_fee TEXT,
    usage_points TEXT,
    cost TEXT,
    linked_summary_number TEXT,
    cost_contingency TEXT
    );
    TRUNCATE TABLE tmp_diff_bfs_service_summary_accessories;
END;
$$;
