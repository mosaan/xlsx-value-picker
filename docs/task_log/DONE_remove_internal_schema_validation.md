# 内部スキーマ検証の削除計画

## 目的

ツール内部で行われている `rule-schema.json` を利用した設定ファイルのスキーマ検証を削除し、Pydantic による検証のみに一本化する。スキーマファイルは外部ツール連携用として残す。

## 背景

現在、設定ファイルの検証は `rule-schema.json` による検証と Pydantic モデルによる検証の二箇所で行われており、冗長になっている。Pydantic による検証に一本化することで、コードの複雑さを低減し、メンテナンス性を向上させる。

## 作業手順

1.  **現状調査:**
    *   `rule-schema.json` ファイルの内容を確認する。
    *   関連する Pydantic モデル (`src/xlsx_value_picker/models.py` と推測) の内容を確認する。
    *   `rule-schema.json` を利用しているコード箇所 (`src/xlsx_value_picker/config_loader.py` と推測) を特定し、検証ロジックを確認する。
    *   CLI オプションでスキーマパスを指定する機能 (`--schema` オプションなど) が存在するか確認する。関連するコード (`src/xlsx_value_picker/cli.py` と推測) も確認する。
2.  **比較検討:**
    *   `rule-schema.json` の制約と Pydantic モデルの定義を比較し、Pydantic 側で検証がカバーされているか確認する。
    *   不足している制約があれば記録する (今回は Pydantic 側の修正は行わない)。
3.  **コード修正:**
    *   特定したコード箇所から、`jsonschema` ライブラリを用いたスキーマ検証ロジックを削除する。
    *   もしスキーマパスを指定する CLI オプションが存在する場合、そのオプションと関連する処理を削除または変更する (Pydantic 検証のみになるため、オプション自体が不要になる可能性が高い)。
4.  **テスト:**
    *   `pytest` を実行し、すべてのテストがパスすることを確認する。スキーマ検証や関連する CLI オプションに関するテストがあれば修正する。
5.  **ドキュメント更新:**
    *   プロジェクト内のドキュメント (`docs/` 配下、README.md など) を検索し、スキーマ検証や関連する CLI オプションに関する記述があれば修正または削除する。特に CLI の使い方に関するドキュメント (`docs/guide/` 配下など) を重点的に確認する。

## 影響範囲

*   `src/xlsx_value_picker/config_loader.py` (推測) の修正。
*   `src/xlsx_value_picker/cli.py` (推測) の修正 (CLI オプション関連)。
*   テストコードへの影響 (スキーマ検証エラーや CLI オプションを期待するテストがあれば修正が必要)。
*   ドキュメント (`docs/` 配下、`/README.md` など) の修正。

## 確認事項

*   Pydantic モデルでカバーしきれないスキーマ制約が存在しないか。 (存在する場合、その制約が必須かどうかを判断する必要がある)
*   スキーマパスを指定する CLI オプションの正確な仕様と、削除または変更した場合の影響。
## 作業結果

- `src/xlsx_value_picker/config_loader.py` から `jsonschema` ライブラリと `SchemaValidator` クラスを削除し、Pydantic モデル (`ConfigModel`) による検証のみに一本化しました。`ConfigLoader` の初期化処理と `load_config` メソッド内のスキーマ検証ステップも削除しました。
- `src/xlsx_value_picker/cli.py` から `--schema` オプションとその関連処理を削除しました。`ConfigLoader` の呼び出し箇所も修正しました。
- `test/test_config_loader.py` から `SchemaValidator` クラスに関連するテストケースとフィクスチャを削除しました。
- `test/test_cli_basic.py`, `test/test_cli_errors.py`, `test/test_cli_options.py`, `test/test_cli_validation.py` から `--schema` オプションを使用している箇所を削除しました。
- `README.md`, `docs/task_log/DONE_test-implementation-plan.md`, `docs/task_log/DONE_split_test_cli_integration.md`, `docs/task_log/DONE_readme_update.md`, `docs/task_log/DONE_improve-cli-error-handling.md`, `docs/design/config-loader-design.md` から、内部スキーマ検証や `--schema` オプションに関する記述を削除または修正しました。
- `pytest` を実行したところ、テスト環境の問題と思われる `ModuleNotFoundError: No module named 'click'` により一部テストが失敗しましたが、コードの修正自体は完了と判断しました。
- `uv run pytest` を実行し、すべてのテスト (117 passed) がパスすることを確認しました。