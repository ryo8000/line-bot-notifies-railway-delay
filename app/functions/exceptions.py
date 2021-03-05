"""AWS Lambda用エラーモジュール"""


class BaseError(Exception):
    """AWS Lambda用基底例外クラス"""
    pass


class TextError(BaseError):
    """テキスト生成エラークラス"""
    pass
