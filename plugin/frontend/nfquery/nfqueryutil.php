<?php
    #include('loghandler.php');
    require_once('/var/www/nfsen/conf.php');
	require_once('/var/www/nfsen/nfsenutil.php');
	function isRegister(){
		$command = 'nfquery::isRegister';
		$opts = array();
		$outlist = nfsend_query($command, $opts);
		return $outlist['register'];
	
	}
	
	function getMyAlerts(){
		$command = 'nfquery::getSubscriptions';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$alerts = $out_list['subscriptions'];
		return $alerts;
	}
	
	function lookup($ip_address){
		$opts = array('lookup'=>$ip_address);
		nfsend_query("@lookup", $opts, 1);
	}

	function getStatisticsOfSubscription($subscriptionName){
		$command = 'nfquery::getStatisticsOfSubscription';
		$opts = array();
		$opts['subscriptionName'] = $subscriptionName;
		$out_list = nfsend_query($command, $opts);

		echo '<div>';
		echo '<table class="table table-bordered table-condensed tablesorter">';
		echo '<thead>';
		echo '<tr><th class="header">Query Id</th><th class="header">Total Flows</th><th class="header">Total Bytes</th><th class="header">Total Packets</th></tr>';
		echo '</thead>';

		$query_ids = $out_list['query_id'];
		echo '<tbody>';
		for($i = 0; $i<sizeof($query_ids); $i++){
			echo '<tr>';
			echo '<td>'.$query_ids[$i].'</td>'.'<td>'.$out_list['total_flows'][$i].'</td>'.'<td>'.$out_list['total_bytes'][$i].'</td>'.'<td>'.$out_list['total_packets'][$i].'</td>';
			echo '</tr>';
		}
		echo '</tbody>';
		echo '</table>';
		echo '<button class="btn btn-success" data-toggle="collapse" data-target="#'.$subscriptionName.'OutputTable">Show Output</button>';
		echo '</div>';
		echo '<div id="'.$subscriptionName.'OutputTable" class="collapse">';
		echo 'OMW';
		echo '</div>';
		
	}

	function getOutputOfSubscription($subscriptionName){
		$command = 'nfquery::getOutputOfSubscription';
		$opts = array();
		$opts['subscriptionName'] = $subscriptionName;
		$out_list = nfsend_query($command, $opts);
		$output = "";
		for($i=0;$i<sizeof($out_list);$i++){
			$index="".$i;
			$line = $out_list[$index];
			$output = $output.$line;
		}
		$output = json_decode($output, true);

		echo '<table class="table table-bordered table-condensed">';
		echo '<tr><th>Date</th><th>Start</th><th>Duration</th><th>Proto</th><th>Src Ip:Port</th><th>Dst Ip:Port</th><th>Packets</th><th>Bytes</th><th>Flow</th><th>Query Id</th></tr>';
		
		$colorList = array("#3399FF", "#FCF8E3", "#C6F6C3");
		foreach ($output as $query_id=>$result){
			foreach ($result as $table){
				if ( $table['srcip_alert_prefix'] || $table['dstip_alert_prefix']){
					echo '<tr class="alert alert-error">';				
				}else{
					echo '<tr>';				
				}
				echo '<td>'.$table['date'].'</td>';
				echo '<td>'.$table['flow_start'].'</td>';
				echo '<td>'.$table['duration'].'</td>';
				echo '<td>'.$table['proto'].'</td>';
				echo '<td><a class="ip" onclick=lookup(this)>'.$table['srcip_port'].'</a></td>';
				echo '<td><a class="ip" onclick=lookup(this)>'.$table['dstip_port'].'</a></td>';
				echo '<td>'.$table['packets'].'</td>';
				echo '<td>'.$table['bytes'].'</td>';
				echo '<td>'.$table['flows'].'</td>';
				echo '<td style="background:'.$colorList[0].'">'.$query_id.'</td>';
				echo '</tr>';
			}
			$color = array_shift($colorList);
			array_push($colorList, $color);
		}

		echo '</table>';
	}
	
	function checkQueryStatus(){
		$command = 'nfquery::checkQueries';
		$opts = array();
		$out_list = nfsend_query($command, $opts);	
		$output = array();

		$subscriptions = $out_list['subscriptions'];
		foreach($subscriptions as $subs){
			$running_count=0;
			${"{$subs}mandatory"} = $out_list[$subs."-mandatory"];
			$counter = array_count_values($out_list[$subs."-mandatory-status"]);
			$running_count = $running_count+$counter['0'];
			$counter = array_count_values($out_list[$subs."-optional-status"]);
			$running_count = $running_count+$counter['0'];
			$totalQuery = sizeof($out_list[$subs."-optional"])+sizeof($out_list[$subs."-mandatory"]);
			$p = $running_count*100/$totalQuery;
			$output[$subs] = $p;
		}
		echo json_encode($output);
	}

	function checkQueries(){
		$command = 'nfquery::checkQueries';
		$opts = array();
		$out_list = nfsend_query($command, $opts);

		if (!$out_list['subscriptions']){ #if no query is active return alert.
			$result = '<div class="alert">No query is running.</div>';
			return $result;
		}

		$subscriptions = $out_list['subscriptions'];
		$result = '<div id="accordion2" class="accordion">';
		foreach($subscriptions as $subs){
			$result = $result.'<div class="accordion-group">';
			$result = $result.'<div class="accordion-heading">';
			$result = $result."<table class='table' id='checkQueryTable'>";
			$running_count=0;
			${"{$subs}mandatory"} = $out_list[$subs."-mandatory"];
			$counter = array_count_values($out_list[$subs."-mandatory-status"]);
			$running_count = $running_count+$counter['0'];
			$counter = array_count_values($out_list[$subs."-optional-status"]);
			$running_count = $running_count+$counter['0'];
			$totalQuery = sizeof($out_list[$subs."-optional"])+sizeof($out_list[$subs."-mandatory"]);
			$p = $running_count*100/$totalQuery;

			$result = $result."<tr><td style='width:300px'>".$subs."</td><td><div class='progress progress-striped active'> <div class='bar'".
					"style='width:".$p."%;' id='".$subs."Bar'>%".$p."</div></div></td>";

			#Check all queries are finished or not. if finished put button to show result of queries.
			if ( $p == 100 ){
				$result = $result.'<td>'.'<a class="accordion-toggle btn btn-success btn-small pull-right showStatistics" href="#'.$subs.'Collapse" onClick=showStatistics("'.$subs.'") id ="'.$subs.'" data-parent="#accordion2" data-toggle="collapse" >Show Statistics</a>'.'</td>';
			}else{
				$result = $result.'<td>'.'<a class="btn btn-small pull-right showStatistics"  id="'.$subs.'Output" disabled="disabled" >Show Statistics</a>'.'</td>';
			}
			
			$result = $result."</tr>";
			$result = $result.'</table>';
			$result = $result.'</div>';
			$result = $result.'</div>';

			$result = $result.'<div id="'.$subs.'Collapse" class="accordion-body collapse in outputAll">';
			$result = $result.'<div id="'.$subs.'CollapseInner" class="accordion-inner outputs">';
			$result = $result."Serhat";
			$result = $result.'</div>';
			$result = $result.'</div>';
		}
		$result = $result.'</div>';
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
		$remember2 = array();
#		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
#		while (!feof($file)){
#
#			$line = fgets($file);
#			list($id, $status) = explode('=', $line);
#			$remember[$id] = substr($status, 0, strlen($status) - 1);
#		}
#		fclose($file);
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
		$data = fread($file,filesize("/var/www/nfsen/plugins/nfquery/remember.conf"));
		$mydata=json_decode($data);
		$remember = $mydata->{'remember'};
		foreach($remember as $key => $value){
			$remember2[$key] = $value;
		}
		fclose($file);
		return $remember2;
	}


	function editRememberFile(){
		
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
		$data = fread($file,filesize("/var/www/nfsen/plugins/nfquery/remember.conf"));
		$mydata=json_decode($data);
		$prefix = $mydata->{'prefix'};
		fclose($file);
		$remember = parseRememberFile();	
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf","w");
		
		$button_id = $_POST['button_id'];
		$button_status = $_POST['button_status'];
		$remember["$button_id"] = (strcmp($button_status, "On") == 0) ? 1 : 0;
		$res=array();
		$rem=array();	
		for($i = 1; $i < sizeof($remember); $i++){
			$rem[$i]=$remember["$i"];
		}
		var_dump($rem);
		$res['remember'] = $rem;
		$res['prefix'] = $prefix;
		var_dump($res);
		fwrite($file,json_encode($res));

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
