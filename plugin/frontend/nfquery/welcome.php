<div class="row-fluid">
	<div class="span11">
	 	<fieldset><strong>Alerts</strong>
		<div id="alertDiv">
		 <?php
                        require_once('nfqueryutil.php');

			$alerts = getMyAlerts();
		    var_dump($alerts);
		?>
		<script type="text/javascript" language="JavaScript">
			//getAlerts();
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
