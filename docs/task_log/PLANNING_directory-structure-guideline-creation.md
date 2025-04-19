# ドキュメント再編計画：ディレクトリ構造、バージョン管理、依存関係管理

## 目的

`docs/project/directory-structure.md` の内容を分割・再構成し、以下の3つのガイドラインを `docs/guide` 配下に新規作成する。

1.  ディレクトリ構造ガイドライン
2.  バージョン管理ガイドライン
3.  依存関係管理ガイドライン

これにより、各トピックに関する情報を整理し、保守性を向上させる。

## 背景

現在の `docs/project/directory-structure.md` は、ディレクトリ構造の説明に加え、バージョン管理方針や依存関係管理に関する情報も含まれている。これらの情報はそれぞれ独立したガイドラインとして管理する方が適切である。また、ディレクトリ構造に関する記述も現状を反映していない部分があるため、見直しが必要である。

## 作業方針

1.  **新規ガイドライン文書作成**:
    *   `docs/guide/directory-structure-guideline.md` を作成する。
    *   `docs/guide/version-control-guideline.md` を作成する。
    *   `docs/guide/dependency-management-guideline.md` を作成する。
2.  **ガイドライン内容の定義**:
    *   **ディレクトリ構造ガイドライン (`docs/guide/directory-structure-guideline.md`)**:
        *   プロジェクトの主要なディレクトリ (`src`, `test`, `docs` など) の役割と、ファイル配置に関する基本的な考え方やルールを記述する。
        *   既存の `docs/project/directory-structure.md` から、「推奨するプロジェクト拡張時のディレクトリ構成」と「ファイル命名規則」のセクションを移行し、内容を現状に合わせて見直す。
        *   既存文書に含まれる現状のディレクトリ構造の具体的な説明（特に更新が追いついていない部分）は削除する。
    *   **バージョン管理ガイドライン (`docs/guide/version-control-guideline.md`)**:
        *   既存の `docs/project/directory-structure.md` から、「バージョン管理方針」セクションの内容を移行する。
    *   **依存関係管理ガイドライン (`docs/guide/dependency-management-guideline.md`)**:
        *   既存の `docs/project/directory-structure.md` から、「依存関係管理」セクションの内容を移行する。
3.  **既存文書の削除**: 新しいガイドライン文書の作成後、古い `docs/project/directory-structure.md` を削除する。

## 成果物

-   `docs/guide/directory-structure-guideline.md` (新規作成)
-   `docs/guide/version-control-guideline.md` (新規作成)
-   `docs/guide/dependency-management-guideline.md` (新規作成)

## 懸念事項

-   特になし

## 今後のステップ

-   この計画についてユーザーの承認を得る。
-   承認後、作業を開始する。
