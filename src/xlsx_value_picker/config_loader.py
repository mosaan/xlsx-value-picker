"""
JSONスキーマに基づく設定データ読み込み機能
"""

import json
import os
from pathlib import Path # pathlib をインポート
from typing import Any, ClassVar

import jsonschema
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError as PydanticValidationError

# カスタム例外をインポート
from .exceptions import ConfigLoadError, ConfigValidationError, XlsxValuePickerError
from .validation_common import ValidationContext, ValidationResult
from .validation_expressions import ExpressionType, convert_expression


# ConfigValidationError は exceptions.py に移動済みのため削除

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
            ConfigLoadError: ファイルが存在しない、またはサポートされていない形式の場合
        """
        if not os.path.exists(file_path):
            # FileNotFoundError の代わりに ConfigLoadError を送出
            raise ConfigLoadError(f"設定ファイルが見つかりません: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    return yaml.safe_load(f)
                elif file_path.endswith(".json"):
                    return json.load(f)
                else:
                    # ValueError の代わりに ConfigLoadError を送出
                    raise ConfigLoadError(f"サポートされていないファイル形式です: {file_path}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
             raise ConfigLoadError(f"設定ファイルのパースに失敗しました: {file_path} - {e}")
        except Exception as e: # その他の予期せぬ読み込みエラー
             raise ConfigLoadError(f"設定ファイルの読み込み中に予期せぬエラーが発生しました: {file_path} - {e}")


class SchemaValidator:
    """JSONスキーマバリデーター"""

    def __init__(self, schema_path: str):
        """
        スキーマファイルを読み込む

        Args:
            schema_path: JSONスキーマファイルのパス

        Raises:
            ConfigLoadError: スキーマファイルが見つからない、またはJSONとして不正な場合
        """
        if not os.path.exists(schema_path):
             # FileNotFoundError の代わりに ConfigLoadError を送出
            raise ConfigLoadError(f"スキーマファイルが見つかりません: {schema_path}")

        try:
            with open(schema_path, encoding="utf-8") as f:
                self.schema = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigLoadError(f"スキーマファイルのJSON形式が不正です: {schema_path} - {e}")
        except Exception as e:
            raise ConfigLoadError(f"スキーマファイルの読み込み中に予期せぬエラーが発生しました: {schema_path} - {e}")


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
            # ConfigValidationError を使用
            raise ConfigValidationError(f"設定ファイルのスキーマ検証に失敗しました: {path} - {e.message}")
        except Exception as e: # jsonschema の予期せぬエラー
            raise ConfigValidationError(f"スキーマ検証中に予期せぬエラーが発生しました: {e}")


# バリデーション式関連のコードは validation_expressions.py に移動済み

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

        if self.format not in ["json", "yaml", "jinja2", "csv"]: # csv を追加 (仮)
             # TODO: csv サポートを正式に追加する際に修正
            raise ValueError(f"サポートされていない出力形式です: {self.format}")
            # pass # 一旦許容

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

    # 修正: デフォルトスキーマパスの計算方法を変更
    _BASE_DIR = Path(__file__).resolve().parent.parent # src ディレクトリを基準とする
    DEFAULT_SCHEMA_PATH: ClassVar[str] = str(
        _BASE_DIR.parent / "docs" / "spec" / "rule-schema.json" # プロジェクトルートからの相対パス
    )

    def __init__(self, schema_path: str = None):
        """
        初期化

        Args:
            schema_path: JSONスキーマファイルのパス（None の場合はデフォルトパスを使用）

        Raises:
            ConfigLoadError: スキーマファイルの読み込みに失敗した場合
        """
        self.schema_path = schema_path or self.DEFAULT_SCHEMA_PATH
        # print(f"DEBUG: Using schema path: {self.schema_path}") # デバッグ用
        try:
            self.validator = SchemaValidator(self.schema_path)
        except ConfigLoadError as e: # SchemaValidator からの ConfigLoadError をキャッチ
            # __init__ で発生したエラーはそのまま送出
            raise e
        except Exception as e: # 予期せぬエラー
             raise ConfigLoadError(f"スキーマバリデーターの初期化中にエラーが発生しました: {e}")


    def load_config(self, config_path: str) -> ConfigModel:
        """
        設定ファイルを読み込み、モデルオブジェクトを返す

        Args:
            config_path: 設定ファイルのパス

        Returns:
            ConfigModel: 設定モデルオブジェクト

        Raises:
            ConfigLoadError: 設定ファイルの読み込みやパースに失敗した場合
            ConfigValidationError: 設定ファイルのスキーマ検証やモデル検証に失敗した場合
        """
        try:
            # 設定ファイルのパース (ConfigLoadError が発生する可能性)
            config_data = ConfigParser.parse_file(config_path)

            # JSONスキーマによる検証 (ConfigValidationError が発生する可能性)
            self.validator.validate(config_data)

            # モデルオブジェクトの生成 (PydanticValidationError が発生する可能性)
            model = ConfigModel.model_validate(config_data)
            return model

        except ConfigLoadError as e:
            # パース時のエラーはそのまま ConfigLoadError として送出
            raise e
        except ConfigValidationError as e:
             # スキーマ検証時のエラーはそのまま ConfigValidationError として送出
            raise e
        except PydanticValidationError as e:
            # Pydantic のバリデーションエラーを ConfigValidationError にラップして送出
            # エラーメッセージを整形して分かりやすくする
            error_details = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
            raise ConfigValidationError(f"設定ファイルのモデル検証に失敗しました: {error_details}") from e
        except Exception as e:
            # その他の予期せぬエラー
            raise XlsxValuePickerError(f"設定ファイルの処理中に予期せぬエラーが発生しました: {e}") from e
