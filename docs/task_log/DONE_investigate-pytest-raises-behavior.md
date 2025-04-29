# pytest.raises 挙動調査 計画 (PLANNING)

## 1. 目的

`test_config_loader.py` において、`pytest.raises(ConfigLoadError)` が期待通りに例外を捕捉できない問題が発生している。この問題の原因を切り分けるため、既存のプロジェクトコードから独立した環境で `pytest.raises` の基本的な挙動を確認する。

## 2. 背景

`test_config_loader.py` の `test_parse_invalid_yaml` テストにおいて、`ConfigParser.parse_file` が `ConfigLoadError` を送出しているにも関わらず、`pytest.raises(ConfigLoadError)` で捕捉できない事象が発生している。`try...except` と `isinstance()` を用いたテストでは成功するため、`pytest.raises` の挙動自体に問題がある可能性、または特定の条件下でのみ問題が発生する可能性が考えられる。

## 3. 調査方針

1.  **独立したテストファイルの作成**: `test/test_pytest.py` という新規ファイルを作成する。(完了)
2.  **シンプルなテストケースの実装**: (完了)
    *   単純なカスタム例外クラス `MyTestError` を `test/test_pytest.py` 内に定義する。
    *   そのカスタム例外を送出する関数 `raise_my_error()` を `test/test_pytest.py` 内に定義する。
    *   `pytest.raises(MyTestError)` を使用して、`raise_my_error()` が期待通りに `MyTestError` を送出するかを検証するテストケース `test_pytest_raises_simple_case()` を作成する。
    *   `pytest.raises` が期待しない例外を捕捉しないことを確認するテストケース `test_pytest_raises_does_not_catch_wrong_exception()` を作成する。
    *   `pytest.raises` が例外メッセージを検証できることを確認するテストケース `test_pytest_raises_with_message_match()` を作成する。
3.  **テスト実行と結果確認**: 作成したテストを実行し、`pytest.raises` が基本的なケースで正しく動作するかを確認する。(完了)
4.  **追加テストケースの実装 (多段継承・例外ラップ)**: (完了)
    *   **多段継承**: `Exception` から複数レベル継承したカスタム例外クラス (`Level1Error`, `Level2Error`) を定義し、`pytest.raises(Level2Error)` で捕捉できるかテストする (`test_pytest_raises_multi_level_inheritance`)。
    *   **例外ラップ**: `raise MyTestError("...") from ValueError()` のように `from` 句でラップされた例外を `pytest.raises(MyTestError)` で捕捉できるかテストする (`test_pytest_raises_wrapped_exception`)。
5.  **追加テスト実行と結果確認 (多段継承・例外ラップ)**: 追加したテストケースを実行し、結果を確認する。(完了、すべて成功)
6.  **追加テストケースの実装 (インポートされた例外)**: 以下の仮説を検証するテストケースを `test/test_pytest.py` に追加する。
    *   **仮説**: `pytest.raises` が別モジュールからインポートされた例外クラスを正しく認識できない場合がある。
    *   **手順**:
        *   `test/helper_exceptions.py` ファイルを作成する。
        *   `test/helper_exceptions.py` 内に `ExternalError(Exception)` を定義する。
        *   `test/test_pytest.py` で `from test.helper_exceptions import ExternalError` を行う。
        *   `ExternalError` を送出する関数 `raise_external_error()` を定義する。
        *   `pytest.raises(ExternalError)` で捕捉できるかテストする (`test_pytest_raises_imported_exception`)。
7.  **追加テスト実行と結果確認 (インポートされた例外)**: 追加したテストケースを実行し、結果を確認する。

## 4. 期待される結果

*   `test/test_pytest.py` のテストが成功し、`pytest.raises` が基本的な例外捕捉機能を持つことが確認できる。
*   もしテストが失敗する場合、pytest のインストール環境やバージョンに問題がある可能性が示唆される。

## 5. 次のステップ

*   `test_pytest_raises_imported_exception` が成功した場合:
    *   `test_config_loader.py` での問題が、単純なインポートの問題ではない可能性が高い。
    *   `test_pytest.py` に `ConfigLoadError` や関連するモジュール (`src/xlsx_value_picker/exceptions.py`) を直接インポートし、`test_config_loader.py` の状況をさらに近づけて再現テストを行う。特に `sys.path` の操作の影響を調査する。
