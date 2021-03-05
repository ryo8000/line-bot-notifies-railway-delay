"""DynamoDB用エンティティ基底モジュール"""

import json


class Base():
    """エンティティ基底クラス"""

    def __str__(self) -> str:
        return json.dumps(self.as_json_dict(),
                          ensure_ascii=False, sort_keys=True)

    def to_dict(self) -> dict:
        """dict型に変換"""
        return self.as_json_dict()

    def as_json_dict(self) -> dict:
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (list, tuple, set)):
                data[key] = list()
                for item in value:
                    if hasattr(item, 'as_json_dict'):
                        data[key].append(item.as_json_dict())
                    else:
                        data[key].append(item)

            elif hasattr(value, 'as_json_dict'):
                data[key] = value.as_json_dict()
            elif value is not None:
                data[key] = value

        return data
