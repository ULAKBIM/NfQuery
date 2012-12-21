<?php 
    require_once('loghandler.php');
    require_once('nfqueryutil.php');

        if(isset($_POST['query_info_list'])){
            $query_info_list = $_POST['query_info_list'];
            $mandatory = $_POST['mandatory'];
            error_log($_POST['mandatory']);
            $result = generateQuery($query_info_list, $mandatory);
            echo $result;
        }
	if(isset($_POST['getAlerts'])){
		$result = getSubscriptions();
		print($result);
	}
	if(isset($_POST['name'])){
                $name = $_POST['name'];
                $result = getSubscriptionDetail($name, "new");

                $subscriptiondetail = $result;
                $html = "";
                $subs_name = "";
                $subscriptiondetail = json_decode($subscriptiondetail);
                foreach ($subscriptiondetail as $subscription_type=>$subscriptiondetails){
                    if ($subscription_type == 1){
                        $html .=<<<EOF
                        <h4><b>This subscription includes queries that are related to {$name} source.</b></h4></br>

EOF;
                    }
                    if ($subscription_type == 2){
                        $html .=<<<EOF
                        <h4><b>This subscription includes queries that are related to {$name} activity.</b></h4></br>
EOF;
                    }
                foreach ($subscriptiondetails as $source_name=>$det_main){
                    foreach ($det_main as $info=>$source_info){
                        if ($info == "source_link" ){
                            $source_link = $source_info;
                            continue;
                        }
                        if ($info == "source_name" ){
                            continue;
                        }
                        if ($info == "queries" ){
                            $query_list = $source_info;
                        }
                        $query_list_array = (array)$query_list;
                        $query_list_array_size = sizeof($query_list_array);
                        $html .=<<<EOF
                        <div class="accordion" id="accordion{$source_name}">
                            <div class="accordion-group">
                            <div class='alert alert-info'>
                                <div class="accordion-heading">
                                    <b>source name: {$source_name}</b></br>
                                    <b>source link: <a href={$source_link}>{$source_link}</a></b></br>
                                    <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion{$source_name}" href="#detailSubs{$source_name}">Queries</a>
                                </div>
                                </div>
                                <div id="detailSubs{$source_name}" class="accordion-body collapse">
                                    <div class="accordion-inner">
                                    <table id='mandatory_table{$source_name}' class='table table-striped table-condensed'>
                                        <thead><tr class='accordion-heading'><th colspan="2">Mandatory</th></tr></thead>
                                        <tr><th>Query Id</th><th>Filter</th></tr><tbody>
EOF;
                        foreach ($query_list as $index=>$packet_detail){

                            foreach ($packet_detail as $query_info=>$query_detail){
                                $query_detail_list = (array)$query_detail;
                                $filter = $query_detail_list['filter'];
                                $query_id = $query_detail_list['query_id'];
                                $category_name = $query_detail_list['category_name'];
                                if ($category_name == "mandatory"){
                                    $html .=<<<EOF
                                    <tr class='mandatory_query'><td>{$query_id}
                                        </td>
                                        <td data-toggle='collapse' data-target='#optional{$index}'>
                                            <a class="accordion-toggle" data-toggle="collapse" href="optional{$index}">
                                                <b>&darr; {$filter}
                                            </a>
                                            <div id='optional{$index}' class='collapse'></b>
EOF;
                                }
                                if ($category_name == "optional"){
                                    $html .=<<<EOF
                                    <span class='optional_query' style='margin-left:10px;border-radius: 3px 3px 3px 3px;'>&#176;{$filter}</span></br>
EOF;
                                }
                            }
                            if($category_name == "mandatory"){
                           $html = $html + "</div></td></tr>";
}

                        }
                        $html .=<<<EOF
                                    </tbody>
                                    </table>
                                    </div>

                             </div>
                        </div></br>
EOF;
                    }}

                echo($html);
        }
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
		runQueries($_POST['runQueries'], $_POST['source']);
	}
	if(isset($_GET['getStatisticsOfSubscription'])){
		getStatisticsOfSubscription($_GET['subscriptionName']);
	}
	if(isset($_GET['getOutputOfSubscription'])){
		getOutputOfSubscription($_GET['subscriptionName']);
	}
	if(isset($_GET['getOutputOfQuery'])){
		getOutputOfQuery($_GET['subscriptionName'], $_GET['query_id']);
	}
	if(isset($_GET['lookup'])){
		lookup($_GET['ip']);
	}
	if(isset($_GET['pushOutput'])){
		pushOutput($_GET['subscriptionName']);
	}

?>
