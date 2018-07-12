# -*- coding=utf-8 -*-
import utils,runner,log,time,json,simplejson
# obj_tools = utils.Tools()
obj_log = log.get_logger()
isbn_list = {'A': '9787308156417', 'B': '9787516143261', 'C': '9787509745816', 'D': '9787040213607', 'E': '9787509755280', 'F': '9787516410790', 'G': '9787561466584',
			 'H': '9787561460207', 'I': '9787108032911', 'J': '9787561460232', 'K': '9787509748985','N': '9787030334282', 'O': '9787513535663', 'P': '9787500672012',
			 'Q': '9787502554774', 'R': '9787200008715', 'S': '9787030323859', 'T': '9787121212437', 'U': '9787111465300', 'V': '9787515901701', 'X': '9787511107633',
			 'Z': '9787500086062', 'Test_null': '123456789'}
class Test_case(runner.Runner):
	def __init__(self, all_config):
		runner.Runner.__init__(self, all_config)
		self.obj_tools = utils.Tools()
	# 资讯新增 hallcode：客户代码 is_need_review：是否需要审核（0:需要 1：不需要）
	def new_add(self, hallcode='', type="2", is_need_review=0):
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
		for i in range(len(newAreaDtos_info)):
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
				if i > 0:
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
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			print req
			if req['status'] == 200:
				obj_log.info('Add new successfully........')
			else:
				obj_log.info('Add new failed.......')
				return False
		# 获取资讯ID
		get_newId_statement = "SELECT id FROM system_news WHERE sourceId = " + str(
			temp_dict['sourceId']) + " and title = '" + temp_dict['title'] + "'"
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
	def movie_upload(self):
		req_type = "PUT"
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		get_categoryId = self._get_SecondCategory()
		print get_categoryId
		temp_dict = {}
		videosChapterDtos_list = []
		videosSectionDtos_list = []
		for k in range(1,3):
			videosChapterDtos_rtn = {}
			videosChapterDtos_rtn['sortNum'] = k
			videosChapterDtos_rtn['name'] = "第" + str(k) + "章"
			videosChapterDtos_rtn['isParashow'] = "true"
			for i in range(1,3):
				videosSectionDtos_rtn = {}
				videosSectionDtos_rtn['name'] = "第" + str(k) + "章" +  "第" + str(i) + "节"
				videosSectionDtos_rtn['sortNum'] = i
				videosSectionDtos_rtn['videoName'] = "第" + str(k) + "章" +  "第" + str(i) + "节" + "视频"
				videosSectionDtos_rtn['videoPath'] = "video/9/7/1531382433997.mp4"
				videosSectionDtos_rtn['videoSize'] = 58707397
				videosSectionDtos_rtn['videoTime'] = "200"
				videosSectionDtos_rtn['isupload'] = "true"
				videosSectionDtos_list.append(videosSectionDtos_rtn)
			videosChapterDtos_rtn['videosSectionDtos'] = videosSectionDtos_list

			videosChapterDtos_list.append(videosChapterDtos_rtn)

		temp_dict['videosChapterDtos'] = videosChapterDtos_list
		temp_dict['videosStatus'] = {"index":3}
		temp_dict['firstCategoryId'] = 1
		temp_dict['secondCategoryId'] = 34
		temp_dict['name'] = "视频名称" + now_time
		temp_dict['startTime'] = "2018-7-12"
		temp_dict['endTime'] = "2019-7-12"
		temp_dict['author'] = "lyp"
		temp_dict['content'] = "视频介绍" + now_time
		image_temp = self.obj_tools.get_imgbas64(r"C:\Users\Administrator\Desktop\APP\11.png")
		temp_dict['image'] = "data:image/png;base64," + image_temp

		API_URL = "http://" + self.add + "/api/videos/save"
		token = self.obj_tools.loginYunyun(hallCode="YTSG", username="lyp", password="123456")
		req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
		if req['status'] == 200:
			obj_log.info('Add new successfully........')
		else:
			obj_log.info('Add new failed.......')
			return False
		return True

