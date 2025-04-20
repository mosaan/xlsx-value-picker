"""
JSONスキーマに基づく設定データ読み込み機能
"""

import json
import os
from typing import Any, ClassVar

import jsonschema
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

# validation_expressions から ExpressionType をインポート
from .validation_common import ValidationContext, ValidationResult
from .validation_expressions import ExpressionType, convert_expression


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


# バリデーション式関連のコードは validation_expressions.py に移動


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
            # validation_expressions の convert_expression を使用
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
        # 内部の式を評価 (self.expression は ExpressionType)
        result: ValidationResult = self.expression.validate(context, self.error_message)

        # ルール名と場所情報を追加
        if not result.is_valid:
            result.rule_name = self.name
            # Ensure locations are populated if fields exist
            if result.error_fields and not result.error_locations:
                 locations = [context.get_field_location(f) for f in result.error_fields if context.get_field_location(f)]
                 result.error_locations = sorted(list(set(locations))) # Use set to avoid duplicates if expression already added some

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
        import re # re をインポート
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
