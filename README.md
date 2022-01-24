# webpy_demo
Securities data analysis demo by webpy and tushare api.

基于 webpy 和 tushare 的证券数据分析。

## 文件结构
- data.py： 从 `tushare` 接口导入数据到 `MySQL` 数据库
- Code.py:：`web.py` 运行的主文件，其中功能类包含实现的算法
- templates：模板的目录

## 使用
1. 配置 Python 环境，安装 MySQL 数据库。
2. 修改 `data.py` 中的 `接口 TOKEN` 和数据库的配置，运行 `data.py` 将数据存储到数据库中。
3. 修改 `Code.py` 中的 `web.database` 数据库的配置，运行 `Code.py`：

    ```
    python Code.py
    ```

## 编程环境
> 语言：Python
> 
> ide：PyCharm
> 
> 系统：Windows10
> 
> 数据库：MySQL
> 
> 数据接口：[Tushare](https://tushare.pro/) 
> 
> 框架：[web.py](https://webpy.org/docs/0.3/tutorial.zh-cn) 

## 实现功能
1. 连接 tushare 接口，接入数据。
2. 获取所选标的的开盘价、收盘价、最低价、最高价、成交量。
3. 找到前一波段的的最低点 min 和最高点 max，找到当前的最高点 max0 和最低点 min0。如果 max0 > max 且成交量 volume 增加，标记为：向上（考虑开盘价或最低价）；如果 min0 < min, 标记为：向下（考虑开盘价或最高价）。
4. 根据 3 计算可信点数和斜率：如果只有一个价格符合，记为 30 分；2 个价格都符合，记为 60 分；每增加一天符合加 1 分；增加一个大波段符合，加 10 分。每两点构成直线，计算斜率：（后面点的价格-前面点的价格）/天数。
5. 计算回落点数
    - 以该波段内最高价和当天最低价计算回落点数（%），显示：回落\*\*点。
    - 设置点数（可交互），以该波段内最高价计算回落价，按当前价输出是否达到提示，并给出当前具体点数；设置点数（可交互），以昨日收盘价计算上涨价，按当前价输出是否达到提示，并给出当前具体点数

## 交互界面
![image](https://user-images.githubusercontent.com/42886406/150705954-a2deb284-033b-4c38-bf46-8fa1882f53c8.png)
## 结果界面
![image](https://user-images.githubusercontent.com/42886406/150705991-9b0d7910-202f-4063-a1b9-37ef1c356234.png)

## TODO
1. 交互界面的美化。
2. 获取多个证券编号的数据进行处理。

