// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

//if the method is choosen it will filter according to method else all Pch Manufacturing Method Details id will come in dropdwon
cur_frm.set_query('start_process', function() {
										 var method_id = cur_frm.doc.manufacturing_method;
										 if(method_id){
											 console.log("start_process query working if------------");
											 return {
					                 "filters": [
					                     ['Pch Manufacturing Method Details', 'pch_method', '=', method_id]
					                 ]
					             }
										 }
				         });

cur_frm.set_query('end_process', function() {
										 var method_id = cur_frm.doc.manufacturing_method;
										 if(method_id){
											 console.log("start_process query working if------------");
											 return {
					                 "filters": [
					                     ['Pch Manufacturing Method Details', 'pch_method', '=', method_id]
					                 ]
					             }
										 }
				         });


frappe.ui.form.on('Pch Manufacturing Record', {
	item_made: function(frm) {
		var item_chosen=cur_frm.doc.item_made;
		var item_methods=get_methods(item_chosen);
		if(item_chosen)
		{
			if(item_methods.length===1){
			cur_frm.set_value("manufacturing_method",item_methods[0]);
			}
   }
	}//end of field trigger
});

/*
1.material issue
2. Material Receipt(if 	Start Process	 process order <=1
3.Material transfer
*/

//on_submit
/*
frappe.ui.form.on("Pch Manufacturing Record", "refresh", function(frm, cdt, cdn) {
	console.log("on_submit working")
	var m_record_type = cur_frm.doc.manufacturing_record_type ;
	if(m_record_type == "Send Material for Manufacturing"){
		send_material_for_manufacturing(cur_frm.doc)
		//validation for issue
	}
});
*/

//on_submit

frappe.ui.form.on("Pch Manufacturing Record", "on_submit", function(frm, cdt, cdn) {
	console.log("on_submit working")
	var m_record_type = cur_frm.doc.manufacturing_record_type ;
	if(m_record_type == "Send Material for Manufacturing"){
		var r=send_material_for_manufacturing(cur_frm.doc)
		console.log(r,"Ok");
		//validation for issue
		for(var i=0;i<r.length;i++)
		{
		
			if(r[i]["Status"]=="Created")
			{
			
				frappe.msgprint("Stock Entry for"+" "+r[i]["Stock Entry Type"]+" "+"has been made"+" "+"ID of the corresponding Stock Entry is"+" "+r[i]["Name"])
				//console.log(r[i]["Name"]);
				if(r[i]["Stock Entry Type"]=="Material Issue")
				{
					cur_frm.set_value("pch_material_issue",r[i]["Name"]);
				}
				else if (r[i]["Stock Entry Type"]=="Material Receipt")	
				{
					cur_frm.set_value("pch_material_receipt",r[i]["Name"]);
				
				}
				
				else
				{
				cur_frm.set_value("pch_material_transfer",r[i]["Name"]);
				}
			}
			cur_frm.save('Submit');
			if(r[i]["Status"]=="Not Created")
			{
			
				console.log('dddd',r[i]["Status"]);
				frappe.msgprint("Did not Submit");
				cur_frm.save('Cancel');
				if(r[i]["Stock Entry Type"]=="Material Transfer")
				{
					//cur_frm.set_value("pch_material_issue","");
					//cur_frm.set_value("pch_material_receipt","");
					console.log(cur_frm.doc.docstatus,"Okkkkkkkkkk");
					if(cur_frm.doc.docstatus==1)
					{
					
						change_docstatus(cur_frm.doc.name);
						
					}
				}
				
			}
		}
		
	}
	if(m_record_type == "Receive Material from Manufacturing"){
	var r1=receive_material_for_manufacturing(cur_frm.doc);
		if(r1[0]["Status"]=="Created")
		
		{
		
			if(r1[0]["Stock Entry Type"]=="Material Transfer")
			{
			
				cur_frm.set_value("pch_material_transfer",r1[0]["Name"]);
			}		
			cur_frm.save('Submit');
		}
		
		if(r1[0]["Status"]=="Not Created")
		
		{
				
			if(r1[0]["Stock Entry Type"]=="Material Transfer")
				{
					
					if(cur_frm.doc.docstatus==1)
					{
					
						change_docstatus(cur_frm.doc.name);
						
					}
				}
		}
	}
	if(m_record_type=="Send Materials to Internal Storage WH")
	{
		var r3=transfer_material_internally(cur_frm.doc);
		if(r3[0]["Status"]=="Created")
		{
			
			if(r3[0]["Stock Entry Type"]=="Material Transfer")
			{
			
				cur_frm.set_value("pch_material_transfer",r3[0]["Name"]);
			}		
			cur_frm.save('Submit');
		
		}
		if(r3[0]["Status"]=="Not Created")
		
		{
				
			if(r3[0]["Stock Entry Type"]=="Material Transfer")
				{
					
					if(cur_frm.doc.docstatus==1)
					{
					
						change_docstatus(cur_frm.doc.name);
						
					}
				}
		}

	
	}
});

