import os

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apps.article.models import Article_type, Comment
from apps.user.models import User
from apps.user.upload import user_type
from settings import Config

from apps.article.models import Article
from ext import db

article_bp=Blueprint('article',__name__,url_prefix='/article')

# 自定义过滤器

@article_bp.app_template_filter('cdecode')
def content_decode(content):
    # content = content
    content = content.decode('utf-8')
    return content

@article_bp.route('/publish',methods=['POST','GET'])
def publish_article():
    if request.method=='POST':
        title=request.form.get('title')
        type_id=request.form.get('type')
        content=request.form.get('content')
        # print(title)
        # print(type_id)
        # print(content)
        # print(g.user.id)
        # 添加文章
        article = Article()
        article.title=title
        article.content = content
        article.type_id=type_id
        #
        article.user_id=g.user.id
        #
        db.session.add(article)
        db.session.commit()
        # return '发表成功！'
        return redirect(url_for('user.index'))

# 文章详情
@article_bp.route('/detail')
def article_detail():
    # 获取文章对象通过id
    article_id = request.args.get('aid')
    article = Article.query.get(article_id)
    # 获取文章分类

    # 点击量变化
    article.click_num += 1
    db.session.commit()
    # 获取用户和文章类型给导航使用
    user, types = user_type()
    # 单独查询评论
    # types = Article_type.query.all()
    # # 登录用户
    # g.user = None
    # user_id = session.get('uid', None)
    # if user_id:
    #     g.user = User.query.get(user_id)
    page = int(request.args.get('page', 1))
    comments = Comment.query.filter(Comment.article_id == article_id).order_by(-Comment.cdatetime).paginate(page=page, per_page=5)

    return render_template('article/detail.html', article=article, user=user,types=types,comments=comments)


# 点赞
@article_bp.route('/love')
def article_love():
    article_id = request.args.get('aid')
    tag = request.args.get('tag')

    article = Article.query.get(article_id)
    if tag == '1':
        article.love_num -= 1
    else:
        article.love_num += 1
    db.session.commit()
    return jsonify(num=article.love_num)


# 发表文章评论
@article_bp.route('/add_comment', methods=['GET', 'POST'])
def article_comment():
    if request.method == 'POST':
        comment_content = request.form.get('comment')
        user_id = g.user.id
        # user_id = session.get('uid', None)
        # user = User.query.get(user_id)
        article_id = request.form.get('aid')
        # 评论模型
        comment = Comment()
        comment.comment = comment_content
        comment.user_id = user_id
        comment.article_id = article_id
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('article.article_detail') + "?aid=" + article_id)
    return redirect(url_for('user.index'))


# 文章分类检索
@article_bp.route('/type_search')
def type_search():
    # 获取用户和文章类型给导航使用
    g.user, types = user_type()

    # tid的获取
    tid = request.args.get('tid', 1)
    page = int(request.args.get('page', 1))

    # 分页器？？？？
    # pagination对象
    articles = Article.query.filter(Article.type_id == tid).paginate(page=page, per_page=3)

    params = {
        'user': g.user,
        'types': types,
        'articles': articles,
        'tid': tid,
    }

    return render_template('article/article_type.html', **params)