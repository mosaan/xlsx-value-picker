"""
バリデーション機能のテスト
"""

import unittest
from unittest.mock import patch, Mock

# validation.py と validation_common.py からクラスをインポート
from xlsx_value_picker.validation_common import ValidationContext, ValidationResult
from xlsx_value_picker.validation import ValidationEngine
from xlsx_value_picker.config_loader import (
    CompareExpression,
    RequiredExpression,
    RegexMatchExpression,
    EnumExpression,
    AllOfExpression,
    AnyOfExpression,
    NotExpression,
    Rule,
)


class TestValidationContext(unittest.TestCase):
    """ValidationContextのテスト"""

    def test_get_field_value(self):
        """get_field_valueメソッドのテスト"""
        context = ValidationContext(
            cell_values={"name": "山田太郎", "age": 30}, field_locations={"name": "Sheet1!A1", "age": "Sheet1!B1"}
        )
        self.assertEqual(context.get_field_value("name"), "山田太郎")
        self.assertEqual(context.get_field_value("age"), 30)
        self.assertIsNone(context.get_field_value("unknown"))

    def test_get_field_location(self):
        """get_field_locationメソッドのテスト"""
        context = ValidationContext(
            cell_values={"name": "山田太郎", "age": 30}, field_locations={"name": "Sheet1!A1", "age": "Sheet1!B1"}
        )
        self.assertEqual(context.get_field_location("name"), "Sheet1!A1")
        self.assertEqual(context.get_field_location("age"), "Sheet1!B1")
        self.assertIsNone(context.get_field_location("unknown"))


class TestValidationResult(unittest.TestCase):
    """ValidationResultのテスト"""

    def test_post_init_with_valid_result(self):
        """有効な結果の初期化テスト"""
        result = ValidationResult(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.error_fields)
        self.assertIsNone(result.error_locations)
        self.assertEqual(result.severity, "error")  # デフォルト値

    def test_post_init_with_invalid_result(self):
        """無効な結果の初期化テスト"""
        result = ValidationResult(is_valid=False, error_message="エラーが発生しました")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "エラーが発生しました")
        self.assertEqual(result.error_fields, [])  # 空のリストに初期化される
        self.assertEqual(result.error_locations, [])  # 空のリストに初期化される
        self.assertEqual(result.severity, "error")


