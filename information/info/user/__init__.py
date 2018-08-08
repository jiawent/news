# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: jiawen
# @time: 18-8-4 下午2:52
from flask import Blueprint

user_blue = Blueprint("profile", __name__, url_prefix="/user")

from . import views
