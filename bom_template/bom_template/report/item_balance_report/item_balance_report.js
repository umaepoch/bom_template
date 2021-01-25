// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Balance Report"] = {
	"filters": [
	{
        "fieldname": "method_filter",
        "label": __("Method"),
        "fieldtype": "Link",
        "options": "Pch Manufacturing Method",
        "reqd": 1,
        "get_query": function() {
		  var item_made_fil = frappe.query_report.get_filter_value('item_made_fil');
		  var item_methods=get_methods(item_made_fil);

          if (item_made_fil){
              if(item_methods.length===1){
                    return {
                                "doctype": "Pch Manufacturing Method",
                                "filters": {
                                    "name": item_methods[0]
                                }
                    }
		      }
          } //end of if
        } //end of get_query
	}, //end of method filter
	{
        "fieldname": "item_made_fil",
        "label": __("Item Made"),
        "fieldtype": "Link",
        "options": "Item"
	}
	],
}

function get_methods(item_made){
	var methods=[];
	frappe.call({
		method:'bom_template.bom_template.report.item_balance_report.item_balance_report.get_method_based_on_item',
		async:false,
		args:{
		"item_made":item_made
		},

		callback:function(r){
		methods=r.message;
		}
	});
	return methods
}