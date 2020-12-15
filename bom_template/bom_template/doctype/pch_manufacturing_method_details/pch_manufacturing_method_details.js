// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Manufacturing Method Details', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Pch Manufacturing Method Details", "pch_method", function(frm, cdt, cdn) {
	console.log("pch_process filed trigger  working")

	var method_name = cur_frm.doc.pch_method;
	var process_name = cur_frm.doc.pch_process;
	var concat_val = method_name + "-" + process_name

	if(method_name && process_name){
		cur_frm.set_value("meth_pro_con", concat_val);
	}
	//cur_frm.set_value("target_warehouse",wh_json.outbound_warehouse);
});




frappe.ui.form.on("Pch Manufacturing Method Details", "pch_process", function(frm, cdt, cdn) {
	var method_name = cur_frm.doc.pch_method;
	var process_name = cur_frm.doc.pch_process;
	var concat_val = method_name + "-" + process_name
	if(method_name && process_name){
		cur_frm.set_value("meth_pro_con", concat_val);
	}
});
