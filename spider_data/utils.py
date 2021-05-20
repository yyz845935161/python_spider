import pymysql

def get_conn():
    # 创建数据库连接
    conn = pymysql.connect(host='127.0.0.1', port=3306,
                           user='root', password='yyz521521',
                           database='covid_19_data', charset='utf8')
    if conn == None:
        print('数据连接失败')
    else:
        print('数据库连接成功')

    cursor = conn.cursor()
    return conn,cursor

#释放资源
def close (conn,cursor):
    cursor.close()
    conn.close()
