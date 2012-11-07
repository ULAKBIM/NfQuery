<?php
	#include('loghandler.php');
	$SUBDIRLAYOUT = 1;
    require_once('/var/www/nfsen/conf.php');
	require_once('/var/www/nfsen/nfsenutil.php');
	function isRegistered(){
		$command = 'nfquery::isRegistered';
		$opts = array();
		$outlist = nfsend_query($command, $opts);
		return $outlist['register'];
	
	}
	
        function generateQuery($query_info_list, $mandatory){
                error_log($mandatory);
		$command = 'nfquery::generateQuery';
		$opts = array('query_list'=>$query_info_list, 'mandatory'=>$mandatory);
		$out_list = nfsend_query($command, $opts);
                return $out_list;
        }	
	function getMyAlerts(){
		$command = 'nfquery::getMyAlerts';
		$opts = array();
		$out_list = nfsend_query($command, $opts);
		$output = "";
		for($i=0;$i<sizeof($out_list);$i++){
			$index="".$i;
			$line = $out_list[$index];
			$output = $output.$line;
        }
        $alerts = json_decode($output, true);

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
		echo '<div class="alert alert-info">';
		echo '<table class="table">';
		echo '<tr><th>#</th><th>Matched</th><th>Total</th><th>Percent</th></tr>';

		echo '<tr><td class="outputInfoLabel"><strong>Flows</strong></td>';
		echo '<td>'.$out_list['matched_flows'].'</td>';
		echo '<td>'.$out_list['total_flows_processed'].'</td>';
		$percent = $out_list['matched_flows']*100;
		$percent = $percent / $out_list['total_flows_processed'];
		echo '<td>% '.intval($percent).'</td></tr>';

		echo '<tr><td class="outputInfoLabel"><strong>Queries</strong></td>';
		echo '<td>'.sizeof($out_list['matched_queries']).'</td>';
		echo '<td>'.sizeof($out_list['query_id']).'</td>';
		$percent = sizeof($out_list['matched_queries'])*100;
		$percent = $percent / sizeof($out_list['query_id']);
		echo '<td>% '.intval($percent).'</td></tr>';


		echo '</table>';
		echo '</div>';

		#
		#Show staticstics in a sortable table.
		#
		echo '<div>';
		echo '<table class="table table-bordered table-condensed tablesorter" id="'.$subscriptionName.'Statistics">';
		echo '<thead>';
		echo '<tr><th class="header">Query Id</th><td style="background-color:#E6EEEE"><strong>Filter</strong></td><th class="header">Total Flows</th><th class="header">Total Bytes</th><th class="header">Total Packets</th></tr>';
		echo '</thead>';
		$query_ids = $out_list['query_id'];
		echo '<tbody>';
		for($i = 0; $i<sizeof($query_ids); $i++){
			echo '<tr>';
			echo '<td class="query_id">'.$query_ids[$i].'</td>';
			echo '<td>'.$out_list['filters'][$i].'</td>';
			echo '<td>'.$out_list['total_flows'][$i].'</td>';
			echo '<td>'.$out_list['total_bytes'][$i].'</td>';
			echo '<td>'.$out_list['total_packets'][$i].'</td>';
			echo '</tr>';
		}
		echo '</tbody>';
		echo '</table>';
		echo '<button class="btn btn-success pushOutput" onClick=pushOutput("'.$subscriptionName.'")>Send Output To Query Server</button>';
		#echo '<button class="btn btn-success" data-toggle="collapse" data-target="#'.$subscriptionName.'OutputTable">Send Output To Query Server</button>';
		echo '</div>';
		#echo '<div id="'.$subscriptionName.'OutputTable" class="collapse">';
		#echo 'OMW';
		#echo '</div>';
		
	}

    function pushOutput($subscriptionName){
		$command = 'nfquery::pushOutputToQueryServer';
		$opts = array();
		$opts['subscriptionName'] = $subscriptionName;
        $out_list = nfsend_query($command, $opts);
        echo "1";
    }

	function getOutputOfQuery($subscriptionName, $query_id){
		$command = 'nfquery::getOutputOfQuery';
		$opts = array();
		$opts['subscriptionName'] = $subscriptionName;
		$opts['query_id'] = $query_id;
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
		foreach ($output as $table){
				if ( $table['srcip_alert_plugin']){
					echo '<tr class="error">';				
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
				echo '<td>'.$query_id.'</td>';
				echo '</tr>';
		}
		
		echo '</table>';

	}

	function getStatisticsOfAlert($alert_id){
		$command = 'nfquery::getStatisticsOfAlert';
		$opts = array();
		$opts['alert_id'] = $alert_id;
		$out_list = nfsend_query($command, $opts);
		$output = "";
		for($i=0;$i<sizeof($out_list);$i++){
			$index="".$i;
			$line = $out_list[$index];
			$output = $output.$line;
        }
        $output = json_decode($output, true);

        return $output;
    }

	function getOutputOfSubscription($subscriptionName, $total_query, $page_number){
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
		
		$query_per_page = 50;
		$pagination = ($total_query < $query_per_page * $page_number)?1:0;	
		$start = 0;
		if ($pagination){
			$start = $query_per_page * $page_number;
		}
		$counter = 0;	
		$colorList = array("#3399FF", "#FCF8E3", "#C6F6C3");

		foreach ($output as $query_id=>$result){
			foreach ($result as $table){
				if ($pagination){
					if ($counter < $start) continue;
					if ($counter == $start + $query_per_page){
						echo '</table>';
						return;
					}
				}

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
				$counter ++;
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
		$conf = parse_ini_file('/var/www/nfsen/plugins/nfquery/remember.conf',1);
		return $conf["remember"];
#		$remember = array();
#		$remember2 = array();
##		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
##		while (!feof($file)){
##
##			$line = fgets($file);
##			list($id, $status) = explode('=', $line);
##			$remember[$id] = substr($status, 0, strlen($status) - 1);
##		}
##		fclose($file);
#		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf", "r");
#		$data = fread($file,filesize("/var/www/nfsen/plugins/nfquery/remember.conf"));
#		$mydata=json_decode($data);
#		$remember = $mydata->{'remember'};
#		foreach($remember as $key => $value){
#			$remember2[$key] = $value;
#		}
#		fclose($file);
#		return $remember2;
	}


	function editRememberFile(){	
		$conf = parse_ini_file('/var/www/nfsen/plugins/nfquery/remember.conf',1);
	        $remember = $conf["remember"];	
		$conf = parse_ini_file('/var/www/nfsen/plugins/nfquery/remember.conf',1);
	        $prefix = $conf["prefix"];
		var_dump($remember);	
		$file = fopen("/var/www/nfsen/plugins/nfquery/remember.conf","w");
		$button_id = $_POST['button_id'];
		$button_status = $_POST['button_status'];
		$remember["$button_id"] = (strcmp($button_status, "On") == 0) ? 1 : 0;
		fwrite($file,"[remember]\n");
		for($i = 1; $i <= sizeof($remember); $i++){
			fwrite($file, "$i=$remember[$i]\n");
		}
		fwrite($file,"[prefix]\n");
		fwrite($file,"1=$prefix[1]\n");
		
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

            $cmd_opts['start_time'] = $_SESSION['tleft'];
            $cmd_opts['end_time'] = $_SESSION['tright'];
        	// a single 5 min timeslice
       		$tslot1 = UNIX2ISO($_SESSION['tleft']);
        	$subdirs = SubdirHierarchy($_SESSION['tleft']);
        	if ( strlen($subdirs) == 0 )
           	 	$args .= " -r nfcapd.$tslot1";
        	else	
            	$args .= " -r $subdirs/nfcapd.$tslot1";

    	} else {
            $cmd_opts['start_time'] = $_SESSION['tleft'];
            $cmd_opts['end_time'] = $_SESSION['tright'];
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
	
	function compileVerificationArgs($first_seen){
		$cmd_opts = array();

		$args = '';


        #calculate new timestamp to find right flow file.
        $time = $first_seen - ($first_seen % 300) + 300;
        $cmd_opts['start_time'] = $time;
        $cmd_opts['end_time'] = $time;

        // a single 5 min timeslice
       	$tslot1 = UNIX2ISO($time);
        $subdirs = SubdirHierarchy($time);

        if ( strlen($subdirs) == 0 )
         	$args .= " -r nfcapd.$tslot1";
        else	
        	$args .= " -r $subdirs/nfcapd.$tslot1";

		$args = $args.' -a';
		$args = "-T $args";
		
		$cmd_opts['args']    = $args;
		$cmd_opts['type']    = ($_SESSION['profileinfo']['type'] & 4) > 0 ? 'shadow' : 'real';
        $cmd_opts['profile'] = $_SESSION['profileswitch'];

        #Verification Queries Run On All Sources //TODO This may change !
        $cmd_opts['source'] = array();
        foreach($_SESSION['profileinfo']['channel'] as $channel=>$details){
            array_push($cmd_opts['source'], $channel);
        } 

		return $cmd_opts;

    }

	function runVerificationQueries($query, $first_seen, $identifier){
		$opts = array();
		$json = json_encode($queries);
		$cargs = compileVerificationArgs($first_seen);

		$opts['query'] = $query;
		$opts['identifier'] = $identifier;
		
		foreach($cargs  as $key=>$value){
			$opts[$key] = $value;
        }

		$out_list = nfsend_query('nfquery::runVerificationQueries', $opts);
        
        $output = "";
		for($i=0;$i<sizeof($out_list);$i++){
			$index="".$i;
			$line = $out_list[$index];
			$output = $output.$line;
		}
		$output = json_decode($output, true);

		return $output;
	}

	function runQueries($queries){
		$opts = array();
		$json = json_encode($queries);
		$cargs = compileArgs();

		$opts['queries'] = $json;
		
		foreach($cargs  as $key=>$value){
			$opts[$key] = $value;
		}
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
