"""AWS用エラーモジュール"""


class BaseError(Exception):
    """AWS用基底例外クラス"""
    pass


class DynamoDBError(BaseError):
    """DynamoDB用エラークラス"""
    pass
