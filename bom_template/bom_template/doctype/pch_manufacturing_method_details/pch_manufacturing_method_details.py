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
