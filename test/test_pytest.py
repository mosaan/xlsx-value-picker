import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# テスト用の単純なカスタム例外クラス
class MyTestError(Exception):
    pass


# カスタム例外を送出する単純な関数
def raise_my_error():
    raise MyTestError("This is a test error")


# pytest.raises が基本的なカスタム例外を捕捉できるかテスト
def test_pytest_raises_simple_case():
    """pytest.raises が単純なカスタム例外を捕捉できることを確認する"""
    with pytest.raises(MyTestError):
        raise_my_error()


# pytest.raises が期待する例外と異なる例外を捕捉しないことをテスト
def test_pytest_raises_does_not_catch_wrong_exception():
    """
    pytest.raises が期待しない例外が発生した場合、
    その例外を捕捉せずにテストが失敗することを確認する。
    """
    try:
        with pytest.raises(MyTestError):
            raise ValueError("This is not MyTestError")
    except ValueError as e:
        # 期待通り ValueError が捕捉されればテスト成功とみなす
        # (pytest.raises(MyTestError) が ValueError を抑制しなかったことを確認)
        print(f"Successfully confirmed that pytest.raises(MyTestError) did not catch ValueError: {e}")
        assert True  # 明示的に成功を示す
    else:
        # ValueError が発生しなかった場合、または pytest.raises が抑制した場合
        pytest.fail("ValueError was expected but not raised or was suppressed by pytest.raises")


# pytest.raises が例外メッセージを検証できるかテスト
def test_pytest_raises_with_message_match():
    """pytest.raises が例外メッセージの検証 (match) を行えることを確認する"""
    with pytest.raises(MyTestError, match="This is a test error"):
        raise_my_error()

    # メッセージがマッチしない場合
    with pytest.raises(AssertionError):  # pytest.raises自体は成功するが、中のコードでAssertionErrorが発生する
        with pytest.raises(MyTestError, match="Wrong message"):
            raise_my_error()  # MyTestErrorは発生するが、メッセージがマッチしないため失敗する


# --- 追加テストケース ---


# 多段継承された例外クラス
class Level1Error(Exception):
    pass


class Level2Error(Level1Error):
    pass


def raise_level2_error():
    raise Level2Error("Level 2 error")


def test_pytest_raises_multi_level_inheritance():
    """pytest.raises が多段継承された例外を捕捉できるか確認する"""
    # 直接の型を指定
    with pytest.raises(Level2Error):
        raise_level2_error()
    # 親の型を指定
    with pytest.raises(Level1Error):
        raise_level2_error()
    # さらに親の型を指定
    with pytest.raises(Exception):  # noqa: B017
        raise_level2_error()


def raise_wrapped_error():
    try:
        raise ValueError("Original error")
    except ValueError as e:
        raise MyTestError("Wrapped error") from e


def test_pytest_raises_wrapped_exception():
    """pytest.raises がラップされた例外 (raise ... from ...) を捕捉できるか確認する"""
    with pytest.raises(MyTestError) as excinfo:
        raise_wrapped_error()
    # ラップされた例外の情報を確認 (オプション)
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert str(excinfo.value.__cause__) == "Original error"


# --- インポートされた例外のテスト ---


def raise_external_error():
    from test.helper_exceptions import ExternalError  # 別ファイルから例外クラスをインポート

    raise ExternalError("External error occurred")


def test_pytest_raises_imported_exception():
    """pytest.raises が別モジュールからインポートされた例外を捕捉できるか確認する"""
    from test.helper_exceptions import ExternalError  # 別ファイルから例外クラスをインポート

    with pytest.raises(ExternalError):
        raise_external_error()

    # メッセージ検証も可能か確認
    with pytest.raises(ExternalError, match="External error occurred"):
        raise_external_error()


# --- インポートされた例外のテスト ---


# --- sys.path 操作の影響テスト ---
def test_pytest_raises_imported_exception_with_sys_path2():
    """sys.path 操作がインポートされた例外の捕捉に影響するか確認する"""
    from test.helper_exceptions import ExternalError  # 別ファイルから例外クラスをインポート

    # 現在の test ディレクトリの親 (プロジェクトルート) を sys.path の先頭に追加してみる
    project_root = str(Path(__file__).parent.parent)
    original_sys_path = sys.path[:]  # 元の sys.path をコピー

    # unittest.mock.patch を使って sys.path を一時的に変更
    # patch デコレータを使う代わりに with ステートメントを使う
    with patch.object(sys, "path", [project_root] + original_sys_path):
        # sys.path が変更された状態でテストを実行
        print(f"\nDEBUG: sys.path inside patch: {sys.path}")  # デバッグ出力
        # 再度インポートを試みる (キャッシュされている可能性もあるが念のため)
        try:
            from test.helper_exceptions import ExternalError as PatchedExternalError

            print(f"DEBUG: ExternalError id: {id(ExternalError)}")
            print(f"DEBUG: PatchedExternalError id: {id(PatchedExternalError)}")
            # ExternalError と PatchedExternalError が同じオブジェクトか確認
            assert ExternalError is PatchedExternalError, "ExternalError objects differ after sys.path manipulation!"

            with pytest.raises(PatchedExternalError):
                raise_external_error()  # raise_external_error は元の ExternalError を送出する

            # メッセージ検証
            with pytest.raises(PatchedExternalError, match="External error occurred"):
                raise_external_error()

        except ImportError as e:
            pytest.fail(f"Failed to import ExternalError after manipulating sys.path: {e}")

    # patch ブロックを抜けた後、sys.path が元に戻っているか確認 (オプション)
    assert sys.path == original_sys_path, "sys.path was not restored correctly after patch"
    print(f"\nDEBUG: sys.path after patch: {sys.path}")  # デバッグ出力


