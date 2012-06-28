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

function showStatistics(subscriptionName){
	if ($("#" + subscriptionName + "CollapseInner").hasClass('filled'))
		return;
	$("#" + subscriptionName + "CollapseInner").html('<center><img src="/nfsen/plugins/nfquery/img/loading.gif" class="loading">Content Loading...</center>');
	$.get('/nfsen/plugins/nfquery/ajaxhandler.php', 
		{getStatisticsOfSubscription: 1,
		 subscriptionName: subscriptionName
		},
	   	function (data){
			$("#" + subscriptionName + "CollapseInner").html(data);
			$("#" + subscriptionName + "CollapseInner").addClass('filled');
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
					showStatistics(key);
				});
			}
		}
	});
    setTimeout(checkQueryStatus, 2500);
}

$(document).ready(function(){
});
