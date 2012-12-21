<?php

    #topN query (by number of generated queries) will be displayed.
    $n;
    
    if (array_key_exists('n', $_POST)){
        $n = $_POST['n'];
    }else{
        $n = 10; #If n is not specified its default value will be 10.
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

