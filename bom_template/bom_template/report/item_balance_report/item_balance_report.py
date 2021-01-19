# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	mrec_data = get_mrec_data(filters)
	#mrec_json = get_mrec_data(filters)
	#for mrec_data in mrec_json.items():


	for item_made,item_list in mrec_data.items():

		parent_row_dic = {"item_made_temp": item_made}

		for item in item_list:
			row_dic = { "manufacturing_method": item.get("manufacturing_method"),
					   "sub_contractor": item.get("sub_contractor")}

			process =  frappe.db.get_value("Pch Manufacturing Method Details", {"name":  item.get("start_process")}, "pch_process")

			if  process == "Rakhi Making":
				process_dic = {"rm_outbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("outbound_warehouse")),
						   "rm_karigar_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("target_warehouse")),
						   "rm_inbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("receiving_warehouse"))
						   }
				row_dic.update(process_dic)

			if  process == "Stone Fitting":
				process_dic = {"sf_outbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("outbound_warehouse")),
						   "sf_karigar_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("target_warehouse")),
						   "sf_inbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("receiving_warehouse"))
						   }
				row_dic.update(process_dic)
			if  process == "Geenth":
				process_dic = {"geenth_outbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("outbound_warehouse")),
						   "geenth_karigar_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("target_warehouse")),
						   "geenth_inbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("receiving_warehouse"))
						   }
				row_dic.update(process_dic)
			if  process == "Packing":
				process_dic = {"pack_outbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("outbound_warehouse")),
						   "pack_karigar_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("target_warehouse")),
						   "pack_inbound_wh_qty":get_stock_qty_in_wh(item.get("item_made"),item.get("receiving_warehouse"))
						   }
				row_dic.update(process_dic)
			parent_row_dic.update(row_dic)

		print ("parent_row_dic",parent_row_dic)
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
	"label": "Subcontractor",
	"options": "Supplier",
	"fieldname": "sub_contractor",
	"fieldtype": "Link",
	"width": 160
	}
	columns[3] = {
	"label": "Rakhi Making Outbound",
	"fieldname": "rm_outbound_wh_qty",
	"width": 160
	}
	columns[4] = {
	"label": "Rakhi Making Karigar",
	"fieldname": "rm_karigar_wh_qty",
	"width": 160
	}
	columns[5] = {
	"label": "Rakhi Making Inbound",
	"fieldname": "rm_inbound_wh_qty",
	"width": 160
	}
	columns[6] = {
	"label": "Geenth Outbound",
	"fieldname": "geenth_outbound_wh_qty",
	"width": 160
	}
	columns[7] = {
	"label": "Geenth Karigar",
	"fieldname": "geenth_karigar_wh_qty",
	"width": 160
	}
	columns[8] = {
	"label": "Geenth Inbound",
	"fieldname": "geenth_inbound_wh_qty",
	"width": 160
	}
	columns[9] = {
	"label": "Stone Fitting Outbound",
	"fieldname": "sf_outbound_wh_qty",
	"width": 160
	}
	columns[10] = {
	"label": "Stone Fitting Karigar",
	"fieldname": "sf_karigar_wh_qty",
	"width": 160
	}
	columns[11] = {
	"label": "Stone Fitting Inbound",
	"fieldname": "sf_inbound_wh_qty",
	"width": 160
	}
	columns[12] = {
	"label": "Packing Outbound",
	"fieldname": "pack_outbound_wh_qty",
	"width": 160
	}
	columns[13] = {
	"label": "Packing Karigar",
	"fieldname": "pack_karigar_wh_qty",
	"width": 160
	}
	columns[14] = {
	"label": "Packing Inbound",
	"fieldname": "pack_inbound_wh_qty",
	"width": 160
	}

	return columns

def get_mrec_data(filters):
	if filters.get("item_made_fil"):
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and mrec.item_made = %s  and mmd.name = mrec.start_process order by mmd.process_order """, (filters.get("item_made_fil")), as_dict=1)
	else:
		mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and  mmd.name = mrec.start_process order by mmd.process_order """,as_dict=1)
	
	mrec_json = {}
	for mrec in mrec_data :
		if mrec_json.get(mrec["item_made"]):
			mrec_json[mrec["item_made"]].append(mrec)
		else:
			mrec_json[mrec["item_made"]]= [mrec]
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
