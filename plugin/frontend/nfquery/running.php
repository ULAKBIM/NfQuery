<script src="/nfsen/plugins/nfquery/js/running.js"></script>

<div class="row-fluid">
	<div class="span4">
		<strong>Running Queries</strong>	
	</div>
</div>

<div class="row-fluid">
	<div class="span10">
		<div  id="queryStatusDiv">
			<?php
				require_once('nfqueryutil.php');
				
				$result = checkQueries();
				echo $result;
			?>
		</div>
    </div>
</div>

<script type="text/javascript">
	checkQueryStatus();
</script>


