<?php
   require_once('nfqueryutil.php');

   $alerts = getMyAlerts();
   
   $identifier_alerts = $alerts['identifier']; 
   $identified_alerts = $alerts['identified']; 
?>

<div class="row-fluid">
	<div class="span12">
        <h2>Alerts</h2>
	</div>
</div>

<div class="row-fluid">
    <div class="span12">
        <h4>Alerts Identified By This Plugin </h4>
        <div class="identifier_alerts">
        <table class="table table-condensed table-hover">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Identified Plugin</th>
            <th>Time Interval</th>
            <th></th>
        </tr>
        <?php
            if (count($identifier_alerts) == 0){
                echo "<tr><td colspan=8><span class='label label-important'>There is no identifier alert.</span></td></tr>";
            }else{
                foreach($identifier_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['identified_plugin_name']."</span></td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['start_time'])." - ".date("Y/m/d H:i:s", $alert['end_time'])."</td>";
                    echo "<td>"."<button class='btn btn-small btn-primary run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' starttime='".$alert['start_time']."' endtime='".$alert['end_time']."' identifier='".$alert['identifier_plugin_id']."' src='/nfsen/plugins/nfquery/img/run.png'>Run Now</button>"."</td>";
                    echo "</tr>";
                }
            }
        ?>
        </table>
		</div>
	</div>
</div>


<div class="row-fluid">
    <div class="span12">
        <h4>Alerts Identified By Other Plugins </h4>
        <div class="identified_alerts">
        <table class="table table-hover table-condensed">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Identifier Plugin</th>
            <th>Time Interval</th>
            <th></th>
        </tr>
        <?php
            if (count($identified_alerts) == 0){
                echo "<tr><td colspan=8><span class='label label-important'>There is no identified alert.</span></td></tr>";
            }else{
                foreach($identified_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['identifier_plugin_name']."</span></td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['start_time'])." - ".date("Y/m/d H:i:s", $alert['end_time'])."</td>";
                    echo "<td>"."<button class='btn btn-small btn-primary run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' starttime='".$alert['start_time']."' endtime='".$alert['end_time']."' identifier='".$alert['identifier_plugin_id']."' src='/nfsen/plugins/nfquery/img/run.png'>Run Now</button>"."</td>";
                    echo "</tr>";
                }
            }
        ?>
        </table>
		</div>
	</div>
</div>
