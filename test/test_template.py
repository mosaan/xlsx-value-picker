import pytest
import tempfile
import os
from pathlib import Path

from xlsx_value_picker.template import render_template


def test_render_template_with_string():
    """テンプレート文字列を使ってレンダリングするテスト"""
    data = {
        "key1": "value1",
        "key2": "value2",
        "nested": {
            "key3": "value3"
        },
        "list": [1, 2, 3]
    }
    template_string = """
    Basic value: {{ data.key1 }}
    Nested value: {{ data.nested.key3 }}
    Loop values: {% for item in data.list %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}
    """
    
    result = render_template(data=data, template_string=template_string)
    
    # 期待値の検証
    assert "Basic value: value1" in result
    assert "Nested value: value3" in result
    assert "Loop values: 1, 2, 3" in result


def test_render_template_with_file():
    """テンプレートファイルを使ってレンダリングするテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "test_template.j2"
        
        # テンプレートファイルを作成
        with open(template_path, "w") as f:
            f.write("""
            Basic value: {{ data.key1 }}
            Nested value: {{ data.nested.key3 }}
            Loop values: {% for item in data.list %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}
            """)
        
        data = {
            "key1": "value1",
            "key2": "value2",
            "nested": {
                "key3": "value3"
            },
            "list": [1, 2, 3]
        }
        
        result = render_template(data=data, template_file=template_path)
        
        # 期待値の検証
        assert "Basic value: value1" in result
        assert "Nested value: value3" in result
        assert "Loop values: 1, 2, 3" in result


def test_render_template_no_template():
    """テンプレートが指定されていない場合はValueErrorが発生することを確認"""
    data = {"key": "value"}
    
    with pytest.raises(ValueError) as excinfo:
        render_template(data=data)
    
    assert "テンプレート文字列またはテンプレートファイルを指定してください" in str(excinfo.value)


def test_render_template_file_not_found():
    """存在しないテンプレートファイルが指定された場合はValueErrorが発生することを確認"""
    data = {"key": "value"}
    template_file = "/path/to/nonexistent/template.j2"
    
    with pytest.raises(ValueError) as excinfo:
        render_template(data=data, template_file=template_file)
    
    assert "テンプレートファイルが見つかりません" in str(excinfo.value)


def test_excel_data_rendering():
    """Excelから抽出したようなデータ構造をレンダリングするテスト"""
    excel_data = {
        "sheet1": "単一セル値",
        "table1": [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Los Angeles"}
        ],
        "range1": [
            {"col1": "A1", "col2": "B1"},
            {"col1": "A2", "col2": "B2"}
        ]
    }
    
    template_string = """
    # Excel Data Report
    
    ## Single Value
    Sheet1 Value: {{ data.sheet1 }}
    
    ## Table Data
    {% for person in data.table1 %}
    - {{ person.name }} ({{ person.age }}) from {{ person.city }}
    {% endfor %}
    
    ## Range Data
    | Column 1 | Column 2 |
    |----------|----------|
    {% for row in data.range1 %}
    | {{ row.col1 }} | {{ row.col2 }} |
    {% endfor %}
    """
    
    result = render_template(data=excel_data, template_string=template_string)
    
    # 期待値の検証
    assert "Sheet1 Value: 単一セル値" in result
    assert "- John (30) from New York" in result
    assert "- Jane (25) from Los Angeles" in result
    assert "| A1 | B1 |" in result
    assert "| A2 | B2 |" in result