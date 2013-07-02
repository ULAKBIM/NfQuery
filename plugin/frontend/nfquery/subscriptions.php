<link rel="stylesheet" href="plugins/nfquery/css/style.css" type="text/css"/>
<script src="plugins/nfquery/js/iphone-style-checkboxes.js" type="text/javascript" charset="utf-8"></script>

<div class="row-fluid">
	<div class="span6">
		<h3>Subscription Management</h3>
	</div>
</div>

<div class="row-fluid" style="padding-top:10px">
	<div class="span4" style="padding-top:10px" id="subscription_list">
		<table id="subscription_table" class="table table-striped table-bordered table-condensed" style="cursor:pointer">
			<tr><th>Subscriptions</th><th>Status</th></tr>

			<?php

				require_once('nfqueryutil.php');

                $subscriptions = getSubscriptions();
                asort($subscriptions);
				$remember = parseRememberFile();
				foreach($subscriptions as $id=>$name) {
					echo '<tr onclick=getSubscriptionDetail3("'.$name.'")><td>'.$name.'</td>';
					if (isset($remember[$id]) && $remember[$id] == 1){ 
						echo '<td>'.'<input type="checkbox" checked="checked" id="'.($id).'" class="subscription_toggle"/>'.'</td></tr>';
					}else{
						echo '<td>'.'<input type="checkbox" id="'.($id).'" class="subscription_toggle"/>'.'</td></tr>';
					}
				}

			?>
		</table>
	</div>
	<div class="span7" id="subscription_details" style="padding-top:10px">
		<!--  SubscriptionDetail2()
		<div id="detail_subs">
		</div>
		<div id="accordion2" class="accordion" style="visibility:hidden">
			<div id="accordion_group1" >
				<div id="accordion_div_id" class="accordion-heading">
				</div>
				<div id="collapseOne" class="accordion-body in collapse" style="height: auto;">
					<div class="accordion-inner" id="accordion_table"> 
						<table id="query_table" class="table table-striped">
						</table>
					</div>
				</div>
			</div>
		</div>
		-->
	
	</div>
</div>
