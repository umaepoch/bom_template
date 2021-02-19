// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Global Process', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Pch Global Process',"is_global",function(frm,cdt,cdn){

	console.log('ok');
	cur_frm.set_value("item_group","");
	cur_frm.refresh_field("item_group");
	var check;
	check=check_is_global();
	console.log(check);
	if(check[0]["Is Global"]==1)
	{
		var update;
		var name=check[0]["Name"];
		frappe.confirm(
    'Are you sure you want to set this as a global process?',
    function(){
        	  show_alert('This configuration is now set as a Global Process Order')
        	  update=update_is_global(name);
        	  cur_frm.refresh();
        	  
    },
    function(){
      
        window.close();
        cur_frm.set_value("is_global",0)
    }
)
	}

	
});
function check_is_global(){


	var check;
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_global_process.pch_global_process.global_po_check",
		async:false,
		callback:function(r){
		
			check=r.message
		}
	
	});
	
	return check

}
function update_is_global(name){

	var check;
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_global_process.pch_global_process.update_gp_check",
		async:false,
		args:{
		
			"name":name
		
		},
		callback:function(r){
		
			check=r.message
		}
	
	});
	
	return check



}

