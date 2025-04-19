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

6.  **単体テスト作成/更新:** (完了)
    *   `test/test_validation.py` に実装していた各クラスの単体テストを、pytestスタイルで `test/validation/` 配下に分割・移行しました。
    *   `ValidationContext`, `ValidationResult`, 各 `Expression` 派生クラス、`Rule` クラス、`ValidationEngine` クラスのテストを `test/validation/` 配下の各ファイルに実装しました。
    *   `test/test_validation.py` は削除済みです。
    *   すべてのテストが成功することを確認しました。

7.  **テスト修正計画の作成:** (完了)
    * 失敗しているテストの問題点を特定し、修正計画を作成しました。

8.  **循環インポートの解消:** (完了)
    *   `validation_common.py` を作成し、共通クラスを分離することで循環インポートを解消しました。
    *   関連するモジュール (`validation.py`, `config_loader.py`, `test/validation/`配下のテスト) のインポート文を修正しました。

9.  **テスト修正の実装:** (完了)
    *   `TestValidationEngine` のモックパスを修正しました。
    *   すべての単体テストが成功することを確認しました。

10. **統合テスト更新:** (完了)
    *   `test/test_cli_integration.py` のテストケースを修正し、バリデーション機能のテストが成功することを確認しました。
    *   バリデーション成功・失敗ケースのテストデータを準備し、テストを実行しました。

11. **テスト実行と確認:** (完了)
    *   単体テスト (`test/validation/`) と統合テスト (`test/test_cli_integration.py`) の両方が成功することを確認しました。

12. **不要コードの削除:** (完了)
    *   `src/xlsx_value_picker/config.py` ファイルを削除しました。

## 4. 成果物 (作成状況)

-   `src/xlsx_value_picker/validation_common.py` (新規作成、完了)
-   `src/xlsx_value_picker/validation.py` (修正、完了)
-   `src/xlsx_value_picker/config_loader.py` (修正、完了)
-   `src/xlsx_value_picker/excel_processor.py` (修正、完了)
-   `src/xlsx_value_picker/cli.py` (修正、完了)
-   `test/validation/` 配下の各テストファイル（`test_validation_context.py` など）(新規作成、完了)
-   `test/test_validation.py` (削除済み)
-   `test/test_cli_integration.py` (修正、完了)
-   テスト用データファイル (準備、完了)
-   `docs/spec/rule-schema.json` (修正、完了)
-   `docs/spec/cli-spec.md` (未修正)
-   `src/xlsx_value_picker/config.py` (削除済み)

## 5. 現在の課題

1.  **ドキュメントの未更新:**
    *   バリデーション機能の追加に伴う `cli-spec.md` の更新が必要です。
    *   `rule-schema.json` は更新済みですが、`cli-spec.md` はまだ更新されていません。

## 6. 次のステップ

1.  **ドキュメント更新:**
    *   `docs/spec/cli-spec.md` に、`--validate-only` および `--ignore-errors` オプションに関する説明を追加します。
    *   必要に応じて、他の設計ドキュメントやREADMEも更新します。

2.  **全テスト実行と確認:**
    *   すべてのテスト (`pytest`) を実行し、プロジェクト全体のテストが成功することを確認します。

3.  **作業完了確認:**
    *   すべての作業が完了したら、ユーザーに報告し、完了の承認を求めます。
