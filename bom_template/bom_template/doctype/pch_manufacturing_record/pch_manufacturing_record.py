# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchManufacturingRecord(Document):
	pass

@frappe.whitelist()
def get_start_end_process_raw_materials(start_process,end_process,method):
	if start_process == end_process :
		start_process_raw_item_data = get_manufacture_method_details_raw_items(start_process)
		return start_process_raw_item_data
	else:
		#product_order_wise_data_start
		#end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
		start_end_process_raw_materials_data = get_pro_order_wise_manufacture_method_details_raw_items(start_process,end_process,method)
		return start_end_process_raw_materials_data

		#product_ordee_wise_data_end

		"""
		start_end_process_raw_materials_list = [start_process_raw_item_data,end_process_raw_item_data]
		start_end_process_raw_materials_data=[]
		for process_raw_materials_list in start_end_process_raw_materials_list:
			for item in process_raw_materials_list:
				start_end_process_raw_materials_data.append(item)

		#print "start_end_process_raw_materials_data",start_end_process_raw_materials_data
		return start_end_process_raw_materials_data
		"""

def get_pro_order_wise_manufacture_method_details_raw_items(start_process,end_process,method):
	start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":start_process},"process_order")
	end_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name":end_process},"process_order")

	manufacture_method_details_raw_items = frappe.db.sql("""select
	mmd.name,mmdi.item_code,mmdi.uom,mmdi.stock_uom,mmdi.conversion_factor,mmdi.operand,mmdi.qty_in_stock_uom
	from
	`tabPch Manufacturing Method Details` mmd,`tabPch Manufacturing Method Details Items` mmdi
	where
	mmd.name=mmdi.parent and process_order>=%s and process_order<= %s and pch_method= %s """,(start_process_pro_ord_no,end_process_pro_ord_no,method), as_dict=1)


	return manufacture_method_details_raw_items



def get_manufacture_method_details_raw_items(doc_name):
	manufacture_method_details_raw_items = frappe.db.sql("""select * from `tabPch Manufacturing Method Details Items` where parent = %s""",(doc_name), as_dict=1)
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
    return wh_name_dic[0][wh_type]

#Ak
@frappe.whitelist()
def validate_start_and_end_process(start_process,end_process):
	flag=1;
	st_list=frappe.db.sql("""select `process_order` as `start_process_order` from  `tabPch Manufacturing Method Details` where meth_pro_con=%s""",(start_process),as_dict=1);
	en_list=frappe.db.sql("""select `process_order` as `end_process_order`  from  `tabPch Manufacturing Method Details` where meth_pro_con=%s""",(end_process),as_dict=1);
	length1=len(st_list);
	length2=len(en_list);
	if(length1==0 or length2==0):
		#print('Manufacturing Method details document is not configured. Please configure Manufacturing Method details and re-try');
		pass
	else:
		for start_process_value in st_list:
			for end_process_value in en_list:
				print(end_process_value);
				print(start_process_value);
				sp_value=start_process_value.start_process_order;
				ep_value=end_process_value.end_process_order;
				if(ep_value < sp_value):
					flag=0;
					#print('End process cannot occur before the start process');
	return flag;
