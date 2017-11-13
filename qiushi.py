import requests
from lxml import etree
import time
import json


class Qiushi(object):
    def __init__(self):
        self.base_url = 'https://www.qiushibaike.com/8hr/page/%s/'
        self.url_list = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
        }
        self.file = open('day03/qiushi.json', 'w', encoding='utf8')

    def generate_url(self):
        self.url_list = [self.base_url % (i) for i in range(1, 14)]
        # print(self.url_list)

    def get_page(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    def parse_data(self, data):
        html = etree.HTML(data)

        node_list = html.xpath('//div[@id="content-left"]/div')
        # print(len(node_list))

        data_list = []
        for node in node_list:
            temp = {}
            try:
                temp['user'] = node.xpath('./div[1]/a[2]/h2/text()')[0].strip()
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
        return data_list

    def save_data(self, data_list):
        for data in data_list:
            str_data = json.dumps(data, ensure_ascii=False) + ',\n'
            self.file.write(str_data)

    def __del__(self):
        self.file.close()

    def run(self):
        self.generate_url()

        for url in self.url_list:
            data = self.get_page(url)
            data_list = self.parse_data(data)
            time.sleep(1)
            self.save_data(data_list)


if __name__ == '__main__':
    qiushi = Qiushi()
    qiushi.run()
