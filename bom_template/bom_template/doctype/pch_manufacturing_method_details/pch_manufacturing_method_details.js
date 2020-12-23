// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt


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
	if(method_name && process_name){
		//validation_start
		var process_flag = process_validation_against_method(method_name,process_name)
		if (process_flag == 1){
			frappe.msgprint("Selected Process : "+ process_name+" is already exist for method : "+method_name +".Please choose unique Process");
			cur_frm.set_value("pch_process", null);
		}else{
			var concat_val = method_name + "-" + process_name
			if(method_name && process_name){
				cur_frm.set_value("meth_pro_con", concat_val);
			}
		}
		//validation_end
	}
});

//Process Order validation:To ensure the Process order is unique across all methods
frappe.ui.form.on("Pch Manufacturing Method Details","process_order",function (frm,cdt,cdn){

	var process_order=cur.frm.doc.process_order;
	console.log('Check');
	var unique_flag;
	unique_flag=process_order_validation(process_order);
	consol
	if(unique_flag===0){
	
		frappe.msgprint('This Process Order has already been used for a Method Process Combination, please enter a new process order number');
		//cur.frm.doc.process_order=0;
	}
	
});

//Process order validation function
function process_order_validation(process_order){
	
	var is_unique_process_order;
	frappe.call({
		method:
		'bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.get_process_order_values',
		async:false,
		args:{
			"process_order":process_order
		},
		
		callback:function(r){
			
			is_unique_process_order=r.message;
		}

	
});
	return is_unique_process_order
}

function process_validation_against_method(method_name,process_name){
	var process_flag ;
	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.process_validation_against_method',
		async: false,
		args:{
			"method_name":method_name,
			"process_name":process_name
		},
		callback: function(r) {
			 if (r.message) {
				 process_flag = r.message;
				}
		}
    });
		return process_flag;
}