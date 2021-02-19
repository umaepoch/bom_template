# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchGlobalProcess(Document):
	pass
@frappe.whitelist()
def global_po_check():
	global_po_list=frappe.db.sql("""select name,is_global from `tabPch Global Process`""",as_dict=1)
	flag=1
	response=[]
	for global_po in global_po_list:
		if(global_po.is_global==1):
			flag=0;
			response.append({"Name":global_po.name,"Is Global":global_po.is_global});
		else:
			pass
	return response

@frappe.whitelist()
def update_gp_check(name):
	frappe.db.sql("""update `tabPch Global Process` SET is_global=0 where name=%s""",name);
	return "Updated global process config"
