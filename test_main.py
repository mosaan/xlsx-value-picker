import openpyxl
import pytest
import os
from main import get_excel_values

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
