"""
バリデーション機能モジュール

このモジュールは、Excelファイルから取得した値が指定されたルールに従っているかを
検証するための機能を提供します。
"""

from typing import Any, Dict, List, Optional, Union

# config_loader ではなく validation_common からクラスをインポート
from xlsx_value_picker.validation_common import ValidationContext, ValidationResult, IExpression

# 前方参照型を使ってRuleをインポート
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xlsx_value_picker.config_loader import Rule


class ValidationEngine:
    """
    バリデーションエンジン

    ルールリストに基づいてバリデーションを実行するエンジンです。
    """

    def __init__(self, rules: List["Rule"]):
        """
        初期化メソッド

        Args:
            rules: 検証に使用するルールのリスト
        """
        self.rules = rules

    def validate(self, excel_file: str, field_mapping: Dict[str, str]) -> List[ValidationResult]:
        """
        バリデーションを実行する

        Args:
            excel_file: Excelファイルのパス
            field_mapping: フィールド名とセル位置のマッピング

        Returns:
            ValidationResultのリスト（エラーがなければ空リスト）
        """
        from .excel_processor import get_excel_values

        # Excelから値を取得
        cell_values = get_excel_values(excel_file, field_mapping)

        # コンテキストを構築
        context = ValidationContext(cell_values=cell_values, field_locations=field_mapping)

        # すべてのルールを評価
        results = []
        for rule in self.rules:
            result = rule.validate(context)
            if not result.is_valid:
                # エラー位置情報を追加
                if result.error_fields:
                    result.error_locations = [
                        field_mapping.get(field, "不明") for field in result.error_fields if field in field_mapping
                    ]
                results.append(result)

        return results
