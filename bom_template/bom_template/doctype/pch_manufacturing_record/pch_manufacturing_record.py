# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class PchManufacturingRecord(Document):
	pass

@frappe.whitelist()
def get_start_end_process_raw_materials(start_process,end_process,method):
	if start_process == end_process :
		start_process_raw_item_data = get_pro_order_wise_manufacture_method_details_raw_items(start_process,start_process,method)
		return start_process_raw_item_data
	else:
		#product_order_wise_data_start
		#end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
		start_end_process_raw_materials_data = get_pro_order_wise_manufacture_method_details_raw_items(start_process,end_process,method)
		return start_end_process_raw_materials_data
		#product_ordee_wise_data_end

@frappe.whitelist()
def get_start_end_p_process_details(start_process,end_process,method):
	if start_process == end_process :
		start_process_raw_item_data = get_pro_order_wise_process_details(start_process,start_process,method)
		return start_process_raw_item_data
	else:
		#product_order_wise_data_start
		#end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
		start_end_process_raw_materials_data = get_pro_order_wise_process_details(start_process,end_process,method)
		return start_end_process_raw_materials_data

def get_pro_order_wise_process_details(start_process,end_process,method):
	start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":start_process},"process_order")
	end_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":end_process},"process_order")

	mmd_process_details = frappe.db.sql("""select
	mmd.name,mmd.pch_process,mmd.pch_method,mmd.process_order,mmd.turnaround_time,mmd.touch_points
	from
	`tabPch Manufacturing Method Details` mmd
	where
	mmd.process_order>=%s and mmd.process_order<= %s and mmd.pch_method= %s order by mmd.process_order asc""",(start_process_pro_ord_no,end_process_pro_ord_no,method), as_dict=1)


	return mmd_process_details

def get_pro_order_wise_manufacture_method_details_raw_items(start_process,end_process,method):
	start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":start_process},"process_order")
	end_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":end_process},"process_order")

	manufacture_method_details_raw_items = frappe.db.sql("""select
	mmd.name,mmdi.item_code,mmdi.item_name,mmdi.qty,mmdi.uom,mmdi.stock_uom,mmdi.conversion_factor,mmdi.operand,mmdi.qty_in_stock_uom
	from
	`tabPch Manufacturing Method Details` mmd,`tabPch Manufacturing Method Details Items` mmdi
	where
	mmd.name=mmdi.parent and process_order>=%s and process_order<= %s and pch_method= %s """,(start_process_pro_ord_no,end_process_pro_ord_no,method), as_dict=1)


	return manufacture_method_details_raw_items


@frappe.whitelist()
def get_child_doc_data(doc_type,parent):
    table="tab"+doc_type
    #table='`tab'+doc_type+'`'
    sql = "select  * from `"+table+"` where parent='"+parent+"'"
    #sql = "select  * from `"+table+"`"
    doc_data = frappe.db.sql(sql,as_dict=1)
    return doc_data

@frappe.whitelist()
def get_wh_ac_to_location(location_name,wh_type,process):
    wh_name_dic = frappe.db.sql("""select outbound_warehouse,inbound_warehouse from `tabPch Locations Child` where parent = %s and process_name = %s """,(location_name,process), as_dict=1)
    return wh_name_dic[0][wh_type] if wh_name_dic else None

#Ak
@frappe.whitelist()
def validate_start_and_end_process(start_process,end_process):
	flag=1;
	st_list=frappe.db.sql("""select `process_order` as `start_process_order` from  `tabPch Manufacturing Method Details` where name=%s""",(start_process),as_dict=1);
	en_list=frappe.db.sql("""select `process_order` as `end_process_order`  from  `tabPch Manufacturing Method Details` where name=%s""",(end_process),as_dict=1);
	start_process_order_value=st_list[0]["start_process_order"];
	end_process_order_value=en_list[0]["end_process_order"];
	if(start_process_order_value > end_process_order_value):
		#print('End process cannot occur before start process');
		flag=0;
	return flag

