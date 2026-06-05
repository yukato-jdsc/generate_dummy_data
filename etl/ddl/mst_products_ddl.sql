CREATE TABLE mst_products (
    itm_cd VARCHAR(20) NOT NULL,
    effective_dt_from VARCHAR(8) NOT NULL,
    effective_tm_from VARCHAR(6) NOT NULL,
    effective_dt_to VARCHAR(8) NOT NULL,
    effective_tm_to VARCHAR(6) NOT NULL,
    long_nm VARCHAR(600) NOT NULL,
    itm_lvl2_id VARCHAR(10) NOT NULL,
    lvl2_long_nm VARCHAR(600) NOT NULL,
    brand_long_nm VARCHAR(600),
    color_nm VARCHAR(300),
    model_cd VARCHAR(20),
    model_long_nm VARCHAR(600),
    ins_itm_typ_cd VARCHAR(3),
    imsi_typ VARCHAR(2),
    imsi_typ_nm VARCHAR(600),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_mst_products PRIMARY KEY (
        itm_cd,
        effective_dt_from,
        effective_tm_from
    )
);

COMMENT ON COLUMN mst_products.itm_cd IS '商品コード';

COMMENT ON COLUMN mst_products.effective_dt_from IS '有効開始日';

COMMENT ON COLUMN mst_products.effective_tm_from IS '有効開始時間';

COMMENT ON COLUMN mst_products.effective_dt_to IS '有効終了日';

COMMENT ON COLUMN mst_products.effective_tm_to IS '有効終了時間';

COMMENT ON COLUMN mst_products.long_nm IS '商品正式名称';

COMMENT ON COLUMN mst_products.itm_lvl2_id IS '商品中分類ID';

COMMENT ON COLUMN mst_products.lvl2_long_nm IS '商品中分類正式名称';

COMMENT ON COLUMN mst_products.brand_long_nm IS 'ブランド正式名称';

COMMENT ON COLUMN mst_products.color_nm IS '商品色正式名称';

COMMENT ON COLUMN mst_products.model_cd IS '機種コード';

COMMENT ON COLUMN mst_products.model_long_nm IS '機種正式名称';

COMMENT ON COLUMN mst_products.ins_itm_typ_cd IS '検品用商品タイプコード';

COMMENT ON COLUMN mst_products.imsi_typ IS 'IMSIタイプ';

COMMENT ON COLUMN mst_products.imsi_typ_nm IS 'IMSIタイプ名称';

COMMENT ON COLUMN mst_products.created_at IS '作成日時';

COMMENT ON COLUMN mst_products.updated_at IS '更新日時';
