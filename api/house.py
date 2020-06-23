# -*- coding: utf-8 -*-
import time
from flask import request, g
from flask_restful import Resource
from model.house import House, HousePrice, HouseAddress
from model.merchant import Merchant
from api.auth import filterLogin, filterAdmin
from untils.ans_res import Ans
from db_init import cache


class HouseInfo(Resource):
    '''
    增加房源，房源列表
    '''
    method_decorators = {
        'post': [filterLogin]
    }

    def post(self):
        req = request.get_json()
        user = g.user
        prices = req.get('prices', None)
        addresses = req.get('address', None)
        merchant_id = req.get("merchant_id", None)
        merchant = Merchant.objects.with_id(merchant_id)
        if merchant is None:
            return Ans(-1, '商户不存在')

        # 商户中有管理员权限
        if not user.HasMerchantRole(merchant_id, 1):
            return Ans(-1, '无权限')

        house = House(
            merchant=merchant,
            create_user=user,
            build_merchant_id=req.get("build_merchant_id", None),
    
            name=req.get("name", None),
            tags=req.get("tags", []),
            brief=req.get("brief", None),
    
            category=req.get('category', None),
            sales_status=req.get('sales_status', None),
    
            renovation=req.get('renovation', None),
            build_area=req.get('build_area', None),
            house_hold=req.get('house_hold', None),
        )

        if prices is not None:
            for price in prices:
                house_price = HousePrice(
                    country=price.get('country', None),
                    price=price.get('price', None),
                    price_min=price.get('price_min', None),
                    price_max=price.get('price_max', None),
                )
                house.prices.append(house_price)
        if addresses is not None:
            for address in addresses:
                house_add = HouseAddress(
                    country=address.get('country', None),
                    province=address.get('province', None)
                )
                house.address.append(house_add)
        house.save()

        return Ans(0, data=house.to_json())

    def get(self):
        '''
        不加p参数，默认第一页，不加s参数，默认一页10个
        :return:
        '''
        try:
            page = int(request.args.get('p', 1))
            size = int(request.args.get('s', 10))
        except:
            return Ans(-1, msg='参数错误')

        cache_data = cache.get('houses:{}-{}'.format(page, size))
        if cache_data:
            return Ans(0, data=cache_data, count=House.objects.count())

        house_list = House.objects.all()[(page-1)*size: page*size]
        data = [house.to_json() for house in house_list]

        cache.set('houses:{}-{}'.format(page, size), data)
        return Ans(0, data=data, count=House.objects.count())


class HouseKuf(Resource):
    '''
    具体房源
    '''
    method_decorators = {
        'put': [filterLogin],
        'delete': [filterAdmin, filterLogin],
    }

    def get(self, id):
        house = House.objects.with_id(id)
        if not house:
            return Ans(-1, msg='房源不存在')
        return Ans(0, data=house.to_json())

    def put(self, id):
        req = request.get_json()
        house = House.objects.with_id(id)

        if not house:
            return Ans(-1, msg='商户不存在')

        if not self.filterUser(house):
            return Ans(-1, msg='无权限')

        for key in req.keys():
            house[key] = req[key]
        house.update_time = time.time()
        house.save()
        return Ans(0, data=house.to_json())

    def delete(self, id):
        house = House.objects.with_id(id)
        house.delete()
        return Ans(0)

    def filterUser(self, house):
        user = g.user
        if house.create_user != user:
            return False
        return True


class HouseGood(Resource):
    '''
    抢单思路，采用先到先得思路
    使用redis的list的队列，将一个商品做一个list，list长度为商品的数量，值为1(值随便)

    设置一个标志0、1，标记抢单是否一开始，0时请求直接返回未开始，1时进入排队队列

    请求进来先查询对应商品的list长度，如果>0则取pop一个，（redis是单线程，所以多个请求同时到来也是一个一个执行）
    商品list长度<0，直接返回没抢到

    将抢到的用户和 商品信息 放进一个订单队列，做下一步的结算做准备。同时另开一个线程将用户的订单信息入库
    '''
