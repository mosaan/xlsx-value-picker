"""
Model Context Protocol (MCP) のリクエスト・レスポンス型定義
"""

from pydantic import BaseModel, Field


class ListModelsRequest(BaseModel):
    """listModelsリクエストのパラメータ"""
    pass  # パラメータなし


class ListModelsResponse(BaseModel):
    """listModelsレスポンスの構造"""
    models: list[str] = Field(..., description="利用可能なモデルIDのリスト")


class GetModelInfoRequest(BaseModel):
    """getModelInfoリクエストのパラメータ"""
    model_id: str = Field(..., description="情報を取得するモデルのID")


class ModelInfo(BaseModel):
    """モデル情報の構造"""
    model_id: str = Field(..., description="モデルのID")
    description: str | None = Field(None, description="モデルの説明")
    fields: dict[str, str] = Field(..., description="フィールド定義（キーとセル参照）")
    excel_path: str | None = Field(None, description="関連するExcelファイルのパス")


class GetModelInfoResponse(BaseModel):
    """getModelInfoレスポンスの構造"""
    model_info: ModelInfo


class ValidationError(BaseModel):
    """バリデーションエラー情報"""
    field: str = Field(..., description="エラーが発生したフィールド")
    message: str = Field(..., description="エラーメッセージ")


class GetDiagnosticsRequest(BaseModel):
    """getDiagnosticsリクエストのパラメータ"""
    model_id: str = Field(..., description="診断を実行するモデルID")


class GetDiagnosticsResponse(BaseModel):
    """getDiagnosticsレスポンスの構造"""
    is_valid: bool = Field(..., description="バリデーション結果（True=成功、False=失敗）")
    errors: list[ValidationError] = Field(default_factory=list, description="検出されたバリデーションエラー")


class GetFileContentRequest(BaseModel):
    """getFileContentリクエストのパラメータ"""
    model_id: str = Field(..., description="コンテンツを取得するモデルID")
    output_format: str | None = Field("json", description="出力形式（json, yaml, markdown, csvなど）")


class GetFileContentResponse(BaseModel):
    """getFileContentレスポンスの構造"""
    content: str = Field(..., description="構造化テキストコンテンツ")
    format: str = Field(..., description="コンテンツの形式（json, yaml, markdown, csvなど）")


# エラーコードマッピング（内部例外からMCPエラーコードへのマッピング）
MCP_ERROR_MAPPING = {
    "ConfigLoadError": {"code": -32803, "message": "設定ファイルの読み込みエラー"},
    "ConfigValidationError": {"code": -32804, "message": "設定ファイルの検証エラー"},
    "ExcelProcessingError": {"code": -32805, "message": "Excelファイル処理エラー"},
    "ValidationError": {"code": -32806, "message": "バリデーションエラー"},
    "ModelNotFoundError": {"code": -32807, "message": "モデルが見つかりません"},
    "InvalidRequestError": {"code": -32600, "message": "無効なリクエスト"}
}