*   `test_pytest_raises_imported_exception` が失敗した場合:
    *   インポートされた例外クラスの扱いに `pytest.raises` の問題がある可能性が示唆される。
    *   pytest のドキュメントや Issue を調査し、関連情報がないか確認する。

## 6. 成果物

*   `test/test_pytest.py` ファイル
*   `test/helper_exceptions.py` ファイル
*   `test_pytest_raises_imported_exception` テストケース
*   本計画書 (`docs/task_log/PLANNING_investigate-pytest-raises-behavior.md`)
*   

## 7. 調査方針と結果

1.  **独立したテストファイルの作成**: `test/test_pytest.py` を作成。(完了)
2.  **シンプルなテストケースの実装**: `test/test_pytest.py` 内で定義した単純なカスタム例外 (`MyTestError`) を用いて、`pytest.raises` の基本的な例外捕捉、異なる例外の非捕捉、メッセージ検証機能を確認。(完了)
3.  **テスト実行と結果確認**: 上記テストケースを実行し、`pytest.raises` が基本的なケースで正しく動作することを確認。(完了、すべて成功)
4.  **追加テストケースの実装 (多段継承・例外ラップ)**: 多段継承された例外 (`Level2Error`) や `from` 句でラップされた例外 (`MyTestError from ValueError`) を `pytest.raises` で捕捉できるかテスト。(完了)
5.  **追加テスト実行と結果確認 (多段継承・例外ラップ)**: 上記テストケースを実行し、多段継承や例外ラップは問題なく扱えることを確認。(完了、すべて成功)
6.  **追加テストケースの実装 (インポートされた例外)**: 別のファイル (`test/helper_exceptions.py`) で定義した例外 (`ExternalError`) をインポートし、`pytest.raises` で捕捉できるかテスト。(完了)
7.  **追加テスト実行と結果確認 (インポートされた例外)**: 上記テストケースを実行し、別モジュールからインポートされた例外も問題なく捕捉できることを確認。(完了、成功)
8.  **追加テストケースの実装 (`sys.path` 操作の影響)**: `test/test_pytest.py` 内で `sys.path` を動的に変更し、その状態でインポートした例外 (`ExternalError`) を `pytest.raises` で捕捉できるかテスト。(完了)
9.  **追加テスト実行と結果確認 (`sys.path` 操作の影響)**: 上記テストケースを実行し、この独立した環境では `sys.path` 操作自体は `pytest.raises` の挙動に直接影響を与えないことを確認。(完了、成功)
10. **追加テストケースの実装 (モジュール二重ロードの影響)**: `sys.path` 操作によって同じモジュールが異なるパスからロードされ、クラスオブジェクトが不一致になる状況を `test/test_pytest.py` で再現しようと試みるテスト (`test_pytest_raises_fails_on_dual_load`) を作成。(完了)
11. **追加テスト実行と結果確認 (モジュール二重ロードの影響)**: 上記テストケースを実行。Python のモジュールキャッシュ機構により、このテスト環境では意図的なクラスオブジェクトの不一致を再現するには至らなかった。(完了、テスト自体は成功)
12. **`test_config_loader.py` での追加検証**: ユーザーにより、`test_config_loader.py` 内の `sys.path.insert(0, ...)` 行をコメントアウトすると、`pytest.raises(ConfigLoadError)` が期待通り動作するようになることを確認。(完了)

## 8. 結論

*   `pytest.raises` の基本的な機能（単純な例外、多段継承、例外ラップ、インポートされた例外の捕捉）自体には問題は見られない。
*   `test_config_loader.py` における `pytest.raises(ConfigLoadError)` の失敗は、テストファイル冒頭で行われている `sys.path.insert(0, ...)` による **`sys.path` の動的な操作が根本原因**である可能性が極めて高い。
*   この操作により、テスト実行時に `xlsx_value_picker.exceptions` モジュールが pytest によって認識されるパスと `sys.path` 操作によって追加されたパスのいずれか、あるいは双方から読み込まれ、結果としてテストコードが期待する `ConfigLoadError` クラスオブジェクトと、実際に `config_loader.py` から送出される `ConfigLoadError` クラスオブジェクトが、Python 内部で**異なるものとして扱われてしまう**（モジュールの二重ロードに類似した状況）ため、`pytest.raises` が一致を検出できずに失敗すると考えられる。

## 9. 推奨される解決策

`test_config_loader.py` から以下の行を削除する:
```python
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```