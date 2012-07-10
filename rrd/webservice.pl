#/usr/bin/perl

use SOAP::Lite;
use JSON::Parse 'json_to_perl';

use strict;

#Connection parameters for webservice
my $uri 	 = "http://test-uri/" 
my $location = "https://www.ulakbim.gov.tr/ulaknet/uuys/yonetici/ws.php";

my $service;

sub getConnection{

	$service = SOAP::Lite->uri($location)->proxy($uri);

}

sub getAllInstitutes{

	my $result;
	
	$result = $service->wsGetInstitutes()->result();
	$result = json_to_perl($result);

	return %{$result}

}


sub get_links_of_man_ip{

	&getConnection();
	my %institutes = &getAllInstitutes();
	my %man_links;

	foreach $inst_id (keys %institutes){
		%institute = $institutes->{$inst_id};

		for $link_id (keys $institute){
			my %link = $institute->{$link_id};

			my $router_man_ip = $link{'router_man_ip'};
			my $link_id = $link{'link_id'};


			if (!$man_links{$router_man_ip}){
				$man_links{$router_man_ip} = {};
			}

			$man_links{$router_man_ip}{$link_id} = \%link;
		}
	}

	return %man_links;

}
