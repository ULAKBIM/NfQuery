#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;
use Data::Printer;
use JSON::RPC::Common::Marshal::HTTP;
use LWP::Protocol::https;
use LWP::UserAgent;
use Config::Simple;

use feature 'say';
use feature 'unicode_strings' ;


sub ParseConfigFile {

    my $config_file = shift;
    my %Config;

    Config::Simple->import_from($config_file, \%Config);
    
    my $cfg = new Config::Simple($config_file);
    
    # assign values
    my $organization = $cfg->param('organization');
    my $adm_name = $cfg->param('adm_name');
    my $adm_mail = $cfg->param('adm_mail');
    my $adm_tel  = $cfg->param('adm_tel');
    #my $adm_publickey_file = $cfg->param('adm_publickey_file');     # not using for the time.

    my $prefix_list = $cfg->param('prefix_list');
    my $plugin_ip = $cfg->param('plugin_ip');

    #print $organization, $adm_name, $adm_mail, $adm_tel, $prefix_list, $plugin_ip;
    my $plugin_info = $organization      ." \n " .
                      $adm_name          ." \n " .
                      $adm_mail          ." \n " .
                      $adm_tel           ." \n " .
                      $prefix_list       ." \n " .
                      $plugin_ip;
    p($plugin_info);

    return;
}


sub getSubscriptionList {

    #my $ua = eval { LWP::UserAgent->new(ssl_opts => { verify_hostname => 1, SSL_ca_file => "/home/serdar/workspace/nfquery/cfg/certs/nfquery.crt" }) }
    #    or die "Could not make user-agent! $@";
    
    my $ua = eval { LWP::UserAgent->new() }
        or die "Could not make user-agent! $@";
    
    #$ua->ssl_opts( verify_hostname => 1, SSL_ca_file => './nfquery.crt' );
    #$ua->ssl_opts( verify_hostname => 1, SSL_ca_file => 'nfquery.crt', SSL_version => 'TLSv1');
    $ua->ssl_opts( verify_hostname => 0, SSL_ca_file => 'nfquery.crt', SSL_version => 'TLSv1');
    
    my $req_data = {
    		jsonrpc => "2.0",
    		id		=> "123123",
            method  => "add",
    		#id      => "xxx",
            #params  => { user=>'yyy', password=>'zzz' },
    		#params  => {name => 'yyy'}
    		params  => [99, 23]
    };
    
    #my $mod_data =  Dumper($req_data);
    
    #print each(%req_data);
    
    my $req_obj = JSON::RPC::Common::Procedure::Call->inflate($req_data);
    
    my $m = JSON::RPC::Common::Marshal::HTTP->new;
    
    my $req = $m->call_to_request($req_obj);
    
    $req->uri("https://193.140.94.205:7777");
    
    #print 'here1    ';
    #print $req;
    #print "\n";
    
    #$ua->ssl_opts(
    #		verify_hostname => 'False',
    #	);
    
    my $res = $ua->request($req);
    
    #print 'here2    ';
    #print bless $res;
    #print "\n";
    
    
    my $res_obj = $m->response_to_result($res);
    #print Dumper($res_obj);
    #print Dumper($res);
    p($res_obj);
    p($res);

}

&ParseConfigFile('plugin.conf.pm');
#&getSubscriptionList;


