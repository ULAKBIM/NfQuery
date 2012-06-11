<?php 
	require_once('/var/www/nfsen/lookup.php');
	require_once('/var/www/nfsen/nfsenutil.php');
?>
<div class="row">
<h3>Subscription Management</h3>
</div>
<div class="row-fluid" style="padding-top:10px">
	<div class="span4" id="subscription_list">
		<table class="table table-striped table-bordered table-condensed" style="cursor:pointer">
			<tr><th>Subscriptions</th></tr>
			<?php
				// the command to be executed in the backend plugin
				$command = 'nfquery::getSubscriptions';
				$opts = array();
				$out_list = nfsend_query($command, $opts);
				$subscriptions = $out_list['subscriptions'];
				foreach ($subscriptions as $subcription) {
					echo '<tr><td>'.$subcription.'</td>';
					echo '<td>'.'<button class="btn btn-danger subscription_toggle">Off</button>'.'</td></tr>';
				}
			?>
		</table>
	</div>
	<div class="span7" id="subscription_details" style="max-height:150px;overflow:auto;">
		<table class="table table-striped table-bordered table-condensed">
			<tr><th>Details Of Selected Subscription</th></tr>
		</table>
	</div>
</div>
