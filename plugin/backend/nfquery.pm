#!/usr/bin/env perl
# This file is part of NfQuery.  NfQuery is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright NfQuery Team Members

package nfquery;
use strict;
use warnings;
use NfConf;
use NfProfile;
use JSON::RPC::LWP;
use JSON;
use Sys::Syslog;
use NetAddr::IP;
use Net::SSL ();
use Parallel::ForkManager;
use DBM::Deep;
use Time::Local;
use Digest::MD5  qw(md5_hex);
use LWP::UserAgent;

my $cfg;
my $rpc;

# plugin info
my $plugin_ip;

# Query Server info
my $uri;

#output directory
my $output_dir;
my %outputTable;
my %prefixes;

#Constants
my $TMP_DIR = $NfConf::VARDIR . "/tmp";
my $DBM_RUNNING_SUBSRIPTIONS = "$TMP_DIR/running_subscriptions";
my $DBM_STATS = "$TMP_DIR/stats";

our $VERSION = 020;

our %cmd_lookup = (
	'getSubscriptions' => \&getSubscriptions,
	'getSubscriptionDetail' => \&getSubscriptionDetail,
	'getMyAlerts' => \&getMyAlerts,
	'getTopNQuery' => \&getTopNQuery,
	'getStatisticsOfAlert' => \&getStatisticsOfAlert,
	'checkQueries'=>\&checkQueries,
	'runQueries' => \&runQueries,
	'runVerificationQueries' => \&runVerificationQueries,
	'isRegistered' => \&isRegistered,
	'getOutputOfSubscription' => \&getOutputOfSubscription,
	'getOutputOfQuery' => \&getOutputOfQuery,
	#'pushOutputToQueryServer' => \&pushOutputToQueryServer,
	'getStatisticsOfSubscription' => \&getStatisticsOfSubscription,
	'generateQuery' => \&generateQuery,
);

################################################################################
#Initialize plugin.
sub Init {
	$cfg = $NfConf::PluginConf{'nfquery'};

	# plugin info
	$plugin_ip = $$cfg{'plugin_ip'};

	$uri = 'https://' . $$cfg{'queryserver_ip'} . ':' . $$cfg{'queryserver_port'};
	$rpc = &get_connection();

	##
	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my $stats = DBM::Deep->new($DBM_STATS);

#	syslog('debug',"plugin_ip: $plugin_ip");
#	eval {
#	my $result = $rpc->call( $uri, 'register', [$plugin_ip ]);
#	} or do {
#		syslog('debug',"register: $@\n");
#		return (0);
#	};

    Cleanup();  ## make a cleanup before startup

	return 1;
}

################################################################################
sub Cleanup {
	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my $stats = DBM::Deep->new($DBM_STATS);

	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);

    foreach my $subscription (keys %{$running_subscriptions}) {
        foreach my $cat ("mandatory", "optional") {
	        foreach my $query_id (keys %{$running_subscriptions->{$subscription}{$cat}}) {
	    	    my $pid = $running_subscriptions->{$subscription}{$cat}{$query_id};
                next if ($pid <= 0);  # pid is -1 for queries that hasn't been started yet.  
                syslog('debug', "Cleanup ($subscription: $cat): $pid\n");
                if (kill 0, $pid) { # if running
                    syslog('debug', "Cleanup ($subscription: $cat): killing $pid...\n");
                    kill 15, $pid;
                }
                if (-f "$TMP_DIR/$pid") {
                    syslog('debug', "Cleanup ($subscription: $cat): $pid $TMP_DIR/$pid file exists\n");
                    if (! unlink("$TMP_DIR/$pid")) {
                        syslog('debug', "Cleanup ($subscription: $cat): $TMP_DIR/$pid cannot be deleted: $!\n");
                    }
                }
            }
        }
    }
    foreach my $file (`ls $TMP_DIR/[0-9]*`) {
        chop $file;
        syslog('debug', "Removing stale file: $file\n");
        if (! unlink($file)) {
                syslog('debug', "Couldn't remove stale file: $file: $!\n");
        }
    }

	$running_subscriptions->clear();
	$stats->clear();
}

