// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Manufacturing Record', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Pch Manufacturing Record", "manufacturing_method", function(frm, cdt, cdn) {
    var method_id = cur_frm.doc.manufacturing_method;
    //var readings = fetch_cocpf_readings(cocpf_id);
		if(method_id){
			console.log(" doc api method_id",method_id);

			frappe.call({
	        method: "bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_child_doc_data",
	        args: {
		    "doc_type":"Pch Manufacturing Method Child",
	      "parent": method_id,
	        },
	        async: false,
	        callback: function(r) {
	            if (r.message) {
	                console.log("method_doc_data" + JSON.stringify(r.message));
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
		}

});


frappe.ui.form.on("Pch Manufacturing Record", "get_required_items", function(frm, cdt, cdn) {
	//console.log("Button clicked");
	//validation  start_process,end_process,manufacturing_method are mandatory to run this method
	var start_process = cur_frm.doc.start_process;
	var end_process = cur_frm.doc.end_process;
	var method = cur_frm.doc.manufacturing_method;

	set_start_end_process_raw_materials(start_process,end_process,method)
});


//what if selected process or location has no wh details?
frappe.ui.form.on("Pch Manufacturing Record", "start_process", function(frm, cdt, cdn) {
	var location_name = cur_frm.doc.location;
	var start_process_temp = cur_frm.doc.start_process;
	if (location_name && start_process_temp){
		var process_name = get_process_name(start_process_temp)
		console.log("process_name",process_name)
		var outbound_warehouse_temp = get_wh_ac_to_location(location_name,"outbound_warehouse",process_name);
		console.log("outbound_warehouse_temp",outbound_warehouse_temp)
		cur_frm.set_value("outbound_warehouse", outbound_warehouse_temp);
	}

});

frappe.ui.form.on("Pch Manufacturing Record","end_process",function(frm,cdt,cdn){
	var validation_flag = end_process_field_validation();
	if (validation_flag == 1){
		var location_name = cur_frm.doc.location;
		var end_process_temp = cur_frm.doc.end_process;
		if (location_name && end_process_temp){
			var process_name = get_process_name(end_process_temp)
			var inbound_warehouse_temp = get_wh_ac_to_location(location_name,"inbound_warehouse",process_name);
			cur_frm.set_value("receiving_warehouse", inbound_warehouse_temp);
		}
	}
});



function set_start_end_process_raw_materials(start_process,end_process,method){
	console.log("method",method)

	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_start_end_process_raw_materials',
		args: {
		   "start_process":start_process,
			 "end_process":end_process,
			 "method":method
		},
		async: false,
		callback: function(r) {
			 if (r.message) {
				console.log("raw material json..." + JSON.stringify(r.message));
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
				frappe.model.set_value(child.doctype, child.name, "mmd", items_list[i]['name']);
				//frappe.model.set_value(child.doctype, child.name, "dispatched_quantity_in_uom", items_list[i]['operand']);
				}//end of for loop...
				refresh_field("req_items");
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
}

function end_process_field_validation(){
	var validation_flag = 1
	var start_process=cur_frm.doc.start_process;
	var end_process=cur_frm.doc.end_process;
	//var check;
	var validate_value=process_order_details(start_process,end_process);
	console.log(validate_value);

	if(validate_value == 0){
		frappe.msgprint("Process Order incorrect. End Process cannot occur before the Start Process, please re-check the sequence");
		frm.set_value('end_process',"");
		validation_flag = 0
	}
	return validation_flag;
}

function process_order_details(start_process,end_process){

	var is_valid_flag;
	frappe.call({
  method:"bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.validate_start_and_end_process",
	args:{

		"start_process":start_process,
		"end_process":end_process

	     },
	async:false,
	callback:function(r){

	is_valid_flag=r.message;
	}
});
return is_valid_flag
}

function get_wh_ac_to_location(location_name,wh_type,process){
	var wh_name = "";
	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_wh_ac_to_location',
		args: {
			 "location_name":location_name,
			 "wh_type":wh_type,
			 "process":process
		},
		async: false,
		callback: function(r) {
			 if (r.message) {
				 wh_name = r.message
				}
		}
		});
		return wh_name
}

function get_process_name(mmd_id){
	var process = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Pch Manufacturing Method Details",
            filters: {
							name: ["=", mmd_id]
            },
            fieldname: ["pch_process"] //"outbound_warehouse","inbound_warehouse"
        },
        async: false,
        callback: function(r) {
					if (r.message) {
					//	console.log("........." + JSON.stringify(r.message));
            process = r.message.pch_process;
					}

        }
    });
		return process
}
