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
				$remember = parseRememberFile();
				for($i = 0; $i < sizeof($subscriptions); ++$i) {
					echo '<tr onclick=getSubscriptionDetail("'.$subscriptions[$i].'")><td>'.$subscriptions[$i].'</td>';
					if ($remember[$i+1] == 1){ 
						echo '<td>'.'<button id="'.($i+1).'" class="btn btn-success subscription_toggle">On</button>'.'</td></tr>';
					}else{
						echo '<td>'.'<button id="'.($i+1).'" class="btn btn-danger subscription_toggle">Off</button>'.'</td></tr>';
					}
				}

			?>

		</table>
	</div>
	<div class="span7" id="subscription_details" style="max-height:150px;">
		<table id="detail_table" class="table table-striped table-bordered table-condensed">
			<tr><th>Details Of Selected Subscription</th></tr>
		<!--	<?php/*
				$detail = getSubscriptionDetail("Amada");
				print $detail;				*/
			?>-->
		</table>
	</div>
</div>
