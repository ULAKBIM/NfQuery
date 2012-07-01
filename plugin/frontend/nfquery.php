<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/bootstrap.css" />

<?php

/*
 * Frontend plugin: demoplugin
 *
 * Required functions: demoplugin_ParseInput and demoplugin_Run
 *
 */

/* 
 * demoplugin_ParseInput is called prior to any output to the web browser 
 * and is intended for the plugin to parse possible form data. This 
 * function is called only, if this plugin is selected in the plugins tab. 
 * If required, this function may set any number of messages as a result 
 * of the argument parsing.
 * The return value is ignored.
 */

include('/var/www/nfsen/details.php');

function nfquery_ParseInput( $plugin_id ) {
	Process_Details_tab(0, 0);
	#SetMessage('error', "Error set by demo plugin!");
	#SetMessage('warning', "Warning set by demo plugin!");
	#SetMessage('alert', "Alert set by demo plugin!");
    #SetMessage('info', "Info set by demo plugin!");

} // End of demoplugin_ParseInput


/*
 * This function is called after the header and the navigation bar have 
 * are sent to the browser. It's now up to this function what to display.
 * This function is called only, if this plugin is selected in the plugins tab
 * Its return value is ignored.
 */
function nfquery_Run( $plugin_id ) {
	        require_once('nfquery/nfqueryutil.php');

		#print '<iframe id="nfqueryIFrame" src="/nfsen/plugins/nfquery/index.php" frameborder="0" style="height:100%;width:100%" scrolling="no">IFrame</iframe>';
		if(isset($_POST['nfqueryTabName'])){
				
			if(!isset($_SESSION['nfquery'])){	
				$_SESSION['nfquery'] = array();
			}
			$_SESSION['nfquery']['nfqueryTabName'] = $_POST['nfqueryTabName'];
		}
		if(file_exists("/home/serhat/nfquery/plugin/backend/nfquery.plugin.conf")){
			$result  = isRegister();
			if($result==0){
				echo "<div class='alert alert-error span11'> Your plugin is not registered to QueryServer yet.</div>";

			}
			if($result==1){
			         include('nfquery/index.php');
			}
		}
		else{
			include('nfquery/conf.php');
		}
} // End of demoplugin_Run


?>
