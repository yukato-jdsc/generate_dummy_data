# (BFSエントリ)モバイル_サービスサマリ_端末

- マート名: `b_hjn_bfs_モバイル_サービスサマリ_端末`
- CSVファイル名: 
  - 初期データ: `YYYYMMDD_DLV_OAI_BFS_BFS_SERVICE_SUMMARY4.csv`
  - 差分データ: `YYYYMMDD_DLV_OAI_BFS_BFS_SERVICE_SUMMARY4_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 初期移行（1,200,000件）、日次差分（1,210件）
- データ量: 初期移行（150MB、2年分）、日次差分（0.21MB）
- データ概要: BFSのモバイル_サービスサマリ_端末情報を保有。
- 参考データ: `sample_data/bfs_service_summary_devices.csv`
- 補足: 参考CSVは502列のため、ExcelシートのうちCSV未採用の末尾2項目は記載していません。

## 差分データの考え方

- `b_hjn_bfs_モバイル_サービスサマリ_端末_diff.csv` は `diff_type` 列を持たない。
- 新規追加行のみを出力し、初期データに存在しない `エントリ番号` を使う。
- 削除行は出力しない。

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | 必須 | 説明 |
| --- | --- | --- | --- | --- | --- |
| エントリ番号 | `entry_no` | VARCHAR | 18 | ○ | - |
| サマリ番号 | `svcsm_id` | VARCHAR | 12 | ○ | - |
| 回線数 | `linenum` | DECIMAL | 10 | － | - |
| レンタルセット端末 | `rental_set_terminal_flg_nm` | VARCHAR | 765 | － | 有 / 無 |
| mnp | `mnp_flg_nm` | VARCHAR | 765 | － | 有 / 無 |
| 商品コード | `itm_cd` | VARCHAR | 15 | ○ | - |
| メーカ | `brand_nm` | VARCHAR | 600 | ○ | - |
| 移動機分類 | `itm_middle_grp_nm` | VARCHAR | 300 | ○ | - |
| 機種名 | `itm_nm` | VARCHAR | 300 | ○ | - |
| カラー1 | `color1` | VARCHAR | 300 | － | - |
| 台数1 | `num1` | DECIMAL | 10 | － | - |
| カラー2 | `color2` | VARCHAR | 300 | － | - |
| 台数2 | `num2` | DECIMAL | 10 | － | - |
| カラー3 | `color3` | VARCHAR | 300 | － | - |
| 台数3 | `num3` | DECIMAL | 10 | － | - |
| カラー4 | `color4` | VARCHAR | 300 | － | - |
| 台数4 | `num4` | DECIMAL | 10 | － | - |
| カラー5 | `color5` | VARCHAR | 300 | － | - |
| 台数5 | `num5` | DECIMAL | 10 | － | - |
| 端末標準価格 | `base_price` | DECIMAL | 10 | － | - |
| 提供代金 | `offered_price` | DECIMAL | 10 | － | - |
| 使用ポイント | `use_point` | DECIMAL | 6 | － | - |
| レンタル料 | `rental_price` | DECIMAL | 10 | － | - |
| レンタル実質提供料金 | `rental_real_offered_price` | DECIMAL | 10 | － | - |
| キャンペーン1 | `campnm1` | VARCHAR | 600 | － | - |
| キャンペーン2 | `campnm2` | VARCHAR | 600 | － | - |
| キャンペーン3 | `campnm3` | VARCHAR | 600 | － | - |
| キャンペーン4 | `campnm4` | VARCHAR | 600 | － | - |
| キャンペーン5 | `campnm5` | VARCHAR | 600 | － | - |
| 特典コード1 | `privcd1` | VARCHAR | 10 | － | - |
| 特典コード2 | `privcd2` | VARCHAR | 10 | － | - |
| 特典コード3 | `privcd3` | VARCHAR | 10 | － | - |
| 特典コード4 | `privcd4` | VARCHAR | 10 | － | - |
| 緊急キャンペーン1 | `urgecamp1` | VARCHAR | 300 | － | - |
| 緊急キャンペーン2 | `urgecamp2` | VARCHAR | 300 | － | - |
| 緊急キャンペーン3 | `urgecamp3` | VARCHAR | 300 | － | - |
| プラン | `cate01` | VARCHAR | 600 | ○ | 基本プラン（音声）、基本プラン（データ）、通話定額基本料（ケータイ）、ホワイト特別相対S、ホワイト特別相対L など |
| ホワイト法人 | `cate02` | VARCHAR | 600 | － | - |
| 通話料割引wホワイト | `cate03` | VARCHAR | 600 | － | - |
| 通話料割引ホワイトl | `cate04` | VARCHAR | 600 | － | - |
| 24時間通話定額 | `cate05` | VARCHAR | 600 | － | - |
| ホワイトオフィス | `cate06` | VARCHAR | 600 | － | - |
| 継続割引 | `cate07` | VARCHAR | 600 | － | - |
| 違約金年契 | `cate08` | VARCHAR | 600 | － | 相対2年契約10000、相対5年契約15000 など |
| sベーシックパック | `cate09` | VARCHAR | 600 | － | ウェブ使用料（無料）、ウェブ使用料（i）、ウェブ使用料なし、ウェブ使用料（スマ放題/通話基本プラン） など |
| 4gデータ通信基本料 | `cate10` | VARCHAR | 600 | － | 4Gデータ通信基本量(i)、4Gデータ通信基本量(F) 4Gデータ通信基本量(S) など |
| 5g基本料 | `cate11` | VARCHAR | 600 | － | 5Gサービス利用料、5G基本料（内包用） など |
| パケット割引 | `cate12` | VARCHAR | 600 | － | データプラン7GB（法人）、パケットし放題フラット など |
| 通信速度制限解除 | `cate13` | VARCHAR | 600 | － | - |
| 通話定額_だれとでも | `cate14` | VARCHAR | 600 | － | - |
| wifi | `cate15` | VARCHAR | 600 | － | - |
| テザリング | `cate16` | VARCHAR | 600 | － | - |
| フラットsp9 | `cate17` | VARCHAR | 600 | － | - |
| オプションパック | `cate18` | VARCHAR | 600 | － | セレクトパック、iPhone法人基本パック、スマートフォン法人基本パック など |
| あんしん保証パック | `cate19` | VARCHAR | 600 | － | (端末)安心保証パックB など |
| app | `cate20` | VARCHAR | 600 | － | - |
| 世界対応ケータイ | `cate21` | VARCHAR | 600 | － | - |
| 海外パケット割引 | `cate22` | VARCHAR | 600 | － | - |
| 通話料明細 | `cate23` | VARCHAR | 600 | － | - |
| it接続基本料 | `cate24` | VARCHAR | 600 | － | - |
| オプションカテゴリ1 | `optcate1` | VARCHAR | 600 | － | VoLTE、安心フィルター、グループ通話、割込通話など |
| オプションサービス1 | `optsvc1` | VARCHAR | 600 | － | VoLTE（YM)、あんしんフィルター（i）など |
| オプションカテゴリ2 | `optcate2` | VARCHAR | 600 | － | - |
| オプションサービス2 | `optsvc2` | VARCHAR | 600 | － | - |
| オプションカテゴリ3 | `optcate3` | VARCHAR | 600 | － | - |
| オプションサービス3 | `optsvc3` | VARCHAR | 600 | － | - |
| オプションカテゴリ4 | `optcate4` | VARCHAR | 600 | － | - |
| オプションサービス4 | `optsvc4` | VARCHAR | 600 | － | - |
| オプションカテゴリ5 | `optcate5` | VARCHAR | 600 | － | - |
| オプションサービス5 | `optsvc5` | VARCHAR | 600 | － | - |
| オプションカテゴリ6 | `optcate6` | VARCHAR | 600 | － | - |
| オプションサービス6 | `optsvc6` | VARCHAR | 600 | － | - |
| オプションカテゴリ7 | `optcate7` | VARCHAR | 600 | － | - |
| オプションサービス7 | `optsvc7` | VARCHAR | 600 | － | - |
| オプションカテゴリ8 | `optcate8` | VARCHAR | 600 | － | - |
| オプションサービス8 | `optsvc8` | VARCHAR | 600 | － | - |
| オプションカテゴリ9 | `optcate9` | VARCHAR | 600 | － | - |
| オプションサービス9 | `optsvc9` | VARCHAR | 600 | － | - |
| オプションカテゴリ10 | `optcate10` | VARCHAR | 600 | － | - |
| オプションサービス10 | `optsvc10` | VARCHAR | 600 | － | - |
| シェア設定 | `share_setting_type_nm` | VARCHAR | 600 | － | - |
| シェアオプション | `share1` | VARCHAR | 600 | － | - |
| grp代表シェアopt | `grp_represent_line_share_nm` | VARCHAR | 600 | － | - |
| grp代表通信速度制限 | `grp_limit_release_method_nm` | VARCHAR | 600 | － | - |
| rntoptカテゴリ1 | `rntopt1` | VARCHAR | 300 | － | レンタル保守パック(i)、レンタル保守パック(s)など |
| rntoptプラン1 | `rntpln1` | VARCHAR | 300 | － | 基本、基本（中古レンタル専用）、プラン1000、プラン2000N など |
| rntoptカテゴリ2 | `rntopt2` | VARCHAR | 300 | － | - |
| rntoptプラン2 | `rntpln2` | VARCHAR | 300 | － | - |
| rntoptカテゴリ3 | `rntopt3` | VARCHAR | 300 | － | - |
| rntoptプラン3 | `rntpln3` | VARCHAR | 300 | － | - |
| rntoptカテゴリ4 | `rntopt4` | VARCHAR | 300 | － | - |
| rntoptプラン4 | `rntpln4` | VARCHAR | 300 | － | - |
| rntoptカテゴリ5 | `rntopt5` | VARCHAR | 300 | － | - |
| rntoptプラン5 | `rntpln5` | VARCHAR | 300 | － | - |
| rntoptカテゴリ6 | `rntopt6` | VARCHAR | 300 | － | - |
| rntoptプラン6 | `rntpln6` | VARCHAR | 300 | － | - |
| rntoptカテゴリ7 | `rntopt7` | VARCHAR | 300 | － | - |
| rntoptプラン7 | `rntpln7` | VARCHAR | 300 | － | - |
| rntoptカテゴリ8 | `rntopt8` | VARCHAR | 300 | － | - |
| rntoptプラン8 | `rntpln8` | VARCHAR | 300 | － | - |
| rntoptカテゴリ9 | `rntopt9` | VARCHAR | 300 | － | - |
| rntoptプラン9 | `rntpln9` | VARCHAR | 300 | － | - |
| rntoptカテゴリ10 | `rntopt10` | VARCHAR | 300 | － | - |
| rntoptプラン10 | `rntpln10` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ1 | `rntoptatt1` | VARCHAR | 300 | － | - |
| rntoptattプラン1 | `rntplnatt1` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ2 | `rntoptatt2` | VARCHAR | 300 | － | - |
| rntoptattプラン2 | `rntplnatt2` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ3 | `rntoptatt3` | VARCHAR | 300 | － | - |
| rntoptattプラン3 | `rntplnatt3` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ4 | `rntoptatt4` | VARCHAR | 300 | － | - |
| rntoptattプラン4 | `rntplnatt4` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ5 | `rntoptatt5` | VARCHAR | 300 | － | - |
| rntoptattプラン5 | `rntplnatt5` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ6 | `rntoptatt6` | VARCHAR | 300 | － | - |
| rntoptattプラン6 | `rntplnatt6` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ7 | `rntoptatt7` | VARCHAR | 300 | － | - |
| rntoptattプラン7 | `rntplnatt7` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ8 | `rntoptatt8` | VARCHAR | 300 | － | - |
| rntoptattプラン8 | `rntplnatt8` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ9 | `rntoptatt9` | VARCHAR | 300 | － | - |
| rntoptattプラン9 | `rntplnatt9` | VARCHAR | 300 | － | - |
| rntoptattカテゴリ10 | `rntoptatt10` | VARCHAR | 300 | － | - |
| rntoptattプラン10 | `rntplnatt10` | VARCHAR | 300 | － | - |
| rntキャンペーン1 | `rntcamp1` | VARCHAR | 300 | － | - |
| rntキャンペーン2 | `rntcamp2` | VARCHAR | 300 | － | - |
| rntキャンペーン3 | `rntcamp3` | VARCHAR | 300 | － | - |
| キャンペーンコード1 | `campcd1` | VARCHAR | 20 | － | - |
| キャンペーンコード2 | `campcd2` | VARCHAR | 20 | － | - |
| rnt緊急キャンペーン1 | `rnturgecamp1` | VARCHAR | 300 | － | - |
| rnt緊急キャンペーン2 | `rnturgecamp2` | VARCHAR | 300 | － | - |
| rnt緊急キャンペーン3 | `rnturgecamp3` | VARCHAR | 300 | － | - |
| 新規事務手数料免除 | `fee1` | VARCHAR | 300 | － | 有 / 無 |
| 機種変更手数料免除 | `fee2` | VARCHAR | 300 | － | 有 / 無 |
| 契変事務手数料免除 | `fee3` | VARCHAR | 300 | － | 有 / 無 |
| 年契違約金免除 | `fee4` | VARCHAR | 300 | － | 有 / 無 |
| 適用中相対割引終了日 | `relative_end_date` | VARCHAR | 20 | － | - |
| 相対pdカテゴリ1 | `pcn1` | VARCHAR | 600 | － | プラン、パケット割引、あんしん保証パックなど |
| 相対pd名称1 | `pdn1` | VARCHAR | 600 | － | 基本プラン（音声）、データプラン5G（法人）など |
| 相対割引方法1 | `dtn1` | VARCHAR | 300 | － | - |
| 相対有効開始日1 | `dsd1` | VARCHAR | 20 | － | - |
| 相対有効終了日1 | `ded1` | VARCHAR | 20 | － | - |
| 相対請求金額1 | `bpr1` | VARCHAR | 8 | － | - |
| 相対割引金額1 | `dpr1` | VARCHAR | 8 | － | - |
| 相対割引率1 | `drt1` | VARCHAR | 6 | － | - |
| 相対割引開始月1 | `dsm1` | VARCHAR | 3 | － | - |
| 相対期間1 | `dtm1` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ2 | `pcn2` | VARCHAR | 600 | － | - |
| 相対pd名称2 | `pdn2` | VARCHAR | 600 | － | - |
| 相対割引方法2 | `dtn2` | VARCHAR | 300 | － | - |
| 相対有効開始日2 | `dsd2` | VARCHAR | 20 | － | - |
| 相対有効終了日2 | `ded2` | VARCHAR | 20 | － | - |
| 相対請求金額2 | `bpr2` | VARCHAR | 8 | － | - |
| 相対割引金額2 | `dpr2` | VARCHAR | 8 | － | - |
| 相対割引率2 | `drt2` | VARCHAR | 6 | － | - |
| 相対割引開始月2 | `dsm2` | VARCHAR | 2 | － | - |
| 相対期間2 | `dtm2` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ3 | `pcn3` | VARCHAR | 600 | － | - |
| 相対pd名称3 | `pdn3` | VARCHAR | 600 | － | - |
| 相対割引方法3 | `dtn3` | VARCHAR | 300 | － | - |
| 相対有効開始日3 | `dsd3` | VARCHAR | 20 | － | - |
| 相対有効終了日3 | `ded3` | VARCHAR | 20 | － | - |
| 相対請求金額3 | `bpr3` | VARCHAR | 8 | － | - |
| 相対割引金額3 | `dpr3` | VARCHAR | 8 | － | - |
| 相対割引率3 | `drt3` | VARCHAR | 6 | － | - |
| 相対割引開始月3 | `dsm3` | VARCHAR | 2 | － | - |
| 相対期間3 | `dtm3` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ4 | `pcn4` | VARCHAR | 600 | － | - |
| 相対pd名称4 | `pdn4` | VARCHAR | 600 | － | - |
| 相対割引方法4 | `dtn4` | VARCHAR | 300 | － | - |
| 相対有効開始日4 | `dsd4` | VARCHAR | 20 | － | - |
| 相対有効終了日4 | `ded4` | VARCHAR | 20 | － | - |
| 相対請求金額4 | `bpr4` | VARCHAR | 8 | － | - |
| 相対割引金額4 | `dpr4` | VARCHAR | 8 | － | - |
| 相対割引率4 | `drt4` | VARCHAR | 6 | － | - |
| 相対割引開始月4 | `dsm4` | VARCHAR | 2 | － | - |
| 相対期間4 | `dtm4` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ5 | `pcn5` | VARCHAR | 600 | － | - |
| 相対pd名称5 | `pdn5` | VARCHAR | 600 | － | - |
| 相対割引方法5 | `dtn5` | VARCHAR | 300 | － | - |
| 相対有効開始日5 | `dsd5` | VARCHAR | 20 | － | - |
| 相対有効終了日5 | `ded5` | VARCHAR | 20 | － | - |
| 相対請求金額5 | `bpr5` | VARCHAR | 8 | － | - |
| 相対割引金額5 | `dpr5` | VARCHAR | 8 | － | - |
| 相対割引率5 | `drt5` | VARCHAR | 6 | － | - |
| 相対割引開始月5 | `dsm5` | VARCHAR | 2 | － | - |
| 相対期間5 | `dtm5` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ6 | `pcn6` | VARCHAR | 600 | － | - |
| 相対pd名称6 | `pdn6` | VARCHAR | 600 | － | - |
| 相対割引方法6 | `dtn6` | VARCHAR | 300 | － | - |
| 相対有効開始日6 | `dsd6` | VARCHAR | 20 | － | - |
| 相対有効終了日6 | `ded6` | VARCHAR | 20 | － | - |
| 相対請求金額6 | `bpr6` | VARCHAR | 8 | － | - |
| 相対割引金額6 | `dpr6` | VARCHAR | 8 | － | - |
| 相対割引率6 | `drt6` | VARCHAR | 6 | － | - |
| 相対割引開始月6 | `dsm6` | VARCHAR | 2 | － | - |
| 相対期間6 | `dtm6` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ7 | `pcn7` | VARCHAR | 600 | － | - |
| 相対pd名称7 | `pdn7` | VARCHAR | 600 | － | - |
| 相対割引方法7 | `dtn7` | VARCHAR | 300 | － | - |
| 相対有効開始日7 | `dsd7` | VARCHAR | 20 | － | - |
| 相対有効終了日7 | `ded7` | VARCHAR | 20 | － | - |
| 相対請求金額7 | `bpr7` | VARCHAR | 8 | － | - |
| 相対割引金額7 | `dpr7` | VARCHAR | 8 | － | - |
| 相対割引率7 | `drt7` | VARCHAR | 6 | － | - |
| 相対割引開始月7 | `dsm7` | VARCHAR | 2 | － | - |
| 相対期間7 | `dtm7` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ8 | `pcn8` | VARCHAR | 600 | － | - |
| 相対pd名称8 | `pdn8` | VARCHAR | 600 | － | - |
| 相対割引方法8 | `dtn8` | VARCHAR | 300 | － | - |
| 相対有効開始日8 | `dsd8` | VARCHAR | 20 | － | - |
| 相対有効終了日8 | `ded8` | VARCHAR | 20 | － | - |
| 相対請求金額8 | `bpr8` | VARCHAR | 8 | － | - |
| 相対割引金額8 | `dpr8` | VARCHAR | 8 | － | - |
| 相対割引率8 | `drt8` | VARCHAR | 6 | － | - |
| 相対割引開始月8 | `dsm8` | VARCHAR | 2 | － | - |
| 相対期間8 | `dtm8` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ9 | `pcn9` | VARCHAR | 600 | － | - |
| 相対pd名称9 | `pdn9` | VARCHAR | 600 | － | - |
| 相対割引方法9 | `dtn9` | VARCHAR | 300 | － | - |
| 相対有効開始日9 | `dsd9` | VARCHAR | 20 | － | - |
| 相対有効終了日9 | `ded9` | VARCHAR | 20 | － | - |
| 相対請求金額9 | `bpr9` | VARCHAR | 8 | － | - |
| 相対割引金額9 | `dpr9` | VARCHAR | 8 | － | - |
| 相対割引率9 | `drt9` | VARCHAR | 6 | － | - |
| 相対割引開始月9 | `dsm9` | VARCHAR | 2 | － | - |
| 相対期間9 | `dtm9` | DECIMAL | 3 | － | - |
| 相対pdカテゴリ10 | `pcn10` | VARCHAR | 600 | － | - |
| 相対pd名称10 | `pdn10` | VARCHAR | 600 | － | - |
| 相対割引方法10 | `dtn10` | VARCHAR | 300 | － | - |
| 相対有効開始日10 | `dsd10` | VARCHAR | 20 | － | - |
| 相対有効終了日10 | `ded10` | VARCHAR | 20 | － | - |
| 相対請求金額10 | `bpr10` | VARCHAR | 8 | － | - |
| 相対割引金額10 | `dpr10` | VARCHAR | 8 | － | - |
| 相対割引率10 | `drt10` | VARCHAR | 6 | － | - |
| 相対割引開始月10 | `dsm10` | VARCHAR | 2 | － | - |
| 相対期間10 | `dtm10` | DECIMAL | 3 | － | - |
| 相対他pdカテゴリ1 | `opcn1` | VARCHAR | 600 | － | - |
| 相対他pd名称1 | `opdn1` | VARCHAR | 600 | － | - |
| 相対他割引方法1 | `odtn1` | VARCHAR | 300 | － | - |
| 相対他有効開始日1 | `odsd1` | VARCHAR | 20 | － | - |
| 相対他有効終了日1 | `oded1` | VARCHAR | 20 | － | - |
| 相対他請求金額1 | `obpr1` | VARCHAR | 8 | － | - |
| 相対他割引金額1 | `odpr1` | VARCHAR | 8 | － | - |
| 相対他割引率1 | `odrt1` | VARCHAR | 6 | － | - |
| 相対他割引開始月1 | `odsm1` | VARCHAR | 2 | － | - |
| 相対他期間1 | `odtm1` | DECIMAL | 3 | － | - |
| 相対他pdカテゴリ2 | `opcn2` | VARCHAR | 600 | － | - |
| 相対他pd名称2 | `opdn2` | VARCHAR | 600 | － | - |
| 相対他割引方法2 | `odtn2` | VARCHAR | 300 | － | - |
| 相対他有効開始日2 | `odsd2` | VARCHAR | 20 | － | - |
| 相対他有効終了日2 | `oded2` | VARCHAR | 20 | － | - |
| 相対他請求金額2 | `obpr2` | VARCHAR | 8 | － | - |
| 相対他割引金額2 | `odpr2` | VARCHAR | 8 | － | - |
| 相対他割引率2 | `odrt2` | VARCHAR | 6 | － | - |
| 相対他割引開始月2 | `odsm2` | VARCHAR | 2 | － | - |
| 相対他期間2 | `odtm2` | DECIMAL | 3 | － | - |
| 相対他pdカテゴリ3 | `opcn3` | VARCHAR | 600 | － | - |
| 相対他pd名称3 | `opdn3` | VARCHAR | 600 | － | - |
| 相対他割引方法3 | `odtn3` | VARCHAR | 300 | － | - |
| 相対他有効開始日3 | `odsd3` | VARCHAR | 20 | － | - |
| 相対他有効終了日3 | `oded3` | VARCHAR | 20 | － | - |
| 相対他請求金額3 | `obpr3` | VARCHAR | 8 | － | - |
| 相対他割引金額3 | `odpr3` | VARCHAR | 8 | － | - |
| 相対他割引率3 | `odrt3` | VARCHAR | 6 | － | - |
| 相対他割引開始月3 | `odsm3` | VARCHAR | 2 | － | - |
| 相対他期間3 | `odtm3` | DECIMAL | 3 | － | - |
| 相対他pdカテゴリ4 | `opcn4` | VARCHAR | 600 | － | - |
| 相対他pd名称4 | `opdn4` | VARCHAR | 600 | － | - |
| 相対他割引方法4 | `odtn4` | VARCHAR | 300 | － | - |
| 相対他有効開始日4 | `odsd4` | VARCHAR | 20 | － | - |
| 相対他有効終了日4 | `oded4` | VARCHAR | 20 | － | - |
| 相対他請求金額4 | `obpr4` | VARCHAR | 8 | － | - |
| 相対他割引金額4 | `odpr4` | VARCHAR | 8 | － | - |
| 相対他割引率4 | `odrt4` | VARCHAR | 6 | － | - |
| 相対他割引開始月4 | `odsm4` | VARCHAR | 2 | － | - |
| 相対他期間4 | `odtm4` | DECIMAL | 3 | － | - |
| 相対他pdカテゴリ5 | `opcn5` | VARCHAR | 600 | － | - |
| 相対他pd名称5 | `opdn5` | VARCHAR | 600 | － | - |
| 相対他割引方法5 | `odtn5` | VARCHAR | 300 | － | - |
| 相対他有効開始日5 | `odsd5` | VARCHAR | 20 | － | - |
| 相対他有効終了日5 | `oded5` | VARCHAR | 20 | － | - |
| 相対他請求金額5 | `obpr5` | VARCHAR | 8 | － | - |
| 相対他割引金額5 | `odpr5` | VARCHAR | 8 | － | - |
| 相対他割引率5 | `odrt5` | VARCHAR | 6 | － | - |
| 相対他割引開始月5 | `odsm5` | VARCHAR | 2 | － | - |
| 相対他期間5 | `odtm5` | DECIMAL | 3 | － | - |
| rnt登録事務手数料免除 | `distype1` | VARCHAR | 300 | － | - |
| rnt登録事務手数料金額 | `payonm1` | VARCHAR | 300 | － | - |
| rnt解約違約金割引方法 | `distype2` | VARCHAR | 300 | － | - |
| rnt解約違約金金額 | `payonm2` | VARCHAR | 300 | － | - |
| r相対op1 | `rntopt_ro1` | VARCHAR | 300 | － | - |
| r相対プラン1 | `rntopt_rp1` | VARCHAR | 600 | － | - |
| r相対割引方法1 | `rntrel_dt1` | VARCHAR | 300 | － | - |
| r相対有効開始日1 | `rntrel_ds1` | VARCHAR | 20 | － | - |
| r相対有効終了日1 | `rntrel_de1` | VARCHAR | 20 | － | - |
| r相対金額1 | `rntrel_op1` | DECIMAL | 10 | － | - |
| r相対期間1 | `rntrel_dm1` | DECIMAL | 3 | － | - |
| r相対op2 | `rntopt_ro2` | VARCHAR | 300 | － | - |
| r相対プラン2 | `rntopt_rp2` | VARCHAR | 600 | － | - |
| r相対割引方法2 | `rntrel_dt2` | VARCHAR | 300 | － | - |
| r相対有効開始日2 | `rntrel_ds2` | VARCHAR | 20 | － | - |
| r相対有効終了日2 | `rntrel_de2` | VARCHAR | 20 | － | - |
| r相対金額2 | `rntrel_op2` | DECIMAL | 10 | － | - |
| r相対期間2 | `rntrel_dm2` | DECIMAL | 3 | － | - |
| r相対op3 | `rntopt_ro3` | VARCHAR | 300 | － | - |
| r相対プラン3 | `rntopt_rp3` | VARCHAR | 600 | － | - |
| r相対割引方法3 | `rntrel_dt3` | VARCHAR | 300 | － | - |
| r相対有効開始日3 | `rntrel_ds3` | VARCHAR | 20 | － | - |
| r相対有効終了日3 | `rntrel_de3` | VARCHAR | 20 | － | - |
| r相対金額3 | `rntrel_op3` | DECIMAL | 10 | － | - |
| r相対期間3 | `rntrel_dm3` | DECIMAL | 3 | － | - |
| r相対op4 | `rntopt_ro4` | VARCHAR | 300 | － | - |
| r相対プラン4 | `rntopt_rp4` | VARCHAR | 600 | － | - |
| r相対割引方法4 | `rntrel_dt4` | VARCHAR | 300 | － | - |
| r相対有効開始日4 | `rntrel_ds4` | VARCHAR | 20 | － | - |
| r相対有効終了日4 | `rntrel_de4` | VARCHAR | 20 | － | - |
| r相対金額4 | `rntrel_op4` | DECIMAL | 10 | － | - |
| r相対期間4 | `rntrel_dm4` | DECIMAL | 3 | － | - |
| r相対op5 | `rntopt_ro5` | VARCHAR | 300 | － | - |
| r相対プラン5 | `rntopt_rp5` | VARCHAR | 600 | － | - |
| r相対割引方法5 | `rntrel_dt5` | VARCHAR | 300 | － | - |
| r相対有効開始日5 | `rntrel_ds5` | VARCHAR | 20 | － | - |
| r相対有効終了日5 | `rntrel_de5` | VARCHAR | 20 | － | - |
| r相対金額5 | `rntrel_op5` | DECIMAL | 10 | － | - |
| r相対期間5 | `rntrel_dm5` | DECIMAL | 3 | － | - |
| r相対他pd名称1 | `orntrel_pd1` | VARCHAR | 600 | － | - |
| r相対他割引方法1 | `orntrel_dt1` | VARCHAR | 300 | － | - |
| r相対他有効開始日1 | `orntrel_ds1` | VARCHAR | 20 | － | - |
| r相対他有効終了日1 | `orntrel_de1` | VARCHAR | 20 | － | - |
| r相対他金額1 | `orntrel_op1` | DECIMAL | 10 | － | - |
| r相対他期間1 | `orntrel_dm1` | DECIMAL | 3 | － | - |
| r相対他pd名称2 | `orntrel_pd2` | VARCHAR | 600 | － | - |
| r相対他割引方法2 | `orntrel_dt2` | VARCHAR | 300 | － | - |
| r相対他有効開始日2 | `orntrel_ds2` | VARCHAR | 20 | － | - |
| r相対他有効終了日2 | `orntrel_de2` | VARCHAR | 20 | － | - |
| r相対他金額2 | `orntrel_op2` | DECIMAL | 10 | － | - |
| r相対他期間2 | `orntrel_dm2` | DECIMAL | 3 | － | - |
| r相対他pd名称3 | `orntrel_pd3` | VARCHAR | 600 | － | - |
| r相対他割引方法3 | `orntrel_dt3` | VARCHAR | 300 | － | - |
| r相対他有効開始日3 | `orntrel_ds3` | VARCHAR | 20 | － | - |
| r相対他有効終了日3 | `orntrel_de3` | VARCHAR | 20 | － | - |
| r相対他金額3 | `orntrel_op3` | DECIMAL | 10 | － | - |
| r相対他期間3 | `orntrel_dm3` | DECIMAL | 3 | － | - |
| r相対他pd名称4 | `orntrel_pd4` | VARCHAR | 600 | － | - |
| r相対他割引方法4 | `orntrel_dt4` | VARCHAR | 300 | － | - |
| r相対他有効開始日4 | `orntrel_ds4` | VARCHAR | 20 | － | - |
| r相対他有効終了日4 | `orntrel_de4` | VARCHAR | 20 | － | - |
| r相対他金額4 | `orntrel_op4` | DECIMAL | 10 | － | - |
| r相対他期間4 | `orntrel_dm4` | DECIMAL | 3 | － | - |
| r相対他pd名称5 | `orntrel_pd5` | VARCHAR | 600 | － | - |
| r相対他割引方法5 | `orntrel_dt5` | VARCHAR | 300 | － | - |
| r相対他有効開始日5 | `orntrel_ds5` | VARCHAR | 20 | － | - |
| r相対他有効終了日5 | `orntrel_de5` | VARCHAR | 20 | － | - |
| r相対他金額5 | `orntrel_op5` | DECIMAL | 10 | － | - |
| r相対他期間5 | `orntrel_dm5` | DECIMAL | 3 | － | - |
| プラン変更許可範囲1 | `chplan1` | VARCHAR | 600 | － | - |
| プラン変更許可範囲2 | `chplan2` | VARCHAR | 600 | － | - |
| プラン変更許可範囲3 | `chplan3` | VARCHAR | 600 | － | - |
| プラン変更許可範囲4 | `chplan4` | VARCHAR | 600 | － | - |
| プラン変更許可範囲5 | `chplan5` | VARCHAR | 600 | － | - |
| プラン変更許可範囲6 | `chplan6` | VARCHAR | 600 | － | - |
| プラン変更許可範囲7 | `chplan7` | VARCHAR | 600 | － | - |
| プラン変更許可範囲8 | `chplan8` | VARCHAR | 600 | － | - |
| プラン変更許可範囲9 | `chplan9` | VARCHAR | 600 | － | - |
| 解除料免除率 | `cancel_exemption_rate` | VARCHAR | 12 | － | - |
| 起算日変更 | `reckon_change_type_nm` | VARCHAR | 600 | － | - |
| サマリ作成担当者id | `svcsm_ins_user_id` | VARCHAR | 20 | － | - |
| サマリ作成日時 | `svcsm_ins_tstamp` | VARCHAR | 26 | － | - |
| サマリ更新担当者id | `svcsm_last_upd_user_id` | VARCHAR | 20 | － | - |
| サマリ更新日時 | `svcsm_last_upd_tstamp` | VARCHAR | 26 | － | - |
| 回線数下限 | `lower_line_num` | DECIMAL | 11 | － | - |
| 提供世代種別 | `provision_generation_type` | VARCHAR | 2 | － | - |
| レンタル機変詳細名称 | `rental_detail_nm` | VARCHAR | 300 | － | - |
| 現端末利用期間名称 | `old_trmnl_service_duration_nm` | VARCHAR | 300 | － | - |
| 現端末回収状況名称 | `old_trmnl_return_nm` | VARCHAR | 300 | － | - |
| 現端末未回収残高 | `old_trmnl_uncollected_amount` | DECIMAL | 11 | － | - |
| 現端末ブランド名 | `old_trmnl_item_brand_nm` | VARCHAR | 600 | － | - |
| 現端末商品コード | `old_trmnl_item_cd` | VARCHAR | 15 | － | - |
| 現端末商品名称 | `old_trmnl_item_nm` | VARCHAR | 300 | － | - |
| 現端末購入月 | `old_trmnl_perchase_month` | VARCHAR | 6 | － | - |
| 複数回線割引名称 | `plan_maney_line_discount_nm` | VARCHAR | 300 | － | - |
| 実通話国内音声 | `in_call_voice` | DECIMAL | 11 | － | - |
| 実通話国内データ | `in_call_data` | DECIMAL | 11 | － | - |
| 大口割引名称 | `in_large_discnt_nm` | VARCHAR | 300 | － | - |
| 実通話国際電話 | `out_call_tel` | DECIMAL | 11 | － | - |
| 国際rmデータ | `out_rm_data` | DECIMAL | 11 | － | - |
| 国際rm音声 | `out_rm_voice` | DECIMAL | 11 | － | - |
| シェア相対パケ名称 | `rltv_share_packet_nm` | VARCHAR | 300 | － | - |
| 違約金減額増額 | `rltv_penalty_plus` | DECIMAL | 11 | － | - |
| 代理店協業有無名称 | `agent_flg_nm` | VARCHAR | 300 | － | - |
| 二次代理店コード | `second_agent_cd` | VARCHAR | 60 | － | - |
| 二次代理店名 | `second_agent_nm` | VARCHAR | 300 | － | - |
| 請求代行業者名称 | `bill_agency_nm` | VARCHAR | 300 | － | - |
| ショット手数料 | `shot_charge` | DECIMAL | 11 | － | - |
| 継続手数料率 | `continue_fee` | VARCHAR | 8 | － | - |
| カスタマイズ等請求額 | `custom_amount` | DECIMAL | 11 | － | - |
| カスタマイズ等コスト | `custom_cost` | DECIMAL | 11 | － | - |
| capex | `capex` | DECIMAL | 11 | － | - |
| その他調整額 | `other_adjust_charge` | DECIMAL | 11 | － | - |
| bizコンシェル定価 | `concier_price` | DECIMAL | 11 | － | - |
| bizコンシェル値引額 | `concier_discount` | DECIMAL | 11 | － | - |
| bizコンシェルコスト | `concier_cost` | DECIMAL | 11 | － | - |
| 保守端末ブランド名 | `maintain_item_brand_nm` | VARCHAR | 600 | － | - |
| 保守端末商品コード | `maintain_item_cd` | VARCHAR | 15 | － | - |
| 保守端末商品名称 | `maintain_item_nm` | VARCHAR | 300 | － | - |
| 保守端末標準価格 | `maintain_cellular_price` | DECIMAL | 11 | － | - |
| 保守端末値引 | `maintain_discount` | DECIMAL | 11 | － | - |
| 保守端末数量 | `maintain_num` | DECIMAL | 11 | － | - |
| wo適用名称 | `wo_select_nm` | VARCHAR | 300 | － | - |
| 足回り名称 | `wo_select_around_nm` | VARCHAR | 300 | － | - |
| ntt東西ma内外名称1 | `wo_ntt_ma_inout_nm_1` | VARCHAR | 300 | － | - |
| アクセス回線距離1 | `wo_access_line_1` | VARCHAR | 13 | － | - |
| 回線数1 | `wo_line_num_1` | DECIMAL | 11 | － | - |
| 定価1 | `wo_price_1` | DECIMAL | 11 | － | - |
| ntt東西ma内外名称2 | `wo_ntt_ma_inout_nm_2` | VARCHAR | 300 | － | - |
| アクセス回線距離2 | `wo_access_line_2` | VARCHAR | 13 | － | - |
| 回線数2 | `wo_line_num_2` | DECIMAL | 11 | － | - |
| 定価2 | `wo_price_2` | DECIMAL | 11 | － | - |
| da1500提供額値引 | `da1500_discount` | DECIMAL | 11 | － | - |
| 内線番号値引 | `in_line_discount` | DECIMAL | 11 | － | - |
| 内線番号回線数 | `in_line_num` | DECIMAL | 11 | － | - |
| 拠点番号値引 | `base_discount` | DECIMAL | 11 | － | - |
| 拠点番号回線数 | `base_line_num` | DECIMAL | 11 | － | - |
| ipbgw登録工事費値引 | `ip_bri_gw_discount` | DECIMAL | 11 | － | - |
| ipbgw登録工事gw台数 | `ip_bri_gw_num` | DECIMAL | 11 | － | - |
| ip接続ch接続料値引 | `ip_connect_discount` | DECIMAL | 11 | － | - |
| ip接続ch接続料ch数 | `ip_connect_num` | DECIMAL | 11 | － | - |
| 月額固定コスト | `fixed_running_cost` | VARCHAR | 9 | － | - |
| 月額変動コスト | `variable_running_cost` | VARCHAR | 8 | － | - |
| 請求書一括割引 | `calc_bill_lump_discount_nm` | VARCHAR | 300 | － | - |
| 通話従量率 | `call_metered_rate` | VARCHAR | 8 | － | - |
| 国際通話従量率 | `inter_call_metered_rate` | VARCHAR | 15 | － | - |
| 国際アクセスチャージ | `inter_access_charge` | VARCHAR | 15 | － | - |
| 旧連結営業貢献利益 | `old_csd_sales_ctb_profit` | VARCHAR | 15 | － | - |
| 新sbmnpv | `new_sbm_npv` | VARCHAR | 15 | － | - |
| 相対相談1 | `relative_consult_01` | VARCHAR | 15 | － | - |
| 相対相談2 | `relative_consult_02` | VARCHAR | 15 | － | - |
| 相対相談3 | `relative_consult_03` | VARCHAR | 15 | － | - |
| 相対相談4 | `relative_consult_04` | VARCHAR | 15 | － | - |
| 相対相談5 | `relative_consult_05` | VARCHAR | 15 | － | - |
| 相対相談6 | `relative_consult_06` | VARCHAR | 15 | － | - |
| 相対相談7 | `relative_consult_07` | VARCHAR | 15 | － | - |
| 相対相談8 | `relative_consult_08` | VARCHAR | 15 | － | - |
| 相対相談9 | `relative_consult_09` | VARCHAR | 15 | － | - |
| 相対相談10 | `relative_consult_10` | VARCHAR | 15 | － | - |
| 適用op料金品目1 | `mnl_input_charge_item_nm_1` | VARCHAR | 600 | － | - |
| 適用op基本使用料1 | `mnl_input_base_charge_1` | DECIMAL | 11 | － | - |
| 適用op提供金額1 | `mnl_input_offered_price_1` | DECIMAL | 11 | － | - |
| 適用op変動費1 | `mnl_input_variable_cost_1` | DECIMAL | 11 | － | - |
| 適用op固定費1 | `mnl_input_fixed_cost_1` | DECIMAL | 11 | － | - |
| 適用op開始月1 | `discount_starting_month_1` | VARCHAR | 2 | － | - |
| 適用op期間1 | `discount_term_month_1` | DECIMAL | 3 | － | - |
| 適用op永年1 | `long_time_flg_nm_1` | VARCHAR | 300 | － | - |
| 適用op料金品目2 | `mnl_input_charge_item_nm_2` | VARCHAR | 600 | － | - |
| 適用op基本使用料2 | `mnl_input_base_charge_2` | DECIMAL | 11 | － | - |
| 適用op提供金額2 | `mnl_input_offered_price_2` | DECIMAL | 11 | － | - |
| 適用op変動費2 | `mnl_input_variable_cost_2` | DECIMAL | 11 | － | - |
| 適用op固定費2 | `mnl_input_fixed_cost_2` | DECIMAL | 11 | － | - |
| 適用op開始月2 | `discount_starting_month_2` | VARCHAR | 2 | － | - |
| 適用op期間2 | `discount_term_month_2` | DECIMAL | 3 | － | - |
| 適用op永年2 | `long_time_flg_nm_2` | VARCHAR | 300 | － | - |
| 適用op料金品目3 | `mnl_input_charge_item_nm_3` | VARCHAR | 600 | － | - |
| 適用op基本使用料3 | `mnl_input_base_charge_3` | DECIMAL | 11 | － | - |
| 適用op提供金額3 | `mnl_input_offered_price_3` | DECIMAL | 11 | － | - |
| 適用op変動費3 | `mnl_input_variable_cost_3` | DECIMAL | 11 | － | - |
| 適用op固定費3 | `mnl_input_fixed_cost_3` | DECIMAL | 11 | － | - |
| 適用op開始月3 | `discount_starting_month_3` | VARCHAR | 2 | － | - |
| 適用op期間3 | `discount_term_month_3` | DECIMAL | 3 | － | - |
| 適用op永年3 | `long_time_flg_nm_3` | VARCHAR | 300 | － | - |
| 適用op料金品目4 | `mnl_input_charge_item_nm_4` | VARCHAR | 600 | － | - |
| 適用op基本使用料4 | `mnl_input_base_charge_4` | DECIMAL | 11 | － | - |
| 適用op提供金額4 | `mnl_input_offered_price_4` | DECIMAL | 11 | － | - |
| 適用op変動費4 | `mnl_input_variable_cost_4` | DECIMAL | 11 | － | - |
| 適用op固定費4 | `mnl_input_fixed_cost_4` | DECIMAL | 11 | － | - |
| 適用op開始月4 | `discount_starting_month_4` | VARCHAR | 2 | － | - |
| 適用op期間4 | `discount_term_month_4` | DECIMAL | 3 | － | - |
| 適用op永年4 | `long_time_flg_nm_4` | VARCHAR | 300 | － | - |
| 適用op料金品目5 | `mnl_input_charge_item_nm_5` | VARCHAR | 600 | － | - |
| 適用op基本使用料5 | `mnl_input_base_charge_5` | DECIMAL | 11 | － | - |
| 適用op提供金額5 | `mnl_input_offered_price_5` | DECIMAL | 11 | － | - |
| 適用op変動費5 | `mnl_input_variable_cost_5` | DECIMAL | 11 | － | - |
| 適用op固定費5 | `mnl_input_fixed_cost_5` | DECIMAL | 11 | － | - |
| 適用op開始月5 | `discount_starting_month_5` | VARCHAR | 2 | － | - |
| 適用op期間5 | `discount_term_month_5` | DECIMAL | 3 | － | - |
| 適用op永年5 | `long_time_flg_nm_5` | VARCHAR | 300 | － | - |
| woおとくdi登録請求額 | `wo_di_register_bill_price` | DECIMAL | 11 | － | - |
| woおとくdi使用請求額 | `wo_di_use_bill_price` | DECIMAL | 11 | － | - |
| isdn1500回線数 | `isdn1500_line_num` | DECIMAL | 11 | － | - |
| isdn1500登録請求額 | `isdn1500_register_bill_price` | DECIMAL | 11 | － | - |
| isdn1500接続請求額 | `isdn1500_base_bill_price` | DECIMAL | 11 | － | - |
| isdn1500定額請求額 | `isdn1500_fixed_bill_price` | DECIMAL | 11 | － | - |
| isdn64回線数 | `isdn64_line_num` | DECIMAL | 11 | － | - |
| isdn64登録請求額 | `isdn64_register_bill_price` | DECIMAL | 11 | － | - |
| isdn64接続請求額 | `isdn64_base_bill_price` | DECIMAL | 11 | － | - |
| isdn64定額請求額 | `isdn64_fixed_bill_price` | DECIMAL | 11 | － | - |
| 解約新規有無 | `termination_new_flg_nm` | VARCHAR | 30 | － | - |
| 未対応商品コード | `unreleased_itm_cd` | VARCHAR | 15 | － | - |
| 未対応商品名称 | `unreleased_itm_nm` | VARCHAR | 300 | － | - |
| 疑似シェア試算容量 | `mock_share_calc_capacity` | VARCHAR | 5 | － | - |
| 疑似シェア超過料 | `over_capacity_fee` | VARCHAR | 5 | － | - |
| esim登録 | `esim_regist_flg_nm` | VARCHAR | 2295 | － | - |
| 現端末契約期間 | `old_trmnl_contract_period` | DECIAML | 2 | - | - |
| サマリ単位反映 | `summary_unit_reflection_nm` | VARCHAR | 60 | - | - |
| 提供価格段階1 | `offered_price_step1` | DECIMAL | 10 | - | - |
| 提供価格段階2 | `offered_price_step2` | DECIMAL | 10 | - | - |
| 提供価格段階3 | `offered_price_step3` | DECIMAL | 10 | - | - |
| INDUSTRIAL_COMPANY_CD | `industrial_company_cd` | VARCHAR | 4 | - | - |
| LOAD_DAY | `load_day` | VARCHAR | 8 | - | - |


## データ作成の注意点
1. `オプションカテゴリ`、`オプションサービス` はセットで入力すること。例えば、`オプションカテゴリ1` ある場合は `オプションサービス1` も入力する
2. `オプションカテゴリ` は１つ前の番号にデータがある場合のみ入力される。例えば、`オプションカテゴリ1` が空であれば、`オプションカテゴリ2` 以降は空である
3. `rntoptカテゴリ`、`rntoptプラン`、`キャンペーン` などの連番があるカラムについても 1 または 2 の注意点を守ること
4. 以下は利用するカラムなので、生成データにはついては実際にありそうなデータにすること
  - オプションカテゴリ
  - オプションサービス
  - rntoptカテゴリ
  - rntoptプラン
  - 相対pdカテゴリ
  - 相対pd名称
  - 相対他pdカテゴリ
  - 相対他pd名称
  - キャンペーン
  - プラン
  - 通話料割引wホワイト
  - 違約金年契
  - sベーシックパック
  - 4gデータ通信基本料
  - 5g基本料
  - パケット割引
  - オプションパック
  - あんしん保証パック
