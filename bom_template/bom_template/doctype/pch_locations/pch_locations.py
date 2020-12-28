# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchLocations(Document):
	pass

@frappe.whitelist()
def get_process_list():
	process_dic =  frappe.db.sql("""select process_name from `tabPch Manufacturing Process` """, as_dict=1)
	process_dic_list = []
	for process_row in process_dic:
		process_dic_list.append(process_row["process_name"])
	return process_dic_list

@frappe.whitelist()
def check_unique_warehouse(warehouse_name,warehouse_type):
	check=1;
	wh_list=frappe.db.get_all('Pch Locations Child',fields=['inbound_warehouse','outbound_warehouse'],as_list=True);
	#wh_list=frappe.db.sql("""select inbound_warehouse,outbound_warehouse from `tabPch Locations Child`"""); 
	length=len(wh_list);
	print(length);
	if(length==0):
		check=1;
		print(check,"Top Loop");
	else:
		for inb,outb in wh_list:
			if(warehouse_type=='inbound'):
				if(warehouse_name==outb):
					#print('Warehouse already exists. Please re-enter the details');
					check=0;
					#print(check,"Inbound loop");
				else:
					pass;
			elif(warehouse_type=='outbound'):
				if(warehouse_name==inb):
					#print('Warehouse already exists. Please re-enter the details');
					check=0;
					#print(check,"Outbound Loop");
				else:
					pass;
			else:
				#print("Invalid warehouse type");
	#print(check);
	return check

#Function to return company specific warehouses
@frappe.whitelist()
def get_company_specific_warehouses(company_name):
	wh_list=frappe.db.sql("""select name,company from `tabWarehouse`  where company=%s""",(company_name),as_dict=1);
	#print(company_name);
	w_list=[];
	for wh in wh_list:
		#print(wh);
		w_list.append(wh.name);
	#print(w_list);
	return w_list
#Function to return only expense accounts
@frappe.whitelist()
def get_account_details(company_name):
	acc_list=frappe.db.sql("""select name from `tabAccount` where root_type="Expense"and company=%s""",(company_name),as_dict=1);
	account_list=[];
	for acc in acc_list:
		account_list.append(acc.name);
	#print(account_list);
	return account_list;	

