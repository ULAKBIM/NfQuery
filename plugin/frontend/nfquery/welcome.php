<?php
   require_once('nfqueryutil.php');

   $alerts = getMyAlerts();
   
   $identifier_alerts = $alerts['identifier']; 
   $identified_alerts = $alerts['identified']; 
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
            <th>Matched Bytes</th>
            <th>Matched Packets</th>
            <th>Matched Flows</th>
            <th>First Seen</th>
            <th>Checksum</th>
        </tr>
        <?php
        
            foreach($identifier_alerts as $alert){
                $statistics = getStatisticsOfAlert($alert['alert_id'])
                echo "<tr>";
                echo "<td>".$alert['query_id']."</td>";
                echo "<td>".$alert['query_filter']."</td>";
                echo "<td>".$statistics['number_of_bytes']."</td>";
                echo "<td>".$statistics['number_of_packets']."</td>";
                echo "<td>".$statistics['number_of_flows']."</td>";
                echo "<td>".date("Y/m/d H:m:s", $alert['first_seen'])."</td>";
                echo "<td>".$alert['checksum']."</td>";
                echo "</tr>";
            }
        ?>
        </table>
		</div>
	</div>
</div>
