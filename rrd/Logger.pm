#!/usr/bin/perl

use Log::Log4perl;

use strict;


my $logger_conf = "/home/istatistik/backend/yeni/conf/logger.conf";

sub logger {
        my ($priority, $message) = @_; 
        return 0 unless ($priority =~ /info|err|debug/);
				
		Log::Log4perl::init($logger_conf);
		my $logger = Log::Log4perl->get_logger();

		if ($priority eq "info"){
			$logger->info($message);
		}elsif ($priority eq "debug"){
			$logger->debug($message);
		}else{
			$logger->error($message);
		}
		
        return 1;
}
