# CLIと既存機能の統合計画

## 1. 概要

このドキュメントでは、Clickライブラリを使用して実装されたCLIスケルトンと既存の機能（Excelファイルからの値取得、JSON/YAML/Jinja2出力機能）の統合について計画します。実装済みのスケルトンに実際の機能を追加し、CLIから利用できるようにするための実装計画です。

## 2. 現状の確認

### 2.1 CLIスケルトンの状況

- Clickライブラリを使用したCLIスケルトンの実装が完了
- コマンドライン引数処理の構造は整備済み
- 主要なオプション（入力ファイル、設定ファイル、出力設定など）は定義済み
- 現状ではオプションの値を表示するだけの実装

### 2.2 既存機能の状況

- `config.py`: Excelファイルからの値取得機能が実装されている
- `template.py`: Jinja2テンプレートによる出力機能が実装されている
- 既存のCLI実装（`cli.py`の旧バージョン）では、これらの機能を呼び出していた

## 3. 統合のアプローチ

### 3.1 基本方針

1. **段階的な実装**: 
   - 最初に基本機能（Excelファイルからの値取得と出力）をCLIスケルトンに統合
   - その後にエラーハンドリングと検証機能を追加

2. **互換性の確保**:
   - 既存のYAML設定ファイルフォーマットとの互換性を**維持しない**。新しい設定ファイルフォーマットを導入する
   - 出力形式（JSON/YAML/Jinja2）の選択肢は維持

3. **テスト駆動開発**:
   - 各統合ステップでテストケースを追加
   - 機能的な正確性を確保

### 3.2 具体的な実装ステップ

1. **Excelファイル処理の統合**:
   ```python
   # 実装イメージ
   def main(input_file, config, ignore_errors, output, log, output_format, template, include_empty_range_row):
       # 1. 設定ファイルの読み込み
       cfg = load_config(config)
       
       # 2. Excelファイルから値を取得
       values = get_excel_values(input_file, cfg, include_empty_row=include_empty_range_row)
       
       # 3. 出力処理（次のステップで実装）
       # ...
   ```

2. **出力機能の統合**:
   ```python
   # 実装イメージ - 続き
   def main(input_file, config, ignore_errors, output, log, output_format, template, include_empty_range_row):
       # ...既存のコード...
       
       # 出力形式の決定
       if output_format == 'json':
           result = json.dumps(values, ensure_ascii=False, indent=2)
       elif output_format == 'yaml':
           result = yaml.dump(values, allow_unicode=True)
       elif output_format == 'jinja2' and template:
           result = render_template(template, values)
       else:
           # デフォルトはJSON
           result = json.dumps(values, ensure_ascii=False, indent=2)
       
       # 出力先の決定
       if output:
           with open(output, 'w', encoding='utf-8') as f:
               f.write(result)
       else:
           click.echo(result)
   ```

3. **エラーハンドリングの追加**:
   ```python
   # 実装イメージ - エラーハンドリング
   def main(input_file, config, ignore_errors, output, log, output_format, template, include_empty_range_row):
       try:
           # 1. 設定ファイルの読み込み
           cfg = load_config(config)
           
           # 2. Excelファイルから値を取得
           values = get_excel_values(input_file, cfg, include_empty_row=include_empty_range_row)
           
           # 3. 出力処理
           # ...省略...
           
       except Exception as e:
           if log:
               # エラーログ出力
               with open(log, 'w', encoding='utf-8') as f:
                   f.write(f"Error: {str(e)}")
           
           if not ignore_errors:
               click.echo(f"Error: {str(e)}", err=True)
               sys.exit(1)
           else:
               click.echo(f"Warning: {str(e)}", err=True)
   ```

4. **バリデーション機能の準備** (将来の実装予定):
   ```python
   # 実装イメージ - バリデーション機能
   from .validation import validate_values
   
   def main(input_file, config, ignore_errors, output, log, output_format, template, include_empty_range_row):
       try:
           # ...既存のコード...
           
           # バリデーション処理（将来の実装）
           validation_results = validate_values(values, cfg.get('validation_rules', {}))
           
           # バリデーション結果のログ出力
           if log and validation_results:
               with open(log, 'w', encoding='utf-8') as f:
                   f.write(json.dumps(validation_results, ensure_ascii=False, indent=2))
           
           # バリデーションエラー処理
           if validation_results and not ignore_errors:
               click.echo(f"Validation failed: {len(validation_results)} errors found.", err=True)
               sys.exit(1)
           
           # ...出力処理...
       except Exception as e:
           # ...エラー処理...
   ```

## 4. テスト計画

### 4.1 単体テスト

- **CLIオプション処理テスト**: 各コマンドラインオプションが正しく処理されることを確認
- **設定ファイル読み込みテスト**: 様々なフォーマットの設定ファイルが正しく読み込まれることを確認
- **出力フォーマットテスト**: 各出力形式（JSON、YAML、Jinja2）が正しく動作することを確認

### 4.2 統合テスト

- **基本的なワークフロー**: 設定ファイルの読み込み -> Excelからの値取得 -> 出力、の一連のフローが正しく動作することを確認
- **エラーケース**: 不正な入力、存在しないファイル、不正な設定などに対して適切にエラー処理が行われることを確認

## 5. 実装スケジュール

1. **基本機能の統合** (1日):
   - Excelファイルからの値取得と設定ファイル読み込みの統合
   - 基本的な出力機能の統合

2. **出力オプションの実装** (0.5日):
   - 出力ファイル処理
   - フォーマット選択処理
   - テンプレート処理

3. **エラーハンドリングの追加** (0.5日):
   - 例外処理の実装
   - エラーログ出力機能

4. **テスト作成と実行** (1日):
   - 単体テストの作成
   - 統合テストの作成
   - テストの実行と不具合修正

合計: 約3日間

## 6. 注意点

- **既存コードの変更**: 既存コードは基本的に破棄し、適切な設計を検討したうえで再実装する。この時ファイルの分割なども併せて検討する。
- **エラーメッセージ**: ユーザーフレンドリーなエラーメッセージを提供するよう心がける
- **設定ファイルのバリデーション**: 設定ファイルの形式チェックを強化し、わかりやすいエラーメッセージを提供する
- **ドキュメント更新**: 実装が完了したらREADMEやユーザードキュメントを更新する

## 7. 今後の拡張

- **プログレスバーの追加**: 大きなExcelファイル処理時に進捗状況を表示する機能
- **バッチ処理モード**: 複数のExcelファイルを一度に処理する機能
- **インタラクティブモード**: 対話形式で設定を行う機能
- **ロギング機能強化**: 詳細なロギングレベル制御とフォーマット指定

---

最終更新日: 2025年4月19日