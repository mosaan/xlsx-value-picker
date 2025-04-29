"""
出力フォーマット機能のテスト
"""

import json
import sys
from pathlib import Path

import pytest
import yaml


from xlsx_value_picker.config_loader import ConfigModel, OutputFormat
from xlsx_value_picker.output_formatter import OutputFormatter


class TestOutputFormatter:
    """OutputFormatterのテスト"""

    @pytest.fixture
    def test_data(self):
        """テスト用のデータを返す"""
        return {"field1": 100, "field2": "テスト文字列", "nested": {"key1": "value1", "key2": 200}, "list": [1, 2, 3]}

    @pytest.fixture
    def json_config(self):
        """JSON出力形式の設定モデルを返す"""
        return ConfigModel(fields={"field1": "Sheet1!A1"}, rules=[], output=OutputFormat(format="json"))

    @pytest.fixture
    def yaml_config(self):
        """YAML出力形式の設定モデルを返す"""
        return ConfigModel(fields={"field1": "Sheet1!A1"}, rules=[], output=OutputFormat(format="yaml"))

    @pytest.fixture
    def jinja2_string_config(self):
        """Jinja2文字列テンプレート出力形式の設定モデルを返す"""
        return ConfigModel(
            fields={"field1": "Sheet1!A1"},
            rules=[],
            output=OutputFormat(format="jinja2", template="値1: {{ field1 }}\n値2: {{ field2 }}"),
        )

    @pytest.fixture
    def jinja2_file_config(self, tmp_path):
        """Jinja2ファイルテンプレート出力形式の設定モデルを返す"""
        # テンプレートファイル作成
        template_path = tmp_path / "template.j2"
        template_path.write_text("値1: {{ field1 }}\n値2: {{ field2 }}", encoding="utf-8")

        return ConfigModel(
            fields={"field1": "Sheet1!A1"},
            rules=[],
            output=OutputFormat(format="jinja2", template_file=str(template_path)),
        )

    def test_init(self, json_config):
        """初期化が正しく行われることをテスト"""
        formatter = OutputFormatter(json_config)
        assert formatter.config == json_config
        assert formatter.output_config == json_config.output

    def test_format_json(self, json_config, test_data):
        """JSON形式の出力が正しく行われることをテスト"""
        formatter = OutputFormatter(json_config)
        result = formatter.format_output(test_data)

        # 出力がJSON形式であることを確認
        parsed = json.loads(result)
        assert parsed["field1"] == 100
        assert parsed["field2"] == "テスト文字列"
        assert parsed["nested"]["key1"] == "value1"
        assert parsed["list"] == [1, 2, 3]

    def test_format_yaml(self, yaml_config, test_data):
        """YAML形式の出力が正しく行われることをテスト"""
        formatter = OutputFormatter(yaml_config)
        result = formatter.format_output(test_data)

        # 出力がYAML形式であることを確認
        parsed = yaml.safe_load(result)
        assert parsed["field1"] == 100
        assert parsed["field2"] == "テスト文字列"
        assert parsed["nested"]["key1"] == "value1"
        assert parsed["list"] == [1, 2, 3]

    def test_format_jinja2_string(self, jinja2_string_config, test_data):
        """Jinja2文字列テンプレートの出力が正しく行われることをテスト"""
        formatter = OutputFormatter(jinja2_string_config)
        result = formatter.format_output(test_data)

        # 出力がテンプレートに基づいていることを確認
        assert "値1: 100" in result
        assert "値2: テスト文字列" in result

    def test_format_jinja2_file(self, jinja2_file_config, test_data):
        """Jinja2ファイルテンプレートの出力が正しく行われることをテスト"""
        formatter = OutputFormatter(jinja2_file_config)
        result = formatter.format_output(test_data)

        # 出力がテンプレートに基づいていることを確認
        assert "値1: 100" in result
        assert "値2: テスト文字列" in result

    def test_format_invalid_format(self, test_data):
        """サポートされていない出力形式でValueErrorが発生することをテスト"""
        # 無効な出力形式の設定
        config = ConfigModel(
            fields={"field1": "Sheet1!A1"},
            rules=[],
            output=OutputFormat(format="json"),  # 一旦有効な形式で初期化
        )
        # 内部的に無効な形式に変更（Pydanticの検証をバイパス）
        config.output.format = "invalid"

        formatter = OutputFormatter(config)
        with pytest.raises(ValueError) as excinfo:
            formatter.format_output(test_data)

        assert "サポートされていない出力形式" in str(excinfo.value)

    def test_missing_template(self, test_data):
        """テンプレートが指定されていない場合にValueErrorが発生することをテスト"""
        # jinja2形式だがテンプレートが指定されていない設定
        config = ConfigModel(
            fields={"field1": "Sheet1!A1"},
            rules=[],
            output=OutputFormat(format="json"),  # 一旦有効な形式で初期化
        )
        # 内部的にjinja2形式に変更（Pydanticの検証をバイパス）
        config.output.format = "jinja2"

        formatter = OutputFormatter(config)
        with pytest.raises(ValueError) as excinfo:
            formatter.format_output(test_data)

        assert "templateまたはtemplate_file" in str(excinfo.value)

    def test_nonexistent_template_file(self, test_data):
        """存在しないテンプレートファイルでFileNotFoundErrorが発生することをテスト"""
        # 存在しないテンプレートファイルを指定
        config = ConfigModel(
            fields={"field1": "Sheet1!A1"},
            rules=[],
            output=OutputFormat(format="jinja2", template_file="nonexistent_template.j2"),
        )

        formatter = OutputFormatter(config)
        with pytest.raises(FileNotFoundError) as excinfo:
            formatter.format_output(test_data)

        assert "テンプレートファイルが見つかりません" in str(excinfo.value)

    def test_write_output_to_file(self, json_config, test_data, tmp_path):
        """ファイルへの出力が正しく行われることをテスト"""
        formatter = OutputFormatter(json_config)
        output_path = tmp_path / "output.json"

        # ファイルに出力
        formatter.write_output(test_data, str(output_path))

        # ファイルが作成されたことを確認
        assert output_path.exists()

        # 内容を確認
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
            parsed = json.loads(content)
            assert parsed["field1"] == 100
            assert parsed["field2"] == "テスト文字列"

    def test_write_output_return_value(self, json_config, test_data):
        """write_outputが出力内容を返すことをテスト"""
        formatter = OutputFormatter(json_config)

        # 出力パスを指定せずに呼び出し
        result = formatter.write_output(test_data)

        # 出力内容が返されることを確認
        parsed = json.loads(result)
        assert parsed["field1"] == 100
        assert parsed["field2"] == "テスト文字列"
