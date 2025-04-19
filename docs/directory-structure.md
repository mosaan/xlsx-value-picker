# xlsx-value-picker プロジェクトのディレクトリ構成

このドキュメントでは、xlsx-value-pickerプロジェクトのディレクトリ構造および各ファイルの役割について説明します。

## ディレクトリ構造概要

```
xlsx-value-picker/
├── .github/                  # GitHub関連設定
│   ├── workflows/            # GitHub Actions
│   │   └── test.yml          # テスト自動化設定
│   └── copilot-instructions.md  # GitHub Copilot用指示
├── docs/                     # ドキュメント
│   ├── cli-spec.md           # CLIインターフェース仕様
│   ├── requirements.md       # 要件定義
│   ├── rule-schema.json      # ルール検証用JSONスキーマ
│   ├── technology-selection.md  # 技術選定ドキュメント
│   └── directory-structure.md  # 本ドキュメント（ディレクトリ構造）
├── src/                      # ソースコード
│   └── xlsx_value_picker/    # メインパッケージ
│       ├── __init__.py       # パッケージ初期化、エクスポート定義
│       ├── __main__.py       # エントリーポイント
│       ├── cli.py            # CLIインターフェース実装
│       ├── config.py         # 設定ファイル処理
│       └── template.py       # Jinja2テンプレート処理
├── test/                     # テストコード
│   ├── generate_sample.py    # サンプルファイル生成
│   ├── sample_template.j2    # テスト用Jinja2テンプレート
│   ├── test_main.py          # メインロジックのテスト
│   └── test_template.py      # テンプレート機能のテスト
├── LICENSE                   # ライセンスファイル（MIT）
├── README.md                 # プロジェクト説明・使用方法
├── pyproject.toml            # プロジェクト設定・依存関係
├── uv.lock                   # uvによる依存関係ロックファイル
└── .python-version           # Python使用バージョン指定
```

## 各ディレクトリとファイルの説明

### ルートディレクトリ

- **LICENSE**: MITライセンスファイル
- **README.md**: プロジェクトの説明書。インストール方法、使い方、設定例などを記載
- **pyproject.toml**: プロジェクトのメタデータや依存パッケージの定義
- **uv.lock**: uvパッケージマネージャによる依存関係の固定ファイル
- **.python-version**: 使用するPythonバージョン（3.12）の指定
- **.gitignore**: Gitによるバージョン管理から除外するファイルやディレクトリの指定

### .github/

GitHub関連の設定ファイルを格納するディレクトリ。

- **workflows/test.yml**: GitHub Actionsによる自動テスト設定
- **copilot-instructions.md**: GitHub Copilotに対する日本語での応答指示

### docs/

プロジェクトのドキュメントを格納するディレクトリ。

- **cli-spec.md**: CLIインターフェースの仕様
- **requirements.md**: 要件定義書
- **rule-schema.json**: バリデーションルール記述のJSONスキーマ
- **technology-selection.md**: 採用した技術と選定理由
- **directory-structure.md**: ディレクトリ構造の説明（本ドキュメント）

### src/

ソースコードを格納するディレクトリ。

- **xlsx_value_picker/**: メインパッケージ
  - **\_\_init\_\_.py**: パッケージ初期化ファイル、公開APIの定義
  - **\_\_main\_\_.py**: モジュールとして実行する際のエントリーポイント
  - **cli.py**: コマンドラインインターフェース実装
  - **config.py**: 設定ファイル読み込み・解析機能
  - **template.py**: Jinja2テンプレートレンダリング機能

### test/

テストコードとテストデータを格納するディレクトリ。

- **generate_sample.py**: テスト用サンプルExcelファイル生成スクリプト
- **sample_template.j2**: テスト用のJinja2テンプレート
- **test_main.py**: メイン機能のテスト
- **test_template.py**: テンプレート機能のテスト

## 推奨するプロジェクト拡張時のディレクトリ構成

今後機能拡張を行う場合に備えて、以下のようなディレクトリ構成を推奨します：

```
xlsx-value-picker/
├── ...（既存のディレクトリ）
├── src/
│   └── xlsx_value_picker/
│       ├── ...（既存のファイル）
│       ├── validator/           # バリデーション機能追加時
│       │   ├── __init__.py
│       │   ├── engine.py        # バリデーションエンジン
│       │   └── rules.py         # ルール定義・実装
│       └── plugins/             # プラグイン機能追加時
│           └── __init__.py
├── examples/                    # 使用例
│   ├── simple.yaml              # 基本的な使用例
│   ├── advanced.yaml            # 高度な設定例
│   └── template_examples/       # テンプレート例
├── docs/
│   ├── ...（既存のファイル）
│   ├── api/                     # API仕様書
│   └── examples/                # 例と使い方の詳細説明
└── scripts/                     # 開発用スクリプト
    ├── release.py               # リリース準備スクリプト
    └── generate_docs.py         # ドキュメント生成
```

## ファイル命名規則

- Python モジュール名: スネークケース（例: `cli.py`, `config.py`）
- クラス名: パスカルケース（例: `ValueSpec`, `Config`）
- 関数・メソッド名: スネークケース（例: `get_excel_values`, `render_template`）
- 定数: 大文字のスネークケース（例: `DEFAULT_FORMAT`, `MAX_ROWS`）
- テストファイル: `test_` プレフィックス + テスト対象のモジュール名（例: `test_main.py`, `test_template.py`）

## バージョン管理方針

- メインコードは `main` ブランチで管理
- 新機能開発は `feature/機能名` ブランチで実施
- バグ修正は `fix/問題の概要` ブランチで実施
- リリースタグは `v1.0.0` のようにセマンティックバージョニングに従う

## 依存関係管理

- 依存パッケージは `pyproject.toml` で管理
- 開発用依存は `pyproject.toml` の `dependency-groups` の `dev` セクションに記載
- バージョン固定は `uv.lock` ファイルで管理