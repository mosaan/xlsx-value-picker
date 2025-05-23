# xlsx-value-picker プロジェクト現状と作業計画

## 1. 現状の概要

xlsx-value-pickerプロジェクトは、Excelファイルからの値取得、バリデーション、および様々な形式での出力機能を提供することを目的としています。現在のプロジェクト状況は以下の通りです：

### 1.1 ドキュメント整備状況

**プロジェクト文書**:
- [要件定義書](project/requirements.md): 作成済み
- [技術選定ドキュメント](project/technology-selection.md): 作成済み

**仕様文書**:
- [CLIインターフェース仕様](spec/cli-spec.md): 作成済み
- [バリデーションルールスキーマ](spec/rule-schema.json): 作成済み
- [MCPサーバー仕様](spec/mcp-server-spec.md): 整備中

**設計文書**:
- [バリデーション設計ドキュメント](design/validation-design.md): 作成済み
- [設定ローダー設計](design/config-loader-design.md): 作成済み
- [MCPサーバー設計](design/mcp-server-design.md): 整備中

**ガイドライン**:
- [Mermaidスタイルガイド](guide/mermaid-style-guide.md): 作成済み
- [ディレクトリ構造ガイドライン](guide/directory-structure-guideline.md): 作成済み
- [バージョン管理ガイドライン](guide/version-control-guideline.md): 作成済み
- [依存関係管理ガイドライン](guide/dependency-management-guideline.md): 作成済み
- [Pydanticモデル設計ガイドライン](guide/pydantic-model-design-guideline.md): 作成済み

**タスク記録**: (完了済みのタスク)
- CLI実装計画
- Expression型認識問題修正
- ドキュメント整理計画
- ドキュメント再編計画（ジャンル別）
- Mermaid図修正
- テスト実行計画
- テスト実装計画
- CLI統合計画
- バリデーション式モジュールの移動
- 不要モジュール（template.py）の削除
- テストコードのリファクタリング
- CLIのエラーハンドリング改善
- MCPサーバー機能の追加

### 1.2 実装状況

- 基本的なCLIフレームワーク: **Clickライブラリを用いた実装完了**（CLI仕様に準拠）
- Excelファイルからの値取得機能: **実装済み**
- 設定ファイル読み込み機能: **JSONスキーマによる検証を含めて実装完了**
- YAML/JSON出力機能: **実装済み**
- Jinja2テンプレートによる出力機能: **実装済み**
- Expression派生クラスの型認識問題: **修正完了**（Union型と前方参照を活用）
- CLIオプション（--ignore-errors）の動作: **改善完了**（すべてのエラー発生箇所で一貫した処理）
- テスト環境: **基本的なテスト一式が実行可能な状態**
- バリデーション機能: **すべてのルール型を実装済み、CLI統合と基本的な出力機能も実装済み**
- バリデーション関連モジュール構成: **リファクタリング完了**（`validation_expressions.py`の分離）
- MCPサーバー機能: **基本機能実装完了**（Model Context Protocol準拠のサーバーとして動作、CLI統合も完了）

### 1.3 現状の課題

1. ~~ドキュメントと実装の不一致~~
   - ~~CLIインターフェース仕様と実際の実装が完全に一致していない。また、技術選定で検討した`Click`ライブラリを使用していない。~~ -> CLIインターフェースは仕様に準拠した実装が完了（Clickライブラリ採用済み）

2. ~~バリデーション機能の完成~~
   - ~~バリデーションエンジンの完成~~ -> **完了**
   - ~~すべてのルール型（compare, required, any_of, all_of, not, regex_match, enum）の実装確認~~ -> **すべて実装完了**
   - ~~バリデーション結果の出力機能~~ -> **基本機能実装完了**
   - バリデーション機能の詳細な改善（以下の点が残っています）:
     - NotExpressionのエラーフィールド情報の扱い明確化
     - エラーメッセージのテンプレート変数に関するドキュメント整備
     - EnumExpressionのcase_sensitiveオプションの実装
     - 複合条件のエラー情報集約に関する設計文書の充実

3. テスト整備の拡充
   - 既存のテストは基本的な機能をカバーしているが、エッジケースや組み合わせテストの追加が必要
   - テストカバレッジの向上
   - E2Eテストの追加

4. ユーザー向けドキュメントの整備
   - インストール方法の詳細説明
   - 設定ファイルの記述例
   - 使い方のチュートリアル

5. MCPサーバー機能の拡張
   - MCPサーバー機能のドキュメント整備
   - Excelパス管理機能の強化
   - バリデーション結果とモデルIDの連携強化
   - 生成AI連携のためのプロンプトテンプレート実装

## 2. 作業計画

以下の順序でプロジェクトを進めていきます：

### フェーズ1: ドキュメント完備と実装の方針確定（完了）

