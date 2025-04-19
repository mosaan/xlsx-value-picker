"""
バリデーション機能モジュール

このモジュールは、Excelファイルから取得した値が指定されたルールに従っているかを
検証するための機能を提供します。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union

@dataclass
class ValidationContext:
    """
    バリデーション実行時のコンテキスト情報を保持するクラス
    
    Attributes:
        cell_values: フィールド名とその値のマッピング
        field_locations: フィールド名とExcelセル位置のマッピング
    """
    cell_values: Dict[str, Any]
    field_locations: Dict[str, str]

    def get_field_value(self, field_name: str) -> Any:
        """指定されたフィールドの値を取得します"""
        return self.cell_values.get(field_name)

    def get_field_location(self, field_name: str) -> Optional[str]:
        """指定されたフィールドのセル位置を取得します"""
        return self.field_locations.get(field_name)


@dataclass
class ValidationResult:
    """
    バリデーション結果を表すクラス
    
    Attributes:
        is_valid: 検証が成功したかどうか
        error_message: エラーメッセージ（検証失敗時）
        error_fields: エラーが発生したフィールドのリスト
        error_locations: エラーが発生したセル位置のリスト
        severity: エラーの重要度（"error", "warning"など）
    """
    is_valid: bool
    error_message: Optional[str] = None
    error_fields: Optional[List[str]] = None
    error_locations: Optional[List[str]] = None
    severity: str = "error"

    def __post_init__(self):
        # error_fieldsが指定されていない場合は空のリストに初期化
        if not self.is_valid and self.error_fields is None:
            self.error_fields = []
        # error_locationsが指定されていない場合は空のリストに初期化
        if not self.is_valid and self.error_locations is None:
            self.error_locations = []


# Expressionクラスのインターフェース（抽象メソッド）
class IExpression(ABC):
    """バリデーション式のインターフェース"""
    
    @abstractmethod
    def validate(self, context: ValidationContext, error_message_template: str) -> ValidationResult:
        """
        ルール式の検証を行い結果を返す
        
        Args:
            context: バリデーションコンテキスト
            error_message_template: エラーメッセージのテンプレート
            
        Returns:
            ValidationResult: 検証結果
        """
        pass


class ValidationEngine:
    """
    バリデーションエンジン
    
    ルールリストに基づいてバリデーションを実行するエンジンです。
    """
    
    def __init__(self, rules: List['RuleModel']):
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
        context = ValidationContext(
            cell_values=cell_values,
            field_locations=field_mapping
        )
        
        # すべてのルールを評価
        results = []
        for rule in self.rules:
            result = rule.validate(context)
            if not result.is_valid:
                # エラー位置情報を追加
                if result.error_fields:
                    result.error_locations = [
                        field_mapping.get(field, "不明") 
                        for field in result.error_fields
                        if field in field_mapping
                    ]
                results.append(result)
        
        return results