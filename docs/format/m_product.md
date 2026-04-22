# (Mars)商品

- マート名: `m_商品`
- テーブル名: `m_product_all.csv`
- 全量更新 or 差分更新: 全量更新
- 更新頻度: 日次
- データ数: 全件（122,802件）
- データ量: 219.76MB
- データ概要: 商品コード単位で商品に関する情報を保有。 M_商品 ：M_商品_ALLから最新フラグが「1」のデータのみ抽出

## カラム定義

| SEQ | 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |
| --- | --- | --- | --- | --- | --- | --- |
|  | 1 | 商品コード | `product_code` | VARCHAR | 40 | － | - |
|  | 2 | 有効開始日 | `validity_start_date` | VARCHAR | 16 | － | - |
|  | 3 | 有効開始時間 | `validity_start_time` | VARCHAR | 12 | － | - |
|  | 4 | 有効終了日 | `validity_end_date` | VARCHAR | 16 | － | - |
|  | 5 | 有効終了時間 | `validity_end_time` | VARCHAR | 12 | － | - |
|  | 6 | 地域コード | `area_code` | VARCHAR | 6 | － | - |
|  | 7 | 商品正式名称 | `product_official_name` | VARCHAR | 1200 | － | - |
|  | 8 | 商品カナ名称 | `product_name_in_kana` | VARCHAR | 1200 | － | - |
|  | 9 | 商品英語名称 | `product_name_in_english` | VARCHAR | 1200 | － | - |
|  | 10 | 商品略称 | `product_abbreviation` | VARCHAR | 600 | － | - |
|  | 11 | 商品細分類id | `product_subcategory_id` | VARCHAR | 20 | － | - |
|  | 12 | 商品細分類正式名称 | `product_subcategory_official_name` | VARCHAR | 1200 | － | - |
|  | 13 | 商品細分類カナ名称 | `product_subcategory_kana` | VARCHAR | 1200 | － | - |
|  | 14 | 商品細分類英語名称 | `product_subcategory_english_name` | VARCHAR | 1200 | － | - |
|  | 15 | 商品小分類id | `product_small_category_id` | VARCHAR | 20 | － | - |
|  | 16 | 商品小分類正式名称 | `product_small_category_official_name` | VARCHAR | 1200 | － | - |
|  | 17 | 商品小分類カナ名称 | `product_small_category_kana` | VARCHAR | 1200 | － | - |
|  | 18 | 商品小分類英語名称 | `product_small_category_english_name` | VARCHAR | 1200 | － | - |
|  | 19 | 商品中分類id | `product_middle_category_id` | VARCHAR | 20 | － | - |
|  | 20 | 商品中分類正式名称 | `product_middle_category_official_name` | VARCHAR | 1200 | － | - |
|  | 21 | 商品中分類カナ名称 | `product_middle_category_kana` | VARCHAR | 1200 | － | - |
|  | 22 | 商品中分類英語名称 | `product_middle_category_english_name` | VARCHAR | 1200 | － | - |
|  | 23 | 商品大分類id | `product_major_category_id` | VARCHAR | 20 | － | - |
|  | 24 | 商品大分類正式名称 | `product_major_category_official_name` | VARCHAR | 1200 | － | - |
|  | 25 | 商品大分類カナ名称 | `product_major_category_kana` | VARCHAR | 1200 | － | - |
|  | 26 | 商品大分類英語名称 | `product_major_category_english_name` | VARCHAR | 1200 | － | - |
|  | 27 | 個体管理タイプコード | `individual_management_type_code` | VARCHAR | 4 | － | - |
|  | 28 | メーカーid | `manufacturer_id` | VARCHAR | 20 | － | - |
|  | 29 | メーカー正式名称 | `manufacturer_official_name` | VARCHAR | 1200 | － | - |
|  | 30 | メーカーカナ名称 | `manufacturer_name_in_kana` | VARCHAR | 1200 | － | - |
|  | 31 | メーカー英語名称 | `manufacturer_name_in_english` | VARCHAR | 1200 | － | - |
|  | 32 | ブランドid | `brand_id` | VARCHAR | 20 | － | - |
|  | 33 | ブランド正式名称 | `brand_official_name` | VARCHAR | 1200 | － | - |
|  | 34 | ブランドコード | `brand_code` | VARCHAR | 4 | － | - |
|  | 35 | ブランドカナ名称 | `brand_name_in_kana` | VARCHAR | 1200 | － | - |
|  | 36 | ブランド略称 | `brand_abbreviation` | VARCHAR | 1200 | － | - |
|  | 37 | ブランド英語名称 | `brand_name_in_english` | VARCHAR | 1200 | － | - |
|  | 38 | janコード | `jan_code` | VARCHAR | 26 | － | - |
|  | 39 | 商品色正式名称 | `product_color_official_name` | VARCHAR | 600 | － | - |
|  | 40 | 商品色略称 | `product_color_abbreviation` | VARCHAR | 240 | － | - |
|  | 41 | 標準色id | `standard_color_id` | DECIMAL | 10,0 | － | - |
|  | 42 | 標準色正式名称 | `standard_color_official_name` | VARCHAR | 1200 | － | - |
|  | 43 | 標準色カナ名称 | `standard_color_name_in_kana` | VARCHAR | 1200 | － | - |
|  | 44 | 標準色英語名称 | `standard_color_name_in_english` | VARCHAR | 1200 | － | - |
|  | 45 | 機種コード | `model_code` | VARCHAR | 40 | － | - |
|  | 46 | 機種正式名称 | `model_official_name` | VARCHAR | 1200 | － | - |
|  | 47 | 手数料支払停止日 | `fee_payment_stop_date` | VARCHAR | 16 | － | - |
|  | 48 | mvno識別id | `mvno_identification_id` | DECIMAL | 10,0 | － | - |
|  | 49 | mvno識別略称2 | `mvno_identification_abbreviation_2` | VARCHAR | 120 | － | - |
|  | 50 | 販売開始日 | `sales_start_date` | VARCHAR | 16 | － | - |
|  | 51 | 販売終了日 | `sales_end_date` | VARCHAR | 16 | － | - |
|  | 52 | 買い増し有効開始日 | `additional_purchase_validity_start_date` | VARCHAR | 16 | － | - |
|  | 53 | 買い増し有効終了日 | `additional_purchase_validity_end_date` | VARCHAR | 16 | － | - |
|  | 54 | cic商品コード | `cic_product_code` | VARCHAR | 6 | － | - |
|  | 55 | 生活必需品外フラグ | `non_essential_flag` | VARCHAR | 2 | － | - |
|  | 56 | サービス世代id | `service_generation_id` | VARCHAR | 4 | － | - |
|  | 57 | サービス世代正式名称 | `service_generation_official_name` | VARCHAR | 240 | － | - |
|  | 58 | 容量 | `capacity` | VARCHAR | 20 | － | - |
|  | 59 | 割賦審査上限chk対象flg | `installment_review_limit_chk_target_flg` | VARCHAR | 2 | － | - |
|  | 60 | opt品割賦販売適用flg | `opt_installment_sales_applicable_flg` | VARCHAR | 2 | － | - |
|  | 61 | opt品割賦販売適用from | `opt_installment_sales_applicable_from` | VARCHAR | 16 | － | - |
|  | 62 | 売価 | `sales_price` | DECIMAL | 10,0 | － | - |
|  | 63 | 端末区分 | `device_category` | VARCHAR | 2 | － | - |
|  | 64 | 端末区分正式名称 | `device_category_official_name` | VARCHAR | 1200 | － | - |
|  | 65 | 大分類 | `major_category` | VARCHAR | 4 | － | - |
|  | 66 | 大分類正式名称 | `major_category_official_name` | VARCHAR | 1200 | － | - |
|  | 67 | 中分類 | `middle_category` | VARCHAR | 4 | － | - |
|  | 68 | 中分類正式名称 | `middle_category_official_name` | VARCHAR | 1200 | － | - |
|  | 69 | 小分類 | `minor_category` | VARCHAR | 4 | － | - |
|  | 70 | 小分類正式名称 | `minor_category_official_name` | VARCHAR | 1200 | － | - |
|  | 71 | 機能フラグ | `feature_flag` | VARCHAR | 100 | － | - |
|  | 72 | バンドルプラン識別id | `bundle_plan_identification_id` | VARCHAR | 20 | － | - |
|  | 73 | バンドルプランnm | `bundle_plan_nm` | VARCHAR | 1200 | － | - |
|  | 74 | チャージ額 | `charge_amount` | DECIMAL | 10,0 | － | - |
|  | 75 | ユニバーサル使用料 | `uni_universal_usage_fee` | DECIMAL | 10,0 | － | - |
|  | 76 | 利用有効期間 | `validity_period` | DECIMAL | 10,0 | － | - |
|  | 77 | 物流商品コード | `logistics_product_code` | VARCHAR | 30 | － | - |
|  | 78 | 数量金額管理区分 | `quantity_amount_classification` | DECIMAL | 10,0 | － | - |
|  | 79 | 商品税分類コード | `product_tax_classification_code` | DECIMAL | 10,0 | － | - |
|  | 80 | 物流商品税分類 | `logistics_product_tax_classification` | VARCHAR | 2 | － | - |
|  | 81 | 物流基本単位数量 | `logistics_base_unit_quantity` | VARCHAR | 40 | － | - |
|  | 82 | 標準入数 | `standard_quantity` | DECIMAL | 13,3 | － | - |
|  | 83 | 出荷時入数 | `shipping_quantity` | DECIMAL | 10,0 | － | - |
|  | 84 | 個装箱サイズ_縦 | `individual_box_size_length` | DECIMAL | 10,0 | － | - |
|  | 85 | 個装箱サイズ_横 | `individual_box_size_width` | DECIMAL | 10,0 | － | - |
|  | 86 | 個装箱サイズ_高さ | `individual_box_size_height` | DECIMAL | 10,0 | － | - |
|  | 87 | 梱包財_紙重量 | `paper_packaging_material_weight` | DECIMAL | 10,0 | － | - |
|  | 88 | 梱包財_プラ重量 | `plastic_packaging_material_weight` | DECIMAL | 10,0 | － | - |
|  | 89 | 商品重量 | `product_weight` | DECIMAL | 10,0 | － | - |
|  | 90 | パレット積み付け数 | `number_of_pallets` | DECIMAL | 10,0 | － | - |
|  | 91 | 梱包仕様等 | `packaging_specifications_etc` | DECIMAL | 10,0 | － | - |
|  | 92 | mrp管理者コード | `mrp_administrator_code` | VARCHAR | 6 | － | - |
|  | 93 | 変換代表フラグ | `conversion_representative_flag` | VARCHAR | 2 | － | - |
|  | 94 | 検品用商品タイプcd | `product_type_for_inspection_cd` | VARCHAR | 6 | － | - |
|  | 95 | 検品用商品タイプnm | `product_type_for_inspection_nm` | VARCHAR | 1200 | － | - |
|  | 96 | model_id | `model_id` | DECIMAL | 10,0 | － | - |
|  | 97 | imsiタイプ | `imsi_type` | VARCHAR | 4 | － | - |
|  | 98 | imsiタイプ正式名称 | `imsi_type_official_name` | VARCHAR | 1200 | － | - |