################################################################################
# prepare connection parameters
sub get_connection {
	$Net::HTTPS::SSL_SOCKET_CLASS = "Net::SSL"; # Force use of Net::SSL

	# CA cert peer verification
	$ENV{HTTPS_CA_FILE}   = $$cfg{'https_ca_file'};
	$ENV{HTTPS_CA_DIR}	= $$cfg{'https_ca_dir'};

	# Client PKCS12 cert support
	$ENV{HTTPS_PKCS12_FILE}  = $$cfg{'https_pkcs12_file'};
	$ENV{HTTPS_PKCS12_PASSWORD} = $$cfg{'https_pkcs12_password'};

	# Prepare user agent
	my $ua = eval { LWP::UserAgent->new() }
			or die "Could not make user-agent! $@";
	$ua->ssl_opts( verify_hostname => 0);
	# $ua->ssl_opts( verify_hostname => 0, SSL_version => 'TLSv1');

	my $rpc = JSON::RPC::LWP->new(
	  ua => $ua,
	  version => '2.0'
	);

	return $rpc;

}

################################################################################
sub isRegistered{
	my $socket = shift;
	my $opts = shift;
	my %args;

	syslog('debug', "In isRegistered"); #ugur
	eval {
		my $result = $rpc->call( $uri, 'register', [$plugin_ip ]);
		$args{'register'} = @{$result->result}[0];
	} or do {
		syslog('debug',"isRegistered-error: $@");
		$args{'register'} = -1;
		$args{'register_error'} = "No connection to QueryServer!";
	};
	syslog('debug', "isRegistered-val: ". $args{"register"}); #ugur

	Nfcomm::socket_send_ok($socket, \%args);
}

################################################################################
sub checkPIDState {
	my $nfdumpPid = shift;
    return 1 if ($nfdumpPid == -1); ## process hasn't been run yet, but we return it as running. -ugur

	my $state = kill 0, $nfdumpPid;
	return $state;
}

################################################################################
sub checkPidStatesOfSubscription{
	my $subscription = shift;
	my %args;

	$args{"$subscription-mandatory"} = [];
	$args{"$subscription-optional"} = [];

	$args{"$subscription-mandatory-status"} = [];
	$args{"$subscription-optional-status"} = [];

	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my %mandatory_queries = %{$running_subscriptions->{$subscription}{'mandatory'}};
	my %optional_queries = %{$running_subscriptions->{$subscription}{'optional'}};
	my @query_statuses;
	my $finished = 1;

	foreach my $query_id (keys %mandatory_queries){
		my $pid = $mandatory_queries{$query_id};
		my $pid_state = &checkPIDState($pid);
		push @{$args{"$subscription-mandatory"}}, $query_id;
		if ($pid_state){
			push @{$args{"$subscription-mandatory-status"}}, $pid_state;
			$finished = 0;
		}else{
			push @{$args{"$subscription-mandatory-status"}}, 0;
		}

	}

	foreach my $query_id (keys %optional_queries){
		my $pid = $optional_queries{$query_id};
		my $pid_state = &checkPIDState($pid);
		push @{$args{"$subscription-optional"}}, $query_id;
		if ($pid_state){
			push @{$args{"$subscription-optional-status"}}, $pid_state;
			$finished = 0;
		}else{
			push @{$args{"$subscription-optional-status"}}, 0;
		}

	}

	if ($finished){
		#if all queries of subscription finished remove from running subscription.
		$args{"$subscription-finished"} = $finished;
	}
	return %args;
}

################################################################################
sub checkQueries{
	my $socket = shift;
	my $opts = shift;
	my %args = ();

	$args{'subscriptions'} = [];

	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);

	foreach my $subscription (keys %$running_subscriptions){
		push @{$args{'subscriptions'}}, $subscription;
		my %states = &checkPidStatesOfSubscription($subscription);
		@args{keys %states} = values %states;

	}

	Nfcomm::socket_send_ok($socket, \%args);
	return;
}

