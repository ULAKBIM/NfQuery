


function getQueryStatus(){
	$("#progres").append("<div class='bar' style='width: 90%;'></div>");
}

function getMyAlerts(){
	$.post("plugins/nfquery/ajaxhandler.php",{ getAlerts: "getAlerts"},function(data){
		alert(data[0]);
		var alertDiv = document.getElementById("alertDiv");
		alertDiv.setAttribute("class","alert alert-block alert-error fade in");
		
	});


}


function getSubscriptionDetail(name){
	$.post("plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
                for(var i = document.getElementById("detail_table").rows.length; i > 0;i--){
                        document.getElementById("detail_table").deleteRow(i -1);
                }
                for(var i = document.getElementById("query_table").rows.length; i > 0;i--){
                        document.getElementById("query_table").deleteRow(i -1);
                }
		$("#anchor_id").remove();
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
			
	
			var detail_table=document.getElementById("detail_table");
			var query_table=document.getElementById("query_table");
			var detail_row = detail_table.insertRow(0);
			var detail_cell = detail_row.insertCell(0);
			detail_cell.innerHTML = "<b>Details Of " + name + "</b>";
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

	} 
	);
}

function runQueries(){
	var subscription = $('#subscripted').val();
	$.post("plugins/nfquery/ajaxhandler.php", {run:1, subscription:subscription}, function(data){});
}

$(document).ready(function() {

	$('.nfqueryNav').click(function(){
		var tabName = $(this).text();
		$('#nfqueryTab').val(tabName);
		$('#navigationForm').submit();
	});

	$(".collapse").collapse();
	$('#runQueries').click(runQueries);

    $('.run').click(function(){
        $("#nfqueryTab").val("Verification");
        $("#query").val($(this).attr('query'));
        $("#queryid").val($(this).attr('queryid'));
        $("#starttime").val($(this).attr('starttime'));
        $("#endtime").val($(this).attr('endtime'));
        
        //TODO
        var mode = "0"; 
        if ($(this).attr('starttime') != $(this).attr('endtime'))
            mode = "1";
       // $("#mode").val(mode);
       // $("#time_left").val($(this).attr('starttime'));
       // $("#time_right").val($(this).attr('endtime'));

        $("#navigationForm").submit();
        
    });

});
