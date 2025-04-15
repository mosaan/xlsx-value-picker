# activeContext.md

## 現在の作業フォーカス
- Memory Bankの初期作成
- プロジェクト要件・設計・技術文書の整備

## 直近の変更
- Memory Bankコアファイルの新規作成
- main.pyでExcelファイルパスを位置引数（第一引数）で指定できるように変更
- get_excel_values関数のpytestテスト（test_main.py）を作成し、正常動作を確認
- テストフレームワークpytestを開発用依存として`uv add pytest --dev`で導入
- テスト実行は`uv run pytest`で行う運用に統一

## 次のステップ
- main.pyの設計・実装開始
- サンプル設定ファイルの作成
- openpyxl, pyyamlのuv addによる導入
- main.pyのさらなる堅牢化（例: エラー処理やYAML出力対応）
- ドキュメント（READMEやサンプル）整備
- 必要に応じて追加テストやCI連携

## アクティブな意思決定・考慮事項
- openpyxlのdata_onlyモードを利用
- uv addによるパッケージ管理徹底
- Memory Bankドキュメント駆動開発を徹底
- テストはpytest＋uv run pytestで実施
- Excel式セルの値取得はopenpyxlの仕様（保存時のみ値が埋まる）に依存

## 学び・インサイト
- Memory Bankを活用したドキュメント駆動開発の重要性
- uvのdev依存・テスト実行フローの明文化で開発効率・再現性が向上
