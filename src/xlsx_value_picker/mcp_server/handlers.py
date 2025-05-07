"""
Model Context Protocol (MCP) のリクエストハンドラー実装
"""

import logging

from xlsx_value_picker.config_loader import MCPAvailableConfigModel
from xlsx_value_picker.exceptions import ExcelProcessingError, XlsxValuePickerError

from .protocol import (
    GetDiagnosticsRequest,
    GetDiagnosticsResponse,
    GetFileContentRequest,
    GetFileContentResponse,
    GetModelInfoRequest,
    ModelInfo,
    ValidationError,
)

# ロガーの設定
logger = logging.getLogger(__name__)


def find_model_by_id(models: list[MCPAvailableConfigModel], model_id: str) -> MCPAvailableConfigModel | None:
    """
    モデルIDに基づいてモデル設定を検索する

    Args:
        models: モデル設定のリスト
        model_id: 検索するモデルID

    Returns:
        MCPAvailableConfigModel: 見つかったモデル設定、見つからなければNone
    """
    for model in models:
        if model.model_name == model_id:
            return model
    return None


def handle_get_model_info(models: list[MCPAvailableConfigModel], request: GetModelInfoRequest) -> ModelInfo:
    """
    getModelInfoリクエストを処理し、指定されたモデルの詳細情報を返す

    Args:
        models: 利用可能なモデル設定のリスト
        request: getModelInfoリクエスト

    Returns:
        ModelInfo: モデル情報

    Raises:
        ValueError: 指定されたモデルIDが見つからない場合
    """
    model = find_model_by_id(models, request.model_id)
    if model is None:
        raise ValueError(f"指定されたモデルID '{request.model_id}' が見つかりません")

    # モデル情報を構築して返す
    return ModelInfo(
        model_id=model.model_name,
        description=model.model_description,
        fields=model.fields,
        excel_path=None,  # 現在の実装ではExcelパスを保持していない
    )


def handle_get_diagnostics(
    models: list[MCPAvailableConfigModel], request: GetDiagnosticsRequest
) -> GetDiagnosticsResponse:
    """
    getDiagnosticsリクエストを処理し、バリデーション結果を返す

    Args:
        models: 利用可能なモデル設定のリスト
        request: getDiagnosticsリクエスト

    Returns:
        GetDiagnosticsResponse: バリデーション結果

    Raises:
        ValueError: 指定されたモデルIDが見つからない場合
    """
    model = find_model_by_id(models, request.model_id)
    if model is None:
        raise ValueError(f"指定されたモデルID '{request.model_id}' が見つかりません")

    # バリデーション実行
    # Note: 実際のExcelパスは現在の実装では設定に含まれていないため、
    # 別途Excelファイルのパスを渡す仕組みが必要
    validation_errors = []
    is_valid = True

    try:
        # TODO: 現在の実装ではExcelパスを取得する方法がないため、
        # この部分は将来的に実装を更新する必要がある
        # excel_path = "path/to/excel/file.xlsx"  # 将来的には設定から取得する
        # processor = ValidationProcessor(model, excel_path)
        # results = processor.validate()
        #
        # is_valid = len(results) == 0
        # for result in results:
        #     validation_errors.append(
        #         ValidationError(field=result.field, message=result.message)
        #     )
        pass
    except Exception as e:
        logger.error(f"バリデーション処理中にエラーが発生しました: {e}")
        is_valid = False
        validation_errors.append(
            ValidationError(field="system", message=f"バリデーション処理中にエラーが発生しました: {e}")
        )

    return GetDiagnosticsResponse(is_valid=is_valid, errors=validation_errors)


def handle_get_file_content(
    models: list[MCPAvailableConfigModel], request: GetFileContentRequest
) -> GetFileContentResponse:
    """
    getFileContentリクエストを処理し、構造化テキストを返す

    Args:
        models: 利用可能なモデル設定のリスト
        request: getFileContentリクエスト

    Returns:
        GetFileContentResponse: 構造化テキスト

    Raises:
        ValueError: 指定されたモデルIDが見つからない場合
        ExcelProcessingError: Excelファイルの処理中にエラーが発生した場合
    """
    model = find_model_by_id(models, request.model_id)
    if model is None:
        raise ValueError(f"指定されたモデルID '{request.model_id}' が見つかりません")

    # 出力形式の設定
    output_format = request.output_format or "json"
    # モデルの出力形式を一時的に上書き
    original_format = model.output.format
    model.output.format = output_format

    try:
        # TODO: 現在の実装ではExcelパスを取得する方法がないため、
        # この部分は将来的に実装を更新する必要がある
        # excel_path = "path/to/excel/file.xlsx"  # 将来的には設定から取得する
        # processor = ExcelProcessor(excel_path, model)
        # content = processor.process()
        content = f'{{"message": "Excel content for model {request.model_id} would be here"}}'

        return GetFileContentResponse(content=content, format=output_format)
    except ExcelProcessingError as e:
        logger.error(f"Excelファイルの処理中にエラーが発生しました: {e}")
        raise
    except Exception as e:
        logger.error(f"ファイルコンテンツの取得中に予期せぬエラーが発生しました: {e}")
        raise XlsxValuePickerError(f"ファイルコンテンツの取得中にエラーが発生しました: {e}") from e
    finally:
        # 元の出力形式に戻す
        model.output.format = original_format
