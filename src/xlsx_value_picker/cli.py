import json
import sys
from typing import Any

import click

from .config_loader import ConfigLoader, ConfigModel, OutputFormat
from .excel_processor import ExcelValueExtractor
from .exceptions import (
    ConfigLoadError,
    ConfigValidationError,
    ExcelProcessingError,
    OutputError,
    XlsxValuePickerError,
)
from .output_formatter import OutputFormatter
from .validation import ValidationEngine
from .validation_common import ValidationResult  # インポート元を修正


def _handle_error(
    e: Exception, ignore_errors: bool, message_prefix: str = "エラーが発生しました"
) -> None:  # 戻り値型を追加
    """共通のエラーハンドリング処理"""
    click.echo(f"{message_prefix}: {e}", err=True)
    if not ignore_errors:
        sys.exit(1)
    else:
        click.echo("--ignore-errors オプションが指定されたため、処理を継続します", err=True)


def _write_validation_log(log_path: str, validation_results: list[ValidationResult]) -> None:  # 戻り値型を追加
    """バリデーション結果をログファイルに書き込む"""
    try:
        with open(log_path, "w", encoding="utf-8") as f:
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
        click.echo(f"バリデーション結果を {log_path} に保存しました", err=True)
    except Exception as e:
        click.echo(f"ログ出力に失敗しました: {e}", err=True)


