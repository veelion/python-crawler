#!/usr/bin/env python3
# encoding: UTF-8
# author: veelion
# file: bee_client.py

import re
import cchardet
import traceback
import time
import json
import asyncio
import urllib.parse as urlparse
import aiohttp
import uvloop


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())



p_tag_a = re.compile(
    r'<a[^>]*?href=[\'"]?([^> \'"]+)[^>]*?>(.*?)</a>',
    re.I|re.S|re.M)


def extract_links_re(url, html):
    newlinks = set()
    aa = p_tag_a.findall(html)
    for a in aa:
        link = a[0].strip()
        if not link:
            continue
        link = urlparse.urljoin(url, link)
        if not link.startswith('http'):
            continue
        newlinks.add(link)
    return newlinks



class CrawlerClient:
    def __init__(self, ):
        self._workers = 0
        self.workers_max = 10
        self.server_host = 'localhost'
        self.server_port = 8080
        self.headers = {'User-Agent': ('Mozilla/5.0 (compatible; MSIE 9.0; '
      'Windows NT 6.1; Win64; x64; Trident/5.0)')}

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def download(self, url, timeout=25):
        status_code = 900
        html = ''
        url_now = url
        try:
            async with self.session.get(url_now, headers=self.headers, timeout=timeout) as response:
                status_code = response.status
                html = await response.read()
                encoding = cchardet.detect(html)['encoding']
                html = html.decode(encoding, errors='ignore')
                url_now = str(response.url)
        except Exception as e:
            # traceback.print_exc()
            print('=== exception: ', e, type(e), str(e))
            msg = 'Failed download: {} | exception: {}, {}'.format(url, str(type(e)), str(e))
            print(msg)
        return status_code, html, url_now

    async def get_urls(self,):
        count = self.workers_max - self.queue.qsize()
        if count <= 0:
            print('no need to get urls this time')
            return None
        url = 'http://%s:%s/task?count=%s' % (
            self.server_host,
            self.server_port,
            count
        )
        try:
            async with self.session.get(url, timeout=3) as response:
                if response.status not in [200, 201]:
                    return
                jsn = await response.text()
                urls = json.loads(jsn)
                msg = ('get_urls()  to get [%s] but got[%s], @%s') % (
                    count, len(urls),
                    time.strftime('%Y-%m-%d %H:%M:%S'))
                print(msg)
                for kv in urls.items():
                    await self.queue.put(kv)
                print('queue size:', self.queue.qsize(), ', _workers:', self._workers)
        except:
            traceback.print_exc()
            return

    async def send_result(self, result):
        url = 'http://%s:%s/task' % (
            self.server_host,
            self.server_port
        )
        try:
            async with self.session.post(url, json=result, timeout=3) as response:
                return response.status
        except:
            traceback.print_exc()
            pass

    def save_html(self, url, html):
        print('saved:', url, len(html))

    def filter_good(self, urls):
        '''根据抓取目的过滤提取的URLs，只要你想要的'''
        good = []
        for url in urls:
            if url.startswith('http'):
                good.append(url)
        return good

    async def process(self, url, ishub):
        status, html, url_now = await self.download(url)
        self._workers -= 1
        print('downloaded:', url, ', html:', len(html))
        if html:
            newurls = extract_links_re(url, html)
            newurls = self.filter_good(newurls)
            self.save_html(url, html)
        else:
            newurls = []
        result = {
            'url': url,
            'url_real': url_now,
            'status': status,
            'newurls': newurls,
        }
        await self.send_result(result)

    async def loop_get_urls(self,):
        print('loop_get_urls() start')
        while 1:
            await self.get_urls()
            await asyncio.sleep(1)

    async def loop_crawl(self,):
        print('loop_crawl() start')
        asyncio.ensure_future(self.loop_get_urls())
        counter = 0
        while 1:
            item = await self.queue.get()
            url, url_level = item
            self._workers += 1
            counter += 1
            asyncio.ensure_future(self.process(url, url_level))

            if self._workers > self.workers_max:
                print('====== got workers_max, sleep 3 sec to next worker =====')
                await asyncio.sleep(3)

    def start(self):
        try:
            self.loop.run_until_complete(self.loop_crawl())
        except KeyboardInterrupt:
            print('stopped by yourself!')
            pass


def run():
    ant = CrawlerClient()
    ant.start()


if __name__ == '__main__':
    run()

