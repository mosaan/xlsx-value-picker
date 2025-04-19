# バリデーション機能実装計画

## 1. 目的

`xlsx-value-picker` に、設定ファイルに基づいてExcelファイルの内容を検証するバリデーション機能を追加実装する。

## 2. 参照ドキュメント

-   [バリデーションエンジンの設計ドキュメント](../design/validation-design.md)
-   [JSONスキーマに基づく設定データ読み込み機能の設計](../design/config-loader-design.md)
-   [設定ファイル仕様](../../spec/rule-schema.json) (※バリデーションルールに関する定義を追記する必要がある)
-   [CLI仕様](../../spec/cli-spec.md) (※バリデーション関連オプションを追記する必要がある)

## 3. 作業ステップ

1.  **基本クラス定義:** (未実装)
    *   `src/xlsx_value_picker/validation.py` を新規作成する。
    *   設計ドキュメント (`validation-design.md`) に基づき、`ValidationContext`, `ValidationResult`, `Rule` (ABC) の基本クラスを定義する。
2.  **基本ルール実装:** (未実装)
    *   `validation.py` に `CompareRule`, `RequiredRule` を実装する。これらは `Rule` を継承し、`config_loader.py` の `CompareExpression`, `RequiredExpression` モデルを受け取って初期化できるようにする。
3.  **複合ルール実装:** (未実装)
    *   `validation.py` に `AnyOfRule` を実装する。これも `Rule` を継承し、`config_loader.py` の `AnyOfExpression` モデルを受け取って初期化できるようにする。（他の複合ルール `AllOfRule`, `NotRule` も同様に実装）
4.  **ルールオブジェクト生成処理:** (一部実装済み、要修正)
    *   `src/xlsx_value_picker/validation.py` に、`config_loader.py` でパースされた `Rule` モデル (Pydantic) を受け取り、ステップ1-3で定義した `Rule` インターフェース実装クラスのオブジェクトリストを生成するファクトリ関数またはクラス (`create_validation_rules` など) を実装する。
    *   `config_loader.py` の `ConfigModel` に `rules: List[RuleModel]` (Pydanticモデル) フィールドは既に存在するが、`Rule` インターフェース実装クラスのリストを保持するフィールドは不要（実行時に生成するため）。
5.  **バリデーションエンジン実装:** (未実装)
    *   `validation.py` に `ValidationEngine` クラスを実装する。
    *   コンストラクタで `List[Rule]` (インターフェース実装クラス) を受け取る。
    *   `validate` メソッドは `ValidationContext` を受け取り、`List[ValidationResult]` を返すようにする。
6.  **Excelプロセッサ統合:** (一部実装済み、要修正)
    *   `src/xlsx_value_picker/excel_processor.py` の `ExcelValueExtractor` クラスを修正、または新たに `ExcelProcessor` のような統括クラスを作成する。
    *   `ValidationEngine` を利用するように修正する。
    *   値抽出 (`extract_values`) 後に `ValidationEngine.validate` を呼び出し、バリデーションを実行する。
    *   バリデーション結果 (`List[ValidationResult]`) を返すようにする。
7.  **CLI統合:** (一部実装済み、要修正)
    *   `src/xlsx_value_picker/cli.py` の `main` 関数を修正する。
    *   `ExcelProcessor` (または修正後の `ExcelValueExtractor`) を呼び出し、データとバリデーション結果を取得する。
    *   `--validate-only` オプションが指定された場合、バリデーション結果のみを整形して出力する。
    *   バリデーションエラーがあり、`--ignore-errors` が指定されていない場合は、エラーメッセージを出力し、非ゼロの終了コードで終了する。
    *   通常実行時は、バリデーション結果に応じて処理を分岐する（エラーがあればログ出力やエラー終了、なければ通常出力）。
    *   バリデーション結果の出力形式（JSON）を実装する。ログファイル出力 (`--log`) も実装する。
8.  **単体テスト作成:** (未実装)
    *   `test/test_validation.py` を新規作成する。
    *   各 `Rule` クラス（`CompareRule`, `RequiredRule`, `AnyOfRule` など）の単体テストを作成する。
    *   ルールオブジェクト生成処理 (`create_validation_rules`) の単体テストを作成する。
    *   `ValidationEngine` の単体テストを作成する。
9.  **統合テスト更新:** (未実装)
    *   `test/test_cli_integration.py` を修正する。
    *   バリデーションが成功するケース、失敗するケース（エラー出力、`--validate-only`, `--ignore-errors`, `--log` オプションの動作確認を含む）のテストを追加する。
    *   テスト用の設定ファイル (`test/data/config_with_validation.yaml` など) とExcelファイル (`test/data/test_validation.xlsx` など) を準備する。
10. **テスト実行と確認:** (未実施)
    *   `uv run pytest` を実行し、すべてのテストが成功することを確認する。
11. **不要コードの削除:** (新規追加)
    *   `src/xlsx_value_picker/config.py` は現在の設計 (`config_loader.py`, `excel_processor.py`) と重複・矛盾するため、削除する。
    *   `config.py` に関連するテストコードが存在する場合（例: `test/test_config.py` など）、それらも合わせて削除する。

## 4. 成果物 (更新)

-   `src/xlsx_value_picker/validation.py` (新規作成)
-   `src/xlsx_value_picker/excel_processor.py` (修正)
-   `src/xlsx_value_picker/cli.py` (修正)
-   `test/test_validation.py` (新規作成)
-   `test/test_cli_integration.py` (修正)
-   テスト用データファイル (新規作成)
-   `docs/spec/rule-schema.json` (修正)
-   `docs/spec/cli-spec.md` (修正)
-   `src/xlsx_value_picker/config.py` (削除)
-   (場合により) `config.py` に関連するテストコード (削除)

## 5. その他

-   エラーメッセージのフォーマットや内容は設計ドキュメントに従う。
-   実装中に設計ドキュメントとの齟齬や改善点が見つかった場合は、適宜ドキュメントを更新する。
