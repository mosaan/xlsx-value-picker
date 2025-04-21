# 作業計画: Workspace Problems の解消 (Ruff 警告)

## 1. 目的

Ruff によって報告された警告（未使用のインポート、ファイル末尾の改行、インポートのソート/フォーマット、行長超過）を解消し、コードのスタイルと一貫性を改善する。

## 2. 対象ファイルと問題点

**Ruff 警告:**

*   `src/xlsx_value_picker/config_loader.py`
    *   L7: `pathlib.Path`: 未使用のインポート
    *   L8: `typing.ClassVar`: 未使用のインポート
*   `test/test_cli_validation.py`
    *   L414: ファイル末尾の改行欠落
*   `src/xlsx_value_picker/cli.py`
    *   L1: インポートブロックのソート/フォーマット未実施
    *   L21: 行長超過 (124 > 120)
*   `test/test_config_loader.py`
    *   L16: インポートブロックのソート/フォーマット未実施
*   `test/test_cli_basic.py`
    *   L343: ファイル末尾の改行欠落
*   `test/test_cli_errors.py`
    *   L294: ファイル末尾の改行欠落
*   `test/test_cli_options.py`
    *   L342: ファイル末尾の改行欠落

## 3. 作業方針

1.  **未使用のインポートの削除:**
    *   `imported but unused` 警告に対応します。対象のインポート文を削除します。
2.  **ファイル末尾の改行追加:**
    *   `No newline at end of file` 警告に対応します。対象ファイルの末尾に改行を追加します。
3.  **インポートブロックの整形:**
    *   `Import block is un-sorted or un-formatted` 警告に対応します。`ruff format <file_path>` コマンドを使用するか、手動でインポート文を標準的な順序（標準ライブラリ、サードパーティライブラリ、自作モジュール）に並べ替え、アルファベット順にソートします。
4.  **行長の調整:**
    *   `Line too long` 警告に対応します。対象の行を読みやすく、かつ指定された最大行長（通常は 120 文字）を超えないように、適切に分割またはリファクタリングします。文字列やリスト、関数の引数などを複数行に分割することを検討します。

## 4. 作業手順

1.  `uv run ruff check . --fix` コマンドを実行し、自動修正可能な警告を修正します。
2.  自動修正されなかった警告（特に `Line too long`）について、上記の「作業方針」に基づき手動で修正します。
3.  修正後、`uv run ruff check .` および `uv run ruff format . --check` を実行し、すべての Ruff 警告が解消されていることを確認します。
4.  `uv run pytest` を実行し、コードスタイルの変更によるリグレッションが発生していないことを確認します。

## 5. 成果物

*   Ruff 警告が解消されたソースコードおよびテストコード。
*   すべてのテストが成功する状態。