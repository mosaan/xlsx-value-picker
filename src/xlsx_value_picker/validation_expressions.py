"""
バリデーション式モデル定義
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

# validation_common から必要なクラスをインポート
from .validation_common import ValidationContext, ValidationResult


class IExpression(ABC):
    """バリデーション式のインターフェース"""

    @abstractmethod
    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        ルール式の検証を行い結果を返す

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: 検証結果
        """
        pass


class Expression(BaseModel, IExpression):
    """バリデーション式の基底クラス"""

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        バリデーションを実行する（基底クラス実装）

        Note:
            この基底クラスの実装は常に有効（True）を返します。
            実際のバリデーションロジックは派生クラスで実装されます。

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        return ValidationResult(is_valid=True)


class UNDEFINED(BaseModel):
    """未指定値を表すマーカークラス"""

    some_internal_value: str = "THIS_IS_MARKER_VALUE"
    # ここでは内部的な値を持たせるが、実際には値は必要ない


_UNDEFINED = UNDEFINED()  # 一つしか値はいらないので生成してしまう。


class CompareExpressionParams(BaseModel):
    """比較式のパラメータを定義するクラス"""

    left: str | int | float | bool | None | UNDEFINED = _UNDEFINED
    left_field: str | UNDEFINED = _UNDEFINED
    operator: Literal["==", "!=", ">", ">=", "<", "<="]
    right: str | int | float | bool | None | UNDEFINED = _UNDEFINED
    right_field: str | UNDEFINED = _UNDEFINED

    @model_validator(mode="after")
    def validate_compare_params(self) -> CompareExpressionParams:
        """
        left または left_field、right または right_field のいずれかのみが指定されていることを確認する
        """
        if (isinstance(self.left, UNDEFINED) and isinstance(self.left_field, UNDEFINED)) or (
            isinstance(self.right, UNDEFINED) and isinstance(self.right_field, UNDEFINED)
        ):
            raise ValueError("left または left_field、right または right_field のいずれかを指定してください。")
        if (isinstance(self.left, UNDEFINED) and isinstance(self.left_field, UNDEFINED)) or (
            isinstance(self.right, UNDEFINED) and isinstance(self.right_field, UNDEFINED)
        ):
            raise ValueError("left と left_field、または right と right_field の両方を同時に指定することはできません。")
        return self

    def get_left_value(self, context: ValidationContext) -> str | int | float | bool | None:
        """
        left または left_field の値を取得する

        Returns:
            str | int | float | bool | None: left または left_field の値
        """
        return (
            self.left
            if not isinstance(self.left, UNDEFINED)
            else context.get_field_value(self.left_field)
            if not isinstance(self.left_field, UNDEFINED)
            else None
        )

    def get_right_value(self, context: ValidationContext) -> str | int | float | bool | None:
        """
        right または right_field の値を取得する

        Returns:
            str | int | float | bool | None: right または right_field の値
        """
        return (
            self.right
            if not isinstance(self.right, UNDEFINED)
            else context.get_field_value(self.right_field)
            if not isinstance(self.right_field, UNDEFINED)
            else None
        )


class CompareExpression(Expression):
    """比較式"""

    compare: CompareExpressionParams

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        比較式のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        left_field = self.compare.left_field
        right_field = self.compare.right_field
        operator = self.compare.operator
        right_value = self.compare.get_right_value(context)
        left_value = self.compare.get_left_value(context)

        # 比較ロジック
        is_valid = False
        try:
            match operator:
                case "==":
                    is_valid = left_value == right_value
                case "!=":
                    is_valid = left_value != right_value
                case ">":
                    # 型変換や型チェックを行い、比較可能な場合のみ比較を実行
                    if left_value is not None and right_value is not None and isinstance(left_value, type(right_value)):
                        is_valid = left_value > right_value
                case ">=":
                    if left_value is not None and right_value is not None and isinstance(left_value, type(right_value)):
                        is_valid = left_value >= right_value
                case "<":
                    if left_value is not None and right_value is not None and isinstance(left_value, type(right_value)):
                        is_valid = left_value < right_value
                case "<=":
                    if left_value is not None and right_value is not None and isinstance(left_value, type(right_value)):
                        is_valid = left_value <= right_value
                case _:
                    # 未知の演算子の場合
                    is_valid = False
        except (TypeError, ValueError):
            # 型が異なる場合や比較不能な場合は無効とする
            is_valid = False

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            fields = [v for v in [left_field, right_field] if not isinstance(v, UNDEFINED)]
            # エラーメッセージのフォーマット
            msg = error_message_template.format(
                left_field=left_field,
                left_value=left_value,
                right_field=right_field,
                right_value=right_value,
                operator=operator,
                field=", ".join(fields),
            )
            # left_fieldがstr型である場合のみlocationを取得
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=fields,
                error_locations=[
                    location if location is not None else "NOT_FOUND"
                    for location in {context.get_field_location(field) for field in fields}
                ],  # Add location
            )


