<?php

    #topN query (by number of generated queries) will be displayed.
    $n = 10;
    
    if (isset($_POST['n'])){
        $n = $_POST['n'];
	if ($n > 100) {
		$n = 100;  ## max number of n
	}
    }

    $topN = getTopNQuery($n);

?>

<div class="row-fluid">
    <div class="span11">

    <h4 align="center">Top <?php echo "$n" ?> Query Ordered By Number of Generated Alerts</h4>
    <table class="table table-condensed table-hover">
        <tr>
            <th>Source Name</th>
            <th>Query Id</th>
            <th>Filter</th>
            <th>Number Of Generated Queries</th>
            <th></th>
        </tr>        
        <?php
            foreach($topN as $query){
                echo "<tr>";
                echo "<td>".$query['source_name']."</td>";
                echo "<td>".$query['query_id']."</td>";

                echo "<td>";
                if (strcmp($query['query_category'], 'mandatory') == 0){
                    echo '<span class="mandatory_query">'.$query['query'].'</span>';
                    echo '<span class="badge badge-warning">M</span>';
                }elseif(strcmp($query['query_category'], 'optional') == 0){
                    echo '<span class="optional_query">'.$query['query'].'</span>';
                    echo '<span class="badge badge-success">O</span>';
                }
                echo "</td>";

                echo "<td>".$query['count']."</td>";
                echo "</tr>";    
            }
        ?>
    </div>
</div>

