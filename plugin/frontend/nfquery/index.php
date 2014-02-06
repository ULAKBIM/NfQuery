<<<<<<< HEAD
<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/bootstrap.css" />
<link rel="stylesheet" href="/nfsen/css/detail.css" />
<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/query.css" />
<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/process.css" /> <!-- Override bootstrap's form elements width and height-->
<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
<script src="/nfsen/plugins/nfquery/js/bootstrap.js"></script>
<script src="/nfsen/plugins/nfquery/js/welcome.js"></script>
<script src="/nfsen/plugins/nfquery/js/newquery.js"></script>
<script src="/nfsen/plugins/nfquery/js/subscription.js"></script>
<script src="/nfsen/plugins/nfquery/js/iphone-style-checkboxes.js"></script>
<div id="index_container"  class="container-fluid">
	<div class="row-fluid">
	  <div class="span2">
			<img src="/nfsen/plugins/nfquery/img/logo2.png">
			<ul class="nav nav-list">
				<form method="post" action="/nfsen/nfsen.php" id="navigationForm"> 
=======
<?php
	global $register;
	$register = 0;
	# there's some extra work here!
	if (($register = isRegistered()) != 3) {
		if (! isset($_SESSION['nfquery']['nfqueryTabName']) || ! in_array($_SESSION['nfquery']['nfqueryTabName'], array("About"))) {
			$_SESSION['nfquery']['nfqueryTabName'] = "Settings";
		}
#		if ($register < 0) {
#			print("No connection to QueryServer. <a href=\"#\" onClick=\"location.reload();\">Recheck</a> later.");
#		} else {
#			print("Please register your plugin to QueryServer.");
#		}
#		exit;
	}
?>
<link rel="stylesheet" href="plugins/nfquery/css/bootstrap.css" />
<link rel="stylesheet" href="css/detail.css" />
<link rel="stylesheet" href="plugins/nfquery/css/query.css" />
<link rel="stylesheet" href="plugins/nfquery/css/process.css" /> <!-- Override bootstrap's form elements width and height-->
<script src="//code.jquery.com/jquery-1.7.2.js"></script>
<script src="plugins/nfquery/js/bootstrap.js"></script>
<script src="plugins/nfquery/js/welcome.js"></script>
<script src="plugins/nfquery/js/newquery.js"></script>
<script src="plugins/nfquery/js/subscription.js"></script>
<script src="plugins/nfquery/js/iphone-style-checkboxes.js"></script>
<div id="index_container"  class="container-fluid">
	<div class="row-fluid">
	  <div class="span2">
			<img src="plugins/nfquery/img/logo2.png">
			<ul class="nav nav-list">
				<form method="post" action="nfsen.php" id="navigationForm"> 
>>>>>>> devel
                    <input type="hidden" name="nfqueryTabName" id="nfqueryTab"/>

                    <!-- This fields need to run verification queries.-->
					<input type="hidden" name="starttime" id="starttime"/>
					<input type="hidden" name="endtime" id="endtime"/>
					<input type="hidden" name="query" id="query"/>
					<input type="hidden" name="queryid" id="queryid"/>
					<input type="hidden" name="identifier" id="identifier"/>

                    <!-- This fields need to update details graph -->
						<?php
<<<<<<< HEAD
							$register = isRegistered();
=======
#SIL#							$register = isRegistered();
>>>>>>> devel
							/*
							 * Check the tab name and activate corresponding tab.
							 * Default tab is Home.
							*/
							if (isset($_SESSION['nfquery']['nfqueryTabName'])){
									$tabName = $_SESSION['nfquery']['nfqueryTabName'];
							}
						?>
				</form>
