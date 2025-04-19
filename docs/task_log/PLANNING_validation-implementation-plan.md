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

1.  **基本クラス定義:** (一部実装済み、要確認)
    *   `src/xlsx_value_picker/validation.py` を新規作成、または既存の関連モジュール (例: `config_loader.py` や `models.py` など) に配置する。
    *   設計ドキュメント (`validation-design.md`) に基づき、`ValidationContext`, `ValidationResult` クラスを定義する。
2.  **Expressionモデルへの検証ロジック実装:** (未実装)
    *   `src/xlsx_value_picker/config_loader.py` (またはモデル定義を分離したファイル) 内の各 `Expression` 派生クラス (`CompareExpression`, `RequiredExpression`, `AnyOfExpression`, `AllOfExpression`, `NotExpression`, `RegexMatchExpression`, `EnumExpression`) に `validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult` メソッドを実装する。
    *   各メソッドは、自身の定義と `ValidationContext` に基づいて検証を行い、`ValidationResult` を返す。
3.  **RuleModelへの検証実行メソッド実装:** (未実装)
    *   `config_loader.py` (またはモデル定義ファイル) 内の `RuleModel` に `validate(self, context: ValidationContext) -> ValidationResult` メソッドを実装する。
    *   このメソッドは、内部で保持する `expression` オブジェクトの `validate` メソッドを呼び出し、結果を返す。
4.  **バリデーション実行処理:** (未実装)
    *   `src/xlsx_value_picker/excel_processor.py` の `ExcelValueExtractor` クラス、または新たに作成する `ExcelProcessor` クラスに、バリデーション実行ロジックを追加する。
    *   `config_loader` から取得した `List[RuleModel]` を受け取る。
    *   各 `RuleModel` の `validate` メソッドを呼び出し、`ValidationContext` を渡して検証を実行する。
    *   すべての `ValidationResult` を収集して返す。
5.  **CLI統合:** (一部実装済み、要修正)
    *   `src/xlsx_value_picker/cli.py` の `main` 関数を修正する。
    *   `ExcelProcessor` (または修正後の `ExcelValueExtractor`) を呼び出し、データとバリデーション結果 (`List[ValidationResult]`) を取得する。
    *   `--validate-only` オプションが指定された場合、バリデーション結果のみを整形して出力する。
    *   バリデーションエラーがあり、`--ignore-errors` が指定されていない場合は、エラーメッセージを出力し、非ゼロの終了コードで終了する。
    *   通常実行時は、バリデーション結果に応じて処理を分岐する（エラーがあればログ出力やエラー終了、なければ通常出力）。
    *   バリデーション結果の出力形式（JSON）を実装する。ログファイル出力 (`--log`) も実装する。
6.  **単体テスト作成/更新:** (未実装)
    *   `test/test_validation.py` を新規作成、または `test/test_config_loader.py` を拡張する。
    *   各 `Expression` 派生クラスの `validate` メソッドに対する単体テストを作成する。
    *   `RuleModel` の `validate` メソッドに対する単体テストを作成する。
    *   `ValidationContext`, `ValidationResult` の単体テストを作成する。
7.  **統合テスト更新:** (未実装)
    *   `test/test_cli_integration.py` を修正する。
    *   バリデーションが成功するケース、失敗するケース（エラー出力、`--validate-only`, `--ignore-errors`, `--log` オプションの動作確認を含む）のテストを追加する。
    *   テスト用の設定ファイル (`test/data/config_with_validation.yaml` など) とExcelファイル (`test/data/test_validation.xlsx` など) を準備する。
8.  **テスト実行と確認:** (未実施)
    *   `uv run pytest` を実行し、すべてのテストが成功することを確認する。
9.  **不要コードの削除:** (未実施)
    *   `src/xlsx_value_picker/config.py` は現在の設計 (`config_loader.py`, `excel_processor.py`) と重複・矛盾するため、削除する。
    *   `config.py` に関連するテストコードが存在する場合（例: `test/test_config.py` など）、それらも合わせて削除する。

## 4. 成果物 (更新)

-   `src/xlsx_value_picker/validation.py` (新規作成または既存ファイルに統合)
-   `src/xlsx_value_picker/config_loader.py` (またはモデル定義ファイル) (修正)
-   `src/xlsx_value_picker/excel_processor.py` (修正)
-   `src/xlsx_value_picker/cli.py` (修正)
-   `test/test_validation.py` (新規作成または既存テストファイルに統合)
-   `test/test_cli_integration.py` (修正)
-   テスト用データファイル (新規作成)
-   `docs/spec/rule-schema.json` (修正)
-   `docs/spec/cli-spec.md` (修正)
-   `src/xlsx_value_picker/config.py` (削除)
-   (場合により) `config.py` に関連するテストコード (削除)

## 5. その他

-   エラーメッセージのフォーマットや内容は設計ドキュメントに従う。
-   実装中に設計ドキュメントとの齟齬や改善点が見つかった場合は、適宜ドキュメントを更新する。
