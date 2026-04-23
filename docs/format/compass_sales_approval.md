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

| 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |
| --- | --- | --- | --- | --- | --- |
| 決裁番号 | `approval_number` | VARCHAR | 240 | － | - |
| 決裁件名 | `approval_subject` | VARCHAR | 765 | － | - |
| ステータス | `status` | VARCHAR | 765 | － | - |
| 申請日時 | `date_and_time_of_application` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 決裁種別 | `approval_type` | VARCHAR | 765 | － | - |
| モバイル | `mobile_type` | VARCHAR | 1 | － | - |
| 音声 | `voice_type` | VARCHAR | 1 | － | - |
| 音声(おとく光電話) | `voice_otoku_hikari_type` | VARCHAR | 1 | － | - |
| ID(データ) | `id_data_type` | VARCHAR | 1 | － | - |
| IS(NI・物販) | `is_ni_product_type` | VARCHAR | 1 | － | - |
| PHS | `phs_type` | VARCHAR | 1 | － | - |
| 【共通】値引きなど | `common_discounts_etc` | VARCHAR | 1 | － | - |
| 【共通】法人まとめ請求 | `common_corporate_consolidated_billing` | VARCHAR | 1 | － | - |
| 【共通】試験用回線 | `common_test_lines` | VARCHAR | 1 | － | - |
| 【モバイル】決裁パターンA(試算シートの利益率判断) | `mobile_approval_pattern_a` | VARCHAR | 1 | － | - |
| 【モバイル】決裁パターンC(試算シートを必要としない減免) | `mobile_approval_pattern_c` | VARCHAR | 1 | － | - |
| 【モバイル】決裁パターンE | `mobile_approval_pattern_e` | VARCHAR | 1 | － | - |
| 【モバイル】インセンティブ調整(増減額) | `mobile_incentive_adjustment_increase` | VARCHAR | 1 | － | - |
| 【モバイル】再販又はレンタル事業者へのサービス提供 | `mobile_resale_or_rental_companies` | VARCHAR | 1 | － | - |
| 【モバイル】預託金・連帯保証・与信緩和 | `mobile_deposits_joint_guarantees_credit_relaxation` | VARCHAR | 1 | － | - |
| 【共通】QAレビュー実施案件 | `common_qa_review_cases` | VARCHAR | 1 | － | - |
| 【共通】特殊な債権回収条件(支払いサイトの変更) | `special_debt_collection` | VARCHAR | 1 | － | - |
| 【共通】建設業法に関わる工事案件 | `construction_industry_law` | VARCHAR | 1 | － | - |
| 水際処理・代理店コード変更 | `agency_code_change` | VARCHAR | 1 | － | - |
| 料金調整・現金返還・料金減免 | `refund_fee_reduction` | VARCHAR | 1 | － | - |
| 代理店契約 | `agency_contract` | VARCHAR | 1 | － | - |
| 【ID(データ)】ODNコンシューマ仕様 | `odn_consumer_specifications` | VARCHAR | 1 | － | - |
| 再販契約 | `reseller_contract` | VARCHAR | 1 | － | - |
| 【ID(データ)】課金テーブル設定 | `id_data_charging_table_settings` | VARCHAR | 1 | － | - |
| 料率・インセンティブ設定 | `rate_incentive_settings` | VARCHAR | 1 | － | - |
| 損害補填目的での料金調整 | `fee_adjustment_for_damage_compensation` | VARCHAR | 1 | － | - |
| 決裁特別施策(モバイル黒字) | `special_approval_measures_mobile_profit` | VARCHAR | 1 | － | - |
| 契約締結(提案決裁承認後) | `contract_conclusion_after_proposal_approval` | VARCHAR | 1 | － | - |
| みなし法人 | `deemed_corporation` | VARCHAR | 1 | － | - |
| 仕入れ販売(300万円以下＆黒字) | `under_3_million_yen_profit` | VARCHAR | 1 | － | - |
| データ系再販(手数料型) | `data_resale_commission_type` | VARCHAR | 1 | － | - |
| 【共通】特殊値引(特別タリフ・個別タリフなど) | `common_special_discounts_special_tariffs_individual_tariffs` | VARCHAR | 1 | － | - |
| 【ID(データ)】再販(ID) | `id_data_resale_id` | VARCHAR | 1 | － | - |
| 【IS(NI・物販)】再販(IS) | `is_ni_product_sales_resale_is` | VARCHAR | 1 | － | - |
| 先行発注 | `pre_order` | VARCHAR | 1 | － | - |
| 再販契約(データ) | `reseller_contract_data` | VARCHAR | 1 | － | - |
| 契約締結(単独) | `contract_conclusion_single` | VARCHAR | 1 | － | - |
| 社外文書提出 | `external_document_submission` | VARCHAR | 1 | － | - |
| NDA契約 | `nda_agreement` | VARCHAR | 1 | － | - |
| その他 | `other_type` | VARCHAR | 1 | － | - |
| 起案者名 | `originators_name` | VARCHAR | 765 | － | - |
| 起案者電話番号 | `originators_phone_number` | VARCHAR | 765 | － | - |
| 起案者の所属組織情報一覧 | `affiliated_org_address_list` | VARCHAR | 12000 | － | - |
| 情報元集約シート | `source_aggregation_sheet_info` | VARCHAR | 240 | － | - |
| 集約番号 | `aggregation_number` | VARCHAR | 765 | － | - |
| 実行予定日（提案/処理依頼予定日) | `scheduled_execution_date` | VARCHAR | 10 | － | YYYY-MM-DD |
| 決裁書有効期間（ヶ月） | `approval_document_period_months` | VARCHAR | 765 | － | - |
| 与信アラート | `credit_alert` | VARCHAR | 765 | － | - |
| 与信審査実施有無 | `whether_credit_review` | VARCHAR | 765 | － | - |
| 与信審査依頼名（COMPASS） | `credit_review_request_name_compass` | VARCHAR | 765 | － | - |
| 与信審査依頼名（BFS） | `credit_review_request_name_bfs` | VARCHAR | 765 | － | - |
| 法務事前審査実施有無 | `whether_legal_pre_review_conducted` | VARCHAR | 765 | － | - |
| 法務事前審査依頼番号 | `legal_pre_review_request_number` | VARCHAR | 765 | － | - |
| 再決裁・起案フラグ | `re_approval_draft_flag` | VARCHAR | 765 | － | - |
| サービス種別 | `service_type` | VARCHAR | 765 | － | - |
| 販路 | `sales_channel` | VARCHAR | 765 | － | - |
| 法個人区分 | `legal_personal_classification` | VARCHAR | 765 | － | - |
| 請求形態 | `billing_form` | VARCHAR | 765 | － | - |
| 代理店協業の条件 | `agency_collaboration_conditions` | VARCHAR | 765 | － | - |
| 水際支払金額 | `borderline_payment_amount` | VARCHAR | 765 | － | - |
| 決裁前事前承認フラグ | `pre_approval_flag` | VARCHAR | 765 | － | - |
| 承認を受けた者の氏名 | `name_of_approved_person` | VARCHAR | 765 | － | - |
| 事後決裁となった理由 | `reason_for_post_approval` | VARCHAR | 12000 | － | - |
| 承認者 | `approver` | VARCHAR | 765 | － | - |
| 申請者 | `applicant` | VARCHAR | 765 | － | - |
| 承認ルートとして利用する組織（起案者の本務/兼務） | `orgl_route_proposers_duties` | VARCHAR | 765 | － | - |
| 承認ルートとして利用する組織（営業担当者の本務/兼務） | `orgl_route_sales_duties` | VARCHAR | 765 | － | - |
| 営業担当者の所属組織情報一覧 | `sales_representatives_list` | VARCHAR | 12000 | － | - |
| 包括決裁 | `comprehensive_approval` | VARCHAR | 1 | － | - |
| グループ包括決裁 | `group_comprehensive_approval` | VARCHAR | 1 | － | - |
| 他案件で利用 | `used_in_other_projects` | VARCHAR | 1 | － | - |
| 担当者名 | `contact_name` | VARCHAR | 765 | － | - |
| 担当者電話番号 | `contact_phone_number` | VARCHAR | 765 | － | - |
| 事前相談有無 | `pre_confirmation` | VARCHAR | 765 | － | - |
| 決裁事前相談名 | `pre_approval_consultation_name` | VARCHAR | 765 | － | - |
| 案件名 | `project_name` | VARCHAR | 765 | － | - |
| 案件ID | `project_id` | VARCHAR | 765 | － | - |
| 企業名 | `company_name` | VARCHAR | 765 | － | - |
| 統一企業コード | `uniform_company_code` | VARCHAR | 765 | － | - |
| TSR評点 | `tsr_rating` | VARCHAR | 765 | － | - |
| 回線数 | `number_of_lines` | DECIMAL | 18,0 | － | - |
| 契約期間（ヶ月） | `contract_period_months` | DECIMAL | 18,0 | － | - |
| 契約開始予定日 | `contract_start_date` | VARCHAR | 10 | － | YYYY-MM-DD |
| SBTM直轄現調・開通立会い回線数 | `number_of_lines_attended_opening` | DECIMAL | 18,0 | － | - |
| 開通工事費無料 | `activation_installation_fee` | VARCHAR | 765 | － | - |
| 番ポ工事費＋付加サービス_工事費無料 | `free_installation_and_additional_service_fee` | VARCHAR | 765 | － | - |
| 負担内容1 | `free_installation_fee` | VARCHAR | 12000 | － | - |
| 負担費用　月額1（円） | `banner_installation_fee_additional_services` | DECIMAL | 18,0 | － | - |
| 負担費用　一時金1（円） | `cost_1` | DECIMAL | 18,0 | － | - |
| 負担内容2 | `cost_monthly_per_yen1` | VARCHAR | 12000 | － | - |
| 負担費用　月額2（円） | `cost_lump_sum_per_yen1` | DECIMAL | 18,0 | － | - |
| 負担費用　一時金2（円） | `cost_monthly_per_yen2` | DECIMAL | 18,0 | － | - |
| 負担内容3 | `cost_lump_sum_per_yen2` | VARCHAR | 12000 | － | - |
| 負担費用　月額3（円） | `cost_monthly_per_yen3` | DECIMAL | 18,0 | － | - |
| 負担費用　一時金3（円） | `cost_lump_sum_per_yen3` | DECIMAL | 18,0 | － | - |
| 提案種別 | `proposal_type` | VARCHAR | 765 | － | - |
| 案件概要①（要旨記述） | `project_summary_1_summary` | VARCHAR | 12000 | － | - |
| 案件概要②（要旨記述・その他） | `project_summary_2_summary` | VARCHAR | 12000 | － | - |
| 見込回線数（上限） | `other` | DECIMAL | 18,0 | － | - |
| 適用プラン | `expected_number_of_lines_maximum` | VARCHAR | 765 | － | - |
| 割引率（％） | `applicable_platform_discount_rate_percent` | DECIMAL | 18,0 | － | - |
| チャネル | `channel` | VARCHAR | 765 | － | - |
| 減免有無 | `exemption_deduction` | VARCHAR | 765 | － | - |
| 減免額（円） | `exemption_amount_yen` | DECIMAL | 18,0 | － | - |
| 売上（円） | `sales_yen` | DECIMAL | 18,0 | － | - |
| 営業変動利益（円） | `variable_operating_profit_yen` | DECIMAL | 18,0 | － | - |
| 営業変動利益率（％） | `variable_operating_profit_margin_percent` | DECIMAL | 18,0 | － | - |
| 営業貢献利益（円） | `operating_contribution_margin_yen` | DECIMAL | 18,0 | － | - |
| 営業貢献利益率（％） | `operating_contribution_margin_margin_percent` | DECIMAL | 18,0 | － | - |
| 営業利益（円） | `operating_profit_yen` | DECIMAL | 18,0 | － | - |
| 営業利益率（％） | `operating_profit_margin_percent` | DECIMAL | 18,0 | － | - |
| 音声営業貢献利益（円） | `voice_sales_contribution_margin_yen` | DECIMAL | 18,0 | － | - |
| 音声営業貢献利益率（％） | `voice_sales_contribution_margin_margin_percent` | DECIMAL | 18,0 | － | - |
| ID(データ)決裁基準利益（円） | `id_data_approval_base_profit_yen` | DECIMAL | 18,0 | － | - |
| ID(データ)決裁基準利益率（％） | `id_data_approval_base_profit_margin_percent` | DECIMAL | 18,0 | － | - |
| IS(NI・物販)決裁基準利益（円） | `is_ni_product_sales_approval_base_profit_yen` | DECIMAL | 18,0 | － | - |
| IS(NI・物販)決裁基準利益率（％） | `is_ni_product_sales_approval_base_profit_margin_percent` | DECIMAL | 18,0 | － | - |
| モバイル営業貢献利益（円） | `mobile_sales_contribution_margin_yen` | DECIMAL | 18,0 | － | - |
| モバイル営業貢献利益率（％） | `mobile_sales_contribution_margin_margin_percent` | DECIMAL | 18,0 | － | - |
| 代理店情報手入力フラグ | `agency_information_manual_input_flag` | VARCHAR | 1 | － | - |
| 代理店名（参照） | `agency_name_reference` | VARCHAR | 765 | － | - |
| 代理店名（試算） | `agency_name_estimate` | VARCHAR | 765 | － | - |
| 代理店コード | `agency_code` | VARCHAR | 54 | － | - |
| 手数料率（％） | `commission_rate_percent_incent` | DECIMAL | 18,0 | － | - |
| インセンティブ額（円） | `incentive_amount_yen` | DECIMAL | 18,0 | － | - |
| 協業理由 | `reason_for_collaboration` | VARCHAR | 12000 | － | - |
| 自動更新有無 | `automatic_renewal` | VARCHAR | 765 | － | - |
| SBM回線数（上限） | `sbm_line_count_upper` | DECIMAL | 18,0 | － | - |
| SBM回線数（下限） | `sbm_line_count_lower` | DECIMAL | 18,0 | － | - |
| ﾓﾊﾞｲﾙ(YM)回線数(上限) | `mobile_ym_line_count_upper` | DECIMAL | 18,0 | － | - |
| ﾓﾊﾞｲﾙ(YM)回線数(下限） | `mobile_ym_line_count_lower` | DECIMAL | 18,0 | － | - |
| 外部支出総額・仕入額（円） | `total_external_expenses_purchases_yen` | DECIMAL | 18,0 | － | - |
| 音声(おとく光電話)営業貢献利益（円） | `voice_otoku_hikari_phone_sales_contribution_margin_yen` | DECIMAL | 18,0 | － | - |
| 音声(おとく光電話)営業貢献利益率（％） | `voice_otoku_hikari_phone_sales_contribution_margin_rate_percent` | DECIMAL | 18,0 | － | - |
| 減免・調整・返還・回収金額（円） | `deduction_adjustment_refund_recovery_amount_yen` | DECIMAL | 18,0 | － | - |
| 外部支出総額（円） | `total_external_expenses_yen` | DECIMAL | 18,0 | － | - |
| 対象期間 | `applicable_period` | VARCHAR | 765 | － | - |
| 支払い時期 | `payment_date` | VARCHAR | 765 | － | - |
| 売上総合計金額（円） | `total_sales_amount_yen` | DECIMAL | 18,0 | － | - |
| 請求書再発行有無 | `invoice_reissue` | VARCHAR | 765 | － | - |
| 関連する決裁（COMPASS） | `related_approvals_compass` | VARCHAR | 765 | － | - |
| 稟議申請番号（COMPASS以外） | `approval_request_number_other_than_compass` | VARCHAR | 765 | － | - |
| ソリューション販売管理システム見積番号 | `solution_sales_management_system_quote_number` | DECIMAL | 18,0 | － | - |
| アセットDB番号 | `asset_db_number` | VARCHAR | 765 | － | - |
| 代理店申請書番号 | `agency_application_number` | VARCHAR | 765 | － | - |
| 代理店申請書番号（SDWF） | `agency_application_number_sd_wf` | VARCHAR | 765 | － | - |
| 備考 | `notes` | VARCHAR | 12000 | － | - |
| 閲覧範囲 | `viewability` | VARCHAR | 765 | － | - |
| 追加・変更内容 | `additions_changes` | VARCHAR | 12000 | － | - |
| 入力者 | `inputter` | VARCHAR | 765 | － | - |
| 入力日 | `input_date` | VARCHAR | 765 | － | - |
| 契約化必須条件1 | `contractual_condition_1` | VARCHAR | 12000 | － | - |
| 契約化必須条件2 | `contractual_condition_2` | VARCHAR | 12000 | － | - |
| フローから子決裁作成フラグ | `create_sub_approval_from_flow_flag` | VARCHAR | 1 | － | - |
| 非公開フラグ | `private_flag` | VARCHAR | 1 | － | - |
| 承認日時 | `approval_date` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 事業区分 | `business_category` | VARCHAR | 765 | － | - |
| 有効期限 | `expiration_date` | VARCHAR | 10 | － | YYYY-MM-DD |
| 追加情報欄 | `additional_information_field` | VARCHAR | 12000 | － | - |
| 基となる提案決裁 | `based_proposal_approval` | VARCHAR | 240 | － | - |
| 決裁内容 | `approval_content` | VARCHAR | 765 | － | - |
| 承認ルート基準 | `approval_route_criteria` | VARCHAR | 765 | － | - |
| 仕入先与信 | `supplier_credit` | VARCHAR | 240 | － | - |
| 有効 | `valid_flg` | VARCHAR | 1 | － | - |
| レコードID（数式） | `record_id_formula` | VARCHAR | 3900 | － | - |
| 作成者ID | `creator_id` | VARCHAR | 765 | － | - |
| 作成日 | `creation_date` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 削除 | `deleted_flg` | VARCHAR | 1 | － | - |
| 最終更新者ID | `last_updated_by_id` | VARCHAR | 765 | － | - |
| 最終更新日 | `last_updated_date` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終参照日 | `last_reference_date` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終閲覧日 | `last_viewed_date` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 所有者ID | `owner_id` | VARCHAR | 765 | － | - |
| レコードタイプID | `record_type_id` | VARCHAR | 3900 | － | - |
| SystemModstamp | `systemmodstamp` | VARCHAR | 23 | － | YYYY-MM-DD HH24:MI:SS.mmm |
| 試算シート番号 | `estimate_sheet_number` | VARCHAR | 12000 | － | - |
| SUMMITデータ移行フラグ | `summit_data_migration_flag` | VARCHAR | 1 | － | - |
| 与信審査依頼名（COMPASS）有無判定 | `credit_review_request_name_compass_presence_absence` | VARCHAR | 1 | － | - |
| 試算シート有無 | `estimate_sheet_presence_absence` | VARCHAR | 765 | － | - |
| プロダクト事前相談 | `product_pre_consultation` | VARCHAR | 765 | － | - |
| モバイル相対相談承認条件 | `mobile_p2p_consultation_approval_conditions` | VARCHAR | 12000 | － | - |
| 事前相談承認条件 | `pre_consultation_approval_conditions` | VARCHAR | 12000 | － | - |
| 要旨補足（申請者専用） | `summary_supplement_applicant_only` | VARCHAR | 12000 | － | - |
| 承認日時（UnixTime） | `approval_date_and_time_unixtime` | VARCHAR | 765 | － | - |
| コメント１ | `comment_1` | VARCHAR | 12000 | － | - |
| コメント２ | `comment_2` | VARCHAR | 12000 | － | - |
| コメント３ | `comment_3` | VARCHAR | 12000 | － | - |
| コメント４ | `comment_4` | VARCHAR | 12000 | － | - |
| コメント５ | `comment_5` | VARCHAR | 12000 | － | - |
| 共有用メールアドレス① | `shared_email_address_1` | VARCHAR | 150 | － | - |
| 共有用メールアドレス② | `shared_email_address_2` | VARCHAR | 150 | － | - |
| 共有用メールアドレス③ | `shared_email_address_3` | VARCHAR | 150 | － | - |
| 起案者共通社員番号 | `proposers_common_employee_id` | VARCHAR | 765 | － | - |
| 起案者部署 | `proposers_dept` | VARCHAR | 765 | － | - |
| 起案部署_組織コード(本部) | `proposal_dept_org_code_headquarters` | VARCHAR | 765 | － | - |
| 起案部署_組織コード(統括部) | `proposal_dept_org_general_affairs_dept` | VARCHAR | 765 | － | - |
| 起案部署_組織コード(部) | `proposal_dept_org_code_dept` | VARCHAR | 765 | － | - |
| 申請者（グループ名） | `applicants_group_name` | VARCHAR | 765 | － | - |
| 申請者（ユーザーID） | `applicants_user_id` | VARCHAR | 765 | － | - |
| 申請者（ユーザー名） | `applicants_user_name` | VARCHAR | 765 | － | - |
| 同意者（グループ名） | `consenters_group_name` | VARCHAR | 765 | － | - |
| 同意者（ユーザーID） | `consenters_user_id` | VARCHAR | 765 | － | - |
| 同意者（ユーザー名） | `consenters_user_name` | VARCHAR | 765 | － | - |
| 承認者のレイヤー | `approvers_layer` | VARCHAR | 765 | － | - |
| 承認者（グループ名） | `approvers_group_name` | VARCHAR | 765 | － | - |
| 承認者（ユーザーID） | `approvers_user_id` | VARCHAR | 765 | － | - |
| 承認者（ユーザー名） | `approvers_user_name` | VARCHAR | 765 | － | - |
| 最終処理日時 | `last_processing_date_and_time` | VARCHAR | 765 | － | - |
| 承認履歴 | `approval_history` | VARCHAR | 12000 | － | - |

## 制約

- 主キー: なし
