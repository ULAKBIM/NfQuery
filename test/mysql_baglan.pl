#!/usr/bin/perl
#use strict;
use DBD::mysql;
use POSIX;
use Math::Complex;
use Math::Round;

# MYSQL VARIABLES
$host = "193.140.83.112";
$database = "ulaknet2";
$user = "caglar";
$pw = "371300";

# DIRECTORY VARIABLES
my $work_dir="istatistik";

# PERL MYSQL CONNECT
#my $connect = Mysql->connect($host, $database, $user, $pw);
#$execute_node = $connect->query($query_node);
#$execute_node = $connect->query($query_node);
$dbh=DBI->connect("dbi:mysql:$database:$host", $user, $pw);
$query_node='select id,short_name,long_name from Nodes';
$execute_node = $dbh -> prepare($query_node);
$execute_node -> execute();
$id=0; #array icinde o uca ait bilgiler icin kullanilacak id

while (@results_node = $execute_node->fetchrow()) {
        $uni_id=$results_node[0];
        $arr{$id}{"uni_id"}=$results_node[0];
        #$alim=$arr[$id]["uni_id"];
        #print "id".$id." uni_id ".$alim."\n";
        $arr{$id}{"name"}=$results_node[1];
        $uni_short=$results_node[1];
        $long_name=$results_node[2];
#for each block assigned to this node
        $query_block="select block_id from Nodes_Blocks where node_id=".$uni_id;
        $execute_block = $dbh -> prepare($query_block);
        $execute_block -> execute();
        $i=0;
        while (@results_block = $execute_block->fetchrow()) {
                                $block_id=$results_block[0];
                                $query_ip="select * from Ip_Blocks where id=".$block_id;
                                $execute_ip = $dbh -> prepare($query_ip);
                                $execute_ip -> execute();
                                while (@results_ip = $execute_ip->fetchrow()) {
                                        $ip_sayisi=$results_ip[4]-$results_ip[3]+1;
                                        $mask=32-round((log($ip_sayisi)/log(2)));
                                        $new="\n";
                                        if($i==1){
                                                $src_filter.= " or  (src net ".$results_ip[1]."/".$mask.")";
                                                $dst_filter.= " or (dst net ".$results_ip[1]."/".$mask.")";
                                        }
                                        if($i==0) {
                                                $src_filter= "(src net ".$results_ip[1]."/".$mask.")";
                                                $dst_filter= "(dst net ".$results_ip[1]."/".$mask.")";
                                                $i=1;
                                        }
                                #print $src_filter.$dst_filter."\n";
                                }
                        }
                        $arr{$id}{"src_filter"}=$src_filter;
                        $arr{$id}{"dst_filter"}=$dst_filter;
                        $id=$id+1;
        }
        $first_node=0;
#For each node
        $command="rm -Rf ".$work_dir."/filters";
        system($command);
        $command="rm -Rf ".$work_dir."/outputs";
        system($command);
        $command="mkdir ".$work_dir."/filters";
        system($command);
        $command="mkdir ".$work_dir."/outputs";
        system($command);
        $command="mkdir ".$work_dir."/commands";
        system($command);
        while($first_node<$id){
                #print "id ".$first_node." uni_id ".$arr{$first_node}{"uni_id"}."\n";
                $directory=$work_dir."/filters/".$arr{$first_node}{"uni_id"};
                $command="mkdir ".$directory;
                system($command);
                $nfdump_outputs=$work_dir."/outputs/".$arr{$first_node}{"uni_id"};
                $command="mkdir ".$nfdump_outputs;
                system($command);
                $nfdump_commands=$work_dir."/commands/".$arr{$first_node}{"uni_id"};
                $second_node=0;
#for all other nodes
                        while($second_node<$id){
                                if($first_node!=$second_node){
                                        my $ouf;
                                        my $ouf2;
                                        $file_name=$directory."/src_".$arr{$first_node}{"uni_id"}."_dst_".$arr{$second_node}{"uni_id"};
                                        $file_name1=$work_dir."/filters/".$arr{$first_node}{"uni_id"}."/src_".$arr{$first_node}{"uni_id"}."_dst_".$arr{$second_node}{"uni_id"};
                                        $filter="(".$arr{$first_node}{"src_filter"}.") and (".$arr{$second_node}{"dst_filter"}.")";
                                        #print $src_filter.$dst_filter."\n";
                                        open $ouf, ">" . $file_name;
                                        print $ouf $filter;
                                        close $ouf;
                                        $nfdump_command="nfdump -R nfcapd.201108091550 -f ".$file_name1." -w ".$work_dir."/outputs/".$arr{$first_node}{"uni_id"}."/src_".$arr{$first_node}{"uni_id"}."_dst_".$arr{$second_node}{"uni_id"}."\n";
                                        open $ouf2, ">>" . $nfdump_commands;
                                        print $ouf2 $nfdump_command;
                                        close $ouf2;
                                }
                                $second_node=$second_node+1;
                        }
                $first_node=$first_node+1;
        } 
