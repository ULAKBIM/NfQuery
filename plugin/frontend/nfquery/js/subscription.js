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


function getSubscriptionDetail(name){
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
                for(var i = document.getElementById("detail_table").rows.length; i > 0;i--){
                        document.getElementById("detail_table").deleteRow(i -1);
                }
                for(var i = document.getElementById("query_table").rows.length; i > 0;i--){
                        document.getElementById("query_table").deleteRow(i -1);
                }
		$("#anchor_id").remove();
		var json = $.parseJSON(data);
		var counter = 0;
		for(i in json){
			var detail_table=document.getElementById("detail_table");
			var query_table=document.getElementById("query_table");
			var detail_row = detail_table.insertRow(0);
			var detail_cell = detail_row.insertCell(0);
			detail_cell.innerHTML = "<b>Detail Of " + name + "</b>";
            	        detail_row = detail_table.insertRow(1);
            		var detail_cell2 = detail_row.insertCell(0);
            		var detail_cell3 = detail_row.insertCell(1);
            		var detail_cell4 = detail_row.insertCell(2);
            		detail_cell2.innerHTML="<b>Category Name</b>";
            		detail_cell3.innerHTML="<b>Source Name</b>";
            		detail_cell4.innerHTML="<b>Source Link</b>";



			var query_row = query_table.insertRow(0);
			var query_cell = query_row.insertCell(0);
			query_cell.innerHTML = "<b>Query Informations Of " + name + "</b>";
			query_row = query_table.insertRow(1);
			var cell1 = query_row.insertCell(0);
			var cell2 = query_row.insertCell(1);
			var cell3 = query_row.insertCell(2);
			var cell4 = query_row.insertCell(3);
		        cell1.innerHTML = "<b>Category Name</b>";
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
						var detail_row = detail_table.insertRow(r);
   						var cell1 = detail_row.insertCell(0);
            					var cell2 = detail_row.insertCell(1);
            					var cell3 = detail_row.insertCell(2);
            					cell1.innerHTML = category_name;
            					cell2.innerHTML = source_name;
						cell3.innerHTML = source_link;
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


		var mydiv=document.getElementById("accordion_div_id");
		var element = document.createElement('a');
		element.setAttribute("class","accordion-toggle");
		element.setAttribute("id","anchor_id");
		element.href = "#collapseOne";
		element.innerHTML = "Queries";
		element.setAttribute("data-toggle","collapse");
		element.setAttribute("data-parent","#accordion2");
		mydiv.appendChild(element);


	/*	var aray = data.split(",");
		var i = 0;
		var j = 0 ;
		for(var i = document.getElementById("detail_table").rows.length; i > 1;i--){
			document.getElementById("detail_table").deleteRow(i -1);
		}
		var table=document.getElementById("detail_table");
		var row = table.insertRow(1);
		var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);
                var cell4 = row.insertCell(3);
		cell1.innerHTML="Category";
                cell2.innerHTML="Query";
                cell3.innerHTML="Query Type";
                cell4.innerHTML="Filter";
		while(i <37){
			x = aray[i].split(":");
			var l = x.length;
			var category = x[l-1];
			i = i+1;
			x = aray[i].split(":");
                        var l = x.length;
                        var query = x[l-1];
			i=i+1;
			x = aray[i].split(":");
                        var l = x.length;
                        var query_type = x[l-1].split("'")[1];
			i=i+1;
			x = aray[i].split(":");
                        var l = x.length;
                        var filter = x[l-1];
			i=i+1;
			j = j+1;
			var row = table.insertRow(j+1);
			var cell1 = row.insertCell(0);
			var cell2 = row.insertCell(1);
			var cell3 = row.insertCell(2);
			var cell4 = row.insertCell(3);
			cell1.innerHTML=category;
			cell2.innerHTML=query;
			cell3.innerHTML=query_type;
			cell4.innerHTML=filter;
		}*/
	} 
	);
}
$(document).ready(function() {

	$('.subscription_toggle').iphoneStyle({
		checkedLabel: 'On',
		uncheckedLabel: 'Off',
		onChange: function(elem, value){
			subscription_toggle(elem);
		}
	});  

	$('.nfqueryNav').click(function(){
		var tabName = $(this).text();
		$('#nfqueryTab').val(tabName);
		$('#navigationForm').submit();
	});
	$(".collapse").collapse();
});
