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
       - sheet: "Sheet1"   # シート名で指定
         cell: "B2"
         name: "total_price"
       - sheet: "*2"       # 左から2番目のシートを指定
         cell: "C5"
         name: "user_count"
       - named_cell: "MY_CELL" # 名前付きセルで指定
         name: "foo"
     ```
   - `sheet`に`*N`（例: `*2`）と指定すると、左からN番目（1始まり）のシートを選択できます。
   - `named_cell`を指定した場合は、Excelの名前付きセルから値を取得します（`sheet`や`cell`は不要）。
   - シート名に`*`はExcelの仕様上使えないため、この記法と競合しません。

2. **コマンドの実行**
   - コマンド例:
     ```
     uv run python main.py --config config.yaml --output result.json
     ```
     または（出力ファイルを指定しない場合、標準出力にJSONが出力されます）:
     ```
     uv run python main.py --config config.yaml
     ```
   - `--config` で設定ファイル、`--output` で出力ファイル名を指定します。`--output`を省略すると標準出力に出力されます。

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

## 設定ファイル例

```yaml
excel_file: sample_all.xlsx
values:
  # シート名で指定し、A1セルの値をvalue1として取得
  - sheet: Sheet1
    cell: A1
    name: value1
  # 左から2番目のシート（Sheet2）を指定し、B2セルの値をvalue2として取得
  - sheet: "*2"
    cell: B2
    name: value2
  # 名前付きセル（MY_CELL、Sheet1!A1）をnamedとして取得
  - named_cell: MY_CELL
    name: named
  # TableSheet上のTable1テーブルから、列名→出力キー名でマッピングして複数行をtable_dataとして取得
  - table: Table1
    columns:
      商品ID: id      # 商品ID列→id
      商品名: name    # 商品名列→name
      点数: score    # 点数列→score
    name: table_data
  # RangeSheetのA2:C4範囲（ヘッダ行除く）から、1列目→a、3列目→cとして複数行をrange_dataとして取得
  - range: RangeSheet!A2:C4
    columns:
      1: a           # 左端の列（A列）→a
      3: c           # 3番目の列（C列）→c
    name: range_data
```

## サンプルデータ内容
- Sheet1: A1=りんご
- Sheet2: B2=バナナ
- 名前付きセル: Sheet1!A1（りんご）
- TableSheet: 商品ID/商品名/点数（みかん/ぶどう/もも等、日本語）
- RangeSheet: さくらんぼ/すいか/メロン など日本語果物名

## 出力例（JSON）

```json
{
  "value1": "りんご",
  "value2": "バナナ",
  "named": "りんご",
  "table_data": [
    {"id": 1, "name": "みかん", "score": 90},
    {"id": 2, "name": "ぶどう", "score": 80},
    {"id": 3, "name": "もも", "score": 70}
  ],
  "range_data": [
    {"a": "さくらんぼ", "c": "メロン"},
    {"a": "いちご", "c": "パイナップル"},
    {"a": "キウイ", "c": "マンゴー"}
  ]
}
```

## テーブル・範囲指定による複数レコード抽出の例

### 設定ファイル例（YAML）

```yaml
excel_file: sample.xlsx
values:
  - table: Table1
    columns:
      ID: id
      Score: score
    name: table_data
  - range: Sheet1!A2:C4
    columns:
      1: a
      3: c
    name: range_data
```

### 出力例（JSON）

```json
{
  "table_data": [
    {"id": 1, "score": 90},
    {"id": 2, "score": 80},
    {"id": 3, "score": 70}
  ],
  "range_data": [
    {"a": 10, "c": 30},
    {"a": 11, "c": 31},
    {"a": 12, "c": 32}
  ]
}
```

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
  または
  ```
  uv run python main.py --config config.yaml
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
