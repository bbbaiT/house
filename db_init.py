# -*- coding: utf-8 -*-
from flask_mongoengine import MongoEngine
from flask_caching import Cache
from config.config import cache_config

db = MongoEngine()

cache = Cache(config=cache_config, with_jinja2_ext=False)
