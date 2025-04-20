# バリデーション式モデルの移動計画

## 1. 目的

`config_loader.py` からバリデーション式関連のモデルとヘルパー関数を新しいファイル `validation_expressions.py` に移動し、モジュールの責務を明確化します。

## 2. 背景

現状、`config_loader.py` に設定読み込みロジックとバリデーション式の定義が混在しており、モジュールの凝集度が低くなっています。バリデーション関連のコードを専用モジュールに分離することで、可読性と保守性を向上させます。

## 3. 作業計画

1.  **新規ファイル作成:** `src/xlsx_value_picker/validation_expressions.py` を作成します。 **(完了)**
2.  **コード移動:**
    - `config_loader.py` から `Expression` 基底クラスおよび全ての派生クラス (`CompareExpression`, `RequiredExpression`, `RegexMatchExpression`, `EnumExpression`, `AllOfExpression`, `AnyOfExpression`, `NotExpression`) を `validation_expressions.py` に移動します。 **(完了)**
    - `config_loader.py` からバリデーション式関連のヘルパー関数 (`detect_expression_type`, `convert_expression`) を `validation_expressions.py` に移動します。 **(完了)**
    - `validation_common.py` の `IExpression` インターフェースを `validation_expressions.py` に移動します。 **(完了)**
3.  **依存関係修正:**
    - `config_loader.py` の `Rule` モデル内で `ExpressionType` を `validation_expressions.ExpressionType` からインポートするように修正します。 **(完了)**
    - `validation.py` が `validation_expressions` を参照するように修正します。 **(確認済み、修正不要)**
    - その他、移動に伴う import 文の修正を各ファイルで行います。 **(完了)**
4.  **テスト実行:** `uv run pytest` を実行し、すべてのテストが成功することを確認します。 **(完了)**

## 4. 作業手順

1.  本計画書についてユーザーの承認を得ます。 **(完了)**
2.  承認後、ファイル名を `WIP_move-validation-expressions.md` に変更します。 **(完了)**
3.  上記「3. 作業計画」に従ってリファクタリングを実施します。 **(完了)**
4.  テストを実行し、すべてのテストが成功することを確認します。 **(完了)**
5.  作業完了後、本計画書に結果を追記し、ファイル名を `DONE_move-validation-expressions.md` に変更してユーザーに完了報告を行います。 **(実施中)**

## 5. 影響範囲

- `src/xlsx_value_picker/config_loader.py`
- `src/xlsx_value_picker/validation_common.py`
- `src/xlsx_value_picker/validation.py`
- (新規作成) `src/xlsx_value_picker/validation_expressions.py`
- 上記ファイルの import 文を使用しているテストコード (`test/` ディレクトリ以下)

## 6. リスク

- コード移動に伴う import エラー。
    - 対策: 慎重に import 文を修正し、テストで確認します。 **(実施済み、テスト成功)**
- 意図しない動作変更（デグレード）。
    - 対策: テスト実行を徹底します。 **(実施済み、テスト成功)**

## 7. 承認

ユーザー確認済み。

## 8. 作業結果

- `src/xlsx_value_picker/validation_expressions.py` を新規作成し、関連するクラスと関数を移動しました。
- `src/xlsx_value_picker/config_loader.py` と `src/xlsx_value_picker/validation_common.py` から移動したコードを削除し、インポート文を修正しました。
- `test/` ディレクトリ以下のテストコードのインポート文を修正しました。
- `uv run pytest` を実行し、すべてのテスト (127件) が成功することを確認しました。