# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: jiawen
# @time: 18-8-4 下午10:16
from flask import Blueprint
from flask import redirect
from flask import request
from flask import session

admin_blue = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


# 检查是否是管理员
# 在用户登陆之前,判断一下,当前登陆的用户到底是不是管理员,如果不是管理员就不能进入到后台的index界面
@admin_blue.before_request
def check_admin():
    # 获取到session里面的数据
    is_admin = session.get("is_admin",None)
    # 如果不是管理员,就不能进入到后台系统,并且,也不能让你请求后台的url地址,admin/login
    if not is_admin and not request.url.endswith("/admin/login"):
        return redirect("/")
