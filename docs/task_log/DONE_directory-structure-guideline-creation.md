# ドキュメント再編および関連ファイル更新計画

## 目的

1.  `docs/project/directory-structure.md` の内容を分割・再構成し、以下の3つのガイドラインを `docs/guide` 配下に新規作成する。
    *   ディレクトリ構造ガイドライン
    *   バージョン管理ガイドライン
    *   依存関係管理ガイドライン
2.  作成したガイドラインの内容を現状に合わせて修正する。
3.  プロジェクトルートの `README.md` および `docs/project-status.md` を、ドキュメント再編の結果と最新のプロジェクト状況を反映するように更新する。

これにより、各トピックに関する情報を整理し、保守性を向上させるとともに、プロジェクトのエントリーポイントとなるドキュメントを最新の状態に保つ。

## 背景

`docs/project/directory-structure.md` にはディレクトリ構造以外の情報も含まれ、内容も古くなっていたため、ガイドラインとして分割・再構成を行った。この変更に伴い、プロジェクトの顔であるルート `README.md` や、進捗を管理する `docs/project-status.md` も更新する必要がある。

## 作業方針

1.  **ガイドラインの分割・作成** (完了済み):
    *   `docs/guide/directory-structure-guideline.md` を作成。
    *   `docs/guide/version-control-guideline.md` を作成。
    *   `docs/guide/dependency-management-guideline.md` を作成。
    *   古い `docs/project/directory-structure.md` を削除。
2.  **ガイドライン内容の現状反映** (完了済み):
    *   `docs/guide/directory-structure-guideline.md` を更新 (docs配下構成、推奨構成例)。
    *   `docs/guide/version-control-guideline.md` を更新 (`git mv` ルール追加)。
    *   `docs/guide/dependency-management-guideline.md` を更新 (開発依存定義、`uv sync` コマンド)。
3.  **ルート README.md の更新**:
    *   現状のファイル内容を確認する。
    *   プロジェクト概要、インストール方法、使い方などが最新か確認する。
    *   ドキュメントへのリンク（特に旧 `directory-structure.md` への言及）を削除または修正する。
    *   `docs/README.md` へのリンクを追加または更新し、詳細なドキュメント構成はそちらを参照するように誘導する。
    *   修正内容をファイルに反映する。
4.  **docs/project-status.md の更新**:
    *   現状のファイル内容を確認する。
    *   「完了したタスク」セクションに、今回のドキュメント再編タスク（ガイドライン3点の作成・更新）が完了した旨を追記する。
    *   その他、古くなっている情報がないか確認する。
    *   修正内容をファイルに反映する。
5.  **内容確認**: 更新後の `README.md` および `docs/project-status.md` の内容を確認する。

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

-   `docs/guide/directory-structure-guideline.md` (更新済み)
-   `docs/guide/version-control-guideline.md` (更新済み)
-   `docs/guide/dependency-management-guideline.md` (更新済み)
-   `README.md` (更新)
-   `docs/project-status.md` (更新)

## 懸念事項

-   特になし

## 今後のステップ

-   この更新された計画についてユーザーの承認を得る。
-   承認後、`README.md` および `docs/project-status.md` の更新作業を開始する。
-   修正完了後、ユーザーに完了報告と承認を求める。
