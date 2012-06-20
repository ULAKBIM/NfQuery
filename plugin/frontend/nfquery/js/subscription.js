function subscription_toggle(button){
	var button_status = 'Off';
	if (button.attr('checked')){
		button_status = 'On';
	}
	//Send button status to be persistence
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",
		{
			button_status: button_status,
			button_id: button.attr('id')
		},
	   	function(){}	
	);
}

function getSubscriptionDetail2(name){
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
		var json = $.parseJSON(data);
		var counter = 0;
                var details_div = document.getElementById("detail_subs");
		$("#query_table").empty();
	
		$("#query_table").append("<tr><td><div id='accordion_group2' class='accordion-group'><div id='accordion_div_id' class='accordion-heading'>"+
					 "<a class='accordion-toggle' href='#validationDiv' data-parent='#accordion_table' data-toggle='collapse'>"+
					 "Validation </a></div><div id='validationDiv' class='accordion-body in collapse' style='height: auto;'>"+
                    			 "<div class='accordion-inner'><table id='validation_table' class='table table-striped'></table></div></div></div></td></tr>"+
				         "<tr><td><div id='accordion_group3' class='accordion-group'><div id='accordion_div_id' class='accordion-heading'>"+
					 "<a class='accordion-toggle' href='#mandatoryDiv' data-parent='#accordion_table' data-toggle='collapse'>"+
					 "Mandatory </a></div><div id='mandatoryDiv' class='accordion-body in collapse' style='height: auto;'>"+
                    			 "<div class='accordion-inner'><table id='mandatory_table' class='table table-striped'></table></div></div></div></td></tr>"+
				         "<tr><td><div id='accordion_group4' class='accordion-group'><div id='accordion_div_id' class='accordion-heading'>"+
					 "<a class='accordion-toggle' href='#optionalDiv' data-parent='#accordion_table' data-toggle='collapse'>"+
					 "Optional </a></div><div id='optionalDiv' class='accordion-body in collapse' style='height: auto;'>"+
                    			 "<div class='accordion-inner'><table id='optional_table' class='table table-striped'></table></div></div></div></td></tr>");

		if(document.getElementById("desc_subs_id") != null) {
			var divelement = document.getElementById('desc_subs_id');
			details_div.removeChild(divelement);
			$("#desc_subs_id").remove();
		}
		$("#anchor_id").remove();
		for(i in json){
			
			$("#accordion2").css('visibility', 'visible');
			$("#accordion_div_id").attr("class","accordion-toggle")
			$("#accordion_div_id").append("<a id='anchor_id' class='accordion-toggle' href='#collapseOne' data-parent='#accordion2'"+
							"data-toggle='collapse'><b>+ Queries</b> </a>");
			$("#validation_table").append("<tr><td><b>Query Id</b></td><td><b>Query Type</b></td><td><b>Filter</b></td></tr>")
			
			var r = 1;
			for (j in json[i]){
				for(k in json[i][j]){
					category_name = json[i][j][k]["category_name"];
					query_id = json[i][j][k]["query_id"];
					query_type = json[i][j][k]["query_type"];
					filter = json[i][j][k]["filter"];
					source_name = json[i][j][k]["source_name"];
					source_link = json[i][j][k]["link"];
					r = r+1;
					if(category_name == "validation"){
						$("#validation_table").append("<tr><td>"+query_id+"</td><td>"+query_type+"</td><td>"+filter+"</td></tr>")
					}
					if(category_name == "mandatory"){
						$("#mandatory_table").append("<tr><td>"+query_id+"</td><td>"+query_type+"</td><td>"+filter+"</td></tr>")
					}
					if(category_name == "optional"){
						$("#optional_table").append("<tr><td>"+query_id+"</td><td>"+query_type+"</td><td>"+filter+"</td></tr>")
					}
					if(r<3){
						var divelement = document.createElement('div');
						divelement.id = "desc_subs_id";
                        			details_div.appendChild(divelement);	
                                                divelement.innerHTML = "<h3><u><b>Details Of " +name+"</b></u></h3></br><h4><b>Source Name : " +
                                                                        " "+source_name+"</b></h4></br><h4><b>Source Link"+"   : " +
                                                                        " <a href="+source_link+">"+source_link+"</a></b></h4></br>";
                                                divelement.setAttribute("class","alert alert-info");

						var query_table=document.getElementById("query_table");
						
					}
				}
			}
		}

	} 
	);
}










