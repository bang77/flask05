import os

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apps.article.models import Article_type, Article
from apps.user.code import Yunpian
from apps.user.models import User, Photo, MessageBoard, AboutMe
from apps.user.upload import upload_qiniu, delete_qiniu
from ext import db
from settings import Config

user_bp = Blueprint('user', __name__,url_prefix='/user')
# user_bp = Blueprint('user', __name__)

required_login_list = ['/user/center',
                       '/user/change',
                       '/user/upload_photo',
                       '/user/photo_del',
                       '/user/board_del',
                       '/user/aboutme',
                       '/user/showabout',
                       '/article/publish' ,
                       '/article/detail',
                       '/article/love',
                       '/article/type_search',
                       '/article/add_comment']

@user_bp.before_app_first_request
def first_request():
    print('before_app_first_request')


# ****重点*****
@user_bp.before_app_request
def before_request1():
    # print('before_request1before_request1', request.path)
    if request.path in required_login_list:
        id = session.get('uid')
        if not id:
            return render_template('user/login.html')
        else:
            user = User.query.get(id)
            # g对象，本次请求的对象
            g.user = user


@user_bp.after_app_request
def after_request_test(response):
    response.set_cookie('a', 'bbbb', max_age=19)
    # print('after_request_test')
    return response


@user_bp.teardown_app_request
def teardown_request_test(response):
    # print('teardown_request_test')
    return response

# 自定义过滤器
@user_bp.app_template_filter('cdecode')
def content_decode(content):
    content = content.decode('utf-8')
    return content

@user_bp.app_template_filter('cdecode1')
def content_decode(content):
    content = content.decode('utf-8')
    return content
#首页
@user_bp.route('/')
def index():
    # 1。cookie获取方式
    # uid = request.cookies.get('uid', None)
    # 2。session的获取,session底层默认获取
    # 2。session的方式：
    uid = session.get('uid')
    #   # 获取文章列表
    # articles = Article.query.order_by(-Article.pdatetime).all()
    # # 获取分类列表
    # types = Article_type.query.all()
    # # 判断用户是否登录
    # if uid:
    #     g.user= User.query.get(uid)
    #     return render_template('user/index.html',user=g.user,articles=articles,types=types)
    # else:
    #     return render_template('user/index.html',articles=articles,types=types)
    page = int(request.args.get('page', 1))
    pagination = Article.query.order_by(-Article.pdatetime).paginate(page=page, per_page=10)
    # print(pagination.items)  # [<Article 4>, <Article 3>, <Article 2>]
    # print(pagination.page)  # 当前的页码数
    # print(pagination.prev_num)  # 当前页的前一个页码数
    # print(pagination.next_num)  # 当前页的后一页的页码数
    # print(pagination.has_next)  # True
    # print(pagination.has_prev)  # True
    # print(pagination.pages)  # 总共有几页
    # print(pagination.total)  # 总的记录条数
    # 获取分类列表
    types = Article_type.query.all()
    # 判断用户是否登录
    if uid:
        g.user = User.query.get(uid)
        return render_template('user/index.html', user=g.user, types=types, pagination=pagination)
    else:
        return render_template('user/index.html', types=types, pagination=pagination)



#用户注册
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if password == repassword:
            # 注册用户
            user = User()
            user.username = username
            # 使用自带的函数实现加密：generate_password_hash
            user.password = generate_password_hash(password)
            # print(password)
            user.phone = phone
            user.email = email
            # 添加并提交
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user.index'))
    return render_template('user/register.html')

#手机验证
@user_bp.route('/checkphone',methods=['GET','POST'])
def check_phone():
    phone = request.args.get('phone')
    user=User.query.filter(User.phone==phone).all()
    if len(user) > 0:
        return jsonify(code=400,msg='此号码已被注册')
    else:
        return jsonify(code=200,msg='此号码可用注册')

#用户登录
@user_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method =='POST':
        f = request.args.get('f')
        #用户名和密码
        if f=='1':
            username = request.form.get('username')
            password = request.form.get('password')
            users= User.query.filter(User.username==username).all()
            for user in users:
                flag=check_password_hash(user.password,password)
                # print(type(flag))
                if flag:
                    # 1.cookie实现机制
                    # response=redirect(url_for('user.index'))
                    # response.set_cookie('uid',str(user.id),max_age=1800)
                    # return response
                    # 2.session机制，session当成字典使用
                    session['uid']=user.id
                    return redirect(url_for('user.index'))
            else:
                return render_template('user/login.html', msg='用户名或者密码有误')
        #手机号码和验证码
        elif f=='2':
            phone = request.form.get('phone')
            code = request.form.get('code')
            # 先验证验证码
            valid_code = session.get(phone)

            if code == valid_code:
                # 查询数据库
                user = User.query.filter(User.phone == phone).first()
                # print(user)
                if user:
                    # 登录成功
                    session['uid'] = user.id
                    return redirect(url_for('user.index'))
                else:
                    return render_template('user/login.html', msg='此号码未注册')
            else:
                return render_template('user/login.html', msg='验证码有误！')

    return render_template('user/login.html')

#用户退出
@user_bp.route('/logout')
def logout():
    response=redirect(url_for('user.index'))
    # #通过response对象的delete——cookie(key),key就是要删除的cookie的key
    # response.delete_cookie('uid')
    # del session['uid']
    session.clear()
    return response

