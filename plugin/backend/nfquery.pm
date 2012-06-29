#!/usr/bin/perl

package nfquery;
use NfProfile;

use strict;
use warnings;
use Data::Dumper;
use Data::Printer;
use Data::Types qw(:all);
use JSON::RPC::Common::Marshal::HTTP;
use LWP::Protocol::https;
use LWP::UserAgent;
use LWP::Simple;
use JSON::RPC::LWP;
use Config::Simple;
use Term::ANSIColor;
use JSON;
use JSON::Parse 'json_to_perl';
use Sys::Syslog;
use IPC::Shareable;
use Proc::ProcessTable;
use Config::Simple;

#package NfQueryPlugin::Main; 

use feature 'say';

my $cfg;
my $rpc;

#Shared memory options
my %running_subscriptions;
my $glue = 'running';
my %options = (
	create => 'yes',
	mode => 0644,
	exclusive => 0,
	destroy => 'yes'
);

tie %running_subscriptions, 'IPC::Shareable', $glue, {%options};
# assign values
my $organization;
my $adm_name;
my $adm_mail;
my $adm_tel;
my $adm_publickey_file;

# plugin info                                                                                           
my $prefix_list;
my $plugin_ip;

# Query Server info                                                                                           
my $qs_ip;
my $qs_port;
my $uri;

#output directory
my $output_dir;
my %outputTable;
my %statisticTable;


#communication functions

our %cmd_lookup = (
	'getSubscriptions' => \&getSubscriptions,
	'getSubscriptionDetail' => \&getSubscriptionDetail,
	'getMyAlerts' => \&getMyAlerts,
	'runQueries' => \&runQueries,
	'checkQueries' => \&checkQueries,
	'getOutputOfSubscription' => \&getOutputOfSubscription,
	'getStatisticsOfSubscription' => \&getStatisticsOfSubscription,
	'createConfigFile' => \&createConfigFile,
);

sub ParseConfigFile {

    my $config_file = shift;
    my %Config;

    Config::Simple->import_from($config_file, \%Config);

    my $cfg = new Config::Simple($config_file);

    return $cfg;
}




#Initialize plugin.
sub Init {
	my $json;
	{
  	local $/; #Enable 'slurp' mode
  	open my $fh, "<", "/home/ahmetcan/nfquery/plugin/backend/nfquery.plugin.conf";
  	$json = <$fh>;
  	close $fh;
	}
	my $cfg = decode_json($json);
	
	$organization = $cfg->{"organization"};
	$adm_name =$cfg->{'admin_name'};
	$adm_mail =$cfg->{'admim_email'};
	$adm_tel  =$cfg->{'admin_phone'};
#	$adm_publickey_file = $cfg->{'adm_publickey_file'};     # not using for the time.

	# plugin info                                                                                           
	$prefix_list = $cfg->{'prefix'};
	$plugin_ip = $cfg->{'plugin_ip'};
	$output_dir = $cfg->{'outputdir'};
	syslog('debug', $output_dir);
	# Query Server info                                                                                           
	$qs_ip = $cfg->{'qserver_ip'};
	$qs_port = $cfg->{'qserver_port'};
	$uri = 'https://' . $qs_ip . ':' . $qs_port;
    
		
	$rpc = &get_connection($qs_ip, $qs_port);
    IPC::Shareable->clean_up_all;	
	
	return 1;
}


sub createConfigFile{
	my $socket = shift;
	my $opts = shift;
	my %args;
	syslog('debug',print Dumper $$opts{'configarray'});



}
# prepare connection parameters
sub get_connection {

    # Prepare user agent
    my $ua = eval { LWP::UserAgent->new() }
            or die "Could not make user-agent! $@";
    $ua->ssl_opts( verify_hostname => 0, SSL_ca_file => 'nfquery.crt', SSL_version => 'TLSv1');
    
    my $rpc = JSON::RPC::LWP->new(
      ua => $ua,
      version => '2.0'
    );

    return $rpc;

}

sub checkPIDState{
	my $nfdumpPid = shift;
	my $state = kill 0, $nfdumpPid;
#	my $t = new Proc::ProcessTable;
#	foreach my $process (@{$t->table}){
#		my $current_pid = $process->pid;
#		my $current_pid_state = $process->state;
#		if ($nfdumpPid == $current_pid){
#			syslog('debug', "EQUAL $current_pid -> $current_pid_state");	
#			$state = $process->state;			
#		}
#	}
	return $state;
}

