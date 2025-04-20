import json
import sys
from typing import Any

import click

from .config_loader import ConfigLoader, ConfigValidationError
from .excel_processor import ExcelValueExtractor
from .output_formatter import OutputFormatter
from .validation import ValidationEngine


@click.command()
@click.argument("excel_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("-c", "--config", default="config.yaml", help="検証ルールや設定を記述した設定ファイル")
@click.option("--ignore-errors", is_flag=True, help="検証エラーが発生しても処理を継続します")
@click.option("-o", "--output", help="出力先ファイルを指定します（未指定の場合は標準出力）")
@click.option("--log", help="検証エラーを記録するログファイルを指定します")
@click.option("--schema", help="JSONスキーマファイルのパスを指定します")
@click.option("--include-empty-cells", is_flag=True, help="空セルも出力に含めます")
@click.option("--validate-only", is_flag=True, help="バリデーションのみを実行します")
@click.version_option(version="0.3.0")
def main(
    excel_file: str,
    config: str,
    ignore_errors: bool,
    output: str | None,
    log: str | None,
    schema: str | None,
    include_empty_cells: bool,
    validate_only: bool,
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
                from .config_loader import ConfigModel, OutputFormat

                config_model = ConfigModel(fields={"dummy": "Sheet1!A1"}, rules=[], output=OutputFormat(format="json"))

        # バリデーションエンジンの準備（ルールが定義されている場合）
        has_validation_rules = len(config_model.rules) > 0
        validation_results = []

        if has_validation_rules:
            # バリデーションエンジンの初期化と検証実行
            validation_engine = ValidationEngine(config_model.rules)
            try:
                validation_results = validation_engine.validate(excel_file, config_model.fields)
            except Exception as e:
                click.echo(f"バリデーション実行中にエラーが発生しました: {e}", err=True)
                if not ignore_errors:
                    sys.exit(1)
                else:
                    click.echo("--ignore-errors オプションが指定されたため、処理を継続します", err=True)

            # バリデーションエラーがある場合の処理
            if validation_results:
                click.echo(f"バリデーションエラーが {len(validation_results)} 件見つかりました:", err=True)
                for idx, result in enumerate(validation_results, 1):
                    locations = ", ".join(result.error_locations) if result.error_locations else "不明"
                    click.echo(f"  {idx}. {result.error_message} (位置: {locations})", err=True)

                # エラーログの出力
                if log:
                    try:
                        with open(log, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "validation_results": [
                                        {
                                            "is_valid": result.is_valid,
                                            "error_message": result.error_message,
                                            "error_fields": result.error_fields,
                                            "error_locations": result.error_locations,
                                            "severity": result.severity,
                                        }
                                        for result in validation_results
                                    ],
                                    "is_valid": False,
                                    "error_count": len(validation_results),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )
                        click.echo(f"バリデーション結果を {log} に保存しました", err=True)
                    except Exception as e:
                        click.echo(f"ログ出力に失敗しました: {e}", err=True)

                # バリデーションのみモードの場合はここで終了
                if validate_only:
                    if not ignore_errors:
                        sys.exit(1)
                    click.echo("バリデーションのみモードで実行しました", err=True)
                    return

                # 通常モードでバリデーションエラーがあり、ignore-errors指定がない場合は終了
                elif not ignore_errors:
                    click.echo("バリデーションエラーが発生したため、処理を中止します", err=True)
                    click.echo(
                        "エラーを無視して処理を継続するには --ignore-errors オプションを指定してください", err=True
                    )
                    sys.exit(1)

                click.echo(
                    "--ignore-errors オプションが指定されたため、バリデーションエラーを無視して処理を継続します",
                    err=True,
                )

        # バリデーションのみのモードで、かつバリデーションが成功した場合
        if validate_only:
            click.echo("バリデーションに成功しました", err=True)
            return

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
            if "extractor" in locals():
                extractor.close()

        # 出力処理
        try:
            formatter = OutputFormatter(config_model)
            result = formatter.write_output(data, output)

            # 出力先が指定されていない場合は標準出力に表示
            if not output:
                click.echo(result)

            click.echo("処理が完了しました。", err=True)
        except Exception as e:
            click.echo(f"出力処理に失敗しました: {e}", err=True)
            if not ignore_errors:
                sys.exit(1)

    except Exception as e:
        click.echo(f"エラーが発生しました: {e}", err=True)
        if not ignore_errors:
            sys.exit(1)


def load_config(config_path: str) -> dict[str, Any]:
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
