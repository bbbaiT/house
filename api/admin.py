# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from api.auth import filterLogin, filterAdmin
from model.merchant import Merchant
from model.user import UserMerchant, User
from untils.ans_res import Ans
from db_init import cache


class UserMerchantInfo(Resource):
    '''
    商户员工
    '''
    method_decorators = {
        "post": [filterAdmin, filterLogin],
        "get": [filterAdmin, filterLogin],
        "delete": [filterAdmin, filterLogin],
    }

    def post(self, id):
        req = request.get_json()
        merchant = Merchant.objects.with_id(id)
        phone = req.get('phone', None)
        if not merchant or not phone:
            return Ans(-1, msg='参数错误')

        user_merchant = UserMerchant(
            merchant_id=merchant.get_id(),
            merchant_name=merchant.name,
            name=merchant.contacts,
            roles=req.get('roles', None),
            position=req.get('position', None),
            logo=req.get('logo', None),
            brief=req.get('brief', None),
        )

        user = User.objects.filter(phone=phone).first()
        if not user:
            user = User(
                phone=phone,
                name=req.get('name', None),
                gender=1,
            )
            user.pwd = user.hash_password('123456')
            user.nickname = user.init_nick_name()

        user.merchants.append(user_merchant)
        user.save()
        cache.delete('merchant-{}-employees'.format(id))
        return Ans(0)

    def get(self, id):
        merchant = Merchant.objects.with_id(id)
        if not merchant:
            return Ans(-1, msg='商户不存在')

        cache_data = cache.get('merchant-{}-employees'.format(id))
        if cache_data:
            return Ans(0, data=cache_data)

        data = []
        users = User.objects.all()
        for user in users:
            for m in user.merchants:
                user_merchant = {}
                if m.merchant_id == id:
                    user_merchant['id'] = user.get_id()
                    user_merchant['name'] = user.name
                    user_merchant['phone'] = user.phone
                    user_merchant['roles'] = m.roles
                    user_merchant['position'] = m.position
                    user_merchant['logo'] = m.logo
                    user_merchant['brief'] = m.brief
                    data.append(user_merchant)

        cache.set('merchant-{}-employees'.format(id), data)
        return Ans(0, data=data)

    def delete(self, id):
        req = request.get_json()
        merchant = Merchant.objects.with_id(id)
        user_id = req.get('user_id', None)

        if not merchant:
            return Ans(-1, msg='商户不存在')

        user = User.objects.with_id(user_id)
        for m in user.merchants:
            if m.merchant_id == id:
                user.merchants.remove(m)
        user.save()

        cache.delete('merchant-{}-employees'.format(id))
        return Ans(0)