function change_docstatus(name){

	var resp;
	frappe.call({
				method:"bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.change_doc_status",
args:{
"name":name},
async:false,
callback:function(r){

	if(r.message){
	
		 resp=r.message;
	}
}
		
	})
	return resp;

}

frappe.ui.form.on("Pch Manufacturing Record","after_cancel",function(frm,cdt,cdn){
	console.log("After c");
	var material_issue_entry=cur_frm.doc.pch_material_issue;
	var material_receipt_entry=cur_frm.doc.pch_material_receipt;
	var material_transfer_entry=cur_frm.doc.pch_material_transfer;
	var record_type=cur_frm.doc.manufacturing_record_type;
	if(record_type=="Send Material for Manufacturing")
	{
	var cancel=cancel_stock_entries(material_issue_entry,material_receipt_entry,material_transfer_entry);
	        
		
	if(cancel){
	
		frappe.msgprint('Corresponding Stock Entries of the cancelled Record have been cancelled');
		cur_frm.set_value("pch_material_issue","");
		cur_frm.refresh_field("pch_material_issue");
		
		cur_frm.set_value("pch_material_receipt","");
		cur_frm.refresh_field("pch_material_receipt");
		
		cur_frm.set_value("pch_material_transfer","");
		cur_frm.refresh_field("pch_material_transfer");
		
		console.log(material_issue_entry);
		
	}
	}
	else if (record_type=="Receive Material from Manufacturing"){
	
		var c1=cancel_se_for_rm(material_transfer_entry);
		cur_frm.set_value("pch_material_transfer","");
		cur_frm.refresh_field("pch_material_transfer");
		console.log("Mat Transfer Cancelled");
	
	
	}
	else if (record_type=="Send Materials to Internal Storage WH")
	{
		var c1=cancel_se_for_rm(material_transfer_entry);
		console.log("Mat Transfer Cancelled");
	
	
	}
	else
	{
		console.log('nnnn');
		
	}

});
function cancel_stock_entries(mat_issue,mat_receipt,mat_transfer){
	var resp;
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.cancel_s_entries",
		args:{
			
			"mat_issue":mat_issue,
			"mat_receipt":mat_receipt,
			"mat_transfer":mat_transfer
		
		},
		async:false,
		callback:function(r){
		
		
			 resp=r.message;
		}
	})
	return resp;
}
function cancel_se_for_rm(mat_transfer){

	var resp;
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.cancel_single_se",
		args:{
			
			"mat_transfer":mat_transfer
			
		
		},
		async:false,
		callback:function(r){
		
		
			 resp=r.message;
		}
	})
	return resp;
}


