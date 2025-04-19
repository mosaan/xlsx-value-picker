import json
import sys
from pathlib import Path

import click
import openpyxl  # noqa: F401
import yaml
from pydantic import TypeAdapter

from .config import (
    Config,
    get_excel_values,
)
from .template import render_template


def load_config(config_path: str | Path) -> Config:
    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return TypeAdapter(Config).validate_python(raw)


@click.command()
@click.argument('input_file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-c', '--config', default='config.yaml', help='検証ルールや設定を記述した設定ファイル')
@click.option('--ignore-errors', is_flag=True, help='検証エラーが発生しても処理を継続します')
@click.option('-o', '--output', help='JSONデータの出力先ファイルを指定します')
@click.option('--log', help='検証エラーを記録するログファイルを指定します')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml', 'jinja2']), help='出力フォーマットを指定します')
@click.option('--template', help='Jinja2テンプレートを使用して出力をカスタマイズします')
@click.option('--include-empty-range-row', is_flag=True, help='range指定で全列がNoneの行も出力に含めます')
@click.version_option(version='0.1.0')
def main(input_file, config, ignore_errors, output, log, output_format, template, include_empty_range_row):
    """Excel検証およびJSON出力ツール"""
    # スケルトン実装として入力値を表示するだけ
    click.echo(f"入力ファイル: {input_file}")
    click.echo(f"設定ファイル: {config}")
    click.echo(f"エラー無視: {ignore_errors}")
    click.echo(f"出力ファイル: {output}")
    click.echo(f"ログファイル: {log}")
    click.echo(f"フォーマット: {output_format}")
    click.echo(f"テンプレート: {template}")
    click.echo(f"空行を含める: {include_empty_range_row}")
    click.echo("Hello World")


if __name__ == "__main__":
    main()
