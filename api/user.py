# -*- coding: utf-8 -*-
import re
from flask import request, g
from flask_restful import Resource
from untils.ans_res import Ans
from model.user import User
from api.auth import filterLogin


class UserRegister(Resource):
    '''
    注册
    '''
    def post(self):
        req = request.get_json()
        pwd = req.get('pwd', None)

        if pwd is None or pwd == "":
            return Ans(-1, msg='密码不得为空')

        if req.get('name', None) is None or req.get('gender', None) is None:
            return Ans(-1, msg='姓名与性别不得为空')

        if not re.match('^1\d{10}$', req.get('phone')):
            return Ans(-1, msg='手机号码格式错误')
        if req.get('email', None):
            if not re.match('^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$', req.get('email')):
                return Ans(-1, msg='邮箱格式错误')

        user = User(
            phone_area=req.get('phone_area', None),
            phone=req.get('phone', None),
            name=req.get('name', None),
            email=req.get('email', None),
            icon=req.get('icon', None),

            signature=req.get('signature', None),
            gender=req.get('gender', None),

            province=req.get('province', None),
            city=req.get('city', None),
            country=req.get('country', None),
        )
        user.pwd = user.hash_password(pwd)
        user.nickname = user.init_nick_name()
        user.save()

        return Ans(0, data=user.to_json())


class UserLogin(Resource):
    '''
    登录
    '''
    def post(self):
        req = request.get_json()
        phone = req.get('phone', None)
        pwd = req.get('pwd', None)

        if pwd is None or pwd == "" or phone is None:
            return Ans(-1, msg='用户名或密码不得为空')

        user = User.objects(phone=phone).first()
        if not user or not user.verify_password(pwd):
            return Ans(-1, msg='用户名或密码不正确')

        user.token = user.generate_auth_token()
        user.save()
        return Ans(0, data={
            'token': user.token
        })


class UserInfo(Resource):
    '''
    详情
    '''
    method_decorators = {
        'get': [filterLogin]
    }

    def get(self):
        user = g.user
        return Ans(0, data=user.to_json())