################################################################################
sub ipInPrefixes{
	my $ip = shift;

	foreach my $plugin_id (keys %prefixes){
		my @prefixes = @{$prefixes{$plugin_id}};
		foreach my $prefix (@prefixes){
			my $block = NetAddr::IP->new($prefix);
			my $ip_address = NetAddr::IP->new($ip);
			if($ip_address->within($block)){
				return $plugin_id;
			}
		}
	}

	return 0;
}

################################################################################
sub dateToTimestamp{
	my $date = shift;
	my ($year,$mon,$mday,$hour,$min,$sec, $msec) = split(/[-\s:\.]+/, $date);
	my $time = timelocal($sec,$min,$hour,$mday,$mon-1,$year);
	return $time

}

################################################################################
sub fiveTupleHash{
	my $srcip = shift;
	my $dstip = shift;
	my $srcip_port = shift;
	my $dstip_port = shift;
	my $proto = shift;

	my $md5_hash = md5_hex($srcip.$dstip.$srcip_port.$dstip_port.$proto);
	return $md5_hash;
}

################################################################################
sub parseOutputFile{
	my $fh = shift;
	my $subscription_name = shift;
	my $query_id = shift;

	my $current_plugin_id = &getPluginId($plugin_ip);
	my $filter = &getFilter($query_id);

	my @output;
	my $summary;
	my %temp_stats;

	my $stats = DBM::Deep->new($DBM_STATS);

    # refresh to latest prefix list
    %prefixes = &getPrefixes();

	if ($subscription_name && $query_id){
		$stats->{$subscription_name}{$query_id} = {};
	}

	foreach my $line (<$fh>){

		chomp($line);
		my @vars = split(/ +/, $line);

		if ($line =~ /^Summary/){
			my @sum = split(/: /, $line, 2);
			my @fields = split(/, /, $sum[1]);
			foreach my $field (@fields){
				my ($key, $value) = split(/: /, $field);
				if ($subscription_name && $query_id){
					$stats->{$subscription_name}{$query_id}{$key} = $value;
				}else{
					$temp_stats{$key} = $value;
				}
			}
			syslog('debug', "SUMMARY $subscription_name $query_id");
			next;
		}elsif ($line =~ /^Time Window/){
			my @dates = split(/ - /, $line, 2);
			if ($subscription_name && $query_id){
				$stats->{$subscription_name}{$query_id}{'first_seen'} = &dateToTimestamp($dates[0]);
				$stats->{$subscription_name}{$query_id}{'last_seen'} = &dateToTimestamp($dates[1]);
			}else{
				$temp_stats{'first_seen'} = &dateToTimestamp($dates[0]);
				$temp_stats{'last_seen'} = &dateToTimestamp($dates[1]);
			}
			next;
		}elsif ($vars[0] =~ /[[:alpha:]]/ || !$line){
			next;
		}else{
			my %table;
			$table{'date'} = $vars[0];


			$table{'flow_start'} = $vars[1];
			$table{'duration'} = $vars[2];
			$table{'proto'} = $vars[3];

			#calculate unixtime stamp
			$table{'timestamp'} = &dateToTimestamp("$vars[0] $vars[1]");

			#check ip adresses are in prefixes or not.
			my @srcip_port;
			my @dstip_port;
			my $src_plugin_id;
			my $dst_plugin_id;

			$table{'srcip_port'} = $vars[5];
			@srcip_port = split(':', $table{'srcip_port'});
			$src_plugin_id = &ipInPrefixes($srcip_port[0]);

			$table{'dstip_port'} = $vars[8];
			@dstip_port = split(':', $table{'dstip_port'});
			$dst_plugin_id = &ipInPrefixes($dstip_port[0]);

			my $A = 0;
			my $B = 0;


			if ($filter =~ /src ip/ && $filter =~ /dst ip/){
				$A = $src_plugin_id;
				$B = $dst_plugin_id;
			}elsif($filter =~ /src ip/){
				$A = $src_plugin_id;
				$B = $dst_plugin_id;
			}elsif($filter =~ /dst ip/){
				$A = $dst_plugin_id;
				$B = $src_plugin_id;
			}

			#Checks for determine alert type (multi/single)
			if ($A == $current_plugin_id){
				if ($B == $current_plugin_id){
					#single domain alert
					$table{'A'} = $A;
					$table{'alert_type'} = 1;
				}else{
					if (($B !=0) && ($B != $current_plugin_id)){
						#multi domain alert
						$table{'A'} = $A;
						$table{'B'} = $B;
						$table{'alert_type'} = 2;
					}
				}
			}else{
				if ($B == $current_plugin_id){
					if (($A != 0) && ($A != $current_plugin_id)){
						#multi domain alert
						$table{'A'} = $A;
						$table{'B'} = $B;
						$table{'alert_type'} = 2;
					}
				}
			}

			$table{'hash'} = &fiveTupleHash($srcip_port[0], $srcip_port[1],
					$dstip_port[0], $dstip_port[1], $table{'proto'});
			$table{'packets'} = $vars[9];
			$table{'bytes'} = $vars[10];
			$table{'flows'} = $vars[11];
			push @output, \%table;
		}
	}
	close $fh;
	if ($subscription_name){
		return \@output;
	}else{
		return (\@output, \%temp_stats);
	}
}

