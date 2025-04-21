# 作業計画: Workspace Problems の解消 (Excel Processor 関連)

## 1. 目的

`src/xlsx_value_picker/excel_processor.py` における mypy エラー（型アノテーション欠落、型非互換、型付けされていない関数の呼び出し）を解消し、Excel ファイル処理部分の信頼性を向上させる。

## 2. 対象ファイルと問題点

**mypy エラー (Excel Processor 関連):**

*   `src/xlsx_value_picker/excel_processor.py`
    *   L28: `__enter__`: 戻り値の型アノテーション欠落 (`-> Self` または `-> ExcelProcessor`)
    *   L34: `openpyxl.load_workbook`: 代入時の型非互換 (`Workbook` -> `None`) (`self.workbook` の型アノテーション修正が必要)
    *   L43: `__exit__`: 型アノテーション欠落 (引数 `exc_type`, `exc_val`, `exc_tb` および戻り値 `-> None | bool`)
    *   L45: `close`: 型付けされていない関数の呼び出し (`close` メソッドに型アノテーションを追加する必要がある)
    *   L113: `close`: 戻り値の型アノテーション欠落 (`-> None`)

## 3. 作業方針

1.  **型アノテーションの追加・修正:**
    *   `__enter__` メソッドには、コンテキストマネージャ自身を返すことを示す `-> Self` (Python 3.11+) または `-> "ExcelProcessor"` (それ以前) の戻り値型アノテーションを追加します。
    *   `__exit__` メソッドには、標準的な引数 (`exc_type: Type[BaseException] | None`, `exc_val: BaseException | None`, `exc_tb: TracebackType | None`) と戻り値 (`-> None | bool`) の型アノテーションを追加します。
    *   `close` メソッドには `-> None` の戻り値型アノテーションを追加します。これにより `Call to untyped function "close"` エラーも解消されます。
2.  **型非互換の修正:**
    *   `Incompatible types in assignment (expression has type "Workbook", variable has type "None")` エラーに対応します。`ExcelProcessor` クラスの `self.workbook` 属性の型アノテーションを `openpyxl.workbook.workbook.Workbook | None` のように修正します (初期値が `None` のため `Optional` または `Union[..., None]` が必要)。

## 4. 作業手順

1.  `src/xlsx_value_picker/excel_processor.py` を開き、上記の「作業方針」に従って修正を行います。
2.  修正後、`uv run mypy src/xlsx_value_picker/excel_processor.py` を実行し、関連するエラーが解消されていることを確認します。
3.  `uv run pytest test/test_excel_processor.py` を実行し、リグレッションが発生していないことを確認します。

## 5. 成果物

*   `excel_processor.py` における mypy エラーが解消されたソースコード。
*   関連するテストが成功する状態。