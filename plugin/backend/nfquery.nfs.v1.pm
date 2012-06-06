#!/usr/bin/perl
#
# Demo plugin for NfSen
#
#
# TODO: Fill here!
#
#
#
#
#
#

# Name of the plugin
package nfquery;

use strict;
use NfProfile;
use NfConf;

use Sys::Syslog;

##### NfQuery Plugin Uses #####
use warnings;
use Data::Dumper;
use JSON::RPC::Common::Marshal::HTTP;
use LWP::Protocol::https;
use LWP::UserAgent;
use Config::Simple;
use feature 'say';
##### NfQuery Plugin Uses #####

# This string identifies the plugin as a version 1.3.0 plugin. 
our $VERSION = 130;

#
# The plugin may send any messages to syslog
# Do not initialize syslog, as this is done by 
# the main process nfsen-run
  
our %cmd_lookup = (
	'getSubscriptions'	=> \&getSubscriptions,
	#'getSubscriptions'	=> \&RunProc,
);

my $EODATA 	= ".\n";

my ( $nfdump, $PROFILEDIR );

#
# Define a nice filter: 
# We like to see flows containing more than 500000 packets
my $nf_filter = 'packets > 500000';

sub getSubscriptions {
#sub RunProc {
	my $socket  = shift;	# scalar
	my $opts	= shift;	# reference to a hash

	#syslog('debug', $opts); 

	### NFQUERY COMMUNICATION ###

	# test nfquery server jsonrpc over https communication

	my $ua = eval { LWP::UserAgent->new() }
    	or die "Could not make user-agent! $@";

	$ua->ssl_opts( verify_hostname => 0,
                   SSL_ca_file => '/home/serdar/workspace/nfquery/plugin/perls/nfquery.crt',
                   SSL_version => 'TLSv1'
    );

	#syslog('debug', 'here1');

	my $req_data = {
	        jsonrpc => "2.0",
	        id      => "TEST",
			method  => "add",
			#method  => "get_subscriptions",
	        #id      => "xxx",
	        #params  => { user=>'yyy', password=>'zzz' },
	        #params  => {name => 'yyy'}
			params  => [99, 23]
			#params  => []
	};

	my $req_obj = JSON::RPC::Common::Procedure::Call->inflate($req_data);

	my $m = JSON::RPC::Common::Marshal::HTTP->new;
	
	my $req = $m->call_to_request($req_obj);
	
	$req->uri("https://193.140.94.205:7777");
	
	#syslog('debug', 'here2');
	print $req;
	print "\n";

	my $res = $ua->request($req);

	#syslog('debug', 'here3');
	print bless $res;
	print "\n";

	my $result = Dumper($res);
	syslog('debug',$result->_content());
	
	# getting subscription information from NfQueryServer
	### NFQUERY COMMUNICATION ###

	## error checking example
	#if ( !exists $$opts{'colours'} ) {
	#	Nfcomm::socket_send_error($socket, "Missing value");
	#	return;
	#}

	# Prepare answer

	my %args;
	$args{'result'} = $result;
	#$args{'result'} = 'returning result to frontend';

	#syslog('debug', $result);

	Nfcomm::socket_send_ok($socket, \%args);

} # End of RunProc

#
# Periodic data processing function
#	input:	hash reference including the items:
#			'profile'		profile name
#			'profilegroup'	profile group
#			'timeslot' 		time of slot to process: Format yyyymmddHHMM e.g. 200503031200

sub run {
	my $argref 		 = shift;
	my $profile 	 = $$argref{'profile'};
	my $profilegroup = $$argref{'profilegroup'};
	my $timeslot 	 = $$argref{'timeslot'};

	syslog('debug', "nfquery run: Profilegroup: $profilegroup, Profile: $profile, Time: $timeslot");

	my %profileinfo     = NfProfile::ReadProfile($profile, $profilegroup);
	my $profilepath 	= NfProfile::ProfilePath($profile, $profilegroup);
	my $all_sources		= join ':', keys %{$profileinfo{'channel'}};
	my $netflow_sources = "$PROFILEDIR/$profilepath/$all_sources";

	syslog('debug', "nfquery args: '$netflow_sources'");
	return;

	# 
	# process all sources of this profile at once
	my @output = `$nfdump -M $netflow_sources -r nfcapd.$timeslot '$nf_filter'`;
	
	#
    # Process the output and notify the duty team
    my ($matched) = $output[-4] =~ /Summary: total flows: (\d+)/;

    if ( defined $matched ) {
        syslog('debug', "demoplugin run: $matched aggregated flows");
    } else {
        syslog('err', "nfquery: Unparsable output line '$output[-4]'");
    }

}

## SERDAR ##
## SERDAR ## Alert condition function.
## SERDAR ## if defined it will be automatically listed as available plugin, when defining an alert.
## SERDAR ## Called after flow filter is applied. Resulting flows stored in $alertflows file
## SERDAR ## Should return 0 or 1 if condition is met or not
## SERDAR #sub alert_condition {
## SERDAR #	my $argref 		 = shift;
## SERDAR #
## SERDAR #	my $alert 	   = $$argref{'alert'};
## SERDAR #	my $alertflows = $$argref{'alertfile'};
## SERDAR #	my $timeslot   = $$argref{'timeslot'};
## SERDAR #
## SERDAR #	syslog('info', "Alert condition function called: alert: $alert, alertfile: $alertflows, timeslot: $timeslot");
## SERDAR #
## SERDAR #	# add your code here
## SERDAR #
## SERDAR #	return 1;
## SERDAR #}
## SERDAR #
## SERDAR ##
## SERDAR ## Alert action function.
## SERDAR ## if defined it will be automatically listed as available plugin, when defining an alert.
## SERDAR ## Called when the trigger of an alert fires.
## SERDAR ## Return value ignored
## SERDAR #sub alert_action {
## SERDAR #	my $argref 	 = shift;
## SERDAR #
## SERDAR #	my $alert 	   = $$argref{'alert'};
## SERDAR #	my $timeslot   = $$argref{'timeslot'};
## SERDAR #
## SERDAR #	syslog('info', "Alert action function called: alert: $alert, timeslot: $timeslot");
## SERDAR #
## SERDAR #	return 1;
## SERDAR #}

#
# The Init function is called when the plugin is loaded. It's purpose is to give the plugin 
# the possibility to initialize itself. The plugin should return 1 for success or 0 for 
# failure. If the plugin fails to initialize, it's disabled and not used. Therefore, if
# you want to temporarily disable your plugin return 0 when Init is called.
#
sub Init {
	syslog("info", "nfquery: Init");

	# Init some vars
	$nfdump  = "$NfConf::PREFIX/nfdump";
	$PROFILEDIR = "$NfConf::PROFILEDATADIR";

	return 1;
}

#
# The Cleanup function is called, when nfsend terminates. It's purpose is to give the
# plugin the possibility to cleanup itself. It's return value is discard.
sub Cleanup {
	syslog("info", "nfquery Cleanup");
	# not used here
}

1;