################################################################################
sub parseOutputOfPid{
	my $pid = shift;
	my $subscription_name = shift;
	my $query_id = shift;

	open my $fh, "<", "$TMP_DIR/$pid";
	my $ref = &parseOutputFile($fh, $subscription_name, $query_id);
	return $ref;
}

################################################################################
sub parseOutputsOfSubscription{
	my $subscriptionName = shift;

	my %output;
	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my %optional_queries = %{$running_subscriptions->{$subscriptionName}{'optional'}};
	my %mandatory_queries = %{$running_subscriptions->{$subscriptionName}{'mandatory'}};

	foreach my $query_id ( keys %mandatory_queries ){
		my $pid = $mandatory_queries{$query_id};
		my @lines = &parseOutputOfPid($pid);
		$output{$query_id} = \@lines;
	}

	foreach my $query_id ( keys %optional_queries ){
		my $pid = $optional_queries{$query_id};
		my @lines = &parseOutputOfPid($pid);
		$output{$query_id} = \@lines;
	}

	return %output;
}

################################################################################
sub getMatchedQueries{
	my $output = shift;
	my $total_packets = 0;
	my @matched_queries;

	foreach my $query_id (keys %{$output}){
		my $lines = $output->{$query_id};
		if (scalar @{$lines}){
			push @matched_queries, $query_id;
		}
	}

	return @matched_queries;
}

################################################################################
sub divideJsonToParts{
	my $json = shift;

	my %args;

	my @chars = split('', $json);
	my $counter = 0;
	my $index = 0;
	my $line = "";
	#Send part by part json string.
	#Because frontend expects key=value and max line size 1024.
	for my $char (@chars){
		$line = $line .$char ;
		if ($counter == 1000){
			$counter = 0;
			$args{"$index"} = $line;
			$index = $index +1;
			$line = "";
		}
		$counter = $counter + 1 ;
	}
	$args{"$index"} = $line;

	return %args;
}

################################################################################
sub getTotalOfFile{
	my $fileName = shift;
	my %total;

	open (FILE, "$TMP_DIR/$fileName");
	my @lines = <FILE>;
	close(FILE);

	my $line = $lines[-2]; #Total of working query is -2. line of file.
	my @fields = split(/, /, $line);

	foreach my $field (@fields){
		my ($key, $value) = split(/: /, $field);
		$total{$key} = $value;
	}

	return %total;
}

################################################################################
sub humanReadableBytes{
	my $bytes = shift;

	if ($bytes =~ /M$/){
		return $bytes;
	}else{
		return $bytes / (1024 * 1024);
	}
}

