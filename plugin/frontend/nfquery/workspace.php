<html>
    <body>
        <div class="row-fluid">
			<div class="span11">
				<?php
    				require_once("loghandler.php");
    				require_once("/var/www/nfsen/nfsenutil.php");
					require_once("/var/www/nfsen/details.php");
					DisplayDetails();
					DisplayProcessing();
                ?>  
			</div>
	</body>
</html>
