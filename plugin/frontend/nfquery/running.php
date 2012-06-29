<script src="/nfsen/plugins/nfquery/js/running.js"></script>

<div class="row-fluid">
	<div class="span4">
		<strong>Running Queries</strong>	
	</div>
</div>


<div class="row-fluid">
	<div class="span12">
		<div  id="queryStatusDiv">
			<div id="lookupBox" style="width:300px; height:300px; visibility: hidden;">
			</div>
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


