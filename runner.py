# -*- coding=utf-8 -*-
import utils,time,log,re,sys,json,simplejson,random,requests,threading
from collections import namedtuple
obj_log = log.get_logger()

class Runner:
	def __init__(self, all_config):
		self.obj_tools = utils.Tools()
		# self.hallCode =  self.obj_utils.hallCode
		self.user = all_config['username']
		self.pwd = all_config['pwd']
		self.port = all_config['port']
		self.ip = all_config['ip']
		self.my_user1 = all_config['my_user1']
		self.my_pwd1 = all_config['my_pwd1']
		self.add = self.obj_tools.add
	'''客户角色新增操作'''

	def _role_add(self, hallcode):
		'''运营系统角色新增'''
		req_type = 'POST'
		temp_dict = {}
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
		login_info = self.obj_tools.sql_event(sql_statement)
		admin_customer_password = login_info[0]['password']
		admin_customer_username = login_info[0]['userName']
		token = self.obj_tools.loginYunyun(hallcode, admin_customer_username, admin_customer_password)
		currentUserId_statement = "SELECT id from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
		currentUserId_info = self.obj_tools.sql_event(currentUserId_statement)
		currentUserId = currentUserId_info[0]['id']
		temp_dict['currentUserId'] = currentUserId
		temp_dict['name'] = hallcode + '-name-' + now_time
		temp_dict['description'] = hallcode + '-desc-' + now_time
		temp_dict['menuIds'] = ["15","18","33","16","37"]
		API_URL = "http://" + self.add + "/api/roleMenu/saveRoleMenu"
		req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
		if req['status'] == 200:
			obj_log.info('Add role {} successfully........'.format(temp_dict['name']))
		else:
			obj_log.info('Add role {} failed.......'.format(temp_dict['name']))
			return False

		return temp_dict['name']

	def _user_add(self, hallcode, role_id):
		'''运营系统用户新增'''
		req_type = 'POST'
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"

		login_info = self.obj_tools.sql_event(sql_statement)
		admin_customer_password = login_info[0]['password']
		admin_customer_username = login_info[0]['userName']
		token = self.obj_tools.loginYunyun(hallcode, admin_customer_username, admin_customer_password)
		temp_dict = {}
		temp_dict['hallCode'] = hallcode
		temp_dict['departmentDto'] = {}
		temp_dict['departmentDto']['deptName'] = '部门1'
		customer_id_statement = "SELECT id from system_customer WHERE hallCode = " + "'" + hallcode + "'"
		customer_id = self.obj_tools.sql_event(customer_id_statement)
		customer_id = customer_id[0]['id']
		dept_id_statement = "SELECT id FROM system_user_department WHERE customerId = " + str(customer_id) + " AND deptName = " + \
							"'" + temp_dict['departmentDto']['deptName'] + "'"
		dept_id = self.obj_tools.sql_event(dept_id_statement)
		dept_id = dept_id[0]['id']
		temp_dict['departmentDto']['id'] = dept_id
		temp_dict['dutyDto'] = {}
		temp_dict['dutyDto']['dutyName'] = '职务1'
		duty_id_statement = "SELECT id FROM system_user_duty WHERE deptId = " + str(dept_id) + " AND dutyName = " + \
							"'" + temp_dict['dutyDto']['dutyName'] + "'"
		dept_id = self.obj_tools.sql_event(duty_id_statement)
		dept_id = dept_id[0]['id']
		temp_dict['dutyDto']['id'] = dept_id
		temp_dict['roleId'] = role_id
		temp_dict['sex'] = "1"
		temp_dict['userName'] = hallcode + "-新增-" + now_time
		temp_dict['phone'] = '13980004762'
		temp_dict['tel'] = '13980004762'
		temp_dict['chat'] = '13980004762@163.com'
		API_URL = "http://" + self.add + "/api/user/saveSystemUser"
		req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
		if req['status'] == 200:
			obj_log.info('Add user %s successfully........' % (temp_dict['userName']))
			update_user_statement = "UPDATE system_user set is_first_login = 1 WHERE hallCode = '" + hallcode + "' and userName = '" + \
									temp_dict['userName'] + "'"
			update_user_status = self.obj_tools.sql_event(update_user_statement)

		else:
			obj_log.info('Add user %s failed.......'% (temp_dict['userName']))
			return False

		return temp_dict['userName']

	def _upload_image(self):
		req_type = 'POST'
		API_URL = "http://" + self.add + "/api/image/uploadImageSaveOrUpdate"
		files = {'fileImage': ("11.png", open(r'C:\Users\Administrator\Desktop\APP\11.jpg', 'rb'), 'image/png')}
		obj_log.info('Upload image start.......')
		token = self.obj_tools.loginYunyun()
		req = self.obj_tools.call_rest_api(API_URL,req_type=req_type,token=token, files=files,multipart=True)
		if req['status'] == 200:
			obj_log.info('Upload image successfully.......')
		else:
			obj_log.info('Upload image failed.......')
			return False
		return req['data']

	def _searchActivity(self, title):
		'''通过活动名字获取活动详情.
				:param title : 活动名称
				:rtype : dict
				'''
		sql_statement = '''SELECT * from system_activity WHERE title = "''' + str(title) + '''"'''
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]


	def _new_audited(self, new_id):
		'''资讯审核'''
		req_type = 'PUT'
		new_status_statement = "SELECT status from system_news WHERE id = " + str(new_id)
		get_new_status = self.obj_tools.sql_event(new_status_statement)
		new_status = get_new_status[0]['status']
		if new_status == 3:
			obj_log.info("The news need audit by second_level customer user........")
			hallcode_statement = "SELECT hallCode from system_customer WHERE id = (SELECT sourceId FROM system_news WHERE id = " + str(new_id) + ")"
			hallcode_name =  self.obj_tools.sql_event(hallcode_statement)

			# 根据new_id判断是不是客户代码 0：图书馆 其他：客户代码
			if len(hallcode_name) == 0:
				library_id_statement = "SELECT sourceId FROM system_news WHERE id = " + str(new_id)
				hallcode_id = self.obj_tools.sql_event(library_id_statement)
				library_id = hallcode_id[0]['sourceId']
				get_customer_statement = "SELECT hallCode from system_customer WHERE id = (SELECT customerId from librarys WHERE id = " + str(library_id) + ")"
				hallcode_temp = self.obj_tools.sql_event(get_customer_statement)
				hallcode = hallcode_temp[0]['hallCode']
			else:
				hallcode = hallcode_name[0]['hallCode']

			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/news/" + str(new_id) + "/newAudited?currentUserId=" +  str(audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			if req['status'] == 200:
				obj_log.info('Audited second_level the new {} successfully........'.format(new_id))

			else:
				obj_log.info('Audited second_level the new {} failed........'.format(new_id))
				return False
		self.obj_tools.progressbar_k(2)
		get_new_status = self.obj_tools.sql_event(new_status_statement)
		new_status = get_new_status[0]['status']
		if new_status == 2:
			obj_log.info("The news need audit by primary_level customer user........")
			hallcode = "YTSG"
			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/news/" + str(new_id) + "/newAudited?currentUserId=" + str(
				audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			if req['status'] == 200:
				obj_log.info('Audited primary_level the new {} successfully........'.format(new_id))
			else:
				obj_log.info('Audited primary_level the new {} failed........'.format(new_id))
				return False

		return True

	def _activity_audited(self, activity):
		'''通过hallCode获取图书馆信息.
		:param activity : 活动详情
		:rtype : dict
		'''
		req_type = 'PUT'
		flag = 0
		new_status = activity['status']
		if new_status == 3:
			# 二级待审
			obj_log.info("二级待审状态，客户审核........")
			hallcode_statement = "SELECT hallCode from system_customer WHERE id = " + str(activity['customerId'])
			hallcode =  self.obj_tools.sql_event(hallcode_statement)
			hallcode = hallcode[0]["hallCode"]
			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + str(hallcode) + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/activity/" + str(activity['id']) + "/audited?userId=" + str(
				audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			if req['status'] == 200:
				obj_log.info('Audited second_level the activity {} successfully........'.format(activity['id']))
				flag += 1
			else:
				obj_log.info('Audited second_level the activity {} failed........'.format(activity['id']))
				return False

		if new_status == 1 or flag == 1:
			obj_log.info("该活动平台创建，直接平台审核.")
			hallcode = "YTSG"
			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + str(hallcode) + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/activity/" + str(activity['id']) + "/audited?userId=" + str(
				audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			if req['status'] == 200:
				obj_log.info('Audited primary_level the activity {} successfully........'.format(activity['id']))
			else:
				obj_log.info('Audited primary_level the activity {} failed........'.format(activity['id']))
				return False

		return True


	def _get_customer_user_info(self, hallcode):
		'''返回hallcode对应客户的用户ID(有新增权限)，username，password'''
		power_list = []
		all_customer_statement = "SELECT id from system_user WHERE hallCode = " + "'" + hallcode + "'" + " AND isEffective = 1"
		all_customer_user = self.obj_tools.sql_event(all_customer_statement)
		user_info = []
		for i in range(len(all_customer_user)):
			for user in all_customer_user[i]:
				user_id = all_customer_user[i]['id']
				user_power_statement = "SELECT id FROM system_menu WHERE id in (\
										SELECT menuId FROM system_role_menu WHERE roleId = (\
										SELECT roleId from system_user_role WHERE userId = " + str(user_id) + "))"
				user_power_info = self.obj_tools.sql_event(user_power_statement)
				for i in user_power_info:
					power_list.append(i['id'])
				# 查看新增权限是否存在： 15L 资讯新增权限
				if 15 in power_list:
					right_username_statement =  "SELECT id, userName, password from system_user WHERE hallCode = " + "'"\
												+ hallcode + "'" + " and id = " + str(user_id)
					user_info = self.obj_tools.sql_event(right_username_statement)
					break
		if len(user_info) == 0:
			obj_log.info("The customer {} have no user possess the power of add the news".format(hallcode))
			obj_log.info("Add the user with the power of add the news on customer {}. ".format(hallcode))
			# 新增有资讯新增权限的用户
			time.sleep(3)
			role_add_rtn = self._role_add(hallcode)
			# 获取客户ID
			customer_id_statement = "SELECT id from system_customer WHERE hallCode = " + "'" + hallcode + "'"
			customer_id = self.obj_tools.sql_event(customer_id_statement)
			customer_id = customer_id[0]['id']
			# 获取角色ID
			role_id_statement = "SELECT id FROM  system_role WHERE customerId = " + str(
				customer_id) + " AND name = " + "'" + role_add_rtn + "'"
			role_id = self.obj_tools.sql_event(role_id_statement)
			role_id = role_id[0]['id']
			add_user_rtn = self._user_add(hallcode, role_id)
			right_add_username = "SELECT id, userName, password from system_user WHERE hallCode = " + "'" \
									   + hallcode + "'" + " and userName = " + "'" + add_user_rtn + "'"
			user_info = self.obj_tools.sql_event(right_add_username)
		else:
			name = user_info[0]['userName']
			obj_log.info("The customer user %s can add the news...." %(name))
		return user_info[0]
	def _get_FirstCategory(self):
		req_type = 'GET'
		hallCode = "YTSG"
		first_category_rtn = {}
		first_category_list = []
		API_URL = "http://" + self.add + "/api/videosCategory/getFirstCategory"
		token = self.obj_tools.loginYunyun(hallCode="YTSG", username= "lyp", password="123456")
		req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
		if req['status'] == 200:
			obj_log.info('Get first category successfully........')
			first_category = req['data']
			for i in range(len(first_category)):
				first_category_id = first_category[i]['id']
				first_category_rtn[first_category_id] =first_category[i]['name']
		else:
			obj_log.info('Get first category failed.......')
			return False

		return first_category_rtn

	def _get_SecondCategory(self):
		req_type = 'GET'
		hallCode = "YTSG"
		temp_dict = {}
		second_category_rtn = {}
		second_category_temp = []
		second_category_list = []
		first_category_list = self._get_FirstCategory()
		API_URL = "http://" + self.add + "/api/videosCategory/getSecondCategory"
		token = self.obj_tools.loginYunyun(hallCode="YTSG", username= "lyp", password="123456")
		for id in first_category_list.keys():
			second_category_list = []
			temp_dict['id'] = id
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			if req['status'] == 200:
				obj_log.info('Get second category successfully........')
				second_category_temp = req['data']
				for i in range(len(second_category_temp)):
					second_category_id = second_category_temp[i]['id']
					second_category_list.append(second_category_id)
			else:
				obj_log.info('Get second category failed.......')
				return False
			second_category_rtn[id] = second_category_list

		return second_category_rtn

	def _getAllCustomerIdAndName(self):
		'''活动新增，获取单位名称和ID'''
		req_type = 'GET'
		customer_tuple = namedtuple("Customer",["id","name"])
		API_URL = "http://" + self.add + "/api/customer/getAllCustomerIdAndName"
		token = self.obj_tools.loginYunyun()
		req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
		if req['status'] == 200:
			obj_log.info("获取客户ID和名称成功！")
			temp_info = [(temp["id"],temp["name"]) for temp in req["data"]]
		else:
			obj_log.info("获取客户ID和名称失败！")
			return False
		return temp_info

	def _findLibraryNameAndId(self):
		'''活动新增，获取图书馆名称和ID'''
		req_type = 'GET'
		temp_dict = {}
		temp_dict["customerId"] = 0
		# customer_tuple = namedtuple("Customer",["id","name"])
		API_URL = "http://" + self.add + "/api/library/findLibraryNameAndIdByCustomerId"
		token = self.obj_tools.loginYunyun()
		req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
		if req['status'] == 200:
			obj_log.info("获取图书馆ID和名称成功！")
			temp_info = [(temp["id"],temp["name"]) for temp in req["data"]]
		else:
			obj_log.info("获取图书馆ID和名称失败！")
			return False
		return temp_info

	def _getCustomerInfoById(self,customer_id):
		'''通过客户ID获取客户信息'''
		req_type = 'GET'
		temp_dict = {}
		temp_dict["id"] = customer_id
		API_URL = "http://" + self.add + "/api/customer/getCustomer"
		token = self.obj_tools.loginYunyun()
		req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
		if req['status'] == 200:
			obj_log.info("获取客户信息成功！")
		else:
			obj_log.info("获取客户信息失败，请检查是否为客户代码！")
			return False
		return req['data']

	def _getLibraryInfoById(self,library_id):
		'''通过图书馆ID获取图书馆详情'''
		req_type = 'GET'
		temp_dict = {}
		temp_dict["id"] = library_id
		API_URL = "http://" + self.add + "/api/library/getLibrary"
		token = self.obj_tools.loginYunyun()
		req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
		if req['status'] == 200:
			obj_log.info("获取图书馆信息成功！")
		else:
			obj_log.info("获取图书馆信息失败！")
			return False
		return req['data']

	def _getCustomerInfoByHallcode(self,hallCode):
		'''通过hallCode获取客户信息.
		:param hallCode : 客户代码
		:rtype : dict
		'''
		sql_statement = '''SELECT * from system_customer WHERE hallCode = "''' + str(hallCode) + '''"'''
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]

	def _getLibraryInfoByHallcode(self,hallCode):
		'''通过hallCode获取图书馆信息.
		:param hallCode : 馆号
		:rtype : dict
		'''
		sql_statement = '''SELECT * from librarys WHERE hallCode = "''' + str(hallCode) + '''"'''
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]

class Multi_new_add(threading.Thread):
	def __init__(self, hallcode, type, is_need_review):
		threading.Thread.__init__(self)
		self.hallcode = hallcode
		self.type = type
		self.is_need_review = is_need_review
		self.ret = ''
	def run(self):
		# self.ret = Runner._new_add(self.hallcode, self.type, self.is_need_review)
		self.ret = obj_runner._new_add(self.hallcode, self.type, self.is_need_review)
	def get_return(self):
		return self.ret

def multi_new_add(hallcode_list, type="2", is_need_review=0):
	thread_list = []
	for hallcode in hallcode_list:
		t = Multi_new_add(hallcode, type, is_need_review)
		thread_list.append(t)

	for thread in thread_list:
		thread.start()

	for thread in thread_list:
		thread.join()

	for thread in thread_list:
		ret = thread.get_return()
		if ret == False:
			return False
	return True



