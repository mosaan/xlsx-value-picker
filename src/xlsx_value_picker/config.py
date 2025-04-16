from pydantic import BaseModel
from typing import List, Dict, Union, Any
import openpyxl

class SheetValueSpec(BaseModel):
    sheet: str
    cell: str
    name: str

    def get_value(self, wb: openpyxl.Workbook, include_empty_range_row: bool = False) -> Any:
        sheet_spec = self.sheet
        sheetnames = wb.sheetnames
        if isinstance(sheet_spec, str) and sheet_spec.startswith('*'):
            idx = int(sheet_spec[1:]) - 1
            if idx < 0 or idx >= len(sheetnames):
                raise ValueError(f"シート指定が不正です: {sheet_spec} (シート数: {len(sheetnames)})")
            sheet = wb[sheetnames[idx]]
        else:
            sheet = wb[sheet_spec]
        return sheet[self.cell].value

class NamedCellValueSpec(BaseModel):
    named_cell: str
    name: str

    def get_value(self, wb: openpyxl.Workbook, include_empty_range_row: bool = False) -> Any:
        name = self.named_cell
        dn = wb.defined_names.get(name)
        if dn is None:
            raise ValueError(f"名前付きセルが見つかりません: {name}")
        dest = list(dn.destinations)
        if not dest:
            raise ValueError(f"名前付きセルの参照先が不正です: {name}")
        sheet_name, cell_addr = dest[0]
        sheet = wb[sheet_name]
        return sheet[cell_addr].value

class TableValueSpec(BaseModel):
    table: str
    columns: Dict[str, str]
    name: str

    def get_value(self, wb: openpyxl.Workbook, include_empty_range_row: bool = False) -> Any:
        for ws in wb.worksheets:
            if self.table in ws.tables:
                from .cli import extract_table_records
                return extract_table_records(ws, self.table, self.columns)
        raise ValueError(f"テーブルが見つかりません: {self.table}")

class RangeValueSpec(BaseModel):
    range: str
    columns: Dict[str, str]
    name: str

    def get_value(self, wb: openpyxl.Workbook, include_empty_range_row: bool = False) -> Any:
        range_str = self.range
        columns_map = self.columns
        if '!' in range_str:
            sheet_name, cell_range = range_str.split('!', 1)
            ws = wb[sheet_name]
        else:
            raise ValueError(f"範囲指定が不正です: {range_str} (シート名を含めて指定してください)")
        from .cli import extract_range_records
        return extract_range_records(ws, cell_range, columns_map, include_empty_row=include_empty_range_row)

ValueSpec = Union[SheetValueSpec, NamedCellValueSpec, TableValueSpec, RangeValueSpec]

class Config(BaseModel):
    excel_file: str
    values: List[ValueSpec]
