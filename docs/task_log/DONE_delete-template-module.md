```markdown
# `template.py` 削除計画

## 1. 目的

現在使用されていない `src/xlsx_value_picker/template.py` モジュールを削除し、コードベースを整理します。

## 2. 背景

`template.py` は Jinja2 テンプレートのレンダリング機能を提供していましたが、`output_formatter.py` 内で直接 Jinja2 ライブラリを使用するように変更されたため、不要になりました。

## 3. 作業計画

1.  **依存関係確認:** `src/xlsx_value_picker/` ディレクトリ全体で `template.py` モジュールが import されていないことを確認します (特に `output_formatter.py`)。
2.  **ファイル削除:** `src/xlsx_value_picker/template.py` ファイルを削除します。
3.  **テスト確認:** 関連するテスト (`test/test_output_formatter.py` など) が `template.py` に依存していないことを確認します。
4.  **テスト実行:** `uv run test` を実行し、すべてのテストが成功することを確認します。

## 4. 作業手順

1.  本計画書についてユーザーの承認を得ます。
2.  承認後、ファイル名を `WIP_delete-template-module.md` に変更します。
3.  上記「3. 作業計画」に従ってリファクタリングを実施します。
4.  テストを実行し、すべてのテストが成功することを確認します。
5.  作業完了後、本計画書に結果を追記し、ファイル名を `DONE_delete-template-module.md` に変更してユーザーに完了報告を行います。

## 5. 影響範囲

- `src/xlsx_value_picker/template.py` (削除)
- 関連するテストコード (確認のみ)

## 6. リスク

- 万が一、`template.py` がどこかで使用されていた場合、削除によってエラーが発生する。
    - 対策: 事前の依存関係確認を確実に行います。

## 7. 承認

ユーザー確認待ち。

## 8. 作業結果

1.  計画書を `WIP_delete-template-module.md` にリネームしました。
2.  `src/xlsx_value_picker/` ディレクトリ内で `template.py` の依存関係がないことを確認しました。
3.  `src/xlsx_value_picker/template.py` ファイルを削除しました。
4.  `test/test_output_formatter.py` が `template.py` に依存していないことを確認しました。
5.  `uv run pytest` を実行し、`test/test_template.py` が存在しない `template.py` を参照しているためエラーが発生することを確認しました。
6.  不要なテストファイル `test/test_template.py` を削除しました。
7.  再度 `uv run pytest` を実行し、すべてのテスト (97件) が成功することを確認しました。
8.  本計画書に結果を追記し、ファイル名を `DONE_delete-template-module.md` に変更しました。
```