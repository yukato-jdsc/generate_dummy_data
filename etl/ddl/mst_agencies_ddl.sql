CREATE TABLE mst_agencies (
    ordcstm_cd VARCHAR(20) NOT NULL,
    effective_dt_from VARCHAR(8) NOT NULL,
    effective_dt_to VARCHAR(8),
    long_nm VARCHAR(600),
    short_nm VARCHAR(120),
    area_cd VARCHAR(2),
    area_eng_cd VARCHAR(1),
    post_cd VARCHAR(10),
    pref_cd VARCHAR(2),
    pref_long_nm VARCHAR(48),
    city_cd VARCHAR(3),
    city_cd_long_nm VARCHAR(144),
    street_cd VARCHAR(3),
    street_cd_long_nm VARCHAR(216),
    add_nbr_cd VARCHAR(3),
    add_nbr_cd_long_nm VARCHAR(144),
    add_complement VARCHAR(360),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_mst_agencies PRIMARY KEY (ordcstm_cd, effective_dt_from)
);

COMMENT ON COLUMN mst_agencies.ordcstm_cd IS '取次店コード';

COMMENT ON COLUMN mst_agencies.effective_dt_from IS '有効開始日';

COMMENT ON COLUMN mst_agencies.effective_dt_to IS '有効終了日';

COMMENT ON COLUMN mst_agencies.long_nm IS '取次店正式名称';

COMMENT ON COLUMN mst_agencies.short_nm IS '取次店略称';

COMMENT ON COLUMN mst_agencies.area_cd IS '地域コード';

COMMENT ON COLUMN mst_agencies.area_eng_cd IS '地域英語コード';

COMMENT ON COLUMN mst_agencies.post_cd IS '取次店郵便番号';

COMMENT ON COLUMN mst_agencies.pref_cd IS '都道府県コード';

COMMENT ON COLUMN mst_agencies.pref_long_nm IS '都道府県漢字';

COMMENT ON COLUMN mst_agencies.city_cd IS '市区町村コード';

COMMENT ON COLUMN mst_agencies.city_cd_long_nm IS '市区町村漢字';

COMMENT ON COLUMN mst_agencies.street_cd IS '通称コード';

COMMENT ON COLUMN mst_agencies.street_cd_long_nm IS '通称漢字';

COMMENT ON COLUMN mst_agencies.add_nbr_cd IS '丁目コード';

COMMENT ON COLUMN mst_agencies.add_nbr_cd_long_nm IS '丁目漢字';

COMMENT ON COLUMN mst_agencies.add_complement IS '付帯住所';

COMMENT ON COLUMN mst_agencies.created_at IS '作成日時';

COMMENT ON COLUMN mst_agencies.updated_at IS '更新日時';
