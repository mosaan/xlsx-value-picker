# ドキュメント再編計画：ディレクトリ構造、バージョン管理、依存関係管理

## 目的

`docs/project/directory-structure.md` の内容を分割・再構成し、以下の3つのガイドラインを `docs/guide` 配下に新規作成する。また、作成したガイドラインの内容を現状に合わせて修正する。

1.  ディレクトリ構造ガイドライン
2.  バージョン管理ガイドライン
3.  依存関係管理ガイドライン

これにより、各トピックに関する情報を整理し、保守性を向上させる。

## 背景

現在の `docs/project/directory-structure.md` は、ディレクトリ構造の説明に加え、バージョン管理方針や依存関係管理に関する情報も含まれている。これらの情報はそれぞれ独立したガイドラインとして管理する方が適切である。また、ディレクトリ構造に関する記述も現状を反映していない部分があるため、見直しが必要である。

## 作業方針

1.  **新規ガイドライン文書作成** (完了済み):
    *   `docs/guide/directory-structure-guideline.md` を作成。
    *   `docs/guide/version-control-guideline.md` を作成。
    *   `docs/guide/dependency-management-guideline.md` を作成。
2.  **ガイドライン内容の定義** (完了済み):
    *   **ディレクトリ構造ガイドライン (`docs/guide/directory-structure-guideline.md`)**:
        *   プロジェクトの主要なディレクトリ (`src`, `test`, `docs` など) の役割と、ファイル配置に関する基本的な考え方やルールを記述。
        *   既存の `docs/project/directory-structure.md` から、「推奨するプロジェクト拡張時のディレクトリ構成」と「ファイル命名規則」のセクションを移行。
        *   既存文書に含まれる現状のディレクトリ構造の具体的な説明は削除。
    *   **バージョン管理ガイドライン (`docs/guide/version-control-guideline.md`)**:
        *   既存の `docs/project/directory-structure.md` から、「バージョン管理方針」セクションの内容を移行。
        *   コミット済みのファイルを移動または名前変更する際は `git mv` を使用するというルールを追加。
    *   **依存関係管理ガイドライン (`docs/guide/dependency-management-guideline.md`)**:
        *   既存の `docs/project/directory-structure.md` から、「依存関係管理」セクションの内容を移行。
3.  **既存文書の削除** (完了済み): 古い `docs/project/directory-structure.md` を削除。
4.  **ガイドライン内容の現状反映**:
    *   **`docs/guide/directory-structure-guideline.md` の修正**: (実施中)
        *   「基本的なディレクトリ構成と考え方」セクションの `docs/` 配下の説明を、現在の構成 (`design/`, `guide/`, `project/`, `spec/`, `task_log/`) を反映するように更新する。
        *   「推奨するプロジェクト拡張時のディレクトリ構成」セクションの内容を見直し、"...（既存のディレクトリ）" のような曖昧な表現を削除し、現在の主要なディレクトリ構造を明記した上で、拡張例を示すように更新する。
    *   **`docs/guide/dependency-management-guideline.md` の修正**: (実施中)
        *   開発用依存関係の定義場所を `[project.optional-dependencies]` から `[dependency-groups]` に修正する。
        *   `pyproject.toml` のコード例を `[dependency-groups]` を使う形に修正する。
        *   ロックファイル更新コマンドの例と注意書きを `uv sync` を中心とした記述に調整する。

## 作業結果サマリ

- `docs/project/directory-structure.md` の内容を分割し、以下の3つのガイドラインを `docs/guide` 配下に新規作成した。
    - `directory-structure-guideline.md`
    - `version-control-guideline.md`
    - `dependency-management-guideline.md`
- 各ガイドラインの内容を現状のプロジェクト構成に合わせて修正した。
    - ディレクトリ構造ガイドライン: `docs` 配下の構成、推奨構成例を更新。
    - バージョン管理ガイドライン: `git mv` の利用ルールを追加。
    - 依存関係管理ガイドライン: 開発依存の定義場所 (`[dependency-groups]`)、ロックファイル更新コマンド (`uv sync`) を修正。
- ユーザーにより、依存関係管理ガイドラインにUVコマンド利用の推奨に関する情報が追記された。
- 古い `docs/project/directory-structure.md` を削除した。

## 成果物

-   `docs/guide/directory-structure-guideline.md` (更新)
-   `docs/guide/version-control-guideline.md` (変更なし)
-   `docs/guide/dependency-management-guideline.md` (更新)

## 懸念事項

-   特になし

## 今後のステップ

-   ガイドラインファイルの修正作業を実行する。
-   修正完了後、ユーザーに完了報告と承認を求める。
-   (完了)