sub checkQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	$args{'subscriptions'} = [];

	foreach my $subscription (keys %running_subscriptions){
		push @{$args{'subscriptions'}}, $subscription;
		$args{"$subscription-mandatory"} = [];
		$args{"$subscription-optional"} = [];

		$args{"$subscription-mandatory-status"} = [];
		$args{"$subscription-optional-status"} = [];

		my %mandatory_queries = %{$running_subscriptions{$subscription}{'mandatory'}};
		my %optional_queries = %{$running_subscriptions{$subscription}{'optional'}};
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

		foreach my $query_id (keys %mandatory_queries){
			my $pid = $mandatory_queries{$query_id};
			my $pid_state = &checkPIDState($pid);
			push @{$args{"$subscription-optional"}, $query_id};
			if ($pid_state){
				push @{$args{"$subscription-optional-status"}}, $pid_state;
				$finished = 0;
			}else{
				push @{$args{"$subscription-optional-status"}}, 0;
			}

		}

		if ($finished){
			#if all queries of subscription finished remove from running subscription.
			#TODO ParseOutput files.
			#delete ($running_subscriptions{$subscription});
		}
	}
	
	Nfcomm::socket_send_ok($socket, \%args);
	return;
}

sub parseOutputOfPid{
	my $pid = shift;
    my @output;
	my $summary;
	
	open my $fh, "<", "$output_dir/$pid";

	foreach my $line (<$fh>){

		chomp($line);
		my @vars = split(/ +/, $line);

		if ($vars[0] =~ /[[:alpha:]]/ || !$line){
			next;
		}elsif ($vars[0] =~ /^Summary/ || $summary){
			$summary = 1;
		}else{
			my %table;
			$table{'date'} = $vars[0];
			$table{'flow_start'} = $vars[1];
			$table{'duration'} = $vars[2];
			$table{'proto'} = $vars[3];
			$table{'srcip_port'} = $vars[5];
			$table{'dstip_port'} = $vars[8];
			$table{'packets'} = $vars[9];
			$table{'bytes'} = $vars[10];
			$table{'flows'} = $vars[11];
			push @output, \%table;
		}
	}
	close $fh;
	return @output;
}

sub parseOutputsOfSubscription{
	my $subscriptionName = shift;

	my %output;	

	my %optional_queries = %{$running_subscriptions{$subscriptionName}{'optional'}};
	my %mandatory_queries = %{$running_subscriptions{$subscriptionName}{'mandatory'}};
	
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

sub getTotalFlows{
	my $output = shift;
	my $total_flows = 0;
	my $total_bytes = 0;
	my $total_packets = 0;
	
	foreach my $query_id (keys %{$output}){
		my $lines = $output->{$query_id};
		foreach my $hash (@{$lines}){
			$total_flows = $total_flows + int($hash->{'flows'});
			$total_packets = $total_packets + int($hash->{'packets'});
			$total_bytes = $total_bytes + int($hash->{'bytes'});
		}
	}
	
	return $total_flows, $total_bytes, $total_packets;
}

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

sub getStatisticsOfSubscription{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	my $subscriptionName = $$opts{'subscriptionName'};

	my %output = &parseOutputsOfSubscription($subscriptionName);	
    my ($total_flows, $total_bytes, $total_packets) = &getTotalFlows(\%output);	
	my @matched_queries = &getMatchedQueries(\%output);
	
	
	$args{'matched'} = @matched_queries;
	$args{'total_query'} = scalar (keys %output);
	$args{'total_flows'} = $total_flows;
	$args{'total_bytes'} = $total_bytes;
	$args{'total_packets'} = $total_packets;


	#TODO Keep all results in a data structure.	
	$outputTable{$subscriptionName} = \%output;
	syslog('debug', 'Response To frontend. GETSTATISTICS');
	Nfcomm::socket_send_ok($socket, \%args);
	return;
}

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

#Share running_subscriptions hash with all other child process. So they can put pid in it.
sub runQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	my $queries = json_to_perl($$opts{'queries'});
	my %queries = %{$queries};
	#Get parameters to the run queries.
	my $profile = $$opts{'profile'};
	my @source = @{$queries{'source'}};
	my $strSource = join(':', @source);
	my %filters = %{$queries{'queries'}};#TODO check here any queries exist.
	my $nfdump_args = $$opts{'args'};
	$profile = substr $profile, 2;

	#Find path to the nfdump and flow files.
	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";
	
	my @filterKeys = keys %filters;
	foreach my $subscription_name (@filterKeys){
		my %category = %{$filters{$subscription_name}};
		
		#Check $subscription name is already running.
		if ($running_subscriptions{$subscription_name}){
			syslog('debug', "$subscription_name is already running.");
			next;
		}
		$running_subscriptions{$subscription_name} = {};
		$running_subscriptions{$subscription_name}{'mandatory'} = {};
		$running_subscriptions{$subscription_name}{'optional'} = {};

		foreach my $query_id (@{$category{'mandatory'}}){
			my $filter = &getFilter($query_id);
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			syslog('debug', "$command");		
			my $pid = fork();
			if ($pid == 0){
				#TODO
				syslog('debug', 'DENEME'); 
				my $nfdump_pid = open(OUT, "nice -n 7 $command |");
				syslog('debug', 'DENEME'); 
			    $running_subscriptions{$subscription_name}{'mandatory'}{$query_id} = $nfdump_pid;			
			    	
				open FILE, ">", "/tmp/$nfdump_pid";
				while (defined(my $line = <OUT>)){
					print FILE $line;
				}
				close FILE;
				my $json = encode_json \%running_subscriptions;	
				syslog('debug', "$json");
				exit(0);
			}	
		}

		foreach my $query_id (@{$category{'optional'}}){
			my $filter = &getFilter(int($query_id));
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			
			my $pid = fork();
			if ($pid == 0){
				#TODO
				syslog('debug', 'DENEME'); 
				my $nfdump_pid = open(OUT, " nice -n 7 $command |");
				syslog('debug', 'DENEME'); 
			    $running_subscriptions{$subscription_name}{'optional'}{$query_id} = $nfdump_pid;			
				
				open FILE, ">", "/tmp/$nfdump_pid";
				while (defined(my $line = <OUT>)){
					print FILE $line;
				}
				close FILE;
				my $json = encode_json \%running_subscriptions;	
				syslog('debug', "$json");
				exit(0);
			}	
		}
	
	}
		
	syslog('debug', 'Response To frontend. - RUNQUERIES');
	Nfcomm::socket_send_ok($socket, \%args);

}

