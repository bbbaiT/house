# -*- coding: utf-8 -*-
from flask import request, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from untils.ans_res import Ans
from config.config import SECRET_KEY
from model.user import User


# token校验
def filterLogin(func):
    def wrapper(*args, **kwargs):
        token_req = request.headers.get('Token')
        if token_req is None:
            return Ans(-1, msg='请登录后操作')
        try:
            s = Serializer(secret_key=SECRET_KEY)
            data = s.loads(token_req)
            if data['id'] == 'None':
                return Ans(-1, '请登录后操作')
            user = User.objects(id=data['id']).first()
            g.user = user
        except SignatureExpired:
            # token正确，但过期了
            return Ans(-1, msg='请重新登录')
        except BadSignature:
            # token错误
            return Ans(-1, msg='请登录后操作')

        return func(*args, **kwargs)
    return wrapper


# 权限校验
def filterAdmin(func):
    def wrapper(*args, **kwargs):
        if not g.user.is_admin:
            return Ans(-1, msg='无权限，请联系管理员')
        return func(*args, **kwargs)
    return wrapper