#raw_material_transactions_start
#pch_locations_id,items
#issue from raw material wh of location
@frappe.whitelist()
def send_material_for_manufacturing(entity):
	entity = json.loads(entity)
	"""
	smfm_transaction_order =[]
	smfm_transaction_order[0]="Material Issue"
	if start_process_pro_ord_no <= 1:
		smfm_transaction_order[1]="Material Receipt"
		smfm_transaction_order[2]="Material Transfer"
	else:
		smfm_transaction_order[1]="Material Transfer"
	"""

	raw_material_warehouse = frappe.db.get_value("Pch Locations", {"name":entity.get("location")},"raw_material_warehouse")
	start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":entity.get("start_process")},"process_order")


	#issue_start
	issue_items_list = []
	for i_row in entity.get("req_items"):
		item_dic = {
		"item_code" :i_row.get("item_code") ,
		"qty":i_row.get("total_qty"),
		"uom":i_row.get("qty_uom"),
		"conversion_factor":i_row.get("conversion_factor"),
		"t_wh":None,
		"s_wh":raw_material_warehouse
		}
		issue_items_list.append(item_dic)
	se_issue_entity  = {"action" :"Material Issue","items_list":issue_items_list}
	#print "se_issue_entity",se_issue_entity
	se_issue = create_stock_entry(se_issue_entity)
	#issue_end

	if se_issue :

		#issue is done #call_next_transaction #material_rec

		#transfer is must
		trans_entity = {
		"items":entity.get("method_items"),
		"s_wh":entity.get("outbound_warehouse"),
		"t_wh":entity.get("target_warehouse")
		}
		expense_account = frappe.db.get_value("Pch Locations", {"name":entity.get("location")},"expense_account")
		trans_entity["add_amount"] = entity.get("subcontracting_rate")
		trans_entity["expense_account"] = expense_account
		trans_entity["isAdditionCost"] = 1
		#transfer is must

		start_process_pro_ord_no =int (start_process_pro_ord_no)



		if start_process_pro_ord_no == 1:
			#print "se_issue created 3t:",se_issue
			#receipt fetch method item #Pch Manufacturing Record Child Method (method_items)

			receipt_items_list = []
			for i_row in entity.get("method_items"):
				item_dic = {
				"item_code" :i_row.get("item_made") ,
				"qty":i_row.get("qty_made"),
				"uom":i_row.get("qty_uom"),
				"conversion_factor" : i_row.get("conversion_factor"),
				"t_wh":entity.get("outbound_warehouse"),
				"s_wh":None
				}
				receipt_items_list.append(item_dic)
			se_rec_entity  = {"action" :"Material Receipt","items_list":receipt_items_list}
			#print "se_rec_entity data",se_rec_entity
			se_receipt = create_stock_entry(se_rec_entity)


			if se_receipt:
				#print "se_receipt created ",se_receipt
				#print "transfer data ",trans_entity

				se_transfer3 = make_transfer(trans_entity)
				#print "se_transfer3 created ",se_transfer3
				return "all 3 created"
		else:
			#print "se_issue created 2t:",se_issue
			#print "transfer data ",trans_entity
			se_transfer2 = make_transfer(trans_entity)
			#print "se_transfer2 created ",se_transfer2
			return "all 2 created"
	else:
		#print "se_transfer3 created ",se_transfer3
		return "failed to create 1 trans issue"

def make_transfer(trans_entity):
	transfer_items_list = []
	for i_row in trans_entity.get("items"):
		item_dic = {
		"item_code" :i_row.get("item_made") ,
		"qty":i_row.get("qty_made"),
		"uom":i_row.get("qty_uom"),
		"conversion_factor" : i_row.get("conversion_factor"),
		"s_wh":trans_entity.get("s_wh"),
		"t_wh":trans_entity.get("t_wh")
		}
		transfer_items_list.append(item_dic)
	se_trans_entity  = {"action" :"Material Transfer","items_list":transfer_items_list}
	se_trans_entity["add_amount"] = trans_entity.get("add_amount")
	se_trans_entity["expense_account"] = trans_entity.get("expense_account")
	se_trans_entity["isAdditionCost"] = 1
	se_transfer = create_stock_entry(se_trans_entity)
	return se_transfer

@frappe.whitelist()
def create_stock_entry(se_entity):
	#print ("from create_stock_entry se_entity :",se_entity)
	se = frappe.new_doc("Stock Entry")
	#e.purpose = se_entity.get("action")
	#se.company = "Epoch Consulting"
	se.company = "Shree Rakhi"
	se.stock_entry_type = se_entity.get("action")

	se.set('items', [])
	for item in se_entity.get("items_list") :
		se_item = se.append('items', {})
		se_item.item_code = item["item_code"]
		se_item.qty = item["qty"]
		se_item.uom = item["uom"]
		se_item.conversion_factor = item["conversion_factor"]
		se_item.stock_uom = frappe.db.get_value("Item", {"name":item["item_code"]},"stock_uom")
		if se_entity.get("action") == "Material Transfer":
			se_item.s_warehouse =  item["s_wh"]
			se_item.t_warehouse =  item["t_wh"]
		if se_entity.get("action") == "Material Issue":
			se_item.s_warehouse =  item["s_wh"]
		if se_entity.get("action") == "Material Receipt":
			se_item.t_warehouse =  item["t_wh"]

	if se_entity.get("isAdditionCost"):
		se.set('additional_costs', [])
		se_add_cost = se.append('additional_costs', {})
		se_add_cost.description = "Manufacturing Record"
		se_add_cost.expense_account = se_entity.get("expense_account")
		se_add_cost.amount = se_entity.get("add_amount")

	se.save(ignore_permissions=True)
	se.submit()
	frappe.db.commit()
	return se.name



@frappe.whitelist()
def receive_material_for_manufacturing(entity):
	entity = json.loads(entity)
	expense_account = frappe.db.get_value("Pch Locations", {"name":entity.get("location")},"expense_account")

	#make_transfer
	#from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
	transfer_items_list = []
	for i_row in entity.get("method_items"):
		item_dic = {
		"item_code" :i_row.get("item_made") ,
		"qty":i_row.get("qty_made"),
		"uom":i_row.get("qty_uom"),
		"conversion_factor" : i_row.get("conversion_factor"),
		"s_wh":entity.get("target_warehouse"), #subcontractor wh
		"t_wh":entity.get("receiving_warehouse") #receiving_warehouse
		}
		transfer_items_list.append(item_dic)



	se_trans_entity  = {"action" :"Material Transfer","items_list":transfer_items_list}
	se_trans_entity["add_amount"] = entity.get("subcontracting_rate")
	se_trans_entity["expense_account"] = expense_account
	se_trans_entity["isAdditionCost"] = 1
	se_transfer = create_stock_entry(se_trans_entity)
	if se_transfer:
		return se_transfer
	else:
		"bug in transfer"



    #ability to create purchase invoice in future
