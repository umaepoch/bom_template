# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	mrec_data = get_mrec_data(filters)
	process_list = ["Rakhi Making","Stone Fitting","Geenth","Packing"]
	for item_made, item_json in mrec_data.items():
		parent_row_dic = {"item_made_temp": item_made}

		for process_wise_rec_data_list in item_json.get("Rakhi Making"):
			if process_wise_rec_data_list.get("manufacturing_record_type") == "Send Material for Manufacturing" :
				process_dic = {
					"manufacturing_method":process_wise_rec_data_list.get("manufacturing_method"),
					"rm_outbound_wh_qty": process_wise_rec_data_list.get("units_s_r") ,
					"rm_karigar_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)
			elif process_wise_rec_data_list.get("manufacturing_record_type") == "Receive Material from Manufacturing" :
				process_dic = {
					"rm_inbound_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)

		for process_wise_rec_data_list in item_json.get("Geenth"):
			if process_wise_rec_data_list.get("manufacturing_record_type") == "Send Material for Manufacturing" :
				process_dic = {
					"manufacturing_method": process_wise_rec_data_list.get("manufacturing_method"),
					"geenth_outbound_wh_qty": process_wise_rec_data_list.get("units_s_r") ,
					"geenth_karigar_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)
			elif process_wise_rec_data_list.get("manufacturing_record_type") == "Receive Material from Manufacturing" :
				process_dic = {
					"geenth_inbound_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)

		for process_wise_rec_data_list in item_json.get("Stone Fitting"):
			if process_wise_rec_data_list.get("manufacturing_record_type") == "Send Material for Manufacturing" :
				process_dic = {
					"manufacturing_method": process_wise_rec_data_list.get("manufacturing_method"),
					"sf_outbound_wh_qty":process_wise_rec_data_list.get("units_s_r") ,
					"sf_karigar_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)
			elif process_wise_rec_data_list.get("manufacturing_record_type") == "Receive Material from Manufacturing" :
				process_dic = {
					"sf_inbound_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)

		for process_wise_rec_data_list in item_json.get("Packing"):
			if process_wise_rec_data_list.get("manufacturing_record_type") == "Send Material for Manufacturing" :
				process_dic = {
					"pack_outbound_wh_qty": process_wise_rec_data_list.get("units_s_r") ,
					"pack_karigar_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)
			elif process_wise_rec_data_list.get("manufacturing_record_type") == "Receive Material from Manufacturing" :
				process_dic = {
					"pack_inbound_wh_qty": process_wise_rec_data_list.get("units_s_r")
				}
				parent_row_dic.update(process_dic)

		data.append(parent_row_dic)

	return columns, data

def get_columns():
	columns = []
	for col in range(15):
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

	columns[2] = {
	"label": "Rakhi Making Outbound",
	"fieldname": "rm_outbound_wh_qty",
	"width": 160
	}
	columns[3] = {
	"label": "Rakhi Making Karigar",
	"fieldname": "rm_karigar_wh_qty",
	"width": 160
	}
	columns[4] = {
	"label": "Rakhi Making Inbound",
	"fieldname": "rm_inbound_wh_qty",
	"width": 160
	}
	columns[5] = {
	"label": "Geenth Outbound",
	"fieldname": "geenth_outbound_wh_qty",
	"width": 160
	}
	columns[6] = {
	"label": "Geenth Karigar",
	"fieldname": "geenth_karigar_wh_qty",
	"width": 160
	}
	columns[7] = {
	"label": "Geenth Inbound",
	"fieldname": "geenth_inbound_wh_qty",
	"width": 160
	}
	columns[8] = {
	"label": "Stone Fitting Outbound",
	"fieldname": "sf_outbound_wh_qty",
	"width": 160
	}
	columns[9] = {
	"label": "Stone Fitting Karigar",
	"fieldname": "sf_karigar_wh_qty",
	"width": 160
	}
	columns[10] = {
	"label": "Stone Fitting Inbound",
	"fieldname": "sf_inbound_wh_qty",
	"width": 160
	}
	columns[11] = {
	"label": "Packing Outbound",
	"fieldname": "pack_outbound_wh_qty",
	"width": 160
	}
	columns[12] = {
	"label": "Packing Karigar",
	"fieldname": "pack_karigar_wh_qty",
	"width": 160
	}
	columns[13] = {
	"label": "Packing Inbound",
	"fieldname": "pack_inbound_wh_qty",
	"width": 160
	}

	return columns

def get_mrec_data(filters):
	if filters.get("item_made_fil"):
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.units_s_r,mrec.manufacturing_record_type,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mmd.pch_process,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and mrec.item_made = %s  and mmd.name = mrec.start_process order by mmd.process_order """, (filters.get("item_made_fil")), as_dict=1)
	else:
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mmd.pch_process,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and  mmd.name = mrec.start_process order by mmd.process_order """,as_dict=1)

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
