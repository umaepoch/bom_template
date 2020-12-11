#hello
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words

@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def test():
	return "sucess"

@frappe.whitelist()
def get_doc_data(doc_type,doc_name):
    table="tab"+doc_type
    #table='`tab'+doc_type+'`'
    sql = "select  * from `"+table+"` where name='"+doc_name+"'"
    #sql = "select  * from `"+table+"`"
    doc_data = frappe.db.sql(sql,as_dict=1)
    return doc_data

@frappe.whitelist()
def get_child_doc_data(doc_type,parent):
    table="tab"+doc_type
    #table='`tab'+doc_type+'`'
    sql = "select  * from `"+table+"` where parent='"+parent+"'"
    #sql = "select  * from `"+table+"`"
    doc_data = frappe.db.sql(sql,as_dict=1)
    return doc_data
