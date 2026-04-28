# (BFSエントリ)モバイル_サービスサマリ_付属品

- マート名: `b_hjn_bfs_モバイル_サービスサマリ_付属品`
- CSVファイル名: 
  - 初期データ: `b_hjn_bfs_モバイル_サービスサマリ_付属品.csv`
  - 差分データ: `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv`
- 全量更新 or 差分更新: 差分更新
- 更新頻度: 日次
- データ数: 初期移行（300,000件）、日次差分（3,907件）
- データ量: 初期移行（5MB、2年分）、日次差分（8.81MB）
- データ概要: BFSのモバイル_サービスサマリ_付属品情報を保有。
- 参考データ: `sample_data/bfs_service_summary_accessories.csv`

## 差分データの考え方

- `b_hjn_bfs_モバイル_サービスサマリ_付属品_diff.csv` は `diff_type` 列を先頭に持つ。
- `diff_type=I` は初期データに存在しない `商品コード` を使う。
- `diff_type=U` は初期データに存在する `商品コード` を使う。
- `diff_type=D` は出力しない。
- `diff_type=U` は同じ `商品コード` を維持したまま、メーカ、商品名、数量、価格系などを更新後の値にした行を持つ。

## カラム定義

| 項目名 | カラム名 | 型 | 桁 | 仮名化 | 説明 |
| --- | --- | --- | --- | --- | --- |
| エントリ番号 | `entry_number` | VARCHAR | 54 | － | - |
| サマリ番号 | `summary_number` | VARCHAR | 36 | － | - |
| シリアル付付属品 | `serial_number_accessories` | VARCHAR | 2295 | － | - |
| 商品コード | `product_code` | VARCHAR | 45 | － | - |
| メーカ | `manufacturer` | VARCHAR | 1800 | － | - |
| 商品名 | `product_name` | VARCHAR | 900 | － | - |
| カラー1 | `color_1` | VARCHAR | 900 | － | - |
| 台数1 | `quantity_1` | DECIMAL | 6 | － | - |
| カラー2 | `color_2` | VARCHAR | 900 | － | - |
| 台数2 | `quantity_2` | DECIMAL | 6 | － | - |
| カラー3 | `color_3` | VARCHAR | 900 | － | - |
| 台数3 | `quantity_3` | DECIMAL | 6 | － | - |
| カラー4 | `color_4` | VARCHAR | 900 | － | - |
| 台数4 | `quantity_4` | DECIMAL | 6 | － | - |
| カラー5 | `color_5` | VARCHAR | 900 | － | - |
| 台数5 | `quantity_5` | DECIMAL | 6 | － | - |
| 付属品標準価格 | `standard_price_of_accessories` | DECIMAL | 10 | － | - |
| 提供代金 | `provision_fee` | DECIMAL | 10 | － | - |
| 使用ポイント | `usage_points` | DECIMAL | 6 | － | - |
| 原価 | `cost` | DECIMAL | 11 | － | - |
| 紐付けサマリ番号 | `linked_summary_number` | VARCHAR | 90 | － | - |
| 原価予備費 | `cost_contingency` | DECIMAL | 8,0 | － | - |