################################################################################
sub getStatisticsOfSubscription{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $subscriptionName = $$opts{'subscriptionName'};
	my %output;


	#
	#This values will be calculated for evey query
	#If query ids index is 'n' its /total_(flows|bytes|packets)/ will 'n'th element of list.
	#
	$args{'query_id'} = [];
	$args{'total_flows'} = [];
	$args{'total_bytes'} = [];
	$args{'total_packets'} = [];
	$args{'filters'} = [];

	$args{'matched_queries'} = [];
	$args{'matched_bytes'} = 0;
	$args{'matched_flows'} = 0;

	my $stats = DBM::Deep->new($DBM_STATS);
	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);

	my $queries = $stats->{$subscriptionName};


	my @temp = @{$running_subscriptions->{$subscriptionName}{'sources'}};
	my @sources;

	foreach my $source (@temp){
		push @sources, $source;
	}

	$args{"sources"} = \@sources;
	$args{"start_time"} = $running_subscriptions->{$subscriptionName}{'start_time'};
	$args{"end_time"} = $running_subscriptions->{$subscriptionName}{'end_time'};

	foreach my $query_id ( keys %$queries ){
		my %fields = %{$queries->{$query_id}};

		if (int($fields{'total flows'}) > 0){
			push @{$args{'matched_queries'}}, $query_id;
			$args{'matched_bytes'} += &humanReadableBytes($fields{'total bytes'});
			$args{'matched_packets'} += int($fields{'total packets'});
			$args{'matched_flows'} += int($fields{'total flows'});
		}

		push @{$args{'query_id'}}, $query_id;
		push @{$args{'total_flows'}}, $fields{'total flows'};
		push @{$args{'total_bytes'}}, $fields{'total bytes'};
		push @{$args{'total_packets'}}, $fields{'total packets'};
		push @{$args{'filters'}}, &getFilter($query_id);
	}

	#
	#Look one of output files to get total flows and total bytes.
	#

	my %optional_queries = %{$running_subscriptions->{$subscriptionName}{'optional'}};
	my %mandatory_queries = %{$running_subscriptions->{$subscriptionName}{'mandatory'}};

	#
	#First check any mandatory queries is running.
	#If found mandatory queries look output of the first one.
	#Else look output of the first optional query.
	#
	foreach my $query_id ( keys %mandatory_queries ){
		my $pid = $mandatory_queries{$query_id};
		my %total;

		if ($pid){
			%total = &getTotalOfFile($pid);
			$args{'total_flows_processed'} = $total{'Total flows processed'};
			$args{'total_bytes_read'} = &humanReadableBytes($total{'Bytes read'});
		}else{
			foreach my $query_id ( keys %optional_queries ){
				$pid = $optional_queries{$query_id};
				%total = &getTotalOfFile($pid);
				$args{'total_flows_processed'} = $total{'Total flows processed'};
				$args{'total_bytes_read'} = &humanReadableBytes($total{'Bytes read'});
				last;
			}
		}
		last;
	}

	Nfcomm::socket_send_ok($socket, \%args);
	return;
}

################################################################################
sub getOutputOfSubscription{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $subscriptionName = $$opts{'subscriptionName'};

	my %output = %{$outputTable{$subscriptionName}};

	my $json = encode_json \%output;
	%args = &divideJsonToParts($json);
	syslog('debug', "$args{'0'}");

	syslog('debug', 'Response To frontend. GETOUTPUTT');
	Nfcomm::socket_send_ok($socket, \%args);
	return;

}

################################################################################
sub getOutputOfQuery{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $subscriptionName = $$opts{'subscriptionName'};
	my $query_id = $$opts{'query_id'};
	my $pid;
	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	#
	#Find pid number. Query id may be in mandatory queries or optional queries.
	#
	my %mandatory_queries = %{$running_subscriptions->{$subscriptionName}{'mandatory'}};
	if ($mandatory_queries{$query_id}){
		$pid = $mandatory_queries{$query_id};
	}else{
		my %optional_queries = %{$running_subscriptions->{$subscriptionName}{'optional'}};
		$pid = $optional_queries{$query_id};
	}


	my ($outputOfQuery, $stats) = &parseOutputOfPid($pid, $subscriptionName, $query_id);
	my $json = encode_json $outputOfQuery;
	%args = &divideJsonToParts($json);

	syslog('debug', 'Response To frontend. GETOUTPUT OF QUERY');
	Nfcomm::socket_send_ok($socket, \%args);
	return;

}