function getSubscriptionDetail(name){
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
                /*for(var i = document.getElementById("detail_table").rows.length; i > 0;i--){
                        document.getElementById("detail_table").deleteRow(i -1);
                }*/
                for(var i = document.getElementById("query_table").rows.length; i > 0;i--){
                        document.getElementById("query_table").deleteRow(i -1);
                }
		$("#anchor_id").remove();
		$("#desc_subs_id").remove();
                
		var divelement = document.createElement('div');
		divelement.id = "desc_subs_id";



		$("#accordion2").css('visibility', 'hidden');
		var json = $.parseJSON(data);
		var counter = 0;
		for(i in json){
			$("#accordion2").css('visibility', 'visible');
			var mydiv=document.getElementById("accordion_div_id");
			var element = document.createElement('a');
			element.setAttribute("class","accordion-toggle");
			element.setAttribute("id","anchor_id");
			element.href = "#collapseOne";
			element.innerHTML = "<i class='icon-plus'></i>Queries";
			element.setAttribute("data-toggle","collapse");
			element.setAttribute("data-parent","#accordion2");
			mydiv.appendChild(element);
			
	
			//var detail_table=document.getElementById("detail_table");
			var query_table=document.getElementById("query_table");
			//var detail_row = detail_table.insertRow(0);
			/*var detail_cell = detail_row.insertCell(0);
			detail_cell.innerHTML = "<b>Details Of " + name + "</b>";
            	        detail_row = detail_table.insertRow(1);
            		var detail_cell3 = detail_row.insertCell(0);
            		var detail_cell4 = detail_row.insertCell(1);
            		detail_cell3.innerHTML="<b>Source Name</b>";
            		detail_cell4.innerHTML="<b>Source Link</b>";*/



			var query_row = query_table.insertRow(0);
			var query_cell = query_row.insertCell(0);
			query_cell.innerHTML = "<b>Query Informations Of " + name + "</b>";
			query_row = query_table.insertRow(1);
			var cell1 = query_row.insertCell(0);
			var cell2 = query_row.insertCell(1);
			var cell3 = query_row.insertCell(2);
			var cell4 = query_row.insertCell(3);
		        cell1.innerHTML = "<b>Category</b>";
		        cell2.innerHTML = "<b>Query Id</b>";
		        cell3.innerHTML = "<b>Query Type</b>";
		        cell4.innerHTML = "<b>Filter</b>";
				
			var r = 1;
			for (j in json[i]){
				
				for(k in json[i][j]){
					category_name = json[i][j][k]["category_name"];
					query_id = json[i][j][k]["query_id"];
					query_type = json[i][j][k]["query_type"];
					filter = json[i][j][k]["filter"];
					source_name = json[i][j][k]["source_name"];
					source_link = json[i][j][k]["link"];
					r = r+1;
					if(r<3){
						var details_div = document.getElementById("detail_subs");
						divelement.innerHTML = "<h3><u><b>Details Of " +name+"</b></u></h3></br><h4><b>Source Name : " +
									" "+source_name+"</b></h4></br><h4><b>Source Link"+"   : " +
									" <a href="+source_link+">"+source_link+"</a></b></h4></br>";
						details_div.appendChild(divelement);
						divelement.setAttribute("class","alert alert-info");
						/*var detail_row = detail_table.insertRow(r);
            					var cell2 = detail_row.insertCell(0);
            					var cell3 = detail_row.insertCell(1);
            					cell2.innerHTML = source_name;
						cell3.innerHTML = source_link;*/
					}
					var query_row = query_table.insertRow(r);

					cell1 = query_row.insertCell(0);
                                        cell2 = query_row.insertCell(1);
                                        cell3 = query_row.insertCell(2);
                                        cell4 = query_row.insertCell(3);
					cell1.innerHTML = category_name;
					cell2.innerHTML = query_id;
					cell3.innerHTML = query_type;
					cell4.innerHTML = filter;
					counter = counter +1;
					if (counter>10)break;
				}
				if (counter>10)break;
			}
			if (counter>10)break;
		}

	} 
	);
}

function runQueries(){
	var subscriptions = $('#subscripted').val() || [];
	subscriptions = subscriptions.join(',');
	alert(subscriptions);
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php", {run:1, subscriptions: subscriptions}, function(data){ alert(data); });
}

function markMandatoryQueries(button, category){
	var subscriptionName = button.attr('name');
	if(button.attr('checked')){
		$('#' + subscriptionName).find('.mandatory_filter').attr('checked', true);
	}else if(!button.attr('checked')){
		$('#' + subscriptionName).find('.mandatory_filter').attr('checked', false);
	}
}

function getFilters(){
	queryMap = {};
	$('#queryDiv .accordion-body').each(function(){
		subscriptionName = $(this).attr('id');
		queryMap[subscriptionName] = {};
		queryMap[subscriptionName]['mandatory'] = []
		queryMap[subscriptionName]['optional'] = []
		$(this).find('.mandatory_filter').each(function(){
			if($(this).attr('checked')){
				queryMap[subscriptionName]['mandatory'].push($(this).attr('name'));
			}
		});

		$(this).find('.optional_filter').each(function(){
			if($(this).attr('checked')){
				queryMap[subscriptionName]['optional'].push($(this).attr('name'));
			}
		});
	});
	alert(queryMap['DFN-Honeypot']['optional'].length);
	//TODO send them to the server.
}

$(document).ready(function() {

	$('.subscription_toggle').iphoneStyle({
		checkedLabel: 'On',
		uncheckedLabel: 'Off',
		onChange: function(elem, value){
			subscription_toggle(elem);
		}
	});  

	$('.markAllMandatory').click(function() {
		markMandatoryQueries($(this), 'optional');
	}); 

	$('.nfqueryNav').click(function(){
		var tabName = $(this).text();
		$('#nfqueryTab').val(tabName);
		$('#navigationForm').submit();
	});

	$(".collapse").collapse();
	$('#runQueries').click(getFilters);

});
