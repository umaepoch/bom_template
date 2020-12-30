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

	var process_order=cur_frm.doc.process_order;
	var method_name=cur_frm.doc.pch_method;
	console.log('Check');
	console.log(process_order);
	console.log(method_name);
	var unique_flag;
	unique_flag=process_order_validation(process_order,method_name);
	console.log(unique_flag);
	if(unique_flag==0){
	
		frappe.msgprint('This Process Order has already been set for a Method Process Combination, please enter a new Process Order number');
		cur_frm.set_value("process_order",null);
	}
	
});


frappe.ui.form.on("Pch Manufacturing Method Details","pch_method",function(frm,cdt,cdn){

	var l1;
	var method_name=cur_frm.doc.pch_method;
	
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.get_item_details",
args:{

	"parent":method_name
},
async:false,
callback:function(r){


	l1=r.message;
	//console.log(l1);
	for(var i=0;i<l1.length;i++)
	{
	
		var child=cur_frm.add_child("items");
		console.log(child)
		frappe.model.set_value(child.doctype,child.name,"item_code",l1[i]["item_made"]);
		frappe.model.set_value(child.doctype,child.name,"uom",l1[i]["qty_uom"]);
		frappe.model.set_value(child.doctype,child.name,"qty",l1[i]["qty_made"]);
		
	}
refresh_field("items");

}
});
	
});

frappe.ui.form.on("Pch Manufacturing Method Details","item",function(frm,cdt,cdn){
	
	
	
	
	var item_chosen=cur_frm.doc.item;
	var item_methods=get_methods(item_chosen);
	//console.log(item_methods);
	//var len=item_methods.length;
	//console.log(item_methods[0]["parent"]);
	if(item_methods.length===1){
		
		cur_frm.set_value("pch_method",item_methods[0]);
	}

	else
	{
	
			cur_frm.set_query("pch_method", function(frm, cdt, cdn) {
//console.log(wh_n);
return {
"filters": [
["Pch Manufacturing Method", "name", "in", item_methods]



]
}
});
	
	
	}


});

//Process order validation function
function process_order_validation(process_order,method_name){
	
	var is_unique_process_order;
	frappe.call({
		method:
		'bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.get_process_order_values',
		async:false,
		args:{
			"process_order":process_order,
			"method_name":method_name
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

function get_methods(item_made){
	var methods=[];
	frappe.call({
	
		method:'bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.get_method_based_on_item',
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
