# -*- coding=utf-8 -*-
import utils,time,log,re,sys,json,simplejson,random,requests,threading
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
		req_type = 'POST'
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
		login_info = self.obj_tools.sql_event(sql_statement)
		admin_customer_password = login_info[0]['password']
		admin_customer_username = login_info[0]['userName']
		token = self.obj_tools.loginYunyun(hallcode, admin_customer_username, admin_customer_password)
		temp_dict = {}
		currentUserId_statement = "SELECT id from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
		currentUserId_info = self.obj_tools.sql_event(currentUserId_statement)
		currentUserId = currentUserId_info[0]['id']
		temp_dict['currentUserId'] = currentUserId
		temp_dict['name'] = hallcode + '-name-' + now_time
		temp_dict['description'] = hallcode + '-desc-' + now_time
		temp_dict['menuIds'] = ["15","16","37"]
		API_URL = "http://" + self.add + "/api/roleMenu/saveRoleMenu"
		req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
		if req['status'] == 200:
			obj_log.info('Add role {} successfully........'.format(temp_dict['name']))
		else:
			obj_log.info('Add role {} failed.......'.format(temp_dict['name']))
			return False

		return temp_dict['name']

	def _user_add(self, hallcode, role_id):
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
		temp_dict['userName'] = hallcode + '-new-' + now_time
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
		API_URL = "http://" + self.add + "/api/image/uploadImageSaveOrUpdate"
		files = {'fileImage': ("11.png", open(r'C:\Users\Administrator\Desktop\APP\11.png', 'rb'), 'image/png')}
		obj_log.info('Upload image start.......')
		req = requests.post(API_URL, files=files)
		if req.status_code == 200:
			obj_log.info('Upload image successfully.......')
		else:
			obj_log.info('Upload image failed.......')
			return False
		rtn_temp = req.text
		rtn = json.loads(rtn_temp)
		return rtn['data']

	def _new_audited(self, new_id):
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

	def _get_customer_user_info(self, hallcode):
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
				if 15L in power_list:
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

	# 资讯新增 hallcode：客户代码 is_need_review：是否需要审核（0:需要 1：不需要）
	def _new_add(self, hallcode='', type="2", is_need_review=0):
		req_type = "PUT"
		hallcode = hallcode.upper()
		temp_dict = {}
		new_AreaDtos_list = []
		new_AreaDtos_rtn = {}
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		get_customer_statement = "SELECT hallCode from system_customer WHERE id = (SELECT customerId from librarys WHERE hallCode = '" + hallcode + "')"
		hallcode_temp = self.obj_tools.sql_event(get_customer_statement)
		customer_code = hallcode_temp[0]['hallCode']
		# 单位资讯
		if type == "2":
			obj_log.info('Add new customer start................')

			sql_statement = "SELECT provinceCode,cityCode,areaCode FROM system_customer WHERE hallCode = " + "'" + hallcode + "'"
			customer_info_statement = "SELECT id, name from system_customer WHERE hallCode = " + "'" + hallcode + "'"
		# 图书馆资讯
		if type == "3":
			obj_log.info('Add new library start................')
			library = hallcode
			sql_statement = "SELECT provinceCode,cityCode,areaCode FROM librarys WHERE hallCode = " + "'" + library + "'"
			customer_info_statement = "SELECT id, name from librarys WHERE hallCode = " + "'" + library + "'"
		# 获取 newAreaDtos

		customer_info = self.obj_tools.sql_event(customer_info_statement)
		newAreaDtos_info = self.obj_tools.sql_event(sql_statement)
		areaAddress_container = ""
		for i in  range(len(newAreaDtos_info)):
			new_AreaDtos_rtn['province'] = newAreaDtos_info[i]['provinceCode']
			if newAreaDtos_info[i]['cityCode'] is None:
				new_AreaDtos_rtn['city'] = "all"
			else:
				new_AreaDtos_rtn['city'] = newAreaDtos_info[i]['cityCode']

			if newAreaDtos_info[i]['areaCode'] is None:
				new_AreaDtos_rtn['area'] = "all"
			else:
				new_AreaDtos_rtn['area'] = newAreaDtos_info[i]['areaCode']
			new_AreaDtos_list.append(new_AreaDtos_rtn)
			temp_dict['newAreaDtos'] = new_AreaDtos_list
			print temp_dict['newAreaDtos']
			if newAreaDtos_info[i]['cityCode'] is None:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				if i > 0 :
					areaAddress_container = areaAddress_container + "," + province_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name
					areaAddress_container = province_name
			elif newAreaDtos_info[0]['cityCode'] is not None and newAreaDtos_info[0]['areaCode'] is None:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				city_statement = "SELECT name FROM system_city WHERE code = " + new_AreaDtos_rtn['city']
				city_name = self.obj_tools.sql_event(city_statement)
				city_name = city_name[0]['name']
				if i > 0:
					areaAddress_container = areaAddress_container + "," + province_name + city_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name + city_name
					areaAddress_container = province_name + city_name

			else:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				city_statement = "SELECT name FROM system_city WHERE code = " + new_AreaDtos_rtn['city']
				city_name = self.obj_tools.sql_event(city_statement)
				city_name = city_name[0]['name']
				area_statement = "SELECT name FROM system_area WHERE code = " + new_AreaDtos_rtn['area']
				area_name = self.obj_tools.sql_event(area_statement)
				area_name = area_name[0]['name']

				if i > 0:
					areaAddress_container = areaAddress_container + "," + province_name + city_name + area_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name + city_name + area_name
					areaAddress_container = province_name + city_name + area_name
		print temp_dict['areaAddress']
		# 获取 当前用户ID-currentUserId
		get_add_user = self._get_customer_user_info(customer_code)
		temp_dict['currentUserId'] = get_add_user['id']
		temp_dict['hight'] = '571'
		# 图片上传
		image_info = self._upload_image()
		temp_dict['image'] = image_info['fileName']
		temp_dict['previemImage'] = image_info['base64']
		# 资讯来源
		temp_dict['source'] = customer_info[0]['name']
		temp_dict['sourceId'] = customer_info[0]['id']
		# temp_dict['timestamp'] = ''
		temp_dict['title'] = '标题-' + now_time
		temp_dict['content'] = "<p>" + "内容-" + now_time + "</p>"
		temp_dict['type'] = type
		temp_dict['width'] = '1470'
		temp_dict['x'] = '0'
		temp_dict['y'] = '150'
		temp_dict['objVal'] = temp_dict['areaAddress']

		API_URL = "http://" + self.add + "/api/news/newAdd"
		if type == "1":
			obj_log.info("We will add the platform news......")

		else:
			add_customer_username = get_add_user['userName']
			add_customer_password = get_add_user['password']
			token = self.obj_tools.loginYunyun(customer_code, add_customer_username, add_customer_password)
			req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
			if req['status'] == 200:
				obj_log.info('Add new successfully........')
			else:
				obj_log.info('Add new failed.......')
				return False
		# 获取资讯ID
		get_newId_statement = "SELECT id FROM system_news WHERE sourceId = " + str(temp_dict['sourceId']) + " and title = '" + temp_dict['title'] + "'"
		new_id = self.obj_tools.sql_event(get_newId_statement)
		new_id = new_id[0]['id']
		# 资讯审核
		if is_need_review == 0:
			obj_log.info("The new is a customer_news,we need customer user audited it.....")
			sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + customer_code + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			admin_customer_password = login_info[0]['password']
			admin_customer_username = login_info[0]['userName']
			token = self.obj_tools.loginYunyun(customer_code, admin_customer_username, admin_customer_password)
			obj_log.info("News audited start...... ")
			new_audited_rtn = self._new_audited(new_id)
		return True

	def _new_add_city(self):
		return True
	def _new_add_province(self):
		return True
obj_runner = Runner()
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


