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


	for mrec in mrec_data:
		row_dic = {"item_made_temp":mrec.get("item_made"),
		"manufacturing_method":mrec.get("manufacturing_method"),
		"start_process":mrec.get("start_process"),
		"process_order":mrec.get("process_order"),
		"sub_contractor":mrec.get("sub_contractor"),
		"subcontractor_warehouse":mrec.get("target_warehouse"),
		"outbound_warehouse":mrec.get("outbound_warehouse"),
		"receiving_warehouse":mrec.get("receiving_warehouse"),
		"qty_after_transaction":1
		}
		data.append(row_dic)
	return columns, data

def get_columns():
	columns = []
	for col in range(10):
		columns.append("")


	columns[0] = {
	"label": "Item Made",
	"fieldname": "item_made_temp",
	"options":"Pch Manufacturing Record Child Method",
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
	"label": "Process",
	"fieldname": "start_process",
	"options":"Pch Manufacturing Method Details",
	"fieldtype": "Link",
	"width": 160
	}
	columns[3] = {
	"label": "Process Order",
	"fieldname": "process_order",
	"options":"Pch Manufacturing Method Details",
	"fieldtype": "Link",
	"width": 160
	}
	columns[4] = {
	"label": "Subcontractor",
	"options": "Supplier",
	"fieldname": "sub_contractor",
	"fieldtype": "Link",
	"width": 160
	}
	columns[5] = {
	"label": "Outbound Warehouse",
	"options": "Warehouse",
	"fieldname": "outbound_warehouse",
	"fieldtype": "Link",
	"width": 160
	}
	columns[6] = {
	"label": "Subcontractor Warehouse",
	"options": "Warehouse",
	"fieldname": "subcontractor_warehouse",
	"fieldtype": "Link",
	"width": 160
	}
	columns[7] = {
	"label": "Receiving Warehouse",
	"options": "Warehouse",
	"fieldname": "receiving_warehouse",
	"fieldtype": "Link",
	"width": 160
	}
	columns[8] = {
	"label": "Item Balance after Transaction",
	"fieldname": "qty_after_transaction",
	"width": 160
	}

	return columns

def get_mrec_data(filters):
	#conditions = get_conditions(filters)
	#query = "select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1  and mmd.name = mrec.start_process order by mmd.process_order"
	#query = "select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse,mrec.start_process,mmd.process_order from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and  mmd.name = mrec.start_process {} order by mmd.process_order".format(conditions)
	#query = "select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and mrec.item_made = 'Food'  and mmd.name = mrec.start_process order by mmd.process_order"
	#mrec_data =  frappe.db.sql(query,as_dict=1)
	mrec_data = frappe.db.sql("""select mrec.name,mrec.item_made,mrec.manufacturing_method,mrec.start_process,mmd.process_order,mrec.outbound_warehouse,mrec.sub_contractor,mrec.target_warehouse,mrec.receiving_warehouse from `tabPch Manufacturing Record`    mrec,`tabPch Manufacturing Method Details` mmd where   mrec.docstatus = 1 and mrec.item_made = %s  and mmd.name = mrec.start_process order by mmd.process_order """, (filters.get("item_made_fil")), as_dict=1)
	"""
	mrec_json = {}
	for mrec in mrec_data :
		if mrec_json.get(mrec["item_made"]):
			mrec_json[mrec["item_made"]].append(mrec)
		else:
			mrec_json[mrec["item_made"]]= [mrec]

	print "mrec_json",mrec_json
	"""

	return mrec_data

def get_conditions(filters):
    conditions = ""
    if filters.get("item_made_fil"):
        conditions += " and mrec.item_made = %s" % frappe.db.escape(filters.get("mrec"), percent=False)
    return conditions
