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

#!/usr/bin/perl

package nfquery;
use NfProfile;
use strict;
use warnings;
use Data::Dumper;
use Data::Printer;
use Data::Types qw(:all);
use LWP::UserAgent;
use JSON::RPC::LWP;
use Term::ANSIColor;
use JSON;
use JSON::Parse 'json_to_perl';
use Sys::Syslog;
use NetAddr::IP;
use Net::SSL ();
use Parallel::ForkManager;
use NfConf;
use DBM::Deep;
use Time::Local;
use Digest::MD5  qw(md5_hex);
use feature 'say';


my $cfg;
my $rpc;

my $Config;

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
my %prefixes;

#communication functions

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
	'pushOutputToQueryServer' => \&pushOutputToQueryServer,
	'getStatisticsOfSubscription' => \&getStatisticsOfSubscription,
	'generateQuery' => \&generateQuery,
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
    $cfg = $NfConf::PluginConf{'nfquery'};

    # assign values
    $organization = $$cfg{'organization'};
    syslog('debug', "organization: $organization");
    $adm_name = $$cfg{'adm_name'};
    $adm_mail = $$cfg{'adm_mail'};
    $adm_tel  = $$cfg{'adm_tel'};
    $adm_publickey_file = $$cfg{'adm_publickey_file'};     # not using for the time.

    # plugin info                                                                                           
    $prefix_list = $$cfg{'prefix_list'};
    $plugin_ip = $$cfg{'plugin_ip'};

    # Query Server info                                                                                           
    $qs_ip = $$cfg{'queryserver_ip'};
    $qs_port = $$cfg{'queryserver_port'};

	$uri = 'https://' . $qs_ip . ':' . $qs_port;
	$rpc = &get_connection();

    ## 
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
    my $stats = DBM::Deep->new( "/tmp/stats" );

    syslog('debug',"plugin_ip: $plugin_ip");
	my $result = $rpc->call( $uri, 'register', [$plugin_ip ]);

    %prefixes = &getPrefixes();
    return 1;
  
    
}

sub Cleanup {
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
    my $stats = DBM::Deep->new( "/tmp/stats" );
    $running_subscriptions->clear();
    $stats->clear();
}



# prepare connection parameters
sub get_connection {
    $Net::HTTPS::SSL_SOCKET_CLASS = "Net::SSL"; # Force use of Net::SSL

    # CA cert peer verification
    $ENV{HTTPS_CA_FILE}   = $$cfg{'https_ca_file'};
    $ENV{HTTPS_CA_DIR}    = $$cfg{'https_ca_dir'};

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


sub isRegistered{
    my $socket = shift;
    my $opts = shift;
    my %args;
	my $result = $rpc->call( $uri, 'register', [$plugin_ip ]);
	if($result){	
       		my $r = $result->result;
		$args{'register'} = @{$r}[0];
		Nfcomm::socket_send_ok($socket, \%args);
	}
}


sub checkPIDState{
	my $nfdumpPid = shift;
	my $state = kill 0, $nfdumpPid;
	return $state;
}

sub checkQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	$args{'subscriptions'} = [];
    
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");

	foreach my $subscription (keys %$running_subscriptions){
		push @{$args{'subscriptions'}}, $subscription;
		$args{"$subscription-mandatory"} = [];
		$args{"$subscription-optional"} = [];

		$args{"$subscription-mandatory-status"} = [];
		$args{"$subscription-optional-status"} = [];

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
			#TODO ParseOutput files.
			#delete ($running_subscriptions{$subscription});
		}
	}
		

	Nfcomm::socket_send_ok($socket, \%args);
	return;
}



sub ipInPrefixes{
	my $ip = shift;
	
	foreach my $plugin_id (keys %prefixes){
        my $prefix = $prefixes{$plugin_id};
		my $block = NetAddr::IP->new($prefix);
		my $ip_address = NetAddr::IP->new($ip);
		if($ip_address->within($block)){
			return $plugin_id;
		}
	}

	return 0;	
}

