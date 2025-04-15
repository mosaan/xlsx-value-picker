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
