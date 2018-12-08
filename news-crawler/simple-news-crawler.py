#!/usr/bin/env python3
# Author: veelion


import re
import requests
import tldextract


def save_to_db(url, html):
    print('%s : %s' % (url, len(html)))


def crawl():
    # 1. download baidu news
    hub_url = 'http://news.baidu.com/'
    html = requests.get(hub_url).text

    # 2. extract news links
    ## 2.1 extract all links with 'href'
    links = re.findall(r'href=[\'"]?(.*?)[\'"\s]', html)
    print('find links:', len(links))
    news_links = []
    ## 2.2 filter non-news link
    for link in links:
        if not link.startswith('http'):
            continue
        tld = tldextract.extract(link)
        if tld.domain == 'baidu':
            continue
        news_links.append(link)

    print('find news links:', len(news_links))
    # 3. download news and save to database
    for link in news_links:
        html = requests.get(link).text
        save_to_db(link, html)
    print('works done!')


if __name__ == '__main__':
    crawl()
