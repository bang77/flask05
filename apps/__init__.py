from flask import Flask
import settings
from apps.article.views import article_bp
from apps.user.views import user_bp
from ext import db, bootstrap, cache
config={
    'CACHE_TYPE':'redis',
    'CACHE_REDIS_HOST':'127.0.0.1',
    'CACHE_REDIS_PORT':6379
}

def create_app():
    app=Flask(__name__,template_folder='../templates',static_folder='../static')
    #环境的设置
    app.config.from_object(settings.DevelopmentConfig)
    #初始化db
    db.init_app(app)
    #初始化缓存文件
    cache.init_app(app=app, config=config)
    #初始化bootstrap
    bootstrap.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(article_bp)
    return app