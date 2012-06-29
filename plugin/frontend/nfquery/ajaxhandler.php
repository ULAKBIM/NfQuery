<?php 
    require_once('loghandler.php');
    require_once('nfqueryutil.php');


	if(isset($_POST['map'])){
		$map = $_POST['map'];
		$json = json_encode($map);
		$fp = fopen('/home/ahmetcan/nfquery/plugin/backend/nfquery.plugin.conf', 'w');
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf","a");
		$res = array();
		$res['prefix'] = $_POST['prefix'];
		fwrite($fp,"#####################################\n");
		fwrite($fp,"######  Nfquery Plugin Conf #########\n");
		fwrite($fp,"#####################################\n\n\n");
		foreach($map as $key => $value){
			fwrite($fp,"#$key\n");
			fwrite($fp,"$key =  $value\n\n");
		}
		fwrite($file,json_encode($res));
		fclose($fp);
		fclose($file);
	}

	if(isset($_POST['getAlerts'])){
		$result = getSubscriptions();
		print($result);
	}
	if(isset($_POST['name'])){
    		$name = $_POST['name'];
        	$result = getSubscriptionDetail($name);
		echo($result);
        	//echo $result;
    }
	if(isset($_POST['button_status'])){
		editRememberFile();
	}
	if(isset($_POST['checkQueryStatus'])){
		checkQueryStatus();
	}	
	if(isset($_POST['runQueries'])){
		session_start();
		runQueries($_POST['runQueries']);
	}
	if(isset($_GET['getStatisticsOfSubscription'])){
		getStatisticsOfSubscription($_GET['subscriptionName']);
	}
	if(isset($_GET['getOutputOfSubscription'])){
		getOutputOfSubscription($_GET['subscriptionName']);
	}

?>
