"""LINE Bot応答用"""

import json
import os
import random
from datetime import datetime

from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (AudioMessage, FollowEvent, ImageMessage,
                            LocationMessage, MessageEvent, StickerMessage,
                            TextMessage, UnfollowEvent, VideoMessage)
from loguru import logger

import railway
from aws.dynamodb import users, users_table
from functions import texts
from functions.exceptions import TextError
from line import line_bot_api

# 定数群
TEN_MINUTES = 10 * 60
FOLLOW_STAMP_PACKAGE_ID = 11537
FOLLOW_STAMP_STICKER_ID = 52002734

# LINE Bot設定
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])


def main(event: dict, context: dict):
    """LINEイベントに対する応答処理

    Args:
        event: リクエストイベント
        context: コンテキスト
    """
    logger.info("リクエストデータ: {}", json.dumps(event, ensure_ascii=False))

    signature = event['headers']['x-line-signature']
    webhook_event = event['body']
    logger.info("リクエストボディ: {}", webhook_event)

    # 各関数にて処理を実施
    try:
        handler.handle(webhook_event, signature)
    except InvalidSignatureError:
        logger.exception("署名の検証に失敗しました。")
    except Exception:
        logger.exception("応答処理に失敗しました。")


@handler.add(FollowEvent)
def handle_follow(line_event: FollowEvent) -> None:
    """フォロー時に対する処理を実施

    Args:
        line_event: LINEイベント(フォロー)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(フォロー): {}", user_id, line_event)

    if not put_user_info(user_id):
        line_bot_api.reply_text_message(
            line_event.reply_token, user_id, texts.FAIL_REGISTER_USER_INFO)
        return
    line_bot_api.reply_stamp_message(
        line_event.reply_token, user_id, FOLLOW_STAMP_PACKAGE_ID,
        FOLLOW_STAMP_STICKER_ID
    )


@handler.add(UnfollowEvent)
def handle_unfollow(line_event: UnfollowEvent) -> None:
    """フォロー解除時に対する処理を実施

    Args:
        line_event: LINEイベント(フォロー解除)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(フォロー解除): {}", user_id, line_event)

    delete_user_info(user_id)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(line_event: MessageEvent) -> None:
    """テキストメッセージに対する処理を実施

    Args:
        line_event: LINEイベント(テキストメッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(テキストメッセージ): {}", user_id, line_event)

    text = create_reply_text(line_event.message.text)
    line_bot_api.reply_text_message(line_event.reply_token, user_id, text)


@handler.add(MessageEvent, message=StickerMessage)
def handle_stamp_message(line_event: MessageEvent) -> None:
    """スタンプメッセージに対する処理を実施

    Args:
        line_event: LINEイベント(スタンプメッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(スタンプメッセージ): {}", user_id, line_event)

    package_id, sticker_id = create_random_stamp_ids(random.randint(1, 3))
    line_bot_api.reply_stamp_message(
        line_event.reply_token, user_id, package_id, sticker_id)


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(line_event: MessageEvent) -> None:
    """音声メッセージに対する処理を実施

    Args:
        line_event: LINEイベント(音声メッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(音声メッセージ): {}", user_id, line_event)

    text = create_fixed_text(line_event.message.type)
    line_bot_api.reply_text_message(line_event.reply_token, user_id, text)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(line_event: MessageEvent) -> None:
    """画像メッセージに対する処理を実施

    Args:
        line_event: LINEイベント(画像メッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(画像メッセージ): {}", user_id, line_event)

    text = create_fixed_text(line_event.message.type)
    line_bot_api.reply_text_message(line_event.reply_token, user_id, text)


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(line_event: MessageEvent) -> None:
    """位置情報メッセージに対する処理を実施

    Args:
        line_event: LINEイベント(位置情報メッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(位置情報メッセージ): {}", user_id, line_event)

    text = create_fixed_text(line_event.message.type)
    line_bot_api.reply_text_message(line_event.reply_token, user_id, text)


@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(line_event: MessageEvent) -> None:
    """動画メッセージに対する処理を実施

    Args:
        line_event: LINEイベント(動画メッセージ)
    """
    user_id = line_event.source.user_id
    logger.info("[{}] LINEイベント(動画メッセージ): {}", user_id, line_event)

    text = create_fixed_text(line_event.message.type)
    line_bot_api.reply_text_message(line_event.reply_token, user_id, text)


def put_user_info(user_id: str) -> dict:
    """ユーザ情報を登録する

    Args:
        user_id: ユーザID

    Returns:
        dict: ユーザ情報の登録結果
    """
    try:
        response = users_table.put_user(user_id)
    except Exception:
        logger.opt(exception=True).warning("[{}] ユーザ情報の登録に失敗しました。", user_id)
        return {}
    logger.info("[{}] ユーザ情報の登録に成功しました。", user_id)
    return response


def delete_user_info(user_id: str) -> dict:
    """ユーザ情報を削除する

    Args:
        user_id: ユーザID

    Returns:
        dict: ユーザ情報の削除結果
    """
    try:
        response = users_table.delete_user(user_id)
    except Exception:
        logger.opt(exception=True).warning("[{}] ユーザ情報の削除に失敗しました。", user_id)
        return {}
    logger.info("[{}] ユーザ情報の削除に成功しました。", user_id)
    return response


def create_reply_text(text: str) -> str:
    """テキストメッセージに対する応答テキストを作成

    Args:
        text: テキスト

    Returns:
        str: 応答テキスト
    """
    if ("jr" in text) or ("Jr" in text) or ("JR" in text) or ("西" in text):
        reply_text = get_railway_delay_info(users.WEST_JR)
    elif ("阪急" in text) or ("はんきゅう" in text):
        reply_text = get_railway_delay_info(users.HANKYU)
    elif ("阪神" in text) or ("はんしん" in text):
        reply_text = get_railway_delay_info(users.HANSHIN)
    elif ("全" in text) or ("教" in text) or ("確認" in text) or (
            "遅延" in text) or ("現状" in text):
        reply_text = get_railway_delay_info(users.ALL)
    elif ("使い方" in text):
        reply_text = texts.HOW_TO_USE
    elif ("せん" in text) or ("ばか" in text) or ("あほ" in text) or (
            "さよなら" in text) or ("それだと" in text) or ("違う" in text):
        reply_text = texts.COMPLAINT
    elif ("ありがと" in text) or ("どうも" in text):
        reply_text = texts.APPRECIATION
    elif ("おはよ" in text):
        reply_text = texts.GREETING_MORNING
    elif ("こんばん" in text):
        reply_text = texts.GREETING_EVENING
    else:
        reply_text = texts.UNSUPPORTED

    return reply_text


def get_railway_delay_info(company_type: int) -> str:
    """鉄道遅延情報を取得する

    Args:
        company_type: 運営会社種類

    Returns:
        str: 鉄道遅延情報
    """
    railway_user = users_table.get_railway()
    timestamp_now = int(datetime.utcnow().timestamp())
    # 過度なリクエストを避けるため、一定時間内であればDBに登録されている鉄道遅延情報を代用する
    if (railway_user.updated_time + TEN_MINUTES) > timestamp_now:
        delay_info_message = railway_user.delay_info_messages.extract_message(
            company_type)
        logger.info("DBに登録されている鉄道遅延情報を使用: {}", delay_info_message)
    else:
        delay_info_message = railway.request_delay_info_message(company_type)
    return delay_info_message


def create_fixed_text(line_event_type: str) -> str:
    """音声・画像・位置情報・動画メッセージに対する固定テキストを作成

    Args:
        line_event_type: LINEイベント種別

    Raises:
        TextError: LINEイベント種別が正しく設定されていない

    Returns:
        str: 固定テキスト
    """
    if line_event_type == "audio":
        text = texts.AUDIO
    elif line_event_type == "image":
        text = texts.IMAGE
    elif line_event_type == "location":
        text = texts.LOCATION
    elif line_event_type == "video":
        text = texts.VIDEO
    else:
        raise TextError(
            f"LINEイベント種別が正しく設定されていません。LINEイベント種別: {line_event_type}")
    return text


def create_random_stamp_ids(rnd: int) -> tuple:
    """スタンプ用IDをランダムに生成する

    Args:
        rnd: 乱数

    Returns:
        tuple: スタンプセットのパッケージIDとスタンプID
    """
    package_id = 11537
    sticker_id = 52002749
    if rnd == 1:
        package_id = 11537
        sticker_id = 52002764
    elif rnd == 2:
        package_id = 11537
        sticker_id = 52002754
    return package_id, sticker_id
