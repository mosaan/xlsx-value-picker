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
    *   現在、一部テストが失敗しています：
        - `TestNotExpression.test_not_invalid` - `NotExpression`の初期化でエラーが発生
        - `TestNotExpression.test_not_valid` - `NotExpression`の初期化でエラーが発生 
        - `TestValidationEngine.test_validate` - `ValidationEngine`のモックテストでエラーが発生

7.  **統合テスト更新:** (作業中)
    *   `test/test_cli_integration.py` の更新を開始しましたが、まだ完了していません。
    *   バリデーション成功・失敗ケースのテストファイルを準備中です。

8.  **テスト実行と確認:** (未実施)
    *   現時点では一部テストが失敗しているため、テスト実行による確認が完了していません。
    *   失敗テストの修正が必要です。
    
9.  **不要コードの削除:** (完了)
    *   `src/xlsx_value_picker/config.py` ファイルを削除しました。このファイルは現在の設計と矛盾しており、新しい実装に置き換えられました。

## 4. 成果物 (作成状況)

-   `src/xlsx_value_picker/validation.py` (新規作成、完了)
-   `src/xlsx_value_picker/config_loader.py` (修正、完了)
-   `src/xlsx_value_picker/excel_processor.py` (修正、完了)
-   `src/xlsx_value_picker/cli.py` (修正、完了)
-   `test/test_validation.py` (新規作成、一部テストが失敗)
-   `test/test_cli_integration.py` (修正中)
-   テスト用データファイル (準備中)
-   `docs/spec/rule-schema.json` (まだ修正していません)
-   `docs/spec/cli-spec.md` (まだ修正していません)
-   `src/xlsx_value_picker/config.py` (削除済み)

## 5. 現在の課題

1. テストの修正
   - `NotExpression`クラスのテストが失敗しています。これはフィールド名の定義（`not_` と `not` のエイリアス）と、テスト時の引数指定方法に問題があると思われます。
   - `ValidationEngine`のモックテストが失敗しています。`get_excel_values`関数のインポートパスに関する問題があるようです。

2. 統合テストの完成
   - CLIのバリデーション機能に対する統合テストを完成させる必要があります。
   - テスト用のExcelファイルと設定ファイルを準備する必要があります。

3. ドキュメント更新
   - `rule-schema.json`と`cli-spec.md`の更新が必要です。

## 6. 次のステップ

1. テスト失敗の修正
   - NotExpressionのテストコードの修正
   - ValidationEngineのモックテストの修正

2. 統合テストの完成
   - 統合テスト用のファイル準備
   - `test_cli_integration.py`の更新完了

3. 実装確認
   - すべてのテストを実行して確認

4. ドキュメント更新
   - 設計ドキュメントとの一貫性確認
   - APIドキュメントの更新
   - `rule-schema.json`の更新
   - `cli-spec.md`の更新
