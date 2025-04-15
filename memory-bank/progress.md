# progress.md

## 現状動作するもの
- Memory Bankのコアファイル作成
- main.pyでExcelファイルパスを位置引数で指定可能
- get_excel_values関数のpytestテスト（test_main.py）が正常動作
- シート指定で`*N`（例: `*2`）と記載した場合、左からN番目（1始まり）のシートを選択できる機能が動作
- main.pyで`--output`未指定時は標準出力にJSON出力される仕様が動作
- READMEのコマンド例・説明も標準出力対応に修正済み
- YAML出力対応は未実装（現状はJSONのみ）。今後のTODO。
- main.pyのコマンドライン引数仕様（--output, --include-empty-range-row等）はREADME・Memory Bankに明記済み。
- エラー処理（ファイル未指定・未存在・不正なシート/セル指定時の明示的なエラー出力と終了）はmain.pyで実装済み。

## 残作業
- main.pyの堅牢化・YAML出力対応
- サンプル設定ファイルの作成
- 必要パッケージの導入
- ドキュメント整備
- 追加テストやCI連携
- `*N`指定のテストケース追加（test_main.py）
- テスト全件パスを確認

## 現在のステータス
- ドキュメント整備フェーズ
- `*N`シート順指定機能の実装・動作確認済み
- 標準出力対応のCLIツールとして柔軟性向上

## 既知の課題
- Excelファイルの計算値取得はopenpyxlの制約に依存
- openpyxlの仕様上、式セルの値はExcelで保存時のみ取得可能

## プロジェクト決定事項の変遷
- uv addによるパッケージ管理を徹底する方針に決定
- テストフレームワークpytestを`uv add pytest --dev`で導入し、`uv run pytest`で実行する運用に決定
- main.pyの`--output`未指定時は標準出力に出力する仕様に変更し、READMEも反映
- Excelテーブル（ListObject）機能対応はopenpyxlを採用する方針に決定
