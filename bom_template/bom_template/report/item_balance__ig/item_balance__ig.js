// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Balance  Ig"] = {
	"filters": [
	{
        "fieldname": "group_wise",
        "label": __("Group Wise"),
        "fieldtype": "Select",
        "options": ["Item","Item Group"],
        "reqd": 1
	},
	{
        "fieldname": "item_filter",
        "label": __("Item"),
        "fieldtype": "Link",
        "options": "Item",
        "reqd": 0
	},
	{
        "fieldname": "ig_filter",
        "label": __("Item Group"),
        "fieldtype": "Link",
        "options": "Item Group",
        "reqd": 0
	}

	]
}
