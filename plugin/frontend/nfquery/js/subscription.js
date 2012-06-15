function subscription_toggle(button){
	if (button.hasClass('btn-danger')){
		button.removeClass('btn-danger');
		button.addClass('btn-success');
		button.text('On');
		$.post("/nfsen/plugins/nfquery/nfqueryutil.php",
				{status: button.text()}, function (data){alert(data);});
		
	}else if(button.hasClass('btn-success')){
		button.removeClass('btn-success');
		button.addClass('btn-danger');
		button.text('Off');
	}
}


function getSubscriptionDetail(name){
	alert(name);
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
		var aray = data.split(",");
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
		}
	} 
	);
}
$(document).ready(function() {
	$('.subscription_toggle').click(function(){
		subscription_toggle($(this));			
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
