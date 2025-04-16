# xlsx-value-picker

## ユーザーマニュアル

### 概要
このツールは、Excelファイルから指定したセルの値を抽出し、JSON、YAML、またはJinja2テンプレートを使用した任意のテキスト形式で出力するコマンドラインツールです。設定ファイル（YAML）で取得対象を柔軟に指定できます。

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

2. **出力フォーマットの指定**
   - JSON, YAML, Jinja2テンプレートからフォーマットを選択できます。
   - 設定ファイル内で指定:
     ```yaml
     output:
       format: json  # json, yaml, jinja2 のいずれかを指定
     ```
   - Jinja2テンプレートを使う場合:
     ```yaml
     output:
       format: jinja2
       # 以下はどちらか一方を指定
       template: |  # テンプレートを直接指定
         # データ: {{ data.key1 }}
       template_file: "path/to/template.j2"  # テンプレートファイルを指定
     ```

3. **コマンドの実行**
   - コマンド例:
     ```
     uv run python main.py --config config.yaml --output result.json
     ```
     または（出力ファイルを指定しない場合、標準出力にJSONが出力されます）:
     ```
     uv run python main.py --config config.yaml
     ```
   - `--config` で設定ファイル、`--output` で出力ファイル名を指定します。
   - `--output`を省略すると標準出力に出力されます。
   - `--config`を省略した場合は、カレントディレクトリの`config.yaml`が自動的に使用されます。
   - **range指定時の空行（全列None）スキップについて**: デフォルトでは、rangeで指定した範囲内の「すべての列がNoneの行」は出力に含まれません。すべての列がNoneの行も出力したい場合は、`--include-empty-range-row`オプションを指定してください。

4. **出力例**
   ```json
   {
     "total_price": 12345,
     "user_count": 42
   }
   ```

### 注意事項
- Excelファイルは事前にExcelアプリで保存し、計算済みの値を取得してください。
- 特に関数セル（=SUM(...), =CONCAT(...) など）は、Excelで一度保存しないとopenpyxlでは値が取得できません（openpyxlの仕様）。
- 設定ファイルの書式が正しいことを確認してください。
- **range指定時の空行（全列None）スキップ仕様**: デフォルトでは、rangeで指定した範囲内の「すべての列がNoneの行」は出力に含まれません。必要に応じて`--include-empty-range-row`オプションで空行も出力できます。

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
output:
  format: json       # 出力形式を指定（json, yaml, jinja2）
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
output:
  format: json
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

## Jinja2テンプレート出力機能

### 概要
Excel値をJSON/YAMLだけでなく、Jinja2テンプレートを使って任意のテキスト形式（Markdown、HTML、CSVなど）で出力できます。

### 設定方法
設定ファイル（YAML）で以下のように指定します：

```yaml
output:
  format: jinja2
  # 以下はどちらか一方を指定
  template: |  # テンプレートを直接指定する場合
    # Excel Data Report
    
    ## 基本データ
    - 果物: {{ data.value1 }}
    - 別のシートの値: {{ data.value2 }}
  
  # または
  template_file: path/to/template.j2  # 外部テンプレートファイルを指定する場合
```

### テンプレート内でのデータ参照方法
- 抽出したExcelデータは `data` オブジェクトとして参照できます
- 例: `{{ data.sheet1_value }}`, `{% for item in data.table_data %}...{% endfor %}`

### 出力例（Markdown形式）

```markdown
# Excel Data Report

## 基本データ
- 果物: りんご
- 別のシートの値: バナナ
- 名前付きセル値: りんご

## テーブルデータ
| 商品ID | 商品名 | 点数 |
|--------|--------|------|
| 1 | みかん | 90 |
| 2 | ぶどう | 80 |
| 3 | もも | 70 |

## 範囲データ
- さくらんぼ to メロン
- いちご to パイナップル
- キウイ to マンゴー
```

### サンプルファイル
本プロジェクトの `test/generate_sample.py` を実行すると、以下のJinja2関連のサンプルファイルが生成されます：
- `sample_jinja2.yaml` - YAML内にテンプレートを直接記述するサンプル
- `sample_template.j2` - 外部テンプレートファイルのサンプル
- `sample_template_file.yaml` - 外部テンプレートファイルを参照する設定ファイルのサンプル

## 出力フォーマット指定について
- 出力フォーマット（json/yaml/jinja2）は設定ファイル（YAML）の`output.format`で指定します。
- 以前あったCLIの`--format`オプションは廃止されました。
- すべての出力形式の指定は設定ファイルで一元管理されます。

## インストール方法

### uv経由
```
uv pip install .
```

### pip経由
```
pip install .
```

## コマンド実行例

### CLIコマンド
```
xlsx-value-picker --config config.yaml --output result.json
```

### モジュール実行
```
python -m xlsx_value_picker --config config.yaml --output result.yaml
```

### Jinja2テンプレート出力の実行例
```
xlsx-value-picker --config sample_jinja2.yaml --output report.md
```

または外部テンプレートファイルを使用する場合：
```
xlsx-value-picker --config sample_template_file.yaml --output report.md
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
   uv add openpyxl pyyaml jinja2
   ```

3. **開発用依存（テスト）**
   ```
   uv add pytest --dev
   ```

### ビルド・実行

- 実装は `xlsx_value_picker` パッケージに集約されています。
- コマンド例:
  ```
  uv run python -m xlsx_value_picker --config config.yaml --output result.json
  ```

### テスト

- テストは `test_main.py` と `test_template.py` に記述されています。
- 実行方法:
  ```
  uv run pytest
  ```

### 技術スタック・注意点

- Python 3.12 以降
- openpyxl, PyYAML, Jinja2
- パッケージ管理: uv
- Windows環境で動作確認済み
