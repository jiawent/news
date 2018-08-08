# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: jiawen
# @time: 18-7-27 下午3:31
from flask import Blueprint

# 创建蓝图对象
# index_blue:蓝图对象的名字
# 第一个参数表示name:name的作用是用来调用函数,name可以随意取
# 第三个参数表示前缀,前缀用来表示请求的url地址前面加上一个标记,告诉大家当前这个地方表示的是什么模块
index_blue = Blueprint("index", __name__)

from . import views