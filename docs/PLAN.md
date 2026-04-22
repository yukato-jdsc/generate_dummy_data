# CSVダミーデータ生成スクリプト設計

## Summary
`docs/format.md` に定義された CSV を生成する単一CLIを追加する。対象は `m_campaign_all.csv`、`m_agency_all.csv`、`m_agency_diff.csv`、`m_product_all.csv`。通常実行は軽量件数、`--full` 指定で本番想定件数を出力する。生成結果はデフォルト固定シードで再現可能にしつつ、`--seed` で変更できるようにする。CSVは `id` 列も含め、`docs/format.md` の列定義をそのまま出力する。

## Key Changes
- 新規CLIを 1 本追加する。想定インターフェース:
  - `uv run python generate_csv.py`
  - `--output-dir <dir>`: 出力先。既定は `generated_data/`
  - `--targets campaign,agency,product`: 生成対象の絞り込み。既定は全件
  - `--full`: 本番想定件数で生成
  - `--seed <int>`: 乱数シード。既定は固定値 `42`
- 生成件数プロファイルを内部定義する
  - 既定: `campaign=50`, `agency_all=1,000`, `agency_diff=53`, `product=1,000`
  - `--full`: `campaign=1,612`, `agency_all=1,200,000`, `agency_diff=53`, `product=122,802`
- `agency` を対象にした場合は常に `m_agency_all.csv` と `m_agency_diff.csv` をセットで生成する
  - 差分は独立生成ではなく、同じ実行で生成した `m_agency_all.csv` の母集団から 53 件を抽出して構成する
  - 差分対象は「前日断面から見て当日更新された行」という扱いにし、`valid_start_date` または `valid_end_date` が差分日付周辺になるように生成する
  - 差分行は全量CSVと同一ヘッダ・同一列構成とする
- 実装は「単一CLI + 定義埋め込み型」にする
  - CSVごとに列順、型、最大桁数、代表的なカテゴリ値、件数プロファイルをコード内で明示定義
  - Markdownを動的に解釈する実装にはしない
  - 書き出しは `csv.writer` による逐次出力で、全件をメモリ保持しない
- 文字コードと出力形式
  - `UTF-8 with BOM`、改行は標準CSV出力
  - ヘッダは `docs/format.md` のカラム名をそのまま使用し、`id` も含める
- 値生成ルール
  - `campaign`: `campaign_id` は一意なコード、名称と説明は日本語ベース、`effective_*` は `YYYY/MM/DD`、`old_flag` は `"0"` または `"1"` を分布付きで生成
  - `agency_all`: コード類は桁数に収まる一意値、住所・電話・担当者・法人名は日本向けダミー、カテゴリ系は少数のマスタ値から分布生成、開始終了日は矛盾しない範囲で生成
  - `agency_diff`: `agency_all` と同じ行生成ルールを使いながら、差分対象53件を抽出し、更新日寄りの有効期間に寄せる
  - `product`: 商品コード一意、開始日と開始時間の整合を持たせ、分類・名称系は商品カテゴリごとのテンプレートで生成
- 業務っぽさの範囲
  - 完全な外部参照整合までは持たせない
  - 同一CSV内では一意性、日付前後関係、フラグ値の妥当性、名称と分類の自然さを持たせる
  - `agency` は都道府県コードと名称、電話番号の地域感、法人名と担当者名の組み合わせを自然にする
  - `agency_diff` は `agency_all` の部分集合として扱える内容にする
- 実装分割
  - `generate_csv.py`: CLIと全体制御
  - 生成ロジックはファイル内の小さなクラスまたは関数群に分ける
  - 共通部品は「乱数」「日付」「文字列切り詰め」「日本語っぽい名称生成」「コード生成」に限定する
  - `agency` だけは「全量行生成」と「差分抽出」を分離する
- 依存関係
  - 既存の `faker` を利用して日本語名・住所風文字列を生成する
  - 追加ライブラリは入れない

## Error Handling / Validation
- 出力前に各CSV定義を検証する
  - ヘッダ重複なし
  - 件数が正数
  - `agency_diff` 件数が `agency_all` 件数を超えない
  - 生成値が最大桁数を超えた場合は切り詰めではなく生成側で再構成する
- 実行時エラー
  - 不正な `--targets` は即エラー終了
  - 出力先が作成できない場合は明示的なメッセージで終了
- 品質チェック
  - 各行の列数一致
  - 一意制約対象の重複なし
  - 日付の前後関係違反なし
  - `agency_diff` の `agent_code` が `agency_all` 内に存在する
  - フル生成時もメモリを過剰消費しない逐次処理
- 差分抽出方法
  - `agency_all` 生成時に差分候補53件だけを乱数サンプリングして保持する
  - 全120万件をメモリ保持せず、差分出力用に必要な53件のみを別バッファに残す

## Test Plan
- 単体テスト
  - 既定件数で 4 CSV が生成される
  - `--full` で指定件数になる
  - 同じ `--seed` では同一内容、別シードでは内容が変わる
  - `--targets` で対象絞り込みできる
  - `id` 列が出力される
- 内容検証テスト
  - ヘッダ順が仕様通り
  - 各列が桁数制約を超えない
  - 必須の一意コードが重複しない
  - `valid/effective start <= end`
  - 分類コードと分類名称の組み合わせが定義済みパターン内に収まる
  - `agency_diff` の全 `agent_code` が `agency_all` に含まれる
  - `agency_diff` は常に53件である
- 実運用寄り確認
  - `agency` の軽量件数で `m_agency_all.csv` と `m_agency_diff.csv` が同時生成される
  - `--full --targets agency` 実行でもプロセスがストリーム処理で安定する
  - `agency_diff` 抽出のために全量行をメモリ保持していないことを確認する

## Assumptions / Defaults
- `docs/format.md` にある `campaign` `agency` `product` だけを対象とする
- `agency` には `m_agency_all.csv` と `m_agency_diff.csv` が含まれる
- CSVには `id` を含める
- 軽量プロファイルは `campaign=50`, `agency_all=1,000`, `agency_diff=53`, `product=1,000`
- 差分CSVは全量CSVの部分集合として生成し、更新対象53件を表す
- 日付形式は仕様の VARCHAR 長に収まる `YYYY/MM/DD` または `YYYY/MM/DD HH:MM` 系を使い、時刻列は `HH:MM:SS` 相当で揃える
- 本番完全互換のマスタ整合ではなく、「型・桁数準拠 + 業務上それらしい分布」を成功条件とする
