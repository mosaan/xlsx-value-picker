"""
設定に基づく出力フォーマット機能
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
import jinja2

from .config_loader import ConfigModel, OutputFormat


class OutputFormatter:
    """
    抽出したデータを設定に基づいて様々な形式に出力するクラス
    """

    def __init__(self, config: ConfigModel):
        """
        初期化

        Args:
            config: 設定モデル
        """
        self.config = config
        self.output_config = config.output

    def format_output(self, data: Dict[str, Any]) -> str:
        """
        データを設定に基づいて指定された形式に変換する

        Args:
            data: 出力するデータ

        Returns:
            str: フォーマットされた出力文字列
        """
        output_format = self.output_config.format

        if output_format == "json":
            return self._format_json(data)
        elif output_format == "yaml":
            return self._format_yaml(data)
        elif output_format == "jinja2":
            return self._format_jinja2(data)
        else:
            raise ValueError(f"サポートされていない出力形式です: {output_format}")

    def _format_json(self, data: Dict[str, Any]) -> str:
        """
        データをJSON形式に変換する

        Args:
            data: 出力するデータ

        Returns:
            str: JSON文字列
        """
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _format_yaml(self, data: Dict[str, Any]) -> str:
        """
        データをYAML形式に変換する

        Args:
            data: 出力するデータ

        Returns:
            str: YAML文字列
        """
        return yaml.dump(data, sort_keys=False, allow_unicode=True)

    def _format_jinja2(self, data: Dict[str, Any]) -> str:
        """
        データをJinja2テンプレートを使用して変換する

        Args:
            data: 出力するデータ

        Returns:
            str: テンプレート適用済み文字列

        Raises:
            ValueError: テンプレートが指定されていない場合
        """
        template_str = None

        # テンプレート文字列の取得
        if self.output_config.template:
            template_str = self.output_config.template
        elif self.output_config.template_file:
            template_path = Path(self.output_config.template_file)
            if not template_path.exists():
                raise FileNotFoundError(f"テンプレートファイルが見つかりません: {template_path}")

            with open(template_path, "r", encoding="utf-8") as f:
                template_str = f.read()
        else:
            raise ValueError("Jinja2出力形式の場合、templateまたはtemplate_fileが必要です")

        # テンプレートの適用
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("."), autoescape=jinja2.select_autoescape(["html", "xml"])
        )
        template = env.from_string(template_str)

        return template.render(**data)

    def write_output(self, data: Dict[str, Any], output_path: Optional[Union[str, Path]] = None) -> str:
        """
        データを設定に基づいてフォーマットし、指定されたパスに書き込む

        Args:
            data: 出力するデータ
            output_path: 出力先パス（Noneの場合は文字列を返す）

        Returns:
            str: フォーマットされた出力文字列
        """
        formatted_output = self.format_output(data)

        # 出力先が指定されている場合は書き込む
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(formatted_output)

        return formatted_output
