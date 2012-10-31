<?php
   require_once('nfqueryutil.php');

   $alerts = getMyAlerts();
   
   $identifier_alerts = $alerts['identifier']; 
   $identified_alerts = $alerts['identified']; 
   
   var_dump($identifier_alerts);
?>

<div class="row-fluid">
	<div class="span11">
        <h2>Alerts</h2>
	</div>
</div>

<div class="row-fluid">
	<div class="span11">
		<div id="identifierAlertsDiv">
		</div>
	</div>
</div>
