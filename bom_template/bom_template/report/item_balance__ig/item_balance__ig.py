# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

OUTBOUND_SUFFIX = "Outbound"
KARIGAR_SUFFIX = "Karigar"
INBOUND_SUFFIX = "Inbound"
SPACE =   " "


def execute(filters=None):
	columns, data = [], []


	#items_code_start
	item_list = []
	if filters.get("group_wise") == "Item":
		columns = get_columns(filters)
		if filters and filters.get("item_filter"):
			item_list = [filters.get("item_filter")]
		else:
			item_list = get_all_items_list()
		# print "sur_len",len(item_list)
		for item in item_list:
			# print "sur_item",item
			item_row_pass_through_data = get_item_row_pass_through_data(item)  # forming item ow day data for all procces 3 wh
			data.append(item_row_pass_through_data)


	if filters.get("group_wise") == "Item Group":
		columns = get_columns(filters)
		item_group_list = []
		if filters and filters.get("ig_filter"):
			item_group_list = [filters.get("ig_filter")]
		else:
			item_group_list = get_all_item_group_list()
		# print "sur_len",len(item_list)


		for item_group in item_group_list:
			item_group_row_pass_through_data = get_item_group_row_pass_through_data(item_group)
			data.append(item_group_row_pass_through_data)

	return columns, data

#for single item column names will be choosed according to item choosed ,choosen item will be querying against manufacture method child doc to fetch method name
#fetched method will be qerying against mmd to get unique processs (asumming each item has one method)
def get_columns(filters):
	columns = []
	column_process_list = get_process_list_for_columns(filters)  #for single item
	column_keys_list = get_process_column_key_list (column_process_list)

	range_temp = 3 + (len(column_keys_list) )

	for col in range(range_temp):
		columns.append("")


	columns[0] = {
	"label": "Item",
	"fieldname": "item_code",
	"options":"Item",
	"fieldtype": "Link",
	"width": 160
	}
	columns[1] = {
		"label": "Item Group",
		"fieldname": "item_group",
		"options": "Item Group",
		"fieldtype": "Link",
		"width": 160
	}
	columns[2] = {
		"label": "Manufacturing Method",
		"fieldname": "manufacturing_method",
		"options": "Pch Manufacturing Method",
		"fieldtype": "Link",
		"width": 160
	}
	last_col = 2

	for column_key in column_keys_list:

		columns[last_col + 1] = {
			"label": column_key,
			"fieldname": column_key,
			"width": 160
		}
		last_col += 1

	#print "columns",columns
	return columns

#return processes in process order ac to item from Pch Manufacturing Method Details
def  get_process_ac_to_item(item) :
	method_name = frappe.db.get_value("Pch Manufacturing Method Child", {"item_made": item},"parent")
	#print "method_name", method_name
	process_dic = frappe.db.sql("""select DISTINCT pch_process  from `tabPch Manufacturing Method Details` where pch_method=%s  order by process_order """,(method_name), as_dict=1)
	process_list = []
	for process in process_dic:
		process_list.append(process["pch_process"])
	return process_list

#return processes from glbal processes doctype where item_group is input
def get_process_ac_to_item_group(item_group):
	process_dic = frappe.db.sql("""
			SELECT 
		    gpc.pch_process,gpc.pch_process_order
			FROM
		    `tabPch Global Process Child` gpc,`tabPch Global Process` gp
		    WHERE
		    gp.item_group= %s  and gp.name = gpc.parent
			order by 
			gpc.pch_process_order; """,(item_group), as_dict=1)

	process_list = []
	for process in process_dic:
		process_list.append(process["pch_process"])
	return process_list




#for single item
def get_process_list_for_columns( filters ):
	process_list = []
	if filters.get("group_wise") == "Item":
		if filters.get("item_filter"):
			process_list = get_process_ac_to_item(filters.get("item_filter"))  # for one item
		else:
			process_list = get_global_process_order_list()

	if filters.get("group_wise") == "Item Group":
		if  filters.get("ig_filter"):
			process_list = get_process_ac_to_item_group(filters.get("ig_filter"))  
		else:
			process_list = get_global_process_order_list()

	return process_list

def get_global_process_order_list():
	process_dic = frappe.db.sql("""
		SELECT 
	    gpc.pch_process,gpc.pch_process_order
		FROM
	    `tabPch Global Process Child` gpc,`tabPch Global Process` gp
	    WHERE
	    gp.is_global=1  and gp.name = gpc.parent
		order by 
		gpc.pch_process_order; """, as_dict=1)

	process_list=[]
	for process in process_dic:
		process_list.append(process["pch_process"])
	return process_list

