# Excel検証およびJSON出力ツールのCLIインターフェース仕様

## コマンド構造

`xlsx-value-picker` は複数のサブコマンドを持つグループコマンドとして実装されています。

```
xlsx-value-picker [グローバルオプション] <サブコマンド> [サブコマンドオプション]
```

### グローバルオプション
- `-v`, `--version`: ツールのバージョンを表示します。
- `-h`, `--help`: ヘルプ情報を表示します。

### サブコマンド

#### `run` - Excelファイル処理（値取得・バリデーション・出力）

##### 基本構文
```
xlsx-value-picker run [オプション] <入力ファイル>
```

##### オプション

###### 入力オプション
- `-c`, `--config <設定ファイル>`: 検証ルールや設定を記述した設定ファイル（YAML形式）を指定します。デフォルトは `config.yaml` です。

###### 検証オプション
- `--ignore-errors`: 検証エラーが発生しても処理を継続します。
- `--validate-only`: バリデーションのみを実行し、値の抽出や出力は行いません。

###### 出力オプション
- `-o`, `--output <出力ファイル>`: データの出力先ファイルを指定します。未指定の場合は標準出力に出力します。
- `--log <ログファイル>`: 検証エラーを記録するログファイルを指定します。
- `--include-empty-cells`: 空セルも出力に含めます。デフォルトでは空セルは出力から除外されます。

#### `server` - MCPサーバー機能

MCPサーバー機能は、Model Context Protocol (MCP) に準拠したサーバーとして動作し、標準入出力を介して外部のMCPクライアント（VS Code拡張機能など）と通信します。

##### 基本構文
```
xlsx-value-picker server [オプション]
```

##### オプション
- `-c`, `--config <設定ファイル>`: MCPサーバー設定ファイル（YAML形式）を指定します。デフォルトは `mcp.yaml` です。
- `--log-level <レベル>`: ログレベルを設定します。指定可能な値は `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` です。デフォルトは `INFO` です。

## 使用例

### デフォルト設定でExcelファイルを処理
```
xlsx-value-picker run input.xlsx
```

### 特定の設定ファイルを使用して検証
```
xlsx-value-picker run -c rules.yaml input.xlsx
```

### 検証結果をJSONファイルに出力
```
xlsx-value-picker run -o results.json input.xlsx
```

### バリデーションのみを実行
```
xlsx-value-picker run --validate-only input.xlsx
```

### バリデーションエラーを無視して処理を継続
```
xlsx-value-picker run --ignore-errors input.xlsx
```

### バリデーション結果をログファイルに出力
```
xlsx-value-picker run --log validation.log input.xlsx
```

### MCPサーバーを起動
```
xlsx-value-picker server
```

### カスタム設定ファイルとログレベルでMCPサーバーを起動
```
xlsx-value-picker server -c custom_mcp_config.yaml --log-level DEBUG
```

## 設定ファイル

### run コマンド用の設定ファイル
run コマンドでは、以下のような構造のYAML/JSONファイルを設定ファイルとして使用します。

```yaml
# 取得フィールド定義
fields:
  field_name1: "Sheet1!A1"
  field_name2: "Sheet1!B2:C3"
  field_name3: "Sheet2!D4"

# バリデーションルール
rules:
  - name: "数値範囲チェック"
    expression:
      compare:
        left_field: "field_name1"
        operator: ">="
        right: 10
    error_message: "{field}は10以上である必要があります（現在: {left_value}）"

# 出力設定
output:
  format: "json"  # json, yaml, csv が指定可能
```

### server コマンド用の設定ファイル
server コマンドでは、以下のような構造のYAML/JSONファイルを設定ファイルとして使用します。

```yaml
# 利用可能なモデル定義
models:
  - model_name: "model1"
    config: "./model1_config.yaml"
    description: "Model 1 description"
  - model_name: "model2"
    config: "./model2_config.yaml"
    description: "Model 2 description"

# MCPサーバー全体の設定
config:
  tool_descriptions:
    listModels: "利用可能なExcelファイル処理モデルの一覧を取得します"
    getModelInfo: "特定のモデルの詳細情報を取得します"
    getDiagnostics: "モデルのバリデーション結果を取得します"
    getFileContent: "Excelファイルの内容を構造化テキストで取得します"
```

モデル設定ファイル（例: model1_config.yaml）は、run コマンドと同様の構造を持ちます。
