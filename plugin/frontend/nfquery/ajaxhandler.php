<?php 
    require_once('loghandler.php');
    require_once('/var/www/nfsen/plugins/nfquery/nfqueryutil.php');
    if($_POST['name']){
    	$name = $_POST['name'];
        $result = getSubscriptionDetail($name);
        echo $result;
    }

?>
