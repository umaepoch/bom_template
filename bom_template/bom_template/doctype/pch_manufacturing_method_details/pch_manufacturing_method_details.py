# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchManufacturingMethodDetails(Document):
	pass

@frappe.whitelist()
def process_validation_against_method(method_name,process_name):
	process_flag = 0
	process_dic =  frappe.db.sql("""select pch_process from `tabPch Manufacturing Method Details` where pch_method=%s """,(method_name), as_dict=1)
	process_dic_list = []
	for process_row in process_dic:
		process_dic_list.append(process_row["pch_process"])
	if process_name in process_dic_list:
		process_flag = 1
	return process_flag



@frappe.whitelist()
def get_process_list():

	process_dic_list = []
	for process_row in process_dic:
		process_dic_list.append(process_row["process_name"])
	return process_dic_list
	
	
@frappe.whitelist()
def get_process_order_values(process_order,method_name):
	flag=1;
	#po_order_list=frappe.db.get_all("Pch Manufacturing Method Details",fields=["process_order"],as_list=True);
	po_order_list=frappe.db.sql("""select process_order,pch_method from `tabPch Manufacturing Method Details`where 			      pch_method=%s""",(method_name),as_dict=1);
	print("Here");
	length=len(po_order_list);
	if(length==0):
		flag=1;
	else:
		for process in po_order_list:
			print(process);	
			process_ordr=process.process_order;
			if(process_ordr==process_order):
				print('Duplicate');
				flag=0;
			
		
	return flag
	
	
