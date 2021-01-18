// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Balance Report"] = {
	"filters": [{
        "fieldname": "item_made_fil",
        "label": __("Item Made"),
        "fieldtype": "Link",
        "options": "Item",

	}
	],
}