sub getFilter{
	my $query_id = shift;
    my $result = $rpc->call($uri,'get_query_filter',[$query_id]);
	syslog('debug', 'Response. - GETFILTER');
	my $r = $result->result;
	syslog('debug',$r);
	return $r;

}

sub getPrefixes{
    my $result = $rpc->call($uri,'get_prefixes',[$plugin_ip]);
	syslog('debug', 'Response. - GETPREFIXES');
	my $r = $result->result;
	syslog('debug',$r);
	return $r;
}

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
		$args{'subscriptions'} = \@{$r};
		syslog('debug', 'Response To frontend. - GETSUBSCRIPTION');
		Nfcomm::socket_send_ok($socket, \%args);
	}else {
		Nfcomm::socket_send_ok($socket, \%args);
	}	
}


sub getMyAlerts{
	my $socket = shift;
	my $opts = shift;
	my $host = '193.149.94.217';
	
	syslog('debug',"$uri");
	my $result = $rpc->call($uri,'get_my_alerts',[$host]);
	my $r = $result->result;
        my %args;
	if (defined $result->result) {
                $args{'alerts'} = \@{$r};
                syslog('debug', 'Response To frontend. - GETMYALERTS');
                Nfcomm::socket_send_ok($socket, \%args);
        }else {
                Nfcomm::socket_send_ok($socket, \%args);
        }       
}

sub getSubscriptionDetail{
    my $socket = shift;
    my $opts = shift;

    syslog('debug', "$uri");
    syslog('debug', $$opts{'name'});
    my $result = $rpc->call($uri,'get_subscription',[$$opts{'name'}]);
    my $r = $result->result;
    my %args;
	my $reff = \%{$r};	
	my $json = encode_json \%{$r};
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
        	##syslog('debug', "$line");
		$line = "";
	    }
	    $counter = $counter + 1 ;
	}
    $args{"$index"} = $line;
	if (defined $result->result){
        syslog('debug', 'Response To frontend. - GETSUBSCRIPTIONDETAIL');
   		Nfcomm::socket_send_ok($socket, \%args);
    }else {
        Nfcomm::socket_send_ok($socket, \%args);
    }
}

sub register{
	my $result = $rpc->call( $uri, 'register', [$organization, $adm_name, $adm_mail, $adm_tel,
                                            $adm_publickey_file, $prefix_list, $plugin_ip, ]);
}


sub run{
}

