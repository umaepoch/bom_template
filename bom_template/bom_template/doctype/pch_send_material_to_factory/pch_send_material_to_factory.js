// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt


frappe.ui.form.on('Pch Send Material to Factory', {
	refresh: function(frm) {
	var button_visiblity_record_types = ["Send Material to Factory","Send Material to Corporate"]

	if(cur_frm.doc.docstatus == 1 &&  button_visiblity_record_types.includes(cur_frm.doc.record_type) ){
	frm.add_custom_button(__("Make Receive"), function() {
	var response = create_receive_transaction(cur_frm.doc);
	if(response[0]["Status"]=="Created")
		{
			frappe.msgprint("Receive Transaction has been created :"+response[0]["Name"])
		}

    });//end of buuton trigger

    }

	}
});



frappe.ui.form.on('Pch Send Material to Factory','on_submit',function(frm,cdt,cdn){
	console.log("On submit");
	var record=cur_frm.doc.record_type;
	if(record=="Send Material to Factory")
	{
		var response=send_material_to_factory(cur_frm.doc);
		//console.log(response);

		if(response[0]["Status"]=="Created")
		{
			frappe.msgprint("Stock Entry for"+" "+response[0]["Stock Entry Type"]+" "+"has been made"+" "+"ID of the corresponding Stock Entry is"+" "+response[0]["Name"])
		}

	}
	/*new approch store :
	on submit  of "Send Material to Factory" create "receive" on draft mode with valuation rates from stock entry issue
	or save the record transaction id on stock entry child table or parent table use this as reference and fetch basic rate from this.
	try creating basic rate of receipt transaction manually first
	*/

	else if (record=="Receive Material at Factory")
	{
		console.log('ok');
		var response=receive_material_at_factory(cur_frm.doc);
		console.log(response);
		if(response[0]["Status"]=="Created")
		{
			frappe.msgprint("Stock Entry for"+" "+response[0]["Stock Entry Type"]+" "+"has been made"+" "+"ID of the corresponding Stock Entry is"+" "+response[0]["Name"])
		}
	}


	else if (record=="Send Material to Corporate") //factory  to  corparate
	{
		console.log('ok');
		var response=send_material_to_corporate(cur_frm.doc);
		console.log(response);
		if(response[0]["Status"]=="Created")
		{
			frappe.msgprint("Stock Entry for"+" "+response[0]["Stock Entry Type"]+" "+"has been made"+" "+"ID of the corresponding Stock Entry is"+" "+response[0]["Name"])
		}
	}
	else if (record=="Receive Material at Corporate")
	{
		console.log('ok');
		var response=receive_material_at_corporate(cur_frm.doc);
		console.log(response);
		if(response[0]["Status"]=="Created")
		{
			frappe.msgprint("Stock Entry for"+" "+response[0]["Stock Entry Type"]+" "+"has been made"+" "+"ID of the corresponding Stock Entry is"+" "+response[0]["Name"])
		}
	}
	else
	{
		console.log(' ');
	}
});

