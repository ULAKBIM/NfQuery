function generateNewQuery(){
    var selected = new Array();
    var array = new Object();
    var query_info = new Object();
    array['src_ip'] = $("#src_ip").val();
    array['src_port'] = $("#src_port").val();
    array['dst_ip'] = $("#dst_ip").val();
    array['dst_port'] = $("#dst_port").val();
    array['proto'] = $("#proto").val();
    array['protocol_version'] = $("#protocol_version").val();
    array['bytes'] = $("#bytes").val();
    array['packets'] = $("#packets").val();
    array['duration'] = $("#duration").val();
    array['flags'] = $("#flags").val();
    array['tos'] = $("#tos").val();
    array['pps'] = $("#pps").val();
    array['bpp'] = $("#bps").val();
    array['AS'] = $("#as").val();
    array['scale'] = $("#scale").val();
    for (var key in array) {
        if(array[key] != ''){
            query_info[key] = array[key];    
            selected.push(key);
        } 
    }
    alert(JSON.stringify(query_info));
   // alert(JSON.stringify($("input:checked")));
//ugur    var selected = new Array();
//ugur    $('#query_info_table input:checked').each(function() {
//ugur        selected.push($(this).attr('name'));
//ugur    });
    alert(JSON.stringify(selected));
    $.post("plugins/nfquery/ajaxhandler.php", {query_info_list:JSON.stringify(query_info),mandatory:JSON.stringify(selected)}, function(data){});
 
}
$(document).ready(function() {
	$('#generate_query_button').click(function(){
            var tabName = $(this).text();
            $('#nfqueryTab').val(tabName);
            generateNewQuery();
	});

});
