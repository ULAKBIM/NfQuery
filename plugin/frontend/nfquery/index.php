		<link rel="stylesheet" href="/nfsen/css/bootstrap.css" />
		<link rel="stylesheet" href="/nfsen/css/detail.css" />
		<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/query.css" />
		<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/process.css" /> <!-- Override bootstrap's form elements width and height-->
		<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
		<script src="/nfsen/js/bootstrap.js"></script>
		<script src="/nfsen/js/welcome.js"></script>
		<script src="/nfsen/js/subscription.js"></script>
		<div class="container-fluid">
			<div class="row-fluid">
			  <div class="span2">
					<h2>Nfquery</h2>
					<ul class="nav nav-list">
						<form method="post" action="/nfsen/nfsen.php" id="navigationForm"> 
							<input type="hidden" name="nfqueryTabName" id="nfqueryTab"/>
								<?php
									/*
									 * Check the tab name and activate corresponding tab.
									 * Default tab is Home.
 									*/
									$tabName = "Home";
									if (isset($_SESSION['nfquery']['nfqueryTabName'])){
											$tabName = $_SESSION['nfquery']['nfqueryTabName'];
									}
								?>
						</form>
							<li class="<?php if (strcmp($tabName, "Home") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav "><i class="icon-home"></i>Home</a></li>
							<li class="<?php if (strcmp($tabName, "Subscription") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-book"></i>Subscription</a></li>
							<li class="<?php if (strcmp($tabName, "Workspace") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-pencil"></i>Workspace</a></li>
							<li class="<?php if (strcmp($tabName, "Running") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-info-sign"></i>Running</a></li>
							<li class="<?php if (strcmp($tabName, "Report") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-bullhorn"></i>Report</a></li>
							<li class="<?php if (strcmp($tabName, "Settings") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-wrench"></i>Settings</a></li>
							<li class="<?php if (strcmp($tabName, "About") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav"><i class="icon-align-justify"></i>About</a></li>
					</ul>
				</div>
					<div class="tab-content span10">

						<div class="tab-pane <?php if (strcmp($tabName, "Home") == 0) echo "active"?>" id="home">
							<div class="container-fluid">
								<? include('welcome.php');?>
							</div>
						</div>
						<div class="tab-pane <?php if (strcmp($tabName, "Subscription") == 0) echo "active"?>" id="subscription">

							<div class="container-fluid">
								<?php include('subscriptions.php'); ?>
							</div>
						</div>
						<div class="tab-pane <?php if (strcmp($tabName, "About") == 0) echo "active"?>" id="about">
							<div class="container-fluid">
								<?php include('about.php'); ?>
							</div>
						</div>
						<div class="tab-pane <?php if (strcmp($tabName, "Workspace") == 0) echo "active"?>" id="workspace">
							<div class="container-fluid">
								<?php include('workspace.php'); ?>
							</div>
						</div>
						<div class="tab-pane <?php if (strcmp($tabName, "Running") == 0) echo "active"?>" id="running">
							<div class="container-fluid">
								<?php include('running.php'); ?>
							</div>
						</div>
					</div>
			
				</div>
			  </div>
			</div>
		</div>
