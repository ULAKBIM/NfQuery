<?php
    if ($_POST['query'] && $_POST['firstseen'] && $_POST['identifier']){
        $output = runVerificationQueries($_POST['query'], $_POST['firstseen'], $_POST['identifier']);
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
                echo nl2br($output['output2']);
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
                echo nl2br($output['output1']);
            ?>
        </div>
    </div>
</div>
