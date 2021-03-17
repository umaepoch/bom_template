# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json


class PchManufacturingRecord(Document):
    pass


@frappe.whitelist()
def get_start_end_process_raw_materials(start_process, end_process, method):
    if start_process == end_process:
        start_process_raw_item_data = get_pro_order_wise_manufacture_method_details_raw_items(start_process,
                                                                                              start_process, method)
        return start_process_raw_item_data
    else:
        # product_order_wise_data_start
        # end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
        start_end_process_raw_materials_data = get_pro_order_wise_manufacture_method_details_raw_items(start_process,
                                                                                                       end_process,
                                                                                                       method)
        return start_end_process_raw_materials_data


@frappe.whitelist()
def get_start_end_process_raw_materials_for_packing(start_process, end_process, method ,item_made_list):
        item_made_list_packing_raw_materials = get_pro_order_wise_manufacture_method_details_raw_items(start_process,start_process, method,item_made_list)
        return item_made_list_packing_raw_materials



# product_ordee_wise_data_end

@frappe.whitelist()
def get_start_end_p_process_details(start_process, end_process, method):
    if start_process == end_process:
        start_process_raw_item_data = get_pro_order_wise_process_details(start_process, start_process, method)
        return start_process_raw_item_data
    else:
        # product_order_wise_data_start
        # end_process_raw_item_data = get_manufacture_method_details_raw_items(end_process)
        start_end_process_raw_materials_data = get_pro_order_wise_process_details(start_process, end_process, method)
        return start_end_process_raw_materials_data


def get_pro_order_wise_process_details(start_process, end_process, method):
    start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name": start_process},
                                                   "process_order")
    end_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name": end_process},
                                                 "process_order")

    mmd_process_details = frappe.db.sql("""select
	mmd.name,mmd.pch_process,mmd.pch_method,mmd.process_order,mmd.turnaround_time,mmd.touch_points
	from
	`tabPch Manufacturing Method Details` mmd
	where
	mmd.process_order>=%s and mmd.process_order<= %s and mmd.pch_method= %s order by mmd.process_order asc""",
                                        (start_process_pro_ord_no, end_process_pro_ord_no, method), as_dict=1)

    return mmd_process_details


def get_pro_order_wise_manufacture_method_details_raw_items(start_process, end_process, method):
    start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name": start_process},
                                                   "process_order")
    end_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details", {"name": end_process},
                                                 "process_order")

    manufacture_method_details_raw_items = frappe.db.sql("""select
mmd.name,mmdi.item_code,mmdi.item_name,mmdi.qty_uom,mmdi.qty_per_unit_made,mmdi.consumption_type,mmdi.stock_uom,mmdi.conversion_factor,mmdi.operand,mmdi.qty_in_stock_uom
from`tabPch Manufacturing Method Details` mmd,`tabPch Manufacturing Method Details RM Child` mmdi where
	mmd.name=mmdi.parent and process_order>=%s and process_order<= %s and pch_method= %s """,
                                                         (start_process_pro_ord_no, end_process_pro_ord_no, method),
                                                         as_dict=1)

    return manufacture_method_details_raw_items

#for packing

@frappe.whitelist()
def get_packing_raw_materials(item_made_json):
    item_made_json = json.loads(item_made_json)
    item_made_list_str = ','.join("'{0}'".format(item_made) for item_made, ob_data in item_made_json.items())

    query = "select mmd.name,mmd.item_code as item_made,mmdi.item_code,mmdi.item_name,mmdi.qty_uom,mmdi.qty_per_unit_made,mmdi.consumption_type,mmdi.stock_uom,mmdi.conversion_factor,mmdi.operand,mmdi.qty_in_stock_uom from`tabPch Manufacturing Method Details` mmd,`tabPch Manufacturing Method Details RM Child` mmdi where mmd.name=mmdi.parent and  mmd.pch_process='Packing'  and mmd.item_code in ( {} )".format(
        item_made_list_str)
    packing_raw_materials = frappe.db.sql(query, as_dict=1)
    return packing_raw_materials


@frappe.whitelist()
def get_child_doc_data(doc_type, parent):
    table = "tab" + doc_type
    # table='`tab'+doc_type+'`'
    sql = "select  * from `" + table + "` where parent='" + parent + "'"
    # sql = "select  * from `"+table+"`"
    doc_data = frappe.db.sql(sql, as_dict=1)
    return doc_data


@frappe.whitelist()
def get_wh_ac_to_location(location_name, wh_type, process):
    wh_name_dic = frappe.db.sql(
        """select outbound_warehouse,inbound_warehouse from `tabPch Locations Child` where parent = %s and process_name = %s """,
        (location_name, process), as_dict=1)
    return wh_name_dic[0][wh_type] if wh_name_dic else None


