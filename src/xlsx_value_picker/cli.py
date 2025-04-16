import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

import openpyxl
import yaml
from pydantic import TypeAdapter
from .config import Config, SheetValueSpec, NamedCellValueSpec, TableValueSpec, RangeValueSpec, ValueSpec, get_excel_values
from .template import render_template


def load_config(config_path: Union[str, Path]) -> Config:
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or {}
    return TypeAdapter(Config).validate_python(raw)

def main() -> None:
    parser = argparse.ArgumentParser(description='Excel値取得ツール')
    parser.add_argument('excel', nargs='?', help='Excelファイルパス（コマンドライン優先）')
    parser.add_argument('-c', '--config', default='config.yaml', help='設定ファイルパス')
    parser.add_argument('-o', '--output', help='出力ファイルパス（未指定時は標準出力）')
    parser.add_argument('--include-empty-range-row', action='store_true', help='range指定で全列がNoneの行も出力に含める')
    parser.add_argument('--format', choices=['json', 'yaml', 'jinja2'], default='json', 
                      help='出力フォーマット（jsonまたはyaml、jinja2）（廃止予定、設定ファイルのoutput.formatで指定推奨）')
    args = parser.parse_args()
    
    # --formatオプションは廃止予定であることを警告する
    if "--format" in sys.argv:
        print('警告: --formatオプションは廃止予定です。設定ファイルのoutput.formatで指定してください。', file=sys.stderr)

    if not Path(args.config).exists():
        print(f'設定ファイルが見つかりません: {args.config}', file=sys.stderr)
        sys.exit(1)
    config: Config = load_config(args.config)
    excel_file = args.excel if args.excel else config.excel_file
    value_specs = config.values

    if not excel_file:
        print('Excelファイルが指定されていません（コマンドラインまたは設定ファイルで指定してください）', file=sys.stderr)
        sys.exit(1)
    if not Path(excel_file).exists():
        print(f'Excelファイルが見つかりません: {excel_file}', file=sys.stderr)
        sys.exit(1)

    results = get_excel_values(excel_file, value_specs, include_empty_range_row=args.include_empty_range_row)

    # 出力形式を決定（コマンドライン引数 > 設定ファイル）
    output_format = args.format if "--format" in sys.argv else config.output.format
    
    # 出力形式に応じて処理を分岐
    if output_format == 'jinja2':
        if not config.output.template and not config.output.template_file:
            print('Jinja2形式の出力には、設定ファイルでtemplate_fileまたはtemplateを指定してください', file=sys.stderr)
            sys.exit(1)
        
        # テンプレートをレンダリング
        try:
            output_text = render_template(
                data=results,
                template_string=config.output.template,
                template_file=config.output.template_file
            )
        except ValueError as e:
            print(f'テンプレートレンダリングエラー: {str(e)}', file=sys.stderr)
            sys.exit(1)
        
        # 出力先に応じて処理
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f'出力完了: {args.output}')
        else:
            print(output_text)
    else:
        # 既存の JSON/YAML 出力処理
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if output_format == 'json':
                    json.dump(results, f, ensure_ascii=False, indent=2)
                else:
                    yaml.dump(results, f, allow_unicode=True, sort_keys=False)
            print(f'出力完了: {args.output}')
        else:
            if output_format == 'json':
                json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
                print()  # 改行
            else:
                yaml.dump(results, sys.stdout, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    main()