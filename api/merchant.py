# -*- coding: utf-8 -*-
import time
from flask import request, g
from flask_restful import Resource
from api.auth import filterLogin, filterAdmin
from model.merchant import Merchant
from model.user import User, UserMerchant
from model.house import House
from untils.ans_res import Ans
from db_init import cache


class MerchantInfo(Resource):
    '''
    增加商户，商户列表
    '''
    method_decorators = {
        'post': [filterLogin],
        'get': [filterLogin],
    }

    def post(self):
        req = request.get_json()
        user = g.user

        merchant = Merchant(
            create_user=user,
            is_self=req.get('is_self', False),

            name=req.get('name', None),
            brief=req.get('brief', None),
            logo=req.get('logo', None),
            htype=req.get('htype', 0),
            service=req.get('service', 0),
            status=req.get('status', ),

            contacts=req.get('contacts', user.name),
            phone=req.get('phone', user.phone),
        ).save()
        cache.delete('merchant_list_{}'.format(user.get_id()))
        return Ans(0, data=merchant.to_json())

    def get(self):
        # 管理员返回所有，不是管理员返回名下商户
        user = g.user
        cache_data = cache.get('merchant_list_{}'.format(user.get_id()))
        if cache_data:
            return Ans(0, data=cache_data)
        if user.is_admin:
            merchant = Merchant.objects.all()
        else:
            merchant = Merchant.objects.filter(create_user=user)
        merchant_list = [data.to_json() for data in merchant]

        cache.set('merchant_list_{}'.format(user.get_id()), merchant_list)
        return Ans(0, data=merchant_list)


class MerchantKuf(Resource):
    '''
    具体商户
    '''
    method_decorators = {
        'put': [filterLogin],
        'delete': [filterAdmin, filterLogin],
    }

    def put(self, id):
        req = request.get_json()
        merchant = Merchant.objects.with_id(id)
        if not merchant:
            return Ans(-1, msg='商户不存在')

        if not self.filterUser(merchant):
            return Ans(-1, msg='无权限')

        for key in req.keys():
            merchant[key] = req[key]
        merchant.update_time = time.time()
        merchant.save()
        return Ans(0, data=merchant.to_json())

    def get(self, id):
        merchant = Merchant.objects.with_id(id)

        if not merchant:
            return Ans(-1, msg='商户不存在')

        return Ans(0, data=merchant.to_json())

    def delete(self, id):
        merchant = Merchant.objects.with_id(id)
        if not merchant:
            return Ans(-1, msg='参数错误')
        if not self.filterUser(merchant):
            return Ans(-1, msg='无权限')
        merchant.delete()

        return Ans(0)

    def filterUser(self, merchant):
        user = g.user
        if merchant.create_user != user:
            return False
        return True


class MerchantExamine(Resource):
    '''
    商户审核
    '''
    method_decorators = {
        'post': [filterLogin]
    }

    def put(self, id):
        merchant = Merchant.objects.with_id(id)
        if not merchant:
            return Ans(-1, msg='商户不存在')

        merchant.status = 2
        merchant.settled_time = time.time()

        # 将商户联系人设为管理员
        # 联系人不在自动创建
        user = User.objects.filter(phone=merchant.phone).first()
        if not user:
            user = User(
                phone=merchant.phone,
                name=merchant.contacts,
                gender=1,
            )
            user.pwd = user.hash_password('123456')
            user.nickname = user.init_nick_name()

        user_merchant = UserMerchant(
            merchant_id=merchant.get_id(),
            merchant_name=merchant.name,
            name=merchant.contacts,
            roles=[1],
        )

        user.merchants.append(user_merchant)
        user.save()

        cache.delete('merchant-{}-employees'.format(id))        # 删除商户下的员工缓存
        return Ans(0)


class MerchantHouse(Resource):
    '''
    商户下的房产
    '''
    def get(self, id):
        merchant = Merchant.objects.with_id(id)
        if not merchant:
            return Ans(-1, msg='商户不存在')

        try:
            page = int(request.args.get('p', 1))
            size = int(request.args.get('s', 10))
        except:
            return Ans(-1, msg='参数错误')

        cache_data = cache.get('merchant_house:{}-{}'.format(page, size))
        if cache_data:
            return Ans(0, data=cache_data)

        house_list = House.objects.filter(merchant=merchant)[(page-1)*size: page*size]

        data = [house.to_json() for house in house_list]

        cache.set('merchant_house:{}-{}'.format(page, size), data)
        return Ans(0, data=data)
