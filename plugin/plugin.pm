#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;
use JSON::RPC::Common::Marshal::HTTP;
use LWP::Protocol::https;
use LWP::UserAgent;
use Config::Simple;

use feature 'say';


sub ParseConfigFile {

    my $config_file = shift;
    my %Config;

    Config::Simple->import_from($config_file, \%Config);
    
    my $cfg = new Config::Simple($config_file);
    
    # accessing values:
    my $adm = $cfg->param('organization');
    
    print $adm;

    return;
}

&ParseConfigFile('plugin.conf.pm');


#while( my ($k, $v) = each %Config ) {
#        print "key: $k, value: $v.\n";
#    }

#my $ua = eval { LWP::UserAgent->new(ssl_opts => { verify_hostname => 1, SSL_ca_file => "/home/serdar/workspace/nfquery/cfg/certs/nfquery.crt" }) }
#    or die "Could not make user-agent! $@";

my $ua = eval { LWP::UserAgent->new() }
    or die "Could not make user-agent! $@";

#$ua->ssl_opts( verify_hostname => 1, SSL_ca_file => './nfquery.crt' );
#$ua->ssl_opts( verify_hostname => 1, SSL_ca_file => 'nfquery.crt', SSL_version => 'TLSv1');
$ua->ssl_opts( verify_hostname => 0, SSL_ca_file => 'nfquery.crt', SSL_version => 'TLSv1');

my $req_data = {
		jsonrpc => "2.0",
		id		=> "TEST",
        method  => "add",
		#id      => "xxx",
        #params  => { user=>'yyy', password=>'zzz' },
		#params  => {name => 'yyy'}
		params  => [99, 23]
};

#my $mod_data =  Dumper($req_data);

#print $req_data;

#print $a;

#print each(%req_data);

my $req_obj = JSON::RPC::Common::Procedure::Call->inflate($req_data);

my $m = JSON::RPC::Common::Marshal::HTTP->new;

my $req = $m->call_to_request($req_obj);

$req->uri("https://193.140.94.205:7777");

print 'here1    ';
print $req;
print "\n";

#$ua->ssl_opts(
#		verify_hostname => 'False',
#	);
#
my $res = $ua->request($req);
#
print 'here2    ';
print bless $res;
print "\n";
#
#my $res_obj = $m->response_to_result($res);
#print Dumper($res_obj);
print Dumper($res);
#
#



