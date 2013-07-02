<?php
	switch ($a=isRegistered()) {
	case 1: 
		$html = "<div class='alert alert-error'><img src='plugins/nfquery/img/check_block.png'>&nbsp; &nbsp; &nbsp;    Your registration request was rejected.</div>";	
		break;
	case 2:
		$html = "<div class='alert alert-info2'><img src='plugins/nfquery/img/check_warning.png'>&nbsp; &nbsp; &nbsp;    Your registration is pending.</div>";	
		break;
	case 3: 
		$html = "<div class='alert alert-info'><img src='plugins/nfquery/img/check_ok.png'>&nbsp; &nbsp; &nbsp;    Plugin is registered.</div>";	
		break;
	case 4: 
		$html = "<div class='alert alert-error'><img src='plugins/nfquery/img/connect_problem.png'>&nbsp; &nbsp; &nbsp;    Connection can't be established!</div>";	
		break;
	default:
		$html = "<div class='alert' >Plugin is not found. Please check your informations or contact to Query Server admin.</div>";
	}
	print ($html);
	
?>
