import requests
from lxml import etree
import os
import json
import sys


class Tieba_cat(object):
    def __init__(self, tieba_name):
        # self.url = 'http://tieba.baidu.com/f?kw=%s' % (tieba_name)
        self.url = 'http://tieba.baidu.com/f?kw={}'.format(tieba_name)
        print(self.url)
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
            # chrome浏览器会自动将HTML页面注释，所以使用叫老的IE浏览器
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0) '

        }
        self.file = open('tieba.json', 'w', encoding='utf8')

    def get_data(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    def parse_list_page(self, data):
        '''//li[@class=" j_thread_list clearfix"]/div/div[2]/div[1]/div[1]/a'''
        # 将源码转换成 element 对象
        html = etree.HTML(data)

        # 获取节点列表
        node_list = html.xpath(
            '//li[@class=" j_thread_list clearfix"]/div/div[2]/div[1]/div[1]/a')
        # print(len(node_list))
        data_list = []
        for node in node_list:
            temp = {}
            temp['title'] = node.xpath('./text()')[0]
            temp['url'] = 'http://tieba.baidu.com/' + node.xpath('./@href')[0]
            # temp['url'] = 'http://tieba.baidu.com/' + node.xpath('./@href')[0]

            data_list.append(temp)

        # 获取下一页，如果是尾页则返回 None
        try:
            next_url = 'http:' + \
                html.xpath('//*[@id="frs_list_pager"]/a[last()-1]/@href')[0]
        except:
            next_url = None

        return data_list, next_url

    def parse_detail_page(self, data):
        '''//div[@class="p_content  p_content p_content_nameplate"]/cc/*[@class="d_post_content j_d_post_content  clearfix"]/img'''
        html = etree.HTML(data)
        image_list = html.xpath(
            '//div[@class="p_content  p_content p_content_nameplate"]/cc/*[@class="d_post_content j_d_post_content  clearfix"]/img/@src'
        )
        return image_list

    def download(self, image_list):
        if not os.path.exists('image'):
            os.makedirs('image')

        for url in image_list:
            filename = 'image' + os.sep + url.split('/')[-1]
            data = self.get_data(url)
            with open(filename, 'wb') as f:
                f.write(data)

    def save_data(self, data):
        str_data = json.dumps(data, ensure_ascii=False) + ',\n'
        self.file.write(str_data)

    def __del__(self):
        self.file.close()

    def run(self):
        next_url = self.url
        while True:
            data = self.get_data(self.url)
            # 在响应页面中抽取详情页面数据列表，下一页url
            detail_list, next_url = self.parse_list_page(data)

            for detail in detail_list:
                # 获取子页面相应
                detail_data = self.get_data(detail['url'])
                image_list = self.parse_detail_page(detail_data)
                self.download(image_list)
                # 保存数据
                detail['images'] = image_list
                self.save_data(detail)


if __name__ == '__main__':
    tieba = Tieba_cat('猫')
    tieba.run()
