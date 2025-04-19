# 依存関係管理ガイドライン

このドキュメントでは、xlsx-value-pickerプロジェクトにおけるPythonの依存関係管理のルールについて説明します。

## 依存パッケージの定義

- プロジェクトの実行に必要な依存パッケージは `pyproject.toml` の `[project.dependencies]` セクションに定義します。
- 開発時にのみ必要な依存パッケージ（テストライブラリ、リンターなど）は `pyproject.toml` の `[project.optional-dependencies]` の `dev` グループなどに定義します。

```toml
# pyproject.toml の例

[project]
# ...
dependencies = [
    "click>=8.0",
    "openpyxl>=3.1",
    "jinja2>=3.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    # 他の開発用ツール
]
```

## バージョン固定

- 依存関係のバージョンは `uv` パッケージマネージャを使用して `uv.lock` ファイルに固定します。
- 依存関係を追加・更新した場合は、以下のコマンドを実行してロックファイルを更新してください。

```bash
# 依存関係をインストールし、ロックファイルを更新
uv pip install -e .[dev]
uv pip freeze > requirements.lock # uv.lock が自動更新されない場合の代替
# または uv sync を使う (uv のバージョンによる)
uv sync
```

*注意: `uv` のバージョンや設定によっては `uv pip install` や `uv sync` で `uv.lock` が自動的に更新される場合があります。プロジェクトの `uv` の設定を確認してください。*
