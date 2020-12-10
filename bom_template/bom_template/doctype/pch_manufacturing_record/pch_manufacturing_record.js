// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Manufacturing Record', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Pch Manufacturing Record", "manufacturing_method", function(frm, cdt, cdn) {
    var method_id = cur_frm.doc.manufacturing_method;
    //var readings = fetch_cocpf_readings(cocpf_id);
    frappe.call({
        method: "bom_template.bom_api.get_doc_data",
        args: {
	    "doc_type":"Pch Manufacturing Method",
      "doc_name": method_id,
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                //console.log("method_doc_data" + JSON.stringify(r.message));
								cur_frm.clear_table("method_items");
								var method_doc_data = r.message;
								for (var i=0;i<method_doc_data.length;i++){
								var child = cur_frm.add_child("method_items");
								frappe.model.set_value(child.doctype, child.name, "item_made", method_doc_data[i]['item_made']);
								frappe.model.set_value(child.doctype, child.name, "qty_made_type", method_doc_data[i]['qty_made_type']);
								frappe.model.set_value(child.doctype, child.name, "qty_uom", method_doc_data[i]['qty_uom']);
								frappe.model.set_value(child.doctype, child.name, "qty_made", method_doc_data[i]['qty_made']);
								frappe.model.set_value(child.doctype, child.name, "stock_uom", method_doc_data[i]['stock_uom']);
								frappe.model.set_value(child.doctype, child.name, "conversion_factor", method_doc_data[i]['conversion_factor']);
								frappe.model.set_value(child.doctype, child.name, "operand", method_doc_data[i]['operand']);
								}//end of for loop...
								refresh_field("method_items");
								}
        } //end of callback fun..
    }) //end of frappe call..
});

frappe.ui.form.on("Pch Manufacturing Record", "get_required_items", function(frm, cdt, cdn) {
	//console.log("Button clicked");
	var start_process = cur_frm.doc.start_process;
	var end_process = cur_frm.doc.end_process;

	get_start_end_process_raw_materials(start_process,end_process)
});

frappe.ui.form.on("Pch Manufacturing Record", "location", function(frm, cdt, cdn) {
	var location_name = cur_frm.doc.location;
	var wh_json = fetch_in_out_wh(location_name);
	cur_frm.set_value("source_warehouse", wh_json.inbound_warehouse);
	cur_frm.set_value("target_warehouse",wh_json.outbound_warehouse);
});

function fetch_in_out_wh(location_name){
	var wh_json_temp = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Pch Location Warehouses",
            filters: {
                location: ["=", location_name]
            },
            fieldname: ["outbound_warehouse","inbound_warehouse"]
        },
        async: false,
        callback: function(r) {
					if (r.message) {
					//	console.log("........." + JSON.stringify(r.message));
            wh_json_temp = r.message;
					}

        }
    });
		return wh_json_temp
}


function get_start_end_process_raw_materials(start_process,end_process){

	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_start_end_process_raw_materials',
		args: {
		   "start_process":start_process,
			 "end_process":end_process
		},
		async: false,
		callback: function(r) {
			 if (r.message) {
				//console.log("supplier criticality..." + JSON.stringify(r.message));
				cur_frm.clear_table("req_items");
				var items_list = r.message;
				for (var i=0;i<items_list.length;i++){
				var child = cur_frm.add_child("req_items");
				frappe.model.set_value(child.doctype, child.name, "item_code", items_list[i]['item_code']);
				//frappe.model.set_value(child.doctype, child.name, "consumption_type", items_list[i]['qty_made_type']);
				frappe.model.set_value(child.doctype, child.name, "qty_uom", items_list[i]['uom']);
				frappe.model.set_value(child.doctype, child.name, "stock_uom", items_list[i]['stock_uom']);
				frappe.model.set_value(child.doctype, child.name, "conversion_factor", items_list[i]['conversion_factor']);
				frappe.model.set_value(child.doctype, child.name, "operand", items_list[i]['operand']);
				frappe.model.set_value(child.doctype, child.name, "qty_in_stock_uom", items_list[i]['qty_in_stock_uom']);
				//frappe.model.set_value(child.doctype, child.name, "dispatched_quantity_in_uom", items_list[i]['operand']);
				}//end of for loop...
				refresh_field("req_items");
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
}