################################################################################
sub findAlertsInOutputOfQuery{
	my $subscriptionName = shift;
	my $query_id = shift;
	my $output_ref = shift;
	my $stats_ref = shift;

	my %alerts;
	my $stats = DBM::Deep->new($DBM_STATS);
	my %stats;
	my @outputOfQuery = @{$output_ref};

	if ($subscriptionName){
		%stats = %{$stats->{$subscriptionName}{$query_id}};
	}else{
		%stats = %{$stats_ref};
	}

	$alerts{$query_id} = {};
	$alerts{$query_id}{'alerts'} = {};
	$alerts{$query_id}{'matched_flows'} = $stats{'total flows'} + 0;
	$alerts{$query_id}{'matched_bytes'} = $stats{'total bytes'} + 0;
	$alerts{$query_id}{'matched_packets'} = $stats{'total packets'} + 0;
	$alerts{$query_id}{'timewindow_start'} = $stats{'first_seen'} + 0;
	$alerts{$query_id}{'timewindow_end'} = $stats{'last_seen'} + 0;

	foreach my $ref (@outputOfQuery){
		syslog('debug', "ORADA");
		my %table = %{$ref};
		if ($table{'alert_type'}){
			$alerts{$query_id}{'alerts'}{$table{'hash'}} = \%table;
		}
	}

	return \%alerts;
}

################################################################################
sub pushOutputToQueryServer{
	my $subscriptionName = shift;
	my $query_id = shift;
	my $output_ref = shift;
	my $stats_ref = shift;
	my $start_time = shift;
	my $end_time = shift;

	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my $stats = DBM::Deep->new($DBM_STATS);
	my %alerts;

	if (!$start_time && !$end_time){
		 $start_time = $running_subscriptions->{$subscriptionName}{'start_time'};
		 $end_time = $running_subscriptions->{$subscriptionName}{'end_time'};
	}
	my $alerts = &findAlertsInOutputOfQuery($subscriptionName, $query_id, $output_ref, $stats_ref);


	my $result = $rpc->call($uri,'push_alerts',[$plugin_ip, $alerts, $start_time, $end_time]);

	#Alerts pushed to queryserver. So no longer keep pids in data structure.
	#delete $running_subscriptions->{$subscriptionName};
	#delete $stats->{$subscriptionName};

	syslog('debug', 'PUSH ALERTS');
}

################################################################################
sub getTopNQuery{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $n = $$opts{'topN'};
	my $result = $rpc->call($uri,'get_topn_query',[$n]);
	my $r = $result->result;
	my $json = encode_json \@$r;
	%args = &divideJsonToParts($json);

	Nfcomm::socket_send_ok($socket, \%args);
}

################################################################################
sub runVerificationQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;

	#Get parameters to the run queries.
	my $profile = $$opts{'profile'};
	my @source = @{$$opts{'source'}};
	my $nfdump_args = $$opts{'args'};
	my $query = $$opts{'query'};
	my $query_id = $$opts{'query_id'};
	my $start_time = $$opts{'start_time'};
	my $end_time = $$opts{'end_time'};

	my $strSource = join(':', @source);
	$profile = substr $profile, 2;

	#Find path to the nfdump and flow files.
	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";
	my $verification_command = "$nfdump -M $flowFiles $nfdump_args '$query'";

	my %output;

	$output{'verification_command'} = $verification_command;

	open my $fh, "$verification_command |";
	my ($output_ref, $stat_ref) = &parseOutputFile($fh, '', $query_id);
	&pushOutputToQueryServer('', $query_id, $output_ref, $stat_ref, $start_time, $end_time);
	$output{'output'} = $output_ref;
	$output{'stats'} = $stat_ref;

	my $json = encode_json \%output;
	%args = &divideJsonToParts($json);

	Nfcomm::socket_send_ok($socket, \%args);
}

