# ドキュメント再編計画 - ジャンル別整理

## 1. 背景と目的

現在のxlsx-value-pickerプロジェクトのドキュメント構成は、基本的なタスク文書の分離（`task_log/`ディレクトリの作成と移行）は完了していますが、さらに細かな分類基準を設けることで以下の効果が期待できます：

1. **文書の探しやすさの向上**: 必要な文書がどこにあるかをディレクトリ構造から直感的に理解できる
2. **関連文書の集約**: 同じジャンルやテーマに属する文書を近くに配置することで相互参照が容易になる
3. **文書作成時の配置場所の明確化**: 新規文書作成時にどこに配置すべきかの判断基準を提供する
4. **プロジェクト全体の構造理解の促進**: 文書構造を通じてプロジェクト全体の構造や関心事を把握しやすくなる

## 2. 現在の文書構成

現在のドキュメント構成は以下の通りです：

```
docs/
├── cli-spec.md                # CLIインターフェース仕様
├── config-loader-design.md    # 設定ローダー設計
├── directory-structure.md     # ディレクトリ構造定義
├── mermaid-style-guide.md     # Mermaidスタイルガイド
├── project-status.md          # プロジェクト現状文書
├── requirements.md            # 要件定義書
├── rule-schema.json           # バリデーションルールのJSONスキーマ
├── technology-selection.md    # 技術選定ドキュメント
├── validation-design.md       # バリデーション設計ドキュメント
└── task_log/                  # 個別タスクの作業計画や実施記録
    ├── cli-implementation-plan.md
    ├── cli-integration-plan.md
    ├── document-reorganization-review.md
    ├── document-reorganization.md
    ├── expression-type-recognition-fix.md
    ├── mermaid-fix.md
    ├── test-execution-plan.md
    └── test-implementation-plan.md
```

## 3. 新たなジャンル分類の提案

文書の性質に基づき、以下のジャンル分類を提案します：

### 3.1 ジャンルの定義

1. **project**: プロジェクト全体に関わる計画、状況、方針などの文書
2. **spec**: 機能仕様、API仕様、設計仕様などの文書
3. **guide**: 開発ガイドライン、コーディング規約、スタイルガイドなど
4. **task_log**: すでに分類済みの個別タスク作業記録（変更なし）
5. **design**: 設計ドキュメント、アーキテクチャ設計、モジュール設計など

### 3.2 新ディレクトリ構造案

```
docs/
├── README.md                  # ドキュメント全体の概要・ガイド
├── project/                   # プロジェクト関連文書
│   ├── requirements.md        # 要件定義書
│   ├── project-status.md      # プロジェクト現状文書
│   ├── technology-selection.md # 技術選定ドキュメント
│   └── directory-structure.md # ディレクトリ構造定義
├── spec/                      # 仕様関連文書
│   ├── cli-spec.md            # CLIインターフェース仕様
│   └── rule-schema.json       # バリデーションルールのJSONスキーマ
├── guide/                     # ガイドライン関連文書
│   └── mermaid-style-guide.md # Mermaidスタイルガイド
├── design/                    # 設計文書
│   ├── validation-design.md   # バリデーション設計ドキュメント
│   └── config-loader-design.md # 設定ローダー設計
└── task_log/                  # （既存）個別タスクの作業計画や実施記録
    └── ...（現在の内容）
```

## 4. project-status.md からの参照方法

プロジェクト現状文書（`project-status.md`）は、他の文書への参照が多く含まれる重要な文書です。ジャンル別の整理に伴い、参照方法を以下のように変更します：

### 4.1 現在の参照方法

```markdown
### 1.1 ドキュメント整備状況
- [要件定義書](requirements.md): 作成済み
- [CLIインターフェース仕様](cli-spec.md): 作成済み
- [ディレクトリ構造定義](directory-structure.md): 作成済み
- [技術選定ドキュメント](technology-selection.md): 作成済み
- [プロジェクト現状文書](project-status.md): 作成済み。随時更新。
- [バリデーション設計ドキュメント](validation-design.md): 作成済み
- [Mermaidスタイルガイド](mermaid-style-guide.md): 作成済み
- [CLI実装計画](task_log/cli-implementation-plan.md): 作成済み。廃止予定。
- [Expression型認識問題修正](task_log/expression-type-recognition-fix.md): 作成済み。問題が解決済み。
- [ドキュメント整理計画](task_log/document-reorganization.md): 作成済み。実施中。
```

### 4.2 新しい参照方法案

以下の3つの案を検討します：

#### 案1: 相対パスによる参照（シンプルだが移動に弱い）

