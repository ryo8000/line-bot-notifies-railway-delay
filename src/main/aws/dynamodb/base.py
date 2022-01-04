"""DynamoDB用エンティティ基底モジュール"""

import json
from decimal import Decimal


class Base():
    """エンティティ基底クラス"""

    def __str__(self):
        return self.to_json_string()

    def __repr__(self):
        return str(self)

    def to_json_string(self) -> str:
        """JSON文字列に変換"""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            default=self._convert_value)

    def to_dict(self) -> dict:
        """dict型に変換"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (list, tuple, set)):
                data[key] = list()
                for item in value:
                    if hasattr(item, "to_dict"):
                        data[key].append(item.to_dict())
                    else:
                        data[key].append(item)
            elif hasattr(value, "to_dict"):
                data[key] = value.to_dict()
            elif value is not None:
                data[key] = value

        return data

    def _convert_value(self, value):
        """json.dumps()で処理できないデータ型の変換処理"""
        if isinstance(value, Decimal):
            return float(value) if value % 1 > 0 else int(value)
        raise TypeError(f"適切な型のデータに変換できません。 値: {repr(value)}")