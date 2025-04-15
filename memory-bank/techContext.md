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

# Excelテーブル機能（ListObject）対応状況調査

## openpyxl
- Excelの「テーブル（ListObject）」を認識・操作する機能あり。
- テーブル名や範囲の取得、行データの抽出が可能（ただし一部制限あり）。

## pandas
- テーブル機能そのものは直接認識しない。
- 範囲指定やシート全体からDataFrameとして読み込むことは可能。
- openpyxl等と組み合わせればテーブル範囲の抽出も可能。

## xlrd
- 新しいExcel形式（.xlsx）のテーブル機能には非対応。

### 結論
- openpyxlを使えば「テーブル名指定」や「範囲指定」でのレコード抽出が実装可能。
- pandasは範囲指定でのデータ抽出が得意だが、テーブル名での直接抽出は不可。
