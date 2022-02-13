"""usersエンティティ用モジュール"""

from decimal import Decimal

from utils.base_class import Json


class User(Json):
    """ユーザクラス"""

    user_id: str
    created_time: Decimal
    updated_time: Decimal
