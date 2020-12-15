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
