# Excel検証およびJSON出力ツールのCLIインターフェース仕様

## コマンド構造

### 基本コマンド
```
excel-validator [オプション] <入力ファイル>
```

### オプション

#### 入力オプション
- `-c`, `--config <設定ファイル>`: 検証ルールや設定を記述した設定ファイル（YAML形式）を指定します。

#### 検証オプション
- `--ignore-errors`: 検証エラーが発生しても処理を継続します。
- `--validate-only`: バリデーションのみを実行し、値の抽出や出力は行いません。

#### 出力オプション
- `-o`, `--output <出力ファイル>`: JSONデータの出力先ファイルを指定します。
- `--log <ログファイル>`: 検証エラーを記録するログファイルを指定します。
- `--format <フォーマット>`: 出力フォーマットを指定します（`json`, `yaml`）。デフォルトは`json`です。
- `--template <Jinja2テンプレートファイル>`: Jinja2テンプレートを使用して出力をカスタマイズします。`--template`オプションを指定した場合、`--format`オプションは無視されます。

#### ヘルプとバージョン
- `-h`, `--help`: ヘルプ情報を表示します。
- `-v`, `--version`: ツールのバージョンを表示します。

## 使用例

### デフォルト設定でExcelファイルを検証
```
excel-validator input.xlsx
```

### 特定の設定ファイルを使用して検証
```
excel-validator -c rules.yaml input.xlsx
```

### 検証結果をJSONファイルに出力
```
excel-validator -o results.json input.xlsx
```

### Jinja2テンプレートを使用して出力
```
excel-validator --template template.j2 input.xlsx
```

### バリデーションのみを実行
```
excel-validator --validate-only input.xlsx
```

### バリデーションエラーを無視して処理を継続
```
excel-validator --ignore-errors input.xlsx
```

### バリデーション結果をログファイルに出力
```
excel-validator --log validation.log input.xlsx
```
