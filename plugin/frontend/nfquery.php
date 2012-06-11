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


function nfquery_ParseInput( $plugin_id ) {

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

	print '<link rel="stylesheet" href="/nfsen/css/bootstrap.css" />';

	print '<div class="container">
				<div class="row-fluid">
		    		<div class="hero-unit">
		    			<h1 class="nfquery-hero-title">Welcome to NfQuery </h1>
					</div>
				</div>
		   ';


	// the command to be executed in the backend plugin
	$command = 'nfquery::getSubscriptions';
    $opts = array();
	$out_list = nfsend_query($command, $opts);

	print '<div class="span8">';
	print "\n".var_dump($out_list);
    print '</div>';	

} // End of demoplugin_Run


?>
