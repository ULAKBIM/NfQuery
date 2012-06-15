<?php 
    require_once('loghandler.php');
    require_once('nfqueryutil.php');
	
	if(isset($_POST['name'])){
    	$name = $_POST['name'];
        $result = getSubscriptionDetail($name);
		//var_dump($result);
        echo $result;
    }
	
	if(isset($_POST['status'])){
		editRememberFile();
	}

?>
