#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;
use Data::Printer;
use Data::Types qw(:all);
use JSON::RPC::Common::Marshal::HTTP;
use LWP::Protocol::https;
use LWP::UserAgent;
use JSON::RPC::LWP;
use Config::Simple;
use Term::ANSIColor;

#package NfQueryPlugin::Main; 

use feature 'say';

sub ParseConfigFile {

    my $config_file = shift;
    my %Config;

    Config::Simple->import_from($config_file, \%Config);
    
    my $cfg = new Config::Simple($config_file);
    
    return $cfg;
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

# get configuration
my $cfg = &ParseConfigFile('plugin.conf.pm');

# assign values
my $organization = $cfg->param('organization');
my $adm_name = $cfg->param('adm_name');
my $adm_mail = $cfg->param('adm_mail');
my $adm_tel  = $cfg->param('adm_tel');
my $adm_publickey_file = $cfg->param('adm_publickey_file');     # not using for the time.

# plugin info                                                                                           
my $prefix_list = $cfg->param('prefix_list');
my $plugin_ip = $cfg->param('plugin_ip');

# Query Server info                                                                                           
my $qs_ip = $cfg->param('queryserver_ip');
my $qs_port = $cfg->param('queryserver_port');
my $uri = 'https://' . $qs_ip . ':' . $qs_port;
                                                                                           
#print all
my $plugin_info = $organization      ." \n " .
                  $adm_name          ." \n " .
                  $adm_mail          ." \n " .
                  $adm_tel           ." \n " .
                  $prefix_list       ." \n " .
                  $plugin_ip         ." \n " .
                  $qs_ip             ." \n " .
                  $qs_port;      

#p($plugin_info);

my $rpc = &get_connection($qs_ip, $qs_port);

# register
my $result = $rpc->call( $uri, 'register', [$organization, $adm_name, $adm_mail, $adm_tel,
                                            $adm_publickey_file, $prefix_list, $plugin_ip, ]);

my $str = "================= Registration =================";
p($str);
p($result->result);
print("\n");

# get subscriptions
my $result = $rpc->call($uri, 'get_subscription', ["Malware"]);
print $result;

#p($result->result);

# dereference the result array
#p($result);
my $r = $result->result;

my $reff = \%{$r};

#print Dumper $new_foo_ref;
print Dumper $reff;
#print $size;
if (defined $result->result) {
    my $str = "================= Subscriptions Detail for Amada =================";
    p($str);
#    my $size = scalar \$dizi;
    my $index = 0;
#    for my $i (0 .. $size-1) {
#       print colored ("[". $index . "]\t" . @{$dizi}[$i], 'bold white');
        #print "\n";
#        $index+=1;
#    }
    print("\n");

}
else {
    print colored ("QueryServer doesn\'t have any subscriptions.\nPlease ask your QS Administrator.\n", "magenta");
}









