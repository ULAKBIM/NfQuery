		<link rel="stylesheet" href="/nfsen/css/bootstrap.css" />
		<link rel="stylesheet" href="/nfsen/css/detail.css" />
		<link rel="stylesheet" href="/nfsen/plugins/nfquery/css/process.css" /> <!-- Override bootstrap's form elements width and height-->
		<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
		<script src="/nfsen/js/bootstrap.js"></script>
		<script src="/nfsen/js/welcome.js"></script>
		<script src="/nfsen/js/subscription.js"></script>
		<div class="container-fluid">
			<div class="row-fluid">
		  	  <div class="span12">
				<div class="tabbable tabs-left">
					<ul class="nav nav-tabs">
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
							<li class="<?php if (strcmp($tabName, "Home") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav ">Home</a></li>
							<li class="<?php if (strcmp($tabName, "Subscription") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">Subscription</a></li>
							<li class="<?php if (strcmp($tabName, "Workspace") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">Workspace</a></li>
							<li class="<?php if (strcmp($tabName, "Running") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">Running</a></li>
							<li class="<?php if (strcmp($tabName, "Report") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">Report</a></li>
							<li class="<?php if (strcmp($tabName, "Settings") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">Settings</a></li>
							<li class="<?php if (strcmp($tabName, "About") == 0) echo "active"?>"><a data-toggle="tab" href="#" class="nfqueryNav">About</a></li>
					</ul>

					<div class="tab-content">

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
