"""
1.热搜入库
2.历史入库
3.详细入库
"""
import json
from selenium.webdriver import Chrome  # 动态爬取
import time
import utils
from tqdm import tqdm

# 爬取热搜
def get_hotdata():
    url = "https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_aladin_banner#tab1"
    brower = Chrome()
    brower.get(url)
    html = brower.page_source

    # 定义空列表，用来存放数据
    hotdata = []

    # 模拟浏览器点击查看更多
    btn = brower.find_element_by_xpath('//*[@id="ptab-1"]/div[3]/div[11]/span')
    btn.click()

    time.sleep(0.5)
    # 获取数据
    content = brower.find_elements_by_xpath('//*[@id="ptab-1"]/div[3]/div/div/a/div')
    for item in content:
        hotdata.append(item.text)
    return hotdata


# 热搜数据库入库
def insert_hotdata():
    # 获取数据库连接
    conn, cursor = utils.get_conn()
    # %s代表占位
    sql = 'insert into hot_search(date,content) values(%s,%s)'
    # 获取当前时间戳
    data = time.strftime("%Y-%m-%d %X")  # 代表小时和分钟
    datas = get_hotdata()
    for item in datas:
        cursor.execute(sql, (data, item))
        # 提交事务
        conn.commit()
    print("热搜数据插入成功")
    utils.close(conn, cursor)


# 获取全世界各国历史数据
def get_history():
    # 逐行读取
    file = open("data/history_world_corona_virus.json", 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line)
        papers.append(dic)
    return papers[0]


# 获取中国历史的数据
def get_history_china():
    history_china = []
    for i in get_history():
        if i['provinceName'] == '中国':
            history_china.append(i)
    return history_china


# 中国历史数据入库
def insert_history_china():
    history_china = get_history_china()
    # 获取数据库连接
    conn, cursor = utils.get_conn()
    # 时间是字符串数据，不能直接写入到数据库中
    #  insert into history_china(date) values ('2011-04-08 00:00:00');
    sql = '''insert into  
    history_china(date,confirmed_count,confirm_add,suspect,suspect_add,cure,cure_add,dead,dead_add,
    current_confirmed_count,current_confirmed_Incr) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute('delete from history_china')
    # 提交事务
    conn.commit()

    for i in history_china:
        # 日期字符串转为y-m-d形式，固定写法
        datastr = str(i['dateId'])
        tup = time.strptime(datastr, "%Y%m%d")
        dt = time.strftime("%Y-%m-%d", tup)
        cursor.execute(sql, [dt, i['confirmedCount'], i['confirmedIncr'],
                             i['suspectedCount'], i['suspectedCountIncr'],
                             i['curedCount'], i['curedIncr'],
                             i['deadCount'], i['deadIncr'],
                             i['currentConfirmedCount'], i['currentConfirmedIncr']])

        # 提交事务
        conn.commit()
    print("中国历史数据数据插入成功")
    utils.close(conn, cursor)


# 获取中国详细数据
def get_history_china_details():
    # 逐行读取
    file = open("data/today_china_details_corona_virus.json", 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line)
        papers.append(dic)
    return papers[0]


# 中国各城市数据入库
def insert_details_china():
    details_china = get_history_china_details()
    # 获取数据库连接
    conn, cursor = utils.get_conn()
    cursor.execute('delete from details_china')
    # 提交事务
    conn.commit()
    sql = '''insert into  
        details_china(id,update_time,province,city,confirm,confirm_add,cure,cure_add,dead,dead_add) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    sql2 = '''insert into  
        details_china(id,update_time,province,city,confirm,cure,dead) values(%s,%s,%s,%s,%s,%s,%s)'''
    # 获取当前时间戳
    data = time.strftime("%Y-%m-%d %X")  # 代表小时和分钟
    i = 1
    for province in details_china:
        cursor.execute(sql, [i, data, province['provinceName'], province['provinceName'],
                             province['currentConfirmedCount'], province['confirmedIncr'],
                             province['curedCount'], province['curedIncr'],
                             province['deadCount'], province['deadIncr']])
        i += 1
        conn.commit()
        for city in province['cities']:
            cursor.execute(sql2, [i, data, province['provinceName'], city['cityName'],
                                  city['currentConfirmedCount'],
                                  city['curedCount'],
                                  city['deadCount']])
            i += 1
            # 提交事务
            conn.commit()
    print("中国各城市数据插入成功")
    utils.close(conn, cursor)


