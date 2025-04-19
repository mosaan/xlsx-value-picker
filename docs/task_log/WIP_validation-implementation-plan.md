# バリデーション機能実装計画

## 1. 目的

`xlsx-value-picker` に、設定ファイルに基づいてExcelファイルの内容を検証するバリデーション機能を追加実装する。

## 2. 参照ドキュメント

-   [バリデーションエンジンの設計ドキュメント](../design/validation-design.md) (更新済み)
-   [Pydanticモデル設計ガイドライン](../guide/pydantic-model-design-guideline.md) (新規作成)
-   [JSONスキーマに基づく設定データ読み込み機能の設計](../design/config-loader-design.md)
-   [設定ファイル仕様](../spec/rule-schema.json) (※バリデーションルールに関する定義を追記する必要がある)
-   [CLI仕様](../spec/cli-spec.md) (※バリデーション関連オプションを追記する必要がある)

## 3. 作業ステップ

1.  **基本クラス定義:** (完了)
    *   `src/xlsx_value_picker/validation.py` を新規作成し、`ValidationContext`, `ValidationResult`, `IExpression` クラスと `ValidationEngine` を実装しました。
    *   設計ドキュメント (`validation-design.md`) に基づき、コンテキストや結果を表すクラスを定義しました。

2.  **Expressionモデルへの検証ロジック実装:** (完了)
    *   `config_loader.py` の各 `Expression` 派生クラス (`CompareExpression`, `RequiredExpression`, `AnyOfExpression`, `AllOfExpression`, `NotExpression`, `RegexMatchExpression`, `EnumExpression`) に `validate` メソッドを実装しました。
    *   各メソッドは、自身の定義と `ValidationContext` に基づいて検証を行い、`ValidationResult` を返します。

3.  **RuleModelへの検証実行メソッド実装:** (完了)
    *   `config_loader.py` 内の `Rule` クラス（設計ドキュメント内では `RuleModel`）に `validate` メソッドを実装しました。
    *   このメソッドは内部で保持する `expression` オブジェクトの `validate` メソッドを呼び出し、結果を返します。

4.  **バリデーション実行処理:** (完了)
    *   `excel_processor.py` に `get_excel_values` 関数を追加し、`ValidationEngine` からバリデーションに必要な値を取得できるようにしました。
    *   `ValidationEngine` クラスに、ルールに基づくバリデーション実行ロジックを実装しました。

5.  **CLI統合:** (完了)
    *   `cli.py` を修正し、`ValidationEngine` を使用したバリデーション処理を統合しました。
    *   `--validate-only` オプションのサポートを実装しました。
    *   バリデーションエラーがあった場合の処理とメッセージ出力を実装しました。
    *   `--ignore-errors` オプションのサポートも実装しています。
    *   バリデーション結果のログファイル出力 (`--log`) も実装しました。

6.  **単体テスト作成/更新:** (部分的に完了、一部テストが失敗)
    *   `test/test_validation.py` を新規作成し、各クラスに対する単体テストを実装しました。
    *   `ValidationContext`, `ValidationResult`, 各 `Expression` 派生クラス、`Rule` クラス、`ValidationEngine` クラスのテストを作成しました。
    *   現在、`TestNotExpression` のテストが失敗しています。

7.  **テスト修正計画の作成:** (完了)
    * 失敗しているテストの問題点を特定し、修正計画を作成しました。

8.  **循環インポートの解消:** (完了)
    *   `validation_common.py` を作成し、共通クラスを分離することで循環インポートを解消しました。
    *   関連するモジュール (`validation.py`, `config_loader.py`, `test_validation.py`) のインポート文を修正しました。

9.  **テスト修正の実装:** (作業中)
    *   `TestValidationEngine` のモックパスを修正しました。
    *   `TestNotExpression` のテスト修正を試みましたが、依然として失敗しています。

10. **統合テスト更新:** (未着手)
    *   `test/test_cli_integration.py` の更新はまだ行っていません。
    *   バリデーション成功・失敗ケースのテストファイルも準備が必要です。

11. **テスト実行と確認:** (未実施)
    *   `TestNotExpression` のテストが失敗しているため、全テストの成功は確認できていません。

12. **不要コードの削除:** (完了)
    *   `src/xlsx_value_picker/config.py` ファイルを削除しました。

## 4. 成果物 (作成状況)

-   `src/xlsx_value_picker/validation_common.py` (新規作成、完了)
-   `src/xlsx_value_picker/validation.py` (修正、完了)
-   `src/xlsx_value_picker/config_loader.py` (修正、完了)
-   `src/xlsx_value_picker/excel_processor.py` (修正、完了)
-   `src/xlsx_value_picker/cli.py` (修正、完了)
-   `test/test_validation.py` (修正、一部テストが失敗)
-   `test/test_cli_integration.py` (未修正)
-   テスト用データファイル (未準備)
-   `docs/spec/rule-schema.json` (未修正)
-   `docs/spec/cli-spec.md` (未修正)
-   `src/xlsx_value_picker/config.py` (削除済み)

## 5. 現在の課題

1.  **`TestNotExpression` のテスト失敗:**
    *   `NotExpression` クラスのインスタンス化時に `ValidationError` が発生しています。
    *   原因は、Pydanticモデルのフィールドにエイリアス (`alias='not'`) が設定されている場合に、Pythonコード内で直接インスタンス化する方法にあると考えられます。
    *   `NotExpression(not_=...)` や `NotExpression.model_validate({"not": ...})` のいずれの方法でも解決できていません。Pydanticの仕様やドキュメントを確認し、エイリアス付きフィールドを持つモデルをコード内で正しく初期化する方法を特定する必要があります。

2.  **統合テストの未実装:**
    *   CLIのバリデーション機能に対する統合テスト (`test/test_cli_integration.py`) が未実装です。
    *   テスト用のExcelファイルと設定ファイル（成功ケース、失敗ケース）を準備する必要があります。

3.  **ドキュメントの未更新:**
    *   バリデーション機能の追加に伴う `rule-schema.json` と `cli-spec.md` の更新が必要です。

## 6. 次のステップ

1.  **`NotExpression` テストの修正 (最優先):**
    *   Pydanticのドキュメントや関連情報を調査し、エイリアス (`alias`) が設定されたフィールドを持つモデルをPythonコード内でインスタンス化する正しい方法を特定します。
    *   特定した方法に基づいて `test/test_validation.py` の `TestNotExpression` を修正します。
    *   `pytest -xvs test/test_validation.py` を実行し、すべてのテストが成功することを確認します。

2.  **統合テストの実装:**
    *   バリデーション成功・失敗ケースを含むテスト用のExcelファイルと設定ファイル (`config.yaml` など) を `test/data` ディレクトリに準備します。
    *   `test/test_cli_integration.py` に、`--validate-only` オプションや `--ignore-errors` オプションを使用した際のCLIの動作を検証するテストケースを追加します。

3.  **実装確認:**
    *   すべてのテスト (`pytest`) を実行し、成功することを確認します。

4.  **ドキュメント更新:**
    *   `docs/spec/rule-schema.json` に、バリデーションルール (`compare`, `required`, `regex_match`, `enum`, `all_of`, `any_of`, `not`) の定義を追加・更新します。
    *   `docs/spec/cli-spec.md` に、`--validate-only` および `--ignore-errors` オプションに関する説明を追加します。
    *   必要に応じて、他の設計ドキュメントやREADMEも更新します。

5.  **作業完了確認:**
    *   すべての作業が完了したら、ユーザーに報告し、完了の承認を求めます。
