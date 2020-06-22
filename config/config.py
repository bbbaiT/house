# -*- coding: utf-8 -*-
host = ''

mdb_config = {
    'username': "root",
    'password': "",
    'host': host,
    'port': 27017,
    'db': "house",
}

rdb_config = {
    'host': host,
    "port": 6379,
    'password': "",
    "db": 0,
}

cache_config = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": rdb_config['host'],
    "CACHE_REDIS_PORT": rdb_config['port'],
    "CACHE_REDIS_PASSWORD": rdb_config['password'],
    "CACHE_REDIS_DB": rdb_config['db'],
    "CACHE_DEFAULT_TIMEOUT": 600,
    "CACHE_KEY_PREFIX": 'house_',
}


SECRET_KEY = 'SignPassword'
EXPIRATION = 60*60*24
