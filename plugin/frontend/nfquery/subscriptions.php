<div class="row">
<h3>Subscription Management</h3>
</div>
<div class="row-fluid" style="padding-top:10px">
	<div class="span4" id="subscription_list">
		<table id="subscription_table" class="table table-striped table-bordered table-condensed" style="cursor:pointer">
			<tr><th>Subscriptions</th></tr>
			<?php
				require_once('nfqueryutil.php');
				$subscriptions = getSubscriptions();
				foreach ($subscriptions as $subscription) {
					echo '<tr><td>'.$subscription.'</td>';
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
