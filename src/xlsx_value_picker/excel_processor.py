"""
設定に基づくExcelファイル処理機能
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import openpyxl

from .config_loader import ConfigModel


class ExcelValueExtractor:
    """設定に基づいてExcelファイルから値を抽出するクラス"""
    
    def __init__(self, excel_path: Union[str, Path]):
        """
        初期化

        Args:
            excel_path: Excelファイルのパス
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excelファイルが見つかりません: {excel_path}")
        
        # data_only=Trueは計算式の代わりに値を取得するために必要
        self.workbook = openpyxl.load_workbook(self.excel_path, data_only=True)
    
    def extract_values(self, config: ConfigModel, include_empty_cells: bool = False) -> Dict[str, Any]:
        """
        設定に基づいてExcelファイルから値を抽出する

        Args:
            config: 設定モデル
            include_empty_cells: 空セルを含めるかどうか

        Returns:
            Dict[str, Any]: フィールド名と値のマッピング
        """
        result = {}
        
        for field_name, cell_ref in config.fields.items():
            value = self._get_cell_value(cell_ref)
            
            # 空セルのチェック
            if value is None and not include_empty_cells:
                continue
                
            result[field_name] = value
        
        return result
    
    def _get_cell_value(self, cell_reference: str) -> Any:
        """
        セル参照から値を取得する

        Args:
            cell_reference: セル参照 (例: "Sheet1!A1")

        Returns:
            Any: セルの値

        Raises:
            ValueError: セル参照の形式が不正な場合
        """
        # シート名とセル位置を分離
        if "!" not in cell_reference:
            raise ValueError(f"無効なセル参照形式です: {cell_reference}")
            
        sheet_name, cell_addr = cell_reference.split("!", 1)
        
        # シートの取得
        try:
            sheet = self.workbook[sheet_name]
        except KeyError:
            raise ValueError(f"シートが見つかりません: {sheet_name}")
        
        # セルの値を取得
        try:
            return sheet[cell_addr].value
        except (ValueError, KeyError):
            raise ValueError(f"無効なセル参照です: {cell_addr}")
    
    def close(self):
        """ワークブックを閉じる"""
        self.workbook.close()