#发送短信息
@user_bp.route('/sendMsg')
def send_message():
    phone = request.args.get('phone')
    YP=Yunpian()
    code=YP.get_code()
    YP.send_code(phone,code)
    session[phone] = code
    return jsonify(code=200, msg='短信发送成功！')

#用户中心
@user_bp.route('/center')
def user_center():
    types = Article_type.query.all()
    photos = Photo.query.filter(Photo.user_id == g.user.id).all()
    return render_template('user/center.html', user = g.user,types = types,photos = photos)

# 图片的扩展名
ALLOWED_EXTENSIONS = ['jpg', 'png', 'gif', 'bmp']


# 用户信息修改
@user_bp.route('/change', methods=['GET', 'POST'])
def user_change():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 只要有图片，获取方式必须使用request.files.get(name)
        icon = request.files.get('icon')
        # 属性： filename 用户获取文件的名字
        # 方法:  save(保存路径)
        icon_name = icon.filename  # 1440w.jpg
        suffix = icon_name.rsplit('.')[-1]
        if suffix in ALLOWED_EXTENSIONS:
            icon_name = secure_filename(icon_name)  # 保证文件名是符合python的命名规则
            file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
            icon.save(file_path)
            # 保存成功
            user = g.user
            user.username = username
            user.phone = phone
            user.email = email
            path = 'upload/icon/'
            user.icon = os.path.join(path, icon_name)
            db.session.commit()
            print(user.icon)
            return redirect(url_for('user.user_center'))
        else:
            return render_template('user/center.html', user=g.user, msg='必须是扩展名是：jpg,png,gif,bmp格式')

    return render_template('user/center.html', user=g.user)

# 上传相册
@user_bp.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    # 获取上传的内容
    photo = request.files.get('photo')  # FileStorage
    # photo.filename,photo.save(path)
    # 工具模块中封装方法
    ret, info = upload_qiniu(photo)
    if info.status_code == 200:
        photo = Photo()
        photo.photo_name = ret['key']
        photo.user_id = g.user.id
        db.session.add(photo)
        db.session.commit()
        return redirect(url_for('user.user_center'))
    else:
        return render_template('500.html', err_msg='上传失败！')
#删除图片
@user_bp.route('/photo_del')
def photo_del():
    pid =request.args.get('pid')
    photo = Photo.query.get(pid)
    filename=photo.photo_name
    info = delete_qiniu(filename)
    # print('########',info.status_code)
    if info.status_code == 200:
        db.session.delete(photo)
        db.session.commit()
        return redirect(url_for('user.user_center'))
    else:

        return render_template('500.html', err_msg='删除相册图片失败！')

# 我的相册
@user_bp.route('/myphoto')
def myphoto():
    # 如果不转成整型，默认是str类型
    page = int(request.args.get('page', 1))
    # 分页操作
    # photos是一个pagination类型
    photos = Photo.query.paginate(page=page, per_page=3)
    #
    user_id = session.get('uid', None)
    g.user = None
    if user_id:
        g.user = User.query.get(user_id)
    return render_template('user/myphoto.html', photos=photos, user=g.user)

# 关于用户介绍添加
@user_bp.route('/aboutme', methods=['GET', 'POST'])
def about_me():
    if request.method == 'POST':
        content = request.form.get('content')
        # print(content)
        # 添加信息
        # try:
        aboutme = AboutMe()
        aboutme.content = content.encode('utf-8')
        aboutme.user_id = g.user.id
        db.session.add(aboutme)
        db.session.commit()
# except Exception as err:
#     return redirect(url_for('user.user_center'))
# else:
    return render_template('user/aboutme.html', user=g.user)

# 展示关于我
@user_bp.route('/showabout')
def show_about():
    return render_template('user/aboutme.html', user=g.user)

# 留言板
@user_bp.route('/board', methods=['GET', 'POST'])
def show_board():
    # 获取登录用户信息
    uid = session.get('uid', None)
    g.user = None
    if uid:
        g.user = User.query.get(uid)

    # 查询所有的留言内容
    page = int(request.args.get('page', 1))
    boards = MessageBoard.query.order_by(-MessageBoard.mdatetime).paginate(page=page, per_page=5)
    # 判断请求方式
    if request.method == 'POST':
        content = request.form.get('board')
        print('======》', content)
        # 添加留言
        msg_board = MessageBoard()
        msg_board.content = content
        if uid:
            msg_board.user_id = uid
        db.session.add(msg_board)
        db.session.commit()
        return redirect(url_for('user.show_board'))
    return render_template('user/board.html', user=g.user, boards=boards)


# 留言删除
@user_bp.route('/board_del')
def delete_board():
    bid = request.args.get('bid')
    if bid:
        msgboard = MessageBoard.query.get(bid)
        db.session.delete(msgboard)
        db.session.commit()
        return render_template('del.html', ok_msg='留言删除成功！')

# 出错页面
@user_bp.route('/error')
def test_error():
    # print(request.headers)
    # print(request.headers.get('Accept-Encoding'))
    referer = request.headers.get('Referer', None)
    return render_template('500.html', err_msg='有误', referer=referer)
