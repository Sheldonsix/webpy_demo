# 从 tushare 接口导入数据到数据库
from venv import create
import pandas as pd
import tushare as ts
from sqlalchemy import create_engine

# 设置 tushare 的接口 TOKEN
ts.set_token('**************************************')

# 用户名和密码换成登录数据库的用户名和密码
engine_ts = create_engine('mysql://用户名:密码@127.0.0.1:3306/ts_history_data?charset=utf8&use_unicode=1')

# 从数据库读数据
def read_data():
    sql = """SELECT * FROM henghe ORDER BY 2 ASC"""
    df = pd.read_sql_query(sql, engine_ts)
    return df

# 向数据库写数据
def write_data(df):
    try:
        res = df.to_sql(ts_code, engine_ts, index=False, if_exists='append', chunksize=5000)
        print(res)
        print("数据成功写到数据库。")
    except Exception as e:
        print(e)
        
# 用 tushare 接口获取数据
def get_data():
    pro = ts.pro_api()
    # 获取证券号为 ts_code 的证券数据
    df = pro.cb_daily(ts_code = ts_code)
    return df


if __name__ == '__main__':
    # df = read_data()
    # 获取数据
    df = get_data()
    # 写入数据
    write_data(df)
    print(df)