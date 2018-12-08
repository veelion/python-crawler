#!/usr/bin/env python3
# Author: veelion


import re
import pickle
import json
import base64
import binascii
import rsa
import requests
import urllib
import time
import traceback



class WeiboLogin:
    user_agent = (
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11'
    )

    def __init__(self, username, password, cookies_tosave='weibo.cookies'):
        self.weibo_user = username
        self.weibo_password = password
        self.cookies_tosave = cookies_tosave
        self.session = requests.session()
        self.session.headers['User-Agent'] = self.user_agent

    def encrypt_user(self, username):
        user = urllib.parse.quote(username)
        su = base64.b64encode(user.encode())
        return su

    def encrypt_passwd(self, passwd, pubkey, servertime, nonce):
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
        passwd = rsa.encrypt(message.encode('utf-8'), key)
        return binascii.b2a_hex(passwd)

    def prelogin(self):
        preloginTimeStart = int(time.time()*1000)
        url = ('https://login.sina.com.cn/sso/prelogin.php?'
               'entry=weibo&callback=sinaSSOController.preloginCallBack&'
               'su=&rsakt=mod&client=ssologin.js(v1.4.19)&'
               '_=%s') % preloginTimeStart
        resp = self.session.get(url)
        pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)
        pre_login = json.loads(pre_login_str)
        pre_login['preloginTimeStart'] = preloginTimeStart
        print ('pre_login 1:', pre_login)
        return pre_login

    def get_prelt(self, pre_login):
        prelt = int(time.time() * 1000) - pre_login['preloginTimeStart'] - pre_login['exectime']
        return prelt

    def login(self):
        # step-1. prelogin
        pre_login = self.prelogin()
        su = self.encrypt_user(self.weibo_user)
        sp = self.encrypt_passwd(
            self.weibo_password,
            pre_login['pubkey'],
            pre_login['servertime'],
            pre_login['nonce']
        )
        prelt = self.get_prelt(pre_login)

        data = {
            'entry': 'weibo',
            'gateway': 1,
            'from': '',
            'savestate': 7,
            'qrcode_flag': 'false',
            'userticket': 1,
            'pagerefer': '',
            'vsnf': 1,
            'su': su,
            'service': 'miniblog',
            'servertime': pre_login['servertime'],
            'nonce': pre_login['nonce'],
            'vsnf': 1,
            'pwencode': 'rsa2',
            'sp': sp,
            'rsakv' : pre_login['rsakv'],
            'encoding': 'UTF-8',
            'prelt': prelt,
            'sr': "1280*800",
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.'
                   'sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }

        # step-2 login POST
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        resp = self.session.post(login_url, data=data)
        print(resp.headers)
        print(resp.content)
        print('Step-2 response:', resp.text)

        # step-3 follow redirect
        redirect_url = re.findall(r'location\.replace\("(.*?)"', resp.text)[0]
        print('Step-3 to redirect:', redirect_url)
        resp = self.session.get(redirect_url)
        print('Step-3 response:', resp.text)

        # step-4 process step-3's response
        arrURL = re.findall(r'"arrURL":(.*?)\}', resp.text)[0]
        arrURL = json.loads(arrURL)
        print('CrossDomainUrl:', arrURL)
        for url in arrURL:
            print('set CrossDomainUrl:', url)
            resp_cross = self.session.get(url)
            print(resp_cross.text)
        redirect_url = re.findall(r'location\.replace\(\'(.*?)\'', resp.text)[0]
        print('Step-4 redirect_url:', redirect_url)
        resp = self.session.get(redirect_url)
        print(resp.text)
        with open(self.cookies_tosave, 'wb') as f:
            pickle.dump(self.session.cookies, f)
        return True

    def fetch(self, url):
        try:
            resp = self.session.get(url, timeout=10)
            return resp
        except:
            traceback.print_exc()
            return None

if __name__ == '__main__':
    weibo_user = 'your-weibo-username'
    weibo_password = 'your-weibo-password'
    wb = WeiboLogin(weibo_user, weibo_password)
    wb.login()
    r = wb.fetch('https://weibo.com/')
    print(r.encoding)
    print(len(r.text))
