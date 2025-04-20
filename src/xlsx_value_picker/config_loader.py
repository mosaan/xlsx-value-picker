"""
JSONスキーマに基づく設定データ読み込み機能
"""

import json
import os
import re
from typing import Any, ClassVar, ForwardRef

import jsonschema
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from .validation_common import IExpression, ValidationContext, ValidationResult


class ConfigValidationError(Exception):
    """設定ファイルのバリデーションエラー"""

    pass


class ConfigParser:
    @staticmethod
    def parse_file(file_path: str) -> dict:
        """
        設定ファイル（YAMLまたはJSON）を読み込み、Pythonオブジェクトに変換する

        Args:
            file_path: 設定ファイルのパス

        Returns:
            dict: 設定データ

        Raises:
            ValueError: サポートされていないファイル形式の場合
            FileNotFoundError: ファイルが存在しない場合
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                return yaml.safe_load(f)
            elif file_path.endswith(".json"):
                return json.load(f)
            else:
                raise ValueError(f"サポートされていないファイル形式です: {file_path}")


class SchemaValidator:
    """JSONスキーマバリデーター"""

    def __init__(self, schema_path: str):
        """
        スキーマファイルを読み込む

        Args:
            schema_path: JSONスキーマファイルのパス
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"スキーマファイルが見つかりません: {schema_path}")

        with open(schema_path, encoding="utf-8") as f:
            self.schema = json.load(f)

    def validate(self, config_data: dict) -> None:
        """
        設定データをスキーマに基づいて検証する

        Args:
            config_data: 検証対象の設定データ

        Raises:
            ConfigValidationError: バリデーションに失敗した場合
        """
        try:
            jsonschema.validate(instance=config_data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            path = ".".join(str(p) for p in e.path) if e.path else "root"
            raise ConfigValidationError(f"設定ファイルの検証に失敗しました: {path} - {e.message}")


# 以下はバリデーション式のモデル定義


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
            return ValidationResult(is_valid=False, error_message=msg, error_fields=[left_field])


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
            return ValidationResult(is_valid=False, error_message=msg, error_fields=[target_field])


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

        # 値が文字列でない場合は文字列に変換
        if value is not None and not isinstance(value, str):
            value = str(value)

        # 値がNoneまたは空文字列の場合は検証をスキップ（有効とする）
        # 必須チェックは別のルールで行う想定
        if value is None or value == "":
            return ValidationResult(is_valid=True)

        # 正規表現マッチ
        is_valid = bool(re.match(pattern, value))

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(field=target_field, value=value, pattern=pattern)
            return ValidationResult(is_valid=False, error_message=msg, error_fields=[target_field])


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

        # 値がNoneの場合は検証をスキップ（有効とする）
        # 必須チェックは別のルールで行う想定
        if value is None:
            return ValidationResult(is_valid=True)

        # 列挙値のチェック
        is_valid = value in allowed_values

        if is_valid:
            return ValidationResult(is_valid=True)
        else:
            # エラーメッセージのフォーマット
            msg = error_message_template.format(
                field=target_field, value=value, allowed_values=", ".join(str(v) for v in allowed_values)
            )
            return ValidationResult(is_valid=False, error_message=msg, error_fields=[target_field])


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
        return Expression


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
        results = [expr.validate(context, "") for expr in self.all_of]

        # すべての条件が有効であれば有効
        if all(r.is_valid for r in results):
            return ValidationResult(is_valid=True)
        else:
            # エラーがあった条件のフィールドを集める
            error_fields = []
            for result in results:
                if not result.is_valid and result.error_fields:
                    error_fields.extend(result.error_fields)

            # 重複を排除
            error_fields = list(set(error_fields))

            # エラーメッセージのフォーマット
            msg = error_message_template
            return ValidationResult(is_valid=False, error_message=msg, error_fields=error_fields)


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
            # すべての条件が無効の場合、エラーフィールドを集める
            error_fields = []
            for result in results:
                if not result.is_valid and result.error_fields:
                    error_fields.extend(result.error_fields)

            # 重複を排除
            error_fields = list(set(error_fields))

            # エラーメッセージのフォーマット
            msg = error_message_template
            return ValidationResult(is_valid=False, error_message=msg, error_fields=error_fields)


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
            # 内部式が有効なら、エラーフィールドを取得
            # 内部式がどのフィールドに対するものか不明確な場合があるため、
            # エラーフィールドはconfig_loader側で判定せず、呼び出し側に委ねる
            msg = error_message_template
            return ValidationResult(
                is_valid=False,
                error_message=msg,
                error_fields=[],  # エラーフィールドは指定しない
            )


# 前方参照の解決
AllOfExpression.model_rebuild()
AnyOfExpression.model_rebuild()
NotExpression.model_rebuild()


class Rule(BaseModel):
    """バリデーションルール"""

    name: str
    expression: ExpressionType
    error_message: str

    @model_validator(mode="before")
    @classmethod
    def validate_expression(cls, data: dict[str, Any]):
        """式のデータを適切な型に変換する"""
        if isinstance(data, dict) and "expression" in data and isinstance(data["expression"], dict):
            data["expression"] = convert_expression(data["expression"])
        return data

    def validate(self, context: ValidationContext) -> ValidationResult:
        """
        ルールのバリデーションを実行する

        Args:
            context: バリデーションコンテキスト

        Returns:
            ValidationResult: バリデーション結果
        """
        # 内部の式を評価
        result = self.expression.validate(context, self.error_message)

        # ルール名を追加しておく（必要に応じて）
        if not result.is_valid:
            result.rule_name = self.name

        return result


class OutputFormat(BaseModel):
    """出力形式設定"""

    format: str = "json"
    template_file: str | None = None
    template: str | None = None

    @model_validator(mode="after")
    def check_jinja2_template(self):
        """Jinja2形式の場合はテンプレートが必要"""
        if self.format == "jinja2" and not (self.template_file or self.template):
            raise ValueError("Jinja2出力形式の場合、template_fileまたはtemplateが必要です")

        if self.format == "jinja2" and self.template_file and self.template:
            raise ValueError("template_fileとtemplateを同時に指定することはできません")

        if self.format not in ["json", "yaml", "jinja2"]:
            raise ValueError(f"サポートされていない出力形式です: {self.format}")

        return self


class ConfigModel(BaseModel):
    """設定ファイルのモデル"""

    fields: dict[str, str]
    rules: list[Rule]
    output: OutputFormat = Field(default_factory=OutputFormat)

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v):
        """フィールド定義の検証"""
        if not v:
            raise ValueError("少なくとも1つのフィールド定義が必要です")

        pattern = r"^[^!]+![A-Z]+[0-9]+$"
        for _, cell_addr in v.items():
            if not re.match(pattern, cell_addr):
                raise ValueError(f"無効なセル参照形式です: {cell_addr}。正しい形式は 'Sheet1!A1' です。")

        return v


class ConfigLoader:
    """設定ファイルローダー"""

    DEFAULT_SCHEMA_PATH: ClassVar[str] = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "spec", "rule-schema.json"
    )

    def __init__(self, schema_path: str = None):
        """
        初期化

        Args:
            schema_path: JSONスキーマファイルのパス（None の場合はデフォルトパスを使用）
        """
        self.schema_path = schema_path or self.DEFAULT_SCHEMA_PATH
        self.validator = SchemaValidator(self.schema_path)

    def load_config(self, config_path: str) -> ConfigModel:
        """
        設定ファイルを読み込み、モデルオブジェクトを返す

        Args:
            config_path: 設定ファイルのパス

        Returns:
            ConfigModel: 設定モデルオブジェクト

        Raises:
            ConfigValidationError: 設定ファイルの検証に失敗した場合
        """
        # 設定ファイルのパース
        config_data = ConfigParser.parse_file(config_path)

        # JSONスキーマによる検証
        self.validator.validate(config_data)

        try:
            # モデルオブジェクトの生成
            return ConfigModel.model_validate(config_data)
        except Exception as e:
            raise ConfigValidationError(f"設定ファイルの検証に失敗しました: {e}")