@click.command()  # type: ignore
@click.argument("excel_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))  # type: ignore
@click.option("-c", "--config", default="config.yaml", help="検証ルールや設定を記述した設定ファイル")  # type: ignore
@click.option("--ignore-errors", is_flag=True, help="検証エラーが発生しても処理を継続します")  # type: ignore
@click.option("-o", "--output", help="出力先ファイルを指定します（未指定の場合は標準出力）")  # type: ignore
@click.option("--log", help="検証エラーを記録するログファイルを指定します")  # type: ignore
# --schema オプションは削除 (スキーマ検証は Pydantic に一本化)
@click.option("--include-empty-cells", is_flag=True, help="空セルも出力に含めます")  # type: ignore
@click.option("--validate-only", is_flag=True, help="バリデーションのみを実行します")  # type: ignore
@click.version_option(version="0.3.0")  # type: ignore
def main(  # 戻り値型を追加
    excel_file: str,
    config: str,
    ignore_errors: bool,
    output: str | None,
    log: str | None,
    # schema 引数は削除
    include_empty_cells: bool,
    validate_only: bool,
) -> None:
    """
    Excelファイルから値を取得し、バリデーションと出力を行うツール

    EXCEL_FILE: 処理対象のExcelファイルパス
    """
    config_model: ConfigModel | None = None
    validation_results: list[ValidationResult] = []
    data: dict[str, Any] = {}

    config_loader: ConfigLoader | None = None

    try:
        # 1. ConfigLoader の初期化 (スキーマ読み込み)
        try:
            # ConfigLoader の初期化 (引数なしに変更)
            config_loader = ConfigLoader()
        # except ConfigLoadError as e: # スキーマ読み込み固有のエラーハンドリングは削除
        #     click.echo(f"スキーマファイルの読み込みに失敗しました: {e}", err=True)
        #     sys.exit(1)
        except Exception as e:  # ConfigLoader 初期化時の予期せぬエラー
            click.echo(f"ConfigLoader の初期化中に予期せぬエラーが発生しました: {e}", err=True)
            sys.exit(1)  # 初期化失敗は致命的なので終了

        # 2. 設定ファイルの読み込みと検証
        try:
            # config_loader は上で初期化成功しているはず
            config_model = config_loader.load_config(config)
        except ConfigLoadError as e:  # 設定ファイルが見つからない、パースできないなど
            _handle_error(e, ignore_errors, "設定ファイルの読み込みに失敗しました")
            if ignore_errors:
                click.echo("最低限の設定で処理を継続します", err=True)
                config_model = ConfigModel(fields={"dummy": "Sheet1!A1"}, rules=[], output=OutputFormat(format="json"))
            else:
                return  # exit しなかった場合は終了
        except ConfigValidationError as e:  # スキーマ検証、モデル検証エラー
            _handle_error(e, ignore_errors, "設定ファイルの検証に失敗しました")
            if ignore_errors:
                click.echo("最低限の設定で処理を継続します", err=True)
                config_model = ConfigModel(fields={"dummy": "Sheet1!A1"}, rules=[], output=OutputFormat(format="json"))
            else:
                return  # exit しなかった場合は終了
        except Exception as e:  # 予期せぬ読み込み/検証エラー
            _handle_error(e, ignore_errors, "設定ファイルの処理中に予期せぬエラーが発生しました")
            if ignore_errors:
                click.echo("最低限の設定で処理を継続します", err=True)
                config_model = ConfigModel(fields={"dummy": "Sheet1!A1"}, rules=[], output=OutputFormat(format="json"))
            else:
                return  # exit しなかった場合は終了

        # config_model が None のチェック (ignore_errors=True でダミーが設定されるため、基本的には通らないはず)
        if config_model is None and not ignore_errors:
            # このパスは load_config でエラーが発生し ignore_errors=False の場合に到達する可能性がある
            click.echo("設定の読み込み/検証に失敗したため処理を中断します。", err=True)
            # _handle_error で既に exit(1) しているはずだが念のため
            sys.exit(1)
        elif config_model is None and ignore_errors:
            # ignore_errors=True の場合、ダミーが設定されるはずなので、ここに来るのは想定外
            click.echo("予期せぬエラー: 設定モデルが None ですが ignore_errors=True です。", err=True)
            sys.exit(1)  # 予期せぬ状態なので終了

        # 3. バリデーションの実行 (ルールが存在する場合)
        has_validation_rules = len(config_model.rules) > 0
        if has_validation_rules:
            try:
                validation_engine = ValidationEngine(config_model.rules)
                validation_results = validation_engine.validate(excel_file, config_model.fields)
            except Exception as e:  # ValidationEngine 内のエラーは汎用 Exception でキャッチ
                _handle_error(e, ignore_errors, "バリデーション実行中にエラーが発生しました")
                # ignore_errors=True の場合、validation_results は空のまま続行

            # バリデーションエラー処理
            if validation_results:
                click.echo(f"バリデーションエラーが {len(validation_results)} 件見つかりました:", err=True)
                for idx, result in enumerate(validation_results, 1):
                    locations = ", ".join(result.error_locations) if result.error_locations else "不明"
                    click.echo(f"  {idx}. {result.error_message} (位置: {locations})", err=True)

                if log:
                    _write_validation_log(log, validation_results)

                if validate_only:
                    click.echo("バリデーションのみモードで実行しました (エラーあり)", err=True)
                    if not ignore_errors:
                        sys.exit(1)
                    return  # ignore_errors=True ならここで終了

                # 通常モードでエラーがあり、ignore_errors=False なら終了
                if not ignore_errors:
                    click.echo("バリデーションエラーが発生したため、処理を中止します", err=True)
                    click.echo(
                        "エラーを無視して処理を継続するには --ignore-errors オプションを指定してください", err=True
                    )
                    sys.exit(1)
                else:
                    click.echo(
                        "--ignore-errors オプションが指定されたため、バリデーションエラーを無視して処理を継続します",
                        err=True,
                    )

        # バリデーションのみモードで成功した場合
        if validate_only:
            if not validation_results:  # エラーがなかった場合
                click.echo("バリデーションに成功しました", err=True)
            # エラーがあっても ignore_errors=True ならここまで来るので return する
            return

        # 3. Excelファイルからの値取得
        try:
            with ExcelValueExtractor(excel_file) as extractor:
                data = extractor.extract_values(config_model, include_empty_cells=include_empty_cells)
        except ExcelProcessingError as e:
            _handle_error(e, ignore_errors, "Excelファイルからの値取得に失敗しました")
            if ignore_errors:
                click.echo("空のデータで処理を継続します", err=True)
                data = {}  # 空のデータで続行
            else:
                return  # エラーハンドリングで exit しなかった場合はここで終了
        except Exception as e:  # 予期せぬエラー
            _handle_error(e, ignore_errors, "Excelファイル処理中に予期せぬエラーが発生しました")
            if ignore_errors:
                click.echo("空のデータで処理を継続します", err=True)
                data = {}
            else:
                return

        # 4. 出力処理
        try:
            formatter = OutputFormatter(config_model)
            result = formatter.write_output(data, output)
            if not output:
                click.echo(result)
            click.echo("処理が完了しました。", err=True)
        except OutputError as e:
            _handle_error(e, ignore_errors, "出力処理に失敗しました")
        except Exception as e:  # 予期せぬエラー
            _handle_error(e, ignore_errors, "出力処理中に予期せぬエラーが発生しました")

    except XlsxValuePickerError as e:
        # 予期されるアプリケーションエラーの最終キャッチ
        _handle_error(e, ignore_errors)
    except Exception as e:
        # 予期しないエラーの最終キャッチ
        click.echo(f"予期しないエラーが発生しました: {e}", err=True)
        # ignore_errors に関わらず、予期しないエラーは終了させるのが安全か検討
        sys.exit(1)


def load_config(config_path: str) -> dict[str, Any]:
    """
    設定ファイルを読み込む (テストとの互換性のために追加)

    Args:
        config_path: 設定ファイルのパス

    Returns:
        設定データ
    """
    # この関数はテスト用なので、リファクタリング対象外とする
    # 必要であれば別途修正
    # ConfigLoader の初期化 (引数なしに変更)
    config_loader = ConfigLoader()
    try:
        return config_loader.load_config(config_path).model_dump()
    except (ConfigLoadError, ConfigValidationError, FileNotFoundError) as e:
        # テスト用にエラーを再送出するか、None を返すかなどを検討
        raise RuntimeError(f"テスト用の設定読み込みに失敗: {e}") from e


if __name__ == "__main__":
    main()
