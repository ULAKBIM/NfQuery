#!/usr/bin/perl


use Config::Simple;

use strict;

my $config_file = "/home/istatistik/backend/yeni/conf/istatistik.conf";

sub parseConfigFile {

    my %Config;

    Config::Simple->import_from($config_file, \%Config);
    
    my $cfg = new Config::Simple($config_file);
    
    return $cfg;
}

1;
