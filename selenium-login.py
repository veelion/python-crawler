#!/usr/bin/env python
# Author: veelion

import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def save_cookies(cookies, file_to_save):
    with open(file_to_save, 'wb') as f:
        pickle.dump(cookies, f)


def login_auto(login_url, username, password,
               username_xpath, password_xpath,
               submit_xpath, cookies_file, browser=None):
    if browser is None:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')
        browser = webdriver.Chrome(chrome_options=options)
    browser.maximize_window()
    browser.get(login_url)
    time.sleep(9) # 等登录加载完成
    browser.find_element_by_xpath(username_xpath).send_keys(username)
    browser.find_element_by_xpath(password_xpath).send_keys(password)
    browser.find_element_by_xpath(submit_xpath).send_keys(Keys.ENTER)
    time.sleep(9) # 等登录加载完成
    cookies = browser.get_cookies()
    print(cookies)
    save_cookies(cookies, cookies_file)


def login_manually(login_url, cookies_file, browser=None):
    # 既然是手动，这里就不自动填写用户名和密码了
    if browser is None:
        browser = webdriver.Chrome()
    browser.get(login_url)
    time.sleep(30) # 给自己多了点时间输入用户名、密码、验证码
    cookies = browser.get_cookies()
    print(cookies)
    save_cookies(cookies, cookies_file)


def load_to_browser(cookies_file, browser=None):
    with open(cookies_file, 'rb') as f:
        cookies = pickle.load(f)
    if browser is None:
        browser = webdriver.Chrome()
    for cookie in cookies:
        browser.add_cookie(cookie)
    return browser


def load_to_requests(cookies_file, session=None):
    with open(cookies_file, 'rb') as f:
        cookies = pickle.load(f)
    if session is None:
        session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])


if __name__ == '__main__':
    from sys import argv
    if argv[1] == 'manually':
        # login_url = 'https://passport.bilibili.com/login'
        login_url = 'https://www.zhihu.com/signin'
        login_manually(login_url, 'z-.cookies')
    elif argv[1] == 'auto':
        login_url = 'https://weibo.com/'
        username_xpath = '//input[@id="loginname"]'
        password_xpath = '//input[@name="password"]'
        submit_xpath = '//a[@action-type="btn_submit"]'
        username = 'your-username'
        password = 'your-password'
        login_auto(login_url, username, password, username_xpath, password_xpath, submit_xpath, 'z-weibo.cookies')
    else:
        print('invalid option')

