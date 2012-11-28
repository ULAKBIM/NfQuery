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
        <div class="identifier_alerts">
        <table class="table table-condensed table-hover">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Identified Plugin</th>
            <th>Matched Bytes</th>
            <th>Matched Packets</th>
            <th>Matched Flows</th>
            <th>First Seen</th>
            <th>Checksum</th>
            <th></th>
        </tr>
        <?php
            if (count($identifier_alerts) == 0){
                echo "<tr><td colspan=8>There is no identifier alert.</td></tr>";
            }else{
                foreach($identifier_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['identified_plugin_name']."</span></td>";
                    echo "<td>".$alert['statistic']['number_of_bytes']."</td>";
                    echo "<td>".$alert['statistic']['number_of_packets']."</td>";
                    echo "<td>".$alert['statistic']['number_of_flows']."</td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['first_seen'])."</td>";
                    echo "<td>".$alert['checksum']."</td>";
                    echo "<td>"."<img class='run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' firstseen='".$alert['first_seen']."' identifier='".$alert['identifier_plugin_id']."' src='/nfsen/plugins/nfquery/img/run.png'>"."</td>";
                    echo "</tr>";
                }
            }
        ?>
        </table>
		</div>
	</div>
</div>


<div class="row-fluid">
    <div class="span11">
        <h4>Identified Alerts</h4>
        <div class="identified_alerts">
        <table class="table table-hover table-condensed">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Identifier Plugin</th>
            <th>Matched Bytes</th>
            <th>Matched Packets</th>
            <th>Matched Flows</th>
            <th>First Seen</th>
            <th>Checksum</th>
        </tr>
        <?php
            if (count($identified_alerts) == 0){
                echo "<tr><td colspan=8>There is no identified alert.</td></tr>";
            }else{
                foreach($identified_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['identified_plugin_name']."</span></td>";
                    echo "<td>".$alert['statistic']['number_of_bytes']."</td>";
                    echo "<td>".$alert['statistic']['number_of_packets']."</td>";
                    echo "<td>".$alert['statistic']['number_of_flows']."</td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['first_seen'])."</td>";
                    echo "<td>".$alert['checksum']."</td>";
                    echo "<td>"."<img class='run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' firstseen='".$alert['first_seen']."' identifier='".$alert['identifier_plugin_id']."' src='/nfsen/plugins/nfquery/img/run.png'>"."</td>";
                    echo "</tr>";
                }
            }
        ?>
        </table>
		</div>
	</div>
</div>
