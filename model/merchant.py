# -*- coding: utf-8 -*-
import time
from bson.json_util import dumps, loads
from db_init import db
from model import user


class Merchant(db.Document):
    create_time = db.IntField(default=time.time())
    update_time = db.IntField(default=time.time())
    settled_time = db.IntField()        # 入驻时间

    create_user = db.ReferenceField(user.User, reverse_delete_rule=db.CASCADE)
    is_self = db.BooleanField(default=False)     # 是否官方

    name = db.StringField(null=True)
    brief = db.StringField(null=True)
    logo = db.StringField(null=True)
    htype = db.IntField()       # 商家类型 1 地产商、2 中介，代理商
    service = db.IntField()     # 所需服务 1 推广获客、2 品牌推广
    status = db.IntField()      # 状态 1 申请中、2 已入驻

    contacts = db.StringField()
    phone = db.StringField()

    meta = {
        'collection': 'merchant',  # 更改数据库表名
    }

    def get_create_user_name(self):
        return self.create_user.name

    def get_id(self):
        return loads(dumps(self.id)).__str__()

    def to_json(self):
        return {
            "id": self.get_id(),
            "name": self.name,
            "brief": self.brief,
            "logo": self.logo,
            "htype": self.htype,
            "service": self.service,
            "status": self.status,

            "create_user": self.get_create_user_name(),
            "is_self": self.is_self,

            "contacts": self.contacts,
            "phone": self.phone,

            "settled_time": self.settled_time,

            "create_time": self.create_time,
            "update_time": self.update_time,
        }

    def __str__(self):
        return self.name
