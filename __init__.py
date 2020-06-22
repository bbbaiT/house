from flask import Flask
from flask_restful import Api
from config.config import mdb_config
from db_init import db, cache
from api import all_api


def register_api(api):
    # 注册api接口
    for _ in all_api:
        api.add_resource(_['view'], '/api'+_['api'], '/api'+_['api'] + '/', endpoint=_['endpoint'])


def register_db(app):
    # 注册数据库
    db.init_app(app)
    cache.init_app(app)


app = Flask(__name__)

app.config['DEBUG'] = True

app.secret_key = 'session_sign_key'

app.config['MONGODB_SETTINGS'] = {
    'db': mdb_config['db'],
    'host': 'mongodb://{}:{}@{}:{}/{}?authSource=admin'.format(mdb_config['username'], mdb_config['password'], mdb_config['host'],  mdb_config['port'], mdb_config['db'])
}


api = Api(app)
register_db(app)
register_api(api)

