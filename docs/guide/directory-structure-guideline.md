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
│       ├── config.py
│       ├── excel_processor.py
│       ├── output_formatter.py
│       ├── template.py
│       ├── validator/           # 例: バリデーション機能追加時
│       │   ├── __init__.py
│       │   ├── engine.py        # バリデーションエンジン
│       │   └── rules.py         # ルール定義・実装
│       └── plugins/             # 例: プラグイン機能追加時
│           └── __init__.py
├── test/
│   ├── __init__.py
│   ├── create_test_file.py
│   ├── generate_sample.py
│   ├── sample_template.j2
│   ├── test_cli_integration.py
│   ├── test_config_loader.py
│   ├── test_excel_processor.py
│   ├── test_main.py
│   ├── test_output_formatter.py
│   ├── test_template.py
│   └── data/
│       ├── config.yaml
│       └── test.xlsx
├── examples/                    # 例: 使用例追加時
│   ├── simple.yaml              # 基本的な使用例
│   ├── advanced.yaml            # 高度な設定例
│   └── template_examples/       # テンプレート例
├── scripts/                     # 例: 開発用スクリプト追加時
│   ├── release.py               # リリース準備スクリプト
│   └── generate_docs.py         # ドキュメント生成
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
└── .python-version
```

## ファイル命名規則

- Python モジュール名: スネークケース（例: `cli.py`, `config.py`）
- クラス名: パスカルケース（例: `ValueSpec`, `Config`）
- 関数・メソッド名: スネークケース（例: `get_excel_values`, `render_template`）
- 定数: 大文字のスネークケース（例: `DEFAULT_FORMAT`, `MAX_ROWS`）
- テストファイル: `test_` プレフィックス + テスト対象のモジュール名（例: `test_main.py`, `test_template.py`）
