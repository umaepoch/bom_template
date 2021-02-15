# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class PchSendMaterialtoFactory(Document):
	pass
@frappe.whitelist()
def get_items(item,start_process,end_process,method):
	print(start_process);
	start_process_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process":start_process},"process_order")
	print(start_process_ord_no);
	end_process_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process":end_process},"process_order")
	print(end_process_ord_no)
	item_list=frappe.db.sql("""select mmd.item_code,mmd.process_order,mmdrm.item_name,mmdrm.qty_uom,mmdrm.qty_per_unit_made,mmdrm.consumption_type,mmdrm.stock_uom,mmdrm.conversion_factor,mmdrm.operand,mmdrm.qty_in_stock_uom from `tabPch Manufacturing Method Details` mmd inner join `tabPch Manufacturing Method Details RM Child` mmdrm on mmd.name=mmdrm.parent where mmd.process_order>=%s and mmd.process_order<=%s and mmd.item_code=%s and mmd.pch_method=%s order by process_order asc""",(start_process_ord_no,end_process_ord_no,item,method),as_dict=1);
	print(item_list);
	return item_list
@frappe.whitelist()
def set_available_methods(item):
	method_list=frappe.db.sql("""select parent from `tabPch Manufacturing Method Child` where item_made=%s""",item,as_dict=1);
	method=[]
	for methods in method_list:
		method.append(methods.parent);
	return method
@frappe.whitelist()
def validate_process_orders(start_process,end_process):
	start_process_order=frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process":start_process},"process_order");
	end_process_order=frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process":end_process},"process_order");
	print(start_process_order,end_process_order);
	flag=0;
	if(start_process_order>end_process_order):
		flag=1;
	else:
		flag=0;
	print(flag)
	return flag;
@frappe.whitelist()
def set_available_processes(method):
	process_list=frappe.db.sql("""select pch_process from `tabPch Manufacturing Method Details` where pch_method=%s order by process_order asc""",method,as_dict=1);
	process=[]
	for processes in process_list:
		process.append(processes.pch_process);
	return process
@frappe.whitelist()
def create_stock_entry(se_entity):
	#print ("from create_stock_entry se_entity :",se_entity)
	#test
	status=[]
	try:
		se = frappe.new_doc("Stock Entry")
		#se.purpose = se_entity.get("action")
		#se.company = "Epoch Consulting"
		se.company = se_entity.get("company")
		se.stock_entry_type = se_entity.get("action")

		se.set('items', [])
		for item in se_entity.get("items_list") :
			se_item = se.append('items', {})
			se_item.item_code = item["item_code"]
			se_item.qty = item["qty"]
			se_item.uom = item["uom"]
			se_item.conversion_factor = item["conversion_factor"]
			se_item.stock_uom = frappe.db.get_value("Item", {"name":item["item_code"]},"stock_uom")
			se_item.expense_account = item["expense_account"]
			se_item.basic_rate=0.01
			print(se_item.basic_rate);
			if se_entity.get("action") == "Material Transfer":
				se_item.s_warehouse =  item["s_wh"]
				se_item.t_warehouse =  item["t_wh"]
			if se_entity.get("action") == "Material Issue":
				se_item.s_warehouse =  item["s_wh"]
			if se_entity.get("action") == "Material Receipt":
				se_item.t_warehouse =  item["t_wh"]

		se.save(ignore_permissions=True)
		se.submit()
		frappe.db.commit()
		status.append({"Name":se.name,"Exception":"Not Occured"});
		
	except Exception as e:	
		print('An exception occured while creating Stock Entry',e);
		status.append({"Name":se.name,"Exception":"Occured","Exception type":e});
		frappe.delete_doc("Stock Entry",se.name)
	return status
@frappe.whitelist()
def send_material_to_factory(entity):
	entity = json.loads(entity)
	internal_transfer_account = frappe.db.get_value("pch Bom Template Settings",{"internal_mat_transfer_acc":"Inter Location Material Transfer Account - RAKHI"}, "internal_mat_transfer_acc")
	location=entity.get("location");
	company=frappe.db.get_value("Pch Locations",{"name":entity.get("location")},"company");
	print(internal_transfer_account)
	response=[];
	#make_transfer
	#from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
	transfer_items_list = []
	for i_row in entity.get("items_being_sent"):
		item_dic = {
		"item_code" :i_row.get("item_code") ,
		"qty":i_row.get("qty_in_stock_uom"),
		"uom":i_row.get("qty_uom"),
		"conversion_factor" : i_row.get("conversion_factor"),
		"s_wh":entity.get("corporate_warehouse"), #Internal warehouse from which the material needs to be transferred to process ob
		"t_wh":entity.get("receiving_warehouse"),
		"expense_account":internal_transfer_account
		
		
		}
		transfer_items_list.append(item_dic)



	se_trans_entity  = {"action" :"Material Issue","items_list":transfer_items_list,"company":company}
	
	
	se_transfer = create_stock_entry(se_trans_entity)
	
	print(se_trans_entity);
	
	
	print(se_transfer)
	if (se_transfer[0]["Exception"]=="Not Occured"):
		response.append({"Name":se_transfer,"Status":"Created","Stock Entry Type":"Material Issue"});
		print(response)
		return response
	else:
		response.append({"Name":se_transfer,"Status":"Not Created","Stock Entry Type":"Material Issue"});
		print(response)
		return response
@frappe.whitelist()
def receive_material_at_factory(entity):
	entity = json.loads(entity)
	internal_transfer_account = frappe.db.get_value("pch Bom Template Settings",{"internal_mat_transfer_acc":"Inter Location Material Transfer Account - RAKHI"}, "internal_mat_transfer_acc")
	location=entity.get("location");
	company=frappe.db.get_value("Pch Locations",{"name":entity.get("location")},"company");
	print(internal_transfer_account)
	response=[];
	#make_transfer
	#from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
	transfer_items_list = []
	for i_row in entity.get("items_being_sent"):
		item_dic = {
		"item_code" :i_row.get("item_code") ,
		"qty":i_row.get("qty_in_stock_uom"),
		"uom":i_row.get("qty_uom"),
		"conversion_factor" : i_row.get("conversion_factor"),
		"s_wh":entity.get("corporate_warehouse"), #Internal warehouse from which the material needs to be transferred to process ob
		"t_wh":entity.get("receiving_warehouse"),
		"expense_account":internal_transfer_account
		
		
		}
		transfer_items_list.append(item_dic)



	se_trans_entity  = {"action" :"Material Receipt","items_list":transfer_items_list,"company":company}
	
	
	se_transfer = create_stock_entry(se_trans_entity)
	
	print(se_trans_entity);
	
	
	print(se_transfer)
	if (se_transfer[0]["Exception"]=="Not Occured"):
		response.append({"Name":se_transfer,"Status":"Created","Stock Entry Type":"Material Transfer"});
		print(response)
		return response
	else:
		response.append({"Name":se_transfer,"Status":"Not Created","Stock Entry Type":"Material Transfer"});
		print(response)
		return response
	
