# CLIエラーハンドリング改善計画

## 1. 目的

`cli.py` におけるエラーハンドリング処理、特に `--ignore-errors` オプションに関連するロジックを簡素化し、可読性と保守性を向上させます。

## 2. 背景

現状の `cli.py` では、設定読み込み、バリデーション、Excel処理、出力処理の各段階で `try...except` ブロックと `--ignore-errors` フラグのチェックがネストしており、コードの流れが複雑になっています。エラー発生時の処理フローを一貫性のあるシンプルな形に改善する必要があります。

## 3. 作業計画 (検討事項含む)

1.  **現状分析:** `cli.py` の `main` 関数内のエラーハンドリング箇所を詳細に分析し、複雑さの原因となっている箇所を特定します。 **(完了)**
2.  **改善方針検討:** 以下のいずれか、または組み合わせによる改善方針を検討します。 **(完了: 共通エラー処理関数、コンテキストマネージャ、独自例外クラスの導入を決定)**
    *   ~~エラーハンドリング用デコレータ: エラー処理と `--ignore-errors` のチェックを共通化するデコレータを作成し、各処理関数に適用する。~~
    *   **共通エラー処理関数:** エラー発生時のログ出力や終了処理をまとめた共通関数を作成し、各 `except` ブロックから呼び出す。
    *   **コンテキストマネージャ:** リソース管理（Excelファイルなど）とエラーハンドリングを組み合わせたコンテキストマネージャを導入する。
    *   **例外クラスの整理:** プロジェクト固有の例外クラスを定義し、より詳細なエラーハンドリングを可能にする。
3.  **実装:** 決定した方針に基づき、`cli.py` のエラーハンドリング部分をリファクタリングします。 **(完了)**
    *   `src/xlsx_value_picker/exceptions.py` 作成 **(完了)**
    *   `src/xlsx_value_picker/excel_processor.py` 修正 (コンテキストマネージャ対応) **(完了)**
    *   `src/xlsx_value_picker/cli.py` リファクタリング **(完了)**
    *   `src/xlsx_value_picker/config_loader.py` 修正 (例外処理改善) **(完了)**
4.  **テスト:** `--ignore-errors` オプションの有無による動作の違いを含め、エラー発生時の挙動が期待通りであることを確認するテストケースを追加・修正します。 **(完了)**
    *   `test/test_cli_integration.py` 修正 **(完了)**
    *   `test/test_excel_processor.py` 修正 **(完了)**
    *   `test/test_config_loader.py` 修正 **(完了)**
5.  **テスト実行:** `uv run pytest` を実行し、すべてのテストが成功することを確認します。 **(完了)**

## 4. 作業手順

1.  本計画書についてユーザーの承認を得ます。 **(完了)**
2.  承認後、ファイル名を `WIP_improve-cli-error-handling.md` に変更します。 **(完了)**
3.  上記「3. 作業計画」に従ってリファクタリングを実施します。 **(完了)**
4.  `uv run pytest` を実行し、すべてのテストが成功することを確認します。 **(完了)**
5.  作業完了後、本計画書に結果を追記し、ファイル名を `DONE_improve-cli-error-handling.md` に変更してユーザーに完了報告を行います。

## 5. 影響範囲

- `src/xlsx_value_picker/cli.py`
- `src/xlsx_value_picker/exceptions.py`
- `src/xlsx_value_picker/excel_processor.py`
- `src/xlsx_value_picker/config_loader.py`
- 関連するテストコード (`test/test_cli_integration.py`, `test/test_excel_processor.py`, `test/test_config_loader.py` など)

## 6. リスク

- リファクタリングによるエラーハンドリングの意図しない変更（デグレード）。
    - 対策: エラー発生時のテストケースを拡充し、動作確認を徹底します。 **(完了)**
- 改善方針の選定が不適切で、逆に複雑化してしまう可能性。
    - 対策: 実装前に改善方針のメリット・デメリットを十分に比較検討します。 **(完了)**

## 7. 承認

承認済み (2025-04-20)

## 8. 作業ログ

*   2025-04-20:
    *   計画書承認。ファイル名を WIP に変更。
    *   現状分析実施。改善方針として、共通エラー処理関数、コンテキストマネージャ、独自例外クラスの導入を決定。
    *   `src/xlsx_value_picker/exceptions.py` を作成し、独自例外クラスを定義。
    *   `src/xlsx_value_picker/excel_processor.py` を修正し、`ExcelValueExtractor` をコンテキストマネージャに対応。
    *   `src/xlsx_value_picker/cli.py` をリファクタリングし、エラーハンドリングを改善。
    *   `test/test_cli_integration.py` を修正し、リファクタリング内容を反映。
    *   `uv run pytest` を実行。テストが複数失敗。
    *   `src/xlsx_value_picker/config_loader.py` の例外処理を修正。
    *   `test/test_excel_processor.py` を修正し、コンテキストマネージャ使用を反映。
    *   `test/test_config_loader.py` を修正し、例外処理の変更を反映。
    *   `uv run pytest` を再実行。テストが複数失敗。
    *   `src/xlsx_value_picker/config_loader.py` のデフォルトスキーマパス計算方法を修正。
    *   `test/test_config_loader.py` の Pydantic バリデーションエラーに関するアサーションを修正。
    *   `uv run pytest` を再実行。テストが複数失敗。原因は `test_cli_integration.py` のデフォルトスキーマパス解決問題と判明。
    *   ユーザー指示により、現状を作業計画に反映。
    # *   `test/test_cli_integration.py` のデフォルトスキーマに依存するテストケースに `--schema` オプションを明示的に追加。(削除)
    *   `src/xlsx_value_picker/cli.py` のエラーハンドリングを修正し、`ConfigLoader` 初期化時と `load_config` 呼び出し時のエラーを分離。# スキーマ読み込みエラーは常に致命的エラーとして扱うように変更。(スキーマ読み込み自体がなくなったため修正)
    *   `test/test_cli_integration.py` の `test_invalid_config`, `test_nonexistent_config`, `test_ignore_errors` のアサーションを `cli.py` の修正に合わせて更新。
    *   `uv run pytest` を再実行。すべてのテストが成功。

## 9. 作業結果

- `cli.py` のエラーハンドリングロジックが改善され、`ConfigLoader` の初期化エラーと設定ファイルの読み込み/検証エラーが明確に区別されるようになりました。
- `--ignore-errors` オプションの挙動がより一貫性のあるものになりました（スキーマエラーは無視されない）。
- 関連するテストケースが修正され、すべてのテストが成功することを確認しました。
- コードの可読性と保守性が向上しました。