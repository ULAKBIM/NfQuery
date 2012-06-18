<div class="row-fluid">
	<div class="span4">
		<fieldset><strong>Recent Queries</strong>
	</div>
</div>
<div class="row-fluid">
 		<div class="span4">
   			<table data-spy="scroll" data-offset="0" class="table table-striped table-bordered table-condensed">
          		<?php
             	?>
			</table>

		</div>
</div>
<div class="row-fluid">
	<div class="span11">
	 	<fieldset><strong>Alerts</strong>

		 <?php

                       require_once('nfqueryutil.php');
		       $myalerts = getMyAlerts();
		       var_dump($myalerts);
		?>
		<script type="text/javascript" language="JavaScript">
			getAlerts();
		</script>
	</div>
</div>
<div class="row-fluid">
	<div class="span11">
		<table>
			<?php
            ?>  
       	</table>

	</div>
</div>
