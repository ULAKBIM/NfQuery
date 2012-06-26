function showOutput(subscriptionName){
	$.get('/nfsen/plugins/nfquery/ajaxhandler.php', 
		{getOutputOfSubscription: 1, 
		 subscriptionName: subscriptionName
		},
	   	function (data){
			alert(data);
		}
	);
}

$(document).ready(function(){
});
