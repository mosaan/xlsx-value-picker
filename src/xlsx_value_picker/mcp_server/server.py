"""
MCPサーバーの起動および管理を行うモジュール
"""

import logging
import sys

from xlsx_value_picker.config_loader import ConfigLoader, ConfigLoadError, ConfigValidationError

from .handlers import (
    handle_get_diagnostics,
    handle_get_file_content,
    handle_get_model_info,
)
from .protocol import GetDiagnosticsRequest, GetFileContentRequest, GetModelInfoRequest

# ロガー設定
logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """
    ロギングの初期設定を行う

    Args:
        level: ロギングレベル（デフォルト: INFO）
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def main(config_path: str = "mcp.yaml", log_level: int = logging.INFO) -> None:
    """
    MCPサーバーのメインエントリーポイント

    Args:
        config_path: MCP設定ファイルのパス（デフォルト: mcp.yaml）
        log_level: ロギングレベル（デフォルト: INFO）
    """
    # ロギングの設定
    setup_logging(log_level)
    logger.info(f"MCPサーバーを起動しています（設定ファイル: {config_path}）")

    try:
        # 設定ファイルの読み込み
        loader = ConfigLoader()
        mcp_config = loader.load_mcp_config(config_path)

        # モデルをキャッシュ
        mcp_config.cache_models()

        # サーバーの設定
        server = mcp_config.configure()

        # ハンドラー関数の登録
        server.add_tool(
            name="listModels",
            fn=mcp_config.handle_list_models,
            description=mcp_config.config.tool_descriptions.get("listModels", "利用可能なモデルの一覧を取得します"),
        )

        server.add_tool(
            name="getModelInfo",
            fn=lambda request_dict: handle_get_model_info(
                mcp_config.loaded_models, GetModelInfoRequest.model_validate(request_dict)
            ),
            description=mcp_config.config.tool_descriptions.get("getModelInfo", "特定のモデルの詳細情報を取得します"),
        )

        server.add_tool(
            name="getDiagnostics",
            fn=lambda request_dict: handle_get_diagnostics(
                mcp_config.loaded_models, GetDiagnosticsRequest.model_validate(request_dict)
            ),
            description=mcp_config.config.tool_descriptions.get(
                "getDiagnostics", "モデルのバリデーション結果を取得します"
            ),
        )

        server.add_tool(
            name="getFileContent",
            fn=lambda request_dict: handle_get_file_content(
                mcp_config.loaded_models, GetFileContentRequest.model_validate(request_dict)
            ),
            description=mcp_config.config.tool_descriptions.get(
                "getFileContent", "Excelファイルの内容を構造化テキストで取得します"
            ),
        )

        # サーバー起動
        logger.info("MCPサーバーが初期化されました。リクエスト待機中...")
        server.run()  # デフォルトでstdioトランスポートで起動

    except ConfigLoadError as e:
        logger.error(f"設定ファイルの読み込みエラー: {e}")
        sys.exit(1)
    except ConfigValidationError as e:
        logger.error(f"設定ファイルの検証エラー: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"MCPサーバーの起動に失敗しました: {e}")
        sys.exit(1)
