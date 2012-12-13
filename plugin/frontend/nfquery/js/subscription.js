var timerId;

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

function getSubscriptionDetail3(name){
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
		var json = $.parseJSON(data);
		var counter = 0;
		$("#subscription_desc").empty();
		$("#mydiv").empty();
		$("#subscription_desc").attr("class","");
		$("#mydiv").attr("class","");
		$("#queries").attr("class","");
		if($("#mandatory_table")!=null)
 			$("#mandatory_table").empty();
		for(i in json){
			var r = 1;
			for (j in json[i]){
				for(k in json[i][j]){
					category_name = json[i][j][k]["category_name"];
					query_id = json[i][j][k]["query_id"];
					query_type = json[i][j][k]["query_type"];
					filter = json[i][j][k]["filter"];
					source_name = json[i][j][k]["source_name"];
					source_link = json[i][j][k]["link"];
					subscription_type = json[i][j][k]["subscription_type"];
					r = r+1;
					if(r<3){
					     //$("#queries").attr("class","alert alert-info2");
					     if(category_name == "mandatory"){	
						$("#queries").append("<table id='mandatory_table' class='table table-striped table-condensed'></table>");
					     	$("#mandatory_table").append("<thead><tr class='accordion-heading'><th><h3>Mandatory</h3></th></tr></thead>");
					     	$("#mydiv").append("<b><center><h3><i class='icon-chevron-down'></i> Queries</h3></center></b>");
					    	$("#mandatory_table").append("<thead><tr><th>Query Id</th><th>Filter"+
										"</th></tr></thead><tbody>");
					     }
                                             if(subscription_type == 1){
		                                 var description = "Details Of " + name;
                      			     }
                         	             else{
                             	                 var description = "This subscription includes queries that are related to "+ name  + " activity.";

                         		     }
                                             

					     $("#subscription_desc").attr("class","alert alert-info");
					     $("#subscription_desc").append("<h4 style='color:black;'><u><b>" + description + "</b></u></h4></br><h4><b>Source Name :  "+
										source_name+"</b></h4></br><h4><b>Source Link"+"   :  <a href="+
										source_link+">"+source_link+"</a></b></h4></br>");
						
						

					}
					if(category_name == "mandatory"){	
					     $("#mydiv").attr("data-target","#queries");
					     $("#mydiv").attr("data-toggle","collapse");
					     $("#mydiv").attr("class","upDown accordion-heading");
					     $("#queries").attr("class","collapse");
					    var mandatory_table_row = "<tr class='mandatory_query'><td >"+query_id+"<td data-toggle='collapse'"+
									"data-target='#optional"+j+"'><b>&darr; "+filter+"</b><div id='optional"+j+
									"'class='collapse' ></td><td><span class='mandatory_query_popover badge badge-warning'>M</span></td></tr>";
					    $("#mandatory_table").append(mandatory_table_row);
						
					}
					if(category_name == "optional"){
						$("#optional"+j).append("<span class='optional_query' style='margin-left:10px;border-radius: 3px 3px 3px 3px;'>&#176; "+
									filter+"</span><span class='optional_query_popover badge badge-success'>O</span></br>");
					}
					//$("#queries").append("<span class='table'>"+query_id+" "+query_type+" "+filter+"</span></br>");
				}
			}
		}
		  $('.mandatory_query_popover').popover({
                	title: "Mandatory Query",
                	content: "Click Here to See Optional Queries Of This Mandatory Query"
        	  });
		  $('.optional_query_popover').popover({
                	title: "Optional Query",
                	content: "This is optional query."
       		  });
		 $('.upDown').click(function (){
                  changeCollapseIcon($(this));
        	 });


	
	} 
	);
}

function runQueries(){
	var subscriptions = $('#subscripted').val() || [];
	subscriptions = subscriptions.join(',');
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php", {run:1, subscriptions: subscriptions}, function(data){ 
		//alert(data);
	 });
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
    var isNull = true;
	var queryMap = {};
	queryMap['queries'] = {};
    
	$('#queryDiv .accordion-body').each(function(){
		subscriptionName = $(this).attr('id');
		queryMap['queries'][subscriptionName] = {};
		queryMap['queries'][subscriptionName]['mandatory'] = []
		queryMap['queries'][subscriptionName]['optional'] = []
		$(this).find('.mandatory_filter').each(function(){
			if($(this).attr('checked')){
                isNull = false;
				queryMap['queries'][subscriptionName]['mandatory'].push($(this).attr('name'));
			}
		});

		$(this).find('.optional_filter').each(function(){
			if($(this).attr('checked')){
                isNull = false;
				queryMap['queries'][subscriptionName]['optional'].push($(this).attr('name'));
			}
		});
	});

	//send them to the server.
	queryMap['source'] = $('#flowSource').val();
    if (isNull){
       alert("Select a Query First !");
    }else{
	    $.post('/nfsen/plugins/nfquery/ajaxhandler.php', {runQueries:queryMap}, function(data){});
	    	
	    $('#nfqueryTab').val('Running');
	    $('#navigationForm').submit();
    }

}

function changeCollapseIcon(column){
	var icon = column.find('i');
	if (icon.hasClass('icon-chevron-down')){
		icon.removeClass('icon-chevron-down');
		icon.addClass('icon-chevron-up');
	}else{
		icon.removeClass('icon-chevron-up');
		icon.addClass('icon-chevron-down');
	}
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
	
	//At least one flow source must be selected.Set First One Default here.
	$("#flowSource option:first").attr('selected','selected');

	$(".collapse").collapse();
	$('#runQueries').click(getFilters);
	
	$('.mandatory_query_popover').popover({
		title: "Mandatory Query",
		content: "Click Here to See Optional Queries Of This Mandatory Query"
	});

	$('.optional_query_popover').popover({
		title: "Optional Query",
		content: "This is optional query."
	});

	$('.upDown').click(function (){
		changeCollapseIcon($(this));
	});
});
