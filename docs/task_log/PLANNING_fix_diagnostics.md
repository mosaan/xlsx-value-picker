# 作業計画: Workspace Problems の解消

## 1. 目的

`workspace_diagnostics` で報告されている mypy エラーおよび Ruff 警告を解消し、コードの品質と信頼性を向上させる。

## 2. 対象ファイルと問題点

以下に、報告されている問題点と対象ファイルをリストアップします。

**mypy エラー:**

*   `src/xlsx_value_picker/validation_common.py`
    *   L56: `__post_init__`: 戻り値の型アノテーション欠落
*   `src/xlsx_value_picker/validation_expressions.py`
    *   L36, L67, L129, L177, L234, L360, L433, L489: `validate`: スーパークラス `BaseModel` とのシグネチャ非互換
    *   L60: `validate_compare`: 型アノテーション欠落
    *   L167: `validate_regex`: 型アノテーション欠落
    *   L227: `validate_enum`: 型アノテーション欠落
    *   L280-L282: `AllOfExpressionRef`, `AnyOfExpressionRef`, `NotExpressionRef`: 型としての使用が無効
    *   L346: `validate_all_of`: 型アノテーション欠落
    *   L372: `expr.validate`: `Union` 型の要素に `validate` 属性がない
    *   L379: `all_error_fields`: 型アノテーション欠落
    *   L397: `sorted`: `None` を含む可能性のあるリストをソートしようとしている
    *   L408: `error_locations`: `ValidationResult` への引数の型が非互換 (`list[str | None]` -> `list[str] | None`)
    *   L419: `validate_any_of`: 型アノテーション欠落
    *   L445: `expr.validate`: `Union` 型の要素に `validate` 属性がない
    *   L452: `all_error_fields`: 型アノテーション欠落
    *   L453: `all_error_locations`: 型アノテーション欠落
    *   L482: `validate_not`: 型アノテーション欠落
*   `src/xlsx_value_picker/config_loader.py`
    *   L24: `parse_file`: `dict` の型パラメータ欠落
    *   L44, L46: `yaml.safe_load`, `json.load`: `Any` を返している (期待値: `dict[Any, Any]`)
    *   L67: `validate_expression`: 戻り値の型アノテーション欠落
    *   L74: `validate`: スーパークラス `BaseModel` との戻り値の型非互換
    *   L96: `set`: `None` を含む可能性のあるリストを `set` に渡している
    *   L110: `check_jinja2_template`: 戻り値の型アノテーション欠落
    *   L135: `validate_fields`: 型アノテーション欠落
    *   L155: `__init__`: 戻り値の型アノテーション欠落
*   `src/xlsx_value_picker/cli.py`
    *   L93, L238: `ConfigLoader`: 型付けされていない関数の呼び出し
    *   L206: `formatter.write_output`: 代入時の型非互換 (`str` -> `ValidationResult`)
*   `src/xlsx_value_picker/excel_processor.py`
    *   L28: `__enter__`: 戻り値の型アノテーション欠落
    *   L34: `openpyxl.load_workbook`: 代入時の型非互換 (`Workbook` -> `None`)
    *   L43: `__exit__`: 型アノテーション欠落
    *   L45: `close`: 型付けされていない関数の呼び出し
    *   L113: `close`: 戻り値の型アノテーション欠落

**Ruff 警告:**

*   `src/xlsx_value_picker/config_loader.py`
    *   L7: `pathlib.Path`: 未使用のインポート
    *   L8: `typing.ClassVar`: 未使用のインポート
*   `test/test_cli_validation.py`
    *   L414: ファイル末尾の改行欠落
*   `src/xlsx_value_picker/cli.py`
    *   L1: インポートブロックのソート/フォーマット未実施
    *   L21: 行長超過 (124 > 120)
*   `test/test_config_loader.py`
    *   L16: インポートブロックのソート/フォーマット未実施
*   `test/test_cli_basic.py`
    *   L343: ファイル末尾の改行欠落
*   `test/test_cli_errors.py`
    *   L294: ファイル末尾の改行欠落
*   `test/test_cli_options.py`
    *   L342: ファイル末尾の改行欠落

## 3. 作業方針

以下の手順で修正作業を進めます。

1.  **型アノテーションの追加・修正:**
    *   mypy エラー `missing a return type annotation`, `Function is missing a type annotation`, `Need type annotation for "..."`, `Missing type parameters for generic type "dict"` に対応します。適切な型ヒントを追加します。特に `__init__`, `__post_init__`, `__enter__`, `__exit__` は `-> None` を基本とします。
    *   `Returning Any from function declared to return "..."` については、可能であればより具体的な型を返すように修正します。難しい場合は `# type: ignore` で一時的に抑制することも検討しますが、極力避けます。
    *   `Call to untyped function "..." in typed context` については、呼び出し先の関数に型アノテーションを追加します。
2.  **シグネチャ/戻り値の型の互換性修正:**
    *   `Signature of "validate" incompatible with supertype "BaseModel"` および `Return type "..." of "validate" incompatible with return type "..." in supertype "BaseModel"` について、`pydantic` の `BaseModel` の仕様を確認し、`validate` メソッドのシグネチャと戻り値の型を互換性のあるように修正します。`@validator` デコレータの使用などを検討します。
3.  **型定義と使用箇所の修正:**
    *   `Variable "..." is not valid as a type` について、`ForwardRef` や `TypeAlias` の使用、`update_forward_refs()` の呼び出しなどを検討し、型ヒントが正しく解決されるように修正します。
    *   `Item ... has no attribute "validate"` について、型ガード (`isinstance`) を使用するか、`Union` 型の定義を見直して共通インターフェースを導入します。
    *   `Value of type variable "..." of "sorted" cannot be "..."` および `Argument 1 to "set" has incompatible type "..."; expected "..."` について、`sorted` や `set` に渡す前に `None` をフィルタリングする処理を追加します。
    *   `Argument "..." to "..." has incompatible type "..."; expected "..."` および `Incompatible types in assignment (expression has type "...", variable has type "...")` について、代入元と代入先の型が一致するように、型アノテーションや値の変換処理を修正します。
4.  **Ruff 警告の修正:**
    *   未使用のインポート (`imported but unused`) を削除します。
    *   ファイル末尾に改行を追加します (`No newline at end of file`)。
    *   インポートブロックを `ruff format` または手動で整形します (`Import block is un-sorted or un-formatted`)。
    *   長すぎる行を適切に分割します (`Line too long`)。
5.  **テストの実行:**
    *   各ファイルの修正後、またはある程度のまとまりごとに `pytest` を実行し、すべてのテストが成功することを確認します。

## 4. 作業手順

1.  上記の「作業方針」に基づき、各ファイルの問題点を個別に修正します。
2.  修正の区切りが良いタイミングで `mypy .` および `ruff check .` を実行し、エラー/警告が解消されていることを確認します。
3.  `pytest` を実行し、リグレッションが発生していないことを確認します。
4.  すべての問題が解消されたら、最終確認として再度 `mypy .`, `ruff check .`, `pytest` を実行します。

## 5. 成果物

*   修正済みのソースコードおよびテストコード。
*   すべての mypy エラーおよび Ruff 警告が解消された状態。
*   すべてのテストが成功する状態。