<?php
    if ($_POST['query'] && $_POST['firstseen'] && $_POST['identifier'] && $_POST['queryid']){
        $output = runVerificationQueries($_POST['query'], $_POST['firstseen'], $_POST['identifier'], $_POST['queryid']);
    }else{
        exit('<div class="alert alert-error">Check parameters !</div>');
    }
?>


<div class="row-fluid">
    <div class="span11">
        <h4>Output Of Verification Query</h4>
        <div>
            <div class="alert alert-info">
                Query: <? echo $output['verification_command']; ?>
            </div>
            <?php 
                $output2 = $output['output2'];
                $stats2 = $output['stats2'];
                foreach ($output2 as $table){
                    var_dump($table);
                    break;
                }
            ?>
        </div>
    </div>
</div>

<div class="row-fluid">
    <div class="span11">
        <h4>Output Of Verification Query With Identifier Plugin IP</h4>
        <div class="alert alert-info">
            Query: <? echo $output['verification_command_with_ip']; ?>
        </div>
        <div>
            <?php 
                $output2 = $output['output2'];
                $stats2 = $output['stats2'];
            ?>
        </div>
    </div>
</div>
