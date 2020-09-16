import hashlib
from operator import or_

from flask import Blueprint, render_template, request, redirect, url_for

from apps.user.models import User
from ext import db
#创建蓝图
user_bp = Blueprint('user',__name__)

#用户注册模块
@user_bp.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        if password==repassword:
            # 注册用户
            user=User()
            user.username=username
            user.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            user.phone = phone
            # 添加
            # 3.将user对象添加到session中（类似缓存）
            db.session.add(user)
            # 4.提交数据
            db.session.commit()
            return redirect(url_for('user.user_center'))
    return render_template('user/register.html')

#用户中心模块
@user_bp.route('/')
def center():
    #查询数据库中的数据
    users=User.query.filter(User.isdelete==False).all()
    return render_template('user/center.html',users=users)

#用户登录模块
@user_bp.route('/login',methods=['GET','POST'])
def login():
     if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         #查找数据库
         new_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
         user_list = User.query.filter_by(username=username)
         for u in user_list:
             if u.password == new_password:
                 return '登录成功'
             else:
                 return render_template('user/login.html',msg='用户名或密码有误')
         return 'testing'
     return render_template('user/login.html')

#查询搜索模块
@user_bp.route('/search')
def search():
    keyword = request.args.get('search')
    user_list = User.query.filter(or_(User.username.contains(keyword),User.phone.contains(keyword))).all()
    return render_template('user/center.html',users=user_list)

#删除模块
@user_bp.route('/delete')
def delete():

    #获取用户的ID
    id  = request.args.get('id')
    # 1.逻辑删除
    # #获取该ID的用户
    # user=User.query.get(id)
    # #逻辑删除
    # user.isdelete=True
    # #提交
    # db.session.commit()
    # # 2.物理删除
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('user.center'))

#用户信息更新
@user_bp.route('/update',methods=['GET','POST'])
def update():
    if request.method=='POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        id = request.form.get('id')
        #找用户
        user=User.query.get(id)
        #改用户信息
        user.username=username
        user.phone=phone
        #提交
        db.session.commit()
        return redirect('user.center')
    else:
        id = request.args.get('id')
        user=User.query.get(id)
    return render_template('user/update.html',user=user)

