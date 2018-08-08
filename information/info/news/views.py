# -*- coding: utf-8 -*-
# @File  : views.py
# @Author: jiawen
# @time: 18-8-1 下午5:41
from flask import g, jsonify
from flask import request

from info import db
from info.models import News, Comment,CommentLike, User
from info.utils.response_code import RET
from . import news_blue
from flask import render_template
from info.utils.common import user_login_data


@news_blue.route("/followed_user", methods=["GET", "POST"])
@user_login_data
def followed_user():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="请登录")
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    other = User.query.get(user_id)

    if action == "follow":
        if other not in user.followed:
            user.followed.append(other)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg="已经关注了该用户")
    else:
        if other in user.followed:
            user.followed.remove(other)
        else:
            return jsonify(errno=RET.PARAMERR,errmsg="没有在我关注的人列表当中")

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="ok")


@news_blue.route("/comment_like", methods=["GET", "POST"])
@user_login_data
def comment_like():
    """评论点赞"""
    """
    1.所有的点赞操作都是基于评论的,所以需要有评论id
    2.所有的点赞操作都是基于用户行为,所有用户必须登陆,所以需要有评论id
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="请登录")
    comment_id = request.json.get("comment_id")
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    """
    1.需要根据评论id查询出来评论,是因为点赞的所有操作是基于评论的
    2.点赞操作需要基于当前的新闻,所以需要查询出新闻
    """

    comment = Comment.query.get(comment_id)

    if action == "add":
        # 如果是add操作,说明想进行点赞
        # 如果之前没有点赞,那么点击一下就可以进行点赞,如果之前已经点赞了,那么就不能再进行点赞了
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id).first()
        # 判断查询出来的点赞是否有值,只有当点赞没有值的时候,才能进行点赞
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1
    else:
        # 就取消点赞
        # 如果是add操作,说明想进行带你赞
        # 如果之前没有点赞,那么点击一下就可以进行点赞,如果之前已经点赞了,那么就不能再点赞了
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id).first()
        if comment_like:
            db.session.delete(comment_like)
            comment.like_count -= 1

    db.session.commit()
    return jsonify(errno = RET.OK, errmsg ="点赞成功")


@news_blue.route("/news_comment", methods=["GET","POST"])
@user_login_data
def news_comment():
    """新闻评论"""

    # 新闻评论是一个用户行为,所以需要用户必须登陆,判断user必须有值
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="请登陆")
    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    news = News.query.get(news_id)

    # 新闻评论实际上就是把评论内容提交到数据库
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_str

    # 因为不是所有的评论都有父评论,所以在赋值的时候,需要判断
    if parent_id:
        comment.parent_id = parent_id
    # 评论是第一次进行提交,所以需要进行add操作
    db.session.add(comment)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg= "评论成功", data = comment.to_dict())


@news_blue.route("/news_collect", methods=["GET", "POST"])
@user_login_data
def news_collect():
    """新闻收藏"""

    # 因为需要收藏新闻,所以需要把新闻id传递过来.不然不清楚要收藏哪条新闻
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    news = News.query.get(news_id)
    user = g.user
    # 因为收藏新闻的是用户行为,所以必须得判断当前用户是否已经登陆,只有登陆才可以收藏新闻
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    if action == "collect":
        # 说明是想收藏新闻
        user.collection_news.append(news)
    else:
        # 说明想取消收藏
        user.collection_news.remove(news)

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="收藏成功")


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """获取到右边的热门点击新闻"""
    user = g.user
    news_model = News.query.order_by(News.clicks.desc()).limit(10)
    news_list = []
    for new_mode in news_model:
        news_list.append(new_mode.to_dict())
    # 根据id查询出具体表示哪条新闻
    news = News.query.get(news_id)

    """
    新闻收藏:
    1.通过一个变量进行控制是否已经收藏,is_collected = true:已经收藏 is_collected = false:说明没有收藏
    2.如果需要收藏新闻,那么收藏新闻是一个用户的动作,必须要用户登陆才可以收藏,如果user有值的话,就说明已经登陆
    3.判断当前是否有这条新闻,如果有新闻,才能收藏,都没有新闻,肯定就没有办法收藏
    4.判断当前的这条新闻是否在收藏的新闻列表当中,如果在说明当前新闻已经被收藏,如果新闻被收藏,那么我们就可ui是is_collected = True
    """

    # 如果是第一次进来,那么肯定是没有收藏,所以这个值默认就是false
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True

    """
    查询新闻评论的列表:
    1.首先获取新闻评论,那么需要根据新闻id进行查询出来所有的新闻
    2.根据评论的时间,进行倒序
    """

    comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    comments_list = []
    commentLike_list = []
    comment_like_list = []
    comment_like_ids = []
    if user:
        # 获取所有的点赞的评论
        commentLike_list = CommentLike.query.filter(CommentLike.user_id == user.id).all()
        # 取出所有的点赞id
        comment_like_ids = [comment_like.comment_id for comment_like in commentLike_list]

    for comment in comments:
        # 取出评论的字典
        comment_dict = comment.to_dict()
        # 因为第一次进来,肯定所有的评论都没有点赞,所以默认值是false
        comment_dict["is_like"] = False
        if comment.id in comment_like_ids:
            comment_dict["is_like"] = True
        comments_list.append(comment_dict)

    # 表示我关注了哪些人,默认情况下,第一次进来,我谁都没有有关注,所以需要设置成false
    is_followed = False

    # 如果我想关注别人的话,那么必须有新闻作者
    # 如果有作者就可以关注,所以必须有作者,因为是我需要关注这个作者,所以用户必须登陆
    if news.user and user:
        if news.user in user.followed:
            # 如果当前新闻的作者在我关注的人列表里面,说明我就关注了这个新闻作者,那么就可以is_followed =True
            is_followed = True

    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list": news_list,
        "is_collected": is_collected,
        "news":news.to_dict(),
        "comments":comments_list,
        "is_followed": is_followed
    }
    return render_template('news/detail.html', data=data)
