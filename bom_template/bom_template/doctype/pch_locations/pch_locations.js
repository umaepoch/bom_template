// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt



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
		}//end  of for

		set_child_table(extra_process_list);
	}

});



//Ak
//Code for checking Inbound and Outbound within the Doctype p1
frappe.ui.form.on("Pch Locations Child",{
inbound_warehouse:function (frm, doctype, name) {
var d = locals[doctype][name];
var ib_list=[];
var details=cur_frm.doc.locations_child;
for(var i=0;i<details.length;i++)
	{
		if(i==0)
		{
		   continue;
		
		}
		else
		{
    			console.log("Enter")
    			var ib_prev=details[i-1]["inbound_warehouse"];
    			var ib_current=details[i]["inbound_warehouse"];
    			var ob_prev=details[i-1]["outbound_warehouse"];
    			var ob_current=details[i]["outbound_warehouse"];
    			
    			if(ib_current===ob_prev)
    			{
    			
    			   frappe.msgprint("This Inbound Warehouse has already been used in the previous row");
    			   console.log(details[i]["inbound_warehouse"]);
    			     details[i]["inbound_warehouse"]="";
    			}
    			
    			else
    			{
    			 	console.log("Nothing");
    			}
    			
              }
        }

	
}
});


//Code for checking Inbound and Outbound within the Doctype p2
frappe.ui.form.on("Pch Locations Child",{
outbound_warehouse:function (frm, doctype, name) {
var d = locals[doctype][name];
var ib_list=[];
var details=cur_frm.doc.locations_child;
for(var i=0;i<details.length;i++)
	{
		if(i==0)
		{
		   continue;
		
		}
		else
		{
    			console.log("Enter")
    			var ib_prev=details[i-1]["inbound_warehouse"];
    			var ib_current=details[i]["inbound_warehouse"];
    			var ob_prev=details[i-1]["outbound_warehouse"];
    			var ob_current=details[i]["outbound_warehouse"];
    			
    			 if(ob_current===ib_prev)
    			{
    			    
    			   frappe.msgprint("This outbound warehouse name has already been used in the previous row");
    			   console.log(details[i]["outbound_warehouse"]);
    			   details[i]["outbound_warehouse"]="";
    			}
    			else
    			{
    			 	console.log("Nothing");
    			}
    			
              }
        }

	
}
});


//Function for checking inbound warehouse across the records
frappe.ui.form.on("Pch Locations Child",{
	inbound_warehouse:function(frm,doctype,name){
	

	
	var d=locals[doctype][name];
	var ib_wh=d.inbound_warehouse;
	console.log(ib_wh);
	//var is_unique_flag;
	var is_unique_flag=is_unique_warehouse(ib_wh,'inbound');
	console.log(is_unique_flag);
	if(is_unique_flag===0)
	{
		 frappe.msgprint('This Inbound Warehouse is already active. Please re-enter a new Inbound Warehouse ');
               
               	d.inbound_warehouse="";
	}
	
	
    
   }
	
	
  
});

//Function for checking outbound warehouse across the records
frappe.ui.form.on("Pch Locations Child",{
	outbound_warehouse:function(frm,doctype,name){
	


	//console.log(company_list);
	var d=locals[doctype][name];
	
	var ob_wh=d.outbound_warehouse;
	console.log(ob_wh);
	//var is_unique_flag;
	 var is_unique_flag=is_unique_warehouse(ob_wh,'outbound');
	console.log(is_unique_flag);
	if(is_unique_flag===0)
	{
		 frappe.msgprint('This Outbound Warehouse is already active. Please re-enter a new Outbound Warehouse ');
               
               	d.outbound_warehouse="";
	}
	
	
    
   }
        
	
 
});

frappe.ui.form.on("Pch Locations",{
company_name:function(frm,cdt,cdn){

  var comp=cur_frm.doc.company_name;
  var ww=get_warehouses_list(comp);
  //console.log(ww);
  
        
        
        //Filtering Outbound warehouse based on company
        cur_frm.set_query("outbound_warehouse", "locations_child", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Warehouse", "name", "in", ww]
                    
                   
        
                ]
            }
		});
		
        cur_frm.refresh_field("locations_child");
        cur_frm.refresh_field("outbound_warehouse");
        
        var a_list=get_account_details(comp);
        
       //Filtering Accounts based on company
        cur_frm.set_query("difference_account", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Account", "name", "in", a_list]
                    
                   
        
                ]
            }
		});
		
        cur_frm.refresh_field("Pch Locations");
        cur_frm.refresh_field("difference_account");
        
        
        //Filtering inbound warehouse based on company 
  cur_frm.set_query("inbound_warehouse", "locations_child", function(frm, cdt, cdn) {
    			//console.log(wh_n);
            return {
                "filters": [
                    ["Warehouse", "name", "in", ww]
                    
                   
        
                ]
            }
		});
		
        cur_frm.refresh_field("locations_child");
        cur_frm.refresh_field("inbound_warehouse");
        
  }
  });

function get_process_list(){
	var process_list ;
	frappe.call({
		method: 'bom_template.bom_template.doctype.pch_locations.pch_locations.get_process_list',
		async: false,
		callback: function(r) {

			 if (r.message) {
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
} //end of set_child_table


function get_account_details(company_name){

	var accounts=[]
	frappe.call({
		method:"bom_template.bom_template.doctype.pch_locations.pch_locations.get_account_details",
		args:{
		
			"company_name":company_name
		
		},
		async:false,
		callback:function(r){
		
			accounts=r.message
		}
	
	});
	
	return accounts

}

function is_unique_warehouse(warehouse_name,warehouse_type){

	var is_unique_flag;
	 frappe.call({
               
        method:"bom_template.bom_template.doctype.pch_locations.pch_locations.check_unique_warehouse",
        args:{
            
            "warehouse_name":warehouse_name,
            "warehouse_type":warehouse_type
        },
        async:false,
        callback:function(r){
            
            is_unique_flag=r.message;
           
            
        }
    
        
    });

	return is_unique_flag;

}

function get_warehouses_list(company_name){

       var warehouse_list=[];
	 frappe.call({
               
        method:"bom_template.bom_template.doctype.pch_locations.pch_locations.get_company_specific_warehouses",
        args:{
            
            "company_name":company_name
        },
        async:false,
        callback:function(r){
            
            warehouse_list=r.message;
            
           
            
        }
    
        
    });

       return warehouse_list;
}
