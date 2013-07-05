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

$GLOBALS["nfsen_frontend_dir"] = dirname($_SERVER["SCRIPT_FILENAME"]);
$GLOBALS["nfsen_frontend_plugin_dir"] = $GLOBALS["nfsen_frontend_dir"] . "/plugins";
include($GLOBALS["nfsen_frontend_dir"].'/details.php');

function nfquery_ParseInput( $plugin_id ) {
    if (isset($_POST['starttime']) && isset($_POST['endtime']) && $_POST['starttime'] && $_POST['endtime']){
        #set tleft and tright session variables so we can see that time range at graphs.
        $_SESSION['tleft'] = $_POST['starttime'];
        $_SESSION['tright'] = $_POST['endtime'];
    }
	Process_Details_tab(0, 0);

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
		if(!isset($_SESSION['nfquery']['nfqueryTabName']))
			$_SESSION['nfquery']['nfqueryTabName'] = "Settings";
			
		include("nfquery/index.php");
} // End of demoplugin_Run


?>
