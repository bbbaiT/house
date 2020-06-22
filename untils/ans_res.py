# -*- coding: utf-8 -*-
from flask import jsonify


def Ans(code, msg='', data={}, **kwargs):
    data = {
        "status": code,
        "msg": msg,
        "data": data
    }
    if kwargs:
        for key in kwargs.keys():
            data.update({
                key: kwargs[key]
            })
    return jsonify(data)

