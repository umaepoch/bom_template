# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PchProductionPlanLite(Document):
	pass

@frappe.whitelist()
def  get_conversion_factor(uom , item_code):
    cf_dic = frappe.db.sql(
        """select conversion_factor from `tabUOM Conversion Detail` where parent = %s and uom = %s """,
        (item_code, uom), as_dict=1)
    return cf_dic[0]["conversion_factor"] if cf_dic else None