# xlsx-value-picker

## ユーザーマニュアル

### 概要
このツールは、Excelファイルから指定したセルの値を抽出し、バリデーション（検証）を行い、JSON、YAML、またはJinja2テンプレートを使用した任意のテキスト形式で出力するコマンドラインツールです。設定ファイル（YAML）で取得対象や検証ルールを柔軟に指定できます。

### インストール方法

#### uvを使用する場合（推奨）
```bash
# uvのインストール（初回のみ）
pip install uv

# xlsx-value-pickerのインストール
uv pip install .
```

#### pipを使用する場合
```bash
pip install .
```

### 使い方

#### 基本的なコマンド構文
```bash
xlsx-value-picker [オプション] <Excelファイル>
```

#### 主なオプション
- `-c`, `--config <設定ファイル>`: 検証ルールや設定を記述した設定ファイル（YAML形式）を指定します。デフォルトは`config.yaml`です。
- `-o`, `--output <出力ファイル>`: データの出力先ファイルを指定します。省略した場合は標準出力に表示します。
- `--log <ログファイル>`: 検証エラーを記録するログファイルを指定します。
- `--ignore-errors`: 検証エラーが発生しても処理を継続します。
- `--validate-only`: バリデーションのみを実行し、値の抽出や出力は行いません。
# --schema オプションは削除
- `--include-empty-cells`: 空セルも出力に含めます。
- `--help`: ヘルプ情報を表示します。
- `--version`: ツールのバージョンを表示します。

#### 設定ファイルの基本構造
設定ファイル（YAML）では以下の項目を定義できます：

```yaml
# フィールド定義（必須）- セル位置とフィールド名のマッピング
fields:
  field_name1: "Sheet1!A1"
  field_name2: "Sheet1!B2"

# バリデーションルール（オプション）
rules:
  - name: "必須項目チェック"
    expression:
      field: "field_name1"
      required: true
    error_message: "{field}は必須項目です"

  - name: "値の範囲チェック"
    expression:
      compare:
        left: "field_name2"
        operator: ">"
        right: 0
    error_message: "{field}は0より大きい値を入力してください"

# 出力形式設定（オプション、デフォルトはJSON）
output:
  format: "json"  # "json", "yaml", "jinja2" のいずれか
  # Jinja2の場合はテンプレートも指定
  # template_file: "template.j2"  # または template: "..."
```

### バリデーション機能

xlsx-value-pickerには強力なバリデーション機能が組み込まれています。以下のタイプのルールを設定できます：

#### 1. 単一フィールドの検証
- **必須項目チェック**：`required`
  ```yaml
  expression:
    field: "user_name"
    required: true
  ```

- **値の比較**：`compare`
  ```yaml
  expression:
    compare:
      left: "quantity"
      operator: ">"  # "==", "!=", ">", ">=", "<", "<="
      right: 0
  ```

- **正規表現マッチ**：`regex_match`
  ```yaml
  expression:
    regex_match:
      field: "email"
      pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"
  ```

- **列挙値チェック**：`enum`
  ```yaml
  expression:
    enum:
      field: "category"
      values: ["A", "B", "C"]
  ```

#### 2. 複合ルール
- **すべての条件を満たす**：`all_of`
  ```yaml
  expression:
    all_of:
      - field: "user_name"
        required: true
      - compare:
          left: "age"
          operator: ">="
          right: 18
  ```

- **いずれかの条件を満たす**：`any_of`
  ```yaml
  expression:
    any_of:
      - compare:
          left: "payment_method"
          operator: "=="
          right: "銀行振込"
      - compare:
          left: "payment_method"
          operator: "=="
          right: "クレジットカード"
  ```

- **条件の否定**：`not`
  ```yaml
  expression:
    not:
      compare:
        left: "status"
        operator: "=="
        right: "完了"
  ```

### 出力機能

#### 1. JSON形式
デフォルトの出力形式です。きれいに整形されたJSON形式で出力されます。

```yaml
output:
  format: "json"
```

