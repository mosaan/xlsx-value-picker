# 依存関係管理ガイドライン

このドキュメントでは、xlsx-value-pickerプロジェクトにおけるPythonの依存関係管理のルールについて説明します。

## 依存パッケージの定義

- プロジェクトの実行に必要な依存パッケージは `pyproject.toml` の `[project.dependencies]` セクションに定義します。
- 開発時にのみ必要な依存パッケージ（テストライブラリ、リンターなど）は `pyproject.toml` の `[dependency-groups]` セクションの `dev` グループなどに定義します。
- ただし、直接`pyproject.toml`を編集して依存関係を追加することは作業ミスにつながる恐れが高いです。そのため、依存関係の追加や更新は `uv` パッケージマネージャを使用して行います。
  - `uv` を使用して依存関係を追加する場合、次のコマンドを実行します: `uv add <package-name>`。開発環境のみで使用するパッケージの場合は、`--dev` オプションを追加します。
```toml
# pyproject.toml の例

[project]
# ...
dependencies = [
    "click>=8.0",
    "openpyxl>=3.1",
    "jinja2>=3.0",
    "pyyaml>=6.0",
    # ... 他の実行時依存
]

# [project.optional-dependencies] ではなく [dependency-groups] を使用
[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    "mypy>=1.0",
    # 他の開発用ツール
]
```

## バージョン固定

- 依存関係のバージョンは `uv` パッケージマネージャを使用して `uv.lock` ファイルに固定します。
- 依存関係を追加・更新した場合は、以下のコマンドを実行して環境を同期し、ロックファイルを更新してください。

```bash
# 開発環境を含むすべての依存関係を同期 (uv.lock が更新される)
uv sync --all-extras
```

*注意: `uv sync` コマンドは `pyproject.toml` と `uv.lock` を基に現在の仮想環境に必要なパッケージをインストール・アンインストールします。依存関係を変更した際は、このコマンドで環境とロックファイルを最新の状態に保ってください。*
