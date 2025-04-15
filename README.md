# xslx-value-picker

## ユーザーマニュアル

### 概要
このツールは、Excelファイルから指定したセルの値を抽出し、JSON形式で出力するコマンドラインツールです。設定ファイル（YAML）で取得対象を柔軟に指定できます。

### 使い方

1. **設定ファイルの準備**
   - 例: `config.yaml`
   - 記述例:
     ```yaml
     file: "sample.xlsx"
     values:
       - sheet: "Sheet1"
         cell: "B2"
         name: "total_price"
       - sheet: "Sheet2"
         cell: "C5"
         name: "user_count"
     ```

2. **コマンドの実行**
   - コマンド例:
     ```
     uv run python main.py --config config.yaml --output result.json
     ```
   - `--config` で設定ファイル、`--output` で出力ファイル名を指定します。

3. **出力例**
   ```json
   {
     "total_price": 12345,
     "user_count": 42
   }
   ```

### 注意事項
- Excelファイルは事前に保存し、計算済みの値を取得してください（関数セルも値として取得されます）。
- 設定ファイルの書式が正しいことを確認してください。

---

## 開発者向けガイド

### セットアップ

1. **uvのインストール**
   ```
   pip install uv
   ```

2. **依存パッケージのインストール**
   ```
   uv pip install -r pyproject.toml
   ```
   または
   ```
   uv add openpyxl pyyaml
   ```

3. **開発用依存（テスト）**
   ```
   uv add pytest --dev
   ```

### ビルド・実行

- 実装は `main.py` に集約されています。
- コマンド例:
  ```
  uv run python main.py --config config.yaml --output result.json
  ```

### テスト

- テストは `test_main.py` に記述されています。
- 実行方法:
  ```
  uv run pytest
  ```

### 技術スタック・注意点

- Python 3.11 以降
- openpyxl, PyYAML
- パッケージ管理: uv
- Windows環境で動作確認済み
