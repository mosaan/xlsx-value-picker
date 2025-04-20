"""
ValidationContextのテスト（pytestスタイル）
"""

from xlsx_value_picker.validation_common import ValidationContext


class TestValidationContext:
    def test_get_field_value(self):
        context = ValidationContext(
            cell_values={"name": "山田太郎", "age": 30}, field_locations={"name": "Sheet1!A1", "age": "Sheet1!B1"}
        )
        assert context.get_field_value("name") == "山田太郎"
        assert context.get_field_value("age") == 30
        assert context.get_field_value("unknown") is None

    def test_get_field_location(self):
        context = ValidationContext(
            cell_values={"name": "山田太郎", "age": 30}, field_locations={"name": "Sheet1!A1", "age": "Sheet1!B1"}
        )
        assert context.get_field_location("name") == "Sheet1!A1"
        assert context.get_field_location("age") == "Sheet1!B1"
        assert context.get_field_location("unknown") is None
