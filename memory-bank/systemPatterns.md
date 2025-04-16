# systemPatterns.md

## システム構成・設計パターン

- 設定ファイル（YAML）→値取得ロジック→出力（JSON/YAML/Jinja2テンプレート）というシンプルなパイプライン
- openpyxlのdata_onlyモードで計算後の値を取得
- コマンドライン引数で設定ファイル・出力ファイルを指定可能
- 拡張性を考慮し、出力フォーマット追加やエラー処理をモジュール化
- 設定ファイル（YAML）でシート名または`*N`（左からN番目のシート）指定が可能な柔軟な値取得パターンを採用
- main.pyのget_excel_values関数で`*N`記法を判定し、シートリストからインデックスで選択する実装
- シート名に`*`が使えないExcel仕様を活用し、記法の衝突を回避
- エラー処理：範囲外や不正な`*N`指定はValueErrorで明示的に例外化
- `*N`記法の自動テスト（test_main.py）でシート順指定の動作を検証
- 出力は現状JSONのみ対応。YAML出力は今後の拡張予定。
- 出力フォーマット（json/yaml/jinja2等）は今後すべて設定ファイル（YAML）の`output.format`で指定する方針。CLIの`--format`オプションは将来的に廃止予定（現状は互換のため残存）。
- main.pyのコマンドライン引数（--output, --include-empty-range-row等）はCLI柔軟性向上のため実装。
- ファイル未指定・未存在・不正なシート/セル指定時は明示的なエラー出力・終了（sys.exit）で堅牢化。
- src/xlsx_value_picker/配下に実装を集約し、パッケージとして配布可能な構成
- CLIコマンドはpyproject.tomlの[project.scripts]で登録し、uv/pipインストール後にxlsx-value-pickerで実行可能
- テストはPYTHONPATH=srcでsrc配下の最新コードを直接参照
- サブプロセスでのCLIテストもuv run python -m ... + PYTHONPATH指定で仮想環境汚染なし
- CI/CDはGitHub Actionsでpytestを自動実行
- .gitignoreで開発・テスト生成物を除外、LICENSE（MIT）を付与
- ドキュメント・サンプル・CI・不要ファイル除外も配布仕様に準拠
- Jinja2テンプレート出力時は、output.format: jinja2 で切り替え
- テンプレートは template_file（外部ファイル）または template（YAML内直接記載）のいずれかで指定可能
- 出力先はCLIの--outputオプションで指定し、YAML内でのoutput_file指定は不要
- 既存のExcel値抽出仕様（table/range/named cell）・型安全設計・テスト自動化・ドキュメント重視の方針を継続

## テーブル・範囲指定による複数レコード抽出仕様

- 設定ファイル（YAML）でExcelテーブル名またはセル範囲を指定し、複数行・複数列のデータを抽出できる方式を採用。
- 出力JSONのキー名は、Excel上の列名または列位置番号と任意のキー名のマッピングで柔軟に指定可能。

### table指定方式
- `table`キーでExcelテーブル名（ListObject名）を指定。
- `columns`で「Excel列名: 出力キー名」のマッピングを記述。
- 例:
  ```yaml
  - table: Table1
    columns:
      Excel列名1: 出力キー1
      Excel列名2: 出力キー2
  ```

### range指定方式
- `range`キーでデータ部分のみのセル範囲（例: Sheet1!A2:D10）を指定（ヘッダ行は含めない）。
- `columns`で「左からの列位置番号（1始まり）: 出力キー名」のマッピングを記述。
- 例:
  ```yaml
  - range: Sheet1!A2:D10
    columns:
      1: keyA
      3: keyC
  ```
- 列位置番号は1始まりで統一。

### range指定の空行（全列None）スキップ仕様（2025/04/16追加）
- range指定でデータ範囲を抽出する際、各行の「すべての列がNone（空）」となる行はデフォルトで出力に含めずスキップする。
- コマンドラインオプション`--include-empty-range-row`を指定した場合のみ、全列がNoneの行も出力に含める。
- これにより、意図しない空行の混入を防ぎつつ、必要に応じて明示的に空行も取得できる柔軟な仕様となっている。
- 実装はextract_range_records関数・main.pyのCLI引数で制御され、テストもtest_main.pyで自動化されている。

### Jinja2テンプレート出力のYAML定義例
```yaml
output:
  format: jinja2
  # どちらか一方を指定
  template_file: path/to/template.j2   # 外部ファイルを使う場合
  # template: |                      # YAML内に直接テンプレートを記載する場合
  #   {{ data.key1 }} - {{ data.key2 }}

values:
  - table: Table1
    columns:
      Excel列名1: key1
      Excel列名2: key2
```

- テンプレート内で参照できる変数名やデータ構造は今後設計・明記予定
- 既存の出力（JSON/YAML）との排他制御・CLIオプションとの整合性も考慮

## 主要コンポーネント
- src/xlsx_value_picker/cli.py: エントリーポイント、全体の制御
- src/xlsx_value_picker/__main__.py: python -m実行用
- pyproject.toml: パッケージ・CLI・依存管理
- test/test_main.py: 単体・E2Eテスト
- .github/workflows/test.yml: CI自動テスト

## 重要な実装パス
- 設定ファイルのバリデーション
- Excelファイルの安全な読み込み
- 取得値の型変換・整形
- CLI/サブプロセス経由のE2Eテスト
