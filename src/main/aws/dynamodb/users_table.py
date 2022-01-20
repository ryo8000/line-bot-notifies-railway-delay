"""users_table操作用モジュール"""

import os
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from botocore.exceptions import ClientError

from aws.dynamodb import utils
from aws.dynamodb.delay_info import DelayInfo, Messages
from aws.dynamodb.users import User
from aws.exceptions import DynamoDBError

users_table = utils.db.Table(os.environ['AWS_USERS_TABLE'])


def put_user(user_id: str) -> User:
    """ユーザ情報を登録する

    Args:
        user_id: ユーザID

    Raises:
        e: ユーザ情報の登録に失敗

    Returns:
        登録したユーザ情報
    """
    timestamp_now = Decimal(datetime.utcnow().timestamp())
    user = User(
        user_id=user_id,
        created_time=timestamp_now,
        updated_time=timestamp_now
    )
    try:
        users_table.put_item(
            Item=utils.replace_data(user.to_dict())
        )
    except ClientError as e:
        raise e
    return user


def update_user(user_id: str, messages: Messages) -> dict:
    """ユーザ情報を更新する

    Args:
        user_id: ユーザID
        messages: 鉄道遅延情報メッセージ群

    Raises:
        e: ユーザ情報の更新に失敗

    Returns:
        ユーザ情報の更新結果
    """
    key = {'user_id': user_id}
    expression = "set #messages=:messages, #updated_time=:updated_time"
    expression_name = {
        '#messages': 'messages',
        '#updated_time': 'updated_time'
    }
    expression_value = {
        ':messages': messages.to_dict(),
        ':updated_time': Decimal(datetime.utcnow().timestamp()),
    }
    return_value = "UPDATED_NEW"
    try:
        response = users_table.update_item(
            Key=key,
            UpdateExpression=expression,
            ExpressionAttributeNames=expression_name,
            ExpressionAttributeValues=utils.replace_data(expression_value),
            ReturnValues=return_value
        )
    except ClientError as e:
        raise e
    return response


def update_delay_info(messages: Messages) -> dict:
    """鉄道遅延情報を更新する

    Args:
        messages: 鉄道遅延情報メッセージ群

    Returns:
        鉄道遅延情報の更新結果
    """
    return update_user("railway", messages)


def delete_user(user_id: str) -> dict:
    """ユーザ情報を削除する

    Args:
        user_id: ユーザID

    Raises:
        e: ユーザ情報の削除に失敗

    Returns:
        ユーザ情報の削除結果
    """
    key = {'user_id': user_id}
    try:
        response = users_table.delete_item(Key=key)
    except ClientError as e:
        raise e
    return response


def get_user(user_id: str) -> Optional[User]:
    """ユーザ情報を取得する

    Args:
        user_id: ユーザID

    Raises:
        e: ユーザ情報の取得に失敗

    Returns:
        ユーザ情報
    """
    key = {'user_id': user_id}
    try:
        response = users_table.get_item(Key=key)
    except ClientError as e:
        raise e
    item = response.get('Item')
    return User.from_dict(item) if item else None


def get_delay_info() -> DelayInfo:
    """鉄道遅延情報を取得する

    Raises:
        DynamoDBError: 鉄道遅延情報が登録されていない

    Returns:
        鉄道遅延情報
    """
    key = {'user_id': 'railway'}
    try:
        response = users_table.get_item(Key=key)
    except ClientError as e:
        raise e
    item = response.get('Item')
    if not item:
        raise DynamoDBError("鉄道遅延情報が登録されていません。")
    return DelayInfo.from_dict(item)


def scan_exclude_delay_info() -> List[User]:
    """鉄道遅延情報を除く全ユーザ情報を取得する

    Raises:
        e: ユーザ情報の取得に失敗

    Returns:
        鉄道遅延情報を除く全ユーザ情報リスト
    """
    scan_kwargs = {
        'FilterExpression': 'user_id  <> :user_id',
        'ExpressionAttributeValues': {':user_id': 'railway'}
    }
    try:
        response = users_table.scan(**scan_kwargs)
    except ClientError as e:
        raise e
    return [User.from_dict(item) for item in response["Items"]]