def get_item_group_mrec_data(item_group,process_name):
	mrec_dic = frappe.db.sql("""
			SELECT 
		    sum(units_s_r) as sum_units_s_r
			FROM
		    `tabPch Manufacturing Record`
			WHERE
			item_group=%s and start_process=(select name from `tabPch Manufacturing Method Details` where  pch_process =%s and item_group_mmd = %s limit 1); """, (item_group,process_name,item_group),as_dict=1)
	#print "mrec_dic",mrec_dic

	return mrec_dic[0]["sum_units_s_r"]  if mrec_dic[0]["sum_units_s_r"] else "NO DATA"

#code here
#prepare process label as key value as data here
def get_item_row_pass_through_data(item):
	method_name = frappe.db.get_value("Pch Manufacturing Method Child", {"item_made": item}, "parent")
	process_list_for_item = get_process_ac_to_item(item)
	item_process_column_key_list = get_process_column_key_list(process_list_for_item)
	parent_row_dic = {"item_code": item, "manufacturing_method": method_name}



	#supplier.
	#find distinct supplier
	mrec_sup_dic = frappe.db.sql("""
					SELECT 
				    DISTINCT sub_contractor
					FROM
				    `tabPch Manufacturing Record`
					WHERE
					item_made = %s and manufacturing_method = %s and docstatus = 1 
					""",
					(item, method_name), as_dict=1)

	supplier_list = []

	for mrec in mrec_sup_dic:
		supplier_list.append(mrec["sub_contractor"])

	all_supplier_item_row_data_list = []
	#calculate item row for each supplier
	for supplier in supplier_list :
		item_row_pass_through_data_ac_to_supplier = get_item_row_pass_through_data_ac_to_supplier(item, method_name,item_process_column_key_list,supplier)
		all_supplier_item_row_data_list.append(item_row_pass_through_data_ac_to_supplier)

	item_supplier_total_process_wise_data_dics = {}  # this dic contains sum of all supplier keys
	for item_process_key in item_process_column_key_list:
		for item_row_data in all_supplier_item_row_data_list: #each supplier row item row dic
			if item_row_data.get(item_process_key):
				if item_supplier_total_process_wise_data_dics.get(item_process_key):
					item_supplier_total_process_wise_data_dics[item_process_key] += item_row_data.get(item_process_key)
				else:
					item_supplier_total_process_wise_data_dics[item_process_key] = item_row_data.get(item_process_key)


	parent_row_dic.update(item_supplier_total_process_wise_data_dics)

	return parent_row_dic




def get_item_row_pass_through_data_ac_to_supplier(item,method_name,item_process_column_key_list,supplier):

	mrec_dic = frappe.db.sql("""
					SELECT 
				    manufacturing_record_type,units_s_r, start_process ,end_process ,item_group,sub_contractor
					FROM
				    `tabPch Manufacturing Record`
					WHERE
					item_made = %s and manufacturing_method = %s and sub_contractor =%s and docstatus = 1 
					ORDER BY 
					creation asc""",
					(item, method_name,supplier), as_dict=1)

	# from process_column_bind_list i will get data all column names along with process asingned for that column
	is_differend_end_process = 0
	process_wise_data_dics = {}

	# print "mrec_dic", mrec_dic
	for mrec in mrec_dic:
		process_wise_data_dics["item_group"] = mrec.get("item_group")
		start_process_karigar_key = get_process_name(mrec.get("start_process")) + SPACE + KARIGAR_SUFFIX
		end_process_karigar_key = get_process_name(mrec.get("end_process")) + SPACE + KARIGAR_SUFFIX
		end_process_inbound_key = get_process_name(mrec.get("end_process")) + SPACE + INBOUND_SUFFIX
		end_process_outbound = get_process_name(mrec.get("end_process")) + SPACE + OUTBOUND_SUFFIX

		if mrec.get("manufacturing_record_type") in ["Send Material for Manufacturing",
													 "Receive Material from Manufacturing"]:
			if is_differend_end_process in [0, 1]:
				if mrec.get("start_process") == mrec.get("end_process"):
					is_differend_end_process = 0
					if mrec.get("manufacturing_record_type") == "Send Material for Manufacturing":
						process_wise_data_dics[start_process_karigar_key] = mrec.get("units_s_r")
					elif mrec.get("manufacturing_record_type") == "Receive Material from Manufacturing":
						process_wise_data_dics[end_process_inbound_key] = mrec.get("units_s_r")
				else:
					# print "start =/ end process else"
					is_differend_end_process = 1
					if mrec.get("manufacturing_record_type") == "Send Material for Manufacturing":
						process_wise_data_dics[start_process_karigar_key] = mrec.get("units_s_r")
					elif mrec.get(
							"manufacturing_record_type") == "Receive Material from Manufacturing":  # end process inbound
						process_wise_data_dics[end_process_inbound_key] = mrec.get("units_s_r")
						in_between_s_and_e_process_data = get_in_between_s_and_e_process_data(start_process_karigar_key,
																							  end_process_inbound_key,
																							  item_process_column_key_list,
																							  mrec.get("units_s_r"))
						process_wise_data_dics.update(in_between_s_and_e_process_data)
				# print "in_between_s_and_e_process_data", in_between_s_and_e_process_data

		elif mrec.get("manufacturing_record_type") == "Send Materials to Internal Storage WH":
			process_wise_data_dics[end_process_outbound] = mrec.get("units_s_r")
	# print "process_wise_data_dics",process_wise_data_dics

	#print "supplier : ", supplier,"row data- ",process_wise_data_dics


	return process_wise_data_dics


