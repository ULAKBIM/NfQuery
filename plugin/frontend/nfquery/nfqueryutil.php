<?php
    #include('loghandler.php');
    require_once('/var/www/nfsen/conf.php');
	require_once('/var/www/nfsen/nfsenutil.php');
	
	function getSubscriptions(){
		$command = 'nfquery::getSubscriptions';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$subscriptions = $out_list['subscriptions'];
		return $subscriptions;
	}
	
	function getSubscriptionDetail($name){
		$command = 'nfquery::getSubscriptionDetail';
		$opts = array();
		$opts['name'] = $name;
		$out_list = nfsend_query($command, $opts);
		$subscriptiondetail = $out_list['subscriptiondetail'];
		return $subscriptiondetail;
	}

	function parseRememberFile(){
		$remember = array();
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
		
		while (!feof($file)){
			$line = fgets($file);
			list($id, $status) = explode('=', $line);
			$remember[$id] = $status;
		}
		fclose($file);

		return $remember;
	}


	function editRememberFile(){

		$remember = parseRememberFile();	
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf","w");
		
		$button_id = $_POST['button_id'];
		$button_status = $_POST['status'];

		for($i = 0; $i < sizeof($remember); $i++){
			if ($i != $button_id)
				$status = $remember[$i];
			else
				$status = (strcmp($button_status, "On") == 0) ? 1 : 0; 
			fwrite($file, "$i=$status\n");
		}
		fclose($file);
	}

?>