################################################################################
sub runQueries {
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $queries = decode_json($$opts{'queries'});
	my %queries = %{$queries};
	#Get parameters to the run queries.
	my $profile = $$opts{'profile'};
	my @source = @{$$opts{'source'}};

    my @nfdumps_to_be_executed = ();

	#Timestamps
	my $start_time = $$opts{'start_time'};
	my $end_time = $$opts{'end_time'};

	my $strSource = join(':', @source);
	my %filters = %{$queries{'queries'}};#TODO check here any queries exist.
	my $nfdump_args = $$opts{'args'};
	$profile = substr $profile, 2;

	#Create a fork manager object and set the maximum number of childen processes to fork.
	local $SIG{CHLD} = 'DEFAULT';  ##ugur 
	my $pm=new Parallel::ForkManager(50);
    $pm->run_on_finish ( sub {
        my ($pid, $exit_code, $ident, $exit_signal, $core_dump, $data_structure_reference) = @_;
        if (defined($data_structure_reference)) {
                syslog('debug', "<<< [$pid: p:". ${$data_structure_reference} ."]: exited");
        } else {
                syslog('debug', "<<< [$pid]: exited");
        }
    });
    $pm->run_on_start ( sub {
        my ($pid, $ident) = @_;
        syslog ("debug", "run_on_start: p: $pid is running.\n");
    });

	#Find path to the nfdump and flow files.
	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";

	my @filterKeys = keys %filters;


	my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
	my $stats = DBM::Deep->new($DBM_STATS);

	foreach my $subscription_name (@filterKeys){
		my %category = %{$filters{$subscription_name}};

		#Check $subscription name is already running.
		if ($running_subscriptions->{$subscription_name}){
			my %states = &checkPidStatesOfSubscription($subscription_name);
			if ($states{"$subscription_name-finished"} == 0){
				syslog('debug', "$subscription_name is already running.");
				next;
			}else{
				delete $running_subscriptions->{$subscription_name};
				delete $stats->{$subscription_name};
			}
		}

		syslog('debug', "INITIALIZING $subscription_name");
		$running_subscriptions->{$subscription_name} = {};
		$running_subscriptions->{$subscription_name}{'sources'} = \@source;
		$running_subscriptions->{$subscription_name}{'start_time'} = $start_time;
		$running_subscriptions->{$subscription_name}{'end_time'} = $end_time;
		$running_subscriptions->{$subscription_name}{'mandatory'} = {};
		$running_subscriptions->{$subscription_name}{'optional'} = {};
		$stats->{$subscription_name} = {};

        foreach my $cat_id ('mandatory','optional') {
                foreach my $query_id (@{$category{$cat_id}}){
                    my $filter = &getFilter($query_id);
                    my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
                    $running_subscriptions->{$subscription_name}{'mandatory'}{$query_id} = -1; ## will run
                    push @nfdumps_to_be_executed, {"subscription_name" => $subscription_name, "cat_id" => $cat_id, "query_id" => $query_id, "command" => $command};
                }
        }

	}

    syslog('debug', 'Response To frontend. - RUNQUERIES');
    Nfcomm::socket_send_ok($socket, \%args);

    my $forkcounter = 0;
    foreach my $the_command (@nfdumps_to_be_executed) {
        ++$forkcounter;
        #start the job.
        $pm->start and next;
        
        my $running_subscriptions = DBM::Deep->new($DBM_RUNNING_SUBSRIPTIONS);
        my $nfdump_pid = open(OUT, "nice -n 7 ". $the_command->{'command'} ." |");
        syslog('debug', ">>> c: $forkcounter: [p:$nfdump_pid: nice -n 7 ". $the_command->{'command'} ." ]: running...\n");
        $running_subscriptions->{$the_command->{'subscription_name'}}{$the_command->{'cat_id'}}{$the_command->{'query_id'}} = $nfdump_pid;
        
        open FILE, ">", "$TMP_DIR/$nfdump_pid";
        while (defined(my $line = <OUT>)){
        	print FILE $line;
        }
        close FILE;
        
        my $output_ref = &parseOutputOfPid($nfdump_pid, $the_command->{'subscription_name'}, $the_command->{"query_id"});
        &pushOutputToQueryServer($the_command->{"subscription_name"}, $the_command->{"query_id"}, $output_ref);
        
        #ugur $pm->finish;
        my $ret = "c:$forkcounter: nice -n 7 ". $the_command->{'command'} ."\n";
        $pm->finish(0, \$ret);
    }

    $pm->wait_all_children if (@nfdumps_to_be_executed);

	syslog('debug', 'Exit from - RUNQUERIES');
}

