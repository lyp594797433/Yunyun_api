#coding=utf-8
import time
import datetime

def yes_time():
    #获取当前时间
    now_time = datetime.datetime.now()
    #当前时间减去一天 获得昨天当前时间
    yes_time = now_time + datetime.timedelta(days=-1)
    #格式化输出
    yes_time_str = yes_time.strftime('%Y-%m-%d %H:%M:%S')
    print yes_time_str  # 2017-11-01 22:56:02

def dif_time():
    #计算两个时间之间差值
    now_time = datetime.datetime.now()
    now_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
    d1 = datetime.datetime.strptime('2017-10-16 19:21:22', '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
    #间隔天数
    day = (d2 - d1).days
    #间隔秒数
    second = (d2 - d1).seconds
    print day   #17
    print second  #13475  注意这样计算出的秒数只有小时之后的计算额 也就是不包含天之间差数

def unix_time():
    #将python的datetime转换为unix时间戳
    dtime = datetime.datetime.now()
    un_time = time.mktime(dtime.timetuple())
    print un_time  #1509636609.0
    #将unix时间戳转换为python  的datetime
    timestamp = un_time
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    print dt

unix_time()