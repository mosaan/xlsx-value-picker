# ドキュメント再編計画と実施記録

## 1. 背景と目的

xlsx-value-pickerプロジェクトの文書が増えるにつれて、以下の問題が発生しました：

1. **文書の混在**: プロジェクト全体に関する文書と個別タスクに関する作業計画文書が混在
2. **関係性の不明確さ**: 文書間の関連性が分かりにくい
3. **配置場所の曖昧さ**: 新しい文書を追加する際の配置場所の判断が難しい
4. **体系的整理の不足**: 文書のジャンル分けがされておらず、探しにくい

これらの問題を解決するため、複数段階にわたるドキュメント再編を計画・実施しました。

## 2. 初期ドキュメント整理計画

### 2.1 タスク文書とプロジェクト文書の分離

プロジェクト文書と個別タスクの作業記録を分離するため、以下の新しいディレクトリ構造を計画しました：

```
docs/
├── README.md              # ドキュメントディレクトリの説明
├── project/               # プロジェクト全体に関わる文書
├── task_log/              # 個別タスクの作業計画や実施記録
└── # その他のプロジェクト主要文書はdocs/直下に残す
```

### 2.2 移行計画

以下のタスク固有の文書を `docs/task_log/` ディレクトリに移動する計画を立てました：

1. `cli-implementation-plan.md` - CLIスケルトン実装計画
2. `cli-integration-plan.md` - CLIと既存機能の統合計画
3. `test-implementation-plan.md` - テスト実装計画
4. `test-execution-plan.md` - テスト実行計画
5. `mermaid-fix.md` - Mermaid関連の修正計画
6. `expression-type-recognition-fix.md` - Expression型認識問題の修正計画

### 2.3 新規文書作成時のルール

今後、新しい文書を作成する際のルールを以下のように定めました：

1. **プロジェクト全体に関わる文書**：`docs/` ディレクトリ直下に配置
2. **個別タスクの作業計画/実施記録**：`docs/task_log/` ディレクトリに配置
3. **命名規則**：ケバブケース（小文字のみ、単語間はハイフン）で統一

## 3. ドキュメント整理計画の配置に関する検討

初期ドキュメント整理計画自体（`document-reorganization.md`）の配置場所について検討を行いました。

### 3.1 文書の性質の検討

整理計画文書は以下のどちらの性質が強いかを分析しました：

1. **プロジェクト全体の方針を定めた文書**: ドキュメント構造やルールなど永続的な方針
2. **特定のタスクに関する作業計画文書**: 一時的なタスクに関する計画と手順

### 3.2 配置の選択肢と評価

**選択肢1: docs/ ディレクトリ直下に維持する（当初の状態）**
- メリット: プロジェクト全体の方針文書として見つけやすい
- デメリット: タスク固有の作業計画という観点では配置場所に一貫性がない

**選択肢2: docs/task_log/ ディレクトリに移動する**
- メリット: タスク固有の文書をすべて task_log/ に集約する方針に一致
- デメリット: プロジェクト全体のドキュメント構造に関する方針文書が見つけにくくなる可能性

### 3.3 結論

文書の主な性質と役割を考慮し、**タスク文書として task_log/ に移動する**ことを決定しました。

理由：
1. 文書の内容は主に「ドキュメント整理」という一時的なタスクの計画と実施手順に焦点を当てている
2. タスク完了後は主に履歴として参照される性質が強い
3. 永続的な方針部分は別途 `docs/README.md` などで整備する予定

## 4. ドキュメント再編計画 - ジャンル別整理

タスク文書の分離に加え、さらに文書のジャンルごとの整理を計画しました。

### 4.1 ジャンルの定義

文書の性質に基づき、以下のジャンル分類を定義しました：

1. **project**: プロジェクト全体に関わる計画、状況、方針などの文書
2. **spec**: 機能仕様、API仕様、設計仕様などの文書
3. **guide**: 開発ガイドライン、コーディング規約、スタイルガイドなど
4. **task_log**: 個別タスク作業記録（既存）
5. **design**: 設計ドキュメント、アーキテクチャ設計、モジュール設計など

### 4.2 新ディレクトリ構造案

```
docs/
├── README.md                  # ドキュメント全体の概要・ガイド
├── project-status.md          # プロジェクト現状文書（メインディレクトリに残す）
├── project/                   # プロジェクト関連文書
│   ├── requirements.md        # 要件定義書
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

### 4.3 参照方法の見直し

プロジェクト現状文書（`project-status.md`）からの参照方法を検討し、以下のカテゴリ付きリスト方式を採用しました：

```markdown
### 1.1 ドキュメント整備状況

