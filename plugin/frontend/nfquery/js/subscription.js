function subscription_toggle(button){
	var button_status = 'Off';
	if (button.attr('checked')){
		button_status = 'On';
	}
	alert(button_status);
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
                for(var i = document.getElementById("detail_table").rows.length; i > 1;i--){
                        document.getElementById("detail_table").deleteRow(i -1);
                }

		var json = $.parseJSON(data);
		var counter = 0;
		for(i in json){
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
			var r = 1;
			for (j in json[i]){
				for(k in json[i][j]){
					category_id = json[i][j][k]["category_id"];
					query_id = json[i][j][k]["query_id"];
					query_type = json[i][j][k]["query_type"];
					filter = json[i][j][k]["filter"];
					r = r+1;
					var row = table.insertRow(r);
   					var cell1 = row.insertCell(0);
            				var cell2 = row.insertCell(1);
            				var cell3 = row.insertCell(2);
            				var cell4 = row.insertCell(3);
            				cell1.innerHTML=category_id;
            				cell2.innerHTML=query_id;
            				cell3.innerHTML=query_type;
            				cell4.innerHTML=filter;
					counter = counter +1;
					if (counter>10)break;
					
				}
				if (counter>10)break;
			}
			if (counter>10)break;
		}





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

	if (window.location.hash) {
			    $(window.location.hash).tab('show')
	}
});
