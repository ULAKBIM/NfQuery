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
		<div id="alertDiv">
		 <?php
                        require_once('nfqueryutil.php');

/*			$subscriptions = getMyAlerts();
			for($i = 0; $i < sizeof($subscriptions); ++$i) {
                                echo "<div class ='alert alert-block alert-error fade-in'>".$subscriptions[$i]."</div>\n";
			
                        }

                       require_once('nfqueryutil.php');
		       $myalerts = getMyAlerts();
		       var_dump($myalerts);*/
		?>
		<script type="text/javascript" language="JavaScript">
			getAlerts();
		</script>
		</div>
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
