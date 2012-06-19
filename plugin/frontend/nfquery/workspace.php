<div class="row-fluid">
	<div class="span11">
		<?php
			DisplayDetails();
			#DisplayProcessing();
        ?>  
	</div>
</div>

<div class="row-fluid">
	<h3>Run Queries</h3>
	<div class="span4">
		<?php
			require_once('nfqueryutil.php');
			
			$subscripted = getSubscriptedSubscription();
			$squeries = getSubscriptionQueries($subscripted);
			if ($subscripted){
				echo '<table id="query_table" class="table table-striped table-bordered table-condensed">';
				echo '<tr><th>Subscriptions</th></tr>';
			}

			foreach($subscripted as $s){
				echo '<tr><td data-toggle="collapse" style="cursor:pointer;" data-target="#'.$s.'">'.$s.'</td><td><input type="checkbox" name="'.$s.'" class="toggle" class="query_toggle">Include Optional Queries</input></td></tr>';
				echo '<tr><td colspan=2><div id='.$s.' class="collapse in" style="max-height:250px;overflow:auto">';
				if ($squeries[$s]){
					echo '<table style="width:100%">';
					foreach($squeries[$s] as $k1=>$package){
						foreach($package as $index=>$query){
							echo '<tr class="amada_queries"><td><input type="checkbox" class="filter_enabled '.$query['category_name'].'" name="'.$query['query_id'].'"/></td><td class="filter">'.$query['filter'].'</td></tr>';
						}
					}
					echo '</table>';
					echo '</div></td></tr>';
				}else{
					echo '<div class="alert alert-info">No Queries Found.</div>';
				}
			}

			if ($subscripted){
				echo '</table>';
			}
			echo '<a id="runQueries" class="btn btn-primary">Run !</a>'
		?>  
	</div>
	<div class="span3">
		<?php

			echo '<label>'.'Select Flow Source: '.'</label>';		
			echo '<select id="flowSource" multiple="multiple">';
			foreach($_SESSION['profileinfo']['channel'] as $channel=>$details){
				echo '<option>'.$channel.'</option>';
			}
			echo '</select>';
		?>
	</div>
</div>