# Ak
@frappe.whitelist()
def validate_start_and_end_process(start_process, end_process):
    flag = 1;
    st_list = frappe.db.sql(
        """select `process_order` as `start_process_order` from  `tabPch Manufacturing Method Details` where name=%s""",
        (start_process), as_dict=1);
    en_list = frappe.db.sql(
        """select `process_order` as `end_process_order`  from  `tabPch Manufacturing Method Details` where name=%s""",
        (end_process), as_dict=1);
    start_process_order_value = st_list[0]["start_process_order"];
    end_process_order_value = en_list[0]["end_process_order"];
    if (start_process_order_value > end_process_order_value):
        # print('End process cannot occur before start process');
        flag = 0;
    return flag


# raw_material_transactions_start
# pch_locations_id,items
# issue from raw material wh of location
@frappe.whitelist()
def send_material_for_manufacturing(entity):
    entity = json.loads(entity)
    item_payload_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},
                                               "item_payload_account")
    units = entity.get("units_to_be_sr");
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");

    raw_material_warehouse = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},
                                                 "raw_material_warehouse")
    start_process_pro_ord_no = frappe.db.get_value("Pch Manufacturing Method Details",
                                                   {"name": entity.get("start_process")}, "process_order")

    # issue_start
    issue_items_list = []
    for i_row in entity.get("req_items"):
        item_dic = {
            "item_code": i_row.get("item_code"),
            # making a change here "qty":i_row.get("total_qty") was the code before this
            "qty": i_row.get("dispatched_quantity_in_uom"),
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "t_wh": None,
            "s_wh": raw_material_warehouse,
            "item_payload_account": item_payload_account

        }
        issue_items_list.append(item_dic)
    se_issue_entity = {"action": "Material Issue", "items_list": issue_items_list, "company": company}
    # print "se_issue_entity",se_issue_entity
    se_issue = create_stock_entry(se_issue_entity)
    # issue_end
    response = [];
    if se_issue[0]["Exception"] == "Not Occured":

        # issue is done #call_next_transaction #material_rec
        # Response JSON to validate Stock Entry Creation
        response.append({"Name": se_issue[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Issue"});
        # transfer is must
        trans_entity = {
            "items": entity.get("method_items"),
            "s_wh": entity.get("outbound_warehouse"),
            "t_wh": entity.get("target_warehouse"),
            "units_to_be_sr": entity.get("units_to_be_sr"),
            "company": company
        }
        labour_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "labour_account")
        trans_entity["labour_account"] = labour_account
        trans_entity["isAdditionCost"] = 1
        trans_entity["add_amount"] = frappe.db.get_value("Stock Entry", {"name": se_issue[0]["Name"]},
                                                         "total_outgoing_value")
        trans_entity["item_payload_account"] = item_payload_account
        # transfer is must

        start_process_pro_ord_no = int(start_process_pro_ord_no)

        if start_process_pro_ord_no == 1:
            # print "se_issue created 3t:",se_issue
            # receipt fetch method item #Pch Manufacturing Record Child Method (method_items)

            receipt_items_list = []
            for i_row in entity.get("method_items"):
                val = i_row.get("qty_made")
                actual_qty = units * val;
                item_dic = {
                    "item_code": i_row.get("item_made"),
                    "qty": actual_qty,
                    "uom": i_row.get("qty_uom"),
                    "conversion_factor": i_row.get("conversion_factor"),
                    "t_wh": entity.get("outbound_warehouse"),
                    "s_wh": None,
                    "item_payload_account": item_payload_account

                }
                receipt_items_list.append(item_dic)
            se_rec_entity = {"action": "Material Receipt", "items_list": receipt_items_list, "company": company}
            # print "se_rec_entity data",se_rec_entity
            se_receipt = create_stock_entry(se_rec_entity)

            if se_receipt[0]["Exception"] == "Not Occured":
                # print "se_receipt created ",se_receipt
                # print "transfer data ",trans_entity
                response.append(
                    {"Name": se_receipt[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Receipt"});
                se_transfer3 = make_transfer(trans_entity)
                if se_transfer3[0]["Exception"] == "Not Occured":
                    response.append({"Name": se_transfer3[0]["Name"], "Status": "Created",
                                     "Stock Entry Type": "Material Transfer"});
                # return response
                # print "se_transfer3 created ",se_transfer3
                else:
                    response.append({"Name": se_transfer3[0]["Name"], "Status": "Not Created",
                                     "Stock Entry Type": "Material Transfer"});
                    doc1 = frappe.get_doc("Stock Entry", se_issue[0]["Name"]);
                    doc1.docstatus = 2
                    doc1.save()
                    doc2 = frappe.get_doc("Stock Entry", se_receipt[0]["Name"]);
                    doc2.docstatus = 2
                    doc2.save()

            else:
                response.append(
                    {"Name": se_receipt[0]["Name"], "Status": "Not Created", "Stock Entry Type": "Material Receipt"});
                doc1 = frappe.get_doc("Stock Entry", se_issue[0]["Name"]);
                doc1.docstatus = 2
                doc1.save()


        else:
            # print "se_issue created 2t:",se_issue
            # print "transfer data ",trans_entity
            se_transfer2 = make_transfer(trans_entity)
            # print "se_transfer2 created ",se_transfer2
            if se_transfer2[0]["Exception"] == "Not Occured":
                response.append(
                    {"Name": se_transfer2[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Transfer"});
            else:
                response.append({"Name": se_transfer2[0]["Name"], "Status": "Not Created",
                                 "Stock Entry Type": "Material Transfer"});
                doc1 = frappe.get_doc("Stock Entry", se_issue[0]["Name"]);
                doc1.docstatus = 2
                doc1.save()
                #print(response)


    else:
        # print "se_transfer3 created ",se_transfer3
        response.append({"Name": se_issue[0]["Name"], "Status": "Not Created", "Stock Entry Type": "Material Issue"});
    #print(response)
    return response

@frappe.whitelist()
def receive_material_for_manufacturing(entity):
    entity = json.loads(entity)
    labour_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "labour_account")
    item_payload_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},
                                               "item_payload_account")
    units = entity.get("units_s_r")
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    response = [];
    # make_transfer
    # from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
    transfer_items_list = []
    for i_row in entity.get("method_items"):
        val = i_row.get("qty_made")
        actual_qty = units * val;
        item_dic = {
            "item_code": i_row.get("item_made"),
            "qty": actual_qty,
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": entity.get("target_warehouse"),  # subcontractor wh
            "t_wh": entity.get("receiving_warehouse"),  # receiving_warehouse
            "item_payload_account": item_payload_account
        }
        transfer_items_list.append(item_dic)

    se_trans_entity = {"action": "Material Transfer", "items_list": transfer_items_list, "company": company}
    se_trans_entity["add_amount"] = entity.get("subcontracting_rate") * entity.get("units_s_r")
    se_trans_entity["labour_account"] = labour_account
    se_trans_entity["isAdditionCost"] = 1
    se_transfer = create_stock_entry(se_trans_entity)
    # print(se_transfer,"-----------------------------------------------");
    if (se_transfer[0]["Exception"] == "Not Occured"):
        # response.append({"Name":se_transfer,"Status":"Created"});
        response.append({"Name": se_transfer[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Transfer"});
    # print(response)
    # return response
    else:
        response.append(
            {"Name": se_transfer[0]["Name"], "Status": "Not Created", "Stock Entry Type": "Material Transfer"});
    # response.append({"Name":se_transfer,"Status":"Not Created"});
    # print(response)
    return response


#packing type suresh

#create issue data first.use same logic of send material for manufacturing
@frappe.whitelist()
def send_material_for_packing(entity):
    entity = json.loads(entity)
    response = []
    #print "entity send_material_for_packing" ,entity
    labour_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "labour_account")
    item_payload_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},"item_payload_account")
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    raw_material_warehouse = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},"raw_material_warehouse")

    #new code start
    for im_row in entity.get("multiple_method_items"):
        issue_items_list = []
        #print "came inside item made ",im_row.get("item_made")
        for i_row in entity.get("req_items"):
            if im_row.get("item_made") ==  i_row.get("item_made") :
                #print "if passed"
                issue_item_dic = {
                    "item_code": i_row.get("item_code"),
                    "qty": i_row.get("dispatched_quantity_in_uom"),
                    "uom": i_row.get("qty_uom"),
                    "conversion_factor": i_row.get("conversion_factor"),
                    "t_wh": None,
                    "s_wh": raw_material_warehouse,
                    "item_payload_account": item_payload_account

                }
                issue_items_list.append(issue_item_dic)

        #create issue for each item made raw materials
        se_issue_entity = {"action": "Material Issue", "items_list": issue_items_list, "company": company}
        se_issue = create_stock_entry(se_issue_entity)

        transfer_items_list = []
        if se_issue[0]["Exception"] == "Not Occured":
            #create transfer for each item made
            trans_item_dic = {
                "item_code": im_row.get("item_made"),
                "qty": im_row.get("units_s_r"),
                "uom": im_row.get("qty_uom"),
                "conversion_factor": im_row.get("conversion_factor"),
                "s_wh": entity.get("outbound_warehouse"),
                "t_wh": entity.get("target_warehouse"),
                "item_payload_account": item_payload_account
            }
            transfer_items_list.append(trans_item_dic)
            se_trans_entity = {"action": "Material Transfer", "items_list": transfer_items_list, "company": company}
            se_trans_entity["add_amount"] = frappe.db.get_value("Stock Entry", {"name": se_issue[0]["Name"]},"total_outgoing_value")
            se_trans_entity["labour_account"] = labour_account  # only for send material for manufacturing
            se_trans_entity["isAdditionCost"] = 1

            se_transfer2 = create_stock_entry(se_trans_entity)

            if se_transfer2[0]["Exception"] == "Not Occured":
                response.append({"Name": se_transfer2[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Transfer"});
            else:
                response.append({"Name": se_transfer2[0]["Name"], "Status": "Not Created","Stock Entry Type": "Material Transfer"});
                doc1 = frappe.get_doc("Stock Entry", se_issue[0]["Name"]);  # here we are cancelling issue only  but we need to canncel all material transfers as well
                doc1.docstatus = 2
                doc1.save()

        else:
            response.append({"Name": se_issue[0]["Name"], "Status": "Not Created", "Stock Entry Type": "Material Issue"});

    #new code end


    return response

@frappe.whitelist()
def receive_material_from_packing(entity):
    entity = json.loads(entity)
    #print "receive_material_from_packing",entity

    labour_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "labour_account")
    item_payload_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},
                                               "item_payload_account")
    units = entity.get("units_s_r")
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    response = [];
    # make_transfer
    # from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==

    for i_row in entity.get("multiple_method_items"):
        transfer_items_list = []

        item_dic = {
            "item_code": i_row.get("item_made"),
            "qty": i_row.get("units_s_r"),
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": entity.get("target_warehouse"),  # subcontractor wh
            "t_wh": entity.get("receiving_warehouse"),  # receiving_warehouse
            "item_payload_account": item_payload_account
        }
        transfer_items_list.append(item_dic)
        se_trans_entity = {"action": "Material Transfer", "items_list": transfer_items_list, "company": company}
        se_trans_entity["add_amount"] =  i_row.get("packing_labour_amount")
        se_trans_entity["labour_account"] = labour_account
        se_trans_entity["isAdditionCost"] = 1
        se_transfer = create_stock_entry(se_trans_entity)
        # print(se_transfer,"-----------------------------------------------");
        if (se_transfer[0]["Exception"] == "Not Occured"):
            response.append(  {"Name": se_transfer[0]["Name"], "Status": "Created", "Stock Entry Type": "Material Transfer"});
        else: #need to cancel previous transactions if any one failed to create
            response.append({"Name": se_transfer[0]["Name"], "Status": "Not Created", "Stock Entry Type": "Material Transfer"});


    # response.append({"Name":se_transfer,"Status":"Not Created"});
    # print(response)
    return response
#packing type


def make_transfer(trans_entity):
    transfer_items_list = []
    units = trans_entity.get("units_to_be_sr");
    company = trans_entity.get("company")
    for i_row in trans_entity.get("items"):
        val = i_row.get("qty_made")
        actual_qty = units * val;
        item_dic = {
            "item_code": i_row.get("item_made"),
            "qty": actual_qty,
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": trans_entity.get("s_wh"),
            "t_wh": trans_entity.get("t_wh"),
            "item_payload_account": trans_entity.get("item_payload_account")
        }
        transfer_items_list.append(item_dic)
    se_trans_entity = {"action": "Material Transfer", "items_list": transfer_items_list, "company": company}
    se_trans_entity["add_amount"] = trans_entity.get("add_amount")
    se_trans_entity["labour_account"] = trans_entity.get(
        "item_payload_account")  # only for send material for manufacturing
    se_trans_entity["isAdditionCost"] = 1
    se_transfer = create_stock_entry(se_trans_entity)
    return se_transfer


@frappe.whitelist()
def create_stock_entry(se_entity):
    #print "from create_stock_entry se_entity :",se_entity
    # test
    status = []
    try:
        se = frappe.new_doc("Stock Entry")
        se.purpose = se_entity.get("action")
        se.stock_entry_type = se_entity.get("action")
        se.company = se_entity.get("company")


        se.set('items', [])
        for item in se_entity.get("items_list"):
            se_item = se.append('items', {})
            se_item.item_code = item["item_code"]
            se_item.qty = item["qty"]
            se_item.uom = item["uom"]
            se_item.conversion_factor = item["conversion_factor"]
            se_item.expense_account = item["item_payload_account"]  # dif acc
            se_item.stock_uom = frappe.db.get_value("Item", {"name": item["item_code"]}, "stock_uom")
            se_item.basic_rate = 0.01
            if se_entity.get("action") == "Material Transfer":
                se_item.s_warehouse = item["s_wh"]
                se_item.t_warehouse = item["t_wh"]
            if se_entity.get("action") == "Material Issue":
                se_item.s_warehouse = item["s_wh"]
            if se_entity.get("action") == "Material Receipt":
                se_item.t_warehouse = item["t_wh"]

        if se_entity.get("isAdditionCost"):
            se.set('additional_costs', [])
            se_add_cost = se.append('additional_costs', {})
            se_add_cost.description = "Manufacturing Record"
            se_add_cost.expense_account = se_entity.get("labour_account")
            se_add_cost.amount = se_entity.get("add_amount")

        se.save(ignore_permissions=True)
        se.submit()


        frappe.db.commit()
        status.append({"Name": se.name, "Exception": "Not Occured"});

    except Exception as e:
        status.append({"Name": se.name, "Exception": "Occured", "Exception type": e});
        frappe.delete_doc("Stock Entry", se.name)
    return status







# ability to create purchase invoice in future
@frappe.whitelist()
def get_method_based_on_item(item_made):
    method_list = frappe.db.sql("""select parent from `tabPch Manufacturing Method Child` where item_made=%s""",
                                (item_made), as_dict=1);
    methods = [];
    length = len(method_list);
    if (length == 1):
        methods.append(method_list[0]["parent"]);
    else:
        for method in method_list:
            methods.append(method.parent);
    # print(methods);
    return methods


@frappe.whitelist()
def cancel_s_entries(mat_issue, mat_receipt, mat_transfer):
    doc1 = frappe.get_doc("Stock Entry", mat_issue);
    doc2 = frappe.get_doc("Stock Entry", mat_receipt);
    doc3 = frappe.get_doc("Stock Entry", mat_transfer);
    # mrec=frappe.get_doc("Pch Manufacturing Record",

    if (doc1):
        doc1.docstatus = 2
        doc1.save()
    if (doc2):
        doc2.docstatus = 2
        doc2.save()
    if (doc3):
        doc3.docstatus = 2
        doc3.save()

    return "SE deleted"


@frappe.whitelist()
def cancel_single_se(mat_transfer):
    doc1 = frappe.get_doc("Stock Entry", mat_transfer);
    if (doc1):
        doc1.docstatus = 2
        doc1.save()
    return "Single SE deleted"


@frappe.whitelist()
def move_material_internally(entity):
    entity = json.loads(entity)
    units = entity.get("units_s_r")

    labour_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "labour_account")
    item_payload_account = frappe.db.get_value("Pch Locations", {"name": entity.get("location")},"item_payload_account")
    location = entity.get("location");
    company = frappe.db.get_value("Pch Locations", {"name": entity.get("location")}, "company");
    response = [];
    # make_transfer
    # from method_item table  Subcontractor Warehouse== sourch wh and Receiving Warehouse==
    transfer_items_list = []
    for i_row in entity.get("method_items"):
        val = i_row.get("qty_made");
        total_qty = units * val;
        item_dic = {
            "item_code": i_row.get("item_made"),
            "qty": total_qty,
            "uom": i_row.get("qty_uom"),
            "conversion_factor": i_row.get("conversion_factor"),
            "s_wh": entity.get("outbound_warehouse"),
            "t_wh": entity.get("receiving_warehouse"),
            "item_payload_account": item_payload_account

        }
        transfer_items_list.append(item_dic)

    se_trans_entity = {"action": "Material Transfer", "items_list": transfer_items_list, "company": company}

    se_transfer = create_stock_entry(se_trans_entity)

    #print(se_trans_entity);

    #print(se_transfer)
    if (se_transfer[0]["Exception"] == "Not Occured"):
        response.append({"Name": se_transfer, "Status": "Created"});
        #print(response)
        return response
    else:
        response.append({"Name": se_transfer, "Status": "Not Created"});
        #print(response)
        return response


@frappe.whitelist()
def change_doc_status(name):
    doc = frappe.get_doc('Pch Manufacturing Record', {'name': name, 'docstatus': ('<', 2)})
    if (doc):
        doc.docstatus = 2
        doc.save()
    else:
        frappe.throw("No such un-cancelled document")
    return "draft mode"