import insert_sql
import spider_final

def updata_mysql():
    spider=spider_final.CoronaVirusSpider()

    #爬取全世界历史的
    spider.crawl_history_world_corona_virus()

    # 爬今天天世界的
    spider.crawl_today_world_corona_virus()

    #爬取今天的各省和城市
    spider.crawl_today_china_details_corona_virus()

    #中国历史数据入库
    insert_sql.insert_history_china()

    #中国今天各省数据入库
    insert_sql.insert_taday_province_china()

    #世界今日数据入库
    insert_sql.insert_today_world()

    #世界历史数据入库
    insert_sql.insert_history_world()

if __name__ == '__main__':
    updata_mysql()