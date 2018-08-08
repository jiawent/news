# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: jiawen
# @time: 18-8-1 下午5:40

from flask import Blueprint

news_blue = Blueprint("news", __name__, url_prefix="/news")

from . import views
