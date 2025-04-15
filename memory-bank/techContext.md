# techContext.md

## 使用技術
- Python 3.11 以降（想定）
- openpyxl（Excelファイル読み取り）
- PyYAML（設定ファイル読み取り）
- uv（パッケージ管理・仮想環境管理）

## 開発環境
- Windows（現状）
- コマンドライン実行

## 技術的制約・依存
- openpyxlはExcelで保存済みの計算値のみ取得可能
- uvによるパッケージ管理（`uv init`, `uv add`）
- 追加パッケージはpyproject.tomlで管理

## ツール利用パターン
- uv initで初期化、uv addでパッケージ追加
- main.pyに実装を集約

## テスト・開発用依存
- テストフレームワーク: pytest
- 開発用依存として `uv add pytest --dev` で導入
- 本番環境には含まれず、開発・CI用途でのみ利用
- テスト実行は `uv run pytest` で行う（仮想環境の有効化不要）
- テスト例: test_main.pyでget_excel_values関数の単体テストを実装
- `*N`記法のテストケース追加・自動化