- [x] 基本的なドキュメント整備
- [x] プロジェクトの現状と計画の文書化（本ドキュメント）
- [x] 実装方針の詳細検討と文書化（[バリデーション設計ドキュメント](design/validation-design.md)、[Mermaidスタイルガイド](guide/mermaid-style-guide.md)）
- [x] スキーマ定義の見直し・拡充（JSONスキーマによる検証実装済み）

### フェーズ2: コードベースの見直しと再構築（完了）

- [x] 現在のコードベースの全体見直し
- [x] CLIインターフェース実装の修正・仕様との整合性確保（Clickライブラリ採用）
- [x] 既存機能（Excelファイルからの値取得、出力機能）とClickベースのCLI実装の統合
- [x] テスティングフレームワークの整備
- [x] コア機能のテストカバレッジ向上
- [x] Expression派生クラスの型認識問題修正
- [x] モジュール構成の最適化（バリデーション式を専用モジュールに分離）
- [x] 不要モジュールの削除（template.py）

### フェーズ3: バリデーション機能の実装（完了）

- [x] バリデーションエンジンの設計と実装計画
- [x] ルール定義のパーサーの実装
- [x] 基本的なルール（compare, required）の実装
- [x] 複合ルール（any_of, all_of, not）の実装
- [x] パターンマッチングルール（regex_match, enum）の実装
- [x] バリデーション結果の出力機能

### フェーズ3-A: バリデーション機能の詳細改善（新規追加）

- [ ] NotExpressionのエラーフィールド情報の扱い明確化
- [ ] バリデーションルールのテンプレート変数に関するドキュメント整備
- [ ] EnumExpressionのcase_sensitiveオプションの実装と確認
- [ ] 複合条件のエラー情報集約に関する設計ドキュメントの充実

### フェーズ3-B: MCPサーバー機能の実装（完了）

- [x] MCPサーバー基本機能の設計
- [x] MCPサーバーのプロトコル実装
- [x] CLI統合（serverサブコマンドの実装）
- [x] 基本的なテスト実装
- [x] ドキュメントの更新

### フェーズ4: ユーザビリティ向上（予定）

- [x] エラーメッセージの改善（--ignore-errorsオプションの一貫した動作）
- [ ] ユーザードキュメントの整備
- [ ] サンプルおよびチュートリアルの作成
- [ ] READMEの充実

### フェーズ5: リリースと継続的改善（予定）

- [ ] バージョン管理の徹底
- [ ] CI/CDパイプラインの整備
- [ ] リリースプロセスの確立
- [ ] フィードバックの収集と継続的な改善

## 3. 次のタスク

短期的に着手するタスクは以下の通りです：

1. **バリデーション機能の詳細改善**
   - バリデーションルールのテンプレート変数に関するドキュメント整備
   - EnumExpressionのcase_sensitiveオプションの実装と確認
   - 複合条件のエラー情報集約に関する設計ドキュメントの充実
   
2. **MCPサーバー機能の拡張**
   - MCPサーバー仕様ドキュメントの整備
   - Excelファイルパス管理機能の強化
   - バリデーション結果とモデルIDの連携強化
   - 生成AI連携のためのプロンプトテンプレート実装

3. **テスト拡充**
   - テストカバレッジ向上のための追加テスト作成
   - より複雑なネストされたバリデーションシナリオのテスト
   - パフォーマンステストの追加

4. **ユーザードキュメント整備**
   - インストールガイドの作成
   - 設定ファイル記述ガイドの作成
   - チュートリアルとサンプル作成
   - MCPサーバー機能の利用ガイド作成

## 4. 注意事項

- **コードの品質と型安全性**: Pydanticモデルを活用した型安全な実装を心がけてください。詳細は [`guide/pydantic-model-design-guideline.md`](guide/pydantic-model-design-guideline.md) を参照してください。Expression派生クラスのような複雑な型階層を扱う場合は特に注意が必要です。

- **互換性の維持**: 既存のAPIとの後方互換性を維持しながら機能拡張を行ってください。

- **ドキュメント間の整合性維持**: 複数のドキュメントで同じ内容を記述している箇所があるため、更新時は関連するすべてのドキュメントを確認し、整合性を保つことが重要です。

- **Mermaid図表の構文**: ドキュメント内のMermaid図表を編集する際は、[`guide/mermaid-style-guide.md`](guide/mermaid-style-guide.md)に記載されているガイドラインを遵守してください。

- **依存関係管理**: 依存パッケージのバージョン固定が必要です。uv（Pythonパッケージマネージャー）を使用して依存関係を管理しています。

## 5. 今後の展望

- GUIによるルール定義支援ツールの開発
- Webインターフェースの提供
- 他のスプレッドシート形式（CSV、Google Spreadsheetsなど）への対応
- プラグインシステムによる拡張性の向上
- ルールのリアルタイム検証機能の提供（Excel VBAとの連携など）
- 複数シートやブックにまたがるクロス参照バリデーションの対応
- MCPサーバー機能の拡充と生成AI連携の強化
- VS Code拡張機能との連携によるExcel処理の効率化

---

最終更新日: 2025年4月30日