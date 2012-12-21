<?php
    if(file_exists("/data/nfsen/etc/nfsen.conf")){
		$registered = isRegistered();
		if($registered==0){
			$html = "<div class='alert' >Plugin is not found.";
			$html=$html." Please check your informations or contact to Query Server admin.</div>";
			echo $html;
		}
		if($registered==1){
			$html = "<div class='alert alert-error'><img src='/nfsen/plugins/nfquery/img/check_block.png'>&nbsp; &nbsp; &nbsp;    Your registration request was rejected.</div>";	
			echo $html;
		}
		if($registered==2){
			$html = "<div class='alert alert-info2'><img src='/nfsen/plugins/nfquery/img/check_warning.png'>&nbsp; &nbsp; &nbsp;    Your registration is pending.</div>";	
			echo $html;
		}
		if($registered==3){
			$html = "<div class='alert alert-info'><img src='/nfsen/plugins/nfquery/img/check_ok.png'>&nbsp; &nbsp; &nbsp;    Plugin is registered.</div>";	
			echo $html;
			
		}
		if($registered==4){
			$html = "<div class='alert alert-error'><img src='/nfsen/plugins/nfquery/img/connect_problem.png'>&nbsp; &nbsp; &nbsp;    Connection can't be established!</div>";	
			echo $html;	
		}
	}
	else{
            $html = "<div class='alert' >Plugin is not found.";
	    $html=$html." Please check your informations or contact to Query Server admin.</div>";
	    echo $html;
	}
	
?>
