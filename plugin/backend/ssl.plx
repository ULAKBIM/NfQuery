use strict;
use warnings;
#use JSON::RPC::Common::Marshal::HTTP;
#use LWP::Protocol::https;
use LWP::UserAgent;
#use LWP::Simple;
use JSON::RPC::LWP;
use JSON::RPC::Client;
#use Net::SSL;
use Net::SSL (); # From Crypt-SSLeay

#$Net::HTTPS::SSL_SOCKET_CLASS = "Net::SSL"; # Force use of Net::SSL
$ENV{HTTPS_DEBUG} = 1;
# CA cert peer verification
$ENV{HTTPS_CA_FILE}   = '/home/serhat/NfQuery/cfg/certs/cacert.pem';
$ENV{HTTPS_CA_DIR}    = '/home/serhat/NfQuery/cfg/certs/';

# Client PKCS12 cert support
$ENV{HTTPS_PKCS12_FILE}     = '/home/serhat/NfQuery/cfg/certs/plugin-cert.p12';
$ENV{HTTPS_PKCS12_PASSWORD} = 'serhat1991';

# client certificate support
#$ENV{HTTPS_CERT_FILE} = '/home/serhat/nfquery/cfg/certs/plugin-cert.pem';
#$ENV{HTTPS_KEY_FILE}  = '/home/serhat/nfquery/cfg/certs/plugin-key.pem';



my $ua = eval { LWP::UserAgent->new() }
        or die "Could not make user-agent! $@";
$ua->ssl_opts( verify_hostname => 0);

print "JSON RPC CONNECTION\n";
my $rpc = JSON::RPC::LWP->new(
  ua => $ua,
  version => '2.0'
);
my $result = $rpc->call(  'https://193.140.100.96:7777', 'echo', '127.0.0.1');
#my $result = $rpc->call( 'https://193.140.100.96:7777', {method=>'echo', params=>['127.0.0.1']});
print $result->result, "\n";