class RequiredExpression(Expression):
    """必須項目式"""

    required: str | list[str]  # 単一フィールドまたはフィールドのリスト

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        必須項目のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # 単一フィールドの場合はリストに変換
        target_fields = [self.required] if isinstance(self.required, str) else self.required

        # すべてのフィールドが値を持っているかチェック
        invalid_fields = []
        for field in target_fields:
            value = context.get_field_value(field)
            if value is None or value == "":
                invalid_fields.append(field)

        if not invalid_fields:
            return ValidationResult(is_valid=True)
        else:
            # エラーフィールドとロケーションのリストを作成
            locations = [
                location
                for location in [context.get_field_location(field) for field in invalid_fields]
                if location is not None
            ]

            # フォーマットに対応するフィールド名（複数の場合はカンマ区切り）
            field_str = ", ".join(invalid_fields)
            # エラーメッセージのフォーマット
            msg = error_message_template.format(field=field_str)
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=invalid_fields,
                error_locations=locations,
            )


class IsEmptyExpression(Expression):
    """空値チェック式"""

    is_empty: str | list[str]  # 単一フィールドまたはフィールドのリスト

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        フィールドが空であることを検証する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # 単一フィールドの場合はリストに変換
        target_fields = [self.is_empty] if isinstance(self.is_empty, str) else self.is_empty

        # すべてのフィールドが空であるかチェック
        non_empty_fields = []
        for field in target_fields:
            value = context.get_field_value(field)
            if value is not None and value != "":
                non_empty_fields.append(field)

        if not non_empty_fields:
            return ValidationResult(is_valid=True)
        else:
            # エラーフィールドとロケーションのリストを作成
            locations = [
                location
                for location in [context.get_field_location(field) for field in non_empty_fields]
                if location is not None
            ]

            # フォーマットに対応するフィールド名（複数の場合はカンマ区切り）
            field_str = ", ".join(non_empty_fields)
            # エラーメッセージのフォーマット
            msg = error_message_template.format(field=field_str)
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=non_empty_fields,
                error_locations=locations,
            )


class RegexMatchExpression(Expression):
    """正規表現マッチ式"""

    regex_match: dict[str, str]

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        正規表現マッチのバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        target_field = self.regex_match["field"]
        pattern = self.regex_match["pattern"]
        value = context.get_field_value(target_field)

        # 値がNoneの場合は無効とする（正規表現は通常文字列に対して動作するため）
        if value is None:
            is_valid = False
        else:
            # 値が文字列でない場合は文字列に変換
            if not isinstance(value, str):
                value_str = str(value)
            else:
                value_str = value

            # 正規表現マッチ
            try:
                is_valid = bool(re.match(pattern, value_str))
            except re.error:
                # パターン自体が無効な場合は Pydantic バリデータで検出されるはずだが念のため
                is_valid = False

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(field=target_field, value=value, pattern=pattern)
            location = context.get_field_location(target_field)
            locations = [location] if location else []
            return ValidationResult(
                is_valid=False, error_message=msg, error_fields=[target_field], error_locations=locations
            )


class EnumExpression(Expression):
    """列挙型式"""

    enum: dict[str, Any]

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        列挙型のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        target_field = self.enum["field"]
        allowed_values = self.enum["values"]
        value = context.get_field_value(target_field)

        # 値がNoneの場合でも、allowed_valuesに含まれていれば有効とする
        # 必須チェックは別のルールで行う想定

        # 列挙値のチェック
        is_valid = value in allowed_values

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(
                field=target_field, value=value, allowed_values=", ".join(str(v) for v in allowed_values)
            )
            location = context.get_field_location(target_field)
            locations = [location] if location else []
            return ValidationResult(
                is_valid=False, error_message=msg, error_fields=[target_field], error_locations=locations
            )


