"""
バリデーション式モデル定義
"""

import re
from abc import ABC, abstractmethod
from typing import Any, ForwardRef

from pydantic import BaseModel, Field, field_validator, model_validator

# validation_common から必要なクラスをインポート
from .validation_common import ValidationContext, ValidationResult


class IExpression(ABC):
    """バリデーション式のインターフェース"""

    @abstractmethod
    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
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

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
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


class CompareExpression(Expression):
    """比較式"""

    compare: dict[str, Any]

    @field_validator("compare")
    def validate_compare(cls, v):
        if not all(k in v for k in ["left", "operator", "right"]):
            raise ValueError("compare式には 'left', 'operator', 'right' が必要です")
        if v["operator"] not in ["==", "!=", ">", ">=", "<", "<="]:
            raise ValueError(f"無効な演算子です: {v['operator']}")
        return v

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        比較式のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        left_field = self.compare["left"]
        operator = self.compare["operator"]
        right_value = self.compare["right"]
        left_value = context.get_field_value(left_field)

        # 比較ロジック
        is_valid = False
        try:
            if operator == "==":
                is_valid = left_value == right_value
            elif operator == "!=":
                is_valid = left_value != right_value
            elif operator == ">":
                is_valid = left_value > right_value
            elif operator == ">=":
                is_valid = left_value >= right_value
            elif operator == "<":
                is_valid = left_value < right_value
            elif operator == "<=":
                is_valid = left_value <= right_value
        except (TypeError, ValueError):
            # 型が異なる場合や比較不能な場合は無効とする
            is_valid = False

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(
                left_field=left_field,
                left_value=left_value,
                operator=operator,
                right_value=right_value,
                field=left_field,  # 'field'も追加（テンプレートで使用される可能性あり）
            )
            location = context.get_field_location(left_field)
            locations = [location] if location else []
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=[left_field],
                error_locations=locations,  # Add location
            )


class RequiredExpression(Expression):
    """必須項目式"""

    field: str
    required: bool = True

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        必須項目のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        target_field = self.field
        value = context.get_field_value(target_field)

        # required=Trueの場合のみチェック
        is_valid = not self.required or (value is not None and value != "")

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(field=target_field)
            location = context.get_field_location(target_field)  # Get location
            locations = [location] if location else []  # Create list
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=[target_field],
                error_locations=locations,  # Add location
            )


class RegexMatchExpression(Expression):
    """正規表現マッチ式"""

    regex_match: dict[str, str]

    @field_validator("regex_match")
    def validate_regex(cls, v):
        if not all(k in v for k in ["field", "pattern"]):
            raise ValueError("regex_match式には 'field', 'pattern' が必要です")
        # 正規表現の有効性を検証
        try:
            re.compile(v["pattern"])
        except re.error:
            raise ValueError(f"無効な正規表現です: {v['pattern']}")
        return v

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
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

    @field_validator("enum")
    def validate_enum(cls, v):
        if not all(k in v for k in ["field", "values"]):
            raise ValueError("enum式には 'field', 'values' が必要です")
        if not isinstance(v["values"], list) or len(v["values"]) == 0:
            raise ValueError("enum.valuesは少なくとも1つの要素を持つリストである必要があります")
        return v

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
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


# 前方参照で循環参照を解決
AllOfExpressionRef = ForwardRef("AllOfExpression")
AnyOfExpressionRef = ForwardRef("AnyOfExpression")
NotExpressionRef = ForwardRef("NotExpression")

