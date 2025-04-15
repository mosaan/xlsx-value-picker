# activeContext.md

## 現在の作業フォーカス
- 配布・開発・テスト・CI/CDを一貫した構成にリファクタリング
- main.pyをsrc/xslx_value_picker/cli.pyへ移動し、__main__.py追加でパッケージ化
- pyproject.tomlで[project.scripts]にCLIコマンド（xslx-value-picker）を登録
- READMEにuv/pipインストール例、uv run xslx-value-picker実行例、YAML出力例を追記
- .gitignore強化、LICENSE（MIT）追加、test/配下にテスト・サンプル整理
- CI（GitHub Actions）でpytest自動実行を追加
- テストのサブプロセス呼び出しはuv run python -m xslx_value_picker ...に統一し、PYTHONPATH=srcを付与することで仮想環境へインストールせずに開発中コードをテスト可能にした
- すべてのテストがパスすることを確認

## 直近の変更
- main.pyのYAML出力対応・堅牢化
- src/ディレクトリ化・パッケージ化・エントリポイント整理
- pyproject.tomlの配布用設定・CLIスクリプト登録
- README・.gitignore・LICENSE・CI・テスト整理
- テストはPYTHONPATH=srcでuv run python -m ...方式で安定動作

## 次のステップ
- ドキュメント・サンプルのさらなる充実
- ユーザーからの追加要望・フィードバック対応

## アクティブな意思決定・考慮事項
- src/xslx_value_picker/配下に実装を集約し、パッケージとして配布可能な構成
- CLIコマンドは[project.scripts]で登録し、uv/pipインストール後にxslx-value-pickerで実行可能
- テストはPYTHONPATH=srcでsrc配下の最新コードを直接参照
- サブプロセスでのCLIテストもuv run python -m ... + PYTHONPATH指定で仮想環境汚染なし
- CI/CDはGitHub Actionsでpytestを自動実行

## 学び・インサイト
- 仮想環境にインストールせずPYTHONPATHでsrc配下を参照することで、開発効率・テスト独立性・CI一貫性が向上
- ドキュメント・実装・テストの一貫性維持が重要
