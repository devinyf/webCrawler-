import requests
from lxml import etree
import time
import json
from queue import Queue
import threading


class Qiushi(object):
    def __init__(self):
        self.base_url = 'https://www.qiushibaike.com/8hr/page/%s/'
        # self.url_list = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
        }
        # 构建三个队列
        self.url_queue = Queue()
        self.response_queue = Queue()
        self.data_queue = Queue()
        self.file = open('day03/qiushi.json', 'w', encoding='utf8')

    def generate_url(self):
        # self.url_list = [self.base_url % (i) for i in range(1, 14)]
        # print(self.url_list)
        print('开始生成url')
        for i in range(1, 14):
            url = self.base_url % i
            self.url_queue.put(url)

    def get_page(self, url):
        # response = requests.get(url, headers=self.headers)
        # return response.content
        while True:
            url = self.url_queue.get()
            print('开始获取%s的响应' % url)
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                self.url_queue.put(url)
            else:
                self.response_queue.put(response.content)
            self.url_queue.task_done()

    def parse_data(self):
        while True:
            print('开始解析数据')
            data = self.response_queue.get()
            html = etree.HTML(data)
            node_list = html.xpath('//div[@id="content-left"]/div')
            # print(len(node_list))

            data_list = []
            for node in node_list:
                temp = {}
                try:
                    temp['user'] = node.xpath(
                        './div[1]/a[2]/h2/text()')[0].strip()
                    temp['zone_link'] = 'https://www.qiushibaike.com/' + \
                        node.xpath('./div[1]/a[2]/@href')[0]
                    temp['age'] = node.xpath('./div[1]/div/text()')[0]
                    temp['gender'] = node.xpath(
                        './div[1]/div/@class')[0].split(' ')[-1].replace('Icon', '')
                except:
                    temp['user'] = '匿名用户'
                    temp['zone_link'] = None
                    temp['age'] = None
                    temp['gender'] = None

                temp['content'] = ''.join(node.xpath(
                    './a[1]/div/span[1]/text()')).strip()
                # print(temp)
                data_list.append(temp)

            self.data_queue.put(data_list)
            self.data_queue.task_done()
            # return data_list

    def save_data(self):
        while True:
            print('开始保存数据')
            data_list = self.data_queue.get()
            for data in data_list:
                str_data = json.dumps(data, ensure_ascii=False) + ',\n'
                self.file.write(str_data)
            self.data_queue.task_done()

    def __del__(self):
        self.file.close()

    def run(self):
        # for url in self.url_list:
        #     data = self.get_page(url)
        #     data_list = self.parse_data(data)
        #     time.sleep(1)
        #     self.save_data(data_list)
        thread_list = []

        # 创建url生成线程
        t_generate_url = threading.Thread(target=self.generate_url)
        thread_list.append(t_generate_url)

        # 创建请求线程
        for i in range(3):
            t = threading.Thread(target=self.get_page)
            thread_list.append(t)

        # 创建解析线程
        for i in range(3):
            t = threading.Thread(target=self.parse_data)
            thread_list.append(t)

        # 创建数据存储进程
        t_save_data = threading.Thread(target=self.save_data)
        thread_list.append(t_save_data)

        # 遍历线程列表
        for t in thread_list:
            # 设置守护线程，死循环中的子线程跟随主线程的退出而退出
            t.setDaemon(True)
            t.start()

        # 设置主线程监听队列状态(主线程等待队列操作完毕再退出)
        for q in [self.url_queue, self.response_queue, self.data_queue]:
            q.join()


if __name__ == '__main__':
    qiushi = Qiushi()
    qiushi.run()