class TestCompareExpression(unittest.TestCase):
    """CompareExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"age": 30, "price": 1000, "name": "テスト"},
            field_locations={"age": "Sheet1!A1", "price": "Sheet1!B1", "name": "Sheet1!C1"},
        )

    def test_equal_operator_valid(self):
        """==演算子のテスト（有効）"""
        expr = CompareExpression(compare={"left": "age", "operator": "==", "right": 30})
        result = expr.validate(self.context, "値が一致しません: {left_field}={left_value}, 期待値={right_value}")
        self.assertTrue(result.is_valid)

    def test_equal_operator_invalid(self):
        """==演算子のテスト（無効）"""
        expr = CompareExpression(compare={"left": "age", "operator": "==", "right": 40})
        result = expr.validate(self.context, "値が一致しません: {left_field}={left_value}, 期待値={right_value}")
        self.assertFalse(result.is_valid)
        self.assertIn("値が一致しません", result.error_message)
        self.assertEqual(result.error_fields, ["age"])

    def test_not_equal_operator(self):
        """!=演算子のテスト"""
        expr = CompareExpression(compare={"left": "age", "operator": "!=", "right": 40})
        result = expr.validate(self.context, "エラーメッセージ")
        self.assertTrue(result.is_valid)

        expr = CompareExpression(compare={"left": "age", "operator": "!=", "right": 30})
        result = expr.validate(self.context, "値が一致しています: {left_field}={left_value}")
        self.assertFalse(result.is_valid)
        self.assertIn("値が一致しています", result.error_message)

    def test_greater_than_operator(self):
        """>演算子のテスト"""
        expr = CompareExpression(compare={"left": "age", "operator": ">", "right": 20})
        result = expr.validate(self.context, "エラーメッセージ")
        self.assertTrue(result.is_valid)

        expr = CompareExpression(compare={"left": "age", "operator": ">", "right": 30})
        result = expr.validate(self.context, "値が小さすぎます: {left_field}={left_value}, 最小値={right_value}")
        self.assertFalse(result.is_valid)
        self.assertIn("値が小さすぎます", result.error_message)

    def test_greater_than_or_equal_operator(self):
        """>=演算子のテスト"""
        expr = CompareExpression(compare={"left": "age", "operator": ">=", "right": 30})
        result = expr.validate(self.context, "エラーメッセージ")
        self.assertTrue(result.is_valid)

        expr = CompareExpression(compare={"left": "age", "operator": ">=", "right": 31})
        result = expr.validate(self.context, "値が小さすぎます: {left_field}={left_value}, 最小値={right_value}")
        self.assertFalse(result.is_valid)

    def test_less_than_operator(self):
        """<演算子のテスト"""
        expr = CompareExpression(compare={"left": "age", "operator": "<", "right": 40})
        result = expr.validate(self.context, "エラーメッセージ")
        self.assertTrue(result.is_valid)

        expr = CompareExpression(compare={"left": "age", "operator": "<", "right": 30})
        result = expr.validate(self.context, "値が大きすぎます: {left_field}={left_value}, 最大値={right_value}")
        self.assertFalse(result.is_valid)

    def test_less_than_or_equal_operator(self):
        """<=演算子のテスト"""
        expr = CompareExpression(compare={"left": "age", "operator": "<=", "right": 30})
        result = expr.validate(self.context, "エラーメッセージ")
        self.assertTrue(result.is_valid)

        expr = CompareExpression(compare={"left": "age", "operator": "<=", "right": 29})
        result = expr.validate(self.context, "値が大きすぎます: {left_field}={left_value}, 最大値={right_value}")
        self.assertFalse(result.is_valid)

    def test_invalid_comparison(self):
        """無効な比較のテスト（異なる型など）"""
        expr = CompareExpression(compare={"left": "name", "operator": "<", "right": 100})
        result = expr.validate(self.context, "比較が不可能です: {left_field}={left_value}")
        self.assertFalse(result.is_valid)


class TestRequiredExpression(unittest.TestCase):
    """RequiredExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"name": "テスト", "empty": "", "none": None},
            field_locations={"name": "Sheet1!A1", "empty": "Sheet1!B1", "none": "Sheet1!C1", "missing": "Sheet1!D1"},
        )

    def test_required_valid(self):
        """必須項目のテスト（有効）"""
        expr = RequiredExpression(field="name", required=True)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertTrue(result.is_valid)

    def test_required_invalid_empty_string(self):
        """必須項目のテスト（無効 - 空文字列）"""
        expr = RequiredExpression(field="empty", required=True)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "emptyは必須項目です")
        self.assertEqual(result.error_fields, ["empty"])

    def test_required_invalid_none(self):
        """必須項目のテスト（無効 - None）"""
        expr = RequiredExpression(field="none", required=True)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_fields, ["none"])

    def test_required_invalid_missing(self):
        """必須項目のテスト（無効 - フィールドなし）"""
        expr = RequiredExpression(field="missing", required=True)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_fields, ["missing"])

    def test_not_required(self):
        """必須ではない項目のテスト"""
        expr = RequiredExpression(field="empty", required=False)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertTrue(result.is_valid)

        expr = RequiredExpression(field="none", required=False)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertTrue(result.is_valid)

        expr = RequiredExpression(field="missing", required=False)
        result = expr.validate(self.context, "{field}は必須項目です")
        self.assertTrue(result.is_valid)


