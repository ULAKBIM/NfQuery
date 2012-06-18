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
		$subscriptiondetail = "";
		for($i=0;$i<sizeof($out_list);$i++){
			$index="".$i;
			$line = $out_list[$index];
			$subscriptiondetail = $subscriptiondetail.$line;
		}
		/*foreach($out_list as $line){
			$subscriptiondetail = $subscriptiondetail."".$line;
			
		}
		*/
	        //$p=1;	
		//$subscriptiondetail = $subscriptiondetail."".$out_list["0"]."".$out_list["1"]."".$out_list["2"]."".$out_list["3"]."".$out_list["4"];
		return $subscriptiondetail;
	}

	function parseRememberFile(){
		$remember = array();
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
		
		while (!feof($file)){
			$line = fgets($file);
			list($id, $status) = explode('=', $line);
			$remember[$id] = substr($status, 0, strlen($status) - 1);
		}
		fclose($file);

		return $remember;
	}


	function editRememberFile(){

		$remember = parseRememberFile();	
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf","w");
		
		$button_id = $_POST['button_id'];
		$button_status = $_POST['button_status'];
		$remember[$button_id] = (strcmp($button_status, "On") == 0) ? 1 : 0;
	
		for($i = 1; $i < sizeof($remember); $i++){
			fwrite($file, "$i=$remember[$i]\n");
		}

		fclose($file);
	}
	
	function getSubscriptedSubscription(){
		$remember = parseRememberFile();
		$subscriptions = getSubscriptions();
		$subscripted = array();

		for($i=1; $i < sizeof($remember); $i++){
			if (strcmp($remember[$i], "1") == 0){
				array_push($subscripted, $subscriptions[$i - 1]);
			}
		}

		return $subscripted;
	}
	
	function runSubscriptionQueries($subscription){

	}
?>