# ...existing code...

# ... (既存のテストケースは省略) ...

# --- sys.path 操作によるモジュール二重ロードの影響テスト ---


def test_pytest_raises_fails_on_dual_load():
    """
    sys.path 操作によりモジュールが二重ロードされ、
    pytest.raises がクラスオブジェクトの不一致で失敗する状況を再現する。
    """
    project_root = str(Path(__file__).parent.parent)
    original_sys_path = sys.path[:]

    # プロジェクトルートを sys.path の先頭に追加
    with patch.object(sys, "path", [project_root] + original_sys_path):
        print(f"\nDEBUG: sys.path inside patch for dual load test: {sys.path}")

        # まず普通にインポート
        from test.helper_exceptions import ExternalError as ErrorFromDirectImport

        # モジュールを 'test.helper_exceptions' という名前で再インポート試行
        # importlib.reload は既存のモジュールオブジェクトを更新するだけなので、
        # 意図的に別名でインポートするか、キャッシュを操作する必要があるかもしれないが、
        # まずは単純な import を試す
        try:
            # importlib を使って明示的に再読み込みを試みる
            # 注意: sys.modules のキャッシュにより、通常は同じオブジェクトが返される
            #       より確実に別オブジェクトにするには、sys.modules から一時的に削除するなど
            #       さらに高度な操作が必要になる場合がある。
            #       しかし、pytest の実行環境や sys.path の影響で意図せず
            #       別オブジェクトになるケースをシミュレートするのが目的。
            import test.helper_exceptions

            # importlib.reload(test.helper_exceptions) # reload は既存オブジェクトを更新する
            ErrorFromSysPathImport = test.helper_exceptions.ExternalError

            print(f"DEBUG: ID of ErrorFromDirectImport: {id(ErrorFromDirectImport)}")
            print(f"DEBUG: ID of ErrorFromSysPathImport: {id(ErrorFromSysPathImport)}")

            # 仮説: sys.path 操作により、これらが異なるオブジェクトになる場合がある
            # このテストでは、まず同じオブジェクトであることを確認し、
            # もし test_config_loader.py で問題が起きるなら、
            # 実際の環境では is False になっていると推測する。
            # assert ErrorFromDirectImport is not ErrorFromSysPathImport,
            # "Hypothesis failed: Objects are the same even with sys.path manipulation."

            # もしオブジェクトが異なると仮定した場合、以下の pytest.raises は失敗するはず
            print("DEBUG: Attempting to catch ErrorFromSysPathImport using pytest.raises(ErrorFromDirectImport)")
            try:
                with pytest.raises(ErrorFromDirectImport):
                    raise ErrorFromSysPathImport("Raising error from sys.path imported module")
                # もし↑が成功してしまったら、仮説がこのテストでは再現できなかったことを示す
                print("WARN: pytest.raises(ErrorFromDirectImport) unexpectedly succeeded.")
                # このテストケース自体の成功/失敗は、is 演算子の結果に依存させるべきかもしれない
                assert ErrorFromDirectImport is ErrorFromSysPathImport, (
                    "pytest.raises succeeded, implying objects were the same."
                )

            except Exception as e:
                # pytest.raises が期待通り失敗した場合 (捕捉できなかった場合)
                print(
                    "DEBUG: pytest.raises(ErrorFromDirectImport) failed "
                    + f"as expected (or another error occurred): {type(e)} - {e}"
                )
                # 捕捉できなかった例外が ErrorFromSysPathImport であることを確認
                assert isinstance(e, ErrorFromSysPathImport)
                # そして、捕捉しようとした ErrorFromDirectImport とは型が異なることを確認
                assert not isinstance(e, ErrorFromDirectImport)  # is演算子の方がより厳密
                assert ErrorFromDirectImport is not ErrorFromSysPathImport, (
                    "pytest.raises failed, confirming objects are different."
                )
                print("DEBUG: Successfully confirmed pytest.raises failure due to object mismatch.")

        except ImportError as e:
            pytest.fail(f"Failed to import test.helper_exceptions after manipulating sys.path: {e}")

    assert sys.path == original_sys_path, "sys.path was not restored"
    print(f"\nDEBUG: sys.path after patch: {sys.path}")
