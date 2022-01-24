import web
import math
from datetime import datetime, timedelta
import time
import numpy as np
import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
from web import form
import pymysql
db = web.database(dbn='mysql', user='****', pw='*****', db='********')
render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/search', 'search',
)

app = web.application(urls, globals())

# myform = form.Dropdown('mydrop', [('20211111', 'des1'), ('20211110', 'des2')])
trade_date = []
date = db.select('henghe', what="trade_date")


for k, v in enumerate(date):
    obj = {}
    for k1, v1 in enumerate(v):
        trade_date.append(v[v1])

# print(trade_date[0]['trade_date'])

myform = form.Form(
    form.Dropdown('股票代码', ['123013.sz']),
    form.Dropdown('交易日期', trade_date),
    form.Dropdown('回落点数', [x for x in range(100)]),
    form.Dropdown('上涨点数', [x for x in range(100)]),
    )

class Function():
    def __init__(self, ts_code, ts_date, user_set_up_points, user_set_fallback_points):
        """
        :param ts_code: 股票代码
        :param ts_date: 交易日期
        :param user_set_fallback_points: 回落点数
        :param user_set_up_points: 上涨点数
        """
        self._ts_code = ts_code
        self._ts_date = ts_date
        self._user_set_fallback_points = user_set_fallback_points
        self._user_set_up_points = user_set_up_points
        self._min_list = []
        self._max_list = []
        self._closing_list = []
        self._closing_num_list = []
        self._band_num_list = []
        self._band_date_list = []
        self._credibility = 0
        self._flag = True
        self._now_band = []
        self._pre_band = []
        self._engine_ts = create_engine('mysql://root:123456@127.0.0.1:3306/ts_history_data?charset=utf8&use_unicode=1')
        self._sql = """SELECT * FROM henghe ORDER BY 2 ASC"""
        self._df = pd.read_sql_query(self._sql, self._engine_ts).to_dict()
        self._df_list = pd.read_sql_query(self._sql, self._engine_ts).values.tolist()
        self._now_num = self.date_to_num(self._ts_date)
        self.get_closing_list()
        self.get_band()
        self.get_band_num()
        self._pre_num_1 = self.date_to_num(self._pre_band[0])
        self._pre_num_2 = self.date_to_num(self._pre_band[1])
        self._now_num_1 = self.date_to_num(self._now_band[0])
        self._now_num_2 = self.date_to_num(self._now_band[1])

    def date_to_num(self, date):
        num = 0
        for i in self._df['trade_date'].values():
            if i == date:
                break
            else:
                num += 1
        return num

    def get_closing_list(self):
        for i in self._df['close'].values():
            self._closing_list.append(i)
        return self._closing_list

    def get_band(self):
        for i in range(1, len(self._closing_list) - 1):
            if self._closing_list[i] < self._closing_list[i - 1] and self._closing_list[i] < self._closing_list[i + 1]:
                self._closing_num_list.append(i)
            elif self._closing_list[i] > self._closing_list[i - 1] and self._closing_list[i] > self._closing_list[i + 1]:
                self._closing_num_list.append(i)
            else:
                continue
        for i in range(len(self._closing_num_list) - 1):
            if self._closing_list[self._closing_num_list[i]] > self._closing_list[self._closing_num_list[i + 1]]:
                self._flag = False
            else:
                self._flag = True
            self._band_num_list.append((self._closing_num_list[i], self._closing_num_list[i + 1], self._flag))
            self._band_date_list.append((self._df_list[self._closing_num_list[i]][1], self._df_list[self._closing_num_list[i + 1]][1], self._flag))
        return self._closing_num_list, self._band_num_list, self._band_date_list

    def get_band_num(self):
        ts_date_strp = datetime.strptime(self._ts_date, '%Y%m%d')
        for i in range(1, len(self._band_date_list)):
            if ts_date_strp >= datetime.strptime(self._band_date_list[i][0], "%Y%m%d") and ts_date_strp < datetime.strptime(self._band_date_list[i][1], '%Y%m%d'):
                self._now_band.append(self._band_date_list[i][0])
                self._now_band.append(self._band_date_list[i][1])
                self._pre_band.append(self._band_date_list[i - 1][0])
                self._pre_band.append(self._band_date_list[i - 1][0])
            else:
                continue
        return self._now_band, self._pre_band

    def get_max(self):
        max = self._df['high'][self._now_num]
        return max

    def get_min(self):
        min = self._df['low'][self._now_num]
        return min

    def get_opening(self):
        opening = self._df['open'][self._now_num]
        return opening

    def get_closing(self):
        closing = self._df['close'][self._now_num]
        return closing

    def get_volume(self):
        volume = self._df['vol'][self._now_num]
        return volume

    def get_band_max(self):
        band_max = self._df['high'][self._now_num_1]
        for i in range(self._now_num_1, self._now_num_2):
            if self._df['high'][i + 1] > self._df['high'][i]:
                band_max = self._df['high'][i + 1]
            else:
                continue
        return band_max

    def get_yesterday_closing(self):
        yesterday_closing = self._df['close'][self._now_num - 1]
        return yesterday_closing

    def get_previous_min(self):
        pre_min = self._df['low'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['low'][i + 1] < self._df['low'][i]:
                pre_min = self._df['low'][i + 1]
            else:
                continue
        return pre_min

    def get_previous_max(self):
        pre_max = self._df['high'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['high'][i + 1] > self._df['high'][i]:
                pre_max = self._df['high'][i + 1]
            else:
                continue
        return pre_max

    def get_previous_max_opening(self):
        pre_max_opening = self._df['open'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['open'][i + 1] > self._df['open'][i]:
                pre_max_opening = self._df['open'][i + 1]
            else:
                continue
        return pre_max_opening

    def get_previous_min_opening(self):
        pre_min_opening = self._df['open'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['open'][i + 1] < self._df['open'][i]:
                pre_min_opening = self._df['open'][i + 1]
            else:
                continue
        return pre_min_opening

    def get_previous_avg_opening(self):
        temp = 0
        for i in range(self._pre_num_1, self._pre_num_2 + 1):
            temp += self._df['open'][i]
        pre_avg_opening = int(temp / (self._pre_num_2 + 1 - self._pre_num_1) * 100) / 100
        return pre_avg_opening

    def get_previous_min_volume(self):
        pre_min_volume = self._df['vol'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['vol'][i + 1] < self._df['vol'][i]:
                pre_min_volume = self._df['vol'][i + 1]
            else:
                continue
        return pre_min_volume

    def get_previous_max_volume(self):
        pre_max_volume = self._df['vol'][self._pre_num_1]
        for i in range(self._pre_num_1, self._pre_num_2):
            if self._df['vol'][i + 1] > self._df['vol'][i]:
                pre_max_volume = self._df['vol'][i + 1]
            else:
                continue
        return pre_max_volume

    def get_previous_average_volume(self):
        temp = 0
        for i in range(self._pre_num_1, self._pre_num_2 + 1):
            temp += self._df['vol'][i]
        pre_avg_volume = int(temp / (self._pre_num_2 + 1 - self._pre_num_1) * 100) / 100
        return pre_avg_volume

    def data_label(self, now_max, previous_max, now_min, previous_min, now_volume, pre_avg_volume,
                   now_opening, pre_avg_opening):
        label = -1
        if (now_max > previous_max and now_volume > pre_avg_volume
                or now_opening > pre_avg_opening and now_volume > pre_avg_volume):
            label = True
            print("当前最高点大于前一波段最高点，且成交量增加，标记向上")
        elif (now_min < previous_min
              or now_opening < pre_avg_opening):
            label = False
            print("当前最低点小于前一波段最低点，标记向下")
        else:
            print("既不向上也不向下")

        return label

    def get_credibility_2(self, now_max, previous_max, now_min, previous_min, now_volume, pre_avg_volume,
                          now_opening, pre_avg_opening):
        up_credibility = 0
        down_credibility = 0
        up_band = 1
        down_band = 1
        up_slop = []
        down_slop = []
        if (now_max > previous_max and now_volume > pre_avg_volume
                or now_opening > pre_avg_opening and now_volume > pre_avg_volume):
            up_credibility = 30
        elif (now_max > previous_max and now_opening > pre_avg_opening and now_volume > pre_avg_volume):
            up_credibility = 60
        elif (now_min < previous_min
              or now_opening < pre_avg_opening):
            down_credibility = 30
        elif (now_min < previous_min and now_opening < pre_avg_opening):
            down_credibility = 60

        if up_credibility >= 30 or down_credibility >= 30:
            for i in range(self._pre_num_1, self._pre_num_2 + 1):
                if now_max > self._df['high'][i]:
                    up_credibility += 1
                    up_slop.append(self.get_slope(now_max, self._df['high'][i], self._now_num, i))
                elif now_min < self._df['low'][i]:
                    down_credibility += 1
                    down_slop.append(self.get_slope(now_min, self._df['low'][i], self._now_num, i))

            for i in range(self._pre_num_1, self._pre_num_2 + 1):
                if now_max >= self._df['high'][i]:
                    continue
                else:
                    up_band = 0

            for i in range(self._pre_num_1, self._pre_num_2 + 1):
                if now_min <= self._df['low'][i]:
                    continue
                else:
                    down_band = 0

            if up_band:
                up_credibility += 10
            elif down_band:
                down_credibility += 10

        return (up_credibility, down_credibility, up_slop, down_slop)

    def get_slope(self, now_price, previous_price, now_num, previous_num):
        return int((now_price - previous_price) / (now_num - previous_num) * 100) / 100

    def get_fallback_points(self, band_max, now_min):
        fallback_points = (band_max - now_min) / band_max * 100
        return int(fallback_points * 100) / 100

    def get_up_points(self, yesterday_closing, now_opening):
        up_points = (now_opening - yesterday_closing) / yesterday_closing * 100
        return int(up_points * 100) / 100


class index:
    def GET(self):
        # data = db.select('henghe')
        form = myform()
        return render.formtest(form)
        # print("Hello, world!")

    def POST(self):
        form = web.input()
        print(form)
        settings = {}
        results = {}
        for k in form:
            settings[k] = form[k]
        print(settings)
        tup = (settings['股票代码'], settings['交易日期'], settings['上涨点数'], settings['回落点数'])
        results['max'] = Function(*tup).get_max()
        results['min'] = Function(*tup).get_min()
        results['opening'] = Function(*tup).get_opening()
        results['closing'] = Function(*tup).get_closing()
        results['volume'] = Function(*tup).get_volume()
        results['band_max'] = Function(*tup).get_band_max()
        results['yesterday_closing'] = Function(*tup).get_yesterday_closing()
        results['pre_min'] = Function(*tup).get_previous_min()
        results['pre_max'] = Function(*tup).get_previous_max()
        results['pre_max_volume'] = Function(*tup).get_previous_max_volume()
        results['pre_min_volume'] = Function(*tup).get_previous_min_volume()
        results['pre_avg_volume'] = Function(*tup).get_previous_average_volume()
        results['pre_max_opening'] = Function(*tup).get_previous_max_opening()
        results['pre_min_opening'] = Function(*tup).get_previous_min_opening()
        results['pre_avg_opening'] = Function(*tup).get_previous_avg_opening()
        results['up_credibility'], results['down_credibility'], results['up_slop'], results['down_slop'] = Function(*tup).get_credibility_2(results['max'], results['pre_max'], results['min'], results['pre_min'], results['volume'], results['pre_avg_volume'], results['opening'], results['pre_avg_opening'])
        results['fallback_points'] = Function(*tup).get_fallback_points(results['band_max'], results['min'])
        results['up_points'] = Function(*tup).get_up_points(results['yesterday_closing'], results['opening'])
        return render.index(settings, results)
# class search:
#     def GET(self):
#         return render.index()
#
#     def POST(self):
#         i = web.input()
#         results = db.select('henghe', where="trade_date = $i")
#         return render.index(results)

if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()
