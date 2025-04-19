"""
Excel処理機能のテスト
"""

import sys
from pathlib import Path

import openpyxl
import pytest

# テスト対象モジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xlsx_value_picker.config_loader import ConfigModel, OutputFormat
from xlsx_value_picker.excel_processor import ExcelValueExtractor


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


class TestExcelValueExtractor:
    """ExcelValueExtractorのテスト"""
    
    @pytest.fixture
    def excel_file(self, tmp_path):
        """テスト用のExcelファイルを作成して、そのパスを返す"""
        excel_path = tmp_path / "test.xlsx"
        create_test_excel(excel_path)
        return str(excel_path)
    
    def test_init(self, excel_file):
        """初期化が正しく行われることをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        assert extractor.excel_path.name == "test.xlsx"
        assert extractor.workbook is not None
        
    def test_init_nonexistent_file(self):
        """存在しないファイルで初期化するとFileNotFoundErrorが発生することをテスト"""
        with pytest.raises(FileNotFoundError):
            ExcelValueExtractor("nonexistent.xlsx")
    
    def test_extract_values(self, excel_file):
        """設定に基づいて値を正しく抽出できることをテスト"""
        # テスト用の設定モデルを作成
        config = ConfigModel(
            fields={
                "value1": "Sheet1!A1",
                "value2": "Sheet1!B2",
                "text": "Sheet1!C3",
                "sheet2_value": "Sheet2!A1"
            },
            rules=[],
            output=OutputFormat(format="json")
        )
        
        # 値の抽出
        extractor = ExcelValueExtractor(excel_file)
        result = extractor.extract_values(config)
        
        # 検証
        assert result["value1"] == 100
        assert result["value2"] == 200
        assert result["text"] == "テスト"
        assert result["sheet2_value"] == "Sheet2値1"
    
    def test_extract_values_empty_cell(self, excel_file):
        """空セルを含める/含めないオプションが正しく動作することをテスト"""
        # テスト用の設定モデルを作成
        config = ConfigModel(
            fields={
                "empty_cell": "Sheet1!D4",
                "non_empty_cell": "Sheet1!A1"
            },
            rules=[],
            output=OutputFormat(format="json")
        )
        
        extractor = ExcelValueExtractor(excel_file)
        
        # デフォルト（空セルを含めない）
        result1 = extractor.extract_values(config)
        assert "empty_cell" not in result1
        assert "non_empty_cell" in result1
        
        # 空セルを含める
        result2 = extractor.extract_values(config, include_empty_cells=True)
        assert "empty_cell" in result2
        assert result2["empty_cell"] is None
        assert result2["non_empty_cell"] == 100
    
    def test_get_cell_value(self, excel_file):
        """_get_cell_valueが正しく値を取得できることをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        
        # 正常なセル参照
        assert extractor._get_cell_value("Sheet1!A1") == 100
        assert extractor._get_cell_value("Sheet1!C3") == "テスト"
        assert extractor._get_cell_value("Sheet2!B2") == "Sheet2値2"
        
        # 空セル
        assert extractor._get_cell_value("Sheet1!D4") is None
    
    def test_get_cell_value_invalid_sheet(self, excel_file):
        """存在しないシートを参照するとValueErrorが発生することをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        
        with pytest.raises(ValueError) as excinfo:
            extractor._get_cell_value("NonExistentSheet!A1")
        
        assert "シートが見つかりません" in str(excinfo.value)
    
    def test_get_cell_value_invalid_format(self, excel_file):
        """不正なセル参照形式でValueErrorが発生することをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        
        with pytest.raises(ValueError) as excinfo:
            extractor._get_cell_value("InvalidFormat")
        
        assert "無効なセル参照形式" in str(excinfo.value)
    
    def test_get_cell_value_invalid_cell(self, excel_file):
        """不正なセル位置を参照するとValueErrorが発生することをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        
        with pytest.raises(ValueError) as excinfo:
            extractor._get_cell_value("Sheet1!InvalidCell")
        
        assert "無効なセル参照" in str(excinfo.value)
    
    def test_close(self, excel_file):
        """closeメソッドが正しく呼び出せることをテスト"""
        extractor = ExcelValueExtractor(excel_file)
        # closeの呼び出しでエラーが発生しないことを確認
        extractor.close()