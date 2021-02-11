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
	columns = get_columns(filters)
	#print "columns",columns
	non_process_colum_name_list = ["item_code","manufacturing_method"]

	item_list = [ ]
	if filters:
		item_list =[filters.get("item_filter") ]
	else:
		item_list = get_all_items_list()
		#print "sur_len",len(item_list)



	non_process_colum_name_list = ["item_code", "manufacturing_method"]

	for item in item_list :
		#print "sur_item",item

		method_name = frappe.db.get_value("Pch Manufacturing Method Child", {"item_made": item}, "parent")
		process_list_for_item = get_process_ac_to_item(item)
		#print "item--- : ",item,"--process_list",process_list_for_item
		item_process_column_key_list = get_item_process_column_key_list(process_list_for_item)

		parent_row_dic = {"item_code": item,"manufacturing_method":method_name}

		item_row_pass_through_data = get_item_row_pass_through_data(item,method_name,process_list_for_item,item_process_column_key_list)   #later bind row heading here

		for column in columns:
			if column.get("fieldname") not in non_process_colum_name_list:
				process_column_key = column.get("fieldname")
				if item_row_pass_through_data.get(process_column_key):
					process_temp_dic =  {process_column_key:item_row_pass_through_data.get(process_column_key)}
					parent_row_dic.update(process_temp_dic)

		data.append(parent_row_dic)

	return columns, data

#for single item column names will be choosed according to item choosed ,choosen item will be querying against manufacture method child doc to fetch method name
#fetched method will be qerying against mmd to get unique processs (asumming each item has one method)
def get_columns(filters):
	columns = []
	process_list = get_process_list(filters)  #for single item
	#print "process_list",process_list


	range_temp = 2 + (len(process_list) * 3)

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
	"label": "Manufacturing Method",
	"fieldname": "manufacturing_method",
	"options":"Pch Manufacturing Method",
	"fieldtype": "Link",
	"width": 160
	}
	last_col = 1

	for process in process_list:
		PROCESS_LABEL = process
		outbound_label = PROCESS_LABEL + SPACE + OUTBOUND_SUFFIX
		karigar_label =  PROCESS_LABEL + SPACE + KARIGAR_SUFFIX
		inbound_label =  PROCESS_LABEL + SPACE + INBOUND_SUFFIX
		columns[last_col + 1] = {
			"label": outbound_label,
			"fieldname": outbound_label,
			"width": 160
		}
		last_col += 1

		columns[last_col + 1] = {
			"label": karigar_label,
			"fieldname": karigar_label,
			"width": 160
		}
		last_col += 1

		columns[last_col + 1] = {
			"label": inbound_label,
			"fieldname": inbound_label,
			"width": 160
		}
		last_col += 1
	#print "columns",columns
	return columns

def  get_process_ac_to_item(item) :
	method_name = frappe.db.get_value("Pch Manufacturing Method Child", {"item_made": item},"parent")
	#print "method_name", method_name
	process_dic = frappe.db.sql("""select DISTINCT pch_process  from `tabPch Manufacturing Method Details` where pch_method=%s  order by process_order """,(method_name), as_dict=1)
	process_list = []
	for process in process_dic:
		process_list.append(process["pch_process"])
	return process_list


#for single item
def get_process_list( filters ):
	process_list = []
	if filters:
		#print "filters",filters
		process_list = get_process_ac_to_item(filters.get("item_filter"))
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

#prepare process label as key value as data here
def get_item_row_pass_through_data(item,method_name,process_list_for_item,item_process_column_key_list):
	#print "item", item
	#print "method_name", method_name
	#print "item_process_column_key_list",item_process_column_key_list
	mrec_dic = frappe.db.sql("""
				SELECT 
			    manufacturing_record_type,units_s_r, start_process ,end_process 
				FROM
			    `tabPch Manufacturing Record`
				WHERE
				item_made = %s and manufacturing_method = %s and docstatus = 1 
				ORDER BY 
				creation asc""",
				(item, method_name ), as_dict=1)

	# from process_column_bind_list i will get data all column names along with process asingned for that column
	is_differend_end_process = 0
	process_wise_data_dics = {}
	#print "mrec_dic", mrec_dic
	for mrec in mrec_dic :
		start_process_karigar_key = get_process_name(mrec.get("start_process")) + SPACE + KARIGAR_SUFFIX
		end_process_karigar_key = get_process_name(mrec.get("end_process")) + SPACE + KARIGAR_SUFFIX
		end_process_inbound_key = get_process_name(mrec.get("end_process")) + SPACE + INBOUND_SUFFIX
		end_process_outbound = get_process_name(mrec.get("end_process")) + SPACE + OUTBOUND_SUFFIX

		if mrec.get("manufacturing_record_type") in [ "Send Material for Manufacturing","Receive Material from Manufacturing"]:
			if is_differend_end_process in [0, 1]:
				if mrec.get("start_process") == mrec.get("end_process"):
					is_differend_end_process = 0
					if mrec.get("manufacturing_record_type") == "Send Material for Manufacturing":
						process_wise_data_dics[start_process_karigar_key] = mrec.get("units_s_r")
					elif mrec.get("manufacturing_record_type") == "Receive Material from Manufacturing":
						process_wise_data_dics[end_process_inbound_key] = mrec.get("units_s_r")
				else:
					#print "start =/ end process else"
					is_differend_end_process = 1
					if mrec.get("manufacturing_record_type") == "Send Material for Manufacturing":
						process_wise_data_dics[start_process_karigar_key] = mrec.get("units_s_r")
					elif mrec.get("manufacturing_record_type") == "Receive Material from Manufacturing":  # end process inbound
						process_wise_data_dics[end_process_inbound_key] = mrec.get("units_s_r")
						in_between_s_and_e_process_data = get_in_between_s_and_e_process_data(start_process_karigar_key,end_process_inbound_key,item_process_column_key_list,mrec.get("units_s_r"))
						process_wise_data_dics.update(in_between_s_and_e_process_data)
						#print "in_between_s_and_e_process_data", in_between_s_and_e_process_data

		elif mrec.get("manufacturing_record_type") == "Send Materials to Internal Storage WH" :
				process_wise_data_dics[end_process_outbound] = mrec.get("units_s_r")
	#print "process_wise_data_dics",process_wise_data_dics
	return  process_wise_data_dics


def get_process_name(mmd_id):
	method_name = frappe.db.get_value("Pch Manufacturing Method Details", {"name": mmd_id}, "pch_process")
	return method_name

def get_item_process_column_key_list(process_list_for_item):
	item_process_column_key_list = []
	for process in process_list_for_item:
		PROCESS_LABEL = process
		#print "PROCESS_LABEL",PROCESS_LABEL
		outbound_label = PROCESS_LABEL + SPACE + OUTBOUND_SUFFIX
		item_process_column_key_list.append(outbound_label)

		karigar_label =  PROCESS_LABEL + SPACE + KARIGAR_SUFFIX
		item_process_column_key_list.append(karigar_label)

		inbound_label =  PROCESS_LABEL + SPACE + INBOUND_SUFFIX
		item_process_column_key_list.append(inbound_label)
	return item_process_column_key_list

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

