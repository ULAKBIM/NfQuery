function showOutput(subscriptionName){
	$.get('/nfsen/plugins/nfquery/ajaxhandler.php', 
		{getOutputOfSubscription: 1, 
		 subscriptionName: subscriptionName
		},
	   	function (data){
			$("#" + subscriptionName + "CollapseInner").html(data);
		}
	);
}

function checkQueryStatus(){
    $.post("/nfsen/plugins/nfquery/ajaxhandler.php", {checkQueryStatus:"checkQueries"}, function(data){
    	var data = JSON.parse(data);
		for (var key in data){
			$("#" + key + "Bar").css('width', data[key] + "%");
			$("#" + key + "Bar").html("%" + data[key]);
			if (data[key] == 100 && ! ($('#' + key + "Output").hasClass('btn-success')) ){
				$('#' + key + "Output").attr('disabled', false);
				$('#' + key + "Output").removeClass('btn-disabled');
				$('#' + key + "Output").addClass('btn-success');
				$('#' + key + "Output").click(function(){
					$("#" + key + "Collapse").collapse('toggle');
					showOutput(key);
				});
			}
		}
	});
    setTimeout(checkQueryStatus, 2500);
}

$(document).ready(function(){
});
