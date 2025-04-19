# JSONスキーマに基づく設定データ読み込み機能のテスト実装計画

## 1. 概要

このドキュメントでは、新たに実装したJSONスキーマに基づく設定データ読み込み機能に対するテスト計画について詳述します。テストは既存のテスト手法に沿って実装し、新機能の正常動作を確認します。

## 2. テスト対象機能

以下の新しく実装したモジュールに対するテストを行います：

1. **config_loader.py** - 設定ファイルの読み込みとJSONスキーマ検証
2. **excel_processor.py** - 設定に基づくExcelファイルからの値抽出
3. **output_formatter.py** - データの各種フォーマットへの出力
4. **cli.py** - コマンドラインインターフェース

## 3. テストの種類

### 3.1 単体テスト

各コンポーネントが正しく動作することを確認するテストを実施します。

* **ConfigParser** - YAMLとJSONファイルの読み込みテスト
* **SchemaValidator** - JSONスキーマでの設定検証テスト
* **Pydanticモデル** - 設定データのバリデーションテスト
* **ExcelValueExtractor** - Excelファイルからの値抽出テスト
* **OutputFormatter** - 各種フォーマットへの出力テスト

### 3.2 統合テスト

複数のコンポーネントを組み合わせた時の動作を確認するテストを実施します。

* **設定からExcel値抽出まで** - 設定を読み込み、その設定に基づいてExcelから値を抽出するテスト
* **設定からデータ出力まで** - 設定に基づいてデータを出力するテスト

### 3.3 E2Eテスト

コマンドラインからの実行を含む一連の処理が正しく動作することを確認するテストを実施します。

* **CLIからの実行** - 実際のコマンドラインオプションを使用したテスト

## 4. テストファイル構成

新規に作成するテストファイルは以下の通りです：

1. **test_config_loader.py** - 設定読み込み機能のテスト
2. **test_excel_processor.py** - Excel処理機能のテスト
3. **test_output_formatter.py** - 出力フォーマット機能のテスト
4. **test_cli_integration.py** - CLI統合テスト

## 5. テストケース一覧

### 5.1 設定読み込み機能のテスト (test_config_loader.py)

1. **test_config_parser_yaml** - YAMLファイルの読み込みテスト
2. **test_config_parser_json** - JSONファイルの読み込みテスト
3. **test_config_parser_invalid_extension** - 不正な拡張子のファイル読み込みテスト
4. **test_schema_validator_valid** - 正常な設定ファイルの検証テスト
5. **test_schema_validator_invalid** - 不正な設定ファイルの検証テスト
6. **test_config_model_valid** - 正常なデータでのモデル検証テスト
7. **test_config_model_invalid** - 不正なデータでのモデル検証テスト
8. **test_expression_models** - 各種式モデルのテスト
9. **test_config_loader_integration** - 設定ローダーの統合テスト

### 5.2 Excel処理機能のテスト (test_excel_processor.py)

1. **test_excel_value_extractor_init** - 初期化テスト
2. **test_excel_value_extractor_nonexistent_file** - 存在しないファイルのテスト
3. **test_excel_value_extractor_valid_cells** - 有効なセル参照のテスト
4. **test_excel_value_extractor_invalid_cells** - 無効なセル参照のテスト
5. **test_excel_value_extractor_include_empty** - 空セル含める/含めないテスト

### 5.3 出力フォーマット機能のテスト (test_output_formatter.py)

1. **test_output_formatter_init** - 初期化テスト
2. **test_output_formatter_json** - JSON出力テスト
3. **test_output_formatter_yaml** - YAML出力テスト
4. **test_output_formatter_jinja2_string** - Jinja2文字列テンプレートテスト
5. **test_output_formatter_jinja2_file** - Jinja2ファイルテンプレートテスト
6. **test_output_formatter_invalid_format** - 無効な出力形式テスト
7. **test_output_formatter_write_file** - ファイル書き込みテスト

### 5.4 CLI統合テスト (test_cli_integration.py)

1. **test_cli_valid_config** - 有効な設定ファイルでのCLI実行テスト
2. **test_cli_invalid_config** - 無効な設定ファイルでのCLI実行テスト
3. **test_cli_output_to_file** - ファイル出力オプションテスト
4. **test_cli_output_to_stdout** - 標準出力オプションテスト
5. **test_cli_schema_option** - スキーマオプションテスト
6. **test_cli_include_empty_cells** - 空セルオプションテスト

## 6. テスト実行方法

テストは以下のコマンドで実行します：

```bash
pytest -xvs test/test_config_loader.py test/test_excel_processor.py test/test_output_formatter.py test/test_cli_integration.py
```

特定のテストのみを実行する場合は以下のように指定します：

```bash
pytest -xvs test/test_config_loader.py::test_config_parser_yaml
```

## 7. テストデータ

テスト用のデータは `test/data` ディレクトリに配置します。新規に以下のテストデータを作成します：

1. **valid_config.yaml** - 有効なYAML設定ファイル
2. **valid_config.json** - 有効なJSON設定ファイル
3. **invalid_config.yaml** - 無効なYAML設定ファイル
4. **template.j2** - テスト用テンプレートファイル

## 8. モック化の方針

以下のコンポーネントについては、テストの独立性を保つためにモック化を検討します：

1. **ファイル操作** - 実際のファイルシステムを操作せずにモック化
2. **スキーマ検証** - 実際のJSONスキーマ検証をモック化する場面もある

## 9. 実装スケジュール

1. 基本的なテストケース作成 - 1日
2. モック化の実装 - 0.5日
3. テストデータの準備 - 0.5日
4. テスト実行と修正 - 1日

## 10. 注意事項

- テストは可能な限り独立しており、テスト間の依存関係がないようにします
- テスト環境の状態変更は最小限に抑え、テスト前後で環境をクリーンアップします
- エラーケースもしっかりとテストし、適切なエラーメッセージが返されることを確認します

---

このテスト実装計画に基づいて、各テストファイルを作成していきます。