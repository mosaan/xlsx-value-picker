"""
設定読み込み機能のテスト
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# テスト対象モジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xlsx_value_picker.config_loader import (
    ConfigLoader,
    ConfigModel,
    ConfigParser,
    ConfigValidationError,
    OutputFormat,
    SchemaValidator,
    Rule, # Rule は config_loader に残る
)
# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validation_expressions import (
    AllOfExpression,
    AnyOfExpression,
    CompareExpression,
    EnumExpression,
    Expression, # Expression 基底クラスも必要に応じてインポート
    NotExpression,
    RegexMatchExpression,
    RequiredExpression,
)
from xlsx_value_picker.validation_common import ValidationContext, ValidationResult # これらは共通モジュールから


class TestConfigParser:
    """ConfigParserのテスト"""

    def test_parse_yaml_file(self, tmp_path):
        """YAMLファイルを正しく読み込めることをテスト"""
        # テスト用YAMLファイルの作成
        yaml_path = tmp_path / "test_config.yaml"
        yaml_data = {
            "fields": {"field1": "Sheet1!A1", "field2": "Sheet1!B2"},
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
        }
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f)

        # パーサーで読み込み
        result = ConfigParser.parse_file(str(yaml_path))

        # 検証
        assert result["fields"]["field1"] == "Sheet1!A1"
        assert result["fields"]["field2"] == "Sheet1!B2"
        assert len(result["rules"]) == 1
        assert result["rules"][0]["name"] == "Test Rule"
        assert result["rules"][0]["error_message"] == "Field1 is required"

    def test_parse_json_file(self, tmp_path):
        """JSONファイルを正しく読み込めることをテスト"""
        # テスト用JSONファイルの作成
        json_path = tmp_path / "test_config.json"
        json_data = {
            "fields": {"field1": "Sheet1!A1", "field2": "Sheet1!B2"},
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f)

        # パーサーで読み込み
        result = ConfigParser.parse_file(str(json_path))

        # 検証
        assert result["fields"]["field1"] == "Sheet1!A1"
        assert result["fields"]["field2"] == "Sheet1!B2"
        assert len(result["rules"]) == 1
        assert result["rules"][0]["name"] == "Test Rule"
        assert result["rules"][0]["error_message"] == "Field1 is required"

    def test_parse_nonexistent_file(self):
        """存在しないファイルを読み込もうとするとFileNotFoundErrorが発生することをテスト"""
        with pytest.raises(FileNotFoundError):
            ConfigParser.parse_file("nonexistent_file.yaml")

    def test_parse_invalid_extension(self, tmp_path):
        """サポートされていない拡張子のファイルを読み込もうとするとValueErrorが発生することをテスト"""
        # テスト用の無効な拡張子ファイルの作成
        invalid_path = tmp_path / "test_config.txt"
        with open(invalid_path, "w", encoding="utf-8") as f:
            f.write("This is not a valid config file")

        with pytest.raises(ValueError) as excinfo:
            ConfigParser.parse_file(str(invalid_path))

        assert "サポートされていないファイル形式" in str(excinfo.value)


class TestSchemaValidator:
    """SchemaValidatorのテスト"""

    @pytest.fixture
    def schema_file(self, tmp_path):
        """テスト用のスキーマファイルを作成して、そのパスを返す"""
        schema_path = tmp_path / "test_schema.json"
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "fields": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "pattern": "^[^!]+![A-Z]+[0-9]+$"},
                },
                "rules": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["fields", "rules"],
        }
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f)
        return str(schema_path)

    def test_validate_valid_config(self, schema_file):
        """有効な設定データが検証を通過することをテスト"""
        # 有効な設定データ
        valid_config = {
            "fields": {"field1": "Sheet1!A1", "field2": "Sheet2!B2"},
            "rules": [{"name": "Test Rule", "expression": {"required": True}, "error_message": "Error"}],
        }

        # バリデーター作成
        validator = SchemaValidator(schema_file)
        # 検証実行（例外が発生しないことを確認）
        validator.validate(valid_config)

    def test_validate_invalid_config(self, schema_file):
        """無効な設定データが検証で例外を発生させることをテスト"""
        # 無効な設定データ（フィールド形式が不正）
        invalid_config = {
            "fields": {"field1": "InvalidFormat", "field2": "Sheet2!B2"},
            "rules": [{"name": "Test Rule"}],
        }

        # バリデーター作成
        validator = SchemaValidator(schema_file)
        # 検証実行（例外が発生することを確認）
        with pytest.raises(ConfigValidationError):
            validator.validate(invalid_config)

    def test_validate_missing_required_field(self, schema_file):
        """必須フィールドが欠けている設定データが検証で例外を発生させることをテスト"""
        # 無効な設定データ（必須フィールドがない）
        invalid_config = {
            "fields": {"field1": "Sheet1!A1"},
            # "rules"が欠けている
        }

        # バリデーター作成
        validator = SchemaValidator(schema_file)
        # 検証実行（例外が発生することを確認）
        with pytest.raises(ConfigValidationError):
            validator.validate(invalid_config)

    def test_nonexistent_schema_file(self):
        """存在しないスキーマファイルを指定するとFileNotFoundErrorが発生することをテスト"""
        with pytest.raises(FileNotFoundError):
            SchemaValidator("nonexistent_schema.json")


class TestPydanticModels:
    """Pydanticモデルのテスト"""

    def test_output_format_default(self):
        """OutputFormatのデフォルト値が正しく設定されることをテスト"""
        output = OutputFormat()
        assert output.format == "json"
        assert output.template_file is None
        assert output.template is None

    def test_output_format_jinja2_missing_template(self):
        """Jinja2出力形式でテンプレートが指定されていないとエラーになることをテスト"""
        with pytest.raises(ValueError) as excinfo:
            OutputFormat(format="jinja2")
        assert "Jinja2出力形式の場合" in str(excinfo.value)

    def test_output_format_jinja2_valid(self):
        """Jinja2出力形式で有効なテンプレート指定をテスト"""
        # テンプレートファイル指定
        output1 = OutputFormat(format="jinja2", template_file="template.j2")
        assert output1.format == "jinja2"
        assert output1.template_file == "template.j2"

        # テンプレート文字列指定
        output2 = OutputFormat(format="jinja2", template="Hello {{ name }}")
        assert output2.format == "jinja2"
        assert output2.template == "Hello {{ name }}"

    def test_output_format_jinja2_both_templates(self):
        """Jinja2出力形式で両方のテンプレート指定があるとエラーになることをテスト"""
        with pytest.raises(ValueError) as excinfo:
            OutputFormat(format="jinja2", template_file="template.j2", template="Hello")
        assert "template_fileとtemplate" in str(excinfo.value)

    def test_output_format_unsupported_format(self):
        """サポートされていない出力形式を指定するとエラーになることをテスト"""
        with pytest.raises(ValueError) as excinfo:
            OutputFormat(format="unsupported")
        assert "サポートされていない出力形式" in str(excinfo.value)

    def test_config_model_valid(self):
        """有効な設定データからConfigModelを作成できることをテスト"""
        config_data = {
            "fields": {"field1": "Sheet1!A1"},
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
            "output": {"format": "json"},
        }
        model = ConfigModel.model_validate(config_data)
        assert model.fields["field1"] == "Sheet1!A1"
        assert len(model.rules) == 1
        assert model.rules[0].name == "Test Rule"
        assert model.output.format == "json"

    def test_config_model_invalid_field_reference(self):
        """無効なセル参照を含む設定データがエラーになることをテスト"""
        config_data = {
            "fields": {"field1": "InvalidFormat"},  # 不正なセル参照形式
            "rules": [],
        }
        with pytest.raises(ValueError) as excinfo:
            ConfigModel.model_validate(config_data)
        assert "無効なセル参照形式" in str(excinfo.value)

    def test_compare_expression(self):
        """比較式のバリデーションをテスト"""
        # 有効な比較式
        valid_expr = {"compare": {"left": "field1", "operator": "==", "right": "value"}}
        expr = CompareExpression.model_validate(valid_expr)
        assert expr.compare["left"] == "field1"
        assert expr.compare["operator"] == "=="
        assert expr.compare["right"] == "value"

        # 無効な比較式（不足しているキー）
        invalid_expr = {"compare": {"left": "field1", "right": "value"}}  # operatorが不足
        with pytest.raises(ValueError):
            CompareExpression.model_validate(invalid_expr)

        # 無効な比較式（不正な演算子）
        invalid_expr = {"compare": {"left": "field1", "operator": "invalid", "right": "value"}}
        with pytest.raises(ValueError):
            CompareExpression.model_validate(invalid_expr)

    def test_required_expression(self):
        """必須項目式のバリデーションをテスト"""
        expr = RequiredExpression(field="field1")
        assert expr.field == "field1"
        assert expr.required is True

    def test_regex_match_expression(self):
        """正規表現マッチ式のバリデーションをテスト"""
        # 有効な正規表現
        valid_expr = {"regex_match": {"field": "field1", "pattern": "^test.*$"}}
        expr = RegexMatchExpression.model_validate(valid_expr)
        assert expr.regex_match["field"] == "field1"
        assert expr.regex_match["pattern"] == "^test.*$"

        # 無効な正規表現（不正なパターン）
        invalid_expr = {"regex_match": {"field": "field1", "pattern": "["}}  # 不正な正規表現
        with pytest.raises(ValueError):
            RegexMatchExpression.model_validate(invalid_expr)

    def test_enum_expression(self):
        """列挙型式のバリデーションをテスト"""
        # 有効な列挙型式
        valid_expr = {"enum": {"field": "field1", "values": ["value1", "value2"]}}
        expr = EnumExpression.model_validate(valid_expr)
        assert expr.enum["field"] == "field1"
        assert expr.enum["values"] == ["value1", "value2"]

        # 無効な列挙型式（空の値リスト）
        invalid_expr = {"enum": {"field": "field1", "values": []}}
        with pytest.raises(ValueError):
            EnumExpression.model_validate(invalid_expr)

    def test_all_of_expression(self):
        """全条件一致式のバリデーションをテスト"""
        # 有効な全条件一致式
        valid_expr = {
            "all_of": [
                {"field": "field1", "required": True},
                {"compare": {"left": "field2", "operator": "==", "right": "value"}},
            ]
        }
        expr = AllOfExpression.model_validate(valid_expr)
        assert len(expr.all_of) == 2

        # このテストは修正されたモデル検証方法に対応させる
        # 元の項目がRequiredExpressionに変換されていること
        assert expr.all_of[0].field == "field1"
        assert expr.all_of[0].required is True

        # 元の項目がCompareExpressionに変換されていること
        assert "left" in expr.all_of[1].compare
        assert expr.all_of[1].compare["operator"] == "=="
        assert expr.all_of[1].compare["right"] == "value"

        # 無効な全条件一致式（空のリスト）
        invalid_expr = {"all_of": []}
        with pytest.raises(ValueError):
            AllOfExpression.model_validate(invalid_expr)

    def test_any_of_expression(self):
        """いずれかの条件一致式のバリデーションをテスト"""
        # 有効ないずれかの条件一致式
        valid_expr = {
            "any_of": [
                {"field": "field1", "required": True},
                {"compare": {"left": "field2", "operator": "==", "right": "value"}},
            ]
        }
        expr = AnyOfExpression.model_validate(valid_expr)
        assert len(expr.any_of) == 2

        # このテストは修正されたモデル検証方法に対応させる
        # 元の項目がRequiredExpressionに変換されていること
        assert expr.any_of[0].field == "field1"
        assert expr.any_of[0].required is True

        # 元の項目がCompareExpressionに変換されていること
        assert "left" in expr.any_of[1].compare
        assert expr.any_of[1].compare["operator"] == "=="
        assert expr.any_of[1].compare["right"] == "value"

        # 無効ないずれかの条件一致式（空のリスト）
        invalid_expr = {"any_of": []}
        with pytest.raises(ValueError):
            AnyOfExpression.model_validate(invalid_expr)

    def test_not_expression(self):
        """否定式のバリデーションをテスト"""
        # 有効な否定式
        valid_expr = {"not": {"field": "field1", "required": True}}
        expr = NotExpression.model_validate(valid_expr)

        # このテストは修正されたモデル検証方法に対応させる
        # 否定対象がRequiredExpressionに変換されていること
        assert expr.not_.field == "field1"
        assert expr.not_.required is True


class TestConfigLoader:
    """ConfigLoaderのテスト"""

    @pytest.fixture
    def schema_file(self, tmp_path):
        """テスト用のスキーマファイルを作成して、そのパスを返す"""
        schema_path = tmp_path / "test_schema.json"
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "fields": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "pattern": "^[^!]+![A-Z]+[0-9]+$"},
                },
                "rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "expression": {"type": "object"},
                            "error_message": {"type": "string"},
                        },
                        "required": ["name", "expression", "error_message"],
                    },
                },
            },
            "required": ["fields", "rules"],
        }
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f)
        return str(schema_path)

    def test_load_config_yaml(self, tmp_path, schema_file):
        """YAML設定ファイルを読み込めることをテスト"""
        # テスト用YAML設定ファイルの作成
        config_path = tmp_path / "test_config.yaml"
        config_data = {
            "fields": {"field1": "Sheet1!A1", "field2": "Sheet2!B2"},
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
            "output": {"format": "json"},
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # 設定ローダー作成
        loader = ConfigLoader(schema_path=schema_file)
        # 設定読み込み
        config = loader.load_config(str(config_path))

        # 検証
        assert config.fields["field1"] == "Sheet1!A1"
        assert config.fields["field2"] == "Sheet2!B2"
        assert len(config.rules) == 1
        assert config.rules[0].name == "Test Rule"
        assert config.output.format == "json"

    def test_load_config_json(self, tmp_path, schema_file):
        """JSON設定ファイルを読み込めることをテスト"""
        # テスト用JSON設定ファイルの作成
        config_path = tmp_path / "test_config.json"
        config_data = {
            "fields": {"field1": "Sheet1!A1", "field2": "Sheet2!B2"},
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
            "output": {"format": "json"},
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        # 設定ローダー作成
        loader = ConfigLoader(schema_path=schema_file)
        # 設定読み込み
        config = loader.load_config(str(config_path))

        # 検証
        assert config.fields["field1"] == "Sheet1!A1"
        assert config.fields["field2"] == "Sheet2!B2"
        assert len(config.rules) == 1
        assert config.rules[0].name == "Test Rule"
        assert config.output.format == "json"

    def test_load_config_invalid_schema(self, tmp_path, schema_file):
        """スキーマ検証に失敗する設定ファイルを読み込もうとするとConfigValidationErrorが発生することをテスト"""
        # 無効な設定データ（フィールド形式が不正）
        config_path = tmp_path / "invalid_config.yaml"
        invalid_config = {
            "fields": {"field1": "InvalidFormat"},  # 不正なセル参照形式
            "rules": [
                {
                    "name": "Test Rule",
                    "expression": {"field": "field1", "required": True},
                    "error_message": "Field1 is required",
                }
            ],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(invalid_config, f)

        # 設定ローダー作成
        loader = ConfigLoader(schema_path=schema_file)
        # 設定読み込み（例外が発生することを確認）
        with pytest.raises(ConfigValidationError):
            loader.load_config(str(config_path))

    def test_load_config_default_schema(self, tmp_path, monkeypatch):
        """デフォルトのスキーマファイルパスを使用できることをテスト"""
        # 仮想的なデフォルトスキーマファイルを作成
        temp_dir = tempfile.mkdtemp()
        default_schema_path = Path(temp_dir) / "docs" / "rule-schema.json"
        default_schema_path.parent.mkdir(parents=True, exist_ok=True)

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "fields": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "pattern": "^[^!]+![A-Z]+[0-9]+$"},
                },
                "rules": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["fields", "rules"],
        }
        with open(default_schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f)

        # デフォルトのスキーマパスを上書き
        monkeypatch.setattr(ConfigLoader, "DEFAULT_SCHEMA_PATH", str(default_schema_path))

        # テスト用設定ファイルの作成
        config_path = tmp_path / "test_config.yaml"
        config_data = {
            "fields": {"field1": "Sheet1!A1"},
            "rules": [],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # スキーマパスを指定せず設定ローダー作成
        loader = ConfigLoader()
        # 設定読み込み
        config = loader.load_config(str(config_path))

        # 検証
        assert config.fields["field1"] == "Sheet1!A1"
