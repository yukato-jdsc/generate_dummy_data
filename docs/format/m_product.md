# (Mars)商品

- マート名: `m_商品_all`
- CSVファイル名： `YYYYMMDD_DLV_OAI_MRS_ITEM.csv`, `YYYYMMDD_DLV_OAI_MRS_ITEM_diff.csv`
- 全量更新 or 差分更新: 全量更新
- 更新頻度: 日次
- データ数: 全件（122,802件）
- データ量: 219.76MB
- データ概要: 商品コード単位で商品に関する情報を保有。 M_商品 ：M_商品_ALLから最新フラグが「1」のデータのみ抽出

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | PK | 必須 | 説明 |
| --- | --- | --- | --- | --- | --- | --- |
| 商品コード | `itm_cd` | VARCHAR | 20 | ○ | ○ | - |
| 有効開始日 | `effective_dt_from` | VARCHAR | 8 | ○ | ○ | - |
| 有効開始時間 | `effective_tm_from` | VARCHAR | 6 | ○ | ○ | - |
| 有効終了日 | `effective_dt_to` | VARCHAR | 8 | － | ○ | - |
| 有効終了時間 | `effective_tm_to` | VARCHAR | 6 | － | ○ | - |
| 地域コード | `area_cd` | VARCHAR | 3 | － | － | - |
| 商品正式名称 | `long_nm` | VARCHAR | 600 | － | ○ | - |
| 商品カナ名称 | `kana_nm` | VARCHAR | 600 | － | ○ | - |
| 商品英語名称 | `eng_nm` | VARCHAR | 600 | － | － | - |
| 商品略称 | `short_nm` | VARCHAR | 300 | － | － | - |
| 商品細分類ID | `itm_lvl4_id` | VARCHAR | 10 | － | － | - |
| 商品細分類正式名称 | `lvl4_long_nm` | VARCHAR | 600 | － | － | - |
| 商品細分類カナ名称 | `lvl4_kana_nm` | VARCHAR | 600 | － | － | - |
| 商品細分類英語名称 | `lvl4_eng_nm` | VARCHAR | 600 | － | － | - |
| 商品小分類ID | `itm_lvl3_id` | VARCHAR | 10 | － | － | - |
| 商品小分類正式名称 | `lvl3_long_nm` | VARCHAR | 600 | － | － | - |
| 商品小分類カナ名称 | `lvl3_kana_nm` | VARCHAR | 600 | － | － | - |
| 商品小分類英語名称 | `lvl3_eng_nm` | VARCHAR | 600 | － | － | - |
| 商品中分類ID | `itm_lvl2_id` | VARCHAR | 10 | － | － | - |
| 商品中分類正式名称 | `lvl2_long_nm` | VARCHAR | 600 | － | － | - |
| 商品中分類カナ名称 | `lvl2_kana_nm` | VARCHAR | 600 | － | － | - |
| 商品中分類英語名称 | `lvl2_eng_nm` | VARCHAR | 600 | － | － | - |
| 商品大分類ID | `itm_lvl1_id` | VARCHAR | 10 | － | － | - |
| 商品大分類正式名称 | `itm_lvl1long_nm` | VARCHAR | 600 | － | － | - |
| 商品大分類カナ名称 | `itm_lvl1kana_nm` | VARCHAR | 600 | － | － | - |
| 商品大分類英語名称 | `itm_lvl1eng_nm` | VARCHAR | 600 | － | － | - |
| 個体管理タイプコード | `idv_mng_typ_cde` | VARCHAR | 2 | － | － | - |
| メーカーID | `maker_id` | VARCHAR | 10 | － | － | - |
| メーカー正式名称 | `maker_long_nm` | VARCHAR | 600 | － | － | - |
| メーカーカナ名称 | `maker_kana_nm` | VARCHAR | 600 | － | － | - |
| メーカー英語名称 | `maker_eng_nm` | VARCHAR | 600 | － | － | - |
| ブランドID | `brand_id` | VARCHAR | 10 | － | － | - |
| ブランド正式名称 | `brand_long_nm` | VARCHAR | 600 | － | － | - |
| ブランドコード | `brand_cd` | VARCHAR | 2 | － | － | - |
| ブランドカナ名称 | `brand_kana_nm` | VARCHAR | 600 | － | － | - |
| ブランド略称 | `brand_short_nm` | VARCHAR | 600 | － | － | - |
| ブランド英語名称 | `brand_eng_nm` | VARCHAR | 600 | － | － | - |
| janコード | `jan_cd` | VARCHAR | 13 | － | － | - |
| 商品色正式名称 | `color_nm` | VARCHAR | 300 | － | － | - |
| 商品色略称 | `color_short_nm` | VARCHAR | 120 | － | － | - |
| 標準色ID | `color_id` | DECIMAL | 10,0 | － | － | - |
| 標準色正式名称 | `color_long_nm` | VARCHAR | 600 | － | － | - |
| 標準色カナ名称 | `color_kana_nm` | VARCHAR | 600 | － | － | - |
| 標準色英語名称 | `color_eng_nm` | VARCHAR | 600 | － | － | - |
| 機種コード | `model_cd` | VARCHAR | 20 | － | ○ | - |
| 機種正式名称 | `model_long_nm` | VARCHAR | 600 | － | ○ | - |
| 手数料支払停止日 | `pay_stop_dt` | VARCHAR | 8 | － | － | - |
| MVNO識別ID | `carrier_id` | DECIMAL | 3,0 | － | － | - |
| MVNO識別略称2 | `short_nm2` | VARCHAR | 60 | － | － | - |
| 販売開始日 | `sale_dt_from` | VARCHAR | 8 | － | － | - |
| 販売終了日 | `sale_dt_to` | VARCHAR | 8 | － | － | - |
| 買い増し有効開始日 | `add_item_effective_dt_from` | VARCHAR | 8 | － | － | - |
| 買い増し有効終了日 | `add_item_effective_dt_to` | VARCHAR | 8 | － | － | - |
| cic商品コード | `cic_itm_cd` | VARCHAR | 3 | － | － | - |
| 生活必需品外フラグ | `not_ncssty_flg` | VARCHAR | 1 | － | － | - |
| サービス世代ID | `service_gen_id` | VARCHAR | 2 | － | － | - |
| サービス世代正式名称 | `service_gen_long_nm` | VARCHAR | 120 | － | － | - |
| 容量 | `capacity` | VARCHAR | 10 | － | － | - |
| 割賦審査上限chk対象flg | `allotment_maximum_chk_flg` | VARCHAR | 1 | － | － | - |
| opt品割賦販売適用flg | `option_allotment_flg` | VARCHAR | 1 | － | － | - |
| opt品割賦販売適用from | `option_allotment_dt_from` | VARCHAR | 8 | － | － | - |
| 売価 | `itm_prc` | DECIMAL | 10,0 | － | － | - |
| 端末区分 | `pdct_cfc_1_1` | VARCHAR | 1 | － | － | - |
| 端末区分正式名称 | `terminal_cfc_nm` | VARCHAR | 600 | － | － | - |
| 大分類 | `pdct_cfc_3_2` | VARCHAR | 2 | － | － | - |
| 大分類正式名称 | `div_l_nm` | VARCHAR | 600 | － | － | - |
| 中分類 | `pdct_cfc_6_2` | VARCHAR | 2 | － | － | - |
| 中分類正式名称 | `div_m_nm` | VARCHAR | 600 | － | － | - |
| 小分類 | `pdct_cfc_9_2` | VARCHAR | 2 | － | － | - |
| 小分類正式名称 | `div_s_nm` | VARCHAR | 600 | － | － | - |
| 機能フラグ | `func_flg` | VARCHAR | 50 | － | － | - |
| バンドルプラン識別id | `bundle_plan_id` | VARCHAR | 10 | － | － | - |
| バンドルプランnm | `bundle_plan_nm` | VARCHAR | 600 | － | － | - |
| チャージ額 | `charge_amt` | DECIMAL | 6,0 | － | － | - |
| ユニバーサル使用料 | `universal_amt` | DECIMAL | 4,0 | － | － | - |
| 利用有効期間 | `effective_dt_use` | DECIMAL | 5,0 | － | － | - |
| 物流商品コード | `logi_itm_cd` | VARCHAR | 15 | － | － | - |
| 数量金額管理区分 | `qty_prc_mng_cfc` | DECIMAL | 1,0 | － | － | - |
| 商品税分類コード | `itm_tax_cd` | DECIMAL | 1,0 | － | － | - |
| 物流商品税分類 | `logi_itm_tax_cd` | VARCHAR | 1 | － | － | - |
| 物流基本単位数量 | `logi_unit_num` | VARCHAR | 20 | － | － | - |
| 標準入数 | `standard_qty` | DECIMAL | 10,3 | － | － | - |
| 出荷時入数 | `ship_qty` | DECIMAL | 6,0 | － | － | - |
| 個装箱サイズ_縦(mm) | `size_d` | DECIMAL | 4,0 | － | － | - |
| 個装箱サイズ_横(mm) | `size_w` | DECIMAL | 4,0 | － | － | - |
| 個装箱サイズ_高さ(mm) | `size_h` | DECIMAL | 4,0 | － | － | - |
| 梱包財_紙重量(g) | `pack_mtr_paper_wgt` | DECIMAL | 7,0 | － | － | - |
| 梱包財_プラ重量(g) | `pack_mtr_plstc_wgt` | DECIMAL | 7,0 | － | － | - |
| 商品重量(g) | `itm_wgt` | DECIMAL | 7,0 | － | － | - |
| パレット積み付け数 | `palette_stack_num` | DECIMAL | 8,0 | － | － | - |
| 梱包仕様等 | `pack_spcf` | DECIMAL | 4,0 | － | － | - |
| MRP管理者コード | `mrpplanner_cd` | VARCHAR | 3 | － | － | - |
| 変換代表フラグ | `chg_def_flg` | VARCHAR | 1 | － | － | - |
| 検品用商品タイプコード | `ins_itm_typ_cd` | VARCHAR | 3 | － | － | - |
| 検品用商品タイプ正式名称 | `ins_itm_typ_long_nm` | VARCHAR | 600 | － | － | - |
| MODEL_ID | `model_id` | DECIMAL | 10,0 | － | － | - |
| ISMIタイプ | `imsi_typ` | VARCHAR | 2 | － | － | - |
| ISMIタイプ名称 | `imsi_typ_nm` | VARCHAR | 600 | － | － | - |
| 最新フラグ | `pickup_flg` | VARCHAR | 1 | － | ○ | 0 / 1 |
