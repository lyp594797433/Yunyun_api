# coding: utf-8
# import requests,json,time
# from requests_toolbelt import MultipartEncoder
# def call_rest_api(API_URL, req_type, data_rtn=None, header=True, get_err_msg=True, token=None, timeout=None):
#     retry_num = 1
#     retry_interval_time = 10
#     cnt = 0
#     while cnt < retry_num:
#         headers = {
#             'token': token,
#             'Content-Type': 'application/json;charset=UTF-8'
#         }
#
#         try:
#             if data_rtn != None:
#                 if req_type == "POST":
#                     values = json.dumps(data_rtn)
#                     # obj_log.info values
#                     req = requests.post(API_URL, data=values, headers=headers)
#                 elif req_type == "PUT":
#                     # obj_log.info API_URL
#                     values = json.dumps(data_rtn)
#                     req = requests.put(API_URL, data=values, headers=headers,timeout=timeout)
#
#                 elif req_type == "GET":
#                     # obj_log.info API_URL
#                     req = requests.get(API_URL, params=data_rtn, headers=headers,timeout=timeout)
#             else:
#                 if req_type == "POST":
#                     values = json.dumps(data_rtn)
#                     req = requests.post(API_URL, headers=headers)
#
#                 elif req_type == "PUT":
#                     # obj_log.info API_URL
#                     req = requests.put(API_URL, headers=headers,timeout=timeout)
#
#                 elif req_type == "GET":
#                     obj_log.info(API_URL)
#                     req = requests.get(API_URL, headers=headers, timeout=timeout)
#         except Exception as e:
#             if get_err_msg == True:
#                 try:
#                     return e.read()
#                 except Exception:
#                     return e
#             continue
#
# 	print req.text
#         if str(req.status_code) == "200":
#             rtn_temp = req.text
#             # rtn_temp = str(rtn_temp)
#             # obj_log.info type(rtn_temp)
#             rtn = json.loads(rtn_temp)
#             req.close()
#             return rtn
#         else:
#             print("ERROR : Failed to requests API!")
#             time.sleep(retry_interval_time)
#             cnt += 1
# 			# print('retry: %d' % cnt)
#             req.close()
#
#     return False
# headers = {
#             'token': '264:a36845a747264078a4a59de9dac8ce78',
#             'Content-Type': 'm.content_type',
#         }
# url = 'http://119.23.205.178/api/image/uploadImageSaveOrUpdate'
#
# image = MultipartEncoder(
#     fields = {"fileImage":("1.png", open(r'D:\1.png', 'rb'),'image/png')}
# )
# test = requests.post(url, data=image, headers=headers)
# print test.text
import datetime
# 计算两个日期的间隔
# d1 = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
# d2 = datetime.datetime.strptime('2018-05-19 00:00:00', '%Y-%m-%d %H:%M:%S')
# print type(d2)
# delta = d2 - d1
# print delta.days
# print delta

#今天的n天后的日期
# now = datetime.datetime.now()
now = datetime.datetime.strptime('2018-06-06 16:54:03', '%Y-%m-%d %H:%M:%S')
print type(now)
delta = datetime.timedelta(days=-29)
n_days=now + delta
print n_days.strftime('%Y-%m-%d %H:%M:%S')
