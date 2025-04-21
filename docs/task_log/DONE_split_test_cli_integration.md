# test/test_cli_integration.py の分割計画

## 目的

`test/test_cli_integration.py` ファイルが長大化しているため、保守性と可読性の向上のために、1ファイルあたり約200行を目安にファイルを分割します。

## 作業手順

1.  **現状確認:** `test/test_cli_integration.py` の内容を確認し、含まれるテストケースの種類を把握します。
2.  **分割方針の決定:** テストケースを以下の論理的なグループに分割します。
    *   **基本機能:** 正常系のテスト (YAML/JSON設定、ファイル出力/標準出力)
    *   **エラーハンドリング:** 不正な入力やファイルに関するテスト (不正な設定、存在しないファイル)
    *   **オプション:** CLIオプションに関するテスト (`--include-empty-cells`, `--ignore-errors`) # --schema を削除
    *   **バリデーション:** バリデーション機能に関するテスト (成功、失敗、ログ出力、`--validate-only`, `--ignore-errors`との組み合わせ)
3.  **ファイル作成:** 上記のグループごとに新しいテストファイルを作成します。
    *   `test/test_cli_basic.py`
    *   `test/test_cli_errors.py`
    *   `test/test_cli_options.py`
    *   `test/test_cli_validation.py`
4.  **コードの移動:**
    *   各新しいテストファイルに必要な `import` 文、ヘルパー関数 (`create_test_excel`, `create_valid_config_yaml` など）、`TestCLI` クラスの定義、`setup_files` フィクスチャ、`run_cli_command` メソッドをコピーします。
    *   元の `test/test_cli_integration.py` から、各グループに対応するテストメソッド (`test_...`) を新しいファイルに移動します。
    *   元の `test/test_cli_integration.py` から移動したテストメソッドを削除します。ヘルパー関数や `setup_files` は、各ファイルで必要となるため残します。（共通化は別タスクとする）
5.  **行数調整:** 各ファイルの行数が約200行になるように調整します。必要であれば、さらにファイルを分割します。
6.  **テスト実行:** `pytest test` を実行し、すべてのテストが成功することを確認します。
7.  **完了:** 作業内容を文書に追記し、ファイル名を `DONE_split_test_cli_integration.md` に変更します。

## 注意点

*   各テストファイルが独立して実行可能であることを確認します。
*   ヘルパー関数やフィクスチャの重複が発生しますが、今回のタスクでは許容し、共通化は別途検討します。
## 作業結果

- `test/test_cli_integration.py` を以下の4つのファイルに分割しました。
    - `test/test_cli_basic.py` (基本機能テスト)
    - `test/test_cli_errors.py` (エラーハンドリングテスト)
    - `test/test_cli_options.py` (オプションテスト)
    - `test/test_cli_validation.py` (バリデーションテスト)
- 元の `test/test_cli_integration.py` には、共通のヘルパー関数とフィクスチャのみを残しました。
- `pytest test` を実行し、すべてのテスト (124件) が成功することを確認しました。