class AllOfExpression(Expression):
    """全条件一致式"""

    all_of: list[ExpressionType]

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        全条件一致のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # すべての条件を評価
        results = [expr.validate_in(context, "") for expr in self.all_of]

        # すべての条件が有効であれば有効
        if all(r.is_valid for r in results):
            return ValidationResult(is_valid=True)
        else:
            # エラーがあった条件のフィールドと場所を集める
            all_error_fields: list[str] = []
            all_error_locations: list[str] = []
            for _, result in enumerate(results):
                if not result.is_valid:
                    if result.error_fields:
                        all_error_fields.extend(f for f in result.error_fields if f is not None)
                    # Add locations based on the fields from the failed sub-expression
                    if result.error_fields:
                        locations = [
                            context.get_field_location(f) for f in result.error_fields if context.get_field_location(f)
                        ]
                        all_error_locations.extend(loc for loc in locations if loc is not None)

            # 重複を排除
            unique_error_fields = sorted(set(all_error_fields))
            unique_error_locations = sorted({loc for loc in all_error_locations if loc is not None})

            # エラーメッセージのフォーマット
            msg = error_message_template

            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=unique_error_fields,
                error_locations=unique_error_locations,
            )


class AnyOfExpression(Expression):
    """いずれかの条件一致式"""

    any_of: list[ExpressionType]

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        いずれかの条件一致のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # すべての条件を評価
        results = [expr.validate_in(context, "") for expr in self.any_of]

        # いずれかの条件が有効であれば有効
        if any(r.is_valid for r in results):
            return ValidationResult(is_valid=True)
        else:
            # すべての条件が無効の場合、エラーフィールドと場所を集める
            all_error_fields: list[str] = []
            all_error_locations: list[str] = []
            for result in results:
                if not result.is_valid:
                    if result.error_fields:
                        all_error_fields.extend(result.error_fields)
                    if result.error_locations:
                        all_error_locations.extend(result.error_locations)

            # 重複を排除
            unique_error_fields = sorted(set(all_error_fields))
            unique_error_locations = sorted(set(all_error_locations))

            # エラーメッセージのフォーマット
            msg = error_message_template
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=unique_error_fields,
                error_locations=unique_error_locations,
            )


class NotExpression(Expression):
    """否定式"""

    not_: ExpressionType = Field(..., alias="not")

    def validate_in(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        否定式のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # 内部式を評価
        result = self.not_.validate_in(context, "")

        # 内部式の結果を否定
        if not result.is_valid:
            # 内部式が無効なら、この否定式は有効
            return ValidationResult(is_valid=True)
        else:
            # 内部式が有効なら、この否定式は無効
            # エラーメッセージのフォーマット
            msg = error_message_template
            # エラーフィールドと場所は、内部式の結果から取得するのではなく、
            # このNotExpression自体に関連付けるフィールドがないため空とする
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=[],  # Not式自体に紐づくフィールドはない
                error_locations=[],  # Not式自体に紐づく場所はない
            )


# すべての式型を含むUnion型
type ExpressionType = (
    CompareExpression
    | RequiredExpression
    | IsEmptyExpression
    | RegexMatchExpression
    | EnumExpression
    | AllOfExpression
    | AnyOfExpression
    | NotExpression
)


# 式型の検出と変換を行う関数
def detect_expression_type(data: dict[str, Any]) -> type[Expression]:
    """
    辞書データから適切な式の型を検出する

    Args:
        data: 式データ

    Returns:
        Expression: 適切な式型のクラス
    """
    if "compare" in data:
        return CompareExpression
    elif "required" in data:
        return RequiredExpression
    elif "is_empty" in data:
        return IsEmptyExpression
    elif "regex_match" in data:
        return RegexMatchExpression
    elif "enum" in data:
        return EnumExpression
    elif "all_of" in data:
        return AllOfExpression
    elif "any_of" in data:
        return AnyOfExpression
    elif "not" in data:
        return NotExpression
    else:
        # デフォルトまたは不明な型の場合はエラーを発生させる
        raise ValueError(f"不明な式型です: {data}")


def convert_expression(data: dict[str, Any] | Expression) -> Expression:
    """
    辞書データまたはExpression型のオブジェクトを適切なExpression派生クラスに変換する

    Args:
        data: 変換対象のデータ

    Returns:
        Expression: 変換後のExpression派生型オブジェクト
    """
    if isinstance(data, Expression):
        return data

    if isinstance(data, dict):
        expr_type = detect_expression_type(data)
        # model_validate を使用して Pydantic モデルに変換
        return expr_type.model_validate(data)

    raise ValueError(f"無効な式型です: {type(data)}")


# すべてのクラス定義後に循環参照を解決するために再構築
AllOfExpression.model_rebuild()
AnyOfExpression.model_rebuild()
NotExpression.model_rebuild()
