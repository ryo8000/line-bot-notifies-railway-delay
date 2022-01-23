"""usersエンティティ用モジュール"""

from decimal import Decimal

from aws.dynamodb.base import Base


class User(Base):
    """ユーザクラス"""

    user_id: str
    created_time: Decimal
    updated_time: Decimal
