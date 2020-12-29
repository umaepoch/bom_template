# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchManufacturingMethod(Document):
	pass

@frappe.whitelist()
def get_conversion_factor(item_code,uom):
	conversion_factor_dic = frappe.db.sql("""select uom,conversion_factor from `tabUOM Conversion Detail` where parent = %s and uom = %s """,(item_code,uom), as_dict=1)
	return conversion_factor_dic[0]["conversion_factor"] if conversion_factor_dic else None
