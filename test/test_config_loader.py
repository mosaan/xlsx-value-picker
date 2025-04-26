"""
設定データ読み込み機能のテスト
"""

import json
import sys
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError as PydanticValidationError  # PydanticValidationError をインポート

# テスト対象モジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xlsx_value_picker.config_loader import (
    ConfigLoader,
    ConfigModel,
    ConfigParser,
    OutputFormat,
    Rule,
)
from xlsx_value_picker.exceptions import ConfigLoadError, ConfigValidationError
from xlsx_value_picker.validator.validation_expressions import RequiredExpression


# --- テストデータ作成用ヘルパー関数 ---
def create_valid_yaml(path):
    data = {"fields": {"key1": "Sheet1!A1"}, "rules": [], "output": {"format": "json"}}
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def create_valid_json(path):
    data = {"fields": {"key1": "Sheet1!A1"}, "rules": [], "output": {"format": "json"}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def create_invalid_yaml(path):
    # 不正なYAML形式
    with open(path, "w", encoding="utf-8") as f:  # 括弧の修正
        f.write("key1: value1\nkey2: [value2")  # 閉じ括弧がない


def create_invalid_json(path):
    # 不正なJSON形式
    with open(path, "w", encoding="utf-8") as f:  # 括弧の修正
        f.write('{"key1": "value1", "key2": ')  # 値がない


def create_valid_schema(path):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"fields": {"type": "object"}, "rules": {"type": "array"}, "output": {"type": "object"}},
        "required": ["fields", "rules", "output"],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f)


def create_invalid_schema(path):
    # 不正なJSON形式のスキーマ
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"type": "object", "properties": ')


# --- テストクラス ---


class TestConfigParser:
    """ConfigParserクラスのテスト"""

    def test_parse_yaml(self, tmp_path):
        """YAMLファイルを正しくパースできることをテスト"""
        yaml_path = tmp_path / "test.yaml"
        create_valid_yaml(yaml_path)
        data = ConfigParser.parse_file(str(yaml_path))
        assert data["fields"]["key1"] == "Sheet1!A1"

    def test_parse_json(self, tmp_path):
        """JSONファイルを正しくパースできることをテスト"""
        json_path = tmp_path / "test.json"
        create_valid_json(json_path)
        data = ConfigParser.parse_file(str(json_path))
        assert data["fields"]["key1"] == "Sheet1!A1"

    def test_parse_invalid_yaml(self, tmp_path):
        """不正なYAMLファイルを読み込もうとするとConfigLoadErrorが発生することをテスト"""
        invalid_yaml_path = tmp_path / "invalid.yaml"
        create_invalid_yaml(invalid_yaml_path)
        with pytest.raises(ConfigLoadError) as excinfo:
            ConfigParser.parse_file(str(invalid_yaml_path))
        assert "設定ファイルのパースに失敗しました" in str(excinfo.value)

    def test_parse_invalid_json(self, tmp_path):
        """不正なJSONファイルを読み込もうとするとConfigLoadErrorが発生することをテスト"""
        invalid_json_path = tmp_path / "invalid.json"
        create_invalid_json(invalid_json_path)
        with pytest.raises(ConfigLoadError) as excinfo:
            ConfigParser.parse_file(str(invalid_json_path))
        assert "設定ファイルのパースに失敗しました" in str(excinfo.value)

    def test_parse_nonexistent_file(self):
        """存在しないファイルを読み込もうとするとConfigLoadErrorが発生することをテスト"""
        with pytest.raises(ConfigLoadError) as excinfo:
            ConfigParser.parse_file("nonexistent_file.yaml")
        assert "設定ファイルが見つかりません" in str(excinfo.value)

    def test_parse_invalid_extension(self, tmp_path):
        """サポートされていない拡張子のファイルを読み込もうとするとConfigLoadErrorが発生することをテスト"""
        # テスト用の無効な拡張子ファイルの作成
        invalid_path = tmp_path / "test_config.txt"
        with open(invalid_path, "w", encoding="utf-8") as f:
            f.write("This is not a valid config file")

        with pytest.raises(ConfigLoadError) as excinfo:
            ConfigParser.parse_file(str(invalid_path))
        assert "サポートされていないファイル形式です" in str(excinfo.value)