class TestRegexMatchExpression(unittest.TestCase):
    """RegexMatchExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={
                "email": "test@example.com",
                "phone": "090-1234-5678",
                "number": 12345,
                "empty": "",
                "none": None,
            },
            field_locations={
                "email": "Sheet1!A1",
                "phone": "Sheet1!B1",
                "number": "Sheet1!C1",
                "empty": "Sheet1!D1",
                "none": "Sheet1!E1",
            },
        )

    def test_regex_match_valid(self):
        """正規表現マッチのテスト（有効）"""
        expr = RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"})
        result = expr.validate(self.context, "{field}のフォーマットが不正です")
        self.assertTrue(result.is_valid)

    def test_regex_match_invalid(self):
        """正規表現マッチのテスト（無効）"""
        expr = RegexMatchExpression(regex_match={"field": "phone", "pattern": r"^\d{10,11}$"})
        result = expr.validate(self.context, "{field}のフォーマットが不正です: {value}")
        self.assertFalse(result.is_valid)
        self.assertIn("phoneのフォーマットが不正です", result.error_message)
        self.assertEqual(result.error_fields, ["phone"])

    def test_regex_match_with_number(self):
        """数値に対する正規表現マッチのテスト"""
        expr = RegexMatchExpression(regex_match={"field": "number", "pattern": r"^\d{5}$"})
        result = expr.validate(self.context, "{field}のフォーマットが不正です")
        self.assertTrue(result.is_valid)  # 文字列に変換されてマッチする

    def test_regex_match_with_empty(self):
        """空文字列に対する正規表現マッチのテスト"""
        expr = RegexMatchExpression(regex_match={"field": "empty", "pattern": r".*"})
        result = expr.validate(self.context, "{field}のフォーマットが不正です")
        self.assertTrue(result.is_valid)  # 空文字列はスキップされる

    def test_regex_match_with_none(self):
        """Noneに対する正規表現マッチのテスト"""
        expr = RegexMatchExpression(regex_match={"field": "none", "pattern": r".*"})
        result = expr.validate(self.context, "{field}のフォーマットが不正です")
        self.assertTrue(result.is_valid)  # Noneはスキップされる


class TestEnumExpression(unittest.TestCase):
    """EnumExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"color": "赤", "number": 1, "empty": "", "none": None},
            field_locations={"color": "Sheet1!A1", "number": "Sheet1!B1", "empty": "Sheet1!C1", "none": "Sheet1!D1"},
        )

    def test_enum_valid(self):
        """列挙型のテスト（有効）"""
        expr = EnumExpression(enum={"field": "color", "values": ["赤", "青", "緑"]})
        result = expr.validate(self.context, "{field}に無効な値が指定されています: {value}")
        self.assertTrue(result.is_valid)

    def test_enum_invalid(self):
        """列挙型のテスト（無効）"""
        expr = EnumExpression(enum={"field": "color", "values": ["青", "緑"]})
        result = expr.validate(self.context, "{field}に無効な値が指定されています: {value}")
        self.assertFalse(result.is_valid)
        self.assertIn("colorに無効な値が指定されています", result.error_message)
        self.assertEqual(result.error_fields, ["color"])

    def test_enum_with_number(self):
        """数値に対する列挙型のテスト"""
        expr = EnumExpression(enum={"field": "number", "values": [1, 2, 3]})
        result = expr.validate(self.context, "{field}に無効な値が指定されています")
        self.assertTrue(result.is_valid)

    def test_enum_with_none(self):
        """Noneに対する列挙型のテスト"""
        expr = EnumExpression(enum={"field": "none", "values": ["値1", "値2"]})
        result = expr.validate(self.context, "{field}に無効な値が指定されています")
        self.assertTrue(result.is_valid)  # Noneはスキップされる


class TestAllOfExpression(unittest.TestCase):
    """AllOfExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"age": 25, "name": "テスト", "email": "test@example.com"},
            field_locations={"age": "Sheet1!A1", "name": "Sheet1!B1", "email": "Sheet1!C1"},
        )

    def test_all_of_valid(self):
        """すべての条件が有効な場合のテスト"""
        expr = AllOfExpression(
            all_of=[
                CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
                RequiredExpression(field="name", required=True),
                RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
            ]
        )
        result = expr.validate(self.context, "すべての条件を満たしていません")
        self.assertTrue(result.is_valid)

    def test_all_of_invalid(self):
        """一部の条件が無効な場合のテスト"""
        expr = AllOfExpression(
            all_of=[
                CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
                RequiredExpression(field="name", required=True),
            ]
        )
        result = expr.validate(self.context, "すべての条件を満たしていません")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "すべての条件を満たしていません")
        self.assertEqual(result.error_fields, ["age"])

    def test_all_of_multiple_invalid(self):
        """複数の条件が無効な場合のテスト"""
        expr = AllOfExpression(
            all_of=[
                CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
                RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w]+$"}),
            ]
        )
        result = expr.validate(self.context, "すべての条件を満たしていません")
        self.assertFalse(result.is_valid)
        self.assertEqual(set(result.error_fields), {"age", "email"})


class TestAnyOfExpression(unittest.TestCase):
    """AnyOfExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"age": 25, "name": "", "email": "invalid"},
            field_locations={"age": "Sheet1!A1", "name": "Sheet1!B1", "email": "Sheet1!C1"},
        )

    def test_any_of_valid(self):
        """いずれかの条件が有効な場合のテスト"""
        expr = AnyOfExpression(
            any_of=[
                CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
                RequiredExpression(field="name", required=True),
                RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
            ]
        )
        result = expr.validate(self.context, "いずれかの条件を満たす必要があります")
        self.assertTrue(result.is_valid)

    def test_any_of_all_invalid(self):
        """すべての条件が無効な場合のテスト"""
        expr = AnyOfExpression(
            any_of=[
                CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
                RequiredExpression(field="name", required=True),
                RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
            ]
        )
        result = expr.validate(self.context, "いずれかの条件を満たす必要があります")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "いずれかの条件を満たす必要があります")
        self.assertEqual(set(result.error_fields), {"age", "name", "email"})


