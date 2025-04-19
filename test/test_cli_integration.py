"""
CLIインターフェースの統合テスト
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest
import yaml

# テスト対象モジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def create_test_excel(path):
    """テスト用のExcelファイルを作成する"""
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Sheet1"
    ws1["A1"] = 100
    ws1["B2"] = 200
    ws1["C3"] = "テスト"
    ws1["D4"] = None  # 空セル
    
    ws2 = wb.create_sheet("Sheet2")
    ws2["A1"] = "Sheet2値1"
    ws2["B2"] = "Sheet2値2"
    
    wb.save(path)


def create_valid_config_yaml(path, excel_path):
    """有効なYAML設定ファイルを作成する"""
    config_data = {
        "fields": {
            "value1": "Sheet1!A1",
            "value2": "Sheet1!B2",
            "text": "Sheet1!C3",
            "sheet2_value": "Sheet2!A1"
        },
        "rules": [
            {
                "name": "テストルール",
                "expression": {"field": "value1", "required": True},
                "error_message": "値1は必須です"
            }
        ],
        "output": {
            "format": "json"
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)


def create_valid_config_json(path, excel_path):
    """有効なJSON設定ファイルを作成する"""
    config_data = {
        "fields": {
            "value1": "Sheet1!A1",
            "value2": "Sheet1!B2",
            "text": "Sheet1!C3"
        },
        "rules": [
            {
                "name": "テストルール",
                "expression": {"field": "value1", "required": True},
                "error_message": "値1は必須です"
            }
        ],
        "output": {
            "format": "json"
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)


def create_invalid_config_yaml(path):
    """無効なYAML設定ファイルを作成する"""
    config_data = {
        "fields": {
            "value1": "InvalidFormat"  # 不正なセル参照形式
        },
        "rules": []
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)


def create_test_schema(path):
    """テスト用のスキーマファイルを作成する"""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "fields": {
                "type": "object",
                "additionalProperties": {
                    "type": "string",
                    "pattern": "^[^!]+![A-Z]+[0-9]+$"
                }
            },
            "rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "expression": {"type": "object"},
                        "error_message": {"type": "string"}
                    },
                    "required": ["name", "expression", "error_message"]
                }
            }
        },
        "required": ["fields", "rules"]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


class TestCLI:
    """CLIインターフェースのテスト"""
    
    @pytest.fixture
    def setup_files(self, tmp_path):
        """テスト用のファイルを作成して、パスを返す"""
        # Excelファイル
        excel_path = tmp_path / "test.xlsx"
        create_test_excel(excel_path)
        
        # YAML設定ファイル
        yaml_config_path = tmp_path / "config.yaml"
        create_valid_config_yaml(yaml_config_path, excel_path)
        
        # JSON設定ファイル
        json_config_path = tmp_path / "config.json"
        create_valid_config_json(json_config_path, excel_path)
        
        # 無効な設定ファイル
        invalid_config_path = tmp_path / "invalid_config.yaml"
        create_invalid_config_yaml(invalid_config_path)
        
        # スキーマファイル
        schema_path = tmp_path / "test_schema.json"
        create_test_schema(schema_path)
        
        return {
            "excel_path": excel_path,
            "yaml_config_path": yaml_config_path,
            "json_config_path": json_config_path,
            "invalid_config_path": invalid_config_path,
            "schema_path": schema_path
        }
    
    def run_cli_command(self, args, cwd=None):
        """CLIコマンドを実行し、結果を返す"""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent)
        
        return subprocess.run(
            [sys.executable, "-m", "xlsx_value_picker.cli"] + args,
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            env=env
        )
    
    def test_valid_yaml_config(self, setup_files):
        """有効なYAML設定ファイルでの実行テスト"""
        excel_path = setup_files["excel_path"]
        yaml_config_path = setup_files["yaml_config_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(yaml_config_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力がJSON形式
        try:
            output_data = json.loads(result.stdout)
            assert output_data["value1"] == 100
            assert output_data["value2"] == 200
            assert output_data["text"] == "テスト"
            assert output_data["sheet2_value"] == "Sheet2値1"
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")
    
    def test_valid_json_config(self, setup_files):
        """有効なJSON設定ファイルでの実行テスト"""
        excel_path = setup_files["excel_path"]
        json_config_path = setup_files["json_config_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(json_config_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力がJSON形式
        try:
            output_data = json.loads(result.stdout)
            assert output_data["value1"] == 100
            assert output_data["value2"] == 200
            assert output_data["text"] == "テスト"
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")
    
    def test_invalid_config(self, setup_files):
        """無効な設定ファイルでの実行テスト"""
        excel_path = setup_files["excel_path"]
        invalid_config_path = setup_files["invalid_config_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(invalid_config_path)
        ])
        
        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # エラーメッセージに「設定ファイルの検証に失敗」が含まれる
        assert "設定ファイルの検証に失敗" in result.stderr
    
    def test_nonexistent_excel(self, setup_files):
        """存在しないExcelファイルでの実行テスト"""
        yaml_config_path = setup_files["yaml_config_path"]
        
        result = self.run_cli_command([
            "nonexistent.xlsx",
            "--config", str(yaml_config_path)
        ])
        
        # 終了コードが2（Click自体のバリデーションエラー終了）
        assert result.returncode == 2
        # エラーメッセージに「File 'nonexistent.xlsx' does not exist」が含まれる
        assert "File 'nonexistent.xlsx' does not exist" in result.stderr
    
    def test_nonexistent_config(self, setup_files):
        """存在しない設定ファイルでの実行テスト"""
        excel_path = setup_files["excel_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", "nonexistent_config.yaml"
        ])
        
        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # エラーメッセージに「設定ファイルの読み込みに失敗」が含まれる
        assert "設定ファイルの読み込みに失敗" in result.stderr
    
    def test_output_to_file(self, setup_files, tmp_path):
        """ファイル出力オプションでの実行テスト"""
        excel_path = setup_files["excel_path"]
        yaml_config_path = setup_files["yaml_config_path"]
        output_path = tmp_path / "output.json"
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(yaml_config_path),
            "--output", str(output_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 出力ファイルが存在する
        assert output_path.exists()
        
        # 出力ファイルの内容を確認
        with open(output_path, "r", encoding="utf-8") as f:
            output_data = json.load(f)
            assert output_data["value1"] == 100
            assert output_data["value2"] == 200
            assert output_data["text"] == "テスト"
    
    def test_output_to_stdout(self, setup_files):
        """標準出力オプションでの実行テスト（明示的に指定なし）"""
        excel_path = setup_files["excel_path"]
        yaml_config_path = setup_files["yaml_config_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(yaml_config_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力にデータが出力される
        try:
            output_data = json.loads(result.stdout)
            assert output_data["value1"] == 100
            assert output_data["value2"] == 200
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")
    
    def test_custom_schema(self, setup_files):
        """カスタムスキーマオプションでの実行テスト"""
        excel_path = setup_files["excel_path"]
        yaml_config_path = setup_files["yaml_config_path"]
        schema_path = setup_files["schema_path"]
        
        result = self.run_cli_command([
            str(excel_path),
            "--config", str(yaml_config_path),
            "--schema", str(schema_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力がJSON形式
        try:
            output_data = json.loads(result.stdout)
            assert output_data["value1"] == 100
            assert output_data["value2"] == 200
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")
    
    def test_include_empty_cells(self, setup_files):
        """空セルを含めるオプションでの実行テスト"""
        excel_path = setup_files["excel_path"]
        
        # 空セル含むフィールドの設定ファイル作成
        tmp_path = Path(excel_path).parent
        config_path = tmp_path / "empty_cells_config.yaml"
        config_data = {
            "fields": {
                "filled_cell": "Sheet1!A1",
                "empty_cell": "Sheet1!D4"
            },
            "rules": [],
            "output": {"format": "json"}
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)
        
        # 空セル含めないオプションなし実行
        result1 = self.run_cli_command([
            str(excel_path),
            "--config", str(config_path)
        ])
        
        # 終了コードが0（正常終了）
        assert result1.returncode == 0
        # 空セルは出力に含まれない
        output_data1 = json.loads(result1.stdout)
        assert "filled_cell" in output_data1
        assert "empty_cell" not in output_data1
        
        # 空セル含むオプション実行
        result2 = self.run_cli_command([
            str(excel_path),
            "--config", str(config_path),
            "--include-empty-cells"
        ])
        
        # 終了コードが0（正常終了）
        assert result2.returncode == 0
        # 空セルも出力に含まれる
        output_data2 = json.loads(result2.stdout)
        assert "filled_cell" in output_data2
        assert "empty_cell" in output_data2
        assert output_data2["empty_cell"] is None
    
    def test_ignore_errors(self, setup_files):
        """エラー無視オプションでの実行テスト"""
        invalid_config_path = setup_files["invalid_config_path"]
        excel_path = setup_files["excel_path"]
        
        # 無効な設定ファイルでエラー無視なしの場合
        result1 = self.run_cli_command([
            str(excel_path),
            "--config", str(invalid_config_path)
        ])
        
        # 終了コードが1（エラー終了）
        assert result1.returncode == 1
        assert "設定ファイルの検証に失敗" in result1.stderr
        
        # 無効な設定ファイルでエラー無視ありの場合
        result2 = self.run_cli_command([
            str(excel_path),
            "--config", str(invalid_config_path),
            "--ignore-errors"
        ])
        
        # エラーメッセージは出るが終了コードは0（正常終了）
        assert result2.returncode == 0
        assert "設定ファイルの読み込みに失敗" in result2.stderr
        assert "--ignore-errors オプションが指定されたため" in result2.stderr