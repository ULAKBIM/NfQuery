<?php
   require_once('nfqueryutil.php');

   $alerts = getMyAlerts();
   
   $critical_alerts = $alerts['critical_alerts']; 
   $multi_domain_alerts = $alerts['multi_domain_alerts']; 
   $single_domain_alerts = $alerts['single_domain_alerts']; 
?>

<div class="row-fluid">
	<div class="span12">
        <h2>ALERTS</h2>
	</div>
</div>

<div class="row-fluid">
    <div class="span12">
        <h4>Critical Alerts</h4>
        <div class="critical_alerts">
        <table class="table table-condensed table-hover">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Source</th>
            <th>Time Interval</th>
            <th></th>
        </tr>
        <?php
            if (count($critical_alerts) == 0){
                echo "<tr><td colspan=8><span class='label label-important'>There is no critical alert.</span></td></tr>";
            }else{
                foreach($critical_alerts as $alert){
                    echo "<tr>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['source_name']."</span></td>";
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
        <h4>Multi Domain Alerts</h4>
        <div class="multi_domain_alerts">
        <table class="table table-condensed table-hover">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Identifier</th>
            <th>Correspondant</th>
            <th>Time Interval</th>
            <th></th>
        </tr>
        <?php
            if (count($multi_domain_alerts) == 0){
                echo "<tr><td colspan=8><span class='label label-important'>There is no multi domain alert.</span></td></tr>";
            }else{
                foreach($multi_domain_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td><span class='label label-warning'>".$alert['identifier_plugin_name']."</span></td>";
                    echo "<td><span class='label label-warning'>".$alert['identified_plugin_name']."</span></td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['start_time'])." - ".date("Y/m/d H:i:s", $alert['end_time'])."</td>";
                    echo "<td>"."<button class='btn btn-small btn-primary run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' starttime='".$alert['start_time']."' endtime='".$alert['end_time']."'>Run Now</button>"."</td>";
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
        <h4>Single Domain Alerts</h4>
        <div class="single_domain_alerts">
        <table class="table table-hover table-condensed">
        <tr>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Time Interval</th>
            <th></th>
        </tr>
        <?php
            if (count($single_domain_alerts) == 0){
                echo "<tr><td colspan=8><span class='label label-important'>There is no single domain alert.</span></td></tr>";
            }else{
                foreach($single_domain_alerts as $alert){
                    echo "<tr class='error'>";
                    echo "<td>".$alert['query_id']."</td>";
                    echo "<td>".$alert['query_filter']."</td>";
                    echo "<td>".date("Y/m/d H:i:s", $alert['start_time'])." - ".date("Y/m/d H:i:s", $alert['end_time'])."</td>";
                    echo "<td>"."<button class='btn btn-small btn-primary run' queryid='".$alert['query_id']."' query='".$alert['query_filter']."' starttime='".$alert['start_time']."' endtime='".$alert['end_time']."' </td>";
                    echo "</tr>";
                }
            }
        ?>
        </table>
		</div>
	</div>
</div>
