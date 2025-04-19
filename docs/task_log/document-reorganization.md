# ドキュメント整理計画

## 1. 概要

プロジェクト文書が増えるにつれて、`docs/`ディレクトリ内のファイル数が増加し、以下の問題が発生しています：

1. プロジェクト全体に関する文書と個別タスクに関する作業計画文書が混在している
2. 文書間の関係性が分かりにくくなっている
3. 新しい文書を追加する際の配置場所の判断が難しくなっている

この問題を解決するために、ドキュメント構成を整理し、より明確な構造を持たせる計画を立てます。

## 2. 新しいディレクトリ構造

プロジェクトのドキュメントを以下のように再構成します：

```
docs/
├── README.md              # ドキュメントディレクトリの説明
├── project/               # プロジェクト全体に関わる文書（将来的に作成予定）
├── task_log/              # 個別タスクの作業計画や実施記録
│   ├── cli-implementation-plan.md
│   ├── cli-integration-plan.md
│   ├── expression-type-recognition-fix.md
│   ├── mermaid-fix.md
│   ├── test-execution-plan.md
│   └── test-implementation-plan.md
└── # その他のプロジェクト主要文書はdocs/直下に残す
    ├── cli-spec.md
    ├── directory-structure.md
    ├── mermaid-style-guide.md
    ├── project-status.md
    ├── requirements.md
    ├── technology-selection.md
    └── validation-design.md
```

## 3. 移行計画

### 3.1 タスク固有の文書の移動

以下の文書を `docs/task_log/` ディレクトリに移動します：

1. `cli-implementation-plan.md` - CLIスケルトン実装計画
2. `cli-integration-plan.md` - CLIと既存機能の統合計画
3. `test-implementation-plan.md` - テスト実装計画
4. `test-execution-plan.md` - テスト実行計画
5. `mermaid-fix.md` - Mermaid関連の修正計画
6. `expression-type-recognition-fix.md` - Expression型認識問題の修正計画

### 3.2 リンク参照の更新

既存文書内のこれらのファイルへのリンクを更新します。特に以下の文書のリンクを確認します：

1. `project-status.md`
2. その他関連文書

### 3.3 インデックスファイルの作成（将来計画）

将来的に`docs/README.md`を作成し、ドキュメントの全体像を分かりやすく説明します。

## 4. 新規文書作成時のルール

今後、新しい文書を作成する際は以下のルールに従います：

1. **プロジェクト全体に関わる文書**：要件定義、設計書、仕様書などは `docs/` ディレクトリ直下に配置
2. **個別タスクの作業計画/実施記録**：特定のタスクに関連する作業計画や実施記録は `docs/task_log/` ディレクトリに配置
3. **命名規則**：ファイル名はケバブケース（小文字のみ、単語間はハイフン）で統一し、内容を表す明確な名前をつける

## 5. 実施手順

1. `docs/task_log/` ディレクトリの作成（完了）
2. タスク固有の文書の移動
3. リンク参照の更新
4. 文書メンテナンスの継続的な実施

## 6. 今後の課題

1. ドキュメントのバージョン管理方法の確立
2. ドキュメント間の関連性を視覚的に表現する方法の検討
3. 自動生成されるドキュメントと手動更新ドキュメントの管理方法の確立

---

最終更新日: 2025年4月19日