# 中国各省今日数据入库
def insert_taday_province_china():
    details_china = get_history_china_details()
    # 获取数据库连接
    conn, cursor = utils.get_conn()
    cursor.execute('delete from today_province_china')
    # 提交事务
    conn.commit()
    sql = '''insert into  
            today_province_china(id,update_time,province,city,current_confirmed_count,current_confirmed_Incr,cure,cure_add,dead,dead_add) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    # 获取当前时间戳
    data = time.strftime("%Y-%m-%d %X")  # 代表小时和分钟
    i = 1
    for province in details_china:
        cursor.execute(sql, [i, data, province['provinceName'], province['provinceName'],
                             province['currentConfirmedCount'], province['confirmedIncr'],
                             province['curedCount'], province['curedIncr'],
                             province['deadCount'], province['deadIncr']])
        i += 1
        conn.commit()
    # 提交事务
    conn.commit()
    print("中国各省数据插入成功")
    utils.close(conn, cursor)

#今日世界数据入库
def insert_today_world():
    # 逐行读取
    file = open("data/today_world_corona_virus.json", 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line)
        papers.append(dic)
    today_world = papers[0]

    # 获取数据库连接
    conn, cursor = utils.get_conn()

    sql = '''insert into  
        today_world(id,country,update_time,confirmed_count,confirm_add,
        current_confirmed_count,current_confirmed_Incr,
        cure,cure_add,dead,dead_add,dead_rate
        ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute('delete from today_world')
    # 提交事务
    conn.commit()
    data = time.strftime("%Y-%m-%d %X")  # 代表小时和分钟
    j = 1
    for i in today_world:
        cursor.execute(sql, [j,i['provinceName'],data,
                             i['confirmedCount'], i['incrVo']['confirmedIncr'],
                             i['currentConfirmedCount'], i['incrVo']['currentConfirmedIncr'],
                             i['curedCount'], i['incrVo']['curedIncr'],
                             i['deadCount'], i['incrVo']['deadIncr'],i['deadRate']])

        # 提交事务
        j += 1
    conn.commit()
    print("今天世界数据插入成功")
    utils.close(conn, cursor)

#历史世界数据入库
def insert_history_world():
    file = open("data/history_world_corona_virus.json", 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line)
        papers.append(dic)
    history_world = papers[0]

    # 获取数据库连接
    conn, cursor = utils.get_conn()

    sql = '''insert into  
                history_world(id,country,date,confirmed_count,confirm_add,
                current_confirmed_count,current_confirmed_Incr,
                cure,cure_add,dead,dead_add
                ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute('delete from history_world')
    # 提交事务
    conn.commit()

    j = 1
    for i in tqdm(history_world, "世界历史数据输入插入中:"):
        # 日期字符串转为y-m-d形式，固定写法
        datastr = str(i['dateId'])
        tup = time.strptime(datastr, "%Y%m%d")
        dt = time.strftime("%Y-%m-%d", tup)
        cursor.execute(sql, [j, i['provinceName'], dt,
                             i['confirmedCount'], i['confirmedIncr'],
                             i['currentConfirmedCount'], i['currentConfirmedIncr'],
                             i['curedCount'], i['curedIncr'],
                             i['deadCount'], i['deadIncr']])
        j += 1
        # 提交事务
    conn.commit()
    print("历史世界数据插入成功")
    utils.close(conn, cursor)


def test():
    file = open("data/history_world_corona_virus.json", 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line)
        papers.append(dic)
    history_world = papers[0]

    # 获取数据库连接
    conn, cursor = utils.get_conn()

    sql = '''insert into  
            history_world(id,country,date,confirmed_count,confirm_add,
            current_confirmed_count,current_confirmed_Incr,
            cure,cure_add,dead,dead_add
            ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute('delete from history_world')
    # 提交事务
    conn.commit()

    j = 1
    for i in tqdm(history_world,"世界历史数据输入插入中:"):
        # 日期字符串转为y-m-d形式，固定写法
        datastr = str(i['dateId'])
        tup = time.strptime(datastr, "%Y%m%d")
        dt = time.strftime("%Y-%m-%d", tup)
        cursor.execute(sql, [j,i['provinceName'],dt,
                             i['confirmedCount'], i['confirmedIncr'],
                             i['currentConfirmedCount'], i['currentConfirmedIncr'],
                             i['curedCount'], i['curedIncr'],
                             i['deadCount'], i['deadIncr']])
        j += 1
        # 提交事务
    conn.commit()
    print("历史世界数据插入成功")
    utils.close(conn, cursor)



if __name__ == '__main__':

    #插入中国历史数据
    insert_history_china()

    # #各省的数据大地图用
    #插入今日各省数据
    insert_taday_province_china()

    #插入世界今日数据
    insert_today_world()

    #插入历史世界数据
    # insert_history_world()

