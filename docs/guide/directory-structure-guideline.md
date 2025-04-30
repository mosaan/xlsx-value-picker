# ディレクトリ構造ガイドライン

このドキュメントでは、xlsx-value-pickerプロジェクトにおけるディレクトリ構造の基本的な考え方とルールについて説明します。

## 基本的なディレクトリ構成と考え方

プロジェクトのルートディレクトリには、主要な設定ファイルやドキュメントの入り口が配置されます。主要なサブディレクトリの役割は以下の通りです。

- **`.github/`**: GitHub ActionsのワークフローやCopilotの設定など、GitHub関連の設定ファイルを格納します。
- **`docs/`**: プロジェクトに関するドキュメントを格納します。
    - **`design/`**: 設計に関するドキュメント（設定ローダー、バリデーションなど）を格納します。
    - **`guide/`**: 開発を進める上での各種ガイドライン（本ドキュメント、依存関係管理、バージョン管理など）を格納します。
    - **`project/`**: プロジェクト全体に関わるドキュメント（要件定義、技術選定、プロジェクトステータスなど）を格納します。
    - **`spec/`**: 仕様書（CLI仕様、ルールスキーマなど）を格納します。
    - **`task_log/`**: 特定のタスクに関する計画や記録を格納します。
- **`src/`**: プロジェクトのソースコードを格納します。
    - **`xlsx_value_picker/`**: メインとなるPythonパッケージです。内部の構造は機能に応じて適切に分割します。
- **`test/`**: テストコードとテスト関連ファイルを格納します。
    - **`data/`**: テストで使用するデータファイル（Excel、設定ファイルなど）を格納します。
- **`scripts/`**: 開発や運用を補助するスクリプト（リリーススクリプト、ドキュメント生成スクリプトなど）を格納します（必要に応じて作成）。
- **`examples/`**: プロジェクトの使用例を示す設定ファイルやテンプレートなどを格納します（必要に応じて作成）。

## 推奨するプロジェクト拡張時のディレクトリ構成

現在のプロジェクト構造を基盤とし、今後機能拡張を行う場合は、以下のようなディレクトリ構成を参考にしてください。

```
xlsx-value-picker/
├── .github/
├── docs/
│   ├── design/
│   ├── guide/
│   ├── project/
│   ├── spec/
│   └── task_log/
├── src/
│   └── xlsx_value_picker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config_loader.py
│       ├── excel_processor.py
│       ├── exceptions.py
│       ├── output_formatter.py
│       ├── validation.py
│       ├── validator/           # バリデーション機能
│       │   ├── __init__.py
│       │   ├── validation_common.py   # 共通クラス・関数
│       │   └── validation_expressions.py # 各種バリデーション式
│       ├── mcp_server/          # MCPサーバー機能
│       │   ├── __init__.py
│       │   ├── server.py        # サーバー起動・設定
│       │   ├── handlers.py      # リクエストハンドラー
│       │   └── protocol.py      # プロトコル定義
│       └── plugins/             # 例: プラグイン機能追加時（未実装）
│           └── __init__.py
├── test/
│   ├── __init__.py
│   ├── create_test_file.py
│   ├── generate_sample.py
│   ├── helper_exceptions.py
│   ├── sample_template.j2
│   ├── test_cli_basic.py
│   ├── test_cli_errors.py
│   ├── test_cli_integration.py
│   ├── test_cli_options.py
│   ├── test_cli_validation.py
│   ├── test_config_loader.py
│   ├── test_excel_processor.py
│   ├── test_mcp_server.py      # MCPサーバーのテスト
│   ├── test_output_formatter.py
│   ├── test_pathlib.py
│   ├── test_pytest.py
│   └── data/
│       ├── config.yaml
│       ├── sample_mcp_config.yaml  # MCPサーバーのテスト用設定
│       └── test.xlsx
├── examples/                    # 例: 使用例追加時（未実装）
│   ├── simple.yaml              # 基本的な使用例
│   ├── advanced.yaml            # 高度な設定例
│   ├── mcp.yaml                 # MCPサーバー設定例
│   └── template_examples/       # テンプレート例
├── scripts/                     # 例: 開発用スクリプト追加時（未実装）
│   ├── release.py               # リリース準備スクリプト
│   └── generate_docs.py         # ドキュメント生成
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
└── .python-version
```

## モジュールの役割

### コアモジュール

- **`__main__.py`**: エントリーポイント。`cli` 関数を呼び出します。
- **`cli.py`**: CLIコマンドの定義と実行。`run`と`server`サブコマンドを提供します。
- **`config_loader.py`**: 設定ファイル読み込み機能を提供します。
- **`excel_processor.py`**: Excelファイルからの値取得機能を提供します。
- **`output_formatter.py`**: 抽出したデータの出力機能を提供します。
- **`validation.py`**: バリデーションエンジンを提供します。
- **`exceptions.py`**: アプリケーション全体で使用する例外クラスを定義します。

### バリデーションモジュール (`validator/`)

- **`validation_common.py`**: バリデーションの共通クラスや関数を定義します。
- **`validation_expressions.py`**: 各種バリデーション式（compare, required, any_of, all_of, notなど）を定義します。

### MCPサーバーモジュール (`mcp_server/`)

- **`server.py`**: MCPサーバーの初期化、設定読み込み、サーバー起動処理を実装します。
- **`handlers.py`**: MCPプロトコルのリクエストに対するハンドラー関数を定義します。
- **`protocol.py`**: MCPプロトコルで使用するデータ構造（リクエスト・レスポンス）をPydanticモデルで定義します。

## ファイル命名規則

- Python モジュール名: スネークケース（例: `cli.py`, `server.py`）
- クラス名: パスカルケース（例: `ValueSpec`, `MCPConfig`）
- 関数・メソッド名: スネークケース（例: `get_excel_values`, `handle_list_models`）
- 定数: 大文字のスネークケース（例: `DEFAULT_FORMAT`, `MAX_ROWS`）
- テストファイル: `test_` プレフィックス + テスト対象のモジュール名（例: `test_mcp_server.py`, `test_cli_basic.py`）

## 設定ファイルの配置

- プロジェクトの標準設定ファイル（`config.yaml`）: プロジェクトルートに配置
- MCPサーバー設定ファイル（`mcp.yaml`）: プロジェクトルートに配置
- テスト用設定ファイル: `test/data/` ディレクトリに配置
- 設定ファイルの例: `examples/` ディレクトリに配置（予定）

---

最終更新日: 2025年4月30日
