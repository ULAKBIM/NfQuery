<?php
    if (array_key_exists('query', $_POST) && array_key_exists('queryid', $_POST)){
       # if ($_POST['starttime'] && $_POST['endtime']){
       #     $_SESSION['tleft'] = $_POST['starttime'];
       #     $_SESSION['tright'] = $_POST['endtime'];
       # }
        $_SESSION['nfquery']['query'] = $_POST['query'];
        $_SESSION['nfquery']['queryid'] = $_POST['queryid'];
        $output = runVerificationQueries($_POST['query'], $_POST['starttime'], $_POST['endtime'], $_POST['queryid']);
    }elseif($_SESSION['nfquery']['query'] && $_SESSION['nfquery']['queryid']){
        $output = runVerificationQueries($_SESSION['nfquery']['query'], $_SESSION['tleft'], $_SESSION['tright'], $_SESSION['nfquery']['queryid']);
    }else{
        exit('<div class="alert alert-error">Check parameters !</div>');
    }
?>

<div class="row-fluid">
    <div class="span12">
        <?php
            DisplayDetails();
        ?>
    </div>
</div>

<script src="plugins/nfquery/js/running.js"></script>
<div class="row-fluid">
    <div class="span12">
        <h4>Output Of Verification Query</h4>
        <div class="alert alert-info">
            Query: <? echo $output['verification_command']; ?>
        </div>
        <div class="verification_output">
            <table class="table .table-striped">
                 <tr>
                 <td>Date</td>
                 <td>flow start</td>
                 <td>Duration</td>
                 <td>Proto</td>
                 <td>Src Ip Addr:Port</td>
                 <td>Dst IP Addr:Port</td>
                 <td>Packets</td>
                 <td>Bytes</td>
                 <td>Flows</td>
                 </tr>
                 <?php 
                     $output = $output['output'];
                     $stats = $output['stats'];
                     foreach ($output as $table){
                        if (isset($table['srcip_alert_plugin']) || isset($table['dstip_alert_plugin'])){     
                            echo "<tr class='error'>";
                        }else{
                            echo "<tr>";
                        }
                        echo "<td>".$table['date']."</td>";
                        echo "<td>".$table['flow_start']."</td>";
                        echo "<td>".$table['duration']."</td>";
                        echo "<td>".$table['proto']."</td>";
                        echo "<td><a class='ip' onclick=lookup(this)>".$table['srcip_port']."</a></td>";
                        echo "<td><a class='ip' onclick=lookup(this)>".$table['dstip_port']."</a></td>";
                        echo "<td>".$table['packets']."</td>";
                        echo "<td>".$table['bytes']."</td>";
                        echo "<td>".$table['flows']."</td>";
                        echo "</tr>";
                     }
                 ?>
            </table>
        </div>
    </div>
</div>
