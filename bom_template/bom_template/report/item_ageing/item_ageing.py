# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt
from erpnext.stock.utils import update_included_uom_in_report
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from datetime import datetime
from datetime import date

def execute(filters=None):
	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)
	sl_entries = get_stock_ledger_entries(filters, items)
	item_details = get_item_details(items, sl_entries, include_uom)
	opening_row = get_opening_balance(filters, columns)
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))

	data = []
	conversion_factors = []
	check_data = []

	issue_list = []
	receive_list = []
	if opening_row:
		data.append(opening_row)

	actual_qty = stock_value = 0

	#print "sl_entries",sl_entries

	available_serial_nos = {}
	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		row_data = []

		if sle.get("actual_qty") > 0:
			receive_list.append(sle)
		else:
			issue_list.append(sle)

		check_data.append([sle.date, sle.item_code, item_detail.item_name, item_detail.item_group,
						   item_detail.brand, item_detail.description, sle.warehouse,
						   item_detail.stock_uom, sle.actual_qty, sle.qty_after_transaction,
						   (sle.incoming_rate if sle.actual_qty > 0 else 0.0),
						   sle.valuation_rate, sle.stock_value, sle.voucher_type, sle.voucher_no,
						   sle.batch_no, sle.serial_no, sle.project, sle.company])

		if include_uom:
			conversion_factors.append(item_detail.conversion_factor)

		receive_date_wise_dic = {}
		for receive_list_date_data in receive_list:
			formatted_date = frappe.utils.formatdate(receive_list_date_data.get("date"), "yyyy-mm-dd")

			if receive_date_wise_dic.get(formatted_date):
				receive_date_wise_dic[formatted_date]["actual_qty"] += receive_list_date_data.get("actual_qty")
			else:
				receive_date_wise_dic[formatted_date] = receive_list_date_data

		# print "receive_date_wise_dic",receive_date_wise_dic

		sent_date_wise_dic = {}
		for issue_list_date_data in issue_list:
			formatted_date = frappe.utils.formatdate(issue_list_date_data.get("date"), "yyyy-mm-dd")

			if sent_date_wise_dic.get(formatted_date):
				sent_date_wise_dic[formatted_date]["actual_qty"] += issue_list_date_data.get("actual_qty")
			else:
				sent_date_wise_dic[formatted_date] = issue_list_date_data

		item_age_calculated_rows = get_item_age_calculated_rows(receive_date_wise_dic, sent_date_wise_dic)
		for date, item_age_calculated_row_list in sorted(item_age_calculated_rows.items()):
			for item_age_calculated_row_dic in item_age_calculated_row_list:
				row_dic = {
					"date": date,
					"item_code": item_age_calculated_row_dic.get("item_code"),
					"karigar_wh": item_age_calculated_row_dic.get("warehouse"),
					"recd_qty": item_age_calculated_row_dic.get("in"),
					"sent_qty": item_age_calculated_row_dic.get("out"),
					"average_ageing": item_age_calculated_row_dic.get("age")
				}
				data.append(row_dic)


	return columns, data

def update_available_serial_nos(available_serial_nos, sle):
	serial_nos = get_serial_nos(sle.serial_no)
	key = (sle.item_code, sle.warehouse)
	if key not in available_serial_nos:
		available_serial_nos.setdefault(key, [])

	existing_serial_no = available_serial_nos[key]
	for sn in serial_nos:
		if sle.actual_qty > 0:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)
		else:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)

	sle.balance_serial_no = '\n'.join(existing_serial_no)

def get_columns():
	#25 columns now ,29 columns now
	columns = []
	for col in range(7):
		columns.append("")
	columns[0] = {
		"label": ("Date"),
		"fieldname": "date",
		"width": 100
	}
	columns[1] = {
		"label": ("Item"),
		"fieldname": "item_code",
		"width": 100,
		"fieldtype": "Link",
		"options": "Item"
	}
	columns[2] = {
		"label": ("Karigar Wh"),
		"fieldname": "karigar_wh",
		"width": 100,
		"fieldtype": "Link",
		"options": "Warehouse"
	}

	columns[3] = {
		"label": ("In"),
		"fieldname": "recd_qty",
		"width": 100
	}
	columns[4] = {
		"label": ("Out"),
		"fieldname": "sent_qty",
		"width": 100
	}
	columns[5] = {
		"label": ("Average Ageing"),
		"fieldname": "average_ageing",
		"width": 100
	}
	return columns


