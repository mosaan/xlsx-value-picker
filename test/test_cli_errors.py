"""
CLIインターフェースのエラーハンドリングテスト
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

    # バリデーションテスト用
    ws1["E1"] = "test@example.com"  # 有効なメールアドレス
    ws1["E2"] = "invalid-email"  # 無効なメールアドレス
    ws1["F1"] = 20  # 有効な年齢
    ws1["F2"] = 15  # 無効な年齢
    ws1["G1"] = "その他"  # 選択肢
    ws1["G2"] = "コメント"  # コメント（有効）

    ws2 = wb.create_sheet("Sheet2")
    ws2["A1"] = "Sheet2値1"
    ws2["B2"] = "Sheet2値2"

    wb.save(path)


def create_valid_config_yaml(path, excel_path):
    """有効なYAML設定ファイルを作成する"""
    config_data = {
        "fields": {"value1": "Sheet1!A1", "value2": "Sheet1!B2", "text": "Sheet1!C3", "sheet2_value": "Sheet2!A1"},
        "rules": [
            {
                "name": "テストルール",
                "expression": {"field": "value1", "required": True},
                "error_message": "値1は必須です",
            }
        ],
        "output": {"format": "json"},
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)


def create_valid_config_json(path, excel_path):
    """有効なJSON設定ファイルを作成する"""
    config_data = {
        "fields": {"value1": "Sheet1!A1", "value2": "Sheet1!B2", "text": "Sheet1!C3"},
        "rules": [
            {
                "name": "テストルール",
                "expression": {"field": "value1", "required": True},
                "error_message": "値1は必須です",
            }
        ],
        "output": {"format": "json"},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)


def create_invalid_config_yaml(path):
    """無効なYAML設定ファイルを作成する (スキーマ違反)"""
    config_data = {
        "fields": {
            "value1": "InvalidFormat"  # スキーマ違反 (pattern)
        },
        "rules": [],
        # output が必須なのにない (required違反)
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)


def create_config_with_validation_yaml(path):
    """バリデーションルールを含むYAML設定ファイルを作成する"""
    config_data = {
        "fields": {"email": "Sheet1!E1", "age": "Sheet1!F1", "selection": "Sheet1!G1", "comment": "Sheet1!G2"},
        "rules": [
            {
                "name": "メールアドレス形式チェック",
                "expression": {"regex_match": {"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}},
                "error_message": "{field}の形式が不正です: {value}",
            },
            {
                "name": "年齢チェック",
                "expression": {"compare": {"left": "age", "operator": ">=", "right": 18}},
                "error_message": "{field}は18歳以上である必要があります（現在: {left_value}歳）",
            },
            {
                "name": "その他選択時コメント必須",
                "expression": {
                    "any_of": [
                        {"compare": {"left": "selection", "operator": "!=", "right": "その他"}},
                        {"field": "comment", "required": True},
                    ]
                },
                "error_message": "「その他」を選択した場合はコメントが必須です",
            },
        ],
        "output": {"format": "json"},
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)


def create_config_with_failing_validation_yaml(path):
    """バリデーションが失敗するYAML設定ファイルを作成する"""
    config_data = {
        "fields": {
            "email": "Sheet1!E2",  # 無効なメールアドレス
            "age": "Sheet1!F2",  # 無効な年齢
            "selection": "Sheet1!G1",  # その他
            "comment": "Sheet1!D4",  # 空セル
        },
        "rules": [
            {
                "name": "メールアドレス形式チェック",
                "expression": {"regex_match": {"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}},
                "error_message": "{field}の形式が不正です: {value}",
            },
            {
                "name": "年齢チェック",
                "expression": {"compare": {"left": "age", "operator": ">=", "right": 18}},
                "error_message": "{field}は18歳以上である必要があります（現在: {left_value}歳）",
            },
            {
                "name": "その他選択時コメント必須",
                "expression": {
                    "any_of": [
                        {"compare": {"left": "selection", "operator": "!=", "right": "その他"}},
                        {"field": "comment", "required": True},
                    ]
                },
                "error_message": "「その他」を選択した場合はコメントが必須です",
            },
        ],
        "output": {"format": "json"},
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)


def create_test_schema(path):
    """テスト用のスキーマファイルを作成する"""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "fields": {"type": "object", "additionalProperties": {"type": "string", "pattern": "^[^!]+![A-Z]+[0-9]+$"}},
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
            "output": {  # output を必須にする
                "type": "object",
                "properties": {"format": {"type": "string", "enum": ["json", "yaml", "csv"]}},
                "required": ["format"],
            },
        },
        "required": ["fields", "rules", "output"],  # output を必須にする
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


class TestCLIErrors:
    """CLIインターフェースのエラーハンドリングテスト"""

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

        # バリデーションルール含む設定ファイル
        validation_config_path = tmp_path / "validation_config.yaml"
        create_config_with_validation_yaml(validation_config_path)

        # バリデーションが失敗する設定ファイル
        failing_validation_config_path = tmp_path / "failing_validation_config.yaml"
        create_config_with_failing_validation_yaml(failing_validation_config_path)

        # スキーマファイル
        schema_path = tmp_path / "test_schema.json"
        create_test_schema(schema_path)

        # ログファイルパス
        log_path = tmp_path / "validation_log.json"

        return {
            "excel_path": excel_path,
            "yaml_config_path": yaml_config_path,
            "json_config_path": json_config_path,
            "invalid_config_path": invalid_config_path,
            "validation_config_path": validation_config_path,
            "failing_validation_config_path": failing_validation_config_path,
            "schema_path": schema_path,
            "log_path": log_path,
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
            env=env,
        )

    def test_invalid_config(self, setup_files):
        """無効な設定ファイルでの実行テスト (スキーマ違反)"""
        excel_path = setup_files["excel_path"]
        invalid_config_path = setup_files["invalid_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [str(excel_path), "--config", str(invalid_config_path)] # --schema を削除
        )

        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # エラーメッセージに「設定ファイルの検証に失敗しました」が含まれる (cli.pyの修正による変更)
        assert "設定ファイルの検証に失敗しました" in result.stderr
        # Pydantic の検証エラーメッセージを確認
        assert "無効なセル参照形式です" in result.stderr
        assert "InvalidFormat" in result.stderr

    def test_nonexistent_excel(self, setup_files):
        """存在しないExcelファイルでの実行テスト"""
        yaml_config_path = setup_files["yaml_config_path"]

        result = self.run_cli_command(["nonexistent.xlsx", "--config", str(yaml_config_path)])

        # 終了コードが2（Click自体のバリデーションエラー終了）
        assert result.returncode == 2
        # エラーメッセージに「File 'nonexistent.xlsx' does not exist」が含まれる
        assert "File 'nonexistent.xlsx' does not exist" in result.stderr

    def test_nonexistent_config(self, setup_files):
        """存在しない設定ファイルでの実行テスト"""
        excel_path = setup_files["excel_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [str(excel_path), "--config", "nonexistent_config.yaml"] # --schema を削除
        )

        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # エラーメッセージに「設定ファイルの読み込みに失敗しました」が含まれる
        assert "設定ファイルの読み込みに失敗しました" in result.stderr
        assert "nonexistent_config.yaml" in result.stderr  # ファイル名が含まれるか