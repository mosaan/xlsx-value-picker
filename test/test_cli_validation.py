"""
CLIインターフェースのバリデーション機能テスト
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
                "expression": {"compare": {"left_field": "age", "operator": ">=", "right": 18}},
                "error_message": "{field}は18歳以上である必要があります（現在: {left_value}歳）",
            },
            {
                "name": "その他選択時コメント必須",
                "expression": {
                    "any_of": [
                        {"compare": {"left_field": "selection", "operator": "!=", "right": "その他"}},
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
                "expression": {"compare": {"left_field": "age", "operator": ">=", "right": 18}},
                "error_message": "{field}は18歳以上である必要があります（現在: {left_value}歳）",
            },
            {
                "name": "その他選択時コメント必須",
                "expression": {
                    "any_of": [
                        {"compare": {"left_field": "selection", "operator": "!=", "right": "その他"}},
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


class TestCLIValidation:
    """CLIインターフェースのバリデーション機能テスト"""

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

    def test_validation_success(self, setup_files):
        """バリデーション成功時のテスト"""
        excel_path = setup_files["excel_path"]
        validation_config_path = setup_files["validation_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [str(excel_path), "--config", str(validation_config_path)]  # --schema を削除
        )

        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力がJSON形式
        try:
            output_data = json.loads(result.stdout)
            assert output_data["email"] == "test@example.com"
            assert output_data["age"] == 20
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")

    def test_validation_failure(self, setup_files):
        """バリデーション失敗時のテスト"""
        excel_path = setup_files["excel_path"]
        failing_validation_config_path = setup_files["failing_validation_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [str(excel_path), "--config", str(failing_validation_config_path)]  # --schema を削除
        )

        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # エラーメッセージにバリデーションエラーが含まれる
        assert "バリデーションエラーが" in result.stderr
        assert "emailの形式が不正です" in result.stderr
        assert "ageは18歳以上である必要があります" in result.stderr
        assert "「その他」を選択した場合はコメントが必須です" in result.stderr
        # 追加された終了メッセージの確認
        assert "バリデーションエラーが発生したため、処理を中止します" in result.stderr
        assert "エラーを無視して処理を継続するには --ignore-errors オプションを指定してください" in result.stderr

    def test_validation_only_mode_success(self, setup_files):
        """バリデーションのみモード成功時のテスト"""
        excel_path = setup_files["excel_path"]
        validation_config_path = setup_files["validation_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [str(excel_path), "--config", str(validation_config_path), "--validate-only"]  # --schema を削除
        )

        # 終了コードが0（正常終了）
        assert result.returncode == 0
        # 標準出力は空（バリデーションのみモードでは出力なし）
        assert not result.stdout.strip()
        # 標準エラー出力にバリデーション成功メッセージが含まれる
        assert "バリデーションに成功しました" in result.stderr

    def test_validation_only_mode_failure(self, setup_files):
        """バリデーションのみモード失敗時のテスト"""
        excel_path = setup_files["excel_path"]
        failing_validation_config_path = setup_files["failing_validation_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [
                str(excel_path),
                "--config",
                str(failing_validation_config_path),
                # "--schema", str(schema_path), # 削除
                "--validate-only",
            ]
        )

        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # 標準出力は空（バリデーションのみモードでは出力なし）
        assert not result.stdout.strip()
        # 標準エラー出力にバリデーションエラーが含まれる
        assert "バリデーションエラーが" in result.stderr
        # 追加された終了メッセージの確認
        assert "バリデーションのみモードで実行しました (エラーあり)" in result.stderr

    def test_validation_log_output(self, setup_files):
        """バリデーションログ出力のテスト"""
        excel_path = setup_files["excel_path"]
        failing_validation_config_path = setup_files["failing_validation_config_path"]
        log_path = setup_files["log_path"]
        # schema_path = setup_files["schema_path"] # 削除

        result = self.run_cli_command(
            [
                str(excel_path),
                "--config",
                str(failing_validation_config_path),
                # "--schema", str(schema_path), # 削除
                "--log",
                str(log_path),
            ]
        )

        # 終了コードが1（エラー終了）
        assert result.returncode == 1
        # ログファイルが存在する
        assert Path(log_path).exists()

        # ログファイルの内容を検証
        with open(log_path, encoding="utf-8") as f:
            log_data = json.load(f)
            assert log_data["is_valid"] is False
            assert "validation_results" in log_data
            assert len(log_data["validation_results"]) > 0
            assert log_data["error_count"] > 0

            # 少なくとも1つのバリデーション結果に適切な情報が含まれているか
            result_log = log_data["validation_results"][0]  # 変数名を変更 (result は subprocess の結果と衝突)
            assert "is_valid" in result_log
            assert "error_message" in result_log
            assert "error_fields" in result_log
            assert "error_locations" in result_log
        # 追加された終了メッセージの確認
        assert "バリデーションエラーが発生したため、処理を中止します" in result.stderr
        assert "エラーを無視して処理を継続するには --ignore-errors オプションを指定してください" in result.stderr

    def test_ignore_errors_with_validation(self, setup_files):
        """バリデーション失敗時のエラー無視オプションテスト"""
        excel_path = setup_files["excel_path"]
        failing_validation_config_path = setup_files["failing_validation_config_path"]
        # schema_path = setup_files["schema_path"] # 削除

        # エラー無視なしの場合
        result1 = self.run_cli_command(
            [str(excel_path), "--config", str(failing_validation_config_path)]  # --schema を削除
        )

        # 終了コードが1（エラー終了）
        assert result1.returncode == 1

        # エラー無視ありの場合
        result2 = self.run_cli_command(
            [
                str(excel_path),
                "--config",
                str(failing_validation_config_path),
                # "--schema", str(schema_path), # 削除
                "--ignore-errors",
            ]
        )

        # 終了コードが0（正常終了）
        assert result2.returncode == 0
        # バリデーションエラーメッセージは表示される
        assert "バリデーションエラーが" in result2.stderr
        # エラー無視メッセージが表示される
        assert (
            "--ignore-errors オプションが指定されたため、バリデーションエラーを無視して処理を継続します"
            in result2.stderr
        )  # メッセージ変更
        # 出力データも取得できる
        try:
            json.loads(result2.stdout)
        except json.JSONDecodeError:
            pytest.fail("標準出力がJSON形式ではありません")
