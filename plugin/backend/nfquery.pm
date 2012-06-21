#!/usr/bin/perl

package nfquery;
use NfConf;
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

#package NfQueryPlugin::Main; 

use feature 'say';

my $cfg;
my $rpc;

my %running_subscriptions;

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
#communication functions

our %cmd_lookup = (
	'getSubscriptions' => \&getSubscriptions,
	'getSubscriptionDetail' => \&getSubscriptionDetail,
	'getMyAlerts' => \&getMyAlerts,
	'runQueries' => \&runQueries,
);

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

sub runQueries{
	my $socket = shift;
	my $opts = shift;
	my %args;
	
	my $queries = json_to_perl($$opts{'queries'});
	my %queries = %{$queries};

	my $profile = $$opts{'profile'};
	my @source = @{$queries{'source'}};
	my $strSource = join(':', @source);
	my %filters = %{$queries{'queries'}};
	my $nfdump_args = $$opts{'args'};
	$profile = substr $profile, 2;

	my $nfdump = "$NfConf::PREFIX/nfdump";
	my $flowFiles = "$NfConf::PROFILEDATADIR/$profile/$strSource";
	

	my @filterKeys = keys %filters;
	
    my %a = %{$filters{'DFN-Honeypot'}};
	my @b = @{$a{'optional'}};
	my $str = join(":", @b);

	syslog('debug', "$organization");
	foreach my $subscription_name (@filterKeys){
		my %category = %{$filters{$subscription_name}};
		$running_subscriptions{$subscription_name} = {};

		foreach my $query_id (@{$category{'mandatory'}}){
			my $filter = &getFilter($query_id);
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			
			my $pid = fork();
			if ($pid == 0){
				my $nfdump_pid = open(OUT, "$command |");
				syslog('debug', "PID: $nfdump_pid COMMAND:$command");
			    $running_subscriptions{$subscription_name}{$query_id} = $nfdump_pid;			
				syslog('debug', "Mandatory");
				syslog('debug', Dumper %running_subscriptions);
			    	
				open FILE, ">", "/tmp/nfquery/$nfdump_pid";
				while (defined(my $line = <OUT>)){
					print FILE $line;
				}
				close FILE;
				exit(0);
			}	
		}

		foreach my $query_id (@{$category{'optional'}}){
			my $filter = &getFilter(int($query_id));
			my $command = "$nfdump -M $flowFiles $nfdump_args '$filter'";
			
			my $pid = fork();
			if ($pid == 0){
				my $nfdump_pid = open(OUT, "$command |");
				syslog('debug', "PID: $nfdump_pid COMMAND:$command");
			    $running_subscriptions{$subscription_name}{$query_id} = $nfdump_pid;			
				syslog('debug', "Optional");
				syslog('debug', Dumper $running_subscriptions{'mandatory'});
				
				open FILE, ">", "/tmp/nfquery/$nfdump_pid";
				while (defined(my $line = <OUT>)){
					print FILE $line;
				}
				close FILE;
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
	#Frontend expects key=value and max line size 1024.
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
               # $args{'subscriptiondetail'} = $json;
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

sub Init {

	$cfg = $NfConf::PluginConf{'nfquery'}; 

	# assign values
	$organization = $$cfg{'organization'};
	syslog('debug', "$organization");
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
    	
	$rpc = &get_connection($qs_ip, $qs_port);
	
	tie %running_subscriptions, 'IPC::Shareable', 'key', {create => 1};
	
	return 1;
}

sub run{
}






