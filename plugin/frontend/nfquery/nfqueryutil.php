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
	if (isset($_POST['status'])){
		echo "olacak gibi";
	}

?>
