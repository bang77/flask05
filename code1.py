# -*- coding: utf-8 -*-
# flake8: noqa
import os

from qiniu import Auth, put_file, etag
import qiniu.config

from settings import Config

access_key = '5AnB0oFvAQAup72xRSE31hsqai6ro9DFOs-YqwiL'
secret_key = 'cx6owZMZhRYtSvVU8163XHoDwZ9IneZ1SLRcMm1O'
q = Auth(access_key, secret_key)
bucket_name = 'wubangfu'
key = 'my-python-logo.png'
#上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
# policy={
#  'callbackUrl':'http://your.domain.com/callback.php',
#  'callbackBody':'filename=$(fname)&filesize=$(fsize)'
#  }
token = q.upload_token(bucket_name, key, 3600)
localfile =os.path.join(Config.UPLOAD_ICON_DIR,'030.jpg')
ret, info = put_file(token, key, localfile)
print(info)
print(ret)
# assert ret['key'] == key
# assert ret['hash'] == etag(localfile)