<html>
	<head>
		<link rel="stylesheet" href="/nfsen/css/bootstrap.css" />
	</head>
	<body>
		<div class="container-fluid">
			<div class="row-fluid">
		  	  <div class="span12">
				<div class="tabbable tabs-left">
					<ul class="nav nav-tabs">
						<li><a data-toggle="tab" href="#home">Home</a></li>
						<li><a data-toggle="tab" href="#subscriptions">Subscription</a></li>
						<li><a data-toggle="tab" href="#">Report</a></li>
						<li><a data-toggle="tab" href="#">Settings</a></li>
						<li><a data-toggle="tab" href="#about">About</a></li>
					</ul>

					<div class="tab-content">

						<div class="tab-pane active" id="home">
							<div class="container-fluid">
								<?php include('welcome.php'); ?>
							</div>
						</div>
						<div class="tab-pane" id="subscriptions">

							<div class="container-fluid">
								<?php include('subscriptions.php'); ?>
							</div>
						</div>
						<div class="tab-pane" id="about">
							<div class="container-fluid">
								<?php include('about.php'); ?>
							</div>
						</div>
					</div>
			
				</div>
			  </div>
			</div>
		</div>
	<script src="http://code.jquery.com/jquery-1.7.2.js"></script>
	<script src="/nfsen/js/bootstrap.js"></script>
	<script src="/nfsen/js/subscription.js"></script>
	<body>
</html>
