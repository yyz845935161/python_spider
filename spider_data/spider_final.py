import requests
import re
import json
from bs4 import  BeautifulSoup
from tqdm import tqdm #进度条

class CoronaVirusSpider(object):
    #初始要爬取的网站
    def __init__(self):
        self.home_url='https://ncov.dxy.cn/ncovh5/view/pneumonia'

    #响应请求，返回页面爬到的内容,返回字符串
    def get_content_from_url(self,url):
        """
        根据url，获取响应内容的字符串数据
        :param url:请求的url
        :return:响应内容的字符串
        """
        response = requests.get(url)
        return response.content.decode()

    #将爬到的内容解析，返回为一个列表
    def parse_home_page(self,home_page,id):
        """
        解析首页内容，获取解析后的数据
        :param home_page:首页的内容
        :return:解析后的json字符串数据（是一个字典）
        """
        # 2.从疫情首页，提取近一日全国疫情数据
        soup = BeautifulSoup(home_page, 'lxml')
        script = soup.find(id=id)
        text = script.string
        # 3.从疫情的数据中，获取json格式字符串
        json_str = re.findall(r'\[.+\]', text)[0]
        # 4.把json转为python
        data = json.loads(json_str)
        return data

    #保存文件
    def save(self,data,path):
        # 5.以json格式保存
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False)


#今天世界的数据
    def crawl_today_world_corona_virus(self):
        """
        采集最近一天的各国疫情数据
        :return:
        """
        # 1.发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
        # 2.解析首页内容，获取最近一天各国疫情数据
        todday_corona_virus = self.parse_home_page(home_page,id='getListByCountryTypeService2true')
        # 3.保存数据
        self.save(todday_corona_virus,'data/today_world_corona_virus.json')
#历史世界数据
    def crawl_history_world_corona_virus(self):
        """
        采集从1月23号以来，各国疫情数据
        :return:
        """
        corona_virus=[]#用于存储总的



        # 1.加载各国疫情数据,
            # 1.1发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
            # 1.2解析首页内容，获取最近一天各国疫情数据
        today_corona_virus = self.parse_home_page(home_page,id='getListByCountryTypeService2true')



        # 2.遍历各国疫情数据，获取统计URl,每个国家都有自己的历史数据
        for country in tqdm(today_corona_virus,'采集1月23日以来的各国疫情信息'):
            # 2.1.发送请求，获取各国1月23号至今的json数据
            history_country_url = country['statisticsData']#拿到每个国家的历史信息网站
            #2.2.拿到网站中字符串内容
            statistics_history_data_str=self.get_content_from_url(history_country_url)
            #2.3.字符串晒选转列表
            statistics_history_data_list=json.loads(statistics_history_data_str)['data']
            #print(type(statistics_history_data_list))
            #2.4 内容中少了国家属性，添加国家属性
            for i in statistics_history_data_list:
                i['provinceName']=country['provinceName']
                i['countryShortCode'] = country['countryShortCode']
            # print(statistics_history_data_list)
            corona_virus.extend(statistics_history_data_list)

        # 6.把列表以json格式保存文件
        self.save(corona_virus, 'data/history_world_corona_virus.json')

#今天中国数据
    def crawl_today_china_details_corona_virus(self):
        """
                采集最近一天的各国疫情数据
                :return:
                """
        # 1.发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
        # 2.解析首页内容，获取最近一天各国疫情数据
        todday_corona_virus = self.parse_home_page(home_page, id='getAreaStat')

        for province in tqdm(todday_corona_virus, '采集今日各省数据'):
            # 2.1.发送请求，获取各国1月23号至今的json数据
            temp = province['statisticsData']  # 拿到每个省份的历史信息网站
            # 2.2.拿到网站中字符串内容
            statistics_history_data_str = self.get_content_from_url(temp)
            # 2.3.字符串晒选转列表
            statistics_history_data_list = json.loads(statistics_history_data_str)['data']
            yesterday_data = statistics_history_data_list[len(statistics_history_data_list) - 1]
            # 添加昨天的
            province['confirmedIncr'] = yesterday_data['confirmedIncr']
            province['curedIncr'] = yesterday_data['curedIncr']
            province['deadIncr'] = yesterday_data['deadIncr']
        print(todday_corona_virus)

        # 保存数据
        self.save(todday_corona_virus, 'data/today_china_details_corona_virus.json')

#历史中国数据
    def crawl_history_china_provinces_corona_virus(self):
        """
                采集从1月23号以来，各国疫情数据
                :return:
                """
        corona_virus = []  # 用于存储总的

        # 1.加载各国疫情数据,
        # 1.1发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
        # 1.2解析首页内容，获取最近一天各国疫情数据
        today_corona_virus = self.parse_home_page(home_page, id='getAreaStat')

        # 2.遍历各国疫情数据，获取统计URl,每个国家都有自己的历史数据
        for province in tqdm(today_corona_virus, '采集1月22日以来的各省疫情信息'):
            # 2.1.发送请求，获取各国1月23号至今的json数据
            history_province_url = province['statisticsData']  # 拿到每个省份的历史信息网站
            # 2.2.拿到网站中字符串内容
            statistics_history_data_str = self.get_content_from_url(history_province_url)
            # 2.3.字符串晒选转列表
            statistics_history_data_list = json.loads(statistics_history_data_str)['data']

            # 2.4 内容中少了国家属性，添加国家属性
            for i in statistics_history_data_list:
                i['provinceName'] = province['provinceName']
                # i['countryShortCode'] = country['countryShortCode']
            # print(statistics_history_data_list)
            corona_virus.extend(statistics_history_data_list)
            # print(corona_virus)
        # 3.把列表以json格式保存文件
        self.save(corona_virus, 'data/history_china_provinces_corona_virus.json')

    def test(self):
        # 1.发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
        # 2.解析首页内容，获取最近一天各国疫情数据
        todday_corona_virus = self.parse_home_page(home_page, id='getAreaStat')

        for province in tqdm(todday_corona_virus,'采集今日各省数据'):
            # 2.1.发送请求，获取各国1月23号至今的json数据
            temp = province['statisticsData']  # 拿到每个省份的历史信息网站
            # 2.2.拿到网站中字符串内容
            statistics_history_data_str = self.get_content_from_url(temp)
            # 2.3.字符串晒选转列表
            statistics_history_data_list = json.loads(statistics_history_data_str)['data']
            yesterday_data=statistics_history_data_list[len(statistics_history_data_list)-1]
            #添加昨天的
            print(yesterday_data)
            province['confirmedIncr']=yesterday_data['confirmedIncr']
            province['curedIncr'] = yesterday_data['curedIncr']
            province['deadIncr'] = yesterday_data['deadIncr']
        print(todday_corona_virus)


        # 保存数据
        self.save(todday_corona_virus, 'data/today_china_details_corona_virus.json')


    def run(self):
        self.crawl_today_corona_virus()

if __name__ == '__main__':
    spider = CoronaVirusSpider()
    #中国的历史数据在世界历史中

    #爬今天世界的
    spider.crawl_today_world_corona_virus()

    #爬全世界历史的
    spider.crawl_history_world_corona_virus()

    #爬今天中国的各省细节的
    spider.crawl_today_china_details_corona_virus()