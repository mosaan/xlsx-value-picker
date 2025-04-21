# 作業計画: Workspace Problems の解消 (Pydantic/Validation Logic 関連)

## 1. 目的

mypy エラーのうち、Pydantic の `BaseModel` との互換性、前方参照 (`ForwardRef`) の解決、`Union` 型の処理、`None` を含む可能性のあるデータの処理、およびバリデーションロジック内での型非互換に関連する問題を解消し、バリデーション機能の信頼性を向上させる。

## 2. 対象ファイルと問題点

**mypy エラー (Pydantic/Validation Logic 関連):**

*   `src/xlsx_value_picker/validation_expressions.py`
    *   L36, L67, L129, L177, L234, L360, L433, L489: `validate`: スーパークラス `BaseModel` とのシグネチャ非互換
    *   L280-L282: `AllOfExpressionRef`, `AnyOfExpressionRef`, `NotExpressionRef`: 型としての使用が無効 (`ForwardRef` または `TypeAlias` が必要)
    *   L372: `expr.validate`: `Union` 型の要素 (`...Ref?`) に `validate` 属性がない (型ガードまたは共通インターフェースが必要)
    *   L397: `sorted`: `None` を含む可能性のあるリスト (`list[str | None]`) をソートしようとしている (`None` のフィルタリングが必要)
    *   L408: `error_locations`: `ValidationResult` への引数の型が非互換 (`list[str | None]` -> `list[str] | None`) (`None` のフィルタリングが必要)
    *   L445: `expr.validate`: `Union` 型の要素 (`...Ref?`) に `validate` 属性がない (型ガードまたは共通インターフェースが必要)
*   `src/xlsx_value_picker/config_loader.py`
    *   L74: `validate`: スーパークラス `BaseModel` との戻り値の型非互換 (`ValidationResult` vs `Rule`)
    *   L96: `set`: `None` を含む可能性のあるリスト (`list[str | None]`) を `set` に渡している (`None` のフィルタリングが必要)
*   `src/xlsx_value_picker/cli.py`
    *   L206: `formatter.write_output`: 代入時の型非互換 (`str` -> `ValidationResult`) (関数の戻り値または変数型の見直しが必要)

## 3. 作業方針

1.  **シグネチャ/戻り値の型の互換性修正:**
    *   `Signature of "validate" incompatible with supertype "BaseModel"` および `Return type "..." of "validate" incompatible with return type "..." in supertype "BaseModel"` について、`pydantic` の `BaseModel` の仕様（特にカスタムバリデーション `@validator` やルートバリデーション `@root_validator`）を確認し、`validate` メソッドのシグネチャと戻り値の型を互換性のあるように修正します。場合によってはメソッド名を変更するか、Pydantic のバリデーション機構を利用するようにリファクタリングします。
2.  **型定義と使用箇所の修正:**
    *   `Variable "..." is not valid as a type` について、`ForwardRef` や `TypeAlias` の使用、モデルクラス末尾での `update_forward_refs()` の呼び出しなどを検討し、循環参照を含む型ヒントが正しく解決されるように修正します。
    *   `Item ... has no attribute "validate"` について、型ガード (`isinstance`) を使用して特定の型の場合のみ `validate` を呼び出すか、`Union` 型に含まれる各クラスが共通の `validate` メソッドを持つようにインターフェースを定義または修正します。
    *   `Value of type variable "..." of "sorted" cannot be "..."` および `Argument 1 to "set" has incompatible type "..."; expected "..."` について、`sorted` や `set` に渡す前にリスト内包表記や `filter` を用いて `None` を除外する処理を追加します。
    *   `Argument "..." to "..." has incompatible type "..."; expected "..."` および `Incompatible types in assignment (expression has type "...", variable has type "...")` について、代入元と代入先の型が一致するように、関連する関数の戻り値の型アノテーションや変数の型アノテーション、または値の変換処理を修正します。

## 4. 作業手順

1.  上記の「対象ファイルと問題点」リストに基づき、各ファイルの問題点を個別に修正します。Pydantic の互換性問題から着手し、次に型解決、`None` 処理、型非互換の順に進めるのが効率的と考えられます。
2.  修正の区切りが良いタイミングで `uv run mypy .` を実行し、関連するエラーが解消されていることを確認します。
3.  `uv run pytest` を実行し、バリデーションロジックの変更によるリグレッションが発生していないことを確認します。
4.  すべての対象エラーが解消されたら、最終確認として再度 `uv run mypy .` および `uv run pytest` を実行します。

## 5. 成果物

*   Pydantic/Validation Logic 関連の mypy エラーが解消されたソースコード。
*   すべてのテストが成功する状態。