sub dateToTimestamp{
    my $date = shift;
    syslog('debug', "$date");
    my ($year,$mon,$mday,$hour,$min,$sec, $msec) = split(/[\s-:\.]+/, $date);
    my $time = timelocal($sec,$min,$hour,$mday,$mon-1,$year);
    return $time

}

sub fiveTupleHash{
    my $srcip = shift;
    my $dstip = shift;
    my $srcip_port = shift;
    my $dstip_port = shift;
    my $proto = shift;

    my $md5_hash = md5_hex($srcip.$dstip.$srcip_port.$dstip_port.$proto);
    return $md5_hash;
}

sub parseOutputOfPid{
	my $pid = shift;
    my @output;
	my $summary;
	
	open my $fh, "<", "/tmp/$pid";
	syslog('debug', "PARSING $pid");
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

            #calculate unixtime stamp
            $table{'timestamp'} = &dateToTimestamp("$vars[0] $vars[1]");

			#check ip adresses are in prefixes or not.
			my @srcip_port;
			my @dstip_port;
			my $plugin_id;

			$table{'srcip_port'} = $vars[5];
			@srcip_port = split(':', $table{'srcip_port'});
			$plugin_id = &ipInPrefixes($srcip_port[0]);	
			if ($plugin_id){
				$table{'srcip_alert_plugin'} = $plugin_id;
			}

			$table{'dstip_port'} = $vars[8];
			@dstip_port = split(':', $table{'dstip_port'});
			$plugin_id = &ipInPrefixes($dstip_port[0]);
			if ($plugin_id){
				$table{'dstip_alert_plugin'} = $plugin_id; 
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
	syslog('debug', "PARSED $pid");
	return @output;
}

sub parseOutputsOfSubscription{
	my $subscriptionName = shift;

	my %output;	
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
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

sub getTotalOfFile{
	my $fileName = shift;
	my %total;

	open (FILE, "/tmp/$fileName");
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

sub humanReadableBytes{
	my $bytes = shift;
	
	if ($bytes =~ /M$/){
		return $bytes;
	}else{
		return $bytes / (1024 * 1024);
	}
}

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
    
    my $stats = DBM::Deep->new( "/tmp/stats" );
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");

	my $queries = $stats->{$subscriptionName};

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

sub getOutputOfQuery{
	my $socket = shift;
	my $opts = shift;
	my %args;

	my $subscriptionName = $$opts{'subscriptionName'};
	my $query_id = $$opts{'query_id'};
	my $pid;
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");	
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
	

	my @outputOfQuery = &parseOutputOfPid($pid);
	my $json = encode_json \@outputOfQuery;
	syslog('debug', "$json");
	%args = &divideJsonToParts($json);	
	
	syslog('debug', 'Response To frontend. GETOUTPUT OF QUERY');
	Nfcomm::socket_send_ok($socket, \%args);
	return;

}

sub findAlertsInOutputOfQuery{
    my $subscriptionName = shift;
    my $ref = shift;
    my %alerts;
    my %queries = %{$ref};
    my $stats = DBM::Deep->new( "/tmp/stats" );

	foreach my $query_id (keys %queries){
		my $pid = $queries{$query_id};
	    my @outputOfQuery = &parseOutputOfPid($pid);
        $alerts{$query_id} = {};
        $alerts{$query_id}{'alerts'} = {};
        $alerts{$query_id}{'matched_flows'} = $stats->{$subscriptionName}{$query_id}{'total flows'} + 0;  
        $alerts{$query_id}{'matched_bytes'} = $stats->{$subscriptionName}{$query_id}{'total bytes'} + 0;  
        $alerts{$query_id}{'matched_packets'} = $stats->{$subscriptionName}{$query_id}{'total packets'} + 0;  
        $alerts{$query_id}{'timewindow_start'} = $stats->{$subscriptionName}{$query_id}{'first_seen'} + 0;  
        $alerts{$query_id}{'timewindow_end'} = $stats->{$subscriptionName}{$query_id}{'last_seen'} + 0;  

        foreach my $ref (@outputOfQuery){
            my %table = %{$ref};
            if ($table{'srcip_alert_plugin'}){
                $alerts{$query_id}{'alerts'}{$table{'hash'}} = \%table;
            }
        }            
	}

    return %alerts;
}

sub pushOutputToQueryServer{
	my $socket = shift;
	my $opts = shift;
	my %args;
    
	my $subscriptionName = $$opts{'subscriptionName'};
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
    my $stats = DBM::Deep->new( "/tmp/stats" );
    my %alerts;
    my %info;
    
    my $start_time = $running_subscriptions->{$subscriptionName}{'start_time'};
    my $end_time = $running_subscriptions->{$subscriptionName}{'end_time'};
	my %mandatory_queries = %{$running_subscriptions->{$subscriptionName}{'mandatory'}};
	my %optional_queries = %{$running_subscriptions->{$subscriptionName}{'optional'}};

    my %temp = &findAlertsInOutputOfQuery($subscriptionName, \%mandatory_queries);

    my %temp2 = &findAlertsInOutputOfQuery($subscriptionName, \%optional_queries);

    %alerts = (%temp, %temp2);
    my $result = $rpc->call($uri,'push_alerts',[$plugin_ip, \%alerts, $start_time, $end_time]);

    #Alerts pushed to queryserver. So no longer keep pids in data structure.
    delete $running_subscriptions->{$subscriptionName};
    delete $stats->{$subscriptionName};

	syslog('debug', 'PUSH ALERTS');
	Nfcomm::socket_send_ok($socket, \%args);
}

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

sub runVerificationQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;

	#Get parameters to the run queries.
	my $profile = $$opts{'profile'};
	my @source = @{$$opts{'source'}};
	my $nfdump_args = $$opts{'args'};
	my $query = $$opts{'query'};
	my $identifier = $$opts{'identifier'};

	my $strSource = join(':', @source);
	$profile = substr $profile, 2;

	#Find path to the nfdump and flow files.
	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";


    #Run verification query with ip filter and without ip filter.
    my $identifier_prefix = $prefixes{$identifier}; 
    my $verification_query = "$query and src net $identifier_prefix";
    
    
    my $verification_command_with_ip = "$nfdump -M $flowFiles $nfdump_args '$verification_query'";
    my $verification_command = "$nfdump -M $flowFiles $nfdump_args '$query'";
     
    syslog('debug', "$verification_command_with_ip"); 
    my %output;
    
    $output{'verification_command_with_ip'} = $verification_command_with_ip;
    $output{'verification_command'} = $verification_command;

    open my $fh, "$verification_command_with_ip |";
    {
        local $/;
        $output{'output1'} = <$fh>;
    }
    close $fh;

    open my $fh, "$verification_command |";
    {
        local $/;
        $output{'output2'} = <$fh>;
    }
    close $fh;
    
     
    syslog('debug', "$output{'output1'}"); 
	my $json = encode_json \%output;
	%args = &divideJsonToParts($json);	
     
	Nfcomm::socket_send_ok($socket, \%args);
}

sub runQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	my $queries = json_to_perl($$opts{'queries'});
	my %queries = %{$queries};
	#Get parameters to the run queries.
	my $profile = $$opts{'profile'};
	my @source = @{$queries{'source'}};

    #Timestamps 
    my $start_time = $$opts{'start_time'};
    my $end_time = $$opts{'end_time'};

	my $strSource = join(':', @source);
	my %filters = %{$queries{'queries'}};#TODO check here any queries exist.
	my $nfdump_args = $$opts{'args'};
	$profile = substr $profile, 2;


    #Create a fork manager object and set the maximum number of childen processes to fork.
    my $pm=new Parallel::ForkManager(50);

	#Find path to the nfdump and flow files.
	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";
	
	my @filterKeys = keys %filters;

    
    my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
    my $stats = DBM::Deep->new( "/tmp/stats" );

	foreach my $subscription_name (@filterKeys){
		my %category = %{$filters{$subscription_name}};
		
		#Check $subscription name is already running.
		if ($running_subscriptions->{$subscription_name}){
			syslog('debug', "$subscription_name is already running.");
			next;
		}else{    
            syslog('debug', "INITIALIZING $subscription_name");
            $running_subscriptions->{$subscription_name} = {};
            $running_subscriptions->{$subscription_name}{'start_time'} = $start_time;
            $running_subscriptions->{$subscription_name}{'end_time'} = $end_time;
            $running_subscriptions->{$subscription_name}{'mandatory'} = {};
            $running_subscriptions->{$subscription_name}{'optional'} = {};
		    $stats->{$subscription_name} = {};
        }
	    
		foreach my $query_id (@{$category{'mandatory'}}){
            
            #start the job.
			$pm->start and next;

            my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
            my $stats = DBM::Deep->new( "/tmp/stats" );
			$stats->{$subscription_name}{$query_id} = {};
			my $filter = &getFilter($query_id);
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			my $nfdump_pid = open(OUT, "nice -n 7 $command |");
			$running_subscriptions->{$subscription_name}{'mandatory'}{$query_id} = $nfdump_pid;			
				
			open FILE, ">", "/tmp/$nfdump_pid";
			while (defined(my $line = <OUT>)){
				print FILE $line;
				if ($line =~ /^Summary/){
					syslog('debug', "SUMMARY $line");
					my @sum = split(/: /, $line, 2);
					my @fields = split(/, /, $sum[1]);
					foreach my $field (@fields){
						my ($key, $value) = split(/: /, $field);
						$stats->{$subscription_name}{$query_id}{$key} = $value;
					}
				}
				if ($line =~ /^Time Window/){
					my @dates = split(/ - /, $line, 2);
					$stats->{$subscription_name}{$query_id}{'first_seen'} = &dateToTimestamp($dates[0]);
					$stats->{$subscription_name}{$query_id}{'last_seen'} = &dateToTimestamp($dates[1]);
				}
			}
			close FILE;
            
            $pm->finish;
		}

		foreach my $query_id (@{$category{'optional'}}){
			
            #start the job.
			$pm->start and next;
            my $running_subscriptions = DBM::Deep->new( "/tmp/running_subscriptions");
            my $stats = DBM::Deep->new( "/tmp/stats" );
			$stats->{$subscription_name}{$query_id} = {};
			my $filter = &getFilter(int($query_id));
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			my $nfdump_pid = open(OUT, " nice -n 7 $command |");
			$running_subscriptions->{$subscription_name}{'optional'}{$query_id} = $nfdump_pid;			
			
			open FILE, ">", "/tmp/$nfdump_pid";
			while (defined(my $line = <OUT>)){
				print FILE $line;
				if ($line =~ /^Summary/){
					my @sum = split(/: /, $line, 2);
					my @fields = split(/, /, $sum[1]);
					foreach my $field (@fields){
						my ($key, $value) = split(/: /, $field);
						$stats->{$subscription_name}{$query_id}{$key} = $value;
					}

				}
				if ($line =~ /^Time Window/){
					my @dates = split(/ - /, $line, 2);
					$stats->{$subscription_name}{$query_id}{'first_seen'} = &dateToTimestamp($dates[0]);
					$stats->{$subscription_name}{$query_id}{'last_seen'} = &dateToTimestamp($dates[1]);
				}

			}
			close FILE;
            
            $pm->finish;
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
	syslog('debug', "Response. - GETPREFIXES" ."".Dumper($r));
	return %{$r};
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
    %args = &divideJsonToParts($json);

	if (defined $result->result){
        syslog('debug', 'Response To frontend. - GETSUBSCRIPTIONDETAIL');
   		Nfcomm::socket_send_ok($socket, \%args);
    }else {
        Nfcomm::socket_send_ok($socket, \%args);
    }
}

#sub register{
#	my $result = $rpc->call( $uri, 'register', [$organization, $adm_name, $adm_mail, $adm_tel,
#                                            $adm_publickey_file, $prefix_list, $plugin_ip, ]);
#}

sub generateQuery{
	my $socket = shift;
	my $opts = shift;
        syslog('debug',"generateQuery");
	syslog('debug', "Response. - GETPREFIXES" ."".Dumper($opts));
        my $result = $rpc->call($uri,'generate_query',[$$opts{'query_list'}, $$opts{'mandatory'}, $plugin_ip]);
    
}

sub run{
}