def get_item_group_row_pass_through_data(item_group) :
	parent_ig_row_dic = {"item_group":item_group}

	process_list_for_item_group = get_process_ac_to_item_group(item_group)  # each item group have one process order defined
	item_group_process_column_key_list = get_process_column_key_list(process_list_for_item_group)

	item_list_ac_to_item_group = get_item_list_ac_to_item_group(item_group)

	item_row_data_list = [] #we will get list of all calculated item row data per item group here
	for  item in item_list_ac_to_item_group:
		item_row_pass_through_data = get_item_row_pass_through_data(item)
		item_row_data_list.append(item_row_pass_through_data)

	ig_process_wise_data_dics = {} #this dic contains some of all col keys values across all item in that item group
	for ig_process_key in item_group_process_column_key_list : #ig_col_key loop
		for item_row_data in item_row_data_list : # each item row key
			if item_row_data.get(ig_process_key):
				if ig_process_wise_data_dics.get(ig_process_key):
					ig_process_wise_data_dics[ig_process_key] += item_row_data.get(ig_process_key)
				else:
					ig_process_wise_data_dics[ig_process_key] = item_row_data.get(ig_process_key)


	parent_ig_row_dic.update(ig_process_wise_data_dics)
	return parent_ig_row_dic

def get_process_name(mmd_id):
	method_name = frappe.db.get_value("Pch Manufacturing Method Details", {"name": mmd_id}, "pch_process")
	return method_name

def get_process_column_key_list(process_list):
	process_column_key_list = []
	for process in process_list:
		PROCESS_LABEL = process
		#print "PROCESS_LABEL",PROCESS_LABEL
		outbound_label = PROCESS_LABEL + SPACE + OUTBOUND_SUFFIX
		process_column_key_list.append(outbound_label)

		karigar_label =  PROCESS_LABEL + SPACE + KARIGAR_SUFFIX
		process_column_key_list.append(karigar_label)

		inbound_label =  PROCESS_LABEL + SPACE + INBOUND_SUFFIX
		process_column_key_list.append(inbound_label)
	return process_column_key_list

def get_in_between_s_and_e_process_data(start_process_karigar_key,end_process_inbound_key,item_process_column_key_list,units_s_r) :
	temp_dic={}
	isvalid= 0
	for column_key  in item_process_column_key_list :
		if column_key == end_process_inbound_key:
			isvalid = 0
			break
		if isvalid ==0 :
			if column_key == start_process_karigar_key:
				isvalid = 1
		else: #if start process column key comes
			t_dic = {column_key: units_s_r}
			temp_dic.update(t_dic)
	return temp_dic

def get_all_items_list():

	mrec_dic = frappe.db.sql("""
					SELECT 
				    DISTINCT item_made 
					FROM
				    `tabPch Manufacturing Record`
					WHERE
					docstatus = 1 and  item_made IS NOT NULL
					ORDER BY 
					creation desc""",
					 as_dict=1)
	item_list = []

	for mrec in mrec_dic:
		item_list.append(mrec["item_made"])
	return item_list

def get_all_item_group_list():

	mrec_dic = frappe.db.sql("""
					SELECT 
				    DISTINCT item_group 
					FROM
				    `tabPch Manufacturing Record`
					WHERE
					docstatus = 1 and  item_made IS NOT NULL and item_group IS NOT NULL
					ORDER BY 
					creation desc""",
					 as_dict=1)
	item_list = []

	for mrec in mrec_dic:
		item_list.append(mrec["item_group"])
	return item_list

def get_item_list_ac_to_item_group(item_group):
	mrec_dic = frappe.db.sql("""
						SELECT 
					    DISTINCT item_made 
						FROM
					    `tabPch Manufacturing Record`
						WHERE
						docstatus = 1 and  item_made IS NOT NULL and item_group = %s
						ORDER BY 
						creation desc""",
							 (item_group), as_dict=1)

	item_list = []
	for mrec in mrec_dic:
		item_list.append(mrec["item_made"])
	return item_list
