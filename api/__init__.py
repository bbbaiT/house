# -*- coding: utf-8 -*-
from api import user, merchant, admin, house, action, upload

all_api = [
    {'view': user.UserRegister, 'api': '/user/register', 'endpoint': 'user_register'},              # 用户注册
    {'view': user.UserLogin, 'api': '/user/login', 'endpoint': 'user_login'},                       # 用户登录
    {'view': user.UserInfo, 'api': '/user', 'endpoint': 'user_info'},                               # 用户详情


    {'view': merchant.MerchantInfo, 'api': '/merchant', 'endpoint': 'merchant_info'},               # 新增商户和商户列表
    {'view': merchant.MerchantKuf, 'api': '/merchant/<id>', 'endpoint': 'merchant_kuf'},            # 具体商户的更新，删除，详情
    {'view': merchant.MerchantExamine, 'api': '/merchant/<id>/examine', 'endpoint': 'merchant_examine'},    # 商户审核
    {'view': merchant.MerchantHouse, 'api': '/merchant/<id>/house', 'endpoint': 'merchant_house'},  # 商户下的房源

    {'view': admin.UserMerchantInfo, 'api': '/merchant/<id>/employees', 'endpoint': 'user_merchant'},   # 商户员工新增，获取商户下的员工， 删除商户下的某一个员工


    {'view': house.HouseInfo, 'api': '/house', 'endpoint': 'house_info'},               # 新增房源和房源列表
    {'view': house.HouseKuf, 'api': '/house/<id>', 'endpoint': 'house_kuf'},               # 具體房源的更新，詳情，刪除


    {'view': action.ActionKuf, 'api': '/action', 'endpoint': 'action_kuf'},               # 阅读，点赞，关注，收藏、单个增删查
]
