"""DynamoDB用ユーティリティモジュール"""

import aws.config as aws

db = aws.session.resource('dynamodb', config=aws.config)


def replace_data(obj: object) -> object:
    """登録・更新用データの置換処理
    空文字はNoneに置換
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = replace_data(value)
    elif isinstance(obj, list):
        [replace_data(element) for element in obj]
    elif obj == '':
        obj = None
    return obj
