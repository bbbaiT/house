# -*- coding: utf-8 -*-
import time
from bson.json_util import dumps, loads
from db_init import db
from model.user import User


class Action(db.Document):
    create_time = db.IntField(default=time.time())
    update_time = db.IntField(default=time.time())

    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    action_type_choice = (
        (1, '阅读'),
        (2, '点赞'),
        (3, '收藏'),
        (4, '关注'),
    )
    action_type = db.IntField(choices=action_type_choice)
    object_id = db.StringField(required=True)

    addition = db.StringField(null=True)
    is_del = db.BooleanField(default=False)

    meta = {
        "collection": "action",
        "indexes": ["#is_del", "#action_type", "#user", "#object_id"]
    }

    def get_id(self):
        return loads(dumps(self.id)).__str__()

    def get_user(self):
        return loads(dumps(self.user.id)).__str__()

    def to_json(self):
        return {
            "id": self.get_id(),
            "user": self.get_user(),
            "action_type": self.action_type,
            "object_id": self.object_id,
            "addition": self.addition,
            "create_time": self.create_time,
            "update_time": self.update_time,
        }
