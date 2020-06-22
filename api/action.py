# -*- coding: utf-8 -*-
from flask import request, g
from flask_restful import Resource
from model.action import Action
from model.house import House
from model.merchant import Merchant
from api.auth import filterLogin
from untils.ans_res import Ans


class ActionKuf(Resource):
    method_decorators = {
        'post': [filterLogin],
        'get': [filterLogin],
        'delete': [filterLogin],
    }

    def post(self):
        req = request.get_json()
        object_id = req.get('object_id', None)

        if object_id:
            if not House.objects.with_id(object_id) and not Merchant.objects.with_id(object_id):
                return Ans(-1, msg='对象不存在')

        if Action.objects(user=g.user, action_type=req.get('action_type', None), object_id=object_id, is_del=False).first():
            return Ans(-1, msg='记录已存在')

        action = Action(
            user=g.user,
            action_type=req.get('action_type', None),
            object_id=object_id,

            addition=req.get('addition', None),
        ).save()
        return Ans(0, data=action.to_json())

    def get(self):
        action_type = int(request.args.get('a', 1))

        action_list = Action.objects.filter(user=g.user, action_type=action_type, is_del=False)
        data = [action.to_json() for action in action_list]
        return Ans(0, data=data)

    def delete(self):
        req = request.get_json()
        action_type = int(req.get('a', 1))
        object_id = req.get('object_id', None)

        action = Action.objects(user=g.user, action_type=action_type, object_id=object_id, is_del=False).first()
        if not action:
            return Ans(-1, msg='不存在该记录')
        action.is_del = True
        action.save()
        return Ans(0)
