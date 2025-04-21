# 作業計画: Workspace Problems の解消 (Type Hinting 関連)

## 1. 目的

mypy エラーのうち、主に関数/メソッドの型アノテーション（引数、戻り値）、変数アノテーション、ジェネリック型のパラメータ、`Any` 型の返却、型付けされていない関数の呼び出しに関連する問題を解消し、コードの型安全性を向上させる。

## 2. 対象ファイルと問題点

**mypy エラー (Type Hinting 関連):**

*   `src/xlsx_value_picker/validation_common.py`
    *   L56: `__post_init__`: 戻り値の型アノテーション欠落 (`-> None`)
*   `src/xlsx_value_picker/validation_expressions.py`
    *   L60: `validate_compare`: 型アノテーション欠落 (引数 `v`, 戻り値)
    *   L167: `validate_regex`: 型アノテーション欠落 (引数 `v`, 戻り値)
    *   L227: `validate_enum`: 型アノテーション欠落 (引数 `v`, 戻り値)
    *   L346: `validate_all_of`: 型アノテーション欠落 (引数 `data`, 戻り値)
    *   L379: `all_error_fields`: 型アノテーション欠落 (`list[...]`)
    *   L419: `validate_any_of`: 型アノテーション欠落 (引数 `data`, 戻り値)
    *   L452: `all_error_fields`: 型アノテーション欠落 (`list[...]`)
    *   L453: `all_error_locations`: 型アノテーション欠落 (`list[...]`)
    *   L482: `validate_not`: 型アノテーション欠落 (引数 `data`, 戻り値)
*   `src/xlsx_value_picker/config_loader.py`
    *   L24: `parse_file`: `dict` の型パラメータ欠落 (`dict[str, Any]`)
    *   L44, L46: `yaml.safe_load`, `json.load`: `Any` を返している (期待値: `dict[str, Any]`)
    *   L67: `validate_expression`: 戻り値の型アノテーション欠落
    *   L110: `check_jinja2_template`: 戻り値の型アノテーション欠落 (`-> None`)
    *   L135: `validate_fields`: 型アノテーション欠落 (引数 `v`, 戻り値)
    *   L155: `__init__`: 戻り値の型アノテーション欠落 (`-> None`)
*   `src/xlsx_value_picker/cli.py`
    *   L93, L238: `ConfigLoader`: 型付けされていない関数の呼び出し ( `ConfigLoader` クラスに型アノテーションを追加する必要がある)

## 3. 作業方針

1.  **型アノテーションの追加・修正:**
    *   mypy エラー `missing a return type annotation`, `Function is missing a type annotation`, `Need type annotation for "..."`, `Missing type parameters for generic type "dict"` に対応します。適切な型ヒントを追加します。特に `__init__`, `__post_init__` は `-> None` を基本とします。クラスメソッド (`@classmethod`) の第一引数は `cls` とし、型は `Type[<ClassName>]` とします。
    *   `Returning Any from function declared to return "..."` については、可能であればより具体的な型 (`dict[str, Any]` など) を返すように修正します。難しい場合は `# type: ignore` で一時的に抑制することも検討しますが、極力避けます。
    *   `Call to untyped function "..." in typed context` については、呼び出し先の関数/クラス (`ConfigLoader`) に型アノテーションを追加します。

## 4. 作業手順

1.  上記の「対象ファイルと問題点」リストに基づき、各ファイルの問題点を個別に修正します。
2.  修正の区切りが良いタイミングで `uv run mypy .` を実行し、関連するエラーが解消されていることを確認します。
3.  `uv run pytest` を実行し、リグレッションが発生していないことを確認します。
4.  すべての対象エラーが解消されたら、最終確認として再度 `uv run mypy .` および `uv run pytest` を実行します。

## 5. 成果物

*   型アノテーション関連の mypy エラーが解消されたソースコード。
*   すべてのテストが成功する状態。