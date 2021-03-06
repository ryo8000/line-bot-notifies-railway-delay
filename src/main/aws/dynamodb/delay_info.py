"""delay_infoエンティティ用モジュール"""

from decimal import Decimal

from aws.exceptions import DynamoDBError

from utils.base_class import Json

ALL = 0
WEST_JR = 1
HANKYU = 2
HANSHIN = 3


class Messages(Json):
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


class DelayInfo(Json):
    """鉄道遅延情報クラス"""

    user_id: str
    updated_time: Decimal
    messages: Messages
