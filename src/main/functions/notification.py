"""LINE Bot通知用"""

from loguru import logger

import railway
from aws.dynamodb import users, users_table
from line import line_bot_api


def main(event: dict, context: object) -> None:
    """LINE通知処理

    Args:
        event: イベント
        context: コンテキスト
    """
    try:
        railway_user = users_table.get_railway()
        db_railway_delay_info_message = railway_user.messages.all

        latest_railway_delay_info_message = railway.request_delay_info_message(
            users.ALL)

        if not validate_railway_delay_info(latest_railway_delay_info_message,
                                           db_railway_delay_info_message):
            return

        notify_all_users_of_railway_delay_info(
            latest_railway_delay_info_message)
    except Exception:
        logger.exception("通知処理に失敗しました。")


def validate_railway_delay_info(latest_railway_delay_info_message: str,
                                db_railway_delay_info_message: str) -> bool:
    """通知対象の鉄道遅延情報かどうか検証する

    Args:
        latest_railway_delay_info_message: 最新の鉄道遅延情報
        db_railway_delay_info_message: DBに登録されている鉄道遅延情報

    Returns:
        通知対象の鉄道遅延情報の場合はTrue
    """
    if "遅延情報はありません。" in latest_railway_delay_info_message:
        logger.info("通知対象の遅延情報はありません。")
        return False
    elif latest_railway_delay_info_message == db_railway_delay_info_message:
        logger.info("最新の遅延情報は前回配信した遅延情報から変化がありません。")
        return False
    return True


def notify_all_users_of_railway_delay_info(
        railway_delay_info_message: str) -> None:
    """全ユーザに鉄道遅延情報を通知する

    Args:
        railway_delay_info_message: 鉄道遅延情報

    Raises:
        e: ユーザ情報の取得に失敗
    """
    try:
        users = users_table.scan_exclude_railway()
    except Exception as e:
        logger.error("ユーザ情報の取得に失敗しました。")
        raise e

    for user in users:
        user_id = user.user_id
        # 途中で例外が発生しても最後まで処理を続ける
        try:
            line_bot_api.push_text_message(user_id, railway_delay_info_message)
        except Exception:
            logger.opt(exception=True).warning(
                "鉄道遅延情報の通知に失敗しましたが処理を続行します。 ユーザID: {}", user_id)
