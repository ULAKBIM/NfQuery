<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/bootstrap.css" />
<script src="/nfsen/plugins/nfquery/js/config.js"></script>
<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
<script src="/nfsen/plugins/nfquery/js/bootstrap.js"></script>
<div class="container-fluid">
	<div class="row-fluid">
		<div class="span2">
                 	<img src="/nfsen/plugins/nfquery/img/logo2.png">
		</div>
		<div class="span8 ">
			<div class="alert alert-inforegister">
				<legend><b>Organization</b></legend>
				<div class="alert alert-info2 ">
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_org"><b>ORGANIZATION</b></label>
					</div>
					<div id="orgdiv" class="span5">
						<center>
					    <input id="id_organization" name="org" type="text" style="height:25px;"title="Organization" >
					    <div id="od"></div>
					</div>
					</div>
				</div>
			</div>
			
			<div class="alert alert-inforegister">
				<legend><b>Administrator Informations</b></legend>
				<div class="alert alert-info2 ">
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_adm_name"><b>FULL NAME</b></label>
					</div>
					<div id="admin_name_div" class="span5">
						<center>
					    <input id="id_admin_name"  type="text" style="height:25px;"title="AdminName" >
					</div>
					</div>

					
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_adm_email"><b>EMAIL</b></label>
					</div>
					<div id="admin_mail_div" class="span5">
						<center>
					    <input id="id_admin_email" type="text" style="height:25px;"title="AdminMail" >
					</div>
					</div>


					
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_adm_phone"><b>PHONE NUMBER</b></label>
					</div>
					<div class="span5">
						<center>
					    <input id="id_admin_phone" type="text" style="height:25px;"title="AdminPhone" >
					</div>
					</div>
				</div>
			</div>
				
			<div class="alert alert-inforegister">
				<legend><b>Plugin Informations</b></legend>
				<div class="alert alert-info2 ">
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_pluginip"><b>PLUGIN IP</b></label>
					</div>
					<div class="span5">
						<center>
					    <input id="id_plugin_ip"  type="text" style="height:25px;"title="PluginIP" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_prefixlist"><b>PREFIX LIST</b></label>
					</div>
					<div class="span5">
						<center>
					    <input id="id_prefix" type="text" style="height:25px;"title="Prefix" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_queryserver"><b>QUERYSERVER IP</b></label>
					</div>
					<div class="span5">
						<center>
					    <input id="id_queryserverip" type="text" style="height:25px;"title="QuseryServerIP" >
					</div>
					</div>
					<div class="row-fluid">
					<div class="span5">
						<center>
					    <label for="id_querysport"><b>QUERYSERVER PORT</b></label>
					</div>
					<div class="span5">
						<center>
					    <input id="id_queryserverport" type="text" style="height:25px;"title="QuseryServerPort" >
					</div>
					</div>
				</div>
			</div>
	<center><div class="alert alert-success"><button id="register" onclick="register()" class="btn btn-primary"> Register</button></div></center>
		</div>
	</div>
</div>



<?php
?>