#### 2. YAML形式
読みやすいYAML形式で出力できます。

```yaml
output:
  format: "yaml"
```

#### 3. Jinja2テンプレート形式
任意のテキスト形式（Markdown、HTML、CSVなど）で出力できます。

```yaml
output:
  format: "jinja2"
  # 以下のいずれか一方を指定
  template: |
    # データレポート
    
    - 項目1: {{ data.field_name1 }}
    - 項目2: {{ data.field_name2 }}
  
  # または
  template_file: "path/to/template.j2"
```

テンプレート内では、抽出したデータは `data` オブジェクトとして参照できます。

### 設定ファイル例

以下は、完全な設定ファイルの例です：

```yaml
# フィールド定義
fields:
  product_name: "Sheet1!A1"
  price: "Sheet1!B1"
  stock: "Sheet1!C1"
  email: "Sheet1!D1"
  category: "Sheet1!E1"

# バリデーションルール
rules:
  - name: "商品名必須チェック"
    expression:
      field: "product_name"
      required: true
    error_message: "商品名は必須項目です"

  - name: "価格範囲チェック"
    expression:
      compare:
        left: "price"
        operator: ">"
        right: 0
    error_message: "価格は0より大きい値を入力してください"

  - name: "在庫数チェック"
    expression:
      compare:
        left: "stock"
        operator: ">="
        right: 0
    error_message: "在庫数は0以上の値を入力してください"

  - name: "メールアドレスチェック"
    expression:
      regex_match:
        field: "email"
        pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"
    error_message: "メールアドレスの形式が正しくありません"

  - name: "カテゴリチェック"
    expression:
      enum:
        field: "category"
        values: ["A", "B", "C"]
    error_message: "カテゴリは A, B, C のいずれかを指定してください"

# 出力形式設定
output:
  format: "json"
```

### コマンド実行例

#### 基本的な実行
```bash
xlsx-value-picker -c config.yaml input.xlsx
```

#### 出力ファイルを指定して実行
```bash
xlsx-value-picker -c config.yaml -o result.json input.xlsx
```

#### バリデーションのみを実行
```bash
xlsx-value-picker -c config.yaml --validate-only input.xlsx
```

#### バリデーションエラーを無視して処理を継続
```bash
xlsx-value-picker -c config.yaml --ignore-errors input.xlsx
```

#### バリデーション結果をログファイルに出力
```bash
xlsx-value-picker -c config.yaml --log validation.log input.xlsx
```

#### 空セルも含めて出力
```bash
xlsx-value-picker -c config.yaml --include-empty-cells input.xlsx
```

#### YAML形式で出力
```bash
xlsx-value-picker -c config_yaml_output.yaml -o result.yaml input.xlsx
```

#### Jinja2テンプレートを使用して出力
```bash
xlsx-value-picker -c config_jinja2.yaml -o report.md input.xlsx
```

### 注意事項
- Excelファイルは事前にExcelアプリで保存し、計算済みの値を取得してください。
- 特に関数セル（=SUM(...), =CONCAT(...) など）は、Excelで一度保存しないとopenpyxlでは値が取得できません（openpyxlの仕様）。
- 設定ファイルの書式が正しいことを確認してください。

---

## 開発者向けガイド

詳細な開発ガイドライン、プロジェクトの設計、仕様については `docs/` ディレクトリ、特に [`docs/README.md`](docs/README.md) を参照してください。

### セットアップ

1. **uvのインストール**
   ```bash
   pip install uv
   ```

2. **依存パッケージのインストール**
   プロジェクトルートで以下のコマンドを実行し、必要な依存関係をインストールします。
   ```bash
   # 開発用依存を含むすべての依存関係をインストール・同期
   uv sync --all-extras
   ```

### テスト

- テストは `test/` ディレクトリに配置されています。
- 実行方法:
  ```bash
  uv run pytest
  ```

### 技術スタック

- Python 3.12 以降
- openpyxl, PyYAML, Jinja2, Click, Pydantic
- パッケージ管理: uv
- Windows環境で動作確認済み