def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = 'and sle.item_code in ({})'\
			.format(', '.join([frappe.db.escape(i) for i in items]))

	return frappe.db.sql("""select concat_ws(" ", posting_date, posting_time) as date,
			item_code, warehouse, actual_qty, qty_after_transaction, incoming_rate, valuation_rate,
			stock_value, voucher_type, voucher_no, batch_no, serial_no, company, project, stock_value_difference
		from `tabStock Ledger Entry` sle
		where company = %(company)s and
			posting_date between %(from_date)s and %(to_date)s
			{sle_conditions}
			{item_conditions_sql}
			order by posting_date asc, posting_time asc, creation asc"""\
		.format(
			sle_conditions=get_sle_conditions(filters),
			item_conditions_sql = item_conditions_sql
		), filters, as_dict=1)

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sl_entries, include_uom):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sl_entries]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if include_uom:
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s" \
			% frappe.db.escape(include_uom)

	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item
			{cf_join}
		where
			item.name in ({item_codes})
	""".format(cf_field=cf_field, cf_join=cf_join, item_codes=','.join(['%s'] *len(items))), items, as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details

def get_sle_conditions(filters):
	conditions = []
	if filters.get("warehouse"):
		warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
		if warehouse_condition:
			conditions.append(warehouse_condition)
	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")
	if filters.get("batch_no"):
		conditions.append("batch_no=%(batch_no)s")
	if filters.get("project"):
		conditions.append("project=%(project)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_opening_balance(filters, columns):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle
	last_entry = get_previous_sle({
		"item_code": filters.item_code,
		"warehouse_condition": get_warehouse_condition(filters.warehouse),
		"posting_date": filters.from_date,
		"posting_time": "00:00:00"
	})
	row = {}
	row["item_code"] = _("'Opening'")
	for dummy, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
			row[v] = last_entry.get(v, 0)

	return row

def get_warehouse_condition(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return " exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
			warehouse_details.rgt)

	return ''

def get_item_group_condition(item_group):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		return "item.item_group in (select ig.name from `tabItem Group` ig \
			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
			item_group_details.rgt)

	return ''

def get_item_age_calculated_rows(receive_date_wise_dic,sent_date_wise_dic):

	initial_receive_item_age_rows = {}
	# calculate initial age and bal qty here
	for receive_date, receive_date_data in sorted(receive_date_wise_dic.items()):
		age = 10
		# update this age for all receive date rows
		today_date = frappe.utils.nowdate()
		today_date_temp = frappe.utils.formatdate(today_date, "yyyy-mm-dd");

		receive_date_data["age"] = get_age_in_days(today_date,receive_date)
		receive_date_data["bal_qty_temp"] = receive_date_data.get("actual_qty")
		initial_receive_item_age_rows.update({receive_date: receive_date_data})

	#print ("initial_receive_item_age_rows first",initial_receive_item_age_rows)

	report_json_data = {}
	sent_date_age = 2
	today = 1
	updated_initial_receive_item_age_rows = {}  # received date updated balance qty

    for sent_date, sent_date_data in sorted(sent_date_wise_dic.items()):
        qty_needed_to_sent = abs(sent_date_data.get("actual_qty"))
        qty_assigned_from_qty_to_be_sent = 0
        qty_left_from_qty_to_be_sent = qty_needed_to_sent

        updated_initial_receive_item_age_rows_temp_rec_loop = initial_receive_item_age_rows

        for receive_date, initial_receive_item_age_row in sorted(initial_receive_item_age_rows.items()):

            bal_qty_in_rec_date_data = updated_initial_receive_item_age_rows_temp_rec_loop[receive_date]["bal_qty_temp"]

            if bal_qty_in_rec_date_data > 0:  # checking stock against received date

                if bal_qty_in_rec_date_data > qty_left_from_qty_to_be_sent:

                    sent_row_data = {}
                    sent_row_data["warehouse"] = initial_receive_item_age_row["warehouse"]
                    sent_row_data["item_code"] = initial_receive_item_age_row["item_code"]
                    sent_row_data["actual_qty"] = initial_receive_item_age_row["actual_qty"]
                    sent_age_cal = initial_receive_item_age_row["age"] - sent_date_age
                    sent_row_data["age"] = get_age_in_days(sent_date, receive_date)
                    sent_row_data["in"] = qty_left_from_qty_to_be_sent
                    sent_row_data["out"] = qty_left_from_qty_to_be_sent
                    sent_row_data["trans_type"] = "sent"

                    updated_initial_receive_item_age_rows_temp_rec_loop[receive_date][
                        "bal_qty_temp"] = bal_qty_in_rec_date_data - qty_left_from_qty_to_be_sent

                    qty_left_from_qty_to_be_sent = qty_left_from_qty_to_be_sent - sent_row_data["out"]
                    qty_assigned_from_qty_to_be_sent = qty_assigned_from_qty_to_be_sent + sent_row_data["out"]

                    # sent row data update
                    if report_json_data.get(receive_date):
                        report_json_data[receive_date].append(sent_row_data)
                    else:
                        report_json_data[receive_date] = [sent_row_data]

                    break

                elif bal_qty_in_rec_date_data == qty_left_from_qty_to_be_sent:
                    sent_row_data = {}
                    sent_row_data["warehouse"] = initial_receive_item_age_row["warehouse"]
                    sent_row_data["item_code"] = initial_receive_item_age_row["item_code"]
                    sent_row_data["actual_qty"] = initial_receive_item_age_row["actual_qty"]
                    sent_row_data["age"] = get_age_in_days(sent_date, receive_date)
                    sent_row_data["in"] = qty_left_from_qty_to_be_sent
                    sent_row_data["out"] = qty_left_from_qty_to_be_sent
                    sent_row_data["trans_type"] = "sent"

                    updated_initial_receive_item_age_rows_temp_rec_loop[receive_date][
                        "bal_qty_temp"] = bal_qty_in_rec_date_data - qty_left_from_qty_to_be_sent

                    # sent row data update
                    if report_json_data.get(receive_date):
                        report_json_data[receive_date].append(sent_row_data)
                    else:
                        report_json_data[receive_date] = [sent_row_data]

                    qty_left_from_qty_to_be_sent = qty_left_from_qty_to_be_sent - sent_row_data["out"]
                    qty_assigned_from_qty_to_be_sent = qty_assigned_from_qty_to_be_sent + sent_row_data["out"]
                    break

                else:
                    qty_can_be_sent_from_receive = bal_qty_in_rec_date_data
                    sent_row_data = {}
                    sent_row_data["warehouse"] = initial_receive_item_age_row["warehouse"]
                    sent_row_data["item_code"] = initial_receive_item_age_row["item_code"]
                    sent_row_data["actual_qty"] = initial_receive_item_age_row["actual_qty"]
                    sent_row_data["age"] = get_age_in_days(sent_date, receive_date)
                    sent_row_data["in"] = qty_can_be_sent_from_receive
                    sent_row_data["out"] = qty_can_be_sent_from_receive
                    sent_row_data["trans_type"] = "sent"

                    updated_initial_receive_item_age_rows_temp_rec_loop[receive_date][
                        "bal_qty_temp"] = bal_qty_in_rec_date_data - qty_can_be_sent_from_receive

                    qty_left_from_qty_to_be_sent = qty_left_from_qty_to_be_sent - sent_row_data["out"]
                    qty_assigned_from_qty_to_be_sent = qty_assigned_from_qty_to_be_sent + sent_row_data["out"]

                    # sent row data update
                    if report_json_data.get(receive_date):
                        report_json_data[receive_date].append(sent_row_data)
                    else:
                        report_json_data[receive_date] = [sent_row_data]

                    if qty_left_from_qty_to_be_sent > 0:
                        continue
                    else:
                        break

        # updation for receive loop calculation
        initial_receive_item_age_rows = updated_initial_receive_item_age_rows_temp_rec_loop  # each recive for loop will have updated receive balance qty
        # updation for total received date calculatiom
        updated_initial_receive_item_age_rows = updated_initial_receive_item_age_rows_temp_rec_loop

    for receive_date, initial_receive_item_age_row in sorted(updated_initial_receive_item_age_rows.items()):

        if initial_receive_item_age_row.get("bal_qty_temp") > 0:
            receive_row_data = {}
            receive_row_data["warehouse"] = initial_receive_item_age_row["warehouse"]
            receive_row_data["item_code"] = initial_receive_item_age_row["item_code"]
            receive_row_data["actual_qty"] = initial_receive_item_age_row["actual_qty"]

            receive_row_data["age"] = initial_receive_item_age_row["age"]
            receive_row_data["in"] = initial_receive_item_age_row["bal_qty_temp"]
            receive_row_data["trans_type"] = "receive"

            # receive row data update
            #report_json_data[receive_date] = [receive_row_data]

            if report_json_data.get(receive_date):
                report_json_data[receive_date].append(receive_row_data)
            else:
                report_json_data[receive_date] = [receive_row_data]



		#print "report_json_data", report_json_data

    return  report_json_data







def get_age_in_days(from_date , to_date):
	from_date = datetime.strptime(from_date, '%Y-%m-%d')
	to_date = datetime.strptime(to_date, '%Y-%m-%d')
	age = from_date - to_date
	return  age.days


@frappe.whitelist()
def calculateAge(posting_date):
	posting_date = "1996-02-29"
	today = date.today()
	dtt = datetime.strptime(posting_date, '%Y-%m-%d')
	dt = dtt.date()
	age = today - dt
	return  age.days