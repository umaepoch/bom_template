# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	process_list = get_process_list(filters.get("method_filter"))
	columns = get_columns(process_list)

	mrec_data = get_mrec_data(filters)
	for item_made, item_json in mrec_data.items():
		parent_row_dic = {"item_made_temp": item_made}

		#dynmic col data
		for process in process_list :
			outbound_label = process + " " + "Outbound"
			karigar_label = process + " " + "Karigar"
			inbound_label = process + " " + "Inbound"
			if item_json.get(process):
				for process_wise_rec_data_list in item_json.get(process):
					if process_wise_rec_data_list.get("manufacturing_record_type") == "Send Material for Manufacturing":
						process_dic = {
							"manufacturing_method": process_wise_rec_data_list.get("manufacturing_method"),
							outbound_label: process_wise_rec_data_list.get("units_s_r"),
							karigar_label: process_wise_rec_data_list.get("units_s_r")
						}
						parent_row_dic.update(process_dic)
					elif process_wise_rec_data_list.get("manufacturing_record_type") == "Receive Material from Manufacturing":
						process_dic = {
							inbound_label: process_wise_rec_data_list.get("units_s_r")
						}
						parent_row_dic.update(process_dic)
		data.append(parent_row_dic)
		#dynmic col data

	return columns, data

def get_columns(process_list):
	columns = []
	range_temp = 2 + (len(process_list) * 3)

	for col in range(range_temp):
		columns.append("")


	columns[0] = {
	"label": "Item Made",
	"fieldname": "item_made_temp",
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

	for process in process_list :
		outbound_label = process + " " + "Outbound"
		karigar_label =  process + " " + "Karigar"
		inbound_label =  process + " " + "Inbound"
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

def get_mrec_data(filters):
	if filters.get("item_made_fil"):
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.units_s_r,mrec.manufacturing_record_type,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mmd.pch_process,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and mrec.item_made = %s  and mmd.name = mrec.start_process order by mmd.process_order """, (filters.get("item_made_fil")), as_dict=1)
	else:
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.units_s_r,mrec.manufacturing_record_type,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mmd.pch_process,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1   and mmd.name = mrec.start_process order by mmd.process_order """, as_dict=1)

	mrec_json = {}   #{"item1":{"process1":[query_data,query_data], "process2":[query_data,query_data] }}
	for mrec in mrec_data :
		if mrec_json.get(mrec["item_made"]):
			#print "item_name-",mrec["item_made"],"-----", "process_name : ",mrec["start_process"]
			if mrec_json.get(mrec["item_made"]).get(mrec["pch_process"]): #if process key exist
				process_temp_dic = mrec_json.get(mrec["item_made"])
				mrec_json[mrec["item_made"]][mrec["pch_process"]].append(mrec)
			else: #if process key  doest exist but other process exist
				process_dic = {mrec.get("pch_process"): [mrec]}
				mrec_json[mrec["item_made"]].update(process_dic)
		else: #no processes exist
			process_dic ={mrec.get("pch_process"): [mrec] }
			mrec_json[mrec["item_made"]]= process_dic
	#print "mrec_json",mrec_json

	return mrec_json

def get_conditions(filters):
    conditions = ""
    if filters.get("item_made_fil"):
        conditions += " and mrec.item_made = %s" % frappe.db.escape(filters.get("mrec"), percent=False)
    return conditions
def get_stock_qty_in_wh(item_code,wh):
    stock_qty_in_wh = frappe.db.sql("""select actual_qty  from `tabBin` where item_code=%s and warehouse= %s""", (item_code,wh), as_dict=1)
    return stock_qty_in_wh[0]["actual_qty"] if  stock_qty_in_wh else 0

def get_process_list(method_name):
	process_dic = frappe.db.sql("""select DISTINCT pch_process  from `tabPch Manufacturing Method Details` where pch_method=%s  order by process_order """,(method_name), as_dict=1)
	process_list = []
	for process in process_dic:
		process_list.append(process["pch_process"])
	return process_list

@frappe.whitelist()
def get_method_based_on_item(item_made):
	method_list=frappe.db.sql("""select parent from `tabPch Manufacturing Method Child` where item_made=%s""",(item_made),as_dict=1);
	methods=[];
	length=len(method_list);
	if(length==1):
		methods.append(method_list[0]["parent"]);
	else:
		for method in method_list:
			methods.append(method.parent);
	#print(methods);
	return methods