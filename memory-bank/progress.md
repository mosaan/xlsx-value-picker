# progress.md

## 現状動作するもの
- Memory Bankのコアファイル作成
- main.pyでExcelファイルパスを位置引数で指定可能
- get_excel_values関数のpytestテスト（test_main.py）が正常動作

## 残作業
- main.pyの実装
- main.pyの堅牢化・YAML出力対応
- サンプル設定ファイルの作成
- 必要パッケージの導入
- ドキュメント整備
- 追加テストやCI連携

## 現在のステータス
- ドキュメント整備フェーズ

## 既知の課題
- Excelファイルの計算値取得はopenpyxlの制約に依存
- openpyxlの仕様上、式セルの値はExcelで保存時のみ取得可能

## プロジェクト決定事項の変遷
- uv addによるパッケージ管理を徹底する方針に決定
- テストフレームワークpytestを`uv add pytest --dev`で導入し、`uv run pytest`で実行する運用に決定
