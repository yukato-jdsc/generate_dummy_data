CREATE TABLE IF NOT EXISTS mst_products (
    product_code VARCHAR(40),
    effective_start_date VARCHAR(16),
    effective_start_time VARCHAR(12),
    effective_end_date VARCHAR(16),
    effective_end_time VARCHAR(12),
    product_official_name VARCHAR(1200),
    product_middle_category_official_name VARCHAR(1200),
    brand_official_name VARCHAR(1200),
    product_color_official_name VARCHAR(600),
    model_code VARCHAR(40),
    model_official_name VARCHAR(1200),
    imsi_type VARCHAR(4),
    imsi_type_official_name VARCHAR(1200)
);
