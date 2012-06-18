<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/style.css" type="text/css"/>
<script src="/nfsen/plugins/nfquery/js/iphone-style-checkboxes.js" type="text/javascript" charset="utf-8"></script>
<div class="row">
<h3>Subscription Management</h3>
</div>
<div class="row-fluid" style="padding-top:10px">
	<div class="span4" id="subscription_list">
		<table id="subscription_table" class="table table-striped table-bordered table-condensed" style="cursor:pointer">
			<tr><th>Subscriptions</th><th>Status</th></tr>

			<?php

				require_once('nfqueryutil.php');

				$subscriptions = getSubscriptions();
				$remember = parseRememberFile();
				for($i = 0; $i < sizeof($subscriptions); ++$i) {
					echo '<tr onclick=getSubscriptionDetail("'.$subscriptions[$i].'")><td>'.$subscriptions[$i].'</td>';
					if ($remember[$i+1] == 1){ 
						echo '<td>'.'<input type="checkbox" checked="checked" id="'.($i+1).'" class="subscription_toggle"/>'.'</td></tr>';
					}else{
						echo '<td>'.'<input type="checkbox" id="'.($i+1).'" class="subscription_toggle"/>'.'</td></tr>';
					}
				}

			?>
		</table>
	</div>
	<div class="span7" id="subscription_details">
		<table id="detail_table" class="table table-striped table-bordered">
		</table>
		<div id="accordion2" class="accordion">
			<div class="accordion-group">
				<div id="accordion_div_id" class="accordion-heading">
				</div>
				<div id="collapseOne" class="accordion-body in collapse" style="height: auto;">
					<div class="accordion-inner"> 
						<table id="query_table" class="table table-striped table-bordered table-condensed">
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
