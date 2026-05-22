# (DWH)統一企業情報

- マート名: `m_hjn_smt_統一企業情報`
- CSVファイル名: 
  - 初期データ: `YYYYMMDD_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_1.csv`, `YYYYMMDD_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_2.csv`
  - 差分データ: `YYYYMMDD_DLV_OAI_SMT_DV_SMT_MST_UNIQ_CORP_IE_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 全件（300万件）、差分更新（46,021件）
- データ量: 全件（800MB）、差分更新（34.02MB）
- データ概要: SUMMITの統一企業情報を保有。
- 参考データ: `sample_data/corp_customer_info.csv`
- 補足: 初期データは二分割すること

## 差分データの考え方

- `m_hjn_smt_統一企業情報_diff.csv` は `diff_type` 列を持たない。
- 新規追加行は初期データ2ファイルに存在しない `統一企業コード` を使う。
- 既存更新行は初期データ2ファイルに存在する `統一企業コード` を使う。
- 削除行は出力しない。

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | 必須 | 説明 |
| --- | --- | --- | --- | --- | --- |
| 統一企業コード | `uniq_corp_cd` | NVARCHAR | 54 | ○ | 統一企業ｺｰﾄﾞ＝AM企業ｺｰﾄﾞ |
| 法人管理番号 | `h_no` | NVARCHAR | 90 | － | WILLCOM企業番号 |
| dunsnumber | `teikoku_db_kigyo_bng` | NVARCHAR | 90 | － | 企業ｺｰﾄﾞ TSRから購入した情報のため、社外提供NG |
| 法人格コード | `hojinkaku_flg` | NVARCHAR | 18 | － | 00：法人格無し・その他法人 01：株式会社 02：有限会社 03：合資会社 04：合名会社 05：協同組合 06：協同組合連合会 07：協業組合 08：企業組合 09：相互会社 10：社団法人 11：学校法人 12：財団法人 13：医療法人 14：社会福祉法人 15：宗教法人 16：生活協同組合 17：農事組合法人 18：監査法人 19：特定非営利活動法人 20：企業組合 21：学校法人 22：宗教法人 23：生産組合 24：事業団 25：農事組合法人 26：森林組合 27：社会福祉法人 28：商工組合連合会 29：その他の法人 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 企業名カナ | `corp_name_kana` | NVARCHAR | 540 | ○ | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 企業名カナ全角 | `corp_name_kana_zen` | NVARCHAR | 1080 | ○ | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 企業名 | `corp_name` | NVARCHAR | 630 | ○ | 漢字商号 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 検索用企業名カナ | `kensaku_corp_kana` | NVARCHAR | 306 | － | ※ORACLE TEXT索引項目 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 検索用企業名カナ全角 | `kensaku_corp_kana_zen` | NVARCHAR | 612 | － | ※ORACLE TEXT索引項目 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 検索用企業名 | `kensaku_corp_name` | NVARCHAR | 630 | － | ※ORACLE TEXT索引項目 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 郵便番号 | `zip` | NVARCHAR | 63 | ○ | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所 | `addr` | NVARCHAR | 2340 | ○ | 漢字所在地 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所１_都道府県 | `addr1` | NVARCHAR | 90 | ○ | 都道府県 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所２_市区群町村 | `addr2` | NVARCHAR | 1800 | ○ | 市区町村 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所３_字名丁目 | `addr3` | NVARCHAR | 1800 | ○ | 詳細住所 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所４_番地 | `addr4` | NVARCHAR | 1800 | - | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 住所５_ビル建物名 | `addr5` | NVARCHAR | 1800 | － | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 電話番号 | `denwa_bng` | NVARCHAR | 117 | ○ | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 主業コード | `shugyo_cd` | NVARCHAR | 45 | － | TDB産業分類主業ｺｰﾄﾞ TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 従業コード | `jugyo_cd` | NVARCHAR | 45 | － | TDB産業分類従業ｺｰﾄﾞ TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 代表者役職名 | `daihyo_sha_yakushoku_name` | NVARCHAR | 180 | － | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 代表者氏名カナ | `daihyo_sha_kana` | NVARCHAR | 180 | － | 代表者ｶﾅ氏名 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 代表者氏名カナ全角 | `daihyo_sha_kana_zen` | NVARCHAR | 360 | － | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 代表者氏名 | `daihyo_sha_name` | NVARCHAR | 360 | － | 代表者漢字氏名 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 主業名 | `shugyo_name` | NVARCHAR | 162 | － | TDB産業分類名主業 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 従業名 | `jugyo_name` | NVARCHAR | 162 | － | TDB産業分類名従業 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 組織区分 | `soshiki_kbn` | NVARCHAR | 9 | － | - |
| 事業内容 | `jigyo_naiyo` | NVARCHAR | 2700 | － | - |
| 重要度ランク | `jyd_rank` | NVARCHAR | 18 | － | - |
| 証券コード | `shoken_cd` | NVARCHAR | 36 | － | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| ＵＲＬ | `url` | NVARCHAR | 2295 | ○ | - |
| 合併企業番号 | `gappei_corp_bng` | NVARCHAR | 54 | － | 「合併企業番号」に相当する6byteテキストエリア。「無効」かつ「合併」のときは必須入力とする。 |
| 親企業フラグ | `top_corp_flg` | NVARCHAR | 9 | － | 最上位の親は1 TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 親企業番号 | `top_corp_cd` | NVARCHAR | 54 | － | - |
| sb業種大 | `sb_ind_1` | NVARCHAR | 900 | － | - |
| sb業種中 | `sb_ind_2` | NVARCHAR | 900 | － | - |
| sb業種小 | `sb_ind_3` | NVARCHAR | 900 | － | - |
| 備考1 | `memo1` | NVARCHAR | 576 | － | WCMフラグ　1:WCM回線有 |
| 備考2 | `memo2` | NVARCHAR | 576 | － | ランドスケイプ　LBC |
| 備考3 | `memo3` | NVARCHAR | 576 | － | ランドスケイプ　医療業界コード |
| 備考4 | `memo4` | NVARCHAR | 576 | － | 未使用 |
| 備考5 | `memo5` | NVARCHAR | 576 | － | 未使用 |
| 有効無効フラグ | `disable_flg` | NVARCHAR | 9 | － | 1:無効 |
| 無効理由 | `disable_reason` | NVARCHAR | 18 | － | 「無効」の時必須入力とする。 10:合併 20:破産・倒産・清算 30:分割消滅 40:クリーニング |
| 登録日 | `toroku_date` | NVARCHAR | 69 | － | 新情報の登録日・時刻 YYYY-MM-DD HH24:MI:SS.000 |
| 更新日 | `koshin_date` | NVARCHAR | 69 | － | 新情報の更新日・時刻 YYYY-MM-DD HH24:MI:SS.000 |
| 登録者 | `toroku_sha` | NVARCHAR | 63 | － | 新情報の登録者 |
| 更新者 | `koshin_sha` | NVARCHAR | 63 | － | 新情報の更新者 |
| 削除フラグ | `del_flg` | NVARCHAR | 9 | － | 1:削除、企業一覧で表示不可 |
| 登録日時 | `regist_date` | NVARCHAR | 69 | － | SUMMITの登録日・時刻 YYYY-MM-DD HH24:MI:SS.000 |
| 更新日時 | `update_date` | NVARCHAR | 69 | － | SUMMITの更新日・時刻 YYYY-MM-DD HH24:MI:SS.000 |
| 登録者名 | `regist_nm` | NVARCHAR | 576 | － | SUMMITの登録者(ログ用) |
| 更新者名 | `update_nm` | NVARCHAR | 576 | － | SUMMITの更新者(ログ用) |
| data_universal_number | `common_corp_cd` | NVARCHAR | 81 | － | - |
| mnc_management_name | `group_addr_name_eng` | NVARCHAR | 720 | － | - |
| postal_code | `all_zip_cd` | NVARCHAR | 90 | － | - |
| country_code | `country_cd` | NVARCHAR | 27 | － | - |
| city | `city_name_eng` | NVARCHAR | 720 | － | - |
| country_calling_code | `country_tel_cd` | DECIMAL | 4 | － | - |
| district | `district_name_eng` | NVARCHAR | 1800 | － | - |
| 現地法人名_日本語 | `local_campany_name` | NVARCHAR | 1800 | － | - |
| customer_name | `local_campany_name_eng` | NVARCHAR | 1800 | － | TSRから購入した情報が含まれる可能性がある為、社外提供NG |
| 備考 | `remarks` | NVARCHAR | 6144 | － | - |
