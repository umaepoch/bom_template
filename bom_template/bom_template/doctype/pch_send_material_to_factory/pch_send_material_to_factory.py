# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class PchSendMaterialtoFactory(Document):
    pass


@frappe.whitelist()
def get_items(item, start_process, end_process, method):
    start_process_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process": start_process},
                                               "process_order")
    end_process_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process": end_process},
                                             "process_order")
    item_list = frappe.db.sql(
        """select mmd.item_code,mmd.process_order,mmdrm.item_name,mmdrm.qty_uom,mmdrm.qty_per_unit_made,mmdrm.consumption_type,mmdrm.stock_uom,mmdrm.conversion_factor,mmdrm.operand,mmdrm.qty_in_stock_uom from `tabPch Manufacturing Method Details` mmd inner join `tabPch Manufacturing Method Details RM Child` mmdrm on mmd.name=mmdrm.parent where mmd.process_order>=%s and mmd.process_order<=%s and mmd.item_code=%s and mmd.pch_method=%s order by process_order asc""",
        (start_process_ord_no, end_process_ord_no, item, method), as_dict=1);
    return item_list


@frappe.whitelist()
def set_available_methods(item):
    method_list = frappe.db.sql("""select parent from `tabPch Manufacturing Method Child` where item_made=%s""", item,
                                as_dict=1);
    method = []
    for methods in method_list:
        method.append(methods.parent);
    return method


@frappe.whitelist()
def validate_process_orders(start_process, end_process):
    start_process_order = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process": start_process},
                                              "process_order");
    end_process_order = frappe.db.get_value("Pch Manufacturing Method Details", {"pch_process": end_process},
                                            "process_order");
    flag = 0;
    if (start_process_order > end_process_order):
        flag = 1;
    else:
        flag = 0;
    return flag;


@frappe.whitelist()
def set_available_processes(method):
    process_list = frappe.db.sql(
        """select pch_process from `tabPch Manufacturing Method Details` where pch_method=%s order by process_order asc""",
        method, as_dict=1);
    process = []
    for processes in process_list:
        process.append(processes.pch_process);
    return process


@frappe.whitelist()
def create_stock_entry(se_entity):
    # test
    status = []
    try:
        se = frappe.new_doc("Stock Entry")

        # se.company = "Epoch Consulting"
        se.company = se_entity.get("company")
        #se.purpose = se_entity.get("action")
        se.stock_entry_type = se_entity.get("action")

        se.set('items', [])
        for item in se_entity.get("items_list"):
            se_item = se.append('items', {})
            se_item.item_code = item["item_code"]
            se_item.qty = item["qty"]
            se_item.uom = item["uom"]
            se_item.conversion_factor = item["conversion_factor"]
            se_item.stock_uom = frappe.db.get_value("Item", {"name": item["item_code"]}, "stock_uom")
            se_item.expense_account = item["expense_account"]
            if se_entity.get("action") == "Material Transfer":
                se_item.s_warehouse = item["s_wh"]
                se_item.t_warehouse = item["t_wh"]
            if se_entity.get("action") == "Material Issue":

                se_item.s_warehouse = item["s_wh"]
            if se_entity.get("action") == "Material Receipt":
                se_item.t_warehouse = item["t_wh"]
                if item["basic_rate"]:
                    se_item.basic_rate = item["basic_rate"]

        se.save(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        status.append({"Name": se.name, "Exception": "Not Occured"});

    except Exception as e:
        status.append({"Name": se.name, "Exception": "Occured", "Exception type": e});
        frappe.delete_doc("Stock Entry", se.name)
    return status


@frappe.whitelist()
def send_material_to_factory(entity):
    entity = json.loads(entity)
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    internal_transfer_account = frappe.db.get_value("pch Bom Template Company Settings", {"name": company},
                                                    "internal_mat_transfer_acc")
    response = [];
    # make_transfer
    # from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
    transfer_items_list = []
    for i_row in entity.get("items_being_sent"):
        item_dic = {
            "item_code": i_row.get("item_code"),
            "qty": i_row.get("dispatched_quantity_in_uom"),
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": entity.get("corporate_warehouse"),
            # Internal warehouse from which the material needs to be transferred to process ob
            "t_wh": entity.get("receiving_warehouse"),
            "expense_account": internal_transfer_account

        }
        transfer_items_list.append(item_dic)

    se_trans_entity = {"action": "Material Issue", "items_list": transfer_items_list, "company": company}

    se_transfer = create_stock_entry(se_trans_entity)


    if (se_transfer[0]["Exception"] == "Not Occured"):
        response.append({"Name": se_transfer["Name"], "Status": "Created", "Stock Entry Type": "Material Issue"});
        return response
    else:
        response.append({"Name": se_transfer["Name"], "Status": "Not Created", "Stock Entry Type": "Material Issue"});
        return response


@frappe.whitelist()
def receive_material_at_factory(entity):
    entity = json.loads(entity)
    # internal_transfer_account = "Inter Location Material Transfer Account - RAKHI"
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    internal_transfer_account = frappe.db.get_value("pch Bom Template Company Settings", {"name": company},
                                                    "internal_mat_transfer_acc")

    response = [];
    # make_transfer
    # from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
    transfer_items_list = []
    for i_row in entity.get("items_being_sent"):
        item_dic = {
            "item_code": i_row.get("item_code"),
            "qty": i_row.get("dispatched_quantity_in_uom"),
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": entity.get("corporate_warehouse"),
            # Internal warehouse from which the material needs to be transferred to process ob
            "t_wh": entity.get("receiving_warehouse"),
            "expense_account": internal_transfer_account,
            "basic_rate" : get_source_warehouse_val_rate(entity.get("corporate_warehouse"),i_row.get("item_code")) #corporate_warehouse mandatory in recive doc
        }
        transfer_items_list.append(item_dic)

    se_trans_entity = {"action": "Material Receipt", "items_list": transfer_items_list, "company": company}

    se_transfer = create_stock_entry(se_trans_entity)


    if (se_transfer[0]["Exception"] == "Not Occured"):
        response.append({"Name": se_transfer["Name"], "Status": "Created", "Stock Entry Type": "Material Receipt"});
        return response
    else:
        response.append({"Name": se_transfer["Name"], "Status": "Not Created", "Stock Entry Type": "Material Receipt"});
        return response

def get_source_warehouse_val_rate(corporate_warehouse,item_code):
    val_rate_dic = frappe.db.sql(
        """select valuation_rate  
        from `tabStock Ledger Entry` 
        where item_code=%s  and warehouse=%s   
        order by creation desc limit 1""",
        (item_code,corporate_warehouse),
        as_dict=1)
    if val_rate_dic :
        return val_rate_dic[0]["valuation_rate"]