class TestPydanticModels:
    """Pydanticモデルのテスト"""

    def test_rule_model_validation(self):
        """Ruleモデルのバリデーションテスト"""
        # 正常系 - RequiredExpressionを使用（新形式のみをサポート）
        rule_data = {
            "name": "必須チェック",
            "expression": {"required": "field1"},
            "error_message": "必須です",
        }
        rule = Rule.model_validate(rule_data)
        assert isinstance(rule.expression, RequiredExpression)
        assert rule.expression.required == "field1"

        # 複数フィールドの場合
        rule_data_multi = {
            "name": "複数必須チェック",
            "expression": {"required": ["field1", "field2"]},
            "error_message": "必須フィールドです",
        }
        rule_multi = Rule.model_validate(rule_data_multi)
        assert isinstance(rule_multi.expression, RequiredExpression)
        assert rule_multi.expression.required == ["field1", "field2"]

        # 異常系 (不正な式タイプ)
        invalid_rule_data = {
            "name": "不正なルール",
            "expression": {"unknown_type": {}},
            "error_message": "エラー",
        }
        with pytest.raises(PydanticValidationError):
            Rule.model_validate(invalid_rule_data)

    def test_output_format_validation(self):
        """OutputFormatモデルのバリデーションテスト"""
        # 正常系 (デフォルト)
        of1 = OutputFormat()
        assert of1.format == "json"

        # 正常系 (jinja2 + template_file)
        of2 = OutputFormat(format="jinja2", template_file="template.j2")
        assert of2.format == "jinja2"

        # 正常系 (jinja2 + template)
        of3 = OutputFormat(format="jinja2", template="Hello {{ name }}")
        assert of3.format == "jinja2"

        # 異常系 (jinja2 でテンプレートなし)
        with pytest.raises(ValueError) as excinfo1:
            OutputFormat(format="jinja2")
        assert "template_fileまたはtemplateが必要" in str(excinfo1.value)

        # 異常系 (jinja2 で両方指定)
        with pytest.raises(ValueError) as excinfo2:
            OutputFormat(format="jinja2", template_file="a.j2", template="b")
        assert "template_fileとtemplateを同時に指定することはできません" in str(excinfo2.value)

        # 異常系 (サポート外フォーマット)
        with pytest.raises(ValueError) as excinfo3:
            OutputFormat(format="xml")
        assert "サポートされていない出力形式です" in str(excinfo3.value)

    def test_config_model_validation(self):
        """ConfigModelモデルのバリデーションテスト"""
        # 正常系
        valid_data = {
            "fields": {"field1": "Sheet1!A1", "field2": "Data!B10"},
            "rules": [{"name": "ルール1", "expression": {"required": "field1"}, "error_message": "必須"}],
            "output": {"format": "yaml"},
        }
        model = ConfigModel.model_validate(valid_data)
        assert len(model.fields) == 2
        assert len(model.rules) == 1
        assert model.output.format == "yaml"

        # 異常系 (fields が空)
        invalid_data1 = {"fields": {}, "rules": [], "output": {"format": "json"}}
        with pytest.raises(PydanticValidationError) as excinfo1:
            ConfigModel.model_validate(invalid_data1)
        assert "Value error, 少なくとも1つのフィールド定義が必要です" in str(excinfo1.value)

        # 異常系 (不正なセル参照)
        invalid_data2 = {"fields": {"f1": "Sheet1A1"}, "rules": [], "output": {"format": "json"}}
        with pytest.raises(PydanticValidationError) as excinfo2:
            ConfigModel.model_validate(invalid_data2)
        assert "Value error, 無効なセル参照形式です" in str(excinfo2.value)


class TestConfigLoader:
    """ConfigLoaderクラスのテスト"""

    @pytest.fixture
    def valid_config_file(self, tmp_path):
        """有効な設定ファイルを作成してパスを返す"""
        config_path = tmp_path / "valid_config.yaml"
        create_valid_yaml(config_path)
        return str(config_path)

    @pytest.fixture
    def invalid_config_file(self, tmp_path):
        """無効な設定ファイルを作成してパスを返す"""
        config_path = tmp_path / "invalid_config.yaml"
        # スキーマ違反 (outputがない)
        data = {"fields": {"key1": "Sheet1!A1"}, "rules": []}
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        return str(config_path)

    def test_load_config_success(self, valid_config_file):
        """有効な設定ファイルを正しく読み込めることをテスト"""
        loader = ConfigLoader()
        try:
            model = loader.load_config(valid_config_file)
            assert isinstance(model, ConfigModel)
            assert model.fields["key1"] == "Sheet1!A1"
        except (ConfigLoadError, ConfigValidationError) as e:
            pytest.fail(f"設定の読み込みに失敗しました: {e}")

    def test_load_config_file_not_found(self):
        """存在しない設定ファイルを指定するとConfigLoadErrorが発生することをテスト"""
        loader = ConfigLoader()
        with pytest.raises(ConfigLoadError) as excinfo:
            loader.load_config("nonexistent_config.yaml")
        assert "設定ファイルが見つかりません" in str(excinfo.value)

    def test_load_config_model_validation_error(self, tmp_path):
        """モデル検証エラーが発生する設定ファイルを指定するとConfigValidationErrorが発生することをテスト"""
        # モデル検証エラー (fields が空)
        config_path = tmp_path / "model_error.yaml"
        data = {"fields": {}, "rules": [], "output": {"format": "json"}}
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

        loader = ConfigLoader()
        with pytest.raises(ConfigValidationError) as excinfo:
            loader.load_config(str(config_path))
        assert "設定ファイルのモデル検証に失敗しました" in str(excinfo.value)
        assert "Value error, 少なくとも1つのフィールド定義が必要です" in str(excinfo.value)