**プロジェクト文書**:
- [要件定義書](project/requirements.md): 作成済み
- [ディレクトリ構造定義](project/directory-structure.md): 作成済み
- [技術選定ドキュメント](project/technology-selection.md): 作成済み

**仕様文書**:
- [CLIインターフェース仕様](spec/cli-spec.md): 作成済み
- [バリデーションルールスキーマ](spec/rule-schema.json): 作成済み

// 以下同様に分類
```

### 4.4 検討事項

- **project-status.md の配置**: プロジェクト全体の現状を表す重要文書として、アクセスしやすいように `docs/` 直下に維持
- **今後の拡張性**: APIドキュメント、チュートリアル、ユーザーガイド、国際化対応の可能性を考慮
- **潜在的な問題点**: 深いディレクトリ階層によるアクセス性低下の可能性、リンク管理の複雑化

## 5. ドキュメント再編実施手順

「ドキュメント再編計画 - ジャンル別整理」に基づく具体的な実施手順を策定しました。

### 5.1 移動対象ファイル一覧

#### project/ に移動するファイル
- requirements.md （既に移動済み）
- directory-structure.md （既に移動済み）
- technology-selection.md

#### spec/ に移動するファイル
- cli-spec.md
- rule-schema.json

#### guide/ に移動するファイル
- mermaid-style-guide.md

#### design/ に移動するファイル
- validation-design.md
- config-loader-design.md

#### docs/ 直下に残すファイル
- project-status.md

### 5.2 移行コマンド

```batch
REM project/ への移動（残りのファイル）
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\technology-selection.md c:\Users\Junichi\Desktop\xlsx-value-picker\docs\project\

REM spec/ への移動
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\cli-spec.md c:\Users\Junichi\Desktop\xlsx-value-picker\docs\spec\
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\rule-schema.json c:\Users\Junichi\Desktop\xlsx-value-picker\docs\spec\

REM guide/ への移動
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\mermaid-style-guide.md c:\Users\Junichi\Desktop\xlsx-value-picker\docs\guide\

REM design/ への移動
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\validation-design.md c:\Users\Junichi\Desktop\xlsx-value-picker\docs\design\
move c:\Users\Junichi\Desktop\xlsx-value-picker\docs\config-loader-design.md c:\Users\Junichi\Desktop\xlsx-value-picker\docs\design\
```

### 5.3 README.md の作成と参照更新

- ドキュメント全体の概要と索引を記載した README.md の作成
- プロジェクト現状文書（`project-status.md`）内のリンクを新しいディレクトリ構造に合わせて更新

### 5.4 実施後の検証項目

1. 各ファイルが適切なディレクトリに移動していることを確認
2. README.md の内容が適切であることを確認
3. project-status.md 内のリンクが正しく機能することを確認
4. 他の文書内のクロスリファレンスが正しく機能することを確認

## 6. 実施結果と今後の課題

### 6.1 実施結果

- ドキュメントのジャンル別整理の完了
- メインとなる文書ディレクトリ構造の確立
- 参照リンクの更新と検証

### 6.2 今後の課題

1. **ドキュメントのバージョン管理方法の確立**：文書の版管理と更新履歴の追跡方法
2. **ドキュメント間の関連性の視覚化**：文書間の依存関係や参照関係を図示する方法
3. **自動生成文書の管理**：API仕様書など自動生成される文書の配置と更新方法
4. **ユーザー向けドキュメントの整備**：チュートリアル、利用ガイドなどの追加
5. **国際化対応**：多言語対応時のディレクトリ構造の検討

## 7. まとめ

本ドキュメント再編作業を通じて、以下の成果を得ました：

1. タスク文書とプロジェクト文書の明確な分離
2. 文書のジャンル（カテゴリ）ごとの整理による探しやすさの向上
3. 文書間の関係性を視覚的に把握しやすいディレクトリ構造の確立
4. 新規文書作成時の配置基準の明確化

これにより、プロジェクトの継続的な発展をドキュメント面から支援する基盤が整いました。今後は、ドキュメント間の関連性の視覚化やユーザー向け文書の充実など、さらなる改善を進めていく予定です。

---

最終更新日: 2025年4月19日