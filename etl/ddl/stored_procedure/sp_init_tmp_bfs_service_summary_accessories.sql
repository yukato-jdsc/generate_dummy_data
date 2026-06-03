CREATE OR REPLACE PROCEDURE sp_init_tmp_bfs_service_summary_accessories()
LANGUAGE PLPGSQL AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS tmp_diff_bfs_service_summary_accessories (
    entry_no varchar(18),
    attach_sm_id varchar(12),
    serial_attach_flg_nm varchar(765),
    itm_cd varchar(15),
    brand_nm varchar(600),
    itm_nm varchar(300),
    color1 varchar(300),
    num1 numeric(6,0),
    color2 varchar(300),
    num2 numeric(6,0),
    color3 varchar(300),
    num3 numeric(6,0),
    color4 varchar(300),
    num4 numeric(6,0),
    color5 varchar(300),
    num5 numeric(6,0),
    base_price numeric(10,0),
    offered_price numeric(10,0),
    use_point numeric(6,0),
    trade_price numeric(11,0),
    linked_svcsm_id varchar(30),
    attach_reserve_base_price numeric(8,0),
    regist_date varchar(20),
    update_date varchar(20),
    industrial_company_cd varchar(4),
    load_day varchar(8),
    CONSTRAINT pk_tmp_diff_bfs_service_summary_accessories PRIMARY KEY (entry_no, attach_sm_id)
    );
    TRUNCATE TABLE tmp_diff_bfs_service_summary_accessories;
END;
$$;
