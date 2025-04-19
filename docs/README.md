# xlsx-value-picker プロジェクト ドキュメントガイド

このディレクトリにはxlsx-value-pickerプロジェクトに関するドキュメントが格納されています。ドキュメントはジャンルごとに整理されており、目的に応じて適切なドキュメントを参照してください。

## ドキュメント構成

### プロジェクト概要文書

- [プロジェクト現状文書](./project-status.md): プロジェクトの現在の状況、進行中の作業、今後の計画などを記載

### ジャンル別ドキュメント

#### プロジェクト文書 (`project/`)

プロジェクト全体に関わる計画、状況、方針などの文書

- [要件定義書](./project/requirements.md): プロジェクトの要件定義
- [技術選定ドキュメント](./project/technology-selection.md): 採用技術とその選定理由
- [ディレクトリ構造定義](./project/directory-structure.md): プロジェクトのディレクトリ構造と役割

#### 仕様文書 (`spec/`)

機能仕様、API仕様、設計仕様などの文書

- [CLIインターフェース仕様](./spec/cli-spec.md): コマンドラインインターフェースの仕様
- [バリデーションルールスキーマ](./spec/rule-schema.json): バリデーションルールを定義するJSONスキーマ

#### 設計文書 (`design/`)

設計ドキュメント、アーキテクチャ設計、モジュール設計など

- [バリデーション設計ドキュメント](./design/validation-design.md): バリデーション機能の設計
- [設定ローダー設計](./design/config-loader-design.md): 設定ファイル読み込み機能の設計

#### ガイドライン (`guide/`)

開発ガイドライン、コーディング規約、スタイルガイドなど

- [Mermaidスタイルガイド](./guide/mermaid-style-guide.md): Mermaidダイアグラム作成のガイドライン

#### タスク記録 (`task_log/`)

個別タスクの作業計画や実施記録

- [CLI実装計画](./task_log/cli-implementation-plan.md): CLI実装に関する作業計画
- [CLI統合計画](./task_log/cli-integration-plan.md): CLIと既存機能の統合計画
- [Expression型認識問題修正](./task_log/expression-type-recognition-fix.md): Expression派生クラスの型認識問題の解決策
- [ドキュメント整理計画](./task_log/document-reorganization.md): 当初のドキュメント整理計画
- [ドキュメント再編計画](./task_log/document-genre-reorganization.md): ジャンル別ドキュメント整理計画
- その他のタスク記録

## ドキュメント作成・更新のガイドライン

### 新規ドキュメント作成時の配置

- プロジェクト全体に関わる計画、状況、方針に関する文書: `project/`
- 機能仕様、API仕様、設計仕様に関する文書: `spec/`
- 設計ドキュメント、アーキテクチャ設計、モジュール設計に関する文書: `design/`
- 開発ガイドライン、コーディング規約、スタイルガイドに関する文書: `guide/`
- 個別タスクの作業計画や実施記録: `task_log/`

### 文書間の相互参照

- 同一ディレクトリ内のファイルを参照: `ファイル名.md`
- 他のディレクトリのファイルを参照: `ディレクトリ名/ファイル名.md`
- docs/直下のファイルを参照: `./ファイル名.md`

---

最終更新日: 2025年4月19日