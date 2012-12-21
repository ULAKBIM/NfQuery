<?php
   require_once('nfqueryutil.php');

?>

<div class="row-fluid">
	<div class="span11">
        <h2>Generate New Query</h2>
	</div>
</div>

<div class="row-fluid">
    <div class="span11">
        <h4>Query Information</h4>
        <div class="query_generate">
        <table id="query_info_table" class="table table-condensed table-hover">
        <tr>
            <th>Nfsen Filter</th><th>Value</th>
            <th>Nfsen Filter</th><th>Value</th>
        </tr>
        <tr>
            <th>Src IP<input type="checkbox" name="src_ip" value="Src IP" /></th><th><input type="text" id="src_ip"></th> 
            <th>Duration<input type="checkbox" name="duration" value="Duration" /></th><th><input type="text" id="duration"></th>
        </tr>
        <tr>
            <th>Src Port<input type="checkbox" name="src_port" value="Src Port" /></th><th><input class="input-small" type="text" id="src_port"></th>
            <th>Flags<input type="checkbox" name="flags" value="Flags" /></th><th><input type="text" id="flags"></th>
        </tr>
        <tr>
            <th>Dst IP<input type="checkbox" name="dst_ip" value="Dst IP" /></th><th><input type="text" id="dst_ip"></th>
            <th>tos<input type="checkbox" name="tos" value="tos" /></th><th><input type="text" id="tos"></th>
        </tr>
        <tr>
            <th>Dst Port<input type="checkbox" name="dst_port" value="Dst Port" /></th><th><input type="text" id="dst_port"></th>
            <th>pps<input type="checkbox" name="pps" value="pps" /></th><th><input type="text" id="pps"><th>
        </tr>
        <tr>
            <th>Proto<input type="checkbox" name="proto" value="Proto" /></th><th><input type="text" id="proto"></th>
            <th>bps<input type="checkbox" name="bps" value="bps" /></th><th><input type="text" id="bps"><th>
        </tr>
        <tr>
            <th>Protocol Version<input type="checkbox" name="protocol_version" value="Protocol Version"/></th><th><input type="text" id="protocol_version"></th>
            <th>bpp<input type="checkbox" name="bpp" value="bpp" /></th><th><input type="text" id="bpp"><th>
        </tr>
        <tr>
            <th>Bytes<input type="checkbox" name="bytes" value="Bytes" /></th><th><input type="text" id="bytes"></th>
            <th>AS<input type="checkbox" name="AS" value="AS" /></th><th><input type="text" id="as"><th>
        </tr>
            <th>Packets<input type="checkbox" name="packets" value="Packets" /></th><th><input type="text" id="packets"></th>
            <th>Scale<input type="checkbox" name="scale" value="Scale" /></th><th><input type="text" id="scale"><th>
        </tr>
        </table>
	</div>
        <button class="btn btn-small btn-primary" id="generate_query_button"type="button">Generate Query</button>   
        </div>
</div>

