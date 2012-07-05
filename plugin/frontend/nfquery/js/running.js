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

function getOutputOfQuery(cell, subscriptionName){
	$.get('/nfsen/plugins/nfquery/ajaxhandler.php', 
		{getOutputOfQuery: 1,
		 subscriptionName: subscriptionName,
		 query_id: $(cell).html()
		},
	   	function (data){
			$('#outputModalBody').html(data);
			$('#outputModal').modal().css({
					      	width: 'auto',
					        'margin-left': function () {
									            return -($(this).width() / 2);
						}
			    });
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
			$('.query_id').click(function (){
				getOutputOfQuery($(this), subscriptionName);
			});
			$('.tablesorter').each(function(){
                var id = $(this).attr('id');
                if ($('#' + id).hasClass('tablesorted')) return;
                $('#' + id).tablesorter();
                $('#' + id).addClass('tablesorted');
            });
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

function lookup(anchor){
	if ($(anchor).hasClass('filled')) return;
	var ip_port = $(anchor).html();
	var ip = ip_port.split(":")[0];
	$(anchor).popover({title:'Lookup', content:'Content Loading', trigger: 'hover'});
	$(anchor).popover('show');
	$(anchor).addClass('filled');
	$.get("/nfsen/plugins/nfquery/ajaxhandler.php", {lookup:1, ip:ip},
		function (data){
			$(anchor).popover('hide');
			$(anchor).data('popover', null)
			$(anchor).popover({title:'Lookup', content:data, trigger: 'hover'});
			$(anchor).popover('show');
			$(anchor).addClass('filled');
		});
}

$(document).ready(function(){
});
