"""usersエンティティ用モジュール"""

from dataclasses import dataclass
from decimal import Decimal

from aws.dynamodb.base import Base
from aws.exceptions import DynamoDBError

ALL = 0
WEST_JR = 1
HANKYU = 2
HANSHIN = 3


@dataclass
class DelayInfoMessages(Base):
    """鉄道遅延情報メッセージ群クラス"""

    west_jr: str
    hankyu: str
    hanshin: str
    all: str

    def extract_message(self, company_type: int) -> str:
        """鉄道遅延情報メッセージ群から対象の鉄道遅延情報メッセージを抽出する

        Args:
            company_type: 運営会社種類

        Raises:
            DynamoDBError: 運営会社種類が正しく設定されていない

        Returns:
            対象の鉄道遅延情報メッセージ
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

    @classmethod
    def from_dict(cls, delay_info_messages: dict):
        """dict型のデータからDelayInfoMessagesインスタンスを生成する

        Args:
            delay_info_messages: dict型データ

        Returns:
            DelayInfoMessagesインスタンス
        """
        return cls(delay_info_messages["west_jr"],
                   delay_info_messages["hankyu"],
                   delay_info_messages["hanshin"],
                   delay_info_messages["all"])


@dataclass
class User(Base):
    """ユーザクラス"""

    user_id: str
    created_time: Decimal
    updated_time: Decimal

    @classmethod
    def from_dict(cls, user: dict):
        """dict型のデータからUserインスタンスを生成する

        Args:
            user: dict型データ

        Returns:
            Userインスタンス
        """
        return cls(user["user_id"],
                   user["created_time"],
                   user["updated_time"])


@dataclass
class Railway(Base):
    """鉄道用ユーザクラス"""

    user_id: str
    updated_time: Decimal
    delay_info_messages: DelayInfoMessages

    @classmethod
    def from_dict(cls, railway: dict):
        """dict型のデータからRailwayインスタンスを生成する

        Args:
            railway: dict型データ

        Returns:
            Railwayインスタンス
        """
        delay_info_messages = railway.get("delay_info_messages")
        type_delay_info_messages = DelayInfoMessages.from_dict(
            delay_info_messages) if delay_info_messages else None
        return cls(railway["user_id"],
                   railway["updated_time"],
                   type_delay_info_messages)