import json
import sys
from pathlib import Path
from typing import Optional, Any, List, Dict, Union

import click

from .config import get_excel_values, ValueSpec
from .config_loader import ConfigLoader, ConfigValidationError
from .excel_processor import ExcelValueExtractor
from .output_formatter import OutputFormatter


@click.command()
@click.argument('excel_file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-c', '--config', default='config.yaml', help='検証ルールや設定を記述した設定ファイル')
@click.option('--ignore-errors', is_flag=True, help='検証エラーが発生しても処理を継続します')
@click.option('-o', '--output', help='出力先ファイルを指定します（未指定の場合は標準出力）')
@click.option('--log', help='検証エラーを記録するログファイルを指定します')
@click.option('--schema', help='JSONスキーマファイルのパスを指定します')
@click.option('--include-empty-cells', is_flag=True, help='空セルも出力に含めます')
@click.option('--validate-only', is_flag=True, help='バリデーションのみを実行します')
@click.version_option(version='0.2.0')
def main(
    excel_file: str,
    config: str,
    ignore_errors: bool,
    output: Optional[str],
    log: Optional[str],
    schema: Optional[str],
    include_empty_cells: bool,
    validate_only: bool
):
    """
    Excelファイルから値を取得し、バリデーションと出力を行うツール
    
    EXCEL_FILE: 処理対象のExcelファイルパス
    """
    try:
        # 設定ファイルの読み込み
        config_loader = ConfigLoader(schema_path=schema)
        try:
            config_model = config_loader.load_config(config)
        except (ConfigValidationError, FileNotFoundError) as e:
            click.echo(f"設定ファイルの読み込みに失敗しました: {e}", err=True)
            if not ignore_errors:  # ignore-errorsオプションを確認
                sys.exit(1)
            else:
                # デフォルト値で処理を継続するための最小限の設定を作成
                click.echo("--ignore-errors オプションが指定されたため、最低限の設定で処理を継続します", err=True)
                from pydantic import TypeAdapter
                from .config_loader import ConfigModel, OutputFormat
                config_model = ConfigModel(
                    fields={"dummy": "Sheet1!A1"},
                    rules=[],
                    output=OutputFormat(format="json")
                )
        
        # Excelファイルからの値取得
        try:
            extractor = ExcelValueExtractor(excel_file)
            data = extractor.extract_values(config_model, include_empty_cells=include_empty_cells)
        except Exception as e:
            click.echo(f"Excelファイルからの値取得に失敗しました: {e}", err=True)
            if not ignore_errors:  # ignore-errorsオプションを確認
                sys.exit(1)
            else:
                # 空のデータで処理を継続
                click.echo("--ignore-errors オプションが指定されたため、空のデータで処理を継続します", err=True)
                data = {}
        finally:
            if 'extractor' in locals():
                extractor.close()
        
        # バリデーションのみ実行の場合
        if validate_only:
            click.echo("バリデーションのみモードはまだ実装されていません。今後のバージョンで実装予定です。", err=True)
            if not ignore_errors:  # ignore-errorsオプションを確認
                sys.exit(1)
            else:
                click.echo("--ignore-errors オプションが指定されたため、処理を継続します", err=True)
        
        # 出力処理
        try:
            formatter = OutputFormatter(config_model)
            result = formatter.write_output(data, output)
            
            # 出力先が指定されていない場合は標準出力に表示
            if not output:
                click.echo(result)
                
            click.echo(f"処理が完了しました。", err=True)
        except Exception as e:
            click.echo(f"出力処理に失敗しました: {e}", err=True)
            if not ignore_errors:
                sys.exit(1)
            
    except Exception as e:
        click.echo(f"エラーが発生しました: {e}", err=True)
        if not ignore_errors:
            sys.exit(1)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    設定ファイルを読み込む (テストとの互換性のために追加)
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        設定データ
    """
    config_loader = ConfigLoader()
    return config_loader.load_config(config_path).model_dump()


if __name__ == "__main__":
    main()