```markdown
### 1.1 ドキュメント整備状況
- [要件定義書](../project/requirements.md): 作成済み
- [CLIインターフェース仕様](../spec/cli-spec.md): 作成済み
- [ディレクトリ構造定義](../project/directory-structure.md): 作成済み
- ...
```

#### 案2: カテゴリ付きリスト（視認性向上）

```markdown
### 1.1 ドキュメント整備状況

**プロジェクト文書**:
- [要件定義書](../project/requirements.md): 作成済み
- [ディレクトリ構造定義](../project/directory-structure.md): 作成済み
- [技術選定ドキュメント](../project/technology-selection.md): 作成済み
- [プロジェクト現状文書](../project/project-status.md): 作成済み。随時更新。

**仕様文書**:
- [CLIインターフェース仕様](../spec/cli-spec.md): 作成済み
- [バリデーションルールスキーマ](../spec/rule-schema.json): 作成済み

**設計文書**:
- [バリデーション設計ドキュメント](../design/validation-design.md): 作成済み
- [設定ローダー設計](../design/config-loader-design.md): 作成済み

**ガイドライン**:
- [Mermaidスタイルガイド](../guide/mermaid-style-guide.md): 作成済み

**タスク記録**:
- [CLI実装計画](../task_log/cli-implementation-plan.md): 作成済み。廃止予定。
- [Expression型認識問題修正](../task_log/expression-type-recognition-fix.md): 作成済み。問題が解決済み。
- [ドキュメント整理計画](../task_log/document-reorganization.md): 作成済み。実施中。
```

#### 案3: ドキュメントインデックスファイル参照方式（将来的な発展性）

README.md にすべてのドキュメントのインデックスを作成し、そこから統一的に参照する方式。
project-status.md ではインデックスへの参照を記載する。

```markdown
### 1.1 ドキュメント整備状況

プロジェクトのドキュメント一覧は[ドキュメント索引](../README.md)を参照してください。

主な文書の状況：
- 要件定義書: 作成済み
- CLIインターフェース仕様: 作成済み
- バリデーション設計ドキュメント: 作成済み
- Mermaidスタイルガイド: 作成済み
- ドキュメント整理計画: 作成済み、実施中
```

## 5. 移行計画

### 5.1 実施手順

1. `docs/`直下に新たな分類ディレクトリ（project, spec, guide, design）を作成
2. 各文書を適切なディレクトリに移動
3. README.md を作成し、ドキュメント全体の概要と索引を記載
4. project-status.md を移動し、内部リンクを更新（案2の方式を採用）
5. 他の文書内のクロスリファレンスを更新

### 5.2 移行スケジュール案

1. ディレクトリ構造の作成（即時）
2. ドキュメント移動とREADME.md作成（1日以内）
3. リンク参照の更新（1-2日）
4. 確認とレビュー（1日）

全体で2-3日程度の作業を見込む。

## 6. 検討事項と課題

### 6.1 今後の拡張性

- APIドキュメント、チュートリアル、ユーザーガイドなどが追加される可能性
- 国際化対応（英語ドキュメント）の際のディレクトリ構造
- 自動生成ドキュメントの配置場所

### 6.2 潜在的な問題点

- 深いディレクトリ階層によるアクセス性低下の可能性
- リンク管理・更新の複雑化
- 分類の曖昧さによる配置判断の難しさ

## 7. 推奨案

各案の長所・短所を考慮し、以下の方針を推奨します：

1. **ジャンル別ディレクトリ構造の採用**: 提案の3.2節で示した構造を基本とする
2. **project-status.md からの参照方式は案2を採用**: カテゴリごとにグループ化してリスト表示
3. **README.md の作成**: ドキュメント全体の索引および利用ガイドとする

この方針により、文書の論理的な整理と探しやすさの向上を両立できます。

## 8. 次のステップ

本計画の承認後、具体的な実施計画を策定し、作業に取り掛かります。以下の点について確認が必要です：

1. 提案したジャンル分類が適切かどうか
2. 各文書の分類先に問題がないか
3. 他に考慮すべき分類カテゴリはないか
4. project-status.md からの参照方式として案2が最適か

## 9. まとめ

本計画では、xlsx-value-pickerプロジェクトのドキュメントをジャンルごとに整理し、より体系的な構造にすることを提案しました。これにより、文書の探しやすさと関連性の把握が容易になり、プロジェクトの継続的発展をドキュメント面でサポートします。

## 10. レビューコメント

- 案2の参照方法は、視認性が高く、文書の関連性を強調できるため良いと思いますが、親ディレクトリに戻って参照する必要があるため、相対パスの管理が煩雑になる可能性があります。`project-status.md`自体は`docs/`直下に置くことを検討しても良いかもしれません。

---

最終更新日: 2025年4月19日