function receive_material_for_manufacturing(doc_object){
	var req_items = doc_object.req_items
	var method_items = doc_object.method_items
	var outbound_warehouse =  doc_object.outbound_warehouse
	var target_warehouse =  doc_object.target_warehouse //subContractor wh
	var location =  doc_object.location //subContractor wh
	var start_process =  doc_object.start_process
	var receiving_warehouse =  doc_object.receiving_warehouse
	var subcontracting_rate =  doc_object.subcontracting_rate
	var units_s_r =  doc_object.units_s_r
	var resp;
	var entity ={
		"req_items":req_items,
		"method_items":method_items,
		"outbound_warehouse":outbound_warehouse,
		"target_warehouse":target_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"start_process":start_process,
		"location":location,
		"subcontracting_rate":subcontracting_rate,
		"units_s_r":units_s_r
	}
	console.log("entity" + JSON.stringify(entity));


	frappe.call({
			method: "bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.receive_material_for_manufacturing",
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
					resp=r.message;
							console.log("method_doc_data receive_material_for_manufacturing" + JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp;
} //end of receive_material_for_manufacturing

function send_material_for_manufacturing(doc_object){
	var req_items = doc_object.req_items
	var method_items = doc_object.method_items
	var outbound_warehouse =  doc_object.outbound_warehouse
	var target_warehouse =  doc_object.target_warehouse //subContractor wh
	var location =  doc_object.location //subContractor wh
	var start_process =  doc_object.start_process
	var subcontracting_rate =  doc_object.subcontracting_rate
	var units_to_be_sr=doc_object.units_s_r
	var resp;
	var entity ={
		"req_items":req_items,
		"method_items":method_items,
		"outbound_warehouse":outbound_warehouse,
		"target_warehouse":target_warehouse,
		"start_process":start_process,
		"location":location,
		"subcontracting_rate":subcontracting_rate,
		"units_to_be_sr":units_to_be_sr
	}

	frappe.call({
			method: "bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.send_material_for_manufacturing",
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
					resp=r.message;
							console.log("method_doc_data" + JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp;
}
function transfer_material_internally(doc_object){
	//var req_items = doc_object.req_items
	var method_items = doc_object.method_items
	var outbound_warehouse =  doc_object.outbound_warehouse
	//var target_warehouse =  doc_object.target_warehouse //subContractor wh
	var location =  doc_object.location //subContractor wh
	var start_process =  doc_object.start_process
	var receiving_warehouse =  doc_object.receiving_warehouse
	//var subcontracting_rate =  doc_object.subcontracting_rate
	var units_s_r =  doc_object.units_s_r
	var resp;
	var entity ={
		
		"method_items":method_items,
		"outbound_warehouse":outbound_warehouse,
		"receiving_warehouse":receiving_warehouse,
		"start_process":start_process,
		"units_s_r":units_s_r
		
	}
	console.log("entity" + JSON.stringify(entity));


	frappe.call({
			method: "bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.move_material_internally",
			args: {
		 "entity":entity
			},
			async: false,
			callback: function(r) {
					if (r.message) {
							resp=r.message
							console.log("method_doc_data receive_material_for_manufacturing" + JSON.stringify(r.message));
							}
			} //end of callback fun..
	}) //end of frappe call..
	return resp
} //end of receive_material_for_manufacturing


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
									frappe.model.set_value(child.doctype, child.name, "item_name", method_doc_data[i]['item_name']);
									frappe.model.set_value(child.doctype, child.name, "qty_made", method_doc_data[i]['qty_made']);
									frappe.model.set_value(child.doctype, child.name, "stock_uom", method_doc_data[i]['stock_uom']);
									frappe.model.set_value(child.doctype, child.name, "qty_made_type", method_doc_data[i]['qty_made_type']);
									frappe.model.set_value(child.doctype, child.name, "qty_uom", method_doc_data[i]['qty_uom']);
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
	var units_s_r = cur_frm.doc.units_s_r;

	set_start_end_process_raw_materials(start_process,end_process,method,units_s_r)
});

frappe.ui.form.on("Pch Manufacturing Record", "get_processs", function(frm, cdt, cdn) {
	//console.log("Button clicked");
	//validation  start_process,end_process,manufacturing_method are mandatory to run this method
	var start_process = cur_frm.doc.start_process;
	var end_process = cur_frm.doc.end_process;
	var method = cur_frm.doc.manufacturing_method;
	var units_s_r = cur_frm.doc.units_s_r;

	set_process_details(start_process,end_process,method,units_s_r)
});


//what if selected process or location has no wh details?
frappe.ui.form.on("Pch Manufacturing Record", "start_process", function(frm, cdt, cdn) {
	var start_process_temp = cur_frm.doc.start_process;

	var location_name = cur_frm.doc.location;
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

//Process Cost Details child_table_field_trigger

frappe.ui.form.on("Pch Mrec  Child Process", {
labour_rate_per_unit: function (frm, cdt, cdn) {
		console.log("child_tanle_triggers is working");
		var sum=0;
		var row = locals[cdt][cdn];
		console.log(row);
		var labour_rate_per_unit_temp = row.labour_rate_per_unit;
		
		console.log("labour_rate_per_unit_temp"+labour_rate_per_unit_temp);
		if(labour_rate_per_unit_temp){
			var units_s_r = cur_frm.doc.units_s_r ;
			var labour_amount = labour_rate_per_unit_temp * units_s_r
			row.labour_amount = labour_amount ;
     
		}
		
		var d=cur_frm.doc.process_items;
		for(var i=0;i<d.length;i++)
		{
		
			var lr=d[i].labour_rate_per_unit;
			sum+=lr;
			console.log(sum);
		}
		cur_frm.set_value("subcontracting_rate",sum);
		 refresh_field("labour_amount");
			refresh_field(frm.doc.process_items);
	}

});
/*
frappe.ui.form.on("Process Cost Details", {
	console.log("child_table_triggers parent is working");
labour_rate_per_unit: function (frm, doctype, name) {
		console.log("child_table_triggers  field is working");

	}

});
*/



function set_process_details(start_process,end_process,method,units_s_r){
	console.log("method",method)

	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_start_end_p_process_details',
		args: {
		   "start_process":start_process,
			 "end_process":end_process,
			 "method":method
		},
		async: false,
		callback: function(r) {
			 if (r.message) {
				console.log("process json..." + JSON.stringify(r.message));
				cur_frm.clear_table("process_items");
				var items_list = r.message;
				for (var i=0;i<items_list.length;i++){
				var total_qty = units_s_r *  items_list[i]['qty']
				var child = cur_frm.add_child("process_items");
				console.log("sur items_list :"+i+" row"+JSON.stringify(items_list[i]))
				frappe.model.set_value(child.doctype, child.name, "pch_process", items_list[i]['pch_process']);
				frappe.model.set_value(child.doctype, child.name, "process_order", items_list[i]['process_order']);
				frappe.model.set_value(child.doctype, child.name, "turnaround_time", items_list[i]['turnaround_time']);
				frappe.model.set_value(child.doctype, child.name, "touch_points", items_list[i]['touch_points']);
				//frappe.model.set_value(child.doctype, child.name, "dispatched_quantity_in_uom", items_list[i]['operand']);
				}//end of for loop...
				refresh_field("process_items");
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
}

function set_start_end_process_raw_materials(start_process,end_process,method,units_s_r){
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
				var total_qty = units_s_r *  items_list[i]['qty_per_unit_made']
				var child = cur_frm.add_child("req_items");
				console.log("sur items_list :"+i+" row"+JSON.stringify(items_list[i]))
				frappe.model.set_value(child.doctype, child.name, "item_code", items_list[i]['item_code']);
				frappe.model.set_value(child.doctype, child.name, "qty_uom", items_list[i]['qty_uom']);
				frappe.model.set_value(child.doctype, child.name, "qty_per_unit_made", items_list[i]['qty_per_unit_made']);
				frappe.model.set_value(child.doctype, child.name, "qty_in_stock_uom", items_list[i]['qty_in_stock_uom']);
				frappe.model.set_value(child.doctype, child.name, "total_qty",total_qty);
				//frappe.model.set_value(child.doctype, child.name, "qty_of_raw_material_being_sent", items_list[i]['qty_of_raw_material_being_sent']);
				frappe.model.set_value(child.doctype, child.name, "consumption_type", items_list[i]['consumption_type']);
				frappe.model.set_value(child.doctype, child.name, "stock_uom", items_list[i]['stock_uom']);
				frappe.model.set_value(child.doctype, child.name, "conversion_factor", items_list[i]['conversion_factor']);
				frappe.model.set_value(child.doctype, child.name, "mmd", items_list[i]['name']);
				//frappe.model.set_value(child.doctype, child.name, "dispatched_quantity_in_uom", items_list[i]['dispatched_quantity_in_uom']);
				frappe.model.set_value(child.doctype, child.name, "operand", items_list[i]['operand']);
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

function get_methods(item_made){
	var methods=[];
	frappe.call({
		method:'bom_template.bom_template.doctype.pch_manufacturing_record.pch_manufacturing_record.get_method_based_on_item',
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

//
//get_required_items button -Manufacturing Method,start_process,end_process,units_s_r validation neede
//get_process button -Manufacturing Method,start_process,end_process,units_s_r validation neede
