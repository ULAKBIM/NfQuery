<?php
	require_once('loghandler.php');
    require_once('/var/www/nfsen/conf.php');
	require_once('/var/www/nfsen/nfsenutil.php');

	function getSubscriptions(){
		$command = 'nfquery::getSubscriptions';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$subscriptions = $out_list['subscriptions'];
		return $subscriptions;
	}

?>
