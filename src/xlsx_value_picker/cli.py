import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

import openpyxl
import yaml
from pydantic import TypeAdapter
from .config import Config, SheetValueSpec, NamedCellValueSpec, TableValueSpec, RangeValueSpec, ValueSpec


def load_config(config_path: Union[str, Path]) -> Config:
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or {}
    return TypeAdapter(Config).validate_python(raw)

def extract_range_records(
    ws: openpyxl.worksheet.worksheet.Worksheet,
    cell_range: str,
    columns_map: Dict[str, str],
    include_empty_row: bool = False
) -> List[Dict[str, Any]]:
    # セル範囲からデータ部分のみ抽出（ヘッダ行含まない前提）
    min_col, min_row, max_col, max_row = openpyxl.utils.range_boundaries(cell_range)
    records = []
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col, values_only=True):
        rec = {}
        for col_pos_str, out_key in columns_map.items():
            col_pos = int(col_pos_str)
            idx = col_pos - 1  # 1始まり→0始まり
            rec[out_key] = row[idx]
        # すべての値がNoneの場合はスキップ（デフォルト）
        if not include_empty_row and all(v is None for v in rec.values()):
            continue
        records.append(rec)
    return records

def get_excel_values(
    excel_path: Union[str, Path],
    value_specs: List[ValueSpec],
    include_empty_range_row: bool = False
) -> Dict[str, Any]:
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    results = {}
    for spec in value_specs:
        # pydanticモデルでなければ変換
        if not hasattr(spec, '__fields__'):
            spec = TypeAdapter(ValueSpec).validate_python(spec)
        results[spec.name] = spec.get_value(wb, include_empty_range_row=include_empty_range_row)
    return results

def main() -> None:
    parser = argparse.ArgumentParser(description='Excel値取得ツール')
    parser.add_argument('excel', nargs='?', help='Excelファイルパス（コマンドライン優先）')
    parser.add_argument('-c', '--config', default='config.yaml', help='設定ファイルパス')
    parser.add_argument('-o', '--output', help='出力ファイルパス（未指定時は標準出力）')
    parser.add_argument('--include-empty-range-row', action='store_true', help='range指定で全列がNoneの行も出力に含める')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='出力フォーマット（jsonまたはyaml）')
    args = parser.parse_args()

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

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(results, f, ensure_ascii=False, indent=2)
            else:
                yaml.dump(results, f, allow_unicode=True, sort_keys=False)
        print(f'出力完了: {args.output}')
    else:
        if args.format == 'json':
            json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
            print()  # 改行
        else:
            yaml.dump(results, sys.stdout, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    main()