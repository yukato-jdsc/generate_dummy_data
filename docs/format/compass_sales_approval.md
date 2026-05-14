# (COMPASS)営業決裁

- マート名: `b_hjn_com_営業決裁`
- CSVファイル名: 
  - 初期データ: `b_hjn_com_営業決裁.csv`
  - 差分データ: `b_hjn_com_営業決裁_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 初期移行（160,000件）、日次差分（2,000件）
- データ量: 初期移行（200MB、2年分）、日次差分（不明）
- データ概要: COMPASSより連携される「営業決裁」を公開する
- 参考データ: `sample_data/compass_sales_approval.csv` 

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | 必須 | 説明 |
| --- | --- | --- | --- | --- | --- |
| ID | `id` | VARCHAR | 20 | ⚪︎ |  |
| 決裁番号 | `approval_number` | VARCHAR | 80 | ⚪︎ | - |
| 決裁件名 | `approval_subject` | VARCHAR | 255 | ⚪︎ | - |
| ステータス | `status` | VARCHAR | 255 | ⚪︎ | いずれか（承認、差戻し、取り下げ、申請者確認中、承認者確認中、条件付き承認、同意者確認中、否決 |
| 申請日時 | `date_and_time_of_application` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 決裁種別 | `approval_type` | VARCHAR | 255 | ⚪︎ | - |
| モバイル | `mobile_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 音声 | `voice_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 音声(おとく光電話) | `voice_otoku_hikari_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| ID(データ) | `id_data_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| IS(NI・物販) | `is_ni_product_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| PHS | `phs_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】値引きなど | `common_discounts_etc` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】法人まとめ請求 | `common_corporate_consolidated_billing` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】試験用回線 | `common_test_lines` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【モバイル】決裁パターンA(試算シートの利益率判断) | `mobile_approval_pattern_a` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】決裁パターンC(試算シートを必要としない減免) | `mobile_approval_pattern_c` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】決裁パターンE | `mobile_approval_pattern_e` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】インセンティブ調整(増減額) | `mobile_incentive_adjustment_increase` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】再販又はレンタル事業者へのサービス提供 | `mobile_resale_or_rental_companies` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】預託金・連帯保証・与信緩和 | `mobile_deposits_joint_guarantees_credit_relaxation` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【共通】QAレビュー実施案件 | `common_qa_review_cases` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】特殊な債権回収条件(支払いサイトの変更) | `special_debt_collection` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【共通】建設業法に関わる工事案件 | `construction_industry_law` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 水際処理・代理店コード変更 | `agency_code_change` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 料金調整・現金返還・料金減免 | `refund_fee_reduction` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 代理店契約 | `agency_contract` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【ID(データ)】ODNコンシューマ仕様 | `odn_consumer_specifications` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 再販契約 | `reseller_contract` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【ID(データ)】課金テーブル設定 | `id_data_charging_table_settings` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 料率・インセンティブ設定 | `rate_incentive_settings` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 損害補填目的での料金調整 | `fee_adjustment_for_damage_compensation` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 決裁特別施策(モバイル黒字) | `special_approval_measures_mobile_profit` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 契約締結(提案決裁承認後) | `contract_conclusion_after_proposal_approval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| みなし法人 | `deemed_corporation` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 仕入れ販売(300万円以下＆黒字) | `under_3_million_yen_profit` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| データ系再販(手数料型) | `data_resale_commission_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】特殊値引(特別タリフ・個別タリフなど) | `common_special_discounts_special_tariffs_individual_tariffs` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【ID(データ)】再販(ID) | `id_data_resale_id` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【IS(NI・物販)】再販(IS) | `is_ni_product_sales_resale_is` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 先行発注 | `pre_order` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 再販契約(データ) | `reseller_contract_data` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 契約締結(単独) | `contract_conclusion_single` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 社外文書提出 | `external_document_submission` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| NDA契約 | `nda_agreement` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| その他 | `other_type` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 起案者名 | `originators_name` | VARCHAR | 255 | ⚪︎ | - |
| 起案者電話番号 | `originators_phone_number` | VARCHAR | 255 | - | - |
| 起案者の所属組織情報一覧 | `affiliated_org_address_list` | VARCHAR | 12000 | ⚪︎ | - |
| 情報元集約シート | `source_aggregation_sheet_info` | VARCHAR | 80 | ⚪︎ | - |
| 集約番号 | `aggregation_number` | VARCHAR | 255 | ⚪︎ | - |
| 実行予定日（提案/処理依頼予定日) | `scheduled_execution_date` | VARCHAR | 10 | ⚪︎ | YYYY-MM-DD |
| 決裁書有効期間（ヶ月） | `approval_document_period_months` | VARCHAR | 255 | ⚪︎ | - |
| 与信アラート | `credit_alert` | VARCHAR | 255 | - | 有 / 無 |
| 与信審査実施有無 | `whether_credit_review` | VARCHAR | 255 | - |  有 / 無 |
| 与信審査依頼名（COMPASS） | `credit_review_request_name_compass` | VARCHAR | 255 | - | - |
| 与信審査依頼名（BFS） | `credit_review_request_name_bfs` | VARCHAR | 255 | - | - |
| 法務事前審査実施有無 | `whether_legal_pre_review_conducted` | VARCHAR | 255 | - |  有 / 無 |
| 法務事前審査依頼番号 | `legal_pre_review_request_number` | VARCHAR | 255 | - | - |
| 再決裁・起案フラグ | `re_approval_draft_flag` | VARCHAR | 255 | - |  有 / 無 |
| サービス種別 | `service_type` | VARCHAR | 255 | ⚪︎ | - |
| 販路 | `sales_channel` | VARCHAR | 255 | ⚪︎ | - |
| 法個人区分 | `legal_personal_classification` | VARCHAR | 255 | -︎ | - |
| 請求形態 | `billing_form` | VARCHAR | 255 | ⚪︎ | - |
| 代理店協業の条件 | `agency_collaboration_conditions` | VARCHAR | 255 | ⚪︎ | - |
| 水際支払金額 | `borderline_payment_amount` | VARCHAR | 255 | ⚪︎ | - |
| 決裁前事前承認フラグ | `pre_approval_flag` | VARCHAR | 255 | - | - |
| 承認を受けた者の氏名 | `name_of_approved_person` | VARCHAR | 255 |  -︎ | - |
| 事後決裁となった理由 | `reason_for_post_approval` | VARCHAR | 12000 | - | - |
| 承認者 | `approver` | VARCHAR | 255 | ⚪︎ | - |
| 申請者 | `applicant` | VARCHAR | 255 | ⚪︎ | - |
| 承認ルートとして利用する組織（起案者の本務/兼務） | `orgl_route_proposers_duties` | VARCHAR | 255 | - | - |
| 承認ルートとして利用する組織（営業担当者の本務/兼務） | `orgl_route_sales_duties` | VARCHAR | 255 | - | - |
| 営業担当者の所属組織情報一覧 | `sales_representatives_list` | VARCHAR | 12000 | - | - |
| 包括決裁 | `comprehensive_approval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| グループ包括決裁 | `group_comprehensive_approval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 他案件で利用 | `used_in_other_projects` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 担当者名 | `contact_name` | VARCHAR | 255 | - | - |
| 担当者電話番号 | `contact_phone_number` | VARCHAR | 255 | - | - |
| 事前相談有無 | `pre_confirmation` | VARCHAR | 255 | - | 有 / 無 |
| 決裁事前相談名 | `pre_approval_consultation_name` | VARCHAR | 255 | ︎- | - |
| 案件名 | `project_name` | VARCHAR | 255 | - | - |
| 案件ID | `project_id` | VARCHAR | 255 | - | - |
| 企業名 | `company_name` | VARCHAR | 255 | ⚪︎ | - |
| 統一企業コード | `uniform_company_code` | VARCHAR | 255 | ⚪︎ | - |
| TSR評点 | `tsr_rating` | VARCHAR | 255 | - | - |
| 回線数 | `number_of_lines` | DECIMAL |  18,0 | - | - |
| 契約期間（ヶ月） | `contract_period_months` | DECIMAL | 18,0 | -︎ | - |
| 契約開始予定日 | `contract_start_date` | VARCHAR | 10 | - | YYYY-MM-DD |
| SBTM直轄現調・開通立会い回線数 | `number_of_lines_attended_opening` | DECIMAL | 18,0 | - | - |
| 開通工事費無料 | `activation_installation_fee` | VARCHAR | 255 | - | 有 / 無 |
| 番ポ工事費＋付加サービス_工事費無料 | `free_installation_and_additional_service_fee` | VARCHAR | 255 | - | - |
| 負担内容1 | `free_installation_fee` | VARCHAR | 12000 | - | - |
| 負担費用　月額1（円） | `banner_installation_fee_additional_services` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金1（円） | `cost_1` | DECIMAL | 18,0 | - | - |
| 負担内容2 | `cost_monthly_per_yen1` | VARCHAR | 12000 | - | - |
| 負担費用　月額2（円） | `cost_lump_sum_per_yen1` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金2（円） | `cost_monthly_per_yen2` | DECIMAL | 18,0 | - | - |
| 負担内容3 | `cost_lump_sum_per_yen2` | VARCHAR | 12000 | - | - |
| 負担費用　月額3（円） | `cost_monthly_per_yen3` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金3（円） | `cost_lump_sum_per_yen3` | DECIMAL | 18,0 | - | - |
| 提案種別 | `proposal_type` | VARCHAR | 255 | - | いずれか（既存追加、機種変更、機変＆提供条件変更、新規、追加新規、提供条件変更、（空白）） |
| 案件概要①（要旨記述） | `project_summary_1_summary` | VARCHAR | 12000 | ⚪︎ | - |
| 案件概要②（要旨記述・その他） | `project_summary_2_summary` | VARCHAR | 12000 | ⚪︎ | - |
| 見込回線数（上限） | `other` | DECIMAL | 18,0 | - | - |
| 適用プラン | `expected_number_of_lines_maximum` | VARCHAR | 255 | - | - |
| 割引率（％） | `applicable_platform_discount_rate_percent` | DECIMAL | 18,0 | - | - |
| チャネル | `channel` | VARCHAR | 255 | - | - |
| 減免有無 | `exemption_deduction` | VARCHAR | 255 | - | 有 / 無 |
| 減免額（円） | `exemption_amount_yen` | DECIMAL | 18,0 | - | - |
| 売上（円） | `sales_yen` | DECIMAL | 18,0 | - | - |
| 営業変動利益（円） | `variable_operating_profit_yen` | DECIMAL | 18,0 | - | - |
| 営業変動利益率（％） | `variable_operating_profit_margin_percent` | DECIMAL | 18,0 | - | - |
| 営業貢献利益（円） | `operating_contribution_margin_yen` | DECIMAL | 18,0 | - | - |
| 営業貢献利益率（％） | `operating_contribution_margin_margin_percent` | DECIMAL | 18,0 | - | - |
| 営業利益（円） | `operating_profit_yen` | DECIMAL | 18,0 | - | - |
| 営業利益率（％） | `operating_profit_margin_percent` | DECIMAL | 18,0 | - | - |
| 音声営業貢献利益（円） | `voice_sales_contribution_margin_yen` | DECIMAL | 18,0 | - | - |
| 音声営業貢献利益率（％） | `voice_sales_contribution_margin_margin_percent` | DECIMAL | 18,0 | - | - |
| ID(データ)決裁基準利益（円） | `id_data_approval_base_profit_yen` | DECIMAL | 18,0 | - | - |
| ID(データ)決裁基準利益率（％） | `id_data_approval_base_profit_margin_percent` | DECIMAL | 18,0 | - | - |
| IS(NI・物販)決裁基準利益（円） | `is_ni_product_sales_approval_base_profit_yen` | DECIMAL | 18,0 | - | - |
| IS(NI・物販)決裁基準利益率（％） | `is_ni_product_sales_approval_base_profit_margin_percent` | DECIMAL | 18,0 | - | - |
| モバイル営業貢献利益（円） | `mobile_sales_contribution_margin_yen` | DECIMAL | 18,0 | - | - |
| モバイル営業貢献利益率（％） | `mobile_sales_contribution_margin_margin_percent` | DECIMAL | 18,0 | - | - |
| 代理店情報手入力フラグ | `agency_information_manual_input_flag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 代理店名（参照） | `agency_name_reference` | VARCHAR | 255 | - | - |
| 代理店名（試算） | `agency_name_estimate` | VARCHAR | 255 | - | - |
| 代理店コード | `agency_code` | VARCHAR | 54 | - | - |
| 手数料率（％） | `commission_rate_percent_incent` | DECIMAL | 18,0 | - | - |
| インセンティブ額（円） | `incentive_amount_yen` | DECIMAL | 18,0 | - | - |
| 協業理由 | `reason_for_collaboration` | VARCHAR | 12000 | - | - |
| 自動更新有無 | `automatic_renewal` | VARCHAR | 255 | ⚪︎ | 有 / 無 |
| SBM回線数（上限） | `sbm_line_count_upper` | DECIMAL | 18,0 | - | - |
| SBM回線数（下限） | `sbm_line_count_lower` | DECIMAL | 18,0 | - | - |
| ﾓﾊﾞｲﾙ(YM)回線数(上限) | `mobile_ym_line_count_upper` | DECIMAL | 18,0 | - | - |
| ﾓﾊﾞｲﾙ(YM)回線数(下限） | `mobile_ym_line_count_lower` | DECIMAL | 18,0 | - | - |
| 外部支出総額・仕入額（円） | `total_external_expenses_purchases_yen` | DECIMAL | 18,0 | - | - |
| 音声(おとく光電話)営業貢献利益（円） | `voice_otoku_hikari_phone_sales_contribution_margin_yen` | DECIMAL | 18,0 | ︎- | - |
| 音声(おとく光電話)営業貢献利益率（％） | `voice_otoku_hikari_phone_sales_contribution_margin_rate_percent` | DECIMAL | 18,0 | - | - |
| 減免・調整・返還・回収金額（円） | `deduction_adjustment_refund_recovery_amount_yen` | DECIMAL | 18,0 | - | - |
| 外部支出総額（円） | `total_external_expenses_yen` | DECIMAL | 18,0 | - | - |
| 対象期間 | `applicable_period` | VARCHAR | 255 | - | - |
| 支払い時期 | `payment_date` | VARCHAR | 255 | - | - |
| 売上総合計金額（円） | `total_sales_amount_yen` | DECIMAL | 18,0 | - | - |
| 請求書再発行有無 | `invoice_reissue` | VARCHAR | 255 | - | - |
| 関連する決裁（COMPASS） | `related_approvals_compass` | VARCHAR | 255 | - | 決裁番号を "," 区切りで入力 |
| 稟議申請番号（COMPASS以外） | `approval_request_number_other_than_compass` | VARCHAR | 255 | - | - |
| ソリューション販売管理システム見積番号 | `solution_sales_management_system_quote_number` | DECIMAL | 18,0 | - | - |
| アセットDB番号 | `asset_db_number` | VARCHAR | 255 | - | - |
| 代理店申請書番号 | `agency_application_number` | VARCHAR | 255 | - | - |
| 代理店申請書番号（SDWF） | `agency_application_number_sd_wf` | VARCHAR | 255 | ⚪︎ | - |
| 備考 | `notes` | VARCHAR | 12000 | - | - |
| 閲覧範囲 | `viewability` | VARCHAR | 255 | - | - |
| 追加・変更内容 | `additions_changes` | VARCHAR | 12000 | - | - |
| 入力者 | `inputter` | VARCHAR | 255 | - | - |
| 入力日 | `input_date` | VARCHAR | 255 | - | - |
| 契約化必須条件1 | `contractual_condition_1` | VARCHAR | 12000 | - | - |
| 契約化必須条件2 | `contractual_condition_2` | VARCHAR | 12000 | - | - |
| フローから子決裁作成フラグ | `create_sub_approval_from_flow_flag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 非公開フラグ | `private_flag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 承認日時 | `approval_date` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm  |
| 事業区分 | `business_category` | VARCHAR | 255 | ⚪︎ | - |
| 有効期限 | `expiration_date` | VARCHAR | 10 | - | YYYY-MM-DD |
| 追加情報欄 | `additional_information_field` | VARCHAR | 12000 | - | - |
| 基となる提案決裁 | `based_proposal_approval` | VARCHAR | 240 | - | - |
| 決裁内容 | `approval_content` | VARCHAR | 255 | ⚪︎ | - |
| 承認ルート基準 | `approval_route_criteria` | VARCHAR | 255 | ⚪︎ | - |
| 仕入先与信 | `supplier_credit` | VARCHAR | 80 | ⚪︎ | - |
| 有効 | `valid_flg` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| レコードID（数式） | `record_id_formula` | VARCHAR | 1300 | ⚪︎ | - |
| 作成者ID | `creator_id` | VARCHAR | 255 | ⚪︎ | - |
| 作成日 | `creation_date` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm  |
| 削除 | `deleted_flg` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 最終更新者ID | `last_updated_by_id` | VARCHAR | 255 | ⚪︎ | - |
| 最終更新日 | `last_updated_date` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終参照日 | `last_reference_date` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終閲覧日 | `last_viewed_date` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm  |
| 所有者ID | `owner_id` | VARCHAR | 255 | ⚪︎ | - |
| レコードタイプID | `record_type_id` | VARCHAR | 3900 | ⚪︎ | - |
| SystemModstamp | `systemmodstamp` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 試算シート番号 | `estimate_sheet_number` | VARCHAR | 12000 | - | - |
| SUMMITデータ移行フラグ | `summit_data_migration_flag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 与信審査依頼名（COMPASS）有無判定 | `credit_review_request_name_compass_presence_absence` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 試算シート有無 | `estimate_sheet_presence_absence` | VARCHAR | 255 | ⚪︎ | 有 / 無 |
| プロダクト事前相談 | `product_pre_consultation` | VARCHAR | 255 | - | - |
| モバイル相対相談承認条件 | `mobile_p2p_consultation_approval_conditions` | VARCHAR | 12000 | - | - |
| 事前相談承認条件 | `pre_consultation_approval_conditions` | VARCHAR | 12000 | - | - |
| 要旨補足（申請者専用） | `summary_supplement_applicant_only` | VARCHAR | 12000 | - | - |
| 承認日時（UnixTime） | `approval_date_and_time_unixtime` | VARCHAR | 255 | - | 承認時のみ入力 unix time形式 |
| コメント１ | `comment_1` | VARCHAR | 12000 | - | - |
| コメント２ | `comment_2` | VARCHAR | 12000 | ︎- | - |
| コメント３ | `comment_3` | VARCHAR | 12000 | - | - |
| コメント４ | `comment_4` | VARCHAR | 12000 | - | - |
| コメント５ | `comment_5` | VARCHAR | 12000 | - | - |
| 共有用メールアドレス① | `shared_email_address_1` | VARCHAR | 150 | - | - |
| 共有用メールアドレス② | `shared_email_address_2` | VARCHAR | 150 | - | - |
| 共有用メールアドレス③ | `shared_email_address_3` | VARCHAR | 150 | - | - |
| 起案者共通社員番号 | `proposers_common_employee_id` | VARCHAR | 255 | ⚪︎ | - |
| 起案者部署 | `proposers_dept` | VARCHAR | 255 | ⚪︎ | - |
| 起案部署_組織コード(本部) | `proposal_dept_org_code_headquarters` | VARCHAR | 255 | - | - |
| 起案部署_組織コード(統括部) | `proposal_dept_org_general_affairs_dept` | VARCHAR | 255 | - | - |
| 起案部署_組織コード(部) | `proposal_dept_org_code_dept` | VARCHAR | 255 | - | - |
| 申請者（グループ名） | `applicants_group_name` | VARCHAR | 255 | - | - |
| 申請者（ユーザーID） | `applicants_user_id` | VARCHAR | 255 | - | - |
| 申請者（ユーザー名） | `applicants_user_name` | VARCHAR | 255 | - | - |
| 同意者（グループ名） | `consenters_group_name` | VARCHAR | 255 | - | - |
| 同意者（ユーザーID） | `consenters_user_id` | VARCHAR | 255 | - | - |
| 同意者（ユーザー名） | `consenters_user_name` | VARCHAR | 255 | - | - |
| 承認者のレイヤー | `approvers_layer` | VARCHAR | 255 | - | - |
| 承認者（グループ名） | `approvers_group_name` | VARCHAR | 255 | - | - |
| 承認者（ユーザーID） | `approvers_user_id` | VARCHAR | 255 | - | - |
| 承認者（ユーザー名） | `approvers_user_name` | VARCHAR | 255 | - | - |
| 最終処理日時 | `last_processing_date_and_time` | VARCHAR | 255 | - | - |
| 承認履歴 | `approval_history` | VARCHAR | 12000 | - | - |

## 制約

- 主キー: なし
