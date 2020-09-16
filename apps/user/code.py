import requests
import random
import json

class Yunpian():
    def __init__(self):
        self.apikey ='535805b385729c478b8ec252da6b3c7f'
        self.url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def get_code(self):
        li = random.sample([i for i in range(10)],4)
        code = ''
        for i in li:
            code += str(i)
        return code
    def send_code(self,phone,code):
        headers = {
            'Accept': 'application/json;charset=utf-8;',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
        }
        data = {
            'apikey':self.apikey,
            'mobile':phone,
            'text':'【邱翠云】您的验证码是%s。如非本人操作，请忽略本短信'%code
        }
        re_data = requests.post(url=self.url,data=data,headers=headers)
        return json.loads(re_data.text)
# if __name__ == "__main__":
#     apikey = '535805b385729c478b8ec252da6b3c7f'
#     url = 'https://sms.yunpian.com/v2/sms/single_send.json'
#     phone='13877788214'
#     y=Yunpian()
#     code=y.get_code()
#     p=y.send_code(phone,code)
#     print(p)
