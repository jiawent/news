# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: jiawen
# @time: 18-7-29 下午4:35
from flask import Blueprint

passport_blue = Blueprint("passport", __name__, url_prefix="/passport")

from . import views