frappe.ui.form.on("Pch Send Material to Factory","corporate_warehouse",function(frm,cdt,cdn){

	var item=cur_frm.doc.item_made;
	var start_process=cur_frm.doc.start_process;
	var end_process=cur_frm.doc.end_process;
	var method=cur_frm.doc.manufacturing_method;
	var units_s_r=cur_frm.doc.units_s_r;
	var r=get_reqd_items(item,start_process,end_process,method);
	console.log(r);
	cur_frm.clear_table("items_required");

	for(var i=0;i<r.length;i++)
	{

		var child=cur_frm.add_child("items_required");
		var total_qty = units_s_r * r[i]['qty_per_unit_made']
		/*frappe.model.set_value(child.doctype, child.name, "item_code", r[i]['item_name']);
		frappe.model.set_value(child.doctype, child.name, "qty_uom", r[i]['qty_uom']);
		frappe.model.set_value(child.doctype, child.name, "qty_per_unit_made", r[i]['qty_per_unit_made']);
		frappe.model.set_value(child.doctype, child.name, "consumption_type", r[i]['consumption_type']);
		frappe.model.set_value(child.doctype, child.name, "stock_uom", r[i]['stock_uom']);
		frappe.model.set_value(child.doctype, child.name, "conversion_factor", r[i]['conversion_factor']);
		frappe.model.set_value(child.doctype, child.name, "qty_in_stock_uom", r[i]['qty_per_unit_made']);*/
		frappe.model.set_value(child.doctype, child.name, "item_code", r[i]['item_name']);
				frappe.model.set_value(child.doctype, child.name, "qty_uom", r[i]['qty_uom']);
				frappe.model.set_value(child.doctype, child.name, "qty_per_unit_made", r[i]['qty_per_unit_made']);
				frappe.model.set_value(child.doctype, child.name, "qty_in_stock_uom", r[i]['qty_in_stock_uom']);
				frappe.model.set_value(child.doctype, child.name, "total_qty",total_qty);
				//frappe.model.set_value(child.doctype, child.name, "qty_of_raw_material_being_sent", quantity_to_be_sent);
				frappe.model.set_value(child.doctype, child.name, "consumption_type", r[i]['consumption_type']);
				frappe.model.set_value(child.doctype, child.name, "stock_uom", r[i]['stock_uom']);
				frappe.model.set_value(child.doctype, child.name, "conversion_factor", r[i]['conversion_factor']);
				frappe.model.set_value(child.doctype, child.name, "mmd", r[i]['name']);
				//frappe.model.set_value(child.doctype, child.name, "dispatched_quantity_in_uom",dispatched_qty);
				frappe.model.set_value(child.doctype, child.name, "operand", r[i]['operand']);


	}
	refresh_field("items_required");
});
function get_reqd_items(item,start_process,end_process,method){

	var resp;
	frappe.call({
				method:"bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.get_items",
args:{
"item":item,
"start_process":start_process,
"end_process":end_process,
"method":method},
async:false,
callback:function(r){

	if(r.message){

		 resp=r.message;
	}
}

	})
	return resp;

}
frappe.ui.form.on('Pch Send Material to Factory','item_made',function(frm,cdt,cdn){


	var item=cur_frm.doc.item_made;
	var r=get_available_methods(item);
	console.log(r);

	if(item)
	{
	  cur_frm.set_query("manufacturing_method", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Pch Manufacturing Method", "name", "in", r]



                ]
            }
		});

        cur_frm.refresh_field("manufacturing_method");
	}
	else
	{

		cur_frm.set_value("manufacturing_method","");
		cur_frm.set_value("start_process","");
		cur_frm.set_value("end_process","");
		cur_frm.clear_table("items_required");
		cur_frm.refresh_fields
	}


});

function get_available_methods(item){

	var resp;
	frappe.call({
				method:"bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.set_available_methods",
args:{
"item":item
},
async:false,
callback:function(r){

	if(r.message){

		 resp=r.message;
	}
}

	})
	return resp;




}
frappe.ui.form.on('Pch Send Material to Factory','end_process',function(frm,cdt,cdn){

	var sp=cur_frm.doc.start_process;
	var ep=cur_frm.doc.end_process;
	var flag=get_process_orders(sp,ep);
	console.log(flag);
	if(flag==1)
	{
		frappe.msgprint('The Start Process Order cannot be greater than the End Process Order! Please re enter the Start Process and End Process fields');
		cur_frm.set_value('start_process',"");
		cur_frm.set_value('end_process',"");
	}


});

function get_process_orders(start_process,end_process){

	var resp;
	frappe.call({
				method:"bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.validate_process_orders",
args:{
"start_process":start_process,
"end_process":end_process
},
async:false,
callback:function(r){

	if(r.message){

		 resp=r.message;
	}
}

	})

	return resp;




}
frappe.ui.form.on('Pch Send Material to Factory','manufacturing_method',function(frm,cdt,cdn){


	var method=cur_frm.doc.manufacturing_method;
	var r=get_available_processes(method);
	console.log(r)

	  cur_frm.set_query("start_process", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Pch Manufacturing Process", "name", "in", r]



                ]
            }
		});

        cur_frm.refresh_field("start_process");



	  cur_frm.set_query("end_process", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Pch Manufacturing Process", "name", "in", r]



                ]
            }
		});

        cur_frm.refresh_field("end_process");



});
function get_available_processes(method){

	var resp;
	frappe.call({
				method:"bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.set_available_processes",
args:{
"method":method
},
async:false,
callback:function(r){

	if(r.message){

		 resp=r.message;
	}
}

	})
	return resp;




}
//Transaction

