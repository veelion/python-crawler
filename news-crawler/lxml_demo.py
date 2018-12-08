#!/usr/bin/env python3
# Author: veelion


import re
import requests
import lxml.html
from pprint import pprint


def parse(li):
    item = {}
    # class="thumb"的div有两个<a>，第一个是类别链接，第二个是文章链接
    thumb = li.xpath('./div[@class="thumb"]/a')
    item['cat'] = thumb[0].text
    item['link'] = thumb[1].get('href')

    # 获取title
    el_title = li.xpath('.//h2[@class="info-tit"]/a')[0]
    item['title'] = el_title.text

    el_info = li.xpath('.//div[@class="info-item"]/span')
    for span in el_info:
        attr = span.get('class')
        if attr == 'author':
            item['author'] = span.text_content()
        elif attr == 'time':
            item['time'] = span.text_content()
        elif attr == 'view':
            digit = re.findall(r'\d+', span.text_content())[0]
            item['view_count'] = int(digit)
        elif attr == 'cmt':
            digit = re.findall(r'\d+', span.text_content())[0]
            item['cmt_count'] = int(digit)
    return item


def main():
    url = 'https://www.yuanrenxue.com/'
    headers = {'User-Agent': 'Firefox'}
    resp = requests.get(url, headers=headers)
    html = resp.content.decode('utf8')
    doc = lxml.html.fromstring(html)
    xp = '//ul[@id="postlist"]/li'
    lis = doc.xpath(xp)
    print('lis:', len(lis))

    articles = [parse(li) for li in lis]
    print('articles:', len(articles))
    pprint(articles[0])


if __name__ == '__main__':
    main()

