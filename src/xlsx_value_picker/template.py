"""
Jinja2テンプレートレンダリング機能
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template


def render_template(
    data: dict[str, Any],
    template_string: str | None = None,
    template_file: str | Path | None = None,
) -> str:
    """
    Jinja2テンプレートをレンダリングする

    Args:
        data: テンプレートに渡すデータ
        template_string: テンプレート文字列
        template_file: テンプレートファイルのパス

    Returns:
        レンダリング結果の文字列

    Raises:
        ValueError: テンプレート文字列もテンプレートファイルも指定されていない場合
    """
    if not (template_string or template_file):
        raise ValueError("テンプレート文字列またはテンプレートファイルを指定してください")

    if template_file:
        template_path = Path(template_file)
        if not template_path.exists():
            raise ValueError(f"テンプレートファイルが見つかりません: {template_file}")

        env = Environment(loader=FileSystemLoader(template_path.parent))
        template = env.get_template(template_path.name)
        return template.render(data=data)

    if template_string:
        template = Template(template_string)
        return template.render(data=data)

    # This should never happen due to the first check, but added for type safety
    raise ValueError("テンプレート文字列またはテンプレートファイルを指定してください")