################################################################################
sub getFilter{
	my $query_id = shift;
	my $result = $rpc->call($uri,'get_query_filter',[$query_id]);
	my $r = $result->result;
	return $r;
}

################################################################################
sub getPrefixes{
	my $result = $rpc->call($uri,'get_all_prefixes',[]);
	syslog('debug', 'Response. - GETPREFIXES');
	my $r = $result->result;
	return %{$r};
}

################################################################################
sub getPluginId{
	my $plugin_ip = shift;
	my $result = $rpc->call($uri,'get_plugin_id',[$plugin_ip]);
	my $r = $result->result;
	return $r;
}

################################################################################
sub getSubscriptions{
	my $socket = shift;
	my $opts = shift;
	# get subscriptions
	syslog('debug', "$uri");
	my $result = $rpc->call($uri, 'get_subscriptions', []);

	my $r = $result->result;
	syslog('debug',"$r");
	my %args;
	syslog('debug', 'Response. - GETFILTER');
	if (defined $result->result) {
		my %subscriptions = %{$r};
		foreach my $id (keys %subscriptions){
			$args{$id} = $subscriptions{$id};
		}
		syslog('debug', 'Response To frontend. - GETSUBSCRIPTION');
		Nfcomm::socket_send_ok($socket, \%args);
	}else {
		Nfcomm::socket_send_ok($socket, \%args);
	}
}

################################################################################
sub getMyAlerts{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $result = $rpc->call($uri,'get_my_alerts',[$plugin_ip]);
	my $r = $result->result;

	if (defined $result->result) {
		my $json = encode_json \%{$r};
		%args = &divideJsonToParts($json);
		Nfcomm::socket_send_ok($socket, \%args);
		syslog('debug', 'Response To frontend. - GETMYALERTS');
	}else {
		Nfcomm::socket_send_ok($socket, \%args);
	}
}

################################################################################
sub getStatisticsOfAlert{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $alert_id = $$opts{'alert_id'};
	my $result = $rpc->call($uri,'get_statistics',[$alert_id]);
	my $r = $result->result;

	syslog('debug', 'OLMADI');
	if (defined $result->result) {
		my $json = encode_json \%{$r};
		%args = &divideJsonToParts($json);
		Nfcomm::socket_send_ok($socket, \%args);
		syslog('debug', 'Response To frontend. - GETMYALERTS');
	}else {
		Nfcomm::socket_send_ok($socket, \%args);
	}
}

################################################################################
sub getSubscriptionDetail{
	my $socket = shift;
	my $opts = shift;

	syslog('debug', "$uri");
	syslog('debug', $$opts{'name'});
	my $result = $rpc->call($uri,'get_subscription',[$$opts{'name'}, $$opts{'method_call'}]);

	my $r = $result->result;
	my %args;
	my $reff = \%{$r};
	my $json = encode_json \%{$r};
	%args = &divideJsonToParts($json);

	if (defined $result->result){
		syslog('debug', 'Response To frontend. - GETSUBSCRIPTIONDETAIL');
   		Nfcomm::socket_send_ok($socket, \%args);
	}else {
		Nfcomm::socket_send_ok($socket, \%args);
	}
}

################################################################################
sub generateQuery{
	my $socket = shift;
	my $opts = shift;

	syslog('debug',"generateQuery");
	my $result = $rpc->call($uri,'generate_query',[$$opts{'query_list'}, $$opts{'mandatory'}, $plugin_ip]);
}

################################################################################
sub run{
}

1;
