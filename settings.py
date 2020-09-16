import os


class Config:
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:Ta#123456@192.168.74.135:3306/flask05'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_ECHO=True
    SECRET_KEY = 'hjsjhfsakfs541sfs51s1a5d4sa1cJJJJJkslklxo'

    # 项目路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静态文件夹的路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
    # 头像的上传目录
    UPLOAD_ICON_DIR = os.path.join(STATIC_DIR, 'upload\icon')
    # 相册的上传目录
    UPLOAD_PHOTO_DIR = os.path.join(STATIC_DIR, 'upload\photo')
class DevelopmentConfig(Config):
    ENV='development'

class ProductionConfig(Config):
    ENV='production'
    BEBUG=False
# if __name__ =='__main__':
#     print(Config.BASE_DIR)
#     print(os.path.abspath(__file__))
#     print(Config.STATIC_DIR)
#     print(Config.UPLOAD_ICON_DIR)
#  ALTER USER 'root'@'localhost' IDENTIFIED BY 'Ta#123456';
# ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Ta#123456';
# GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'Ta#123456' WITH GRANT OPTION;