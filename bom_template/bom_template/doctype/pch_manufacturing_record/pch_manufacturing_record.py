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
		print('End process cannot occur before start process');
		flag=0;
	return flag
