# -*- coding: utf-8 -*-
# @File  : views.py
# @Author: jiawen
# @time: 18-8-4 下午2:53
from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import request
from flask import session

from info.utils.image_storage import storage

from info import constants
from info import db
from info.models import Category, News, User
from info.utils.response_code import RET
from . import user_blue
from flask import render_template
from info.utils.common import user_login_data


@user_blue.route("/other_news_list")
def other_news_list():
    p = request.args.get("p", 1)
    user_id = request.args.get("user_id")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.PARAMERR, errmsg="参数错误")

    user = User.query.get(user_id)
    paginate = News.query.filter(News.user_id == user.id).paginate(p, 10, False)
    news_li = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {
        "news_list": news_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }
    return jsonify(errno = RET.OK, errmsg="ok", data = data)


@user_blue.route("/other_info")
@user_login_data
def other_info():
    user = g.user
    if not user:
        return jsonify(errno = RET.SERVERERR, errmsg="请登陆")
    other_id = request.args.get("id")
    other = User.query.get(other_id)

    is_followed = False
    if other and user:
        if other in user.followed:
            is_followed = True

    data = {
        "user_info": user.to_dict(),
        "other_info": other.to_dict(),
        "is_followed": is_followed
    }
    return render_template("news/other.html", data = data)


"""
我的关注
"""
@user_blue.route("/follow")
@user_login_data
def follow():
    user = g.user
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = user.followed.paginate(page, 4 , False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    other_list = []
    for item in items:
        other_list.append(item.to_dict())
    data = {
        "users":other_list,
        "current_pae": current_page,
        "total_page": total_page
    }
    return render_template("news/user_follow.html", data = data)


@user_blue.route("/news_list")
@user_login_data
def news_list():
    user = g.user
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = News.query.filter(News.user_id == user.id).paginate(page, 2, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.page

    items_list = []
    for item in items:
        items_list.append(item.to_review_dict())

    data = {
        "news_list": items_list,
        "current_page":current_page,
        "total_page":total_page
    }
    return render_template("news/user_news_list.html", data = data)


@user_blue.route("/news_release", methods=["GET", "POST"])
@user_login_data
def news_release():
    user = g.user
    if request.method == "GET":
        categorys = Category.query.all()
        category_list = []
        for category in categorys:
            category_list.append(category.to_dict())
        category_list.pop(0)
        data = {
                "categories":category_list
            }
        return render_template("news/user_news_release.html", data = data)
    # 获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image").read()
    category_id = request.form.get("category_id")
    # 判断是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    key = storage(index_image)

    news = News()
    news.title = title
    news.source = source
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1

    db.session.add(news)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="发布成功")


@user_blue.route("/collection")
@user_login_data
def collection():
    user = g.user
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = user.collection_news.paginate(page, 2, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    items_list = []
    for item in items:
        items_list.append(item.to_review_dict())

    data = {
        "collections": items_list,
        "current_page":current_page,
        "total_page":total_page
    }
    return render_template("news/user_collection.html", data = data)


@user_blue.route("/pass_info",methods=["GET", "POST"])
@user_login_data
def pass_info():
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_pass_info.html", data = data)
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    user.password = new_password
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="密码修改成功")


@user_blue.route("/pic_info", methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_pic_info.html", data = data)
    # 获取到用户传递过来的头像参数
    avatar_url = request.files.get("avatar").read()
    # 在传递到七牛之后,七牛会返回一个key,返回的目的是帮助我们取访问图片
    key = storage(avatar_url)

    user.avatar_url = key
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="头像设置成功", data = {"avatar_url": constants.QINIU_DOMIN_PREFIX})


@user_blue.route("/base_info", methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":

        data = {
            "user_info": user.to_dict() if user else None,
        }
        return render_template("news/user_base_info.html", data = data)
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的参数")

    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="ok")


@user_blue.route("/info")
@user_login_data
def get_use_info():
    user = g.user
    if not user:
        return redirect("/")
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("news/user.html", data = data)
