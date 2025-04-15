import openpyxl
import sys
import json
from main import get_excel_values
from pathlib import Path
import subprocess

def create_sample_excel(path):
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Sheet1"
    ws1['A1'] = 123
    ws1['B2'] = "=SUM(1, 2)"
    ws2 = wb.create_sheet("Sheet2")
    ws2['C3'] = "abc"
    wb.save(path)

def test_get_excel_values(tmp_path):
    excel_path = tmp_path / "sample.xlsx"
    create_sample_excel(excel_path)
    value_specs = [
        {"sheet": "Sheet1", "cell": "A1", "name": "value1"},
        {"sheet": "Sheet1", "cell": "B2", "name": "value2"},
        {"sheet": "Sheet2", "cell": "C3", "name": "value3"},
    ]
    result = get_excel_values(str(excel_path), value_specs)
    assert result["value1"] == 123
    # openpyxlの仕様上、式セルの値はNoneになる
    assert result["value2"] is None
    assert result["value3"] == "abc"

def test_get_excel_values_sheet_index(tmp_path):
    excel_path = tmp_path / "sample.xlsx"
    create_sample_excel(excel_path)
    value_specs = [
        {"sheet": "*1", "cell": "A1", "name": "value1"},  # Sheet1
        {"sheet": "*2", "cell": "C3", "name": "value2"},  # Sheet2
    ]
    result = get_excel_values(str(excel_path), value_specs)
    assert result["value1"] == 123
    assert result["value2"] == "abc"

def test_main_output_file_and_stdout(tmp_path):
    # Excelファイルと設定ファイルを作成
    excel_path = tmp_path / "sample.xlsx"
    create_sample_excel(excel_path)
    config_path = tmp_path / "config.yaml"
    config = f"""\
excel_file: {excel_path}
values:
  - sheet: Sheet1
    cell: A1
    name: value1
  - sheet: Sheet2
    cell: C3
    name: value2
"""
    config_path.write_text(config, encoding="utf-8")
    # 出力ファイル指定
    output_path = tmp_path / "result.json"
    result = subprocess.run([
        sys.executable, "main.py", "--config", str(config_path), "--output", str(output_path)
    ], cwd=Path(__file__).parent, capture_output=True, encoding="utf-8")
    assert output_path.exists()
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["value1"] == 123
    assert data["value2"] == "abc"
    # 標準出力（--output未指定）
    result = subprocess.run([
        sys.executable, "main.py", "--config", str(config_path)
    ], cwd=Path(__file__).parent, capture_output=True, encoding="utf-8")
    # 出力をJSONとしてパースし値を比較
    stdout_json = json.loads(result.stdout)
    assert stdout_json["value1"] == 123
    assert stdout_json["value2"] == "abc"

def test_get_excel_values_named_cell(tmp_path):
    excel_path = tmp_path / "sample.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws['A1'] = 999
    # 名前付きセルを新APIで追加（openpyxl 3.1以降推奨）
    from openpyxl.workbook.defined_name import DefinedName
    dn = DefinedName('MY_CELL', attr_text=f"'{ws.title}'!$A$1")
    wb.defined_names.add(dn)
    wb.save(excel_path)
    value_specs = [
        {"named_cell": "MY_CELL", "name": "foo"},
    ]
    result = get_excel_values(str(excel_path), value_specs)
    assert result["foo"] == 999
