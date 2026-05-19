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
| 決裁番号 | `name` | VARCHAR | 80 | ⚪︎ | - |
| 決裁件名 | `salesapprovaltitle` | VARCHAR | 255 | ⚪︎ | - |
| ステータス | `status` | VARCHAR | 255 | ⚪︎ | いずれか（承認、差戻し、取り下げ、申請者確認中、承認者確認中、条件付き承認、同意者確認中、否決 |
| 申請日時 | `applicationdate` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 決裁種別 | `paymenttype` | VARCHAR | 255 | ⚪︎ | - |
| モバイル | `mobile` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 音声 | `voice` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 音声(おとく光電話) | `voicediscount` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| ID(データ) | `dataid` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| IS(NI・物販) | `isniproduct` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| PHS | `phs` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】値引きなど | `discount` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】法人まとめ請求 | `companybill` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】試験用回線 | `testline` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【モバイル】決裁パターンA(試算シートの利益率判断) | `decisionpatterna` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】決裁パターンC(試算シートを必要としない減免) | `decisionpatternc` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】決裁パターンE | `decisionpatterne` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】インセンティブ調整(増減額) | `incentiveadjust` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】再販又はレンタル事業者へのサービス提供 | `serviceprovisionresalerental` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【モバイル】預託金・連帯保証・与信緩和 | `depositguaranteecreditrelax` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【共通】QAレビュー実施案件 | `qareviewcase` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】特殊な債権回収条件(支払いサイトの変更) | `specialdebtcollectioncond` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【共通】建設業法に関わる工事案件 | `constructionworklaw` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 水際処理・代理店コード変更 | `borderprocessingagentcode` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 料金調整・現金返還・料金減免 | `feeadjustcashrefundreduction` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 代理店契約 | `agencycontract` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【ID(データ)】ODNコンシューマ仕様 | `odnconsumerspec` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 再販契約 | `resalecontract` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 【ID(データ)】課金テーブル設定 | `billingtablesetup` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 料率・インセンティブ設定 | `rateincentivesetup` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 損害補填目的での料金調整 | `feeadjustfordamagecomp` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 決裁特別施策(モバイル黒字) | `specialapprovalmobileprofit` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 契約締結(提案決裁承認後) | `contractafterproposalapproval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| みなし法人 | `deemedcorporation` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 仕入れ販売(300万円以下＆黒字) | `purchasesaleunder3mprofit` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| データ系再販(手数料型) | `dataresalecommissiontype` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【共通】特殊値引(特別タリフ・個別タリフなど) | `specialdiscounttariff` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【ID(データ)】再販(ID) | `resaleid` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 【IS(NI・物販)】再販(IS) | `resaleis` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 先行発注 | `advanceorder` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 再販契約(データ) | `resalecontractdata` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 契約締結(単独) | `contractsingle` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 社外文書提出 | `externaldocsubmission` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| NDA契約 | `ndacontract` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| その他 | `otherapprovalcontent` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 起案者名 | `recordcreatorname` | VARCHAR | 255 | ⚪︎ | - |
| 起案者電話番号 | `recordcreatorphone` | VARCHAR | 255 | - | - |
| 起案者の所属組織情報一覧 | `recordcreatordeplist` | VARCHAR | 12000 | ⚪︎ | - |
| 情報元集約シート | `aggregatequotation` | VARCHAR | 80 | ⚪︎ | - |
| 集約番号 | `aggregationnumber` | VARCHAR | 255 | ⚪︎ | - |
| 実行予定日（提案/処理依頼予定日) | `executionschedule` | VARCHAR | 10 | ⚪︎ | YYYY-MM-DD |
| 決裁書有効期間（ヶ月） | `documentvalidity` | VARCHAR | 255 | ⚪︎ | - |
| 与信アラート | `creditalert` | VARCHAR | 255 | - | 有 / 無 |
| 与信審査実施有無 | `creditscreeningexecuted` | VARCHAR | 255 | - |  有 / 無 |
| 与信審査依頼名（COMPASS） | `creditscreeningrequestnamesummit` | VARCHAR | 255 | - | - |
| 与信審査依頼名（BFS） | `creditscreeningrequestnamebfs` | VARCHAR | 255 | - | - |
| 法務事前審査実施有無 | `legalpreauditexecuted` | VARCHAR | 255 | - |  有 / 無 |
| 法務事前審査依頼番号 | `legalprecheckrequestno` | VARCHAR | 255 | - | - |
| 再決裁・起案フラグ | `resalesapprovalflag` | VARCHAR | 255 | - |  有 / 無 |
| サービス種別 | `servicetype` | VARCHAR | 255 | ⚪︎ | - |
| 販路 | `saleschannel` | VARCHAR | 255 | ⚪︎ | - |
| 法個人区分 | `personaldivision` | VARCHAR | 255 | -︎ | - |
| 請求形態 | `billingtype` | VARCHAR | 255 | ⚪︎ | - |
| 代理店協業の条件 | `agencycollabconditions` | VARCHAR | 255 | ⚪︎ | - |
| 水際支払金額 | `paymentamount` | VARCHAR | 255 | ⚪︎ | - |
| 決裁前事前承認フラグ | `preapprovalflag` | VARCHAR | 255 | - | - |
| 承認を受けた者の氏名 | `approvername` | VARCHAR | 255 |  -︎ | - |
| 事後決裁となった理由 | `postsalesapprovalreason` | VARCHAR | 12000 | - | - |
| 承認者 | `approver` | VARCHAR | 255 | ⚪︎ | - |
| 申請者 | `applicant` | VARCHAR | 255 | ⚪︎ | - |
| 承認ルートとして利用する組織（起案者の本務/兼務） | `recordcreatordepselect` | VARCHAR | 255 | - | - |
| 承認ルートとして利用する組織（営業担当者の本務/兼務） | `salesrepresentativedepselect` | VARCHAR | 255 | - | - |
| 営業担当者の所属組織情報一覧 | `salesrepresentativedeplist` | VARCHAR | 12000 | - | - |
| 包括決裁 | `comprehensivesalesapproval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| グループ包括決裁 | `groupsalesapproval` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 他案件で利用 | `useothercases` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE  |
| 担当者名 | `responsiblename` | VARCHAR | 255 | - | - |
| 担当者電話番号 | `responsiblephone` | VARCHAR | 255 | - | - |
| 事前相談有無 | `preconsultationexists` | VARCHAR | 255 | - | 有 / 無 |
| 決裁事前相談名 | `preconsultationname` | VARCHAR | 255 | ︎- | - |
| 案件名 | `opportunity` | VARCHAR | 255 | - | - |
| 案件ID | `opportunityid` | VARCHAR | 255 | - | - |
| 企業名 | `account` | VARCHAR | 255 | ⚪︎ | - |
| 統一企業コード | `accountcode` | VARCHAR | 255 | ⚪︎ | - |
| TSR評点 | `tsrscore` | VARCHAR | 255 | - | - |
| 回線数 | `linecount` | DECIMAL |  18,0 | - | - |
| 契約期間（ヶ月） | `contractperiod` | DECIMAL | 18,0 | -︎ | - |
| 契約開始予定日 | `plannedstartdate` | VARCHAR | 10 | - | YYYY-MM-DD |
| SBTM直轄現調・開通立会い回線数 | `directmaintlinecount` | DECIMAL | 18,0 | - | - |
| 開通工事費無料 | `constructionfeefree` | VARCHAR | 255 | - | 有 / 無 |
| 番ポ工事費＋付加サービス_工事費無料 | `constructionfeewithservices` | VARCHAR | 255 | - | - |
| 負担内容1 | `burdencontent1` | VARCHAR | 12000 | - | - |
| 負担費用　月額1（円） | `monthlycost1` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金1（円） | `onetimecost1` | DECIMAL | 18,0 | - | - |
| 負担内容2 | `burdencontent2` | VARCHAR | 12000 | - | - |
| 負担費用　月額2（円） | `monthlycost2` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金2（円） | `onetimecost2` | DECIMAL | 18,0 | - | - |
| 負担内容3 | `burdencontent3` | VARCHAR | 12000 | - | - |
| 負担費用　月額3（円） | `monthlycost3` | DECIMAL | 18,0 | - | - |
| 負担費用　一時金3（円） | `onetimecost3` | DECIMAL | 18,0 | - | - |
| 提案種別 | `proposaltype` | VARCHAR | 255 | - | いずれか（既存追加、機種変更、機変＆提供条件変更、新規、追加新規、提供条件変更、（空白）） |
| 案件概要①（要旨記述） | `casesummary1` | VARCHAR | 12000 | ⚪︎ | - |
| 案件概要②（要旨記述・その他） | `casesummary2` | VARCHAR | 12000 | ⚪︎ | - |
| 見込回線数（上限） | `estimatedlinecountmax` | DECIMAL | 18,0 | - | - |
| 適用プラン | `applicableplan` | VARCHAR | 255 | - | - |
| 割引率（％） | `discountrate` | DECIMAL | 18,0 | - | - |
| チャネル | `channel` | VARCHAR | 255 | - | - |
| 減免有無 | `waiverexists` | VARCHAR | 255 | - | 有 / 無 |
| 減免額（円） | `waiveramount` | DECIMAL | 18,0 | - | - |
| 売上（円） | `revenue` | DECIMAL | 18,0 | - | - |
| 営業変動利益（円） | `variableprofit` | DECIMAL | 18,0 | - | - |
| 営業変動利益率（％） | `variableprofitrate` | DECIMAL | 18,0 | - | - |
| 営業貢献利益（円） | `contributionprofit` | DECIMAL | 18,0 | - | - |
| 営業貢献利益率（％） | `contributionprofitrate` | DECIMAL | 18,0 | - | - |
| 営業利益（円） | `operatingprofit` | DECIMAL | 18,0 | - | - |
| 営業利益率（％） | `operatingprofitrate` | DECIMAL | 18,0 | - | - |
| 音声営業貢献利益（円） | `voicecontributionprofit` | DECIMAL | 18,0 | - | - |
| 音声営業貢献利益率（％） | `voicecontributionprofitrate` | DECIMAL | 18,0 | - | - |
| ID(データ)決裁基準利益（円） | `id_datasalesapprovalprofit` | DECIMAL | 18,0 | - | - |
| ID(データ)決裁基準利益率（％） | `id_datasalesapprovalprofitrate` | DECIMAL | 18,0 | - | - |
| IS(NI・物販)決裁基準利益（円） | `is_ni_productprofit` | DECIMAL | 18,0 | - | - |
| IS(NI・物販)決裁基準利益率（％） | `is_ni_productprofitrate` | DECIMAL | 18,0 | - | - |
| モバイル営業貢献利益（円） | `mobilecontributionprofit` | DECIMAL | 18,0 | - | - |
| モバイル営業貢献利益率（％） | `mobilecontributionprofitrate` | DECIMAL | 18,0 | - | - |
| 代理店情報手入力フラグ | `agencyinputflag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 代理店名（参照） | `agencyname` | VARCHAR | 255 | - | - |
| 代理店名（試算） | `agencynameaggregatequotation` | VARCHAR | 255 | - | - |
| 代理店コード | `agencycode` | VARCHAR | 54 | - | - |
| 手数料率（％） | `commissionrate` | DECIMAL | 18,0 | - | - |
| インセンティブ額（円） | `incentiveamount` | DECIMAL | 18,0 | - | - |
| 協業理由 | `collaborationreason` | VARCHAR | 12000 | - | - |
| 自動更新有無 | `autorenewexists` | VARCHAR | 255 | ⚪︎ | 有 / 無 |
| SBM回線数（上限） | `sbmlinecountmax` | DECIMAL | 18,0 | - | - |
| SBM回線数（下限） | `sbmlinecountmin` | DECIMAL | 18,0 | - | - |
| ﾓﾊﾞｲﾙ(YM)回線数(上限) | `mobileymlinecountmax` | DECIMAL | 18,0 | - | - |
| ﾓﾊﾞｲﾙ(YM)回線数(下限） | `mobileymlinecountmin` | DECIMAL | 18,0 | - | - |
| 外部支出総額・仕入額（円） | `totalexternalcost_supplies` | DECIMAL | 18,0 | - | - |
| 音声(おとく光電話)営業貢献利益（円） | `voiceprofit` | DECIMAL | 18,0 | ︎- | - |
| 音声(おとく光電話)営業貢献利益率（％） | `voiceprofitrate` | DECIMAL | 18,0 | - | - |
| 減免・調整・返還・回収金額（円） | `waiveradjustmentamount` | DECIMAL | 18,0 | - | - |
| 外部支出総額（円） | `totalexternalcost` | DECIMAL | 18,0 | - | - |
| 対象期間 | `targetperiod` | VARCHAR | 255 | - | - |
| 支払い時期 | `paymenttiming` | VARCHAR | 255 | - | - |
| 売上総合計金額（円） | `totalrevenue` | DECIMAL | 18,0 | - | - |
| 請求書再発行有無 | `reissueinvoiceexists` | VARCHAR | 255 | - | - |
| 関連する決裁（COMPASS） | `relatedsalesapproval` | VARCHAR | 255 | - | 決裁番号を "," 区切りで入力 |
| 稟議申請番号（COMPASS以外） | `approvalnumber` | VARCHAR | 255 | - | - |
| ソリューション販売管理システム見積番号 | `solutionestimatenumber` | DECIMAL | 18,0 | - | - |
| アセットDB番号 | `assetdbnumber` | VARCHAR | 255 | - | - |
| 代理店申請書番号 | `agencyapplicationnumber` | VARCHAR | 255 | - | - |
| 代理店申請書番号（SDWF） | `agencyapplicationnumber_sdw` | VARCHAR | 255 | ⚪︎ | - |
| 備考 | `remarks` | VARCHAR | 12000 | - | - |
| 閲覧範囲 | `viewingscope` | VARCHAR | 255 | - | - |
| 追加・変更内容 | `addchangecontent` | VARCHAR | 12000 | - | - |
| 入力者 | `inputperson` | VARCHAR | 255 | - | - |
| 入力日 | `inputdate` | VARCHAR | 255 | - | - |
| 契約化必須条件1 | `contractrequiredcondition1` | VARCHAR | 12000 | - | - |
| 契約化必須条件2 | `contractrequiredcondition2` | VARCHAR | 12000 | - | - |
| フローから子決裁作成フラグ | `createdecisionflag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 非公開フラグ | `isprivateflag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 承認日時 | `approveddate` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm  |
| 事業区分 | `businesstype` | VARCHAR | 255 | ⚪︎ | - |
| 有効期限 | `expirationdate` | VARCHAR | 10 | - | YYYY-MM-DD |
| 追加情報欄 | `addedinformation` | VARCHAR | 12000 | - | - |
| 基となる提案決裁 | `salesapprovalbased` | VARCHAR | 240 | - | - |
| 決裁内容 | `salesapprovaldetails` | VARCHAR | 255 | ⚪︎ | - |
| 承認ルート基準 | `applicantconsenterapproverset` | VARCHAR | 255 | ⚪︎ | - |
| 仕入先与信 | `suppliercsr` | VARCHAR | 80 | ⚪︎ | - |
| 有効 | `isvalid` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| レコードID（数式） | `recordid_formula` | VARCHAR | 1300 | ⚪︎ | - |
| 作成者ID | `createdbyid` | VARCHAR | 255 | ⚪︎ | - |
| 作成日 | `createddate` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm  |
| 削除 | `isdeleted` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 最終更新者ID | `lastmodifiedbyid` | VARCHAR | 255 | ⚪︎ | - |
| 最終更新日 | `lastmodifieddate` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終参照日 | `lastreferenceddate` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm |
| 最終閲覧日 | `lastvieweddate` | VARCHAR | 23 | - | YYYY-MM-DD HH24:MI:SS.mmm  |
| 所有者ID | `ownerid` | VARCHAR | 255 | ⚪︎ | - |
| レコードタイプID | `recordtypeid` | VARCHAR | 3900 | ⚪︎ | - |
| SystemModstamp | `systemmodstamp` | VARCHAR | 23 | ⚪︎ | YYYY-MM-DD HH24:MI:SS.mmm |
| 試算シート番号 | `quotationnumber` | VARCHAR | 12000 | - | - |
| SUMMITデータ移行フラグ | `smt_datamigrationflag` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 与信審査依頼名（COMPASS）有無判定 | `csrnamesummitexists` | VARCHAR | 5 | ⚪︎ | TRUE / FALSE |
| 試算シート有無 | `aggregatequotationexisted` | VARCHAR | 255 | ⚪︎ | 有 / 無 |
| プロダクト事前相談 | `priorconsofproduct` | VARCHAR | 255 | - | - |
| モバイル相対相談承認条件 | `sbmreviewcomments` | VARCHAR | 12000 | - | - |
| 事前相談承認条件 | `priorconsapprovalconditions` | VARCHAR | 12000 | - | - |
| 要旨補足（申請者専用） | `summarysupplement` | VARCHAR | 12000 | - | - |
| 承認日時（UnixTime） | `approveddateunixtime` | VARCHAR | 255 | - | 承認時のみ入力 unix time形式 |
| コメント１ | `comment1` | VARCHAR | 12000 | - | - |
| コメント２ | `comment2` | VARCHAR | 12000 | ︎- | - |
| コメント３ | `comment3` | VARCHAR | 12000 | - | - |
| コメント４ | `comment4` | VARCHAR | 12000 | - | - |
| コメント５ | `comment5` | VARCHAR | 12000 | - | - |
| 共有用メールアドレス① | `share_address_1` | VARCHAR | 150 | - | - |
| 共有用メールアドレス② | `share_address_2` | VARCHAR | 150 | - | - |
| 共有用メールアドレス③ | `share_address_3` | VARCHAR | 150 | - | - |
| 起案者共通社員番号 | `creatorcommonemployeeid` | VARCHAR | 255 | ⚪︎ | - |
| 起案者部署 | `recordcreatororganizationofficialnm` | VARCHAR | 255 | ⚪︎ | - |
| 起案部署_組織コード(本部) | `proposaldep_orgcd4` | VARCHAR | 255 | - | - |
| 起案部署_組織コード(統括部) | `proposaldep_orgcd5` | VARCHAR | 255 | - | - |
| 起案部署_組織コード(部) | `proposaldep_orgcd6` | VARCHAR | 255 | - | - |
| 申請者（グループ名） | `applicantgroupname` | VARCHAR | 255 | - | - |
| 申請者（ユーザーID） | `applicantuserid` | VARCHAR | 255 | - | - |
| 申請者（ユーザー名） | `applicantusername` | VARCHAR | 255 | - | - |
| 同意者（グループ名） | `consentergroupname` | VARCHAR | 255 | - | - |
| 同意者（ユーザーID） | `consenteruserid` | VARCHAR | 255 | - | - |
| 同意者（ユーザー名） | `consenterusername` | VARCHAR | 255 | - | - |
| 承認者のレイヤー | `approverlayer` | VARCHAR | 255 | - | - |
| 承認者（グループ名） | `approvergroupname` | VARCHAR | 255 | - | - |
| 承認者（ユーザーID） | `approveruserid` | VARCHAR | 255 | - | - |
| 承認者（ユーザー名） | `approverusername` | VARCHAR | 255 | - | - |
| 最終処理日時 | `finalprocessingdate` | VARCHAR | 255 | - | - |
| 承認履歴 | `approvalhistory` | VARCHAR | 12000 | - | - |

## 制約

- 主キー: なし
