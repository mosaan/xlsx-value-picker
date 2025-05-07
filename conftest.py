import pytest


# 非同期テストを行う際に(asynioを使わず)trioのみを使用するための設定
# この指定がないと、pytestがasyncioとtrio両方(厳密にはすべての対応したもの)を使用しようとする
@pytest.fixture
def anyio_backend() -> str:
    return "trio"