function send_material_to_factory(doc_object){



	var items_being_sent=doc_object.items_required;
	var corporate_warehouse=doc_object.corporate_warehouse;
	var receiving_warehouse=doc_object.receiving_warehouse;
	var location=doc_object.location;
	var resp;
	var entity={

		"items_being_sent":items_being_sent,
		"corporate_warehouse":corporate_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"location":location
	}
		frappe.call({
			method: "bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.send_material_to_factory",
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log( JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	console.log(resp)
	return resp

}
function receive_material_at_factory(doc_object){

	var items_being_sent=doc_object.items_required;
	var corporate_warehouse=doc_object.corporate_warehouse;
	var receiving_warehouse=doc_object.receiving_warehouse;
	var location=doc_object.location;
	var resp;
	var entity={

		"items_being_sent":items_being_sent,
		"corporate_warehouse":corporate_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"location":location
	}
		frappe.call({
			method: "bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.receive_material_at_factory",
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log( JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp

}
frappe.ui.form.on("Pch Reqired Items",{
qty_of_raw_material_being_sent:function(frm, cdt, cdn) {

	var d=locals[cdt][cdn]
	var cf=d.conversion_factor;
	var qty_to_be_sent=d.qty_of_raw_material_being_sent
	var total_qty=qty_to_be_sent*cf
	console.log(total_qty)
	d.dispatched_quantity_in_uom=total_qty
	}

});

function send_material_to_corporate(doc_object){

	var items_being_sent=doc_object.items_required;
	var corporate_warehouse=doc_object.corporate_warehouse;
	var receiving_warehouse=doc_object.receiving_warehouse;
	var location=doc_object.location;
	var resp;
	var entity={

		"items_being_sent":items_being_sent,
		"corporate_warehouse":corporate_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"location":location
	}
		frappe.call({
			method: "bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.send_material_to_corporate", //using same function of factory because there is no changes
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log( JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp

}


function receive_material_at_corporate(doc_object){

	var items_being_sent=doc_object.items_required;
	var corporate_warehouse=doc_object.corporate_warehouse;
	var receiving_warehouse=doc_object.receiving_warehouse;
	var location=doc_object.location;
	var resp;
	var entity={

		"items_being_sent":items_being_sent,
		"corporate_warehouse":corporate_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"location":location
	}
		frappe.call({
			method: "bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.receive_material_at_corporate", //using same function of factory because there is no changes
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log( JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp

}

function create_receive_transaction(doc_object){


	var items_required=doc_object.items_required;
	var corporate_warehouse=doc_object.corporate_warehouse;
	var receiving_warehouse=doc_object.receiving_warehouse;

	var start_process=doc_object.start_process;
	var end_process=doc_object.end_process;
	var units_s_r=doc_object.units_s_r;

	var item_made=doc_object.item_made;
	var location=doc_object.location;
	var manufacturing_method=doc_object.manufacturing_method;
	var record_type;
	var button_visiblity_record_types = ["Send Material to Factory","Send Material to Corporate"]


	if(doc_object.record_type == "Send Material to Factory"){
	record_type=  "Receive Material at Factory"
	}
	else{
	record_type=  "Receive Material at Corporate"
	}

	var resp;
	var entity={
	    "start_process":start_process,
	    "end_process":end_process,
	    "units_s_r":units_s_r,
	    "item_made":item_made,
	    "location":location,
	    "manufacturing_method":manufacturing_method,
	    "record_type":record_type,

		"items_required":items_required,
		"corporate_warehouse":corporate_warehouse,
		"receiving_warehouse":receiving_warehouse
			}
		frappe.call({
			method: "bom_template.bom_template.doctype.pch_send_material_to_factory.pch_send_material_to_factory.create_receive_transaction", //using same function of factory because there is no changes
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log( JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp

}

