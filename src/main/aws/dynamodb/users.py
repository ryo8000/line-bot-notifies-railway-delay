"""usersエンティティ用モジュール"""

from dataclasses import dataclass
from decimal import Decimal

from aws.dynamodb.base import Base


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
