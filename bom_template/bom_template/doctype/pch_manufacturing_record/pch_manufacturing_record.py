# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchManufacturingRecord(Document):
	pass

@frappe.whitelist()
def get_start_end_process_raw_materials(start_process,end_process):
	start_process_raw_item_data = get_manufacture_method_details_raw_items(start_process)
	if start_process == end_process :
		return start_process_raw_item_data
	end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
	start_end_process_raw_materials_list = [start_process_raw_item_data,end_process_raw_item_data]
	start_end_process_raw_materials_data=[]
	for process_raw_materials_list in start_end_process_raw_materials_list:
		for item in process_raw_materials_list:
			start_end_process_raw_materials_data.append(item)

	print "start_end_process_raw_materials_data",start_end_process_raw_materials_data
	return start_end_process_raw_materials_data

def get_manufacture_method_details_raw_items(doc_name):
	manufacture_method_details_raw_items = frappe.db.sql("""select * from `tabPch Manufacturing Method Details Items` where parent = %s""",(doc_name), as_dict=1)
	return manufacture_method_details_raw_items
