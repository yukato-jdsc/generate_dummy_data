CREATE TABLE IF NOT EXISTS mst_agencies (
    agency_code VARCHAR(40),
    effective_start_date VARCHAR(16),
    effective_end_date VARCHAR(16),
    agency_name VARCHAR(1200),
    updated_at timestamp(6) NOT NULL
)
