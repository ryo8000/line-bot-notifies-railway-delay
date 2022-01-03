"""鉄道用モジュール"""

import json

import requests
from loguru import logger

from aws.dynamodb import users_table
from aws.dynamodb.users import DelayInfoMessages

# 定数群
DELAY_URL = "https://tetsudo.rti-giken.jp/free/delay.json"
WEST_JR_URL = "https://trafficinfo.westjr.co.jp/kinki.html"
HANKYU_URL = "https://www.hankyu.co.jp/railinfo/"
HANSHIN_URL = "https://rail.hanshin.co.jp/railinfo/"


def request_delay_info_message(company_type: int) -> str:
    """鉄道遅延情報メッセージを取得する

    Args:
        company_type: 運営会社種類

    Raises:
        e: 鉄道遅延情報メッセージの取得／登録に失敗

    Returns:
        str: 鉄道遅延情報メッセージ
    """
    logger.info("鉄道遅延情報メッセージを取得します。 運営会社種類: {}", company_type)
    try:
        delay_info_list = _request_delay_info_list()
        delay_info_messages = _generate_delay_info_messages(delay_info_list)
    except Exception as e:
        logger.error("鉄道遅延情報メッセージの取得に失敗しました。")
        raise e
    logger.info("鉄道遅延情報メッセージの取得に成功しました。 鉄道遅延情報メッセージ: {}", delay_info_messages)

    try:
        users_table.update_railway(delay_info_messages)
    except Exception as e:
        logger.error("鉄道遅延情報メッセージの登録に失敗しました。")
        raise e
    delay_info_message = delay_info_messages.extract_message(company_type)
    return delay_info_message


def _request_delay_info_list() -> list:
    """鉄道遅延情報リストを要求する

    Raises:
        e: 鉄道遅延情報リストの取得に失敗

    Returns:
        list: 鉄道遅延情報リスト
    """
    try:
        delay_info_list = requests.get(DELAY_URL).json()
    except Exception as e:
        logger.error("鉄道遅延情報リストの取得に失敗しました。")
        raise e
    logger.info(
        "鉄道遅延情報リスト: {}",
        json.dumps(delay_info_list, ensure_ascii=False)
    )
    return delay_info_list


def _generate_delay_info_messages(delay_info_list: list) -> DelayInfoMessages:
    """鉄道遅延情報リストから運営会社毎の鉄道遅延情報メッセージを作成する

    Args:
        delay_info_list: 鉄道遅延情報リスト

    Returns:
        DelayInfoMessages: 鉄道遅延情報メッセージ群
    """
    west_jr_delay_lines = []
    hankyu_delay_lines = []
    hanshin_delay_lines = []
    for delay_info in delay_info_list:
        # JR西日本
        if _is_match(delay_info, "JR西日本", "学研都市線"):
            west_jr_delay_lines.append("JR学研都市線")
        elif _is_match(delay_info, "JR西日本", "ＪＲ東西線") or _is_match(
                delay_info, "JR西日本", "JR東西線"):
            west_jr_delay_lines.append("JR東西線")
        elif _is_match(delay_info, "JR西日本", "ＪＲ神戸線") or _is_match(
                delay_info, "JR西日本", "JR神戸線"):
            west_jr_delay_lines.append("JR神戸線")

        # 阪急電鉄
        if _is_match(delay_info, "阪急電鉄", "阪急線"):
            hankyu_delay_lines.append("阪急線")
        elif _is_match(delay_info, "阪急電鉄", "神戸線"):
            hankyu_delay_lines.append("阪急神戸線")
        elif _is_match(delay_info, "阪急電鉄", "神戸本線"):
            hankyu_delay_lines.append("阪急神戸本線")

        # 阪神電気鉄道
        elif _is_match(delay_info, "阪神電気鉄道", "阪神線"):
            hanshin_delay_lines.append("阪神線")
        elif _is_match(delay_info, "阪神電気鉄道", "阪神本線"):
            hanshin_delay_lines.append("阪神本線")
        elif _is_match(delay_info, "阪神電気鉄道", "神戸高速線"):
            hanshin_delay_lines.append("阪神神戸高速線")

    west_jr_delay_info_message = f"{', '.join(west_jr_delay_lines)}が遅延しています。\n{WEST_JR_URL}" if west_jr_delay_lines else "JR西日本の遅延情報はありません。"
    hankyu_delay_info_message = f"{', '.join(hankyu_delay_lines)}が遅延しています。\n{HANKYU_URL}" if hankyu_delay_lines else "阪急電鉄の遅延情報はありません。"
    hanshin_delay_info_message = f"{', '.join(hanshin_delay_lines)}が遅延しています。\n{HANSHIN_URL}" if hanshin_delay_lines else "阪神電鉄の遅延情報はありません。"

    if not (west_jr_delay_lines or hankyu_delay_lines or hanshin_delay_lines):
        all_companies_delay_info_message = "兵庫～大阪間の鉄道の遅延情報はありません。"
    else:
        all_companies_delay_lines = west_jr_delay_lines + \
            hankyu_delay_lines + hanshin_delay_lines
        all_companies_delay_info_message = f"{', '.join(all_companies_delay_lines)}が遅延しています。"
        if west_jr_delay_lines:
            all_companies_delay_info_message += f"\n{WEST_JR_URL}"
        if hankyu_delay_lines:
            all_companies_delay_info_message += f"\n{HANKYU_URL}"
        if hanshin_delay_lines:
            all_companies_delay_info_message += f"\n{HANSHIN_URL}"

    delay_info_messages = DelayInfoMessages(
        west_jr_delay_info_message,
        hankyu_delay_info_message,
        hanshin_delay_info_message,
        all_companies_delay_info_message
    )
    logger.info("鉄道遅延情報メッセージ群: {}", delay_info_messages)
    return delay_info_messages


def _is_match(delay_info: dict, company: str, line: str) -> bool:
    """対象の鉄道かどうか判定する

    Args:
        delay_info: 鉄道遅延情報
        company: 運営会社名
        line: 路線名

    Raises:
        e: JSON内に処理対象のキーが存在しない

    Returns:
        bool: 対象の鉄道の場合はTrue
    """
    try:
        return delay_info['company'] == company and delay_info['name'] == line
    except KeyError as e:
        logger.error("JSON内に処理対象のキーが存在しません。")
        raise e
