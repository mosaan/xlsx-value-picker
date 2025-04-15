import argparse
import json
import sys
from pathlib import Path

import openpyxl
import yaml


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_excel_values(excel_path, value_specs):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    results = {}
    sheetnames = wb.sheetnames
    for spec in value_specs:
        if 'named_cell' in spec:
            # 名前付きセル優先
            name = spec['named_cell']
            dn = wb.defined_names.get(name)
            if dn is None:
                raise ValueError(f"名前付きセルが見つかりません: {name}")
            # 参照先（シート名, セルアドレス）を取得
            dest = list(dn.destinations)
            if not dest:
                raise ValueError(f"名前付きセルの参照先が不正です: {name}")
            sheet_name, cell_addr = dest[0]
            sheet = wb[sheet_name]
            value = sheet[cell_addr].value
            results[spec['name']] = value
        else:
            sheet_spec = spec['sheet']
            if isinstance(sheet_spec, str) and sheet_spec.startswith('*'):
                # シート名が'*N'形式の場合、左からN番目のシートを選択
                try:
                    idx = int(sheet_spec[1:]) - 1
                    if idx < 0 or idx >= len(sheetnames):
                        raise IndexError
                    sheet = wb[sheetnames[idx]]
                except (ValueError, IndexError):
                    raise ValueError(f"シート指定が不正です: {sheet_spec} (シート数: {len(sheetnames)})")
            else:
                sheet = wb[sheet_spec]
            value = sheet[spec['cell']].value
            results[spec['name']] = value
    return results

def main():
    parser = argparse.ArgumentParser(description='Excel値取得ツール')
    parser.add_argument('excel', nargs='?', help='Excelファイルパス（コマンドライン優先）')
    parser.add_argument('-c', '--config', default='config.yaml', help='設定ファイルパス')
    parser.add_argument('-o', '--output', help='出力ファイルパス（未指定時は標準出力）')
    args = parser.parse_args()

    config = load_config(args.config)
    excel_file = args.excel if args.excel else config.get('excel_file')
    value_specs = config['values']

    if not excel_file:
        print('Excelファイルが指定されていません（コマンドラインまたは設定ファイルで指定してください）', file=sys.stderr)
        sys.exit(1)
    if not Path(excel_file).exists():
        print(f'Excelファイルが見つかりません: {excel_file}', file=sys.stderr)
        sys.exit(1)

    results = get_excel_values(excel_file, value_specs)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'出力完了: {args.output}')
    else:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()  # 改行

if __name__ == '__main__':
    main()
