# 生成データ定義索引

実体の定義は `docs/format/` 配下にあります。各データ単位で分割した Markdown を参照してください。

- [キャンペーン](format/m_campaign.md)
- [取次店](format/m_agency.md)
- [商品](format/m_product.md)
- [統一企業情報](format/dwh_unified_company_information.md)
- [BFSエントリモバイル_エントリ情報](format/bfs_entry_informations.md)
- [BFSエントリモバイル_サービスサマリ_端末](format/bfs_service_summary_device.md)
- [BFSエントリモバイル_サービスサマリ_付属品](format/bfs_service_summary_accessories.md)
- [COMPASS営業決裁](format/compass_sales_approval.md)


# 全体ルール
各出力データの特定のカラムはフォーマットを揃える必要がある。以下にそのカラムを定義する。

## 統一企業コード
- (DWH)統一企業情報 : `uniq_corp_cd`
- (COMPASS)営業決裁 : `accountcode`
- (BFSエントリ)モバイル_エントリ情報 : `corp_cd`

## エントリ番号
- (BFSエントリ)モバイル_エントリ情報 : `entry_no`
- (BFSエントリ)モバイル_サービスサマリ_付属品 : `entry_no` 
- (BFSエントリ)モバイル_サービスサマリ_端末 : `entry_no`

## 決裁番号
- (COMPASS)営業決裁 : `name`
- (BFSエントリ)モバイル_エントリ情報 : `decide_no1`
