<?php
    #include('loghandler.php');
    require_once('/var/www/nfsen/conf.php');
	require_once('/var/www/nfsen/nfsenutil.php');
	require_once('Thread.php');

	function getMyAlerts(){
		$command = 'nfquery::getSubscriptions';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$alerts = $out_list['subscriptions'];
		return $alerts;
	}

	function checkQueries(){
		$command = 'nfquery::checkQueries';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$subscriptions = $out_list['subscriptions'];
		$result="<table class='table' id='checkQueryTable'><thead><tr><th>Subscription</th><th>Status</th></tr></thead><tbody>";
		foreach($subscriptions as $subs){
			$running_count=0;
			${"{$subs}mandatory"} = $out_list[$subs."-mandatory"];
			$counter = array_count_values($out_list[$subs."-mandatory"]);
			$running_count = $running_count+$counter[1];
			$counter = array_count_values($out_list[$subs."-optional"]);
			$running_count = $running_count+$counter[1];
			$totalQuery = sizeof($out_list[$subs."-optional"])+sizeof($out_list[$subs."-mandatory"]);
			$p = $running_count*100/$totalQuery;
			$result = $result."<tr><td>".$subs."</td><td><div class='progress progress-striped active'> <div class='bar'".
    					"style='width:".$p."%;'></div></div></td></tr>";
		
		}
		return $result;
	}

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

	function compileArgs(){
		$cmd_opts = array();

		$args = '';

    	// From the argument checks, we know at least one source is selected
    	// multiple sources
    	if ( $_SESSION['tleft'] == $_SESSION['tright'] ) {
        	// a single 5 min timeslice
       		 $tslot1 = UNIX2ISO($_SESSION['tleft']);
        	$subdirs = SubdirHierarchy($_SESSION['tleft']);
        	if ( strlen($subdirs) == 0 )
           	 	$args .= " -r nfcapd.$tslot1";
        	else	
            	$args .= " -r $subdirs/nfcapd.$tslot1";

    	} else {
        	// several 5 min timeslices
        	$tslot1 = UNIX2ISO($_SESSION['tleft']);
        	$subdirs1 = SubdirHierarchy($_SESSION['tleft']);
        	$tslot2 = UNIX2ISO($_SESSION['tright']);
        	$subdirs2 = SubdirHierarchy($_SESSION['tright']);
        	if ( strlen($subdirs1) == 0 )
         	  	 $args .= " -R nfcapd.$tslot1:nfcapd.$tslot2";
        	else
            	$args .= " -R $subdirs1/nfcapd.$tslot1:$subdirs2/nfcapd.$tslot2";
    	}
		
		$args = $args.' -a';
		$args = "-T $args";
		
		$cmd_opts['args']    = $args;
		$cmd_opts['type']    = ($_SESSION['profileinfo']['type'] & 4) > 0 ? 'shadow' : 'real';
        $cmd_opts['profile'] = $_SESSION['profileswitch'];
		return $cmd_opts;

	}
	
	function runQueries($queries){
		$opts = array();
		$json = json_encode($queries);
		$cargs = compileArgs();

		$opts['queries'] = $json;
		
		foreach($cargs  as $key=>$value){
			$opts[$key] = $value;
		}
		var_dump($opts);
		$response = nfsend_query('nfquery::runQueries', $opts);

		 //TODO check response and show whats happening there 
		return true;
	}

	function getSubscriptionQueries($subscriptions){

        $squeries = array();
        foreach($subscriptions as $subscription){
            $json = getSubscriptionDetail($subscription);
            $details = json_decode($json, true);

            foreach($details as $k1=>$v1){
                    $squeries[$subscription] = $v1;
            }
        }

        return $squeries;
    }


?>
