"""DynamoDB用エンティティ基底モジュール"""

from pydantic import BaseModel


class Base(BaseModel):
    """エンティティ基底クラス"""

    def __str__(self):
        return self.to_json_string()

    def to_json_string(self) -> str:
        """JSON文字列に変換"""
        return self.json(
            ensure_ascii=False
        )

    def to_dict(self) -> dict:
        """dict型に変換"""
        return self.dict()

    @classmethod
    def from_dict(cls, obj: dict):
        """dict型のデータからインスタンスを生成"""
        return cls.parse_obj(obj)
