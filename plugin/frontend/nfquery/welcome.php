<div class="row-fluid">
	<div class="span11">
	 	<fieldset><strong>Alerts</strong>
		<div id="alertDiv">
		 <?php
            require_once('nfqueryutil.php');

            $alerts = getMyAlerts();
            
            $identifier_alerts = $alerts['identifier']; 
            $identified_alerts = $alerts['identified']; 
            
            var_dump($identifier_alerts);
		?>
		</div>
	</div>
</div>
