# (BFSエントリ)モバイル_サービスサマリ_付属品

- マート名: `b_hjn_bfs_モバイル_サービスサマリ_付属品`
- CSVファイル名: `bfs_service_summary_accessories_all.csv`, `bfs_service_summary_accessories_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 初期移行（300,000件）、日次差分（3,907件）
- データ量: 初期移行（5MB、2年分）、日次差分（8.81MB）
- データ概要: BFSのモバイル_サービスサマリ_付属品情報を保有。
- 参考データ: `sample_data/bfs_service_summary_accessories.csv`

## カラム定義

| SEQ | 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |
| --- | --- | --- | --- | --- | --- | --- |
|  | 1 | エントリ番号 | `entry_number` | VARCHAR | 54 | － | - |
|  | 2 | サマリ番号 | `summary_number` | VARCHAR | 36 | － | - |
|  | 3 | シリアル付付属品 | `serial_number_accessories` | VARCHAR | 2295 | － | - |
|  | 4 | 商品コード | `product_code` | VARCHAR | 45 | － | - |
|  | 5 | メーカ | `manufacturer` | VARCHAR | 1800 | － | - |
|  | 6 | 商品名 | `product_name` | VARCHAR | 900 | － | - |
|  | 7 | カラー1 | `color_1` | VARCHAR | 900 | － | - |
|  | 8 | 台数1 | `quantity_1` | DECIMAL | 6 | － | - |
|  | 9 | カラー2 | `color_2` | VARCHAR | 900 | － | - |
|  | 10 | 台数2 | `quantity_2` | DECIMAL | 6 | － | - |
|  | 11 | カラー3 | `color_3` | VARCHAR | 900 | － | - |
|  | 12 | 台数3 | `quantity_3` | DECIMAL | 6 | － | - |
|  | 13 | カラー4 | `color_4` | VARCHAR | 900 | － | - |
|  | 14 | 台数4 | `quantity_4` | DECIMAL | 6 | － | - |
|  | 15 | カラー5 | `color_5` | VARCHAR | 900 | － | - |
|  | 16 | 台数5 | `quantity_5` | DECIMAL | 6 | － | - |
|  | 17 | 付属品標準価格 | `standard_price_of_accessories` | DECIMAL | 10 | － | - |
|  | 18 | 提供代金 | `provision_fee` | DECIMAL | 10 | － | - |
|  | 19 | 使用ポイント | `usage_points` | DECIMAL | 6 | － | - |
|  | 20 | 原価 | `cost` | DECIMAL | 11 | － | - |
|  | 21 | 紐付けサマリ番号 | `linked_summary_number` | VARCHAR | 90 | － | - |
|  | 22 | 原価予備費 | `cost_contingency` | DECIMAL | 8,0 | － | - |
