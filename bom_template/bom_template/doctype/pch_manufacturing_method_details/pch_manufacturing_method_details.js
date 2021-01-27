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
	
	
		//Ak
	var l1;
	//var method_name=cur_frm.doc.pch_method;
	var item_made=cur_frm.doc.item_code;
	console.log(item_made);
	
	l1=get_child_items(method_name,item_made);
	
	if(method_name)
	
	{
		var child=cur_frm.add_child("items");
		console.log(child)
		frappe.model.set_value(child.doctype,child.name,"item_code",l1[0]["item_made"]);
		frappe.model.set_value(child.doctype,child.name,"uom",l1[0]["qty_uom"]);
		frappe.model.set_value(child.doctype,child.name,"qty",l1[0]["qty_made"]);
		frappe.model.set_value(child.doctype,child.name,"conversion_factor",l1[0]["conversion_factor"]);
		var prod=l1[0]["conversion_factor"]*l1[0]["qty_made"];
		frappe.model.set_value(child.doctype,child.name,"qty_in_stock_uom",prod);
		refresh_field("items");
	}


	else{
	
		cur_frm.clear_table("items"); 
		cur_frm.refresh_fields();
	
	}
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




frappe.ui.form.on("Pch Manufacturing Method Details","item_code",function(frm,cdt,cdn){
	
	
	
	
	var item_chosen=cur_frm.doc.item_code;
	var item_methods=get_methods(item_chosen);
	//console.log(item_methods);
	//var len=item_methods.length;
	//console.log(item_methods[0]["parent"]);
	if(item_chosen)
	{
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
	}
	else
	{
		cur_frm.set_value("pch_method",null);
	
	}


});

function get_child_items(parent,item_made){

	var l1;
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.get_method_details",
args:{

	"parent":parent,
	"item_made":item_made
},
async:false,
callback:function(r){


	l1=r.message;
}
});
	return l1;
}

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

frappe.ui.form.on("Pch Manufacturing Method Details RM Child",{qty_per_unit_made:function(frm,cdt,cdn){

	console.log("Trigger");
	var row=frappe.get_doc(cdt,cdn);
	
	//row.conversion_factor=11;
	console.log(row.item_code);
	
	var resp=populate_uoms_and_cf(row.item_code);
	
	row.conversion_factor=resp[0]["conversion_factor"];
	row.qty_uom=resp[0]["uom"];
	row.stock_uom=resp[0]["stock_uom"];
	var qty_per_unit=row.qty_per_unit_made;
	var conv_fact=row.conversion_factor
	var prod=qty_per_unit*conv_fact;
	console.log(qty_per_unit,conv_fact);
	row.qty_in_stock_uom=prod;

	}	
	});
function populate_uoms_and_cf(item_code){

	var r1;
	frappe.call({
	method:"bom_template.bom_template.doctype.pch_manufacturing_method_details.pch_manufacturing_method_details.populate_uom_cf",
	args:{
		"item_code":item_code
	},
	async:false,
	callback:function(r){
	
		if(r.message){
		
			r1=r.message;
		}
	}



});
	console.log(r1);
	return r1
}

