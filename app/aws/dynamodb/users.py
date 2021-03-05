"""usersエンティティ用モジュール"""

from decimal import Decimal

from aws.dynamodb.base import Base
from aws.exceptions import DynamoDBError

ALL = 0
WEST_JR = 1
HANKYU = 2
HANSHIN = 3


class User(Base):
    """ユーザクラス"""

    def __init__(self, user_id: str, created_time: Decimal,
                 updated_time: Decimal, delay_info_messages: dict = None):
        self.user_id = user_id
        self.created_time = created_time
        self.updated_time = updated_time
        self.delay_info_messages = DelayInfoMessages(
            delay_info_messages['west_jr'],
            delay_info_messages['hankyu'],
            delay_info_messages['hanshin'],
            delay_info_messages['all']) if delay_info_messages else None


class DelayInfoMessages(Base):
    """鉄道遅延情報メッセージ群クラス"""

    def __init__(self, west_jr: str, hankyu: str, hanshin: str, all: str):
        self.west_jr = west_jr
        self.hankyu = hankyu
        self.hanshin = hanshin
        self.all = all

    def extract_message(self, company_type: int) -> str:
        """鉄道遅延情報メッセージ群から対象の鉄道遅延情報メッセージを抽出する

        Args:
            company_type: 運営会社種類

        Raises:
            DynamoDBError: 運営会社種類が正しく設定されていない

        Returns:
            str: 対象の鉄道遅延情報メッセージ
        """
        if company_type == WEST_JR:
            extracted_message = self.west_jr
        elif company_type == HANKYU:
            extracted_message = self.hankyu
        elif company_type == HANSHIN:
            extracted_message = self.hanshin
        elif company_type == ALL:
            extracted_message = self.all
        else:
            raise DynamoDBError(f"運営会社種類が正しく設定されていません。運営会社種類: {company_type}")
        return extracted_message