class TestNotExpression(unittest.TestCase):
    """NotExpressionのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"age": 25, "status": "inactive"}, field_locations={"age": "Sheet1!A1", "status": "Sheet1!B1"}
        )

    def test_not_valid(self):
        """否定条件が有効な場合のテスト（内部条件が無効）"""
        expr = NotExpression(not_=CompareExpression(compare={"left": "age", "operator": "<", "right": 20}))
        result = expr.validate(self.context, "条件に合致してはいけません")
        self.assertTrue(result.is_valid)

    def test_not_invalid(self):
        """否定条件が無効な場合のテスト（内部条件が有効）"""
        expr = NotExpression(not_=CompareExpression(compare={"left": "age", "operator": ">", "right": 20}))
        result = expr.validate(self.context, "条件に合致してはいけません")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "条件に合致してはいけません")
        # NotExpressionはエラーフィールドを指定しない
        self.assertEqual(result.error_fields, [])


class TestRule(unittest.TestCase):
    """Ruleのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.context = ValidationContext(
            cell_values={"age": 25, "email": "test@example.com"},
            field_locations={"age": "Sheet1!A1", "email": "Sheet1!B1"},
        )

    def test_rule_valid(self):
        """ルールが有効な場合のテスト"""
        rule = Rule(
            name="年齢チェック",
            expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
            error_message="{field}は20以上である必要があります",
        )
        result = rule.validate(self.context)
        self.assertTrue(result.is_valid)

    def test_rule_invalid(self):
        """ルールが無効な場合のテスト"""
        rule = Rule(
            name="年齢チェック",
            expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
            error_message="{field}は30以上である必要があります",
        )
        result = rule.validate(self.context)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_message, "ageは30以上である必要があります")
        # rule_nameが追加されている
        self.assertEqual(result.rule_name, "年齢チェック")


class TestValidationEngine(unittest.TestCase):
    """ValidationEngineのテスト"""

    @patch('xlsx_value_picker.excel_processor.get_excel_values')
    def test_validate(self, mock_get_excel_values):
        """バリデーションエンジンのテスト"""
        # モックの設定
        mock_get_excel_values.return_value = {"age": 25, "email": "invalid-email"}

        # ルールの作成
        rule1 = Rule(
            name="年齢チェック",
            expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
            error_message="{field}は20以上である必要があります",
        )
        rule2 = Rule(
            name="メールアドレス形式チェック",
            expression=RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
            error_message="{field}の形式が不正です: {value}",
        )

        # バリデーションエンジンの初期化
        engine = ValidationEngine([rule1, rule2])

        # バリデーションの実行
        results = engine.validate("dummy.xlsx", {"age": "Sheet1!A1", "email": "Sheet1!B1"})

        # 結果の検証
        self.assertEqual(len(results), 1)  # rule2のみがエラー
        self.assertEqual(results[0].error_fields, ["email"])
        self.assertTrue("emailの形式が不正です" in results[0].error_message)
        self.assertEqual(results[0].error_locations, ["Sheet1!B1"])


if __name__ == "__main__":
    unittest.main()
