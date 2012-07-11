#!/usr/bin/perl

use SOAP::Lite;
use JSON::Parse 'json_to_perl';

use strict;

#Connection parameters for webservice
my $uri 	 = "http://test-uri/"; 
my $location = "https://www.ulakbim.gov.tr/ulaknet/uuys/yonetici/ws.php";

my $service;

sub getConnection{

	$service = SOAP::Lite->uri($uri)->proxy($location);

}

sub getAllInstitutes{

	my $result;
	
	$result = $service->wsGetMainLinksByInstId()->result();
	$result = json_to_perl($result);

	return %{$result}

}

sub getLinksOfManIp{

	&getConnection();
	my %institutes = &getAllInstitutes();
	my %man_links;

    
	foreach my $inst_id (keys %institutes){
		my %institute = %{$institutes{$inst_id}};

		for my $link_id (keys %institute){
			my %link = %{$institute{$link_id}};

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

1;

