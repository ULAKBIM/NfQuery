<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/bootstrap.css" />
<script src="/nfsen/plugins/nfquery/js/config.js"></script>
<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
<script src="/nfsen/plugins/nfquery/js/bootstrap.js"></script>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<div class="container-fluid">
	<div class="row-fluid">
		<div class="span2">
                 	<img src="/nfsen/plugins/nfquery/img/logo2.png"></br></br></br></br>
                 	<a href="http://www.geant.net"><img src="/nfsen/plugins/nfquery/img/geantlogo.jpg"></a>
		</div>
		<div class="span8 ">
			<div><strong><h2>Register</h2></strong></div>
			<div class="alert alert-inforegister">
				<legend><b>Plugin Informations</b></legend>
				<div class="alert alert-info2 ">
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_pluginip"><b>PLUGIN IP</b></label>
					</div>
					<div id="id_plugin_div" class="span5">
						<center>
					    <input id="id_plugin_ip"  type="text" style="height:25px;"title="PluginIP" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_queryserver"><b>QUERYSERVER IP</b></label>
					</div>
					<div id="id_queryserver_div" class="span5">
						<center>
					    <input id="id_queryserverip" type="text" style="height:25px;"title="QuseryServerIP" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_querysport"><b>QUERYSERVER PORT</b></label>
					</div>
					<div id="id_qsport_div" class="span5">
						<center>
					    <input id="id_queryserverport" type="text" style="height:25px;"title="QuseryServerPort" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_adm_pkfile"><b>PUBLIC KEY FILE</b></label>
					</div>
					<div id="id_pkeyfile_div" class="span5">
						<center>
					    <input id="id_pkeyfile" type="text" style="height:25px;"title="Public Key File" >
					</div>
					</div>
				</div>
			</div>
	<center><div id="warning"></div></center>
	<center><div class="alert alert-success"><button id="register" onclick="register()" class="btn btn-primary"> Register</button></div></center>
		</div>
	</div>
</div>



<?php
?>
