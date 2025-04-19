# テストコードリファクタリング計画

## 1. 目的

`test/test_validation.py` ファイルが肥大化し、プロジェクトの技術選定指針に反して `unittest` を使用している問題を解消します。具体的には、以下の対応を行います。

*   テストフレームワークを `pytest` に統一します。
*   テスト対象のクラスごとにテストファイルを分割し、可読性とメンテナンス性を向上させます。
*   分割したテストファイルを `test/validation/` サブディレクトリに格納し、テストファイルの構成を整理します。

## 2. 参照ドキュメント

*   `docs/project/technology-selection.md`: プロジェクトで使用する技術スタック（pytestの使用を含む）
*   `docs/task_log/WIP_validation-implementation-plan.md`: 関連するバリデーション機能実装計画

## 3. 作業ステップ

1.  **計画文書の承認:** この文書の内容についてユーザーの承認を得ます。(完了)
2.  **作業ディレクトリの作成:** `test/validation/` ディレクトリを作成します。
3.  **テストファイルの分割とpytestへの移行:**
    *   `test/test_validation.py` 内の各テストクラス (`TestValidationContext`, `TestValidationResult`, `TestCompareExpression`, etc.) を、それぞれ独立したPythonファイルに分割します。
    *   分割後のファイルは `test/validation/` ディレクトリ配下に配置します。ファイル名は `test_<クラス名>.py` の形式とします（例: `test/validation/test_validation_context.py`）。
    *   各テストファイルの内容を `pytest` のスタイルに書き換えます。
        *   `unittest.TestCase` の継承を削除します。
        *   `setUp` メソッドを使用している場合は、`pytest.fixture` を使用するように変更します（必要に応じて）。
        *   `self.assertEqual()`, `self.assertTrue()`, `self.assertFalse()` などの `unittest` のアサーションメソッドを、`pytest` の `assert` 文に置き換えます。
4.  **元のテストファイルの削除:** `test/test_validation.py` ファイルを削除します。
5.  **テストの実行と確認:** `pytest` コマンドを実行し、リファクタリング後のすべてのテストが成功することを確認します。特に、以前問題が発生していた `TestNotExpression` に関連するテスト (`test/validation/test_not_expression.py`) が成功するかどうかを重点的に確認します。
6.  **完了報告と計画文書の更新:**
    *   すべてのテストが成功したら、ユーザーに作業完了を報告し、承認を求めます。
    *   承認後、この計画文書に作業結果（実行したコマンド、テスト結果の概要など）を追記し、ファイル名を `DONE_test-refactoring-plan.md` に変更します。

## 4. 成果物

*   `test/validation/` ディレクトリ
*   `test/validation/test_validation_context.py`
*   `test/validation/test_validation_result.py`
*   `test/validation/test_compare_expression.py`
*   `test/validation/test_required_expression.py`
*   `test/validation/test_regex_match_expression.py`
*   `test/validation/test_enum_expression.py`
*   `test/validation/test_all_of_expression.py`
*   `test/validation/test_any_of_expression.py`
*   `test/validation/test_not_expression.py`
*   `test/validation/test_rule.py`
*   `test/validation/test_validation_engine.py`
*   更新された `docs/task_log/DONE_test-refactoring-plan.md`

## 5. 確認事項

*   リファクタリング後、すべてのテストが `pytest` で正常に実行され、成功すること。
*   `TestNotExpression` のテストが成功すること。失敗する場合は、原因調査と修正を別途計画します。

## 6. 作業進捗（2025-04-19時点）

- `test/validation/`ディレクトリを作成済み。
- `test/test_validation.py`から以下のテストクラスをpytestスタイルで分割・移行済み：
    - `TestValidationContext` → `test/validation/test_validation_context.py`
    - `TestValidationResult` → `test/validation/test_validation_result.py`
    - `TestCompareExpression` → `test/validation/test_compare_expression.py`
- 今後の予定：
    - `TestRequiredExpression`以降の各テストクラスも順次pytestスタイルで分割・移行する。
    - 全クラス移行後、`test/test_validation.py`を削除し、pytestで全テストが成功することを確認する。
