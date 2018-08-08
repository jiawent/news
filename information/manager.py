# -*- coding: utf-8 -*-
# @File  : manager.py
# @Author: jiawen
# @time: 18-7-27 下午2:33

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app,db
from info import models

# manager.py的作用是入口程序
from info.models import User

app = create_app("develop")

# 创建一个命令行对象
manager = Manager(app)
# 需要创建表
Migrate(app, db)
# 添加一个命令, 添加一个迁移命令的对象,对象的名字随意取(一般要见名知义)
manager.add_command("mysql", MigrateCommand)


@manager.option('-n', '--name', dest='name')
@manager.option('-p', '--password', dest='password')
def create_super_user(name, password):
    user = User()
    user.nick_name = name
    user.password = password
    user.mobile = name
    user.is_admin = True
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    # print(app.url_map)
    # manager.run()
    app.run(host="192.168.11.138", port=8888)