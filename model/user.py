# -*- coding: utf-8 -*-
import time
import random
from bson.json_util import dumps, loads
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from db_init import db
from config.config import SECRET_KEY, EXPIRATION


class UserMerchant(db.EmbeddedDocument):
    # 名下的商户
    merchant_id = db.StringField()
    merchant_name = db.StringField()
    name = db.StringField(required=True)
    choice_role = (
        (1, '管理员'),
        (2, '经纪人'),
    )
    roles = db.ListField(db.IntField(choices=choice_role), default=[])  # 1 管理员 2 经纪人
    position = db.StringField(null=True)     # 职位
    logo = db.StringField(null=True)         # Logo
    brief = db.StringField(null=True)        # 商户简介

    def to_json(self):
        return {
            'merchant_name': self.merchant_name,
            'name': self.name,
            'roles': self.roles,
            'position': self.position,
            'logo': self.logo,
            'brief': self.brief,
        }


class User(db.Document):

    phone_area = db.StringField(default='+86')
    phone = db.StringField(required=True, unique=True)
    pwd = db.StringField()
    name = db.StringField(required=True)
    email = db.EmailField(null=True)
    icon = db.StringField(bull=True)
    nickname = db.StringField()

    signature = db.StringField(null=True)        # 签名

    gender_choice = (
        (1, '男'),
        (2, '女'),
    )
    gender = db.IntField(required=True, choices=gender_choice)           # 性别 1 男  2 女

    province = db.StringField(null=True)
    city = db.StringField(null=True)
    country = db.StringField(null=True)

    token = db.StringField()

    create_time = db.IntField(default=time.time())
    update_time = db.IntField(default=time.time())

    is_admin = db.BooleanField(default=False)
    merchants = db.ListField(db.EmbeddedDocumentField(UserMerchant), default=[])

    meta = {
        'collection': 'user',  # 更改数据库表名
        'indexes': [
            '#phone',
            '#token',
            '#pwd'
        ]
    }

    def get_id(self):
        return loads(dumps(self.id)).__str__()

    def init_nick_name(self):
        nickname = '新用户_'
        for nick in random.sample('zyxwvutsrqponmlkjihgfedcbaABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', 10):
            nickname += nick
        return nickname

    # 加密密码
    def hash_password(self, password):
        return pwd_context.encrypt(password)

    # 密码验证
    def verify_password(self, password):
        return pwd_context.verify(password, self.pwd)

    # 加密token，有效期1天
    def generate_auth_token(self, expiration=EXPIRATION):
        s = Serializer(secret_key=SECRET_KEY, expires_in=expiration)
        return str(s.dumps({'id': str(self.id)}), encoding='utf-8')

    def HasMerchantRole(self, merchant_id, rol_int):
        for m in self.merchants:
            if m.merchant_id == merchant_id:
                if rol_int in m.roles:
                    return True
        return False

    def get_merchant(self):
        return [merchant.to_json() for merchant in self.merchants]


    def to_json(self):
        return {
            "id": self.get_id(),
            "phone_area": self.phone_area,
            "phone": self.phone,
            "name": self.name,
            "email": self.email,
            "icon": self.icon,
            "nickname": self.nickname,
            "token": self.token,
            "signature": self.signature,
            "gender": self.gender,

            "province": self.province,
            "city": self.city,
            "country": self.country,
            "is_admin": self.is_admin,
            "merchants": self.get_merchant(),
            "create_time": self.create_time,
            "update_time": self.update_time,
        }

