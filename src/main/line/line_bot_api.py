"""LINE Bot API用モジュール"""

import os

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import StickerSendMessage, TextSendMessage
from loguru import logger

# LINE Bot設定
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])


def reply_text_message(reply_token: str, user_id: str, text: str) -> None:
    """テキストメッセージを応答する

    Args:
        reply_token: 応答トークン
        user_id: ユーザID
        text: メッセージのテキスト

    Raises:
        error: テキストメッセージの応答に失敗
    """
    logger.info("ユーザID: {}, 応答テキストメッセージ: {}", user_id, text)
    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    except LineBotApiError as error:
        logger.error("テキストメッセージの応答に失敗しました。 ユーザID: {}", user_id)
        raise error


def reply_stamp_message(reply_token: str, user_id: str,
                        package_id: int, sticker_id: int) -> None:
    """スタンプメッセージを応答する

    Args:
        reply_token: 応答トークン
        user_id: ユーザID
        package_id: スタンプセットのパッケージID
        sticker_id: スタンプID

    Raises:
        error: スタンプメッセージの応答に失敗
    """
    logger.info(
        "ユーザID: {}, 応答スタンプメッセージ: [パッケージID: {}, スタンプID: {}]",
        user_id, package_id, sticker_id
    )
    try:
        line_bot_api.reply_message(
            reply_token,
            StickerSendMessage(
                package_id=package_id,
                sticker_id=sticker_id
            )
        )
    except LineBotApiError as error:
        logger.error("スタンプメッセージの応答に失敗しました。 ユーザID: {}", user_id)
        raise error


def push_text_message(user_id: str, text: str) -> None:
    """テキストメッセージを通知する

    Args:
        user_id: ユーザID
        text: メッセージのテキスト

    Raises:
        error: テキストメッセージの通知に失敗
    """
    logger.info("ユーザID: {}, 通知テキストメッセージ: {}", user_id, text)
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    except LineBotApiError as error:
        logger.error("テキストメッセージの通知に失敗しました。 ユーザID: {}", user_id)
        raise error
