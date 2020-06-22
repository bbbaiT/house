# -*- coding: utf-8 -*-
import time
from bson.json_util import dumps, loads
from db_init import db
from model import user, merchant


class HousePrice(db.EmbeddedDocument):
    country = db.StringField(null=True)      # RMB、USD
    price = db.FloatField(null=True)     # 价格，单位万元
    price_min = db.FloatField(null=True)
    price_max = db.FloatField(null=True)

    def to_json(self):
        return {
            "country": self.country,
            "price": self.price,
            "price_min": self.price_min,
            "price_max": self.price_max
        }


class HouseAddress(db.EmbeddedDocument):
    country = db.StringField(null=True)
    province = db.StringField(null=True)

    def to_json(self):
        return {
            "country": self.country,
            "province": self.province
        }


class House(db.Document):
    create_time = db.IntField(default=time.time())
    update_time = db.IntField(default=time.time())

    merchant = db.ReferenceField(merchant.Merchant, reverse_delete_rule=db.CASCADE)
    create_user = db.ReferenceField(user.User, reverse_delete_rule=db.CASCADE)
    build_merchant_id = db.StringField(null=True)

    name = db.StringField(required=True)
    tags = db.ListField(db.StringField(), default=[])       # 标签
    brief = db.StringField(null=True)

    category_choice = (
        (1, '住宅'),
        (2, '独栋别墅'),
        (3, '联排别墅'),
        (4, '公寓'),
        (5, '商品房'),
    )
    category = db.IntField(choices=category_choice)    # 物业类型 1 住宅、2 独栋别墅、3 联排别墅、4 公寓、5 商业房
    sales_choice = (
        (1, '在售'),
        (2, '代售')
    )
    sales_status = db.IntField(choices=sales_choice)    # 销售状态 1 在售、2 代售
    ren_choice = (
        (1, '毛坯'),
        (2, '普装'),
        (3, '精装')
    )
    renovation = db.IntField(choices=ren_choice)      # 交房标准，1:毛坯 2:普装 3精装
    build_area = db.FloatField(null=True)    # 规则面积
    house_hold = db.IntField(null=True)      # 总户数

    prices = db.ListField(db.EmbeddedDocumentField(HousePrice), default=[])
    address = db.ListField(db.EmbeddedDocumentField(HouseAddress), default=[])

    meta = {
        'collection': 'house',  # 更改数据库表名
        'indexes': ['#merchant']
    }

    def get_id(self):
        return loads(dumps(self.id)).__str__()

    def get_prices(self):
        return [price.to_json() for price in self.prices]

    def get_address(self):
        return [add.to_json() for add in self.address]

    def get_create_user(self):
        return loads(dumps(self.create_user.id)).__str__()

    def get_merchant(self):
        return loads(dumps(self.merchant.id)).__str__()

    def to_json(self):
        return {
            "id": self.get_id(),
            "merchant": self.get_merchant(),
            "create_user": self.get_create_user(),
            "build_merchant_id": self.build_merchant_id,

            "name": self.name,
            "tags": self.tags,
            "brief": self.brief,

            "category": self.category,
            "sales_status": self.sales_status,
            "renovation": self.renovation,
            "build_area": self.build_area,
            "house_hold": self.house_hold,

            "prices": self.get_prices(),
            "address": self.get_address(),

            "create_time": self.create_time,
            "update_time": self.update_time,
        }
