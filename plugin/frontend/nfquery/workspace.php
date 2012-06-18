<div class="row-fluid">
	<div class="span11">
		<?php
			DisplayDetails();
			#DisplayProcessing();
        ?>  
	</div>
</body>

<div class="row-fluid">
	<div class="span4">
		<h3>Run Queries</h3>
		<?php
			require_once('nfqueryutil.php');
			
			$subscripted = getSubscriptedSubscription();

			echo '<label>'.'Select subscription: '.'</label>';		
			echo '<select id="subscripted">';
			foreach($subscripted as $s){
				echo '<option>'.$s.'</option>';
			}
			echo '</select>';

			echo '<a id="runQueries" class="btn btn-primary">Run !</a>'
		?>  
	</div>
</body>
