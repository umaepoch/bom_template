// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Manufacturing Method', {
	refresh: function(frm) {

	}
});

/*
frappe.ui.form.on("Pch Manufacturing Method","method_makes",function(frm,cdt,cdn){
		var method_makes = cur_frm.doc.method_makes;
		if (method_makes =="Multiple Items"){
			frm.toggle_display("master_item")
			console.log("con satisfied");

		}
});
*/

//item triger for stock uom
//uom trigger for conversio factor (Please Select Item first)
//child table field(add upto 100%)

frappe.ui.form.on("Pch Manufacturing Method","method_makes",function(frm,cdt,cdn){

	var items=get_all_items();
	//console.log(items);
	cur_frm.set_query("master_item",  function(frm, cdt, cdn) {
//console.log(wh_n);
return {
"filters": [
["Item", "name", "in", items]



]
}
});

});

frappe.ui.form.on("Pch Manufacturing Method Child", {
item_made: function (frm, cdt, cdn) {
		console.log("child_tanle_triggers is working");
		//validation_start
		var units_s_r = cur_frm.doc.method_makes ;
		var row = locals[cdt][cdn];
		if(units_s_r == "Single Item"){
			if(row.idx >1 ){
				console.log("Through message");
				frappe.msgprint("Not allowed.Cannot create more than one item.Method makes field is configured as single");
				row.item_made = "" ;
				refresh_field("item_made");
				refresh_field(frm.doc.method_items);
			}
		} //end of validation

		//stock uom fetching
		var stock_uom_temp = get_stock_uom(row.item_made)
		row.stock_uom = stock_uom_temp ;
		refresh_field("stock_uom");
		refresh_field(frm.doc.method_items);
	},//end of item_made

	qty_made: function (frm, cdt, cdn) {
			console.log("child_tanle_triggers is working");
			var units_s_r = cur_frm.doc.method_makes ;
			if(units_s_r == "Single Item"){
				var row = locals[cdt][cdn];
				if(row.idx >1 ){
					frappe.msgprint("Not allowed.Cannot create more than one item.Method makes field is configured as single");
					row.qty_made = "" ;
					refresh_field("qty_made");
					refresh_field(frm.doc.method_items);
				}
			}
		},

		qty_uom: function (frm, cdt, cdn) {
				console.log("child_tanle_triggers is working");
				var units_s_r = cur_frm.doc.method_makes ;
				var row = locals[cdt][cdn];

				if(units_s_r == "Single Item"){
					if(row.idx >1 ){
						frappe.msgprint("Not allowed.Cannot create more than one item.Method makes field is configured as single");
						row.qty_uom = "" ;
						refresh_field("qty_uom");
						refresh_field(frm.doc.method_items);
					}
				}//end of validtion

				//stock uom fetching
				if(row.item_made){
					var cf = get_conversion_factor(row.item_made,row.qty_uom)
					row.conversion_factor = cf ;
					refresh_field("conversion_factor");
					refresh_field(frm.doc.method_items);
				}else{
					frappe.msgprint("Please Select Item first");
					row.qty_uom = "" ;
					refresh_field("qty_uom");
					refresh_field(frm.doc.method_items);
				}

			},
			conversion_factor: function (frm, cdt, cdn) {
					console.log("child_tanle_triggers is working");
					var units_s_r = cur_frm.doc.method_makes ;
					if(units_s_r == "Single Item"){
						var row = locals[cdt][cdn];
						if(row.idx >1 ){
							frappe.msgprint("Not allowed.Cannot create more than one item.Method makes field is configured as single");
							row.conversion_factor = "" ;
							refresh_field("conversion_factor");
							refresh_field(frm.doc.method_items);
						}
					}//end of validation
				},
			val_input_per:function (frm, cdt, cdn) {
					var row = locals[cdt][cdn];
					var val_input_per = row.val_input_per;
					if(val_input_per > 100){
						frappe.msgprint("The percent numbers should be less than 100%");
						row.val_input_per = "" ;
						refresh_field("val_input_per");
						refresh_field(frm.doc.method_items);
					}

			}
});

function get_conversion_factor(item_code,uom){
	var cf = "";
	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_manufacturing_method.pch_manufacturing_method.get_conversion_factor',
		args: {
			 "item_code":item_code,
			 "uom":uom
		},
		async: false,
		callback: function(r) {
			 if (r.message) {
				 cf = r.message
				}
		}
		});
		return cf

}

function get_stock_uom(item_code){
	var stock_uom = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item",
            filters: {
							name: ["=", item_code]
            },
            fieldname: ["stock_uom"] //"outbound_warehouse","inbound_warehouse"
        },
        async: false,
        callback: function(r) {
					if (r.message) {
					//	console.log("........." + JSON.stringify(r.message));
            stock_uom = r.message.stock_uom;
					}

        }
    });
		return stock_uom
}
function get_all_items(){

	var item_list;
	frappe.call({
	
		method:"bom_template.bom_template.doctype.pch_manufacturing_method.pch_manufacturing_method.get_items",
		async:false,
		callback:function(r){
		
			item_list=r.message;		
		
		}
		
		
	
	});
	
	return item_list


}
