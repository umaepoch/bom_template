// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Locations', {
	refresh: function(frm) {

});
frappe.ui.form.on("Pch Locations", "get_process", function(frm, cdt, cdn) {
	var process_list =get_process_list();
	var child_doc_data = cur_frm.doc.locations_child;
	if(!child_doc_data){
		set_child_table(process_list);
	}
	else{
		//console.log("yes child doc   exist"+JSON.stringify(child_doc_data));
		var exist_process_list=[] ;
		var extra_process_list =[]
		for (var i=0;i<child_doc_data.length;i++){
			exist_process_list.push(child_doc_data[i]["process_name"])
		}

		for (var i=0;i<process_list.length;i++){
			if(exist_process_list.indexOf(process_list[i]) !== -1){
				 console.log("already_present");
	    } else{
					extra_process_list.push(process_list[i])
	    }
		}

		set_child_table(extra_process_list);

	}

});

function get_process_list(){
	var process_list ;
	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_locations.pch_locations.get_process_list',
		async: false,
		callback: function(r) {
			 if (r.message) {
				 //console.log("process_list ..." + JSON.stringify(r.message));
				 process_list = r.message;
				}
		}
    });
		return process_list;
}

function set_child_table( items_list){
	for (var i=0;i<items_list.length;i++){
	var child = cur_frm.add_child("locations_child");
	frappe.model.set_value(child.doctype, child.name, "process_name", items_list[i]);
	}//end of for loop...
	refresh_field("locations_child");
}