<<<<<<< HEAD
					<li class="navItem <?php if (strcmp($tabName, "Home") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav "><i class="icon-home"></i>Home</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "Subscription") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-book"></i>Subscription</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "Workspace") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-pencil"></i>Workspace</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "Running") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-info-sign"></i>Running</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "Report") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-bullhorn"></i>Report</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "AddQuery") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class=" icon-certificate"></i>AddQuery</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "Settings") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-wrench"></i>Settings</a>
					</li>
					<li class="navItem <?php if (strcmp($tabName, "About") == 0) echo "active"?>">
						<a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-align-justify"></i>About</a>
					</li>
			</ul>
		</div>
			<div class="tab-content span10">

				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Home") == 0) echo "active" ?>" id="home">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "Home") == 0) include('welcome.php');?>
					</div>
				</div>

				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Subscription") == 0) echo "active"?>" id="subscription">
					<div class="container-fluid">
						<?php if ( strcmp($tabName, "Subscription") == 0) include('subscriptions.php'); ?>
					</div>
				</div>
				
				<div class="tab-pane <?php if (strcmp($tabName, "Settings") == 0) echo "active"?>" id="settings">

					<div class="container-fluid">
						<?php if (strcmp($tabName, "Settings") == 0) include('settings.php'); ?>
					</div>
				</div>

				<div class="tab-pane <?php if (strcmp($tabName, "About") == 0) echo "active"?>" id="about">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "About") == 0) include('about.php'); ?>
					</div>
				</div>

				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Workspace") == 0) echo "active"?>" id="workspace">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "Workspace") == 0) include('workspace.php');?>
					</div>
				</div>
				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "AddQuery") == 0) echo "active"?>" id="addquery">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "AddQuery") == 0) include('newquery.php');?>
					</div>
				</div>

				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Running") == 0) echo "active"?>" id="running">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "Running") == 0)include('running.php');?>
					</div>
				</div>

				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Verification") == 0) echo "active"?>" id="verification">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "Verification") == 0)include('verification.php');?>
					</div>

				</div>
				<div class="tab-pane <?php if ($register==3 and strcmp($tabName, "Report") == 0) echo "active"?>" id="verification">
					<div class="container-fluid">
						<?php if (strcmp($tabName, "Report") == 0)include('report.php');?>
					</div>
				</div>
=======
<?php
	$tab_meta = array (
				"Home" => array("id" => "home", "extra_check" => ($register==3), "include" => "welcome.php", "icon" => "icon-home"),
				"Subscription" => array("id" => "subscription", "extra_check" => ($register==3), "include" => "subscriptions.php", "icon" => "icon-book"),
				"Workspace" => array("id" => "workspace", "extra_check" => ($register==3), "include" => "workspace.php", "icon" => "icon-pencil"),
				"Running" => array("id" => "running", "extra_check" => ($register==3), "include" => "running.php", "icon" => "icon-info-sign"),
				"Report" => array("id" => "report", "extra_check" => ($register==3), "include" => "report.php", "icon" => "icon-bullhorn"),
				#"AddQuery" => array("id" => "addquery", "extra_check" => ($register==3), "include" => "newquery.php", "icon" => "icon-certificate"),
				"Settings" => array("id" => "settings", "extra_check" => true, "include" => "settings.php", "icon" => "icon-wrench"),
				"About" => array("id" => "about", "extra_check" => true, "include" => "about.php", "icon" => "icon-align-justify"),
				# "Verification" => array("id" => "verification", "extra_check" => true, "include" => "verification.php", "icon" => "icon-check"),
			);
	foreach ($tab_meta AS $subpage => $attr) {
		print ("<li class=\"navItem". (($tabName == $subpage) ? " active" : "") ."\"><a data-toggle=\"tab\" href=\"#\" class=\"nfqueryNav\"><i class=\"". $attr["icon"] ."\"></i>$subpage</a></li>\n");
	}
?>
			</ul>
		</div>
			<div class="tab-content span10">
<?php
	if (isset ($tab_meta[$tabName]) && $tab_meta[$tabName]["extra_check"]) {
		print "<div class=\"tab-pane active\" id=\"". $tab_meta[$tabName]["id"]. "\">\n"
                      	. "<div class=\"container-fluid\">\n";
		include($tab_meta[$tabName]["include"]);
		print "</div>\n</div>\n";
	}
?>

>>>>>>> devel
			</div>
	
		</div>
	  </div>
	</div>
</div>
