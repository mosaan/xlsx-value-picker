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
    for spec in value_specs:
        sheet = wb[spec['sheet']]
        value = sheet[spec['cell']].value
        results[spec['name']] = value
    return results

def main():
    parser = argparse.ArgumentParser(description='Excel値取得ツール')
    parser.add_argument('-c', '--config', default='config.yaml', help='設定ファイルパス')
    parser.add_argument('-o', '--output', default='output.json', help='出力ファイルパス')
    args = parser.parse_args()

    config = load_config(args.config)
    excel_file = config['excel_file']
    value_specs = config['values']

    if not Path(excel_file).exists():
        print(f'Excelファイルが見つかりません: {excel_file}', file=sys.stderr)
        sys.exit(1)

    results = get_excel_values(excel_file, value_specs)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'出力完了: {args.output}')

if __name__ == '__main__':
    main()