# すべての式型を含むUnion型
type ExpressionType = (
    CompareExpression
    | RequiredExpression
    | RegexMatchExpression
    | EnumExpression
    | AllOfExpressionRef
    | AnyOfExpressionRef
    | NotExpressionRef
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
    elif "field" in data and "required" in data:
        return RequiredExpression
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
        # デフォルトまたは不明な型の場合、基底クラスを返すかエラーを発生させるか検討
        # ここでは基底クラスを返すが、より厳密にするならValueErrorが良いかもしれない
        # raise ValueError(f"不明な式型です: {data}")
        return Expression  # または適切なデフォルト処理


def convert_expression(data: dict[str, Any] | Expression) -> ExpressionType:
    """
    辞書データまたはExpression型のオブジェクトを適切なExpression派生クラスに変換する

    Args:
        data: 変換対象のデータ

    Returns:
        ExpressionType: 変換後のExpression派生型オブジェクト
    """
    if isinstance(data, Expression):
        return data

    if isinstance(data, dict):
        expr_type = detect_expression_type(data)
        # model_validate を使用して Pydantic モデルに変換
        return expr_type.model_validate(data)

    raise ValueError(f"無効な式型です: {type(data)}")


class AllOfExpression(Expression):
    """全条件一致式"""

    all_of: list[ExpressionType]

    @model_validator(mode="before")
    @classmethod
    def validate_all_of(cls, data):
        """すべての条件式を適切な型に変換する"""
        if isinstance(data, dict) and "all_of" in data:
            if not data["all_of"] or len(data["all_of"]) == 0:
                raise ValueError("all_of式には少なくとも1つの条件が必要です")

            # リスト内の各要素を適切な式型に変換
            converted = []
            for item in data["all_of"]:
                converted.append(convert_expression(item))
            data["all_of"] = converted

        return data

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        全条件一致のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # すべての条件を評価
        results = [expr.validate(context, "") for expr in self.all_of]  # Use a neutral template for sub-expressions

        # すべての条件が有効であれば有効
        if all(r.is_valid for r in results):
            return ValidationResult(is_valid=True)
        else:
            # エラーがあった条件のフィールドと場所を集める
            all_error_fields = []
            all_error_locations = []
            for _, result in enumerate(results):
                if not result.is_valid:
                    if result.error_fields:
                        all_error_fields.extend(result.error_fields)
                    # Add locations based on the fields from the failed sub-expression
                    if result.error_fields:
                        locations = [
                            context.get_field_location(f) for f in result.error_fields if context.get_field_location(f)
                        ]
                        all_error_locations.extend(locations)
                    # Optionally collect sub-messages
                    # if result.error_message:
                    #    sub_error_messages.append(f"Condition {i+1} failed: {result.error_message}")

            # 重複を排除
            unique_error_fields = sorted(set(all_error_fields))
            unique_error_locations = sorted(set(all_error_locations))

            # エラーメッセージのフォーマット (Main message + optional sub-messages)
            msg = error_message_template
            # if sub_error_messages:
            #    msg += " (" + "; ".join(sub_error_messages) + ")"

            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=unique_error_fields,
                error_locations=unique_error_locations,
            )


class AnyOfExpression(Expression):
    """いずれかの条件一致式"""

    any_of: list[ExpressionType]

    @model_validator(mode="before")
    @classmethod
    def validate_any_of(cls, data):
        """いずれかの条件式を適切な型に変換する"""
        if isinstance(data, dict) and "any_of" in data:
            if not data["any_of"] or len(data["any_of"]) == 0:
                raise ValueError("any_of式には少なくとも1つの条件が必要です")

            # リスト内の各要素を適切な式型に変換
            converted = []
            for item in data["any_of"]:
                converted.append(convert_expression(item))
            data["any_of"] = converted

        return data

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        いずれかの条件一致のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # すべての条件を評価
        results = [expr.validate(context, "") for expr in self.any_of]

        # いずれかの条件が有効であれば有効
        if any(r.is_valid for r in results):
            return ValidationResult(is_valid=True)
        else:
            # すべての条件が無効の場合、エラーフィールドと場所を集める
            all_error_fields = []
            all_error_locations = []
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

    @model_validator(mode="before")
    @classmethod
    def validate_not(cls, data):
        """否定対象の式を適切な型に変換する"""
        if isinstance(data, dict) and "not" in data:
            data["not"] = convert_expression(data["not"])

        return data

    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        否定式のバリデーションを実行する

        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート

        Returns:
            ValidationResult: バリデーション結果
        """
        # 内部式を評価
        result = self.not_.validate(context, "")

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
            # (もし特定のフィールドに対する否定なら、そのフィールドを別途指定する設計が必要)
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=[],  # Not式自体に紐づくフィールドはない
                error_locations=[],  # Not式自体に紐づく場所はない
            )


# 前方参照の解決
AllOfExpression.model_rebuild()
AnyOfExpression.model_rebuild()
NotExpression.model_rebuild()
