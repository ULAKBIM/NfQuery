#!/usr/bin/perl

package nfquery;
use NfConf;

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
use Sys::Syslog;

#package NfQueryPlugin::Main; 

use feature 'say';

my $cfg;
my $rpc;

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

sub getSubscriptions{
	my $socket = shift;
	my $opts = shift;

	# get subscriptions
	syslog('debug', "$uri");
	my $result = $rpc->call($uri, 'get_subscriptions', []);
	
	my $r = $result->result;
	my %args;

	if (defined $result->result) {
		$args{'subscriptions'} = \@{$r};
		syslog('debug', 'Response To frontend.');
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
	syslog('debug', $json);
        if (defined $result->result){
                $args{'subscriptiondetail'} = $json;
                syslog('debug', 'Response To frontend.');
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
	return 1;
}

sub run{
}






