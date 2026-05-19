# (BFSエントリ)モバイル_エントリ情報

- マート名: `b_hjn_bfs_モバイル_エントリ情報`
- CSVファイル名: 
  - 初期データ: `YYYYMMDD_DLV_OAI_BFS_BFS_ENTRY_INFO.csv`
  - 差分データ: `YYYYMMDD_DLV_OAI_BFS_BFS_ENTRY_INFO_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 初期移行（2,000,000件）、日次差分（5,921件）
- データ量: 初期移行（約375MB、2年分）、日次差分（7.66MB）
- データ概要: BFSエントリのモバイル向けエントリ情報を保有。
- 参考データ: `sample_data/bfs_entry_informations.csv`

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | 必須 | 説明 |
| --- | --- | --- | --- | --- | --- |
| エントリ番号 | `entry_no` | VARCHAR | 54 | ⚪︎ | - |
| 件名 | `entry_nm` | VARCHAR | 2304 | - | - |
| 作成区分 | `entry_status_nm` | VARCHAR | 900 | ⚪︎ | いずれか（エントリ作成、試算作成、申込書作成） |
| オーダ種別 | `entry_type_nm` | VARCHAR | 900 | ⚪︎ | 追加新規 で固定 |
| 申込書連携 | `application_make_type` | VARCHAR | 900 | ⚪︎ | 有 / 無 |
| 特約分離出力有無 | `latest_appli_output_type` | VARCHAR | 900 | ⚪︎ | 有 / 無 |
| 通知書対象 | `corp_notification` | VARCHAR | 900 | ⚪︎ | 有 / 無 |
| 開通済有無 | `line_opened_status` | VARCHAR | 900 | ⚪︎ | 有 / 無 |
| 開通日 | `open_date` | VARCHAR | 60 | - | yyyy/M/d H:mm |
| 非完結依頼種別 | `incomplete_type_nm` | VARCHAR | 900 | - | - |
| コピー元エントリ種別 | `src_entry_type_nm` | VARCHAR | 900 | － | - |
| 営業担当者コード | `cmn_staff_no_bizchrg` | VARCHAR | 21 | － | - |
| 営業担当者 | `entry_user_nm` | VARCHAR | 2295 | － | - |
| 取次店コード | `unit_agent_cd` | VARCHAR | 27 | ⚪︎ | - |
| 所属代理店 | `unit_agent_nm` | VARCHAR | 900 | ⚪︎ | - |
| キャリア種別 | `carrier_type_nm` | VARCHAR | 2295 | ⚪︎ | - |
| 事業者区分 | `enterprise_type_nm` | VARCHAR | 2295 | ⚪︎ | - |
| 申込書番号 | `application_no` | VARCHAR | 54 | ⚪︎ | - |
| 契約種別 | `contract_type_nm` | VARCHAR | 900 | ⚪︎ | 相対 または 約款 |
| 納品予定日 | `delivery_expect_date` | VARCHAR | 60 | － | yyyy/MM/dd 0:00:00 |
| 申込日 | `application_date` | VARCHAR | 60 | － | yyyy/MM/dd 0:00:00 |
| ipad顧客種別 | `ipad_customer_type_nm` | VARCHAR | 900 | － | - |
| 請求方法 | `terminal_pay_method_nm` | VARCHAR | 900 | － | - |
| 支払回数 | `terminal_pay_num_nm` | VARCHAR | 90 | － | - |
| 請求区分 | `terminal_bill_nm` | VARCHAR | 900 | － | - |
| 通話料合算種別 | `call_charge_totaling_nm` | VARCHAR | 900 | － | - |
| 付属品購入 | `accessory_sale_flg_nm` | VARCHAR | 2295 | － | 有 / 無 |
| 付属品代金支払い方法 | `accessory_pay_method_nm` | VARCHAR | 900 | － | - |
| 付属品代金請求区分 | `attach_bill_nm` | VARCHAR | 900 | － | - |
| 付属品通話料合算種別 | `accessory_totaling_nm` | VARCHAR | 900 | － | - |
| 変更対象 | `change_target_type_nm` | VARCHAR | 900 | － | - |
| 受付区分 | `receipt_type_nm` | VARCHAR | 900 | － | - |
| webオーダ番号 | `web_ord_no` | VARCHAR | 33 | － | - |
| 請求先割引変更 | `bill_no_discount_change_flg_nm` | VARCHAR | 2295 | － | - |
| エントリ作成者id | `entry_create_user_id` | VARCHAR | 60 | ⚪︎ | - |
| エントリ作成日時 | `entry_ins_tstamp` | VARCHAR | 78 | ⚪︎ | yyyy/MM/dd H:mm:ss |
| エントリ更新担当者id | `entry_last_upd_user_id` | VARCHAR | 60 | ⚪︎ | - |
| エントリ更新日時 | `entry_last_upd_tstamp` | VARCHAR | 78 | ⚪︎ | yyyy/MM/dd H:mm:ss |
| 関係者1 | `concerned_user_nm1` | VARCHAR | 2295 | － | - |
| 関係者2 | `concerned_user_nm2` | VARCHAR | 2295 | － | - |
| 関係者3 | `concerned_user_nm3` | VARCHAR | 2295 | － | - |
| 関係者4 | `concerned_user_nm4` | VARCHAR | 2295 | － | - |
| 関係者5 | `concerned_user_nm5` | VARCHAR | 2295 | － | - |
| 関係者6 | `concerned_user_nm6` | VARCHAR | 2295 | － | - |
| 関係者7 | `concerned_user_nm7` | VARCHAR | 2295 | － | - |
| 関係者8 | `concerned_user_nm8` | VARCHAR | 2295 | － | - |
| 関係者9 | `concerned_user_nm9` | VARCHAR | 2295 | － | - |
| 関係者10 | `concerned_user_nm10` | VARCHAR | 2295 | － | - |
| sfa番号 | `sfa_no` | VARCHAR | 108 | － | - |
| sfa案件名 | `sfa_nm` | VARCHAR | 765 | － | - |
| 統一企業コード | `corp_cd` | VARCHAR | 18 | － | - |
| 企業名 | `corp_nm` | VARCHAR | 900 | － | - |
| 営業決裁件名 | `sales_decide_nm` | VARCHAR | 2304 | － | - |
| 営業決裁番号 | `sales_decide_no` | VARCHAR | 108 | － | - |
| 代理店コード | `agent_cd` | VARCHAR | 27 | － | - |
| 集約ブック番号 | `collected_book_no` | VARCHAR | 42 | － | - |
| 試算ブック番号 | `calculate_book_no` | VARCHAR | 54 | － | - |
| かんたん見積番号 | `eet_no` | VARCHAR | 60 | － | - |
| 相対契約管理番号 | `negociated_contract_no` | VARCHAR | 108 | － | - |
| 決裁番号1 | `decide_no1` | VARCHAR | 90 | － | - |
| 決裁番号2 | `decide_no2` | VARCHAR | 90 | － | - |
| 決裁番号3 | `decide_no3` | VARCHAR | 90 | － | - |
| 決裁番号4 | `decide_no4` | VARCHAR | 90 | － | - |
| 決裁番号5 | `decide_no5` | VARCHAR | 90 | － | - |
| 取次店コード1 | `distributer_cd` | VARCHAR | 54 | － | - |
| 取次店名 | `distributer_nm` | VARCHAR | 2295 | － | - |
| 営業担当者1 | `bizchrg_nm` | VARCHAR | 2295 | － | - |
| 電話番号 | `biz_charge_telno` | VARCHAR | 39 | － | - |
| 部署名 | `div_official_nm` | VARCHAR | 2133 | － | - |
| 本人確認実施者コード | `identification_charge_cd` | VARCHAR | 30 | － | - |
| 受付担当者コード | `receipt_charge_cd` | VARCHAR | 30 | － | - |
| 申請者名 | `applicant_user_nm` | VARCHAR | 900 | － | - |
| 部署名1 | `applicant_division_nm` | VARCHAR | 2295 | － | - |
| 共通社員番号 | `cmn_staff_no` | VARCHAR | 21 | － | - |
| 与信申請番号 | `credit_appl_no` | VARCHAR | 48 | － | - |
| 与信回答番号 | `credit_ans_no` | VARCHAR | 51 | － | - |
| 契約者番号 | `contract_no` | VARCHAR | 36 | － | - |
| 契約者タイプ | `mb_corp_type_nm` | VARCHAR | 2295 | － | - |
| 法人格位置 | `corp_status_pos_nm` | VARCHAR | 2295 | － | - |
| 法人格 | `corp_status_nm` | VARCHAR | 2295 | － | - |
| 契約者名 | `contract_nm_org` | VARCHAR | 2295 | － | - |
| 契約者名カナ | `contract_nm_kn` | VARCHAR | 2295 | － | - |
| 法人タイプ | `corp_type_nm` | VARCHAR | 2295 | － | - |
| みなし法人用決裁番号 | `apply_no` | VARCHAR | 765 | － | - |
| 担当者名 | `contract_charge_nm` | VARCHAR | 270 | － | - |
| 担当者名カナ | `contract_charge_nm_kana` | VARCHAR | 540 | － | - |
| 担当者部署 | `contract_div_nm` | VARCHAR | 2295 | － | - |
| 契変更確認チェック | `contract_nm_change_flg_nm` | VARCHAR | 900 | － | - |
| 契約者名変更コメント | `contract_nm_coment` | VARCHAR | 2295 | － | - |
| 請求先番号 | `bill_no` | VARCHAR | 36 | － | - |
| 法人格位置1 | `corp_status_pos_nm1` | VARCHAR | 2295 | － | - |
| 法人格1 | `corp_status_nm1` | VARCHAR | 2295 | － | - |
| 請求先名 | `bill_nm_org` | VARCHAR | 2295 | － | - |
| 請求先名カナ | `bill_nm_kn` | VARCHAR | 2295 | － | - |
| 部門名 | `bill_contact_div_nm` | VARCHAR | 2304 | － | - |
| 担当者 | `bill_contact_nm` | VARCHAR | 270 | － | - |
| 支払方法 | `pay_method_type_nm` | VARCHAR | 1536 | － | - |
| 請求書タイプ | `bill_account_type_nm` | VARCHAR | 1536 | － | - |
| 請求書送付 | `bill_send_type_nm` | VARCHAR | 1536 | － | - |
| 下4桁表示 | `telno_disp_nm` | VARCHAR | 1536 | － | - |
| 請求群情報 | `bill_cycle_nm` | VARCHAR | 1536 | － | - |
| 割賦許容番号 | `installment_allowance_num` | VARCHAR | 60 | － | - |
| 代行業者 | `surrogate_nm` | VARCHAR | 1536 | － | - |
| 法人複数回線割引 | `discount_nm` | VARCHAR | 300 | － | - |
| 割引率 | `discount_rate` | VARCHAR | 18 | － | - |
| 割引額 | `discount` | VARCHAR | 24 | － | - |
| 割引月数 | `discount_months` | VARCHAR | 300 | － | - |
| 手数料種別 | `charge_type` | VARCHAR | 3 | － | - |
| 請求書一括割引 | `discount_nm_1` | VARCHAR | 300 | － | - |
| 割引率1 | `discount_rate_1` | VARCHAR | 18 | － | - |
| 割引額1 | `discount_1` | VARCHAR | 24 | － | - |
| 割引月数1 | `discount_months_1` | VARCHAR | 300 | － | - |
| 手数料種別1 | `charge_type_1` | VARCHAR | 3 | － | - |
| s番法人複数回線割引 | `discount_nm_2` | VARCHAR | 300 | － | - |
| 割引率2 | `discount_rate_2` | VARCHAR | 18 | － | - |
| 割引額2 | `discount_2` | VARCHAR | 24 | － | - |
| 割引月数2 | `discount_months_2` | VARCHAR | 300 | － | - |
| 手数料種別2 | `charge_type_2` | VARCHAR | 3 | － | - |
| s番大口通話料割引 | `discount_nm_3` | VARCHAR | 300 | － | - |
| 割引率3 | `discount_rate_3` | VARCHAR | 18 | － | - |
| 割引額3 | `discount_3` | VARCHAR | 24 | － | - |
| 割引月数3 | `discount_months_3` | VARCHAR | 300 | － | - |
| 手数料種別3 | `charge_type_3` | VARCHAR | 3 | － | - |
| シェア | `discount_nm_4` | VARCHAR | 300 | － | - |
| 割引率4 | `discount_rate_4` | VARCHAR | 18 | － | - |
| 割引額4 | `discount_4` | VARCHAR | 24 | － | - |
| 割引月数4 | `discount_months_4` | VARCHAR | 300 | － | - |
| 手数料種別4 | `charge_type_4` | VARCHAR | 3 | － | - |
| 請求先送付先区分 | `bill_biz_send_type_nm` | VARCHAR | 1536 | － | - |
| 送付先宛名 | `bill_nm` | VARCHAR | 2295 | － | - |
| 請求書カスタマイズ | `bill_custom` | VARCHAR | 2304 | － | - |
| 請求書送付区分 | `bill_biz_send_type_nm_1` | VARCHAR | 1536 | － | - |
| 送付先宛名1 | `bill_nm_2` | VARCHAR | 2295 | － | - |
| 請求書カスタマイズ1 | `bill_custom_2` | VARCHAR | 2304 | － | - |
| 特約開始年月日 | `special_start_date` | VARCHAR | 60 | － | - |
| 特約期間 | `special_period_nm` | VARCHAR | 900 | － | - |
| 契約期間月数 | `contract_period_month` | VARCHAR | 6 | － | - |
| 自動更新後の期間 | `auto_renew_term_nm` | VARCHAR | 900 | － | XXヶ月 |
| 初期レンタル期間 | `initial_rental_term_nm` | SMALLINT | - | － | XXヶ月 |
| 中古レンタル開始日 | `rental_start_date` | VARCHAR | 60 | － | - |
| 中古レンタル終了日 | `rental_end_date` | VARCHAR | 60 | － | - |
| 特約適用上限回線数 | `special_apply_max_line` | DECIMAL | 10 | － | - |
| 回線数 | `line_num` | DECIMAL | 10 | － | - |
| 倉庫種別 | `warehouse_type_nm` | VARCHAR | 900 | － | - |
| 非完結帳票作成依頼 | `create_form_flg_nm` | VARCHAR | 900 | － | - |
| gisun登録不可 | `register_unavailable_flg` | VARCHAR | 3 | － | - |
| 交換種別 | `usim_replace_type_nm` | VARCHAR | 900 | － | - |
| 在庫種別 | `stock_type_nm` | VARCHAR | 900 | － | - |
| 営業所 | `business_office_location_nm` | VARCHAR | 900 | － | - |
| 申告内容 | `declaration_content_nm` | VARCHAR | 900 | － | - |
| usim種別 | `usim_item_nm` | VARCHAR | 450 | － | - |
| usim種別その他 | `usim_item_else` | VARCHAR | 900 | － | - |
| 台数 | `terminal_num` | DECIMAL | 10 | － | - |
| wo専用usim | `wo_special_usim_type_nm` | VARCHAR | 900 | － | - |
| 試算テンプレートver | `calc_temp_ver` | VARCHAR | 90 | － | - |
| 決裁承認日 | `sales_decide_approval_date` | VARCHAR | 60 | － | - |
| 起票元試算番号 | `issue_src_calc_no` | VARCHAR | 54 | － | - |
| コピー元エントリ番号 | `src_entry_no` | VARCHAR | 54 | － | - |
| 最低利用回線数 | `min_line_num` | DECIMAL | 11 | － | - |
| 端末縛り金額 | `terminal_restrict_price` | DECIMAL | 11 | － | - |
| 端末縛り期間 | `terminal_restrict_term` | DECIMAL | 3 | － | - |
| 国際rm値引指定有無 | `discount_specify_flg_nm` | VARCHAR | 900 | － | - |
| 国際rm値引指定割引率 | `discount_specify_rate` | VARCHAR | 24 | － | - |
| プラン縛り1 | `plan_bind_1` | VARCHAR | 1800 | － | - |
| プラン縛り2 | `plan_bind_2` | VARCHAR | 1800 | － | - |
| プラン縛り3 | `plan_bind_3` | VARCHAR | 1800 | － | - |
| プラン縛り4 | `plan_bind_4` | VARCHAR | 1800 | － | - |
| プラン縛り5 | `plan_bind_5` | VARCHAR | 1800 | － | - |
| プラン縛り6 | `plan_bind_6` | VARCHAR | 1800 | － | - |
| プラン縛り7 | `plan_bind_7` | VARCHAR | 1800 | － | - |
| プラン縛り8 | `plan_bind_8` | VARCHAR | 1800 | － | - |
| プラン縛り9 | `plan_bind_9` | VARCHAR | 1800 | － | - |
| プラン縛り10 | `plan_bind_10` | VARCHAR | 1800 | － | - |
| プラン縛り11 | `plan_bind_11` | VARCHAR | 1800 | － | - |
| プラン縛り12 | `plan_bind_12` | VARCHAR | 1800 | － | - |
| 比率指定プラン1 | `plan_ratio_plan_1` | VARCHAR | 1800 | － | - |
| プラン比率1 | `plan_ratio_ratio_1` | VARCHAR | 24 | － | - |
| 比率指定プラン2 | `plan_ratio_plan_2` | VARCHAR | 1800 | － | - |
| プラン比率2 | `plan_ratio_ratio_2` | VARCHAR | 24 | － | - |
| 比率指定プラン3 | `plan_ratio_plan_3` | VARCHAR | 1800 | － | - |
| プラン比率3 | `plan_ratio_ratio_3` | VARCHAR | 24 | － | - |
| 比率指定プラン4 | `plan_ratio_plan_4` | VARCHAR | 1800 | － | - |
| プラン比率4 | `plan_ratio_ratio_4` | VARCHAR | 24 | － | - |
| 必須opカテゴリ1 | `opt_required_category_1` | VARCHAR | 1800 | － | - |
| 必須op1 | `opt_required_opt_1` | VARCHAR | 1800 | － | - |
| 必須opカテゴリ2 | `opt_required_category_2` | VARCHAR | 1800 | － | - |
| 必須op2 | `opt_required_opt_2` | VARCHAR | 1800 | － | - |
| 必須opカテゴリ3 | `opt_required_category_3` | VARCHAR | 1800 | － | - |
| 必須op3 | `opt_required_opt_3` | VARCHAR | 1800 | － | - |
| 必須opカテゴリ4 | `opt_required_category_4` | VARCHAR | 1800 | － | - |
| 必須op4 | `opt_required_opt_4` | VARCHAR | 1800 | － | - |
| 比率指定opカテゴリ1 | `opt_ratio_category_1` | VARCHAR | 1800 | － | - |
| 比率指定op1 | `opt_ratio_opt_1` | VARCHAR | 1800 | － | - |
| op比率1 | `opt_ratio_ratio_1` | VARCHAR | 24 | － | - |
| 比率指定opカテゴリ2 | `opt_ratio_category_2` | VARCHAR | 1800 | － | - |
| 比率指定op2 | `opt_ratio_opt_2` | VARCHAR | 1800 | － | - |
| op比率2 | `opt_ratio_ratio_2` | VARCHAR | 24 | － | - |
| 比率指定opカテゴリ3 | `opt_ratio_category_3` | VARCHAR | 1800 | － | - |
| 比率指定op3 | `opt_ratio_opt_3` | VARCHAR | 1800 | － | - |
| op比率3 | `opt_ratio_ratio_3` | VARCHAR | 24 | － | - |
| 比率指定opカテゴリ4 | `opt_ratio_category_4` | VARCHAR | 1800 | － | - |
| 比率指定op4 | `opt_ratio_opt_4` | VARCHAR | 1800 | － | - |
| op比率4 | `opt_ratio_ratio_4` | VARCHAR | 24 | － | - |
| その他指定1 | `other_specific_1` | VARCHAR | 1800 | － | - |
| その他指定2 | `other_specific_2` | VARCHAR | 1800 | － | - |
| その他指定3 | `other_specific_3` | VARCHAR | 1800 | － | - |
| その他指定4 | `other_specific_4` | VARCHAR | 1800 | － | - |
| その他指定5 | `other_specific_5` | VARCHAR | 1800 | － | - |
| その他指定6 | `other_specific_6` | VARCHAR | 1800 | － | - |
| その他指定7 | `other_specific_7` | VARCHAR | 1800 | － | - |
| その他指定8 | `other_specific_8` | VARCHAR | 1800 | － | - |
| 補足 | `supplemental` | VARCHAR | 12000 | － | - |
| チャネル | `channel` | VARCHAR | 900 | － | - |
| 試算ステータス | `entry_detail_status_nm` | VARCHAR | 900 | － | - |
| rental_中古_開始年月日 | `rental_used_start_date` | VARCHAR | 60 | － | - |
| rental_中古_期間_ヶ月 | `rental_used_date_month` | VARCHAR | 6 | － | - |
| 特約条項 | `article` | VARCHAR | 3000 | － | - |
