"""
設定に基づくExcelファイル処理機能
"""

from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

from .config_loader import ConfigModel
from .exceptions import ExcelProcessingError


class ExcelValueExtractor:
    """設定に基づいてExcelファイルから値を抽出するクラス"""

    def __init__(self, excel_path: str | Path):
        """
        初期化

        Args:
            excel_path: Excelファイルのパス
        """
        self.excel_path = Path(excel_path)
        self.workbook = None  # Initialize workbook to None

    def __enter__(self):
        """コンテキストマネージャの開始時にExcelファイルを開く"""
        if not self.excel_path.exists():
            raise ExcelProcessingError(f"Excelファイルが見つかりません: {self.excel_path}")
        try:
            # data_only=Trueは計算式の代わりに値を取得するために必要
            self.workbook = openpyxl.load_workbook(self.excel_path, data_only=True)
            return self
        except InvalidFileException as e:
            raise ExcelProcessingError(f"Excelファイル形式が無効です: {self.excel_path} - {e}")
        except Exception as e:
            raise ExcelProcessingError(f"Excelファイルの読み込み中に予期せぬエラーが発生しました: {self.excel_path} - {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャの終了時にワークブックを閉じる"""
        self.close()

    def extract_values(self, config: ConfigModel, include_empty_cells: bool = False) -> dict[str, Any]:
        """
        設定に基づいてExcelファイルから値を抽出する

        Args:
            config: 設定モデル
            include_empty_cells: 空セルを含めるかどうか

        Returns:
            Dict[str, Any]: フィールド名と値のマッピング

        Raises:
            ExcelProcessingError: ワークブックが開かれていない場合
        """
        if self.workbook is None:
            raise ExcelProcessingError("Excelワークブックが開かれていません。コンテキストマネージャを使用してください。")

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
            ExcelProcessingError: セル参照の形式が不正な場合、シートが見つからない場合、
                                  またはセル参照が無効な場合
        """
        if self.workbook is None:
            raise ExcelProcessingError("Excelワークブックが開かれていません。")

        # シート名とセル位置を分離
        if "!" not in cell_reference:
            raise ExcelProcessingError(f"無効なセル参照形式です: {cell_reference}")

        sheet_name, cell_addr = cell_reference.split("!", 1)

        # シートの取得
        try:
            sheet = self.workbook[sheet_name]
        except KeyError:
            raise ExcelProcessingError(f"シートが見つかりません: {sheet_name}")

        # セルの値を取得
        try:
            return sheet[cell_addr].value
        except (ValueError, KeyError):
            raise ExcelProcessingError(f"無効なセル参照です: {cell_addr}")

    def close(self):
        """ワークブックを閉じる"""
        if self.workbook:
            self.workbook.close()
            self.workbook = None


# ValidationEngine用の関数
def get_excel_values(excel_file: str, field_mapping: dict[str, str]) -> dict[str, Any]:
    """
    Excelファイルからフィールドマッピングに基づいて値を取得する

    Args:
        excel_file: Excelファイルのパス
        field_mapping: フィールド名とセル位置のマッピング

    Returns:
        Dict[str, Any]: フィールド名と値のマッピング

    Raises:
        Exception: Excel値の取得中にエラーが発生した場合
    """
    try:
        with ExcelValueExtractor(excel_file) as extractor:
            result = {}
            for field_name, cell_ref in field_mapping.items():
                value = extractor._get_cell_value(cell_ref)
                result[field_name] = value
            return result
    except ExcelProcessingError as e:
        # ValidationEngine は標準の Exception を期待している可能性があるため、
        # ここでは再送出せずにエラーメッセージを返すか、より汎用的な例外にラップする
        # 今回は元の実装に合わせて Exception を送出する
        raise Exception(f"Excel値の取得中にエラーが発生しました: {e}") from e
