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
        <h4>Identifier Alerts</h4>
        <div id="identifierAlertsDiv">
        <table class="table">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Start Time</th>
            <th>End Time</th>
        </tr>
        <?php

           foreach($identifier_alerts as $alert){
                echo "<tr>";
                echo "<td>".$alert['query_id']."</td>";
                echo "<td>".$alert['query_filter']."</td>";
                echo "<td>".date("Y/m/d H:m:s", $alert['start_time'])."</td>";
                echo "<td>".date("Y/m/d H:m:s", $alert['end_time'])."</td>";
                echo "</tr>";
            }
        ?>
        </table>
		</div>
	</div>
</div>
