// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pch Production Plan Lite', {
	season: function(frm) {
	var season = cur_frm.doc.season
	if(season){
	var is_season_exist = is_season_exist_already(season)
	if(is_season_exist == 1){
	//through message
	console.log("yes already exist")
	frappe.msgprint("Season : "+season+"  Already exist .Please modify that");
	}
	}
	}
});

frappe.ui.form.on("Items",{
production_plan_in_uom:function(frm, cdt, cdn) {
	console.log("Items trigger working")



	}

});

frappe.ui.form.on("Pch Production Plan Lite Item",{
uom:function(frm, cdt, cdn) {
    var d=locals[cdt][cdn]
	if(d.item){
	var conversion_factor = get_conversion_factor( d.uom , d.item)
	d.conversion_factor = conversion_factor
	refresh_field("conversion_factor");
	refresh_field(frm.doc.items);

	}

},
production_plan_in_uom:function(frm, cdt, cdn) {
	console.log("Items bbb trigger working")

	var d=locals[cdt][cdn]
	if(d.production_plan_in_uom){
	var cf=d.conversion_factor;
	var qty_to_be_sent=d.qty_of_raw_material_being_sent
	var total_qty=qty_to_be_sent*cf
	console.log("qty_of_raw_material_being_sent trgger"+total_qty)
	d.production_plan_in_stock_uom=d.production_plan_in_uom * cf
	refresh_field("production_plan_in_stock_uom");
	refresh_field(frm.doc.items);
	}
	}

});

function get_conversion_factor(uom_val , item_code){
	var cf;
	console.log("uom_val :"+uom_val +"item_code :"+item_code)
	frappe.call({
		method:'bom_template.bom_template.doctype.pch_production_plan_lite.pch_production_plan_lite.get_conversion_factor',
		async:false,
		args:{
		"uom":uom_val,
		"item_code":item_code,
		},

		callback:function(r){
		cf=r.message;
		}
	});
	return cf
}

function is_season_exist_already(season_val){
	var season_exist_flag = 0;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Pch Production Plan Lite",
            filters: {
							season: ["=", season_val]
            },
            fieldname: ["name"] //"outbound_warehouse","inbound_warehouse"
        },
        async: false,
        callback: function(r) {
					if (r.message.name) {
					console.log("........." + JSON.stringify(r));
            season_exist_flag = 1
					}

        }
    });
		return season_exist_